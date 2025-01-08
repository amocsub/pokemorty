#! python3
from flask import Flask, render_template, request, make_response, redirect, send_file, abort
from os import getenv, path
from random import randint
from itertools import product
from functools import wraps
import sqlite3
import base64
from io import BytesIO
from hashlib import sha1
from requests import get

# -------------------------- #
#       INITIALIZE DB
# -------------------------- #


def init_db():
    if path.exists("database.db"):
        open('database.db', 'w').close()
    conn = sqlite3.connect('database.db')
    conn.execute(
        'CREATE TABLE IF NOT EXISTS pokemon_masters (master_id INTEGER PRIMARY KEY ASC, username TEXT, password TEXT)')
    conn.execute(
        'CREATE TABLE IF NOT EXISTS pokemons (pokemon_id INTEGER PRIMARY KEY, pokemon_hash TEXT, pokemon_name TEXT, pokemon_image TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS pokemons_discovered (master_id INTEGER, pokemon_id INTEGER, FOREIGN KEY(master_id) REFERENCES pokemon_masters(master_id), FOREIGN KEY(pokemon_id) REFERENCES pokemons(pokemon_id))')
    pokemons_file = open("./misc/pokemons", "r")
    pokemons_data = pokemons_file.readlines()
    pokemons = list()
    for pokemon_data in pokemons_data:
        if "\n" in pokemon_data:
            pokemon_data = pokemon_data[:-1]
        pokemon_data_as_a_list = pokemon_data.split("\\\\----\\\\")
        pokemon_data_as_a_list.append(sha1(pokemon_data_as_a_list[1].encode("ascii")).hexdigest())
        pokemons.append(pokemon_data_as_a_list)
    conn.executemany(
        "INSERT OR IGNORE INTO pokemons (pokemon_id, pokemon_name, pokemon_image, pokemon_hash) values (?, ?, ?, ?)", pokemons)
    conn.execute("INSERT OR IGNORE INTO pokemon_masters (master_id, username, password) values (1, 'morty', '5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8'), (2, 'supermorty', 'f3ad14966208fa896b68d34867f29b2fb6645d01'), (3, 'mortytest', 'ea036d960850fefa8b5a134030d31ecf9e5f10f6'), (4, 'oviegas3', 'f668810b411b011b62a1bc4a0fe31a3719656f99'), (5, 'wfleming4', '5ecfcdfa610d3a355b0aaf1174c1d44ed17952e9'), (6, 'pcorrie5', 'f5a8cb1f84cfd726393ba90e3dd12ed0c7e4fac4'), (7, 'hwebster6', '7e8f23cb8f93fc4bb8d4d981688889daea946b0b'), (8, 'wmacallester7', 'e7a842128f67a50c422388cdbdb0073401d13610'), (9, 'dwilce8', '5b26d7bf89b85e38a0bd61171670426089d9d763'), (10, 'agirardey9', '951db53de84defca680c8a5b554725c62bde5307'), (11, 'tvanshina', '4c3809e59416a35ce37d04c925409ccd4676caad'), (12, 'csollandb', '11838a241fa2bf83f333cb4ac92f78b0de8eb451'), (13, 'drosebyc', '75ebabd2c69e6c507f7ce3b6d4e3702bf891789a'), (14, 'rrizzardid', '003f6d38fa569d16711803834c8994009244babd'), (15, 'lalfordee', '43f81a8dad66c098fa3d5d069c63f8673cd2e614'), (16, 'dsmyf', '5d837563d8bebd9dcdd0a75f05adae1e08e03fab'), (17, 'fspoerlg', '8cda8b2cffe2c35c02beb0df2cc68e3fed704c7f'), (18, 'noheagertieh', 'a3fe59f9e28de7dbe5935395fab432af04b53b63'), (19, 'fmatyushkini', '46fde73b9d50c6331e9b90e67d4e23ed19aff39d'), (20, 'efitzgibbonj', 'e26838d4d0f1fcdc796fa71a9120b4ab136c42a0'), (21, 'lmittenk', 'bde6f07dfefff8b4c796d60175812981f6f62537'), (22, 'lharmarl', 'dd874b15726b7e75b6a7c95d8bf78a6313c1dffa'), (23, 'agilbodym', '13de25561575eb2e76ed2ea13e7397ee4ce1cdc5'), (24, 'kposselln', '8b7154bfa6f90db840acff084079f99517dff367'), (25, 'tharlowo', 'f7a4ef0a24037d8fdf99be02ed7d95733abdd880'), (26, 'hskeatp', 'ff67224159243ed80d8d92ecfe87db6a6521f80a'), (27, 'cbodegaq', '1a34a3451725ab1747babecceeefd6dddd4b2da8'), (28, 'rfinlanr', '812133e4aece86eadc455000bc015342caaa24eb'), (29, 'mjacobis', 'd340cff4c559e3d17621e2ac8d1d9a6212d1743c'), (30, 'kkrauzet', 'd9cd874b6907913c4b847a7571cc038508619aa4'), (31, 'fpertu', 'd125cd0909ad462c28e832337fa75829e412de3f'), (32, 'gpeterkenv', '94d0c2840da37172e59b56b74957116e9390f67d'), (33, 'oheaffeyw', '136b0f8ce1a3c146dbdab33ddf5b7f84e9167d58'), (34, 'stoulamainx', 'b7f93767ece79757cefa716139b4baf65dfb7cbe'), (35, 'fminnocky', '92611a6b817575bdca63608380ac07e4df2178b1'), (36, 'ttadgellz', '894edb37d38fd7b1d92712d719407ccb88f8c845'), (37, 'rmcgannon10', 'b619e3ef2adc7779b4d01864cb23b67951b0964f'), (38, 'gpurple11', 'a052e88fdad87139e385a5de21bb23ee4817ae2b'), (39, 'mmullen12', '9ad2715888fcfb9ec40716f878f17c5ad39ce893'), (40, 'brobison13', 'af299c49521638105d856f935e21ca3bdb37dc4c'), (41, 'sdils14', '465ae8e8f1f9bebc5ace4235e1b07e867bd4ad4c'), (42, 'mroggeman15', '363b7508fde3c81625df2cdaea76a700b839535f'), (43, 'bbartels16', '9ab3544622c0e18df0de1aea1699080759e35e0c'), (44, 'mcoots17', '55fca1224b1f0c6a4afccdced8a22701848f1882'), (45, 'ebernardoux18', 'b65d2a561fd204ea5ece96d5110244f1c49d2428'), (46, 'zkingston19', 'b094254b2073e3dfe4b68f5cb4bcc248502ba9b8'), (47, 'oloftin1a', 'f874f9aa7ae96499137c253e2052024cbea16d69'), (48, 'gmeneghi1b', '83cc1ab43ec346e2648cdf35dd1fd92dfdcda825'), (49, 'jevers1c', 'dea1118e34eacb42eaac7ac4a5357eb511cfdf84'), (50, 'yperfili1d', 'd0ac581d39032963b6c136a228e9b9f9cb9b85c5'), (51, 'jmoulson1e', 'bf8c0e1857e0e254b46fc2a8d4283de91740693e'), (52, 'zkingsnorth1f', 'a14e1e52941d0379d718c5c627cad91cd55df9b9'), (53, 'atrevance1g', '63972f680182a1ac779ba853d119f0f852e84242'), (54, 'bbeiderbecke1h', '5695a94852faa2b69cd0ea7136d6f738cd2e0716'), (55, 'glille1i', '43a1f4e3acce09586f04efd978a51b00b6a582ee'), (56, 'dheape1j', 'db01eab144193196fd1593d22929d4031adb9408'), (57, 'dfalls1k', 'b22f880f0354f732571a5f358f9147bc69fabde2'), (58, 'showsin1l', '39e9b02622e21304670b0480cf41416a4a222510'), (59, 'kbundey1m', 'e6ec15e34785e2f51fa3947e458c4540a8ad8019'), (60, 'rwale1n', 'cb3894a11f27284aa9e8d593ae5b030b4d290bd4'), (61, 'asilberschatz1o', '6bcb31714101db1b0ff58229bc9ca1eae413345f'), (62, 'gmacnab1p', 'f4c0d777865ced65eab923fcb9961d95f7e9c6b6'), (63, 'rcoldbath1q', '97857fb3ac46ba727437204f5a3a1f86c8a47910'), (64, 'mdodding1r', '0ae95e7091e71c70a6d2f1eb6356c5e2e820a490'), (65, 'tsorby1s', '94740c1891f86b96efaa657e6417a47dc7ab513b'), (66, 'kmully1t', 'bdc453457d35a8685d01bd4cc0a91f7d732e21a9'), (67, 'pcheeney1u', '9944fd58b14133802cb93174a9bbf41363019cfd'), (68, 'mflacknell1v', '5ae4ccbb48e184eebe5cefa7a93bc7444fb81019'), (69, 'csummersby1w', 'ff533eb79e55ce562bac1d2030c2207a74ead8f6'), (70, 'akorpal1x', '8b5d92bf368b59ffb5c1511bf3d03521c8416960'), (71, 'vinkpen1y', '7850a327d2bdc651369ea9bad1af92f0f478753c'), (72, 'bstruttman1z', 'c42596846a1f17a9ecd3933525e4b000e94ac23c'), (73, 'pmilkeham20', '626c467f453984c0b42871671c7e41f59b20ff26'), (74, 'gshenley21', '4ff882229da29da22a06772c550660e5c035072b'), (75, 'pbrigden22', '915b8bb26eb6b10d90e5cf0c55728683bd67a21d'), (76, 'rbrownbill23', 'ab149063eb90381eb2884e7a22cd4cbcc95a7c88'), (77, 'mturfitt24', 'd2a56bca1c92a5b56d5690a7f1ba49ec91568dae'), (78, 'cbaxstare25', '11f5d1ebed7aa23fa02a72bb8035d0912d4309a2'), (79, 'elile26', 'c4bba4dc1ee856358b802e7dfa3e92cc9692fb19'), (80, 'pboom27', 'fe808754cef977a650b11d292e976c6ec5978a7f'), (81, 'ariddle28', 'b73fe5384309731b38606dabdb365f3b2715005a'), (82, 'kjurasz29', 'e2f1da55225c2131c2d4333c04ce08741e6b110e'), (83, 'ctonn2a', '8b64303abc42687391ef7d2205e1a846d1b87b56'), (84, 'scommon2b', '6a955e8e81fce4b758236f1e2a7de8dac4d8a988'), (85, 'mchurm2c', '9d589161ac72701dfed1498c32851253b71c77e2'), (86, 'mmashal2d', '25365eff60637e2237915c8f5285e12d2ba4b706'), (87, 'cpires2e', '32372b60bb0e90bbf2830032410a23dc135c052e'), (88, 'pboteman2f', '54fab30d7f6468a3b50d62d7e0d29d60a54feee1'), (89, 'cpenk2g', '86c4999d9690cea4f892bc0065d16f4e0df6cffc'), (90, 'spevie2h', '92d182713affaf5002a3106162135ff218ebefa6'), (91, 'bgeffinger2i', '024c76e04eaf335729073502c8887b137a2be106'), (92, 'aforst2j', 'cf4573e8d0b3585201e13e583a14b3406fdee989'), (93, 'ecassius2k', '556050633a5a9d7e751f75a1cd7e3a725ca5a380'), (94, 'kovershott2l', '3a3ee45d9315fc5ace27530c43fa277cc1de1f76'), (95, 'bbuckley2m', 'e468cf3de1ff504d871352f6ba10129b0c0707cf'), (96, 'rgilkison2n', 'a2f3f82c8d6aede83ecafca8df92f984a2b7c03f'), (97, 'okolakowski2o', 'cf03458be35c8b4626258cf0447ae03b37bddda8'), (98, 'sgayle2p', '5c21543e5cd86823d5b2d0ff37a66e44afb51683'), (99, 'cinchbald2q', 'ffac8dd3df47b77074e6edf1c26ae9bf3e39cd3c'), (100, 'emenguy2r', 'be3f4eab1531b25f0bcb71589ab029df0c494a46'), (101, 'rcrangle2s', '93135d15f3a9a88257fff75a12c902d8569110fc'), (102, 'hbetje2t', '0ee28e0b9e58909bea3ddaef662ebd9f99e8e86d'), (103, 'rtroke2u', 'a05bcec4a79950f3809306dd0f26c5ef942b0669'), (104, 'ascoffins2v', '78061ee9e52c379155d3b651b6e5df109ce62cb2'), (105, 'TheRealMorty', '330e6c0cd5b68c3c280b4ce34f1384d369f876cf'), (106, 'ctitterington2x', 'c7a19b2aa05494c645f892dfd2a151d5bedf3525'), (107, 'hboustred2y', '18780b4b178c181552d955375c2f719ab4926642'), (108, 'lnorwell2z', '3bcfbaca6628795a25d1af46868367ac81a81e97'), (109, 'ngilding30', 'bb217b1d6ef86760578109ad97776397eca3b94d'), (110, 'gtainton31', '17c94c6fb1e18f851357e4c7cce92ca1b7a2a1ff'), (111, 'mwhittlesea32', 'f3b46ffa37d299c28002f7ada7ff117a69494248'), (112, 'mgaughan33', 'c84d14e3ecfab462ee4e5561546a822f07d7cbaa'), (113, 'gclemencet34', 'c34e109da7064fed919f89fcdf31084ca2c1b91c'), (114, 'bmcgiff35', '0cad06257db8a1d8ad38d5f7736d7ea1da9737f3'), (115, 'zraikes36', '01bba4414ccac51691c6bb61a2c82343ab546669'), (116, 'biwanczyk37', '2f0511d2341381c6d5609adf07654591aa6cdaa0'), (117, 'alinskill38', 'ec5db2736bacaaa90eae63083722255fc5dcd4f9'), (118, 'jvarian39', 'af9d5832dcd413415e69784766ccecec72cfc6ba'), (119, 'kconboy3a', '12096ee97efd38de0d0bbdc861f3ae65e88c35ba'), (120, 'acarnegie3b', 'd3a9b78a57a8f86ce36bb98cf96de85a6505c8ca'), (121, 'agerretsen3c', 'cf21023b79b2f2ce4d4706efe5fc8412afaa84ba'), (122, 'esiggin3d', 'a7160a0a1efef83f57e2cc83ef9ace89c811619b'), (123, 'tmicheli3e', '0ca7ce4d86e828165eae41856b71a6503d4930a6'), (124, 'alamswood3f', '29f014bb8ee17d11ee87d2be52fe21201d0f8332'), (125, 'gbellefant3g', 'f01a1f3de1298076d591cafb49880774663ade40'), (126, 'rleckie3h', '6b75e314551a7ad6906eb46dc97b5c4b070dcaa3'), (127, 'bpoznanski3i', '07995241a2c2116df00282e992280ddf2d447a31'), (128, 'rwadhams3j', 'd1f83011403f60a48f5def664691fab6495a3581'), (129, 'dhabberjam3k', 'dcad34b47160a87e71e3e6d94b134a1f41e3325f'), (130, 'RickSanchez', 'e37db3cb85dfac732ffb3fad130bf08d17d9bab9'), (131, 'wbang3m', 'f4dc6a84ebe41c3e8b2816d3ff08033a3aeaa4be'), (132, 'skasparski3n', 'ff62805bb3f3af49bcf5b5917427cb9245d70546'), (133, 'femanuele3o', '92ef77092851bd831ac62b63800a90a0db0ffebf'), (134, 'Beth11', '691774b7e56f3f0cc7a9bd3c82e7666bb1e6bd50'), (135, 'charce3q', 'fcee3aee2e95911b12eb8d7799d341242a017c53'), (136, 'lwolsey3r', '59221063db789c42dd36e63295ff45dde3286628'), (137, 'cmelpuss3s', 'f99ef143ce1698967677d7c549334be5a44c2b53'), (138, 'kwiltshire3t', 'c974741b7350b877f5cb2092d76b2d782a757480'), (139, 'aleat3u', '5a5f8de8d5eac3e2e7d1c0448901e59a65be4f03'), (140, 'bwhitechurch3v', 'bda2f24c9eb8bbf40c53f70d5c2bd1db2a910d1c'), (141, 'aadcocks3w', '95d33eac2596db953dc6f848cba9cdd363e55a2c'), (142, 'lausello3x', '3cde60ae3cc6e6b0169e3b7bffad2cdf823f9c6a'), (143, 'JerrySmith', '154ca2baf522963de40fed8e0800c7194ebc9a1c'), (144, 'fstitch3z', 'fc681baec28cbf98905fe4b24aabca0aa0ee5ac7'), (145, 'cbroke40', 'a357219b40a3a0c3c15de9dc1e780560e2ad48c2'), (146, 'vdaleman41', 'c8e5614e8ffa585a6713c7c6609278912ca99d55'), (147, 'zclissett42', '6ff96c20e535a65cd79af0248b84ae3c026be062'), (148, 'ltregaskis43', '4446612909b8adf5d2e908758b214e1dc97f7b95'), (149, 'aronisch44', '1245b06029cc7273c6cade23459876c1a1d87284'), (150, 'nwye45', 'a6b8a0cf4a59e794cc68dfc31690551813e36f98'), (151, 'ksainz46', 'cfccea7b53c76f33af7041ca253718434b417834'), (152, 'jclaessens47', '760a3afc396547cd3725d7742e1515bd1006d4d0'), (153, 'vjindra48', '94e435c774af027aa4d8cf53c66a1abc8ebdd49d'), (154, 'abrownbridge49', 'be522b0637f60c9e6579f133c1c8a89e68350ca3'), (155, 'htinton4a', '0aa35932f34d6d33b6928a2720c6fbdf9e5afa5e'), (156, 'ffreddi4b', 'fe5006cf35cde6c331fcf6c25c098eacfd26e0c7'), (157, 'cclawe4c', '5ef7b8837d886a146660b86d5f71d96776bdf140'), (158, 'htanti4d', '3311a6d02b2163f9aaf5633029b350ea56fbd294'), (159, 'rwindrum4e', '5932a98e1d62340c3d09b0caa0e4847223054523'), (160, 'dthreader4f', '450c3d770c393f5acc1b4534e02b11c747f464dd'), (161, 'hcumpsty4g', '999268a085b608539c9e4c43758c4be3f919787e'), (162, 'lambrois4h', '08751afc07c607b38721be2ca2419c33374734fa'), (163, 'imckie4i', '24b74ed0bdc514153c534e7055699eae0839a1de'), (164, 'rcurnnok4j', 'ea8546cd6e220777d64004f28859e248d67116b3'), (165, 'rromeril4k', '4f96515ace39d72d163577128cfdf9ffd80852bc'), (166, 'adignum4l', '5613b6ef6ccc2d1c3fddd7313ef1637eeee5d1d4'), (167, 'dfasey4m', 'cb626862a28c769ff04a7a9c2e8801db7dc9371d'), (168, 'meadon4n', '987d0a6ac1c5542c505690a527bf4f9bc9171c7b'), (169, 'atomkys4o', 'd8e3265f0bdaef14d9b358a18c778e49be3c3ab9'), (170, 'ldurkin4p', 'aeed618673d15291dae9b3467f62fa4117d2c48f'), (171, 'jfraschetti4q', '32bee8f6323b1d622f905d2fffa3c9ac4818711e'), (172, 'dandrich4r', '64134b1658821054f5f622f24ff9903b9faac9e6'), (173, 'aamey4s', '7d4fd3cbb7f042ad6f48ab53ef4babecf6afee21'), (174, 'sjozef4t', '55e21bf5501d278b637b2f86fa8e1b3247bbe1d6'), (175, 'dcampanelli4u', 'ae1eeaa50002c4af86786e97a6fb3826ce7bdac1'), (176, 'dcannings4v', '90aa321637c2d850aedcb68025ae3bb1d897aae8'), (177, 'partist4w', 'f4817fcb6180ba1a58232675e27d707b4bd15e1c'), (178, 'hstannah4x', 'f88a8cd96f1d8f538994fb8249d943b01c54838e'), (179, 'msarre4y', 'a43743ffd285cb9b2b4f5a8720759abd616fa452'), (180, 'bterbeck4z', '5deb9466bf53766b400da0c0184b878355f4ff26'), (181, 'msteels50', 'c70b888e29e6d9f40d70b74e62fc9c6700402640'), (182, 'arule51', '06c0dd642691a46648aa5a9400adac15906d03bb'), (183, 'clavarack52', '40f4beb3fc923524702189823466704f51594392'), (184, 'elording53', '0d566acedcda65b1305914a43b852af71c5ca95a'), (185, 'sgiacobillo54', 'bc1cb8dc48fd29aa21c243f6de78b4fbe5a51a77'), (186, 'fwalters55', '13cff6a44f251a9c683a09dd65edcca152867e39'), (187, 'tvandenvelde56', '57b4e77d1fa02c070f736962d156f6a974320b67'), (188, 'hlangstone57', 'a0dee6bf74844e883e42d65c0ee3bcf0db71347b'), (189, 'kgerardin58', 'c10c46dd69f0c063ec3b424435b1099c6f3e0e21'), (190, 'fquaif59', '1d9c4c22cbdb7b99bd7f79cd176982b5b41fcb02')")
    if conn.execute("SELECT COUNT(*) FROM pokemons_discovered").fetchone()[0] == 0:
        other_trainers_discovered = [item for sublist in list(product([trainer], list(range(randint(
            1, 50), randint(51, 129), 8))) for trainer in list(range(1, 129, 1))) for item in sublist]
        rick_sanchez_discovered = list(product([130], range(1, 152, 1)))
        conn.executemany("INSERT OR IGNORE INTO pokemons_discovered (master_id, pokemon_id) values (?, ?)",
                         other_trainers_discovered + rick_sanchez_discovered)
    conn.commit()
    conn.close()


