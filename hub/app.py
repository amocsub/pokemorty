#!/usr/bin/env python3
"""amocsub CTF Hub — central platform for managing challenges, events, and player progress."""

import json
import os
import secrets
from datetime import datetime
from functools import wraps

import firebase_admin
from firebase_admin import auth as fb_auth, credentials
from flask import (Flask, abort, g, jsonify, redirect, render_template,
                   request, session, url_for)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

# ── Firebase ──────────────────────────────────────────────────────────────────

_firebase_initialized = False


def init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return
    svc = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
    if svc:
        cred = credentials.Certificate(json.loads(svc))
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True


def firebase_web_config():
    return json.loads(os.environ.get('FIREBASE_WEB_CONFIG', '{}'))


# ── Database ──────────────────────────────────────────────────────────────────

DB_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(__file__), 'hub.db'))

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id           TEXT PRIMARY KEY,
    email        TEXT UNIQUE NOT NULL,
    display_name TEXT,
    photo_url    TEXT,
    is_admin     INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS challenges (
    id               TEXT PRIMARY KEY,
    slug             TEXT UNIQUE NOT NULL,
    name             TEXT NOT NULL,
    description      TEXT,
    url              TEXT,
    category         TEXT NOT NULL DEFAULT 'web',
    difficulty       TEXT NOT NULL DEFAULT 'medium',
    points           INTEGER NOT NULL DEFAULT 100,
    total_stages     INTEGER NOT NULL DEFAULT 1,
    is_active        INTEGER NOT NULL DEFAULT 1,
    requires_code    INTEGER NOT NULL DEFAULT 0,
    access_code_hash TEXT,
    webhook_secret   TEXT NOT NULL,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS events (
    id          TEXT PRIMARY KEY,
    slug        TEXT UNIQUE NOT NULL,
    name        TEXT NOT NULL,
    description TEXT,
    start_time  TEXT,
    end_time    TEXT,
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS event_challenges (
    event_id     TEXT NOT NULL REFERENCES events(id),
    challenge_id TEXT NOT NULL REFERENCES challenges(id),
    PRIMARY KEY (event_id, challenge_id)
);

CREATE TABLE IF NOT EXISTS challenge_access (
    user_id      TEXT NOT NULL REFERENCES users(id),
    challenge_id TEXT NOT NULL REFERENCES challenges(id),
    granted_at   TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, challenge_id)
);

CREATE TABLE IF NOT EXISTS solve_tokens (
    token        TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL REFERENCES users(id),
    challenge_id TEXT NOT NULL REFERENCES challenges(id),
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS solves (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        TEXT NOT NULL REFERENCES users(id),
    challenge_id   TEXT NOT NULL REFERENCES challenges(id),
    flag           TEXT,
    stage          INTEGER NOT NULL DEFAULT 1,
    points_awarded INTEGER NOT NULL DEFAULT 0,
    solved_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, challenge_id, stage)
);
"""


def get_db():
    if 'db' not in g:
        import sqlite3
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA journal_mode=WAL')
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()


def init_db():
    import sqlite3
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)

    # Seed Pokemorty challenge (idempotent — uses INSERT OR IGNORE)
    pokemorty_secret = os.environ.get('POKEMORTY_WEBHOOK_SECRET')
    if not pokemorty_secret:
        # Check if one already exists in DB so we don't regenerate
        existing = db.execute("SELECT webhook_secret FROM challenges WHERE id='pokemorty'").fetchone()
        pokemorty_secret = existing[0] if existing else secrets.token_hex(32)

    db.execute("""
        INSERT OR IGNORE INTO challenges
            (id, slug, name, description, url, category, difficulty, points, total_stages, webhook_secret)
        VALUES
            ('pokemorty', 'pokemorty', 'Pokemorty',
             'A Rick and Morty themed challenge. Steganography, SQL injection, and IDOR. Three stages. Good luck.',
             'https://pokemorty.fly.dev', 'web', 'medium', 300, 3, ?)
    """, (pokemorty_secret,))
    db.commit()
    db.close()


init_firebase()
init_db()

# ── Auth helpers ──────────────────────────────────────────────────────────────


def current_user():
    if 'user_id' not in session:
        return None
    return get_db().execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.path))
        user = get_db().execute('SELECT is_admin FROM users WHERE id=?', (session['user_id'],)).fetchone()
        if not user or not user['is_admin']:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ── Public routes ─────────────────────────────────────────────────────────────


@app.route('/')
def index():
    db = get_db()
    challenges = db.execute('SELECT * FROM challenges WHERE is_active=1 ORDER BY created_at').fetchall()
    events = db.execute('SELECT * FROM events WHERE is_active=1 ORDER BY start_time DESC').fetchall()
    user = current_user()

    solved_ids = set()
    solve_counts = {}
    if user:
        rows = db.execute(
            'SELECT DISTINCT challenge_id FROM solves WHERE user_id=?', (user['id'],)
        ).fetchall()
        solved_ids = {r['challenge_id'] for r in rows}

    for c in challenges:
        row = db.execute(
            'SELECT COUNT(DISTINCT user_id) as n FROM solves WHERE challenge_id=? AND stage=?',
            (c['id'], c['total_stages'])
        ).fetchone()
        solve_counts[c['id']] = row['n'] if row else 0

    return render_template('index.html', challenges=challenges, events=events,
                           user=user, solved_ids=solved_ids, solve_counts=solve_counts)


@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html', firebase_config=firebase_web_config(),
                           next=request.args.get('next', '/dashboard'))


@app.route('/auth/callback', methods=['POST'])
def auth_callback():
    data = request.get_json(force=True) or {}
    id_token = data.get('idToken')
    if not id_token:
        return jsonify({'error': 'missing token'}), 400

    try:
        init_firebase()
        decoded = fb_auth.verify_id_token(id_token)
    except Exception as e:
        return jsonify({'error': str(e)}), 401

    uid = decoded['uid']
    email = decoded.get('email', '')
    display_name = decoded.get('name', email.split('@')[0])
    photo_url = decoded.get('picture', '')

    admin_emails = {e.strip() for e in os.environ.get('ADMIN_EMAILS', '').split(',') if e.strip()}
    is_admin = 1 if email in admin_emails else 0

    db = get_db()
    existing = db.execute('SELECT is_admin FROM users WHERE id=?', (uid,)).fetchone()
    # Never demote an existing admin
    if existing and existing['is_admin']:
        is_admin = 1

    db.execute("""
        INSERT INTO users (id, email, display_name, photo_url, is_admin)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            display_name = excluded.display_name,
            photo_url    = excluded.photo_url,
            is_admin     = MAX(is_admin, excluded.is_admin)
    """, (uid, email, display_name, photo_url, is_admin))
    db.commit()

    session['user_id'] = uid
    session['display_name'] = display_name
    session.permanent = True

    next_url = data.get('next', '/dashboard')
    return jsonify({'ok': True, 'redirect': next_url})


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    user = current_user()
    solves = db.execute("""
        SELECT s.*, c.name AS challenge_name, c.slug, c.total_stages
        FROM solves s
        JOIN challenges c ON s.challenge_id = c.id
        WHERE s.user_id = ?
        ORDER BY s.solved_at DESC
    """, (user['id'],)).fetchall()

    total_points = db.execute(
        'SELECT COALESCE(SUM(points_awarded),0) AS pts FROM solves WHERE user_id=?', (user['id'],)
    ).fetchone()['pts']

    # Progress per challenge: max stage reached
    progress = {}
    for s in solves:
        cid = s['challenge_id']
        if cid not in progress or s['stage'] > progress[cid]['stage']:
            progress[cid] = dict(s)

    challenges = db.execute('SELECT * FROM challenges WHERE is_active=1').fetchall()

    return render_template('dashboard.html', user=user, solves=solves,
                           total_points=total_points, progress=progress,
                           challenges=challenges)


@app.route('/leaderboard')
def leaderboard():
    db = get_db()
    rankings = db.execute("""
        SELECT u.display_name, u.photo_url,
               COUNT(DISTINCT s.challenge_id) AS challenges_solved,
               COALESCE(SUM(s.points_awarded), 0) AS total_points,
               MAX(s.solved_at) AS last_solve
        FROM users u
        JOIN solves s ON u.id = s.user_id
        GROUP BY u.id
        ORDER BY total_points DESC, last_solve ASC
        LIMIT 100
    """).fetchall()
    user = current_user()
    return render_template('leaderboard.html', rankings=rankings, user=user)


@app.route('/events/<slug>')
def event_detail(slug):
    db = get_db()
    event = db.execute('SELECT * FROM events WHERE slug=? AND is_active=1', (slug,)).fetchone()
    if not event:
        abort(404)

    challenges = db.execute("""
        SELECT c.* FROM challenges c
        JOIN event_challenges ec ON c.id = ec.challenge_id
        WHERE ec.event_id = ? AND c.is_active = 1
    """, (event['id'],)).fetchall()

    user = current_user()
    solved_ids = set()
    if user:
        rows = db.execute(
            'SELECT DISTINCT challenge_id FROM solves WHERE user_id=?', (user['id'],)
        ).fetchall()
        solved_ids = {r['challenge_id'] for r in rows}

    leaderboard = db.execute("""
        SELECT u.display_name, u.photo_url,
               COUNT(DISTINCT s.challenge_id) AS solved,
               COALESCE(SUM(s.points_awarded), 0) AS points,
               MAX(s.solved_at) AS last_solve
        FROM solves s
        JOIN users u ON s.user_id = u.id
        WHERE s.challenge_id IN (
            SELECT challenge_id FROM event_challenges WHERE event_id=?
        )
        GROUP BY s.user_id
        ORDER BY points DESC, last_solve ASC
        LIMIT 50
    """, (event['id'],)).fetchall()

    return render_template('event.html', event=event, challenges=challenges,
                           user=user, solved_ids=solved_ids, leaderboard=leaderboard)


# ── Challenge launch (generates solve token) ──────────────────────────────────


@app.route('/play/<slug>')
@login_required
def play_challenge(slug):
    db = get_db()
    challenge = db.execute(
        'SELECT * FROM challenges WHERE slug=? AND is_active=1', (slug,)
    ).fetchone()
    if not challenge:
        abort(404)

    user = current_user()

    # Check access code requirement
    if challenge['requires_code']:
        has_access = db.execute(
            'SELECT 1 FROM challenge_access WHERE user_id=? AND challenge_id=?',
            (user['id'], challenge['id'])
        ).fetchone()
        if not has_access:
            return render_template('unlock.html', challenge=challenge, user=user, error=None)

    # Generate a solve token so the challenge can report progress back
    token = secrets.token_urlsafe(32)
    db.execute(
        'INSERT INTO solve_tokens (token, user_id, challenge_id) VALUES (?, ?, ?)',
        (token, user['id'], challenge['id'])
    )
    db.commit()

    target = challenge['url']
    separator = '&' if '?' in target else '?'
    return redirect(f"{target}{separator}hub_token={token}")


@app.route('/play/<slug>/unlock', methods=['POST'])
@login_required
def unlock_challenge(slug):
    import hashlib
    db = get_db()
    challenge = db.execute('SELECT * FROM challenges WHERE slug=? AND is_active=1', (slug,)).fetchone()
    if not challenge:
        abort(404)

    user = current_user()
    code = request.form.get('access_code', '').strip()
    code_hash = hashlib.sha256(code.encode()).hexdigest()

    if code_hash == challenge['access_code_hash']:
        db.execute(
            'INSERT OR IGNORE INTO challenge_access (user_id, challenge_id) VALUES (?,?)',
            (user['id'], challenge['id'])
        )
        db.commit()
        return redirect(url_for('play_challenge', slug=slug))

    return render_template('unlock.html', challenge=challenge, user=user, error='Invalid access code.')


# ── Webhook (called by challenge apps to report solves) ───────────────────────


@app.route('/api/webhook/solve', methods=['POST'])
def webhook_solve():
    data = request.get_json(force=True) or {}
    challenge_slug = data.get('challenge')
    webhook_secret = data.get('secret')
    hub_token = data.get('token')
    stage = int(data.get('stage', 1))
    flag = data.get('flag', '')

    if not all([challenge_slug, webhook_secret, hub_token]):
        abort(400)

    db = get_db()
    challenge = db.execute('SELECT * FROM challenges WHERE slug=?', (challenge_slug,)).fetchone()
    if not challenge or challenge['webhook_secret'] != webhook_secret:
        abort(403)

    token_row = db.execute(
        'SELECT user_id FROM solve_tokens WHERE token=? AND challenge_id=?',
        (hub_token, challenge['id'])
    ).fetchone()
    if not token_row:
        return jsonify({'ok': False, 'reason': 'unknown token'})

    user_id = token_row['user_id']
    points = (challenge['points'] // challenge['total_stages']) * stage
    if stage == challenge['total_stages']:
        # Final stage gets any rounding remainder too
        points = challenge['points']

    db.execute("""
        INSERT OR IGNORE INTO solves (user_id, challenge_id, flag, stage, points_awarded)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, challenge['id'], flag, stage, points))
    db.commit()

    return jsonify({'ok': True})


