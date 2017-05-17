
import requests
from bs4 import BeautifulSoup
import pandas as pd

#get the url for each page and return the beautiful soup object
def get_url (page):
    if page >13:
        exit
    else:
        page = (page - 1) * 30
        url = 'https://www.tripadvisor.com/Search?geo=191&redirect&q=national+park&uiOrigin&ssrc=g&returnTo=__2F__&pid=3826&startTime&searchSessionId=42709F017B9DACC99BEE6E3996EF059B1494301728016ssid&sid=42709F017B9DACC99BEE6E3996EF059B1494375065646&rf=0&sessionId=42709F017B9DACC99BEE6E3996EF059B&actionType=updatePage&dist=undefined&o=%s&ajax=search' % (
        page)
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        return soup


#get_name of park
def get_name (soup):

    name = [] 
    state = []
    things_to_do =[]

    for item in soup.find_all("div", {"class": "info geo-info"}):  
        park_name = str(item.find("div", {"class": "title"}).text)
        # to_do_link = 'https://www.tripadvisor.com'+ str(item.find_all("a")[1]["href"])
        if len(park_name.split(',')) == 3:
            if 'National' in park_name.split(',')[0]:
                name.append(park_name.split(',')[0])
            else:
                name.append(park_name.split(',')[1])
        else:
            name.append(park_name.split(',')[0])
        state.append(park_name.rsplit(',',1)[1])
        things_to_do.append('https://www.tripadvisor.com'+ str(item.find_all("a")[1]["href"]))

    park_info = pd.DataFrame([name, state, things_to_do]).transpose()
    park_info.columns = ['Name', 'State', 'Link']
     return park_info


#get top things to do for each park
link = 'https://www.tripadvisor.com/Attractions-g60999-Activities-Yellowstone_National_Park_Wyoming.html'
def get_top (link):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")

    title = []
    rating = []
    review_link = []

    for item in soup.find_all("div",{"class": "listing_info"}):
        title.append(item.find("a").text)
        rating.append(item.find("div",{"class":"rs rating"}).find("span")["alt"].split(' ')[0])
        review_link.append('https://www.tripadvisor.com' + str(item.find("div",{"class":"rs rating"}).find("a")["href"]))

    top_things = pd.DataFrame([title, rating, review_link]).transpose()
    top_things.columns = ['Title', 'Rating', 'Review Link']

    return top_things

review_link = 'https://www.tripadvisor.com/Attraction_Review-g60999-d532063-Reviews-Lower_Geyser_Basin-Yellowstone_National_Park_Wyoming.html#REVIEWS'
# review_link = 'https://www.tripadvisor.com/Attraction_Review-g60999-d2236532-Reviews-or10-Lamar_Valley-Yellowstone_National_Park_Wyoming.html#REVIEWS'
def get_reviews (review_link):
    # page = 0
    # review_link.rsplit('-',2)[0] + 'or%s-'%(page) + review_link.rsplit('-',2)[1] + '-' + review_link.rsplit('-',2)[2]
    r = requests.get(review_link)
    base_soup = BeautifulSoup(r.content, "html.parser")
    # print base_soup.find("div", {"class": "pageNumbers"}).find_all("a")
    print base_soup.find("div", {"id": "REVIEWS"})
    #
    # title = []
    # rating = []
    # review = []
    #
    # # first page
    # for item in base_soup.find_all("div",{"class": "review"})[1:]:
    #     title.append(str(item.find("span", {"class":"noQuotes"}).text))
    #     rating.append(str(item.find("span", {"class": "ui_bubble_rating"})["class"][1].split('_')[1]))
    #     review.append(str(item.find("p", {"class":"partial_entry"}).text.encode("utf-8")))
    #
    title = []
    rating = []
    review = []

    #following pages
    for item in base_soup.find("div", {"class": "pageNumbers"}).find_all("a"):
        url = 'https://www.tripadvisor.com' + item["href"]
        # url = 'https://www.tripadvisor.com/Attraction_Review-g60999-d532063-Reviews-or80-Lower_Geyser_Basin-Yellowstone_National_Park_Wyoming.html#REVIEWS'
        # r = requests.get(url)
        # soup = BeautifulSoup(r.content, "html.parser")
        print item.text

        # for item in soup.find_all("div", {"class":"quote"}):
        #     print item
        # for item in soup.find_all("span", {"class":"noQuotes"}):
        #     print item
        # print soup.find_all("div", {"class":"quote"})
        # print soup.find_all("span", {"class":"noQuotes"})


        for item in soup.find_all("div",{"class": "review"})[1:]:
            if item.find("span", {"class":"noQuotes"}) is None:
                title.append('')
            else:
                title.append(str(item.find("span", {"class":"noQuotes"}).text))
            rating.append(str(item.find("span", {"class": "ui_bubble_rating"})["class"][1].split('_')[1]))
            review.append(str(item.find("p", {"class":"partial_entry"}).text.encode("utf-8")))

    reviews = pd.DataFrame([title, rating, review]).transpose()
    reviews.columns = ['Review Title', 'Review Rating', 'Review']

    print reviews

    return reviews

get_reviews(review_link)

print get_reviews (review_link)



#get info from wikipedia
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
            # national_park_name.append(row.find("th").find("a").attrs['title'].encode("utf-8"))
            national_park_name.append(row.find("th").find("a").text.encode("utf-8"))
            national_park_location.append(row.find_all("td")[1].find('span', {'class': 'geo'}).text.encode("utf-8"))
            national_park_visitor.append(int(row.find_all("td")[4].text.replace(',','').encode("utf-8")))

    national_park_info = pd.DataFrame([national_park_name, national_park_location, national_park_visitor]).transpose()
    national_park_info.columns = ['Name', 'Location', 'Visitors']

    return national_park_info


def main():
    park_list = pd.DataFrame()
    for i in range(1, 5):
        soup = get_url(i)
        park_list = pd.concat([park_list,get_name(soup)], ignore_index= True)
    print park_list

    wiki_url = 'https://en.wikipedia.org/wiki/List_of_national_parks_of_the_United_States'
    print wiki_national_park(wiki_url)


if __name__ == "__main__":
    main()
