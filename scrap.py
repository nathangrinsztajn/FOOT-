from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unidecode
import sqlite3
import datetime

driver = webdriver.Firefox()
driver.implicitly_wait(20)

#normalize le texte
def normalize(txt):
    txt = unidecode.unidecode(txt.lower())
    enlever = ["fc ", " fc", " st ", "st-", "saint"]
    for u in enlever:
        txt = txt.replace(u, "")
    txt = txt.replace(" ", "")
    return txt


### cote comparateur ###

def purifie(textComparateur):  #renvoit un tableau sous la forme [[equipe1, equipe2, datetimeMatch]...]
    tabMatchs = textComparateur.split("\n")
    matchs = [k.split(" - ") for k in tabMatchs]
    for k in range(len(matchs)):
        if len(matchs[k]) == 3:
            matchs[k][1] = matchs[k][1].split(",")[0]
            matchs[k][2] = matchs[k][2].split("(")[1].replace(")", "").strip()
            u = matchs[k][2].split("/")
            v = u[2].split(" à ")
            matchs[k][2] = datetime.datetime(int(v[0]), int(u[1]), int(u[0]), hour=int(v[1].split("h")[0]),
                                             minute=int(v[1].split("h")[1]))
        elif len(matchs[k]) == 2:
            if len(matchs[k][1].split("("))==2:
                h = [matchs[k][0], matchs[k][1].split(", ")[0], matchs[k][1].split("(")[1].replace(")", "").strip()]
                u = h[2].split("/")
                v = u[2].split(" à ")
                h[2] = datetime.datetime(int(v[0]), int(u[1]), int(u[0]), hour=int(v[1].split("h")[0]),
                                     minute=int(v[1].split("h")[1]))
                matchs[k] = h
            elif len(matchs[k][1].split("("))==3:
                h = [matchs[k][0], matchs[k][1].split(", ")[0], matchs[k][1].split("(")[2].replace(")", "").strip()]
                u = h[2].split("/")
                v = u[2].split(" à ")
                h[2] = datetime.datetime(int(v[0]), int(u[1]), int(u[0]), hour=int(v[1].split("h")[0]),
                                     minute=int(v[1].split("h")[1]))
                matchs[k] = h
    return matchs


def extrairecote(equipe1, equipe2, date, cur):
    driver.get("http://www.comparateur-de-cotes.fr/comparateur/recherche?" + equipe1)
    texte = driver.find_element_by_id('searchresult').text
    if texte.split(":")[1] == " 0 équipe(s) et 0 événement(s).":
        print("Pas de résultats pour " + equipe1)
        return "n"
    else:
        elem = driver.find_elements_by_class_name("notfat")
        equipesTrouvees = 0
        while equipesTrouvees < len(elem) and elem[equipesTrouvees].text.find("Football") != -1:
            equipesTrouvees += 1
        corps = driver.find_element_by_id('searchresult')
        elems = corps.find_elements_by_tag_name('ul')[0:equipesTrouvees]
        matchsTrouvees = [purifie(elems[k].text) for k in range(len(elems))]
        matchquimatche1 = 0
        matchquimatche2 = 0
        compteurMatch = 0
        cas = 0  # =0 si les équipes sont dans l'odre de la recherce, 1 sinon (il faut inverser les côtes par rapport au site)
        #print(matchsTrouvees)
        for k in range(len(matchsTrouvees)):
            for match in range(len(matchsTrouvees[k])):
                if stringToDate(str(date)) - stringToDate(str(matchsTrouvees[k][match][2])) <= datetime.timedelta(minutes=1) and stringToDate(str(date)) - stringToDate(str(matchsTrouvees[k][match][2]))>= datetime.timedelta(minutes = -1) :
                    if isequal(equipe1, matchsTrouvees[k][match][0]):
                        print(matchsTrouvees[k][match][1] + " ; " + equipe2)
                        if not isequal(equipe2, matchsTrouvees[k][match][1]):
                            cur.execute('INSERT INTO nomfc(nomf, nomc) VALUES(?,?)', [equipe2, matchsTrouvees[k][match][1]])
                        matchquimatche1 = k
                        matchquimatche2 = match
                        compteurMatch += 1
                    elif isequal(equipe1, matchsTrouvees[k][match][1]):
                        print(matchsTrouvees[k][match][0] + " ; " + equipe2)
                        if not isequal(equipe2, matchsTrouvees[k][match][0]):
                            cur.execute('INSERT INTO nomfc(nomf, nomc) VALUES(?,?)', [equipe2, matchsTrouvees[k][match][0]])
                        matchquimatche1 = k
                        matchquimatche2 = match
                        compteurMatch += 1
                        cas = 1
                    elif isequal(equipe2, matchsTrouvees[k][match][1]):
                        print(matchsTrouvees[k][match][0] + " ; " + equipe1)
                        if not isequal(equipe1, matchsTrouvees[k][match][0]):
                            cur.execute('INSERT INTO nomfc(nomf, nomc) VALUES(?,?)', [equipe1, matchsTrouvees[k][match][0]])
                        matchquimatche1 = k
                        matchquimatche2 = match
                        compteurMatch += 1
                    elif isequal(equipe2, matchsTrouvees[k][match][0]):
                        print(matchsTrouvees[k][match][1] + " ; " + equipe1)
                        if not isequal(equipe1, matchsTrouvees[k][match][1]):
                            cur.execute('INSERT INTO nomfc(nomf, nomc) VALUES(?,?)', [equipe1, matchsTrouvees[k][match][1]])
                        matchquimatche1 = k
                        matchquimatche2 = match
                        compteurMatch += 1
                        cas = 1
        if compteurMatch == 0:
            print("Pas de résultat où la date et "+ equipe1 +" concordent.")
            return "n"
        else:
            lienMatch = elems[matchquimatche1].find_elements_by_tag_name('li')[matchquimatche2].find_element_by_tag_name('a').click() #on clique sur le bon lien
            return (extrairePageFinale(cas))


