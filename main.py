from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import date
import csv
import json
import os

ext = 0
def main():

    global ext

    fajl = open("linkovi.txt", "r")

    #stvaramo csv i u njega za svaki link iz fajla s linkovima skidamo i zapisujemo metapodatke
    with open('superportal-metapodaci.csv', 'w', newline='\n', encoding="utf-8") as file:
        with open('linkovi.txt', "r", newline='\n', encoding="utf-8") as linkovi:
            writer = csv.writer(file)
            writer.writerow(["Link",
                             "Naslov",
                             "Kategorija",
                             "Datum",
                             "Tekst",
                             "Autor",
                             "Broj_clanaka_autora"])


            for link in linkovi:
                a = getMetadata(link)
                print(link)
                writer.writerow([a[0], a[1], a[2], a[3], a[4], a[5], a[6]])

    print("Zapisano u CSV")
    file.close()
    linkovi.close()

    #CSV -> JSON
    data = {}
    print('Radim JSON file')
    with open('superportal-metapodaci.csv', "r", newline='\n', encoding="utf-8") as csvf:
        with open('superportal-meta.json', "w", newline='\n', encoding="utf-8") as jsonf:
            csvReader = csv.DictReader(csvf)

            jsonf.write(json.dumps(data, indent=4, ensure_ascii=False))
    csvf.close()
    jsonf.close()
    print("Gotov JSON!")
    os.remove("linkovi.txt")

def getMetadata(link):
    c = urlopen(link).read()
    soup = BeautifulSoup(c, features="html.parser")
    text = soup.get_text()
    head_tag = soup.head
    metas = head_tag.find_all("meta")
    mList = []
    for meta in metas:
        mList.append(meta)
    mList = mList[1:]
    title = ""
    url = ""
    description = ""
    pubTime = ""
    for m in mList:
        if (m.get("property")) == "og:title":
            title = (m.get("content")) #naslov
        elif (m.get("property")) == "og:description":
            description = (m.get("content")) #podnaslov
        elif (m.get("property")) == "og:url":
            url = (m.get("content")) #url
        elif (m.get("property")) == "article:published_time":
            pubTime = (m.get("content"))
        else:
            pass
    datetime = pubTime[:10]
    dateBroken = datetime.split("-")
    pyDate = date(int(dateBroken[0]), int(dateBroken[1]), int(dateBroken[2]))
    pubTime = pyDate #kad se izdao clanak

    body_tag = soup.body
    divs = body_tag.find_all("div")
    mydivs = soup.find("div", {"class": "td-post-author-name"})
    author_link = mydivs.find("a")['href']
    author_name = mydivs.find("a").get_text() #ime autora clanka
    author_post_count = getAuthorCounters(author_link) #broj autorovih clanaka

    kategorije = ""
    mydivs2 = soup.find_all("li", {"class": "entry-category"})
    for li in mydivs2:
        kategorije +=  (li.get_text()) + ","
    kateList = kategorije.split(",")
    category = kateList[0] #kategorija
    kateList.pop(-1)
        
    tekst = body_tag.find("div",{"class": "td-post-content"})
    realText = str(tekst.get_text())
    return url, title, category, pubTime, realText, author_name, author_post_count

#broj clanaka autora
def getAuthorCounters (link):
    c = urlopen(link).read()
    soup = BeautifulSoup(c, features="html.parser")
    text = soup.get_text()
    secondDivs = soup.find("div", {"class": "td-author-counters"})
    postCountStr = secondDivs.find("span", {"class": "td-author-post-count"}).get_text().split()
    postCount = postCountStr[0]
    return postCount
  
if __name__ == "__main__":
    main()