# ── Admin routes ──────────────────────────────────────────────────────────────


@app.route('/admin')
@admin_required
def admin_index():
    db = get_db()
    stats = {
        'users':      db.execute('SELECT COUNT(*) AS n FROM users').fetchone()['n'],
        'challenges': db.execute('SELECT COUNT(*) AS n FROM challenges').fetchone()['n'],
        'solves':     db.execute('SELECT COUNT(*) AS n FROM solves').fetchone()['n'],
        'events':     db.execute('SELECT COUNT(*) AS n FROM events').fetchone()['n'],
    }
    recent_solves = db.execute("""
        SELECT s.solved_at, u.display_name, c.name AS challenge_name,
               s.stage, c.total_stages, s.points_awarded
        FROM solves s
        JOIN users u ON s.user_id = u.id
        JOIN challenges c ON s.challenge_id = c.id
        ORDER BY s.solved_at DESC LIMIT 20
    """).fetchall()
    return render_template('admin/index.html', user=current_user(),
                           stats=stats, recent_solves=recent_solves)


@app.route('/admin/challenges')
@admin_required
def admin_challenges():
    db = get_db()
    challenges = db.execute('SELECT * FROM challenges ORDER BY created_at DESC').fetchall()
    return render_template('admin/challenges.html', user=current_user(), challenges=challenges)


