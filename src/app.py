from flask import Flask, render_template, request, make_response, redirect, send_from_directory
from os import getenv
from random import randint
from itertools import product
from functools import wraps
import sqlite3

app = Flask(__name__)
conn = sqlite3.connect('database.db')


# Load initial data
FLAG=getenv("SECRET", "ABK{I_LOVE_POKEMON}")
conn.execute('CREATE TABLE IF NOT EXISTS pokemon_masters (master_id INTEGER PRIMARY KEY ASC, username TEXT, password TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS pokemons (pokemon_id INTEGER PRIMARY KEY, pokemon_name TEXT, pokemon_image TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS pokemons_discovered (master_id INTEGER, pokemon_id INTEGER, FOREIGN KEY(master_id) REFERENCES pokemon_masters(master_id), FOREIGN KEY(pokemon_id) REFERENCES pokemons(pokemon_id))')
pokemons_file = open("./src/misc/pokemons", "r")
pokemons_data = pokemons_file.readlines()
pokemons = list()
for pokemon_data in pokemons_data:
    if "\n" in pokemon_data:
        pokemon_data = pokemon_data[:-1]
    pokemons.append(pokemon_data.split("\\\\----\\\\"))
conn.executemany("INSERT OR IGNORE INTO pokemons (pokemon_id, pokemon_name, pokemon_image) values (?, ?, ?)", pokemons)
conn.execute("INSERT OR IGNORE INTO pokemon_masters (master_id, username, password) values (?, ?, ?)", (130 ,getenv("RICK_NAME", "rick"), getenv("RICK_PASSWORD", "sanchez")))
conn.execute("INSERT OR IGNORE INTO pokemon_masters (username, password) values ('lrutter0', '6Q4ZHCfdK'), ('hhorsburgh1', 'yLrlpgC'), ('vklageman2', 'rDXuu6jm'), ('oviegas3', '3iRj5R7Y'), ('wfleming4', 'gZ4Trd'), ('pcorrie5', 'V2ZHqoE6'), ('hwebster6', 'fsMjJxC'), ('wmacallester7', 'Qm4bOfMX'), ('dwilce8', 'pNYYtA3sVHY'), ('agirardey9', 'z2iz2V6pR0Sq'), ('tvanshina', 'SjdV20drm'), ('csollandb', 'NdPpD0rFB6'), ('drosebyc', 'yShglY'), ('rrizzardid', 'OoGDNOIVtET'), ('lalfordee', 'd7fCM9a'), ('dsmyf', 'rB8PQFd'), ('fspoerlg', 'Ocht3V8bt2YB'), ('noheagertieh', 'RwFd7gv6tD2'), ('fmatyushkini', 'Ee21yWnYF'), ('efitzgibbonj', 'JiBsiDEi'), ('lmittenk', 'wqlXZM4KBA'), ('lharmarl', 'z60ei0t'), ('agilbodym', 'ngn4MZ'), ('kposselln', 'pV4ZyXQW98z'), ('tharlowo', 'yKMTzbv5F'), ('hskeatp', '9e8D9Vrmfvno'), ('cbodegaq', 'Gh5vdxxAanu'), ('rfinlanr', 'PY5R9jvc'), ('mjacobis', 'E6qgUp'), ('kkrauzet', '0KhSltO7aZ'), ('fpertu', 'TjgO9kd5ROS'), ('gpeterkenv', 'DFjRCipchWqK'), ('oheaffeyw', 'y5puTN'), ('stoulamainx', 'bgeWUHVgCxny'), ('fminnocky', 'Dmugx25kV'), ('ttadgellz', 'QNgPqgZgjK'), ('rmcgannon10', 'ZO1pRMs7UINp'), ('gpurple11', '324lmnJ'), ('mmullen12', 'Pr5moNa'), ('brobison13', '88Ts77'), ('sdils14', 'qY0RN0UQux'), ('mroggeman15', 'yHDs9A'), ('bbartels16', '1aUx6bBdxO'), ('mcoots17', 'MkdS6WBwV'), ('ebernardoux18', '1RXG6h0'), ('zkingston19', 'DehJzcl'), ('oloftin1a', 'cUjZsJBRoGd'), ('gmeneghi1b', 'Kdr5se3g5E6'), ('jevers1c', 'zXkPLv4Hee7M'), ('yperfili1d', 'CSSL46O'), ('jmoulson1e', '9K688dAXqc'), ('zkingsnorth1f', 'wuPFDQgaM3G'), ('atrevance1g', 'pVvbaH'), ('bbeiderbecke1h', 'L4XYUY5O'), ('glille1i', '18NngBHZLh'), ('dheape1j', 'n3lwAkE1Xt'), ('dfalls1k', 'rp5lyYbZc'), ('showsin1l', 'CnlCUNy4'), ('kbundey1m', 'sEvNH1W'), ('rwale1n', '4wUpUrB'), ('asilberschatz1o', 'IPXF9CZAwaE2'), ('gmacnab1p', '0KegQhUUZMxl'), ('rcoldbath1q', 'zLZyuPDuQnes'), ('mdodding1r', 'ok2G5JgUj'), ('tsorby1s', 'qLHnndI'), ('kmully1t', 'kHaWyV'), ('pcheeney1u', 'Qj1C8uQLD2'), ('mflacknell1v', 'dRWNI3OZG'), ('csummersby1w', 'LL83a8'), ('akorpal1x', 'djlFOp7v'), ('vinkpen1y', 'IqvYldmYw2Y'), ('bstruttman1z', 'U8zC3DEiX'), ('pmilkeham20', 'Z9bIQuN'), ('gshenley21', 'n3e29zTqwrK'), ('pbrigden22', 'R6Wr7K1icP'), ('rbrownbill23', '6KCWVtdAg'), ('mturfitt24', 'K1S7aMTse2I'), ('cbaxstare25', '2aaHhL3hKd'), ('elile26', 'KcOntHW8'), ('pboom27', 'QxIbQuD'), ('ariddle28', '55186wjj'), ('kjurasz29', 'hdqkSTj0aDhA'), ('ctonn2a', '55MOpymID'), ('scommon2b', 'LPV76eWxeVff'), ('mchurm2c', 'BPecBlms'), ('mmashal2d', 'Xv29Ubp'), ('cpires2e', 'OtemlJaZ'), ('pboteman2f', 'pb4IVB2'), ('cpenk2g', '4Q7y83A'), ('spevie2h', 'JRmume'), ('bgeffinger2i', 'wRFoeWT'), ('aforst2j', 'VIZq7Lmjr'), ('ecassius2k', 'nBjfHR23L'), ('kovershott2l', 'DaYwepEy'), ('bbuckley2m', 'NpWbkBjiNk7'), ('rgilkison2n', 'VcaAZwBu97'), ('okolakowski2o', '6KzUi7'), ('sgayle2p', '9gEJ24JqGK'), ('cinchbald2q', 'hiIFc2bw'), ('emenguy2r', 'ZBuzDXK72sA'), ('rcrangle2s', 'NSXicWRNi'), ('hbetje2t', 'rlnSPCap'), ('rtroke2u', '6ywVoli'), ('ascoffins2v', '0keeX0CNJi5'), ('gcatmull2w', 'SX4Uzyyy'), ('ctitterington2x', 'QAi8YhG'), ('hboustred2y', '9TAT2JYBB'), ('lnorwell2z', 'whc3QSvC'), ('ngilding30', 'MWanKgyeN'), ('gtainton31', 's6TtShx'), ('mwhittlesea32', 'UH5WgJwE'), ('mgaughan33', 'zstFzIgd'), ('gclemencet34', 'yhIkWkVrk'), ('bmcgiff35', 'Ws4BWwYft1U'), ('zraikes36', 'ct3By6pl6gA7'), ('biwanczyk37', 'uZHeEaoB'), ('alinskill38', 'zQ4Ac34t'), ('jvarian39', 'lYw6ZS8NBMgF'), ('kconboy3a', 'KnpmQjE'), ('acarnegie3b', 'NFdETEPrN8'), ('agerretsen3c', 'saGh4BS4L'), ('esiggin3d', 'ORZAhW8QX'), ('tmicheli3e', 'p3RL0AsEq'), ('alamswood3f', 'l2hHGsz'), ('gbellefant3g', 'QXkvCbieo'), ('rleckie3h', 'vCSrtgM'), ('bpoznanski3i', 'xrddyqgNVsZc'), ('rwadhams3j', 'SLuelzncWwC'), ('dhabberjam3k', 'AAil4jZhp'), ('rpetford3l', 'rdz9JFE'), ('wbang3m', 'jMdFUN'), ('skasparski3n', 'iCA3oZ'), ('femanuele3o', 'PSoHG4e5f'), ('screeghan3p', 'd5YGQJmW4pM'), ('charce3q', 'KcREcZ6Z5S0v'), ('lwolsey3r', '8OvKjEvQ'), ('cmelpuss3s', 'Kx5Hmil'), ('kwiltshire3t', 'FQkldSpRWVt'), ('aleat3u', 'tnNsKB5qo4f9'), ('bwhitechurch3v', 'dcvRkmvtgh'), ('aadcocks3w', 'qpi9mUE'), ('lausello3x', 'zdWQAtKO'), ('kfleming3y', 'Xi0YFJij0PS'), ('fstitch3z', 'K1qthGnt8D'), ('cbroke40', 'y39Tp1ARjKjD'), ('vdaleman41', 'NKk3dP'), ('zclissett42', 'ZonQYuHjKh'), ('ltregaskis43', 'sP6uRGDRi'), ('aronisch44', '41Oq7Iq'), ('nwye45', 'eybAYXiaD3'), ('ksainz46', 'KFDpg4Ja'), ('jclaessens47', 'woXJUReBlsH'), ('vjindra48', 'VRRCdjnD'), ('abrownbridge49', 'j2Tm4RXPOAgt'), ('htinton4a', 'GgALS7jLM'), ('ffreddi4b', '6oRiiWS'), ('cclawe4c', '5FzikeHAWxFU'), ('htanti4d', 'LcmLX9G'), ('rwindrum4e', 'GCUNIxLyzzt'), ('dthreader4f', 'rviYlbJcB'), ('hcumpsty4g', 'yHad5sDHn'), ('lambrois4h', 'oDz0MTbhMI'), ('imckie4i', 'bWNT93WB'), ('rcurnnok4j', 'UnOotuXQR6'), ('rromeril4k', '7zSFauA2A4DX'), ('adignum4l', 'JUcTY0KZvJ'), ('dfasey4m', 'SCzwXHFO12'), ('meadon4n', 'W5AQaP6'), ('atomkys4o', 'w0052H6DFnKn'), ('ldurkin4p', 'oGimUuGLls'), ('jfraschetti4q', '26TDY1bkLcWQ'), ('dandrich4r', 'oiV7jn7EXCB'), ('aamey4s', 'PpSgar'), ('sjozef4t', 'IJGYaFUmXHT'), ('dcampanelli4u', 'JBQDC6Ru'), ('dcannings4v', 'xhyxFKHi'), ('partist4w', 'BiWojR7G4'), ('hstannah4x', 'uxzDjG29'), ('msarre4y', 'xqR4SMvIr'), ('bterbeck4z', 'kiY6Idz'), ('msteels50', '7yujYqzG'), ('arule51', '0Kl493A'), ('clavarack52', 'T7RzBRpn'), ('elording53', 'esU98VAmht'), ('sgiacobillo54', 'cJjsCO'), ('fwalters55', 'YbXXqJON7WG'), ('tvandenvelde56', 'XM69mQJHp'), ('hlangstone57', 'zqVoCQ'), ('kgerardin58', 'oEvG7TGTkxa2'), ('fquaif59', '0evd5M4f')")
if conn.execute("SELECT COUNT(*) FROM pokemons_discovered").fetchone()[0] == 0:
    pokemons_discovered = [item for sublist in list(product([trainer], list(range(randint(1,50), randint(51,129), 8))) for trainer in list(range(1, 129, 1))) for item in sublist]
    others = list(product([130], range(1,152,1)))
    conn.executemany("INSERT OR IGNORE INTO pokemons_discovered (master_id, pokemon_id) values (?, ?)", pokemons_discovered + others)
