# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import bs4
import json
from datetime import datetime
import requests
import re


def string_format(s):
    remove = ['\n', ' ', '–', '-', '\xa0', ' ']
    for i in remove:
        s = s.strip(i)
    return s


def store_data():
    f_name = 'Data/country_leader_by_year/%s.txt' % y
    f = open(f_name, 'w')
    cnt = 1
    for country, d in D.items():
        f.write(str(cnt))
        d_json = json.dumps(d, ensure_ascii=False)
        f.write('\t' + country + '\t' + d_json + '\n')
        cnt += 1

    return


def print_data():
    for i, v in D.items():
        for j, k in v.items():
            print((i, j, k))


def get_info():
    global y
    global D
    D = {}
    start, end = 2018, 2019
    # start, end = 1945, 2019
    # 1958exception
    url_prefix = 'https://en.wikipedia.org/wiki/List_of_state_leaders_in_'
    for year in range(start, end):
        y = year
        print(year)
        # f = open('%s.txt' % year, 'w')
        url = url_prefix + str(year)
        c = requests.get(url).content
        soup = BeautifulSoup(c, 'html.parser')
        continents = soup.select('h2 > span#Africa, h2 > span#Asia, h2 > span#Europe,\
        h2 > span#North_America, h2 > span#Oceania, h2 > span#South_America')
        for c in continents:
            for country in c.parent.find_next_sibling('ul').select('> li'):
                get_country_info(country)
        # print_data()
        store_data()
        print(len(D))
        D = {}
    return


def get_country_info(country):
    global g_name
    country_name = get_country_name(country)
    if not country_name:
        if country.select('> a'):
            name = country.select('> a:nth-of-type(1)')
            country_name = name[0].text.split('(')[0]
            # print(country_name)
            # pass
            # print('oversea')
        else:
            print('warning')
            # print(country.text)
            return
    country_name = string_format(country_name)
    g_name = country_name
    D[country_name] = {}
    get_position(country)
    # print(country_name)


def get_position(country):
    # lis = country.select(' > ul > li')
    # for li in lis:
    ols = country.select('> ul > li > ol')
    if ols:
        for ol in ols:
            position_name = ol.previous_element
            position_name = string_format(position_name)
            lis = ol.select('> li')
            for li in lis:
                leader_name = get_leader_name(li)
                if D[g_name].get(position_name):
                    D[g_name][position_name].append(leader_name)
                else:
                    D[g_name][position_name] = [leader_name]
                # print((g_name, position_name, leader_name))
    else:
        lis = country.select('> ul > li')
        for li in lis:
            name = li.select('> a:nth-of-type(1)')
            if name:
                position_name = name[0].previous_element
                if position_name == ' ':
                    return
                if type(position_name) == bs4.element.NavigableString:
                    position_name = string_format(position_name)
                    leader_name = get_leader_name(li)
                    if D[g_name].get(position_name):
                        D[g_name][position_name].append(leader_name)
                    else:
                        D[g_name][position_name] = [leader_name]
                    # print((g_name, position_name, leader_name))


def get_leader_name(li):
    name = li.select('> a:nth-of-type(1)')
    if not name:
        if li.select('> a'):
            print((y, g_name))
        return ""
    s = string_format(name[0].text)
    return s


def get_country_name(country):
    for i in country.select('> b'):
        # title = i.find('a')['title']
        name = i.text
        return name

def main():
    get_info()


if __name__ == '__main__':
    main()