@app.route('/admin/challenges/new', methods=['POST'])
@admin_required
def admin_create_challenge():
    import hashlib
    db = get_db()
    slug = request.form['slug'].strip().lower().replace(' ', '-')
    access_code = request.form.get('access_code', '').strip()

    db.execute("""
        INSERT INTO challenges
            (id, slug, name, description, url, category, difficulty, points,
             total_stages, is_active, requires_code, access_code_hash, webhook_secret)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
    """, (
        secrets.token_hex(8), slug,
        request.form['name'],
        request.form.get('description', ''),
        request.form.get('url', ''),
        request.form.get('category', 'web'),
        request.form.get('difficulty', 'medium'),
        int(request.form.get('points', 100)),
        int(request.form.get('total_stages', 1)),
        1 if access_code else 0,
        hashlib.sha256(access_code.encode()).hexdigest() if access_code else None,
        secrets.token_hex(32),
    ))
    db.commit()
    return redirect(url_for('admin_challenges'))


@app.route('/admin/challenges/<cid>/toggle', methods=['POST'])
@admin_required
def admin_toggle_challenge(cid):
    db = get_db()
    db.execute('UPDATE challenges SET is_active = 1 - is_active WHERE id=?', (cid,))
    db.commit()
    return redirect(url_for('admin_challenges'))


