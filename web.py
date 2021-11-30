#! python3
from flask import Flask, render_template, request, make_response, redirect, send_file, abort
from os import getenv, remove, path
from random import randint
from itertools import product
from functools import wraps
import sqlite3
import base64
from io import BytesIO

# -------------------------- #
#       INITIALIZE DB
# -------------------------- #
def init_db():
    if path.exists("database.db"):
        open('database.db', 'w').close()
    conn = sqlite3.connect('database.db')
    conn.execute('CREATE TABLE IF NOT EXISTS pokemon_masters (master_id INTEGER PRIMARY KEY ASC, username TEXT, password TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS pokemons (pokemon_id INTEGER PRIMARY KEY, pokemon_name TEXT, pokemon_image TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS pokemons_discovered (master_id INTEGER, pokemon_id INTEGER, FOREIGN KEY(master_id) REFERENCES pokemon_masters(master_id), FOREIGN KEY(pokemon_id) REFERENCES pokemons(pokemon_id))')
    pokemons_file = open("./misc/pokemons", "r")
    pokemons_data = pokemons_file.readlines()
    pokemons = list()
    for pokemon_data in pokemons_data:
        if "\n" in pokemon_data:
            pokemon_data = pokemon_data[:-1]
        pokemons.append(pokemon_data.split("\\\\----\\\\"))
    conn.executemany("INSERT OR IGNORE INTO pokemons (pokemon_id, pokemon_name, pokemon_image) values (?, ?, ?)", pokemons)
    conn.execute("INSERT OR IGNORE INTO pokemon_masters (master_id, username, password) values (1, 'morty', 'ilovemyfamily'), (2, 'supermorty', 'yLrlpgC'), (3, 'mortytest', 'rDXuu6jm'), (4, 'oviegas3', '3iRj5R7Y'), (5, 'wfleming4', 'gZ4Trd'), (6, 'pcorrie5', 'V2ZHqoE6'), (7, 'hwebster6', 'fsMjJxC'), (8, 'wmacallester7', 'Qm4bOfMX'), (9, 'dwilce8', 'pNYYtA3sVHY'), (10, 'agirardey9', 'z2iz2V6pR0Sq'), (11, 'tvanshina', 'SjdV20drm'), (12, 'csollandb', 'NdPpD0rFB6'), (13, 'drosebyc', 'yShglY'), (14, 'rrizzardid', 'OoGDNOIVtET'), (15, 'lalfordee', 'd7fCM9a'), (16, 'dsmyf', 'rB8PQFd'), (17, 'fspoerlg', 'Ocht3V8bt2YB'), (18, 'noheagertieh', 'RwFd7gv6tD2'), (19, 'fmatyushkini', 'Ee21yWnYF'), (20, 'efitzgibbonj', 'JiBsiDEi'), (21, 'lmittenk', 'wqlXZM4KBA'), (22, 'lharmarl', 'z60ei0t'), (23, 'agilbodym', 'ngn4MZ'), (24, 'kposselln', 'pV4ZyXQW98z'), (25, 'tharlowo', 'yKMTzbv5F'), (26, 'hskeatp', '9e8D9Vrmfvno'), (27, 'cbodegaq', 'Gh5vdxxAanu'), (28, 'rfinlanr', 'PY5R9jvc'), (29, 'mjacobis', 'E6qgUp'), (30, 'kkrauzet', '0KhSltO7aZ'), (31, 'fpertu', 'TjgO9kd5ROS'), (32, 'gpeterkenv', 'DFjRCipchWqK'), (33, 'oheaffeyw', 'y5puTN'), (34, 'stoulamainx', 'bgeWUHVgCxny'), (35, 'fminnocky', 'Dmugx25kV'), (36, 'ttadgellz', 'QNgPqgZgjK'), (37, 'rmcgannon10', 'ZO1pRMs7UINp'), (38, 'gpurple11', '324lmnJ'), (39, 'mmullen12', 'Pr5moNa'), (40, 'brobison13', '88Ts77'), (41, 'sdils14', 'qY0RN0UQux'), (42, 'mroggeman15', 'yHDs9A'), (43, 'bbartels16', '1aUx6bBdxO'), (44, 'mcoots17', 'MkdS6WBwV'), (45, 'ebernardoux18', '1RXG6h0'), (46, 'zkingston19', 'DehJzcl'), (47, 'oloftin1a', 'cUjZsJBRoGd'), (48, 'gmeneghi1b', 'Kdr5se3g5E6'), (49, 'jevers1c', 'zXkPLv4Hee7M'), (50, 'yperfili1d', 'CSSL46O'), (51, 'jmoulson1e', '9K688dAXqc'), (52, 'zkingsnorth1f', 'wuPFDQgaM3G'), (53, 'atrevance1g', 'pVvbaH'), (54, 'bbeiderbecke1h', 'L4XYUY5O'), (55, 'glille1i', '18NngBHZLh'), (56, 'dheape1j', 'n3lwAkE1Xt'), (57, 'dfalls1k', 'rp5lyYbZc'), (58, 'showsin1l', 'CnlCUNy4'), (59, 'kbundey1m', 'sEvNH1W'), (60, 'rwale1n', '4wUpUrB'), (61, 'asilberschatz1o', 'IPXF9CZAwaE2'), (62, 'gmacnab1p', '0KegQhUUZMxl'), (63, 'rcoldbath1q', 'zLZyuPDuQnes'), (64, 'mdodding1r', 'ok2G5JgUj'), (65, 'tsorby1s', 'qLHnndI'), (66, 'kmully1t', 'kHaWyV'), (67, 'pcheeney1u', 'Qj1C8uQLD2'), (68, 'mflacknell1v', 'dRWNI3OZG'), (69, 'csummersby1w', 'LL83a8'), (70, 'akorpal1x', 'djlFOp7v'), (71, 'vinkpen1y', 'IqvYldmYw2Y'), (72, 'bstruttman1z', 'U8zC3DEiX'), (73, 'pmilkeham20', 'Z9bIQuN'), (74, 'gshenley21', 'n3e29zTqwrK'), (75, 'pbrigden22', 'R6Wr7K1icP'), (76, 'rbrownbill23', '6KCWVtdAg'), (77, 'mturfitt24', 'K1S7aMTse2I'), (78, 'cbaxstare25', '2aaHhL3hKd'), (79, 'elile26', 'KcOntHW8'), (80, 'pboom27', 'QxIbQuD'), (81, 'ariddle28', '55186wjj'), (82, 'kjurasz29', 'hdqkSTj0aDhA'), (83, 'ctonn2a', '55MOpymID'), (84, 'scommon2b', 'LPV76eWxeVff'), (85, 'mchurm2c', 'BPecBlms'), (86, 'mmashal2d', 'Xv29Ubp'), (87, 'cpires2e', 'OtemlJaZ'), (88, 'pboteman2f', 'pb4IVB2'), (89, 'cpenk2g', '4Q7y83A'), (90, 'spevie2h', 'JRmume'), (91, 'bgeffinger2i', 'wRFoeWT'), (92, 'aforst2j', 'VIZq7Lmjr'), (93, 'ecassius2k', 'nBjfHR23L'), (94, 'kovershott2l', 'DaYwepEy'), (95, 'bbuckley2m', 'NpWbkBjiNk7'), (96, 'rgilkison2n', 'VcaAZwBu97'), (97, 'okolakowski2o', '6KzUi7'), (98, 'sgayle2p', '9gEJ24JqGK'), (99, 'cinchbald2q', 'hiIFc2bw'), (100, 'emenguy2r', 'ZBuzDXK72sA'), (101, 'rcrangle2s', 'NSXicWRNi'), (102, 'hbetje2t', 'rlnSPCap'), (103, 'rtroke2u', '6ywVoli'), (104, 'ascoffins2v', '0keeX0CNJi5'), (105, 'TheRealMorty', 'SX4Uzyyy'), (106, 'ctitterington2x', 'QAi8YhG'), (107, 'hboustred2y', '9TAT2JYBB'), (108, 'lnorwell2z', 'whc3QSvC'), (109, 'ngilding30', 'MWanKgyeN'), (110, 'gtainton31', 's6TtShx'), (111, 'mwhittlesea32', 'UH5WgJwE'), (112, 'mgaughan33', 'zstFzIgd'), (113, 'gclemencet34', 'yhIkWkVrk'), (114, 'bmcgiff35', 'Ws4BWwYft1U'), (115, 'zraikes36', 'ct3By6pl6gA7'), (116, 'biwanczyk37', 'uZHeEaoB'), (117, 'alinskill38', 'zQ4Ac34t'), (118, 'jvarian39', 'lYw6ZS8NBMgF'), (119, 'kconboy3a', 'KnpmQjE'), (120, 'acarnegie3b', 'NFdETEPrN8'), (121, 'agerretsen3c', 'saGh4BS4L'), (122, 'esiggin3d', 'ORZAhW8QX'), (123, 'tmicheli3e', 'p3RL0AsEq'), (124, 'alamswood3f', 'l2hHGsz'), (125, 'gbellefant3g', 'QXkvCbieo'), (126, 'rleckie3h', 'vCSrtgM'), (127, 'bpoznanski3i', 'xrddyqgNVsZc'), (128, 'rwadhams3j', 'SLuelzncWwC'), (129, 'dhabberjam3k', 'AAil4jZhp'), (130, 'RickSanchez', 'IL0veMorty'), (131, 'wbang3m', 'jMdFUN'), (132, 'skasparski3n', 'iCA3oZ'), (133, 'femanuele3o', 'PSoHG4e5f'), (134, 'Beth11', 'd5YGQJmW4pM'), (135, 'charce3q', 'KcREcZ6Z5S0v'), (136, 'lwolsey3r', '8OvKjEvQ'), (137, 'cmelpuss3s', 'Kx5Hmil'), (138, 'kwiltshire3t', 'FQkldSpRWVt'), (139, 'aleat3u', 'tnNsKB5qo4f9'), (140, 'bwhitechurch3v', 'dcvRkmvtgh'), (141, 'aadcocks3w', 'qpi9mUE'), (142, 'lausello3x', 'zdWQAtKO'), (143, 'JerrySmith', 'Xi0YFJij0PS'), (144, 'fstitch3z', 'K1qthGnt8D'), (145, 'cbroke40', 'y39Tp1ARjKjD'), (146, 'vdaleman41', 'NKk3dP'), (147, 'zclissett42', 'ZonQYuHjKh'), (148, 'ltregaskis43', 'sP6uRGDRi'), (149, 'aronisch44', '41Oq7Iq'), (150, 'nwye45', 'eybAYXiaD3'), (151, 'ksainz46', 'KFDpg4Ja'), (152, 'jclaessens47', 'woXJUReBlsH'), (153, 'vjindra48', 'VRRCdjnD'), (154, 'abrownbridge49', 'j2Tm4RXPOAgt'), (155, 'htinton4a', 'GgALS7jLM'), (156, 'ffreddi4b', '6oRiiWS'), (157, 'cclawe4c', '5FzikeHAWxFU'), (158, 'htanti4d', 'LcmLX9G'), (159, 'rwindrum4e', 'GCUNIxLyzzt'), (160, 'dthreader4f', 'rviYlbJcB'), (161, 'hcumpsty4g', 'yHad5sDHn'), (162, 'lambrois4h', 'oDz0MTbhMI'), (163, 'imckie4i', 'bWNT93WB'), (164, 'rcurnnok4j', 'UnOotuXQR6'), (165, 'rromeril4k', '7zSFauA2A4DX'), (166, 'adignum4l', 'JUcTY0KZvJ'), (167, 'dfasey4m', 'SCzwXHFO12'), (168, 'meadon4n', 'W5AQaP6'), (169, 'atomkys4o', 'w0052H6DFnKn'), (170, 'ldurkin4p', 'oGimUuGLls'), (171, 'jfraschetti4q', '26TDY1bkLcWQ'), (172, 'dandrich4r', 'oiV7jn7EXCB'), (173, 'aamey4s', 'PpSgar'), (174, 'sjozef4t', 'IJGYaFUmXHT'), (175, 'dcampanelli4u', 'JBQDC6Ru'), (176, 'dcannings4v', 'xhyxFKHi'), (177, 'partist4w', 'BiWojR7G4'), (178, 'hstannah4x', 'uxzDjG29'), (179, 'msarre4y', 'xqR4SMvIr'), (180, 'bterbeck4z', 'kiY6Idz'), (181, 'msteels50', '7yujYqzG'), (182, 'arule51', '0Kl493A'), (183, 'clavarack52', 'T7RzBRpn'), (184, 'elording53', 'esU98VAmht'), (185, 'sgiacobillo54', 'cJjsCO'), (186, 'fwalters55', 'YbXXqJON7WG'), (187, 'tvandenvelde56', 'XM69mQJHp'), (188, 'hlangstone57', 'zqVoCQ'), (189, 'kgerardin58', 'oEvG7TGTkxa2'), (190, 'fquaif59', '0evd5M4f')")
    if conn.execute("SELECT COUNT(*) FROM pokemons_discovered").fetchone()[0] == 0:
        other_trainers_discovered = [item for sublist in list(product([trainer], list(range(randint(1,50), randint(51,129), 8))) for trainer in list(range(1, 129, 1))) for item in sublist]
        rick_sanchez_discovered = list(product([130], range(1,152,1)))
        conn.executemany("INSERT OR IGNORE INTO pokemons_discovered (master_id, pokemon_id) values (?, ?)", other_trainers_discovered + rick_sanchez_discovered)
    conn.commit()
    conn.close()