init_db()
app = Flask(__name__)

# -------------------------- #
#     WRAPPED VALIDATORS
# -------------------------- #


def validate_flag_found(wrapped_function):
    @wraps(wrapped_function)
    def _wrapper(*args, **kwargs):
        challenge_flag = request.cookies.get("flag")
        if challenge_flag and challenge_flag == "FLAG{I_LOVE_POKEMON}":
            return redirect("/you_have_found_the_flag")
        else:
            return wrapped_function(*args, **kwargs)
    return _wrapper


def validate_authentication_cookie(wrapped_function):
    @wraps(wrapped_function)
    def _wrapper(*args, **kwargs):
        authenticated_cookie = request.cookies.get("authenticated")
        master_id_cookie = request.cookies.get("master_id")
        if authenticated_cookie and master_id_cookie and authenticated_cookie == "NOW_WE_ARE_TALKING":  # IDOR
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
                result = conn.execute(
                    "SELECT P.pokemon_hash FROM pokemons AS P LEFT JOIN pokemons_discovered PD ON P.pokemon_id = PD.pokemon_id where PD.master_id = %s" % master_id_cookie)
                pokemons_discovered = list(
                    map(lambda p: str(p[0]), result.fetchall()))
                if kwargs["pokemon_hash"] in pokemons_discovered:
                    return wrapped_function(*args, **kwargs)
            abort(404)
        except:
            abort(404)
    return _wrapper