@app.route('/admin/challenges/<cid>/secret')
@admin_required
def admin_challenge_secret(cid):
    db = get_db()
    c = db.execute('SELECT webhook_secret FROM challenges WHERE id=?', (cid,)).fetchone()
    if not c:
        abort(404)
    return jsonify({'webhook_secret': c['webhook_secret']})


@app.route('/admin/events')
@admin_required
def admin_events():
    db = get_db()
    events = db.execute('SELECT * FROM events ORDER BY created_at DESC').fetchall()
    challenges = db.execute('SELECT * FROM challenges WHERE is_active=1').fetchall()
    return render_template('admin/events.html', user=current_user(),
                           events=events, challenges=challenges)


@app.route('/admin/events/new', methods=['POST'])
@admin_required
def admin_create_event():
    db = get_db()
    eid = secrets.token_hex(8)
    slug = request.form['slug'].strip().lower().replace(' ', '-')
    db.execute("""
        INSERT INTO events (id, slug, name, description, start_time, end_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        eid, slug,
        request.form['name'],
        request.form.get('description', ''),
        request.form.get('start_time') or None,
        request.form.get('end_time') or None,
    ))
    for cid in request.form.getlist('challenges'):
        db.execute('INSERT OR IGNORE INTO event_challenges VALUES (?,?)', (eid, cid))
    db.commit()
    return redirect(url_for('admin_events'))


@app.route('/admin/events/<eid>/toggle', methods=['POST'])
@admin_required
def admin_toggle_event(eid):
    db = get_db()
    db.execute('UPDATE events SET is_active = 1 - is_active WHERE id=?', (eid,))
    db.commit()
    return redirect(url_for('admin_events'))


@app.route('/admin/users')
@admin_required
def admin_users():
    db = get_db()
    users = db.execute("""
        SELECT u.*, COALESCE(SUM(s.points_awarded),0) AS total_points,
               COUNT(DISTINCT s.challenge_id) AS challenges_solved
        FROM users u
        LEFT JOIN solves s ON u.id = s.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """).fetchall()
    return render_template('admin/users.html', user=current_user(), users=users)


@app.route('/admin/users/<uid>/toggle-admin', methods=['POST'])
@admin_required
def admin_toggle_user_admin(uid):
    # Prevent self-demotion
    if uid == session.get('user_id'):
        return redirect(url_for('admin_users'))
    db = get_db()
    db.execute('UPDATE users SET is_admin = 1 - is_admin WHERE id=?', (uid,))
    db.commit()
    return redirect(url_for('admin_users'))


# ── Error handlers ────────────────────────────────────────────────────────────


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access denied.'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Not found.'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error.'), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
