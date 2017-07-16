# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from requests.exceptions import ConnectionError

# get_name of park and the link to things to do
def get_name (pages):

    name = []
    state = []
    things_to_do =[]

    if pages <= 13:
        for page in range(pages):
            url = 'https://www.tripadvisor.com/Search?geo=191&redirect&q=national+park&uiOrigin&ssrc=g&returnTo=__2F__&pid=' \
                  '3826&startTime&searchSessionId=42709F017B9DACC99BEE6E3996EF059B1494301728016ssid&sid=42709F017B9DACC99BEE6E3996EF059B1494375065646&rf' \
                  '=0&sessionId=42709F017B9DACC99BEE6E3996EF059B&actionType=updatePage&dist=undefined&o=%s&ajax=search' % (page * 30)
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")

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
                if item.find("a", href=re.compile('Attractions-')) is None:
                    things_to_do.append('N/A')
                else:
                    things_to_do.append('https://www.tripadvisor.com'+ str(item.find("a", href=re.compile('Attractions-'))["href"]))

            park_info = pd.DataFrame([name, state, things_to_do]).transpose()
            park_info.columns = ['Name', 'State', 'Link']

    return park_info


# get top things to do for each park
# link = 'https://www.tripadvisor.com/Attractions-g143010-Activities-Acadia_National_Park_Mount_Desert_Island_Maine.html'
def get_top (park_info):

    link = park_info["Link"]
    link = 'https://www.tripadvisor.com/Attractions-g60672-Activities-Pago_Pago_Tutuila.html'
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")

    # if the park has less top things to do then we requested
    # if len(soup.find_all("div",{"class": "listing_info"})) < top_num:
    #     top_num = len(soup.find_all("div", {"class": "listing_info"}))
    # else:
    #     top_num = top_num

    title = []
    rating = []
    review_link = []

    for item in soup.find_all("div",{"class": "listing_info"}):

        if item.find("div",{"class":"rs rating"}) is not None:
            title.append(item.find("a").text)
            rating.append(item.find("div",{"class":"rs rating"}).find("span")["alt"].split(' ')[0])
            review_link.append('https://www.tripadvisor.com' + str(item.find("div",{"class":"rs rating"}).find("a")["href"]))
        else:
            break

    top_num = len(review_link)
    name = [park_info["Name"]] * top_num
    state = [park_info["State"]] * top_num
    # name = ['American Samoa National Park'] * top_num
    # state = ['Pago Pago'] * top_num

    top_things = pd.DataFrame([name, state, title, rating, review_link]).transpose()
    top_things.columns = ["Name","State",'Title', 'Rating', 'Review Link']

    return top_things

# get reviews for each things to do
def get_reviews (things_todo):

    base_review_link = things_todo["Review Link"]
    # base_review_link = 'https://www.tripadvisor.com/Attraction_Review-g60784-d261325-Reviews-Cuyahoga_Valley_National_Park-Brecksville_Ohio.html'

    try:
        base_r = requests.get(base_review_link)

    except ConnectionError:
        pass

    else:
        base_soup = BeautifulSoup(base_r.content, "html.parser")
        review_link = 'https://www.tripadvisor.com' + str(base_soup.find("div", id=re.compile("review_(\\d)+")).find("div", {"class": "quote"}).find("a")["href"])
        r = requests.get(review_link)
        soup = BeautifulSoup(r.content, "html.parser")

        # find out the last page
        if soup.find("div", {"class": "pageNumbers"}) is not None:
            last_page_num = int(soup.find("div", {"class": "pageNumbers"}).find_all("a")[-1].text)
        else:
            last_page_num = 1

        for page in range(int(last_page_num)):
            if page == 0:
                title = []
                rating = []
                review = []
                review_date = []
            else:
                review_link = 'https://www.tripadvisor.com' + str(soup.find("div", {"class": "unified pagination "}).find_all("a")[1]["href"])
                r = requests.get(review_link)
                soup = BeautifulSoup(r.content, "html.parser")

            # if the first post in the page is not english, then get out of the loop
            if soup.find("div", id=re.compile("review_(\\d)+")).text.encode("utf-8") == '\n':
                break

            for item in soup.find_all("div", id=re.compile("review_(\\d)+")):
                # somehow if the post is not english, it will be empty
                if item.text.encode("utf-8") != '\n':
                    title.append(item.find("div", {"class": "quote"}).text.encode("utf-8"))
                    # rating.append(item.find("span", {"class": "ui_bubble_rating"})["alt"].split(' ')[0].encode("utf-8"))
                    rating.append(item.find("span", {"class": "ui_bubble_rating"})["class"][1].split('_')[1].encode("utf-8"))
                    review_date.append(item.find("span", {"class": "ratingDate"}).text.encode("utf-8"))
                    review.append(item.find("div", {"class": "entry"}).text.encode("utf-8"))
                else:
                    break

        num_reviews = len(title)
        park_name = [things_todo["Name"]] * num_reviews
        things = [things_todo["Title"]] * num_reviews
        reviews = pd.DataFrame([park_name, things, title, rating, review_date, review]).transpose()
        reviews.columns = ['Park Name','Things To Do', 'Review Title', 'Review Rating', 'Review Date', 'Review']
        print things_todo["Title"], base_review_link

        return reviews


# get info from wikipedia
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

    park_list = get_name(3)

    # top_things_todo = pd.DataFrame(columns= ["Name", "State", 'Title', 'Rating', 'Review Link'])

    park_start = 61
    park_end = 70
    # num_of_things_todo = 30

    for i in range(park_start, park_end):
        top_things_todo = get_top(park_list.ix[i])
        park_reviews = pd.DataFrame(columns=['Park Name', 'Things To Do', 'Review Title', 'Review Rating', 'Review'])
        for i in range(len(top_things_todo)):
            things_todo = top_things_todo.ix[i]
            park_reviews = park_reviews.append(get_reviews(things_todo), ignore_index=True)
            print i, things_todo['Name'], things_todo['Title'], things_todo['Review Link']
        park_reviews.to_csv('/Users/mliu/National_Parks/park_data/%s.csv'%(park_reviews['Park Name'][0]))
        # print park_list.ix[i]["Name"]

        # park_reviews = pd.DataFrame(columns=['Park Name', 'Things To Do', 'Review Title', 'Review Rating', 'Review'])
        # things_todo = top_things.ix[1]
        # park_reviews = park_reviews.append(get_reviews(things_todo), ignore_index=True)
        # print i, things_todo['Name'], things_todo['Title'], things_todo['Review Link']
        # park_reviews.to_csv('/Users/mliu/National_Parks/park_data/%s.csv'%(park_reviews['Park Name'][0]))

    # wiki_url = 'https://en.wikipedia.org/wiki/List_of_national_parks_of_the_United_States'
    # # print wiki_national_park(wiki_url)

    # wiki_national_park(wiki_url).to_csv('/Users/mliu/National_Parks/wiki_output.csv')

if __name__ == "__main__":
    main()