def extrairePageFinale(cas):  # renvoit la page finale du comparateur de cote sous le format [ [cote1 (victoire equi1),coten (partie nulle),cote2 (victoire e2),"Betclic" (nom broker)],...]
    elem = driver.find_element_by_class_name("bettable")
    elems = elem.find_elements_by_tag_name("tr")[1:]
    cote = [u.text.split(" ") for u in elems]
    for i in range(len(cote)):
        if cas == 0:
            cote[i] = [float(cote[i][0]), float(cote[i][1]), float(cote[i][2])]
        else:
            cote[i] = [float(cote[i][2]), float(cote[i][1]), float(cote[i][0])]
    return [[cote[k], elems[k].get_attribute("title").split(" ")[2]] for k in range(len(elems))]


def isequal(e1, e2):
    if normalize(e1) == normalize(e2):
        return True
    else:
        conn = sqlite3.connect("base.sq3")
        cur = conn.cursor()
        a = False
        b = False
        if cur.execute("""select COUNT(nomf) from nomfc where nomf = ? and nomc = ?""", [e1, e2]).fetchall()[0][0] >= 1 :
            a = True
        if cur.execute("""select COUNT(nomf) from nomfp where nomf = ? and nomp = ?""", [e1, e2]).fetchall()[0][0] >= 1 :
            b = True
        return a or b


# extrairecote("Arsenal", "Palace", datetime.datetime(2017, 4, 10, hour=21, minute=0))


### extraire fairlay ###

def convertDate(date):  # format 2017-04-15T13:00:00+00:00 en datetime ATTENTION CHANGEMENT D'HEURE
    u = date.split('T')
    d = u[0].split('-')
    h = u[1].split(':')
    return datetime.datetime(int(d[0]), int(d[1]), int(d[2]), hour=int(h[0]), minute=int(h[1])) + datetime.timedelta(0,
                                                                                                                     7200,
                                                                                                                     0)  # GMT +2 France
def stringToDate(st):
    a = st.split("-")
    b = a[2].split(":")
    return datetime.datetime(int(a[0]), int(a[1]), int(b[0].split(" ")[0]), hour = int(b[0].split(" ")[1]), minute = int(b[1]))



def convert(s):  # notation chiffrée américaine string en float
    if s == '-':
        return '-'
    else:
        u = s.split(',')
        if len(u) == 1:
            return float(s)
        else:
            r = 0
            for i in range(len(u)):
                r = r + int(u[i]) * 1000 ** (len(u) - i - 1)
            return float(r)