app = Flask(__name__)


# -------------------------- #
#     WRAPPED VALIDATORS
# -------------------------- #
def validate_flag_found(wrapped_function):
    @wraps(wrapped_function)
    def _wrapper(*args, **kwargs):
        challenge_flag = request.cookies.get("flag")
        if challenge_flag and challenge_flag == "ABK{I_LOVE_POKEMON}":
            return redirect("/you_have_found_the_flag")
        else:
            return wrapped_function(*args, **kwargs)
    return _wrapper

def validate_authentication_cookie(wrapped_function):
    @wraps(wrapped_function)
    def _wrapper(*args, **kwargs):
        authenticated_cookie = request.cookies.get("authenticated")
        master_id_cookie = request.cookies.get("master_id")
        if authenticated_cookie and master_id_cookie and authenticated_cookie == "NOW_WE_ARE_TALKING": # IDOR
            return wrapped_function(*args, **kwargs)
        else:
            response = redirect("/login")
            response.delete_cookie("master_id")
            response.delete_cookie("username")
            return response
    return _wrapper

def validate_challenge(wrapped_function):
    @wraps(wrapped_function)
    def _wrapper(*args, **kwargs):
        challenge_cookie = request.cookies.get("challenge")
        if challenge_cookie and challenge_cookie == "YEAH":
            return wrapped_function(*args, **kwargs)
        else:
            return redirect("/challenge")
    return _wrapper

