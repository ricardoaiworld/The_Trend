from bs4 import BeautifulSoup
import bs4
from datetime import datetime
import requests
import re


def get_info():
    global y
    start, end = 1971, 1990
    # start, end = 1945, 2019
    # 1958exception
    url_prefix = 'https://en.wikipedia.org/wiki/List_of_state_leaders_in_'
    for year in range(start, end):
        y = year
        # f = open('%s.txt' % year, 'w')
        url = url_prefix + str(year)
        c = requests.get(url).content
        soup = BeautifulSoup(c, 'html.parser')
        continents = soup.select('h2 > span#Africa, h2 > span#Asia, h2 > span#Europe,\
        h2 > span#North_America, h2 > span#Oceania, h2 > span#South_America')
        for c in continents:
            for country in c.parent.find_next_sibling('ul').select('> li'):
                c_info = get_country_info(country)


def get_country_info(country):
    global g_name
    country_name = get_country_name(country)
    g_name = country_name
    position = get_position(country)
    # print(country_name)
    max()


def get_position(country):
    # lis = country.select(' > ul > li')
    # for li in lis:
    ols = country.select('> ul > li > ol')
    if ols:
        for ol in ols:
            position_name = ol.previous_element
            lis = ol.select('> li')
            for li in lis:
                get_leader_name(li)
    else:
        lis = country.select('> ul > li')
        for li in lis:
            get_leader_name(li)


def get_leader_name(li):
    name = li.select('> a:nth-of-type(1)')
    if not name:
        print((y, g_name))
        return
    # print(name[0].text)


def get_country_name(country):
    for i in country.select('> b'):
        # title = i.find('a')['title']
        name = i.text
        return name

def main():
    get_info()


if __name__ == '__main__':
    main()