def extraireCotefair(jour): #extrait les matchs avec *jour* jours en avance. Forme : [[['Young Boys', 'FC Basel'], datetime.datetime(2017, 7, 22, 19, 0), [[[2.72, 1353.0], ['-']], [['-'], ['-']], [[2.56, 1353.0], ['-']], [['-'], ['-']], [[3.75, 1353.0], ['-']], [['-'], ['-']]], datetime.datetime(2017, 7, 22, 17, 33, 33, 118334)]
    maint = datetime.datetime.today()
    page = 1
    datem = True
    cotef = []
    while datem:
        driver.get("https://fairlay.com/category/soccer/?page=" + str(page))
        tableRows = driver.find_elements_by_tag_name("tr")[1:]
        listeMatchs = [[tableRows[3 * i], tableRows[3 * i + 1], tableRows[3 * i + 2]] for i in
                       range(len(tableRows) // 3)]
        for i in listeMatchs:
            noms = i[0].find_elements_by_tag_name("td")[0].text.split(" vs. ")
            noms[0]=noms[0].replace(" (n)", "")
            noms[1] = noms[1].split("\n")[0]
            date = convertDate(i[0].find_elements_by_tag_name("td")[7].get_attribute("data-isodate"))
            datem = datem and (date - datetime.datetime.today() < datetime.timedelta(jour, 0, 0)) #réglé sur *jour* jours en avance
            if datem:
                cotes0 = [i[0].find_elements_by_tag_name("td")[2:4], i[0].find_elements_by_tag_name("td")[4:6],
                          i[1].find_elements_by_tag_name("td")[1:3], i[1].find_elements_by_tag_name("td")[3:5],
                          i[2].find_elements_by_tag_name("td")[1:3], i[2].find_elements_by_tag_name("td")[3:5]]
                cotes = [[cotes0[k][1].text.split("\n"), cotes0[k][0].text.split("\n")] if k % 2 == 0 else [
                    cotes0[k][0].text.split("\n"), cotes0[k][1].text.split("\n")] for k in range(len(cotes0))]
                #print(cotes)
                cotes = [[[convert(i) for i in u] for u in a] for a in cotes]
                cotef.append([noms, date, cotes, maint])
        page += 1
    print(cotef)
    return cotef





### les résultats ###

def victoire(a, b):
    if a > b:
        return "1"
    elif a == b:
        return "x"
    else:
        return "2"


def egaliteSansOrdre(liste1, liste2):
    return isequal(liste1[0], liste2[0]) and isequal(liste1[1], liste2[1]) or (
    isequal(liste1[0], liste2[1]) and isequal(liste1[1], liste2[0]))


def equalagissantF(t1, t2, cur): #t1 les 2 equipes de fairlay, t2 de Forbet : renvoit [bool, int] avec int = 0 si l'ordre est le même, 1 sinon
    e1 = t1[0]
    e2 = t1[1]
    f1 = t2[0]
    f2 = t2[1]
    cas = 0  # si les e sont dans le même ordre : 0 sinon 1.
    if isequal(e1, f1):
        print(e2 + " / " + f2)
        if not isequal(e2, f2):
            cur.execute('INSERT INTO nomfp(nomf, nomp) VALUES(?,?)', [e2, f2])
        return [True, cas]
    elif isequal(e1, f2):
        print(e2 + " / " + f1)
        if not isequal(e2, f1):
            cur.execute('INSERT INTO nomfp(nomf, nomp) VALUES(?,?)', [e2, f1])
        cas = 1
        return [True, cas]
    elif isequal(e2, f1):
        print(e1 + " / " + f2)
        if not isequal(e1, f2):
            cur.execute('INSERT INTO nomfp(nomf, nomp) VALUES(?,?)', [e1, f2])
        cas = 1
        return [True, cas]
    elif isequal(e2, f2):
        print(e1 + " / " + f1)
        if not isequal(e1, f1):
            cur.execute('INSERT INTO nomfp(nomf, nomp) VALUES(?,?)', [e1, f1])
        return [True, cas]
    else:
        return [False]


def exctractforbet(): # renvoit un tableau de tous les match de la veille, sous le format précisé en dessous
    driver.get("http://www.forebet.com/en/football-predictions-from-yesterday")
    liste1 = driver.find_elements_by_class_name("tr_1")
    liste0 = driver.find_elements_by_class_name("tr_0")
    liste = liste1 + liste0
    listeParis = []  # sous le format [[equipe1, equipe2, date, "1" "2" ou "x" (nul) pour le vainqueur, buts1, buts2, proba1, probax, proba2],...]
    for elem in liste:
        l = elem.text.split("\n")
        if len(l)>5:
            res = l[-2].split(" ")
            if len(res) == 3:
                if len(l[0]) <= 3:
                    datep = l[3].split(" ")[0].split("/")
                    h = l[3].split(" ")[1].split(":")
                    date = datetime.datetime(int(datep[2]), int(datep[1]), int(datep[0]), hour=int(h[0]),
                                             minute=int(h[1]))
                    # print(date)
                    result = victoire(res[-3], res[-1])
                    listeParis.append(
                        [l[1], l[2], date, result, res[-3], res[-1], l[3].split(" ")[2], l[3].split(" ")[3],
                         l[3].split(" ")[4]])
                else:
                    print("erreur de format pour " + l[1])
        else:
            print("erreur de format pour " + l[1])
    return(listeParis)


def permute(s):
    if s=='1':
        return '2'
    elif s=='2':
        return '1'
    else:
        return s

### Fonctions Finales ###

#les fonctions avec "test" sont des fonctions qui ne commit pas sur les bases de données. À appeler avant les vraies versions.

def reztest(minu):# nombre de minutes autorisées entre la date de deux matchs condidérés égaux --sans commit
    fichierDonnees = "base.sq3"
    conn = sqlite3.connect(fichierDonnees)
    cur = conn.cursor()
    now1 = datetime.datetime.today()
    now = str(now1).split(" ")[0]+" 01:00:00" #donne le jour à 1h
    veille = (now1 - datetime.timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0)
    matchshier = cur.execute("select date, e1, e2 from matchavenir where date < ?", [now]).fetchall()
    print(len(matchshier))
    reshier = exctractforbet()
    print(len(reshier))
    for match in matchshier:
        cur.execute("insert into matchhier (date,  e1, e2) VALUES(?,?,?)", match)
        cur.execute("DELETE FROM matchavenir WHERE date=? and e1=? and e2=?", match)
        for match2 in reshier:
            if stringToDate(match[0]) - match2[2] <= datetime.timedelta(minutes=minu) and stringToDate(match[0]) - match2[2] >= datetime.timedelta(minutes = -minu):
                a = equalagissantF([match[1], match[2]], [match2[0], match2[1]], cur)
                if a[0] and a[1]==0:
                    cur.execute('INSERT INTO result (e1, e2, date, rez, but1, but2, prob1, probx, prob2) VALUES(?,?,?,?,?,?,?,?,?)',
                                [match[1], match[2]]+match2[2:])
                    cur.execute("DELETE FROM matchhier WHERE date=? and e1=? and e2=?", match)
                elif a[0] and a[1]==1:
                    cur.execute(
                        'INSERT INTO result (e1, e2, date, rez, but1, but2, prob1, probx, prob2) VALUES(?,?,?,?,?,?,?,?,?)',
                        [match[1], match[2], match2[2], permute(match2[3]), match2[5], match2[4], match2[8], match2[7], match2[6]])
                    cur.execute("DELETE FROM matchhier WHERE date=? and e1=? and e2=?", match)
                #else:
                    #print("""cur.execute('INSERT INTO nomfp(nomf, nomp) VALUES(?,?)', [""" + match[1]+ ", " + match2[0] + "])")
                    #print("""cur.execute('INSERT INTO nomfp(nomf, nomp) VALUES(?,?)', [""" + match[1] + ", " + match2[1] + "])")
    matchshier1 = cur.execute("select date, e1, e2 from matchhier").fetchall()
    for match in matchshier1:
        val = False
        for match2 in reshier:
            if stringToDate(match[0]) - match2[2] <= datetime.timedelta(minutes=minu) and stringToDate(match[0]) - match2[2] >= datetime.timedelta(minutes = -minu): #ici 60 peut être changé
                print("""cur.execute('INSERT INTO nomfp(nomf, nomp) VALUES(?,?)', [""" + "'" + match[1] + "'" + ", " + "'" + match2[
                    0] + "'" + "])")
                print("""cur.execute('INSERT INTO nomfp(nomf, nomp) VALUES(?,?)', [""" + "'" + match[1] + "'" + ", " + "'" + match2[
                    1] + "'" + "])")
                val = True
        if not val:
            print("pas de résultats pour " + str(match[0]) + " ; "+ match[1] + " et " +match[2])
    print("restant à match : ")
    print (cur.execute("select * from matchhier").fetchall())
    print(cur.execute("select COUNT(e1) from matchhier").fetchall()[0][0])
    print(cur.execute("select * from result where date < ? and date > ?", [now, veille]).fetchall())

def rez(minu):
    fichierDonnees = "base.sq3"
    conn = sqlite3.connect(fichierDonnees)
    cur = conn.cursor()
    now1 = datetime.datetime.today()
    now = str(now1).split(" ")[0]+" 00:00:00" #donne le jour à minuit
    matchshier = cur.execute("select date, e1, e2 from matchavenir where date < ?", [now]).fetchall()
    reshier = exctractforbet()
    for match in matchshier:
        cur.execute("insert into matchhier (date,  e1, e2) VALUES(?,?,?)", match)
        cur.execute("DELETE FROM matchavenir WHERE date=? and e1=? and e2=?", match)
        for match2 in reshier:
            if stringToDate(match[0]) - match2[2] <= datetime.timedelta(minutes=minu) and stringToDate(match[0]) - match2[2] >= datetime.timedelta(minutes = -minu):
                a = equalagissantF([match[1], match[2]], [match2[0], match2[1]], cur)
                if a[0] and a[1]==0:
                    cur.execute('INSERT INTO result (e1, e2, date, rez, but1, but2, prob1, probx, prob2) VALUES(?,?,?,?,?,?,?,?,?)',
                                [match[1], match[2]]+match2[2:])
                    cur.execute("DELETE FROM matchhier WHERE date=? and e1=? and e2=?", match)
                elif a[0] and a[1]==1:
                    cur.execute(
                        'INSERT INTO result (e1, e2, date, rez, but1, but2, prob1, probx, prob2) VALUES(?,?,?,?,?,?,?,?,?)',
                        [match[1], match[2], match2[2], permute(match2[3]), match2[5], match2[4], match2[8], match2[7], match2[6]])
                    cur.execute("DELETE FROM matchhier WHERE date=? and e1=? and e2=?", match)
    print (cur.execute("select * from matchhier").fetchall())
    cur.execute("DELETE FROM matchhier")
    conn.commit()
    cur.close()
    conn.close()


def c(couple):
    if len(couple)==1:
        return 0
    else:
        return couple[0]


def v(couple):
    if len(couple)==1:
        return 0
    else:
        return couple[1]

def scrapmatchtest(jour): #insère le tableau de extraireCoteFair dans les base de données (sans commit)
    fichierDonnees = "base.sq3"
    conn = sqlite3.connect(fichierDonnees)
    cur = conn.cursor()
    now1 = datetime.datetime.today()
    matchsfair = extraireCotefair(jour)
    compteur = 0
    for match in matchsfair:
        print(match)
        if cur.execute("select COUNT(e1) from matchavenir where e1=? and e2=? and date=?", [match[0][0], match[0][1], match[1]]).fetchall()[0][0]==0:
            cur.execute("INSERT into matchavenir (date, e1, e2) VALUES(?,?,?)", [match[1], match[0][0], match[0][1]])
        cur.execute("INSERT into coteFair (dateDuJour, DateMatch, e1, e2, coteVic11, coteVic12, coteNonVic11, "
                    "coteNonVic12, coteVic21, coteVic22, coteNonVic21, "
                    "coteNonVic22, coteNul1, coteNul2, coteNonNul1, coteNonNul2) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [now1, match[1], match[0][0], match[0][1], c(match[2][0][0]), c(match[2][0][1]), c(match[2][1][0]), c(match[2][1][1]), c(match[2][2][0]), c(match[2][2][1]),c(match[2][3][0]), c(match[2][3][1]), c(match[2][4][0]), c(match[2][4][1]), c(match[2][5][0]), c(match[2][5][1])])
        cur.execute("INSERT into volumeFair (dateDuJour, DateMatch, e1, e2, volVic11, volVic12, volNonVic11, "
                "volNonVic12, volVic21, volVic22, volNonVic21, "
                "volNonVic22, volNul1, volNul2, volNonNul1, volNonNul2) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [now1, match[1], match[0][0], match[0][1], v(match[2][0][0]),
                 v(match[2][0][1]), v(match[2][1][0]), v(match[2][1][1]), v(match[2][2][0]), v(match[2][2][1]),
                 v(match[2][3][0]), v(match[2][3][1]), v(match[2][4][0]), v(match[2][4][1]), v(match[2][5][0]),
                 v(match[2][5][1])])
        compteur +=1
    print(compteur)


def scrapmatch(jour):#insère le tableau de extraireCoteFair dans les base de données (avec commit)
    fichierDonnees = "base.sq3"
    conn = sqlite3.connect(fichierDonnees)
    cur = conn.cursor()
    now1 = datetime.datetime.today()
    matchsfair = extraireCotefair(jour)
    for match in matchsfair:
        if cur.execute("select COUNT(e1) from matchavenir where e1=? and e2=? and date=?", [match[0][0], match[0][1], match[1]]).fetchall()[0][0]==0:
            cur.execute("INSERT into matchavenir (date, e1, e2) VALUES(?,?,?)", [match[1], match[0][0], match[0][1]])
        cur.execute("INSERT into coteFair (dateDuJour, DateMatch, e1, e2, coteVic11, coteVic12, coteNonVic11, "
                    "coteNonVic12, coteVic21, coteVic22, coteNonVic21, "
                    "coteNonVic22, coteNul1, coteNul2, coteNonNul1, coteNonNul2) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [now1, match[1], match[0][0], match[0][1], c(match[2][0][0]), c(match[2][0][1]), c(match[2][1][0]), c(match[2][1][1]), c(match[2][2][0]), c(match[2][2][1]),c(match[2][3][0]), c(match[2][3][1]), c(match[2][4][0]), c(match[2][4][1]), c(match[2][5][0]), c(match[2][5][1])])
        cur.execute("INSERT into volumeFair (dateDuJour, DateMatch, e1, e2, volVic11, volVic12, volNonVic11, "
                "volNonVic12, volVic21, volVic22, volNonVic21, "
                "volNonVic22, volNul1, volNul2, volNonNul1, volNonNul2) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [now1, match[1], match[0][0], match[0][1], v(match[2][0][0]),
                 v(match[2][0][1]), v(match[2][1][0]), v(match[2][1][1]), v(match[2][2][0]), v(match[2][2][1]),
                 v(match[2][3][0]), v(match[2][3][1]), v(match[2][4][0]), v(match[2][4][1]), v(match[2][5][0]),
                 v(match[2][5][1])])
    print("OK")
    conn.commit()
    cur.close()
    conn.close()

def ajourfctest(jour):
    now=datetime.datetime.today()
    limite = now + datetime.timedelta(days = jour)
    fichierDonnees = "base.sq3"
    conn = sqlite3.connect(fichierDonnees)
    cur = conn.cursor()
    av = cur.execute("select COUNT(nomf) from nomfc").fetchall()[0][0]
    matchs = cur.execute("select e1, e2, date from matchavenir where date > ? and date < ? order by date", [now, limite]).fetchall()
    for match in matchs:
        print(match)
        h = extrairecote(match[0], match[1], match[2], cur)
    diff = cur.execute("select COUNT(nomf) from nomfc").fetchall()[0][0]-av
    print(diff)


def ajourfc(jour):
    now=datetime.datetime.today()
    limite = now + datetime.timedelta(jour)
    fichierDonnees = "base.sq3"
    conn = sqlite3.connect(fichierDonnees)
    cur = conn.cursor()
    matchs = cur.execute("select e1, e2, date from matchavenir where date > ? and date < ? order by date", [now, limite]).fetchall()
    for match in matchs:
        h = extrairecote(match[0], match[1], match[2], cur)
        if h != "n" and len(h)>0 :
            for cote in h:
                cur.execute("INSERT into coteSites (dateDuJour, DateMatch, e1, e2, parieur, cote1, coten, cote2) VALUES (?,?,?,?,?,?,?,?)", [now, match[2], match[0], match[1], cote[1], cote[0][0], cote[0][1], cote[0][2]])
    conn.commit()
    cur.close()
    conn.close()

def scrap(duree, delai, jours): #scrap pendant %durée heures toutes les %délai minutes pour %jours jours en avance
    scrapmatch(jours)
    now = datetime.datetime.today()
    var = datetime.datetime.today()
    while datetime.datetime.today()-now < datetime.timedelta(hours=duree):
        if datetime.datetime.today()-var > datetime.timedelta(minutes=delai):
            scrapmatch(jours)
            var = datetime.datetime.today()
            print(var)


### dans l'ordre, les trucs à faire (dans projetX) ###


#reztest(61)
#print("---- scrapmatch ----")
#scrapmatchtest(2)
#print("---- ajourcf ----")
#ajourfctest(2)



#reprise le 08/07 pour le scrap des match dans la base de données




### à faire : ###

# si on trouve pas avec e1 pour ajourfc, on tente e2 dans la barre de recherche
# ne pas rajouter nom si apparait déjà
#regarder par exemple (rapide) si incohérence binaire (intérêt de parier sur oui et non simultanément)