def validate_pokemon_owned(wrapped_function):
    @wraps(wrapped_function)
    def _wrapper(*args, **kwargs):
        try:
            master_id_cookie = request.cookies.get("master_id")
            if master_id_cookie:
                conn = sqlite3.connect('database.db')
                result = conn.execute("SELECT pokemon_id FROM pokemons_discovered WHERE master_id = %s" % master_id_cookie)
                pokemons_discovered = list(map(lambda p: str(p[0]) ,result.fetchall()))
                if kwargs["pokemon_id"] in pokemons_discovered:
                    return wrapped_function(*args, **kwargs)
            abort(404)
        except:
            abort(404)
    return _wrapper


def validate_authentication_form(form):
    try:
        username, password = form.get("username"), form.get("password")
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        result = conn.execute("SELECT master_id, password FROM pokemon_masters WHERE username = '{0}'".format(username)) # SQLI
        result_raw = list(map(lambda e: dict(e), result.fetchall()))
        conn.close()
        if result_raw:
            password_data = dict(result_raw[0])
            if password_data and password_data.get("password") == password:
                return True, result_raw
            else:
                for elem in result_raw:
                    if "password" in elem and elem.get("master_id", 1) != 1:
                        elem["password"] = "####SENSITIVE-DATA####"
                return False, result_raw
        return False, []
    except:
        abort(404)


