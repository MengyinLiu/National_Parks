
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

#get the url for each page and return the beautiful soup object
def get_url (page):
    page = (page - 1) * 30
    url = "https://www.tripadvisor.com/Search?geo=191&redirect&q=national+park&uiOrigin=MASTHEAD&ssrc=A&typeaheadRedirect=true&returnTo=__2F__Travel__2D__g191__2D__c3259__2F__United__2D__States%%3ANational__2E__Parks__2E__Monuments__2E__Etc__2E__html__2F__&pid=3825&startTime=undefined&searchSessionId=52A513F08A52B338445106C616C0147C1480475706599ssid?&o=%s" %(page)

    r = requests.get(url)
    soup = BeautifulSoup(r.content,"html.parser")
    return soup


def get_name (soup):
    name = []
    for item in soup.find_all("div", {"class": "result ATTRACTIONS"}):
        name.append(str(item.find_all("div", {"class": "title"})[0].text))
    return name

park_list = []
for i in range(1,5):
    soup = get_url(i)
    park_list.extend(get_name(soup))

print park_list


wiki_url = 'https://en.wikipedia.org/wiki/List_of_national_parks_of_the_United_States'
r = requests.get(wiki_url)
soup = BeautifulSoup(r.content,"html.parser")
table = soup.find_all("table", {"class": "wikitable sortable plainrowheaders"})[0]

# national_park_name = []
# for item in table.find_all("th", {"scope": "row"}):
#     park_name = item.find_all("a")[0].attrs['title'].encode("utf-8")
#     national_park_name.append(park_name)
#
#
# for item in table.find_all("span", {"class": "geo"}):
#     location = item.string.encode("utf-8")
#     national_park_location.append(location)
# print national_park_location

wiki_url = 'https://en.wikipedia.org/wiki/List_of_national_parks_of_the_United_States'
def wiki_national_park (wiki_url):
    wiki_url = wiki_url
    r = requests.get(wiki_url)
    soup = BeautifulSoup(r.content, "html.parser")
    table = soup.find_all("table", {"class": "wikitable sortable plainrowheaders"})[0]

    national_park_name = []
    national_park_location = []
    national_park_visitor = []
    for row in table.find_all("tr"):
        if len(row.find_all("td")) == 0:
            continue
        else:
            national_park_name.append(row.find("th").find("a").attrs['title'].encode("utf-8"))
            national_park_location.append(row.find_all("td")[1].find('span', {'class': 'geo'}).text.encode("utf-8"))
            national_park_visitor.append(int(row.find_all("td")[4].text.replace(',','').encode("utf-8")))

    national_park_info = pd.DataFrame([national_park_name, national_park_location, national_park_visitor]).transpose()
    national_park_info.columns = ['Name', 'Location', 'Visitors']

    return national_park_info













