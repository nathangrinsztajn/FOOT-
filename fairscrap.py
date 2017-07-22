from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unidecode
import sqlite3
import datetime

fichierDonnees = "base.sq3"
conn = sqlite3.connect(fichierDonnees)
cur = conn.cursor()
now = datetime.datetime.today()
#matchs = cur.execute("select e1, e2, date from matchavenir where date > ? order by date", [now]).fetchall()
#cote = cur.execute("select * from coteFair where DateMatch > ? order by DateMatch", [now]).fetchall()
#cote = cur.execute("select m.e1, m.e2, c.cote1, c.coten, c.cote2, parieur from coteSites as c, matchavenir as m where m.date > ? and c.e1 = m.e1 order by dateDuJour", [now]).fetchall()
#print(cote)
#print([k[0] for k in (cur.execute("select rez from result where date>? order by date", [now-datetime.timedelta(days=200)]).fetchall())])

a = """print(cur.execute("select * from result where date>? order by date desc", [now-datetime.timedelta(days=200)]).fetchall())
t=[k[0] for k in (cur.execute("select rez from result where date>? order by date", [now-datetime.timedelta(days=200)]).fetchall())]
c1=0
c2=0
cn=0
for i in t:
    if i==1:
        c1+=1
    if i==2:
        c2+=1
    if i=="x":
        cn+=1
print("c1= "+str(c1))
print("c2= "+str(c2))
print("cn= "+str(cn))
"""
print(cur.execute("select nomp from nomfp where nomf = 'VMFD Zalgiris Vilnius' ").fetchall())
#conn.commit()
cur.close()
conn.close()