# -------------------------- #
#         ENDPOINTS
# -------------------------- #

@app.route("/challenge")
@validate_flag_found
def challenge():
    try:
        challenge_cookie = request.cookies.get("challenge")
        winner = challenge_cookie == "YEAH"
        return render_template("challenge.html", winner=winner, looser=not(winner) and challenge_cookie is not None)
    except:
        abort(404)

@app.route("/01100110011011000110000101100111", methods=["POST"])
def get_flag():
    try:
        form = request.form
        if form and form.get("01100110011011000110000101100111"):
            if form.get("01100110011011000110000101100111") == "ABK{I_LOVE_POKEMON}":
                response = redirect("/you_have_found_the_flag")
                response.set_cookie("flag", "ABK{I_LOVE_POKEMON}")
                return response
        response = redirect("/")
        response.set_cookie("status", "fail")
        return response
    except:
        abort(404)

@app.route("/challenge_validation", methods=["POST"])
@validate_flag_found
def challenge_validation():
    try:
        form = request.form
        if form and form.get("passcode"):
            if str(form["passcode"]).upper() == "11CK0001":
                response = redirect("/login")
                response.set_cookie("challenge", "YEAH")
                return response
        response = redirect("/challenge")
        response.set_cookie("challenge", "LOOSER")
        return response
    except:
        abort(404)