def validate_authentication_form(form):
    try:
        username, password = form.get("username"), form.get("password")
        password_hash = sha1(password.encode("ascii")).hexdigest()
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        result = conn.execute(
            "SELECT * FROM pokemon_masters WHERE username = '{0}' and password = '{1}'".format(username, password_hash))  # SQLI
        result_raw = list(map(lambda e: dict(e), result.fetchall()))
        conn.close()
        return len(result_raw) > 0, result_raw
    except:
        abort(404)


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
            if form.get("01100110011011000110000101100111") == "FLAG{I_LOVE_POKEMON}":
                response = redirect("/you_have_found_the_flag")
                response.set_cookie("flag", "FLAG{I_LOVE_POKEMON}")
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
            if str(form["passcode"]).upper() == "PIKACHU":
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
            return redirect("/login")
        valid_user, result_raw = validate_authentication_form(form)
        if valid_user:
            master_data = dict(result_raw[0])
            response = redirect("/pokedex")
            response.set_cookie("authenticated", "NOW_WE_ARE_TALKING")
            response.set_cookie("master_id", str(master_data["master_id"]))
            response.set_cookie("username", str(master_data["username"]))
            return response
        else:
            response = redirect("/login")
            if "debug" in form or request.cookies.get("debug"):
                response.set_cookie("db_raw_data", base64.b64encode(str(result_raw).encode('ascii')).decode('ascii'))
                if "debug" not in request.cookies:
                    response.set_cookie("debug", "true")
            if "authenticated" not in request.cookies:
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
        if request.headers.get("Referer","").endswith("/login") and authenticated_cookie == "NOW_WE_ARE_TALKING":
            return make_response(render_template("login.html", incorrect_password=False, winner=True))
        elif request.headers.get("Referer","").endswith("/login") and authenticated_cookie != "NOW_WE_ARE_TALKING":
            return make_response(render_template("login.html", incorrect_password=True, winner=False))
        else:
            return make_response(render_template("login.html", incorrect_password=False, winner=False))
    except:
        abort(404)


