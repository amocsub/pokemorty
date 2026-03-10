# CLAUDE.md — Pokemorty CTF Challenge

This file provides AI assistants with everything needed to understand, navigate, and work on this repository effectively.

## Project Overview

**Pokemorty** is an educational Capture The Flag (CTF) web application built with Python/Flask. It is Rick and Morty themed and intentionally contains several classic web security vulnerabilities (SQL Injection, IDOR, steganography) for participants to exploit as part of a three-stage challenge. The project is used for internal security training competitions.

**Live URL**: https://pokemorty.fly.dev
**Solution Guide**: `doc/solution/readme.md`

---

## Repository Structure

```
pokemorty/
├── app.py                          # Main Flask application (single-file backend)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Multi-stage Docker build
├── fly.toml                        # Fly.io deployment configuration
├── readme.md                       # Project README
├── CLAUDE.md                       # This file
├── .github/
│   └── workflows/
│       └── fly-deploy.yml          # CI/CD: auto-deploy to Fly.io on push to main
├── templates/                      # Jinja2 HTML templates
│   ├── index.html                  # Home page (contains binary-encoded hint)
│   ├── login.html                  # Login page (vulnerable to SQL injection)
│   ├── challenge.html              # CAPTCHA challenge page
│   ├── pokedex.html                # Pokémon list for authenticated user
│   ├── you_have_found_the_flag.html # Success/flag found page
│   └── 404.html                    # Error page
├── static/                         # Static assets (images, favicon)
│   ├── captcha.jpg                 # CAPTCHA image with steganographic hint
│   ├── flag_found.gif
│   ├── rick-and-morty-dancing.gif
│   └── ...
├── misc/
│   └── pokemons                    # Newline-separated list of 150 Pokémon names
└── doc/
    └── solution/
        └── readme.md               # Full step-by-step solution walkthrough
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10.13 |
| Web Framework | Flask |
| Templating | Jinja2 (server-side rendering) |
| Database | SQLite (initialized fresh at startup) |
| Production Server | Gunicorn |
| Containerization | Docker (multi-stage build) |
| Hosting | Fly.io (region: CDG/Paris) |
| CI/CD | GitHub Actions |

**Dependencies** (`requirements.txt`):
- `flask` — web framework
- `gunicorn` — WSGI production server
- `requests` — HTTP client (used for Telegram notification)

---

## Application Architecture

### Single-File Flask App (`app.py`)

The entire backend lives in `app.py` (~303 lines). It follows a monolithic structure:

1. **Database initialization** (`init_db()`) — runs on startup, creates SQLite tables, loads 150 Pokémon, and creates 190 user accounts with SHA1-hashed passwords.
2. **Decorator-based middleware** — authentication and authorization are implemented as Python decorators applied to route functions.
3. **Route handlers** — each Flask route is a function decorated with auth validators.
4. **Jinja2 template rendering** — all pages are server-side rendered HTML.

### Database Schema (SQLite)

Three tables, created fresh on every startup:

```sql
-- User accounts (190 pre-populated entries)
pokemon_masters (
    master_id  INTEGER PRIMARY KEY,
    username   TEXT,
    password   TEXT   -- SHA1 hash
)

-- Pokémon catalog (150 entries from misc/pokemons)
pokemons (
    pokemon_id    INTEGER PRIMARY KEY,
    pokemon_hash  TEXT,   -- SHA1 hash of pokemon_name
    pokemon_name  TEXT,
    pokemon_image TEXT    -- Base64-encoded image fetched from PokéAPI
)

