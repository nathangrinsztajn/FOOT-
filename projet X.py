from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unidecode
import sqlite3
import datetime

driver = webdriver.Firefox()
driver.implicitly_wait(4)


def normalize(txt):
    txt = unidecode.unidecode(txt.lower())
    enlever = ["fc ", " fc", " st ", "st-", "saint"]
    for u in enlever:
        txt = txt.replace(u, "")
    txt = txt.replace(" ", "")
    return txt


def purifie(textComparateur):  # sous la forme [[equipe1, equipe2, datetimeMatch]...]
    tabMatchs = textComparateur.split("\n")
    matchs = [k.split(" - ") for k in tabMatchs]
    for k in matchs:
        if len(k) == 3:
            k[1] = k[1].split(",")[0]
            k[2] = k[2].split("(")[1].replace(")", "").strip()
            u = k[2].split("/")
            v = u[2].split(" à ")
            k[2] = datetime.datetime(int(v[0]), int(u[1]), int(u[0]), hour=int(v[1].split("h")[0]),
                                     minute=int(v[1].split("h")[1]))
    return matchs


def extrairecote(equipe1, equipe2, date):
    driver.get("http://www.comparateur-de-cotes.fr/comparateur/football")
    elem = driver.find_elements_by_name("search")[1]
    elem.clear()
    elem.send_keys(equipe1)
    elem.send_keys(Keys.RETURN)
    elem = driver.find_elements_by_name("search")[1]
    elem.clear()
    elem.send_keys(equipe1)
    elem.send_keys(Keys.RETURN)
    elem = driver.find_elements_by_class_name('notfat')
    equipesTrouvees = 0
    while elem[equipesTrouvees].text.find("Football") != -1:
        equipesTrouvees += 1
    corps = driver.find_element_by_id('searchresult')
    elems = corps.find_elements_by_tag_name('ul')[0:equipesTrouvees]
    matchsTrouvees = [purifie(elems[k].text) for k in range(len(elems))]
    return matchsTrouvees


driver.get("http://www.comparateur-de-cotes.fr/comparateur/football")
elem = driver.find_elements_by_name("search")[1]
elem.clear()
elem.send_keys("barcelone")
elem.send_keys(Keys.RETURN)
elem = driver.find_elements_by_class_name('notfat')
equipesTrouvees = 0
while elem[equipesTrouvees].text.find("Football") != -1:
    equipesTrouvees += 1
corps = driver.find_element_by_id('searchresult')
elems = corps.find_elements_by_tag_name('ul')[0:equipesTrouvees]
matchsQuiMatchent = [purifie(k.text) for k in elems]

matches = elems[0].find_elements_by_tag_name('li')