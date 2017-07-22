import sqlite3
import datetime

fichierDonnees = "base.sq3"
conn = sqlite3.connect(fichierDonnees)
cur = conn.cursor()

cur.execute('INSERT INTO nomfp(nomf, nomp) VALUES(?,?)', ['Inter Baku (n)', 'Inter Baku'])
cur.execute('INSERT INTO nomfp(nomf, nomp) VALUES(?,?)', ['VMFD Zalgiris Vilnius', 'VMFD Zalgiris'])
cur.execute('INSERT INTO nomfp(nomf, nomp) VALUES(?,?)', ['Zilina', 'MSK Zilina'])

#conn.commit()
cur.close()
conn.close()