-- Many-to-many: which user owns which Pokémon
pokemons_discovered (
    master_id   INTEGER,  -- FK → pokemon_masters
    pokemon_id  INTEGER   -- FK → pokemons
)
```

### Authentication / Authorization Flow

Authentication state is tracked entirely via HTTP cookies (no server-side sessions):

| Cookie | Value | Set When |
|--------|-------|----------|
| `flag` | `I_HAVE_NOT_FOUND_THE_FLAG` | Default; changed when flag is found |
| `challenge` | `YEAH` | After solving the CAPTCHA challenge |
| `NOW_WE_ARE_TALKING` | Base64-encoded query result | After successful login |
| `master_id` | Integer user ID | After successful login |

Decorator validators check cookies before allowing access to protected routes:
- `@validate_flag_found` — redirects to success page if flag already found
- `@validate_challenge` — redirects to `/challenge` if CAPTCHA not completed
- `@validate_authentication_cookie` — redirects to `/login` if not logged in
- `@validate_pokemon_owned` — 403 if user doesn't own the requested Pokémon

---

## API Routes / Endpoints

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Home page with hidden binary hint |
| `/challenge` | GET | CAPTCHA challenge page |
| `/challenge_validation` | POST | Submit CAPTCHA answer ("PIKACHU") |
| `/login` | GET | Login form page |
| `/authenticate` | POST | Process login credentials (**SQL-injectable**) |
| `/pokedex` | GET | Display user's discovered Pokémon (**IDOR-vulnerable**) |
| `/pokemon/<pokemon_hash>` | GET | Download Pokémon image file |
| `/01100110011011000110000101100111` | POST | Flag submission endpoint (route is binary-encoded) |
| `/you_have_found_the_flag` | GET | Success page |
| `/restore_database` | GET | Reset the database to initial state |

---

## Intentional Vulnerabilities (CTF Stages)

This application is **intentionally vulnerable**. Do not "fix" these unless specifically asked:

### Stage 1 — Steganography / Recon
- The home page (`/`) displays binary-encoded text that decodes to a path.
- Hidden Braille text and HTML comments provide additional hints.
- `static/captcha.jpg` contains a hidden steganographic message identifying "PIKACHU" as the CAPTCHA answer.

### Stage 2 — SQL Injection
- The login form at `/authenticate` uses **unparameterized string formatting**:
  ```python
  # app.py ~line 120 — INTENTIONALLY VULNERABLE
  query = f"SELECT * FROM pokemon_masters WHERE username='{username}' AND password='{password}'"
  ```
- Classic payloads like `' OR 1=1 --` allow authentication bypass and data extraction.

### Stage 3 — IDOR (Insecure Direct Object Reference)
- The `master_id` cookie controls which user's Pokémon are shown in `/pokedex`.
- Changing `master_id` to another user's ID (e.g., Rick Sanchez's) exposes their Pokémon.
- The flag `FLAG{I_LOVE_POKEMON}` is hidden steganographically inside a Pokémon image.

---

## Development Workflow

### Local Setup

```bash
# Install dependencies (Python 3.10+ recommended)
pip install -r requirements.txt

# Run development server
python app.py
# or
flask run
```

The app initializes the SQLite database on first run. The database is ephemeral (recreated on each start).

### Docker Build & Run

```bash
docker build -t pokemorty .
docker run -p 8080:8080 pokemorty
```

### Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `PORT` | No | HTTP port (default: 8080) |
| `FLY_API_TOKEN` | CI only | Fly.io deployment token (GitHub secret) |

No `.env` file is needed for local development.

### Database Reset

Visit `/restore_database` in a browser (no auth required) to re-initialize the SQLite database to its default state with all 190 users and 150 Pokémon.

---

## CI/CD Pipeline

Defined in `.github/workflows/fly-deploy.yml`:
- **Trigger**: Push to `main` branch
- **Action**: `flyctl deploy --remote-only` (builds Docker image remotely on Fly.io)
- **Auth**: `FLY_API_TOKEN` GitHub secret
- **Concurrency**: One deployment at a time (cancels in-progress runs)

Deployments go to the `pokemorty` app on Fly.io in the CDG region.

---

## Key Conventions & Patterns

### Code Style
- Pure Python, no type annotations, no linting config.
- Single-file Flask pattern — all routes, helpers, and DB logic in `app.py`.
- Decorator-based auth/validation applied directly to route handlers.
- `get_db()` / `close_db()` helpers for SQLite connection management with Flask `g`.

### Templates
- Standard Jinja2 with `{{ variable }}` and `{% block %}` patterns.
- No template inheritance base layout — each template is standalone.
- Hidden challenge hints embedded as HTML comments, invisible text, or encoding tricks.

### Static Assets
- Images stored in `static/` and served by Flask's built-in static file handler.
- Pokémon images are fetched from the PokéAPI at DB initialization time and stored as Base64 in SQLite.
- Challenge images may contain steganographic data — do not re-compress or re-export them.

### Security-Sensitive Files
- **Do not parameterize** the SQL query in `app.py:~120` — it is intentionally vulnerable.
- **Do not add** proper session management — cookie-based IDOR is intentional.
- **Do not remove** hidden hints from templates (`index.html`, `login.html`).
- **Do not modify** `static/captcha.jpg` — it contains steganographic data critical to the challenge.

---

## Testing

There are **no automated tests** in this repository. The app is a demonstration challenge and is manually validated by:
1. Running locally and walking through the three challenge stages.
2. Using `/restore_database` to reset state between test runs.

---

## Deployment Notes

- The Fly.io app uses `shared-cpu-1x` machines with min/max of 0–1 instances (auto-start/stop).
- Internal port is 8080; Fly.io handles HTTPS termination and redirects HTTP → HTTPS.
- SQLite database is **ephemeral** — it is re-created every time the container restarts.
- A Telegram bot notification is triggered when a participant successfully captures the flag (bot token is embedded in `app.py`).
