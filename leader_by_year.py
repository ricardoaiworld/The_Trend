from bs4 import BeautifulSoup
import bs4
from datetime import datetime
import requests
import re
# import mysql.connector

global d
d = {}


def set_year_range():
    start_year = 1945
    now_year = datetime.now().year + 1
    return start_year, now_year


def string_format(s):
    new_s = s.replace('\n', ' ').replace('-', '').strip(' ').lower()
    return new_s


def country_name_info_format(l):
    name = l
    new_name = name.split('(')
    for i in range(len(new_name)):
        new_name[i] = new_name[i].strip(' ()')
    # print(new_name)
    return new_name[0]


def get_continent(soup):
    l_region = ['Africa', 'Asia', 'Europe', 'North America', 'Oceania', 'South America']
    test = 0
    for region in soup.select('h2'):
        continent = region.span
        if continent is not None and (continent.text in l_region):
            # print(continent.text)
            test += 1
            num = get_country_by_continent(region)


def get_country_by_continent(region):
    countries = region.find_next_sibling('ul')
    count = 0
    for country in countries.select('> li'):
        count += 1
        country_name = get_country_name(country)
        # print(country_name)
        d[country_name] = d.get(country_name, {})
        country_leader = get_country_leader(country_name, country)
        # print(country_name)
    return count


def generate_leading_position():
    l = []
    f = open('government_position_list.txt', 'r')
    for line in f.readlines()[1:]:
        position = line.split('\t')[0]
        l.append(position)
    s = 's* -|'.join(l)
    return s


def get_country_leader(country_name, country):
    s = generate_leading_position()
    pattern = re.compile(s)
    ul = country.find('ul')
    if ul == None:
        print(country_name)
        return
    icon = ul.find_all(class_='flagicon')
    if len(icon) > 1:
        # print(country_name +'\thas sub country')
        get_coexist_country_info(country_name, ul)
    else:
        for i in ul.find_all(text=pattern):
            position = i.strip('\n -')
            d[country_name][position] = []
            # print(position)
            # print(d[country_name])
            leader_name = i.find_next_sibling()
            li = leader_name.find_all('li')
            if li != []:
                for j in li:
                    d[country_name][position].append(j.a.text)
            else:
                # print(d[country_name])
                d[country_name][position].append(leader_name.text)


def get_coexist_country_info(country_name, ul):
    for li in ul.select('> li'):
        sub_name = get_country_name(li)
        if sub_name == None:
            print(country_name)
            return
        country_name = country_name + ' - ' + sub_name
        d[country_name] = {}
        get_country_leader(country_name, li)
    pass


def get_country_info():
    # {'1945':{}, '1946':{'num': , 'country':{}}}
    # 'country': {'China':{}, 'Iran':{}}
    # 'China': {'Nationalist Government':{'url':, 'President':[] ,'Primer':[]}, '':{} }
    # start, end = set_year_range()
    start, end = 1945, 2019
    url_prefix = 'https://en.wikipedia.org/wiki/List_of_state_leaders_in_'
    for year in range(start, end):
        f = open('%s.txt' % year, 'w')
        print(year)
        if year > 1993 and year < 2000:
            continue
        url = url_prefix + str(year)
        c = requests.get(url).content
        soup = BeautifulSoup(c, 'html.parser')
        continent = get_continent(soup)
        num = 1
        for k, v in d.items():
            country = k
            f.write(str(num) + '\t' + country)
            # print(k,v)
            for i in v:
                position = i
                person = v[i]
                f.write('\t' + position + ': ')
                for p in person:
                    f.write(p + ',')
            f.write('\n')
            num += 1
        print(len(d))
    return


def get_country_name(content):
    l_check = [' > b > a', ' > a', '> b']
    for i in l_check:
        name = content.select(i)
        if name:
            l_name_info = []
            for item in name:
                l_name_info.append(item.text)
            return country_name_info_format(l_name_info[0])
    return None

'''
def get_coexist_country_info(content):
    d_result = {}
    for i in content:
        coexist = i.find_next_sibling()
        for li in coexist.select('> li'):
            c_name = li.select('> a')
            if c_name:
                f_name = string_format(c_name[0].text)
                d_result[f_name] = {}
                leader = c_name[0].find_next_sibling()
                for l in leader.select('> li'):
                    for many in l.select('> ol > li'):
                        for a in many.select('a'):
                            position = ''
                            for i in l:
                                position = i
                                break
                            position = string_format(position)
                            leader_name = a.text
                            #leader_url = a['href']
                            c = d_result[f_name]
                            if c.get(position, '123'):
                                print(c)
                                c[position] = 'hhhh'
                                print(d_result[f_name].get(position))
                            else:
                                d_result[f_name][position].append(leader_name)
                                print(d_result)
                            #print((position, leader_name, leader_url))
                            break
                    for a in l.select('> a'):
                        postion = ''
                        for i in l:
                            position = i
                            break
                        position = string_format(position)
                        leader_name = a.text
                        leader_url = a['href']
                        #print((position, leader_name, leader_url))
                        break

'''

def main():
    get_country_info()


if __name__ == '__main__':
    main()
