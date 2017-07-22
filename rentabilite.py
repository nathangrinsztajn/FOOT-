from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unidecode
import sqlite3
import datetime
import matplotlib.pyplot as plt





#for
#A = cur.execute("select coteVic11, coteNul1, coteVic21 from result where ").fetchall())

def difBaseF(e):
    X = []
    compteur = 0
    fichierDonnees = "base.sq3"
    conn = sqlite3.connect(fichierDonnees)
    cur = conn.cursor()
    A = cur.execute("select e1, e2, date, but1, but2, prob1, probx, prob2, rez from result order by date desc").fetchall()
    for match in A:
        B = cur.execute("select coteVic11, coteNul1, coteVic21, DateMatch, DateDuJour from coteFair where e1 = ? and e2 = ? and DateMatch = ? order by coteVic11 desc", [match[0], match[1], match[2]]).fetchall()
        if len(B)>0:
            B = B[0]
            print(B)
            Val = [float(match[5]) * float(B[0]) / 100, float(match[6]) * float(B[1]) / 100,
                   float(match[7]) * float(B[2]) / 100]
            print(Val)
            if Val[0] > e:
                if str(match[8]) == '1':
                    compteur += float(B[0]) - 1
                else:
                    compteur += -1
                print(float(match[5]) / 100, B[0])
            if Val[1] > e:
                if str(match[8]) == 'x':
                    compteur += float(B[1]) - 1
                else:
                    compteur += -1
                print(float(match[6]) / 100, B[1])
            if Val[2] > e:
                if str(match[8]) == '2':
                    compteur += float(B[2]) - 1
                else:
                    compteur += -1
                print(float(match[7]) / 100, B[2])
            print(compteur)
            X.append(compteur)
            print(" ")
            print(" ")
            print(" ")
    plt.plot(X)
    plt.show()
    cur.close()
    conn.close()

def difBaseC(e, entrep):
    X=[]
    compteur = 0
    esperanc = 0
    fichierDonnees = "base.sq3"
    conn = sqlite3.connect(fichierDonnees)
    cur = conn.cursor()
    A = cur.execute("select e1, e2, date, rez from result order by date").fetchall()
    for match in A:
        vic1 = cur.execute("select coteVic11, coteNul1, coteVic21, DateMatch, DateDuJour from coteFair where e1 = ? and e2 = ? and DateMatch = ? order by coteVic11 desc", [match[0], match[1], match[2]]).fetchall()[0][0]
        nul = cur.execute("select coteNul1 from coteFair where e1 = ? and e2 = ? and DateMatch = ? order by coteNul1 desc", [match[0], match[1], match[2]]).fetchall()[0][0]
        vic2 = cur.execute("select coteVic21 from coteFair where e1 = ? and e2 = ? and DateMatch = ? order by coteVic21 desc", [match[0], match[1], match[2]]).fetchall()[0][0]
        C = cur.execute("select parieur, cote1, coten, cote2, DateMatch, DateDuJour, e1, e2 from coteSites where e1 = ? and e2 = ? and DateMatch = ? and parieur = ? order by DateDuJour desc", [match[0], match[1], match[2], entrep]).fetchall()
        print(C)
        if len(C)>0:
            C=C[0]
            s = 1/float(C[1])+1/float(C[2])+1/float(C[3])
            print("s = "+str(s))
            Val = [float(vic1)/ (float(C[1]) * s ), float(nul)/ (float(C[2]) * s ),
               float(vic2)/ (float(C[3]) * s )]
            print(Val)
            if Val[0] < e:
                esperanc = esperanc + Val[0] -1
                print("pari e1")
                if str(match[3]) == '1':
                    print(vic1)
                    compteur += float(vic1)-1
                else:
                    compteur = compteur -1
                    print("gagnant : " + str(match[3]))
                print(compteur)
            if Val[1] < e:
                esperanc = esperanc + Val[1] -1
                print("pari n")
                if str(match[3]) == 'x':
                    print(nul)
                    compteur += float(nul)-1
                else:
                    compteur = compteur -1
                    print("gagnant : " + str(match[3]))
                print(compteur)
            if Val[2] < e:
                esperanc += Val[2]-1
                print("pari e2")
                if str(match[3]) == '2':
                    print(vic2)
                    compteur += float(vic2)-1
                else:
                    compteur = compteur -1
                    print("gagnant : " + str(match[3]))
                print(compteur)
            print("compteur = "+str(compteur))
            print("esperance = "+str(esperanc))
            X.append(compteur)
        print(" ")
        print(" ")
        print(" ")
    plt.plot(X)
    cur.close()
    conn.close()
    plt.xlabel('$matchs$')
    plt.ylabel('$gold$')
    plt.title(entrep)
    plt.show()
    print("fin")

#difBaseC(0.95, 'Betclic')
difBaseF(0.95)

#les parieurs : 'Betclic', 'Bwin', 'ParionsWeb', 'PMU', 'Unibet', 'Winamax', 'ZEbet'

#fichierDonnees = "base.sq3"
#conn = sqlite3.connect(fichierDonnees)
#cur = conn.cursor()
#print(cur.execute("select coteVic11, coteVic12 from coteFair").fetchall())
#cur.close()
#conn.close()