conn.commit()
conn.close()


def validate_auth(wrapped_function):
    @wraps(wrapped_function)
    def _wrapper(*args, **kwargs):
        authenticated_cookie = request.cookies.get("authenticated")
        master_id_cookie = request.cookies.get("master_id")
        if authenticated_cookie and master_id_cookie and authenticated_cookie == "NOW_WE_ARE_TALKING":
            return wrapped_function(*args, **kwargs)
        else:
            response = make_response(render_template("login.html", incorrect_password=True))
            response.delete_cookie("authenticated")
            response.delete_cookie("master_id")
            response.delete_cookie("username")
            return response
    return _wrapper


def check_authentication_successfully(form):
    try:
        username, password = form.get("username"), form.get("password")
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        result = conn.executescript("SELECT master_id, password FROM pokemon_masters WHERE username = '{0}'".format(username))
        result_raw = result.fetchone()
        if result_raw:
            password_data = dict(result_raw)
            if password_data and password_data.get("password") == password:
                return password_data.get("master_id")
        return None
    except:
        return None

@app.route("/challenge")
def challenge():
    winner_cookie = request.cookies.get("challenge", "LOOSER")
    winner = True if winner_cookie == "YEAH" else False
    looser = True if winner_cookie == "LOOSER" else False
    return render_template("challenge.html", winner=winner, looser=looser)

