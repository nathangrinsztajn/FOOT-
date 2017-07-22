import sqlite3

# nomfc (nomf STRING, nomc STRING) fairlay - comparateur de cote

# nomfp (nomf STRING, nomp STRING) fairlay - forbet

# result (date DATETIME, e1 STRING, e2 STRING, rez STRING, but1 INT, but2 INT, prob1 INT, probx INT, prob2 INT) résultats

# matchs (date,  e1 STRING, e2 STRING) tous les matchs

# matchavenir (date,  e1 STRING, e2 STRING)

# matchhier (date,  e1 STRING, e2 STRING)

#matchpassé (date DATETIME,  e1 STRING, e2 STRING)

# coteFair (dateDuJour DATETIME, DateMatch DATETIME, equipevrai1 TEXT, equipevrai2 TEXT, coteVic11 REAL, coteVic12 REAL,
# coteNonVic11 REAL, coteNonVic12 REAL,coteNul1 REAL, coteNul2 REAL, coteNonNul1 REAL, coteNonNul2 REAL, coteVic21 REAL,
#  coteVic22 REAL, coteNonVic21 REAL, coteNonVic22) REAL)

# volumeFair (idem)

# coteSites (dateDuJour DATETIME, DateMatch DATETIME, e1 TEXT, parieur TEXT, cote1 REAL, coten REAL, cote2 REAL)

fichierDonnees = "base.sq3"
conn = sqlite3.connect(fichierDonnees)
cur = conn.cursor()
cur.execute("CREATE TABLE nomfc (nomf STRING, nomc STRING)")
cur.execute("CREATE TABLE nomfp (nomf STRING, nomp STRING)")
cur.execute("CREATE TABLE result (date DATETIME, e1 STRING, e2 STRING, rez STRING, but1 INT, but2 INT, prob1 INT, probx INT, prob2 INT)")
cur.execute("CREATE TABLE matchs (date DATETIME,  e1 STRING, e2 STRING)")
cur.execute("CREATE TABLE matchavenir (date DATETIME,  e1 STRING, e2 STRING)")
cur.execute("CREATE TABLE matchhier (date DATETIME,  e1 STRING, e2 STRING)")
cur.execute("CREATE TABLE coteFair (dateDuJour DATETIME, DateMatch DATETIME, e1 TEXT, e2 TEXT, coteVic11 REAL, coteVic12 REAL, coteNonVic11 REAL, coteNonVic12 REAL,coteNul1 REAL, coteNul2 REAL, coteNonNul1 REAL, coteNonNul2 REAL, coteVic21 REAL, coteVic22 REAL, coteNonVic21 REAL, coteNonVic22 REAL)")
cur.execute("CREATE TABLE volumeFair (dateDuJour DATETIME, DateMatch DATETIME, e1 TEXT, e2 TEXT, volVic11 REAL, volVic12 REAL, volNonVic11 REAL, volNonVic12 REAL,volNul1 REAL, volNul2 REAL, volNonNul1 REAL, volNonNul2 REAL, volVic21 REAL, volVic22 REAL, volNonVic21 REAL, volNonVic22 REAL)")
cur.execute("CREATE TABLE coteSites (dateDuJour DATETIME, DateMatch DATETIME, e1 TEXT, e2 TEXT, parieur TEXT, cote1 REAL, coten REAL, cote2 REAL)")
cur.execute("CREATE TABLE matchpassé (date DATETIME,  e1 STRING, e2 STRING)")

#les equipes sont stockées avec le même nom et le même ordre que sur Fairlay

#conn.commit()
#cur.execute("select prob1 from result")
cur.close()
conn.close()