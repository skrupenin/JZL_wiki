import requests

# по фамилии героя получить данные из WikiData при помощи прямого SPARQL запроса
def getPersonData(humanName):
    url = 'https://query.wikidata.org/sparql'
    query="""
    PREFIX wdno: <http://www.wikidata.org/prop/novalue/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?human ?humanLabel ?humanDescription ?BirthDate ?StartDate ?article WHERE {
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],ru". }
      ?human wdt:P31 wd:Q5 .       #find humans
      ?human ?Label "_humanName"@ru.
      OPTIONAL { ?human wdt:P569 ?BirthDate. }
      OPTIONAL { ?human wdt:P2031 ?StartDate. }
      
      ?article schema:about ?human .
      ?article schema:isPartOf <https://ru.wikipedia.org/>.

    }"""

    r = requests.get(url, params = {'format': "json", 'query': query.replace("_humanName", humanName)})
    return r.json()

# из названия файла выделяет фамилию.
# форматы названий файлов:
#   Адмирал Нельсон (Владимир Шигин) - 2010.fb2
#   Адам Смит. Его жизнь и научная деятельность (Валентин Яковенко).fb2
def getHero(fName):
    p=fName.find(". Его")
    if p==-1: p=fName.find("(")-1
    if p<=-1: return ""
    return fName[:p]

import pprint
import sys

# разбирает входящий JSON и форматирует строку с выводными данными
# пример JSON: {'head': {'vars': ['human', 'humanLabel', 'humanDescription', 'BirthDate', 'StartDate', 'article']}, 'results': {'bindings': [{'human': {'type': 'uri', 'value': 'http://www.wikidata.org/entity/Q132682'}, 'article': {'type': 'uri', 'value': 'https://ru.wikipedia.org/wiki/%D0%9C%D1%83%D1%81%D0%BE%D1%80%D0%B3%D1%81%D0%BA%D0%B8%D0%B9,_%D0%9C%D0%BE%D0%B4%D0%B5%D1%81%D1%82_%D0%9F%D0%B5%D1%82%D1%80%D0%BE%D0%B2%D0%B8%D1%87'}, 'BirthDate': {'datatype': 'http://www.w3.org/2001/XMLSchema#dateTime', 'type': 'literal', 'value': '1839-03-09T00:00:00Z'}, 'humanLabel': {'xml:lang': 'ru', 'type': 'literal', 'value': 'Модест Петрович Мусоргский'}, 'humanDescription': {'xml:lang': 'ru', 'type': 'literal', 'value': 'русский композитор'}}]}}
# если герой не найден -- то JSON выглядит так: {'head': {'vars': ['human', 'humanLabel', 'humanDescription', 'BirthDate', 'StartDate', 'article']}, 'results': {'bindings': []}}
def parsePersonData(b):
    b=b[0]
    r=""
    items=['humanLabel','humanDescription','BirthDate','StartDate','article']
    for i in items:
        if r!="":r+=";"
        if i in b:
            v=b[i]['value'].partition("T00:00")[0].split("-")
            if len(v)==1:
                r=r+'"'+b[i]['value']+'"'
            else:
                if len(v)==3:
                    r=r+v[2]+'.'+v[1]+'.'+v[0]
                else:
                    r=r+'"'+''.join(v)+'"'
                
        else:
            r+=""
    return r


import os
import datetime

startDir = "/Users/sergey_krupeninepam.com/Desktop/ЖЗЛ"

# итератор по иерархии директорий. Возвращает полные названия файлов
# r=root, d=directories, f=files
def crawlFiles(walkDir):
    for r, d, f in os.walk(walkDir):
        if r!=walkDir: print(r)
        for file in f:
                yield((r, file))

# итератор по героям -- надстройка над итератором по иерархии директорий. Возвращает строку для выводного файла                
def crawlPersons(startDir):    
    for fName in crawlFiles(startDir):
        name=getHero(fName[1])
        data=getPersonData(name)
        b=data['results']['bindings']
        if(b!=[]):
            yield(parsePersonData(b)+';"'+fName[0]+"/"+fName[1]+'"')
        else:
            yield('"'+name+'";;;;'+';"'+fName[0]+"/"+fName[1]+'"')


n=1
ofName="/Users/sergey_krupeninepam.com/Desktop/Герои "+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
fu=open(ofName+" utf-8.txt", "w",  encoding="utf-8")
fc=open(ofName+" mac.txt", "w",  encoding="mac_cyrillic")
for persondata in crawlPersons(startDir):
    print(persondata, file=fu)
    print(persondata, file=fc)
    if n%10==0: print(n)
    n+=1
fc.close()
fu.close()
print("Done")