@app.route("/authenticate", methods=["POST"])
@validate_flag_found
def authenticate():
    try:
        form = request.form
        if not form:
            return redirect("/login.html")
        valid_user, result_raw = validate_authentication_form(form)
        if valid_user:
            master_data = dict(result_raw[0])
            response = redirect("/pokedex")
            response.set_cookie("authenticated", "NOW_WE_ARE_TALKING")
            response.set_cookie("master_id", str(master_data["master_id"]))
            response.set_cookie("username", form.get("username"))
            return response
        else:
            response = redirect("/login")
            response.set_data("db_raw_data: " +str(base64.b64encode(str(result_raw).encode('ascii'))))
            response.set_cookie("authenticated", "VGhpcyBpcyBub3QgbW9yZSB0aGFuIGEgZGlzdHJhY3Rpb24sIGJ1dCBpdCB3YXMgZnVuIHRvIHNlZSB5b3Ugd2FzdGluZyB5b3VyIHRpbWUhISEKCkhBSEE=")
            return response
    except:
        abort(404)

@app.route("/login")
@validate_flag_found
@validate_challenge
def login():
    try:
        authenticated_cookie = request.cookies.get("authenticated")
        if not authenticated_cookie or authenticated_cookie == "NOW_WE_ARE_TALKING":
            return make_response(render_template("login.html", incorrect_password=False))
        else:
            return make_response(render_template("login.html", incorrect_password=True))
    except:
        abort(404)

@app.route("/you_have_found_the_flag")
def you_have_found_the_flag():
    try:
        challenge_flag = request.cookies.get("flag")
        if challenge_flag and challenge_flag == "ABK{I_LOVE_POKEMON}":
            return make_response(render_template("you_have_found_the_flag.html"))
        else:
            response = redirect("/")
            return response
    except:
        abort(404)

@app.route("/")
@validate_flag_found
def index():
    try:
        response = make_response(render_template("index.html", fail=request.cookies.get("status") == "fail"))
        return response
    except:
        abort(404)

@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
@validate_flag_found
def error(error):
    response = make_response(render_template("404.html")), 404
    return response

@app.route("/pokemon/<pokemon_id>")
@validate_flag_found
@validate_challenge
@validate_authentication_cookie
@validate_pokemon_owned
def pokemon(pokemon_id : int = 0):
    try:
        conn = sqlite3.connect('database.db')
        result = conn.execute("SELECT pokemon_image, pokemon_name FROM pokemons WHERE pokemon_id = %s" % pokemon_id) # IDOR
        data = result.fetchone()
        if data:
            return send_file(   BytesIO(base64.b64decode(data[0].encode("ascii"))),
                                mimetype="image/gif",
                                download_name=data[1]+".jpg")
        else:
            abort(404)
    except:
        abort(404)

@app.route("/pokedex")
@validate_flag_found
@validate_challenge
@validate_authentication_cookie
def pokedex():
    try:
        master_id = request.cookies.get("master_id")
        username = request.cookies.get("username")
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        result = conn.execute("SELECT P.* FROM pokemons AS P LEFT JOIN pokemons_discovered PD ON P.pokemon_id = PD.pokemon_id where PD.master_id = %s" % master_id) # IDOR
        pokemon_list = list(map(lambda p: dict(p), result.fetchall()))
        response = make_response(render_template("pokedex.html", pokemon_master=username, pokemon_list=pokemon_list))
        return response
    except:
        abort(404)

@app.route("/restore_database")
def restore_database():
    try:        
        init_db()
        return "Success"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=getenv("PORT", 8080))