@app.route("/challenge_validation", methods=["POST"])
def challenge_validation():
    form = request.form
    if form and form.get("passcode"):
        if str(form["passcode"]).upper() == "11CK0001":
            response = redirect("/login")
            response.set_cookie("challenge", "YEAH")
            return response
    response = redirect("/challenge")
    response.set_cookie("challenge", "LOOSER")
    return response

@app.route("/authenticate", methods=["POST"])
def authenticate():
    form = request.form
    if not form:
        response = make_response(render_template("login.html", incorrect_password=True))
        response.delete_cookie("authenticated")
        response.delete_cookie("master_id")
        response.delete_cookie("username")
        return response
    master_id = check_authentication_successfully(form)
    if master_id:
        response = make_response(render_template("index.html", pokemon_master=form.get("username")  , hide=False))
        response.set_cookie("authenticated", "NOW_WE_ARE_TALKING")
        response.set_cookie("master_id", str(master_id))
        response.set_cookie("username", form.get("username"))
        return response
    else:
        response = make_response(render_template("login.html", incorrect_password=True))
        response.delete_cookie("authenticated")
        response.delete_cookie("master_id")
        response.delete_cookie("username")
        return response

@app.route("/flag")
@validate_auth
def get_flag():
    form = request.form
    if form and form.get("flag"):
        if form.get("flag") == FLAG:
            conn
            return "OK"

@app.route("/login")
def login():
    response = make_response(render_template("login.html", incorrect_password=False))
    return response

@app.route("/completed")
def completed():
    response = make_response(render_template("completed.html"))
    return response

@app.route("/")
@validate_auth
def index():
    master_id = request.cookies.get("master_id")
    username = request.cookies.get("username")
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    result = conn.execute("SELECT P.* FROM pokemons AS P LEFT JOIN pokemons_discovered PD ON P.pokemon_id = PD.pokemon_id where PD.master_id = %s" % master_id)
    pokemon_list = list(map(lambda p: dict(p), result.fetchall()))
    response = make_response(render_template("index.html", pokemon_master=username, pokemon_list=pokemon_list))
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)