@app.route("/you_have_found_the_flag")
def you_have_found_the_flag():
    try:
        challenge_flag = request.cookies.get("flag")
        if challenge_flag and challenge_flag == "FLAG{I_LOVE_POKEMON}":
            try:
                get("https://api.telegram.org/bot1665736308:AAENBtwYcbevus9k-sJfJtBwpxHXXlLmcHI/sendMessage?chat_id=-1001196751999&text="+request.cookies.get("nickname","Unknown")+" won the challenge!")
            except:
                pass
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
        response = make_response(render_template(
            "index.html", fail=request.cookies.get("status") == "fail"))
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


@app.route("/pokemon/<pokemon_hash>")
@validate_flag_found
@validate_challenge
@validate_authentication_cookie
@validate_pokemon_owned
def pokemon(pokemon_hash: str = ""):
    try:
        conn = sqlite3.connect('database.db')
        result = conn.execute(
            "SELECT pokemon_image, pokemon_name FROM pokemons WHERE pokemon_hash = '%s'" % pokemon_hash)
        data = result.fetchone()
        if data:
            return send_file(BytesIO(base64.b64decode(data[0].encode("ascii"))),
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
        result = conn.execute(
            "SELECT P.* FROM pokemons AS P LEFT JOIN pokemons_discovered PD ON P.pokemon_id = PD.pokemon_id where PD.master_id = %s" % master_id)  # IDOR
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
