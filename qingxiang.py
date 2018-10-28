import wikipedia
from bs4 import BeautifulSoup
import requests
import re
import mysql.connector


def get_country_name_order_by_GDP():
    count = 0
    D_c = {}
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    c = requests.get(url).content
    soup = BeautifulSoup(c,'html.parser')
    for tables in soup.find_all(class_='"wikitable"|}'):
        IMF2017 = tables.select('.wikitable tbody')[0]
        for tr in IMF2017.find_all('tr'):
            td = tr.select('td')
            if len(td) == 0:
                continue
            rank = td[0].text.strip()
            c_name = td[1].select('a')[0].text
            GDP = td[2].text.strip()
            # print((rank,c_name,GDP))
            D_c[c_name] = {'gdp':{'2017':{'IMF2017':{'GDP':GDP,'rank':rank}}}}
    return D_c


def get_country_government(D_country,D_gov):
    government = []
    D_r = {'President':'president','Chancellor':'chancellor','Prime Minister':'prime_minister'}
    for country in D_country:
        count = 0
        D_country[country]["government"] = []
        url = "https://en.wikipedia.org/wiki/" + country
        c = requests.get(url).content
        soup = BeautifulSoup(c,'html.parser')
        for tables in soup.find_all(class_="infobox"):
            trs = tables.select('tbody tr')
            for tr in trs:
                gover_title = tr.select("th a")
                for item in gover_title:
                    if item.text=="President" or item.text=="Chancellor" or item.text=="Prime Minister":
                        if D_r[item.text] == D_gov[country]:
                            url = item['href']
                            D_country[country]["url_leader"] = url
                            #print(url)
                            count += 1
                    if item.text == "Government":
                        politics = tr.select("td a")
                        for part in politics:
                            if bool(re.match(r'^[a-zA-z- ]+$',part.text)):
                                D_country[country]["government"].append(part.text.lower())
        if count == 0:
            print(country+"*****")
            D_country[country]["url_leader"] = "url_unknown"
        if D_country[country]["government"] == []:
            print((country))
                        ##print((count,country,D_country[country]["government"]))
    return D_country


def get_country_name():
    D_name = {}
    f = open("government.txt","r")
    for line in f.readlines():
        l = line.strip('\n').split("\t")
        name = l[0]
        D_name[name] = {}
    print(len(D_name))
    return D_name


def get_each_leaderlist():
    check = ['Candidate','Candidates','President','Term of Office','Term of office', 'Prime Minister', 'Portrait']
    f = open('info_v2.txt','r')
    for line in f.readlines()[1:]:
        L = line.strip('\n').split('\t')
        country = L[1]
        url_suffix = L[2]
        if url_suffix != 'url_unknown':
            url = "https://en.wikipedia.org" + url_suffix
            c = requests.get(url).content
            soup = BeautifulSoup(c,'html.parser')
            tables = soup.find_all(class_="wikitable")
            count = len(tables)
            L_title = []
            for t in tables:
                title = t.select("tr")[0]
                l = title.text.strip(' \n').split('\n')
                L_title.append(l)
            if count == 1:
                n = 0
                for i in check:
                    if i not in l:
                        n += 1
                if n == len(check):
                    continue
            elif count > 1:
                n = 0
                for i in check:
                    if i not in l:
                        n+=1
                if n == len(check):
                    print(L[1])
                    print(L_title)
            else:
                continue
                #print(L[1])
                    

def main():
    connect_db()
    # get_each_leaderlist()
    '''
    #get_dominate_position()
    D_gov = {}
    D = get_country_name()
    #D = {'China':{}}
    f = open("info_v2.txt","w")
    r = open("dominate_position_v1.txt","r")
    for line in r.readlines():
        L = line.strip('\n').split("\t")
        name = L[1]
        gov = L[2]
        D_gov[name] = gov
    newD = get_country_government(D,D_gov)
    count = 0
    f.write("#\t" + "country\t" + "leader_url\t" + "government\n")
    for c in newD:
        count += 1
        print(c)
        f.write(str(count)+'\t'+c+'\t'+newD[c]["url_leader"]+'\t'+' '.join(newD[c]["government"])+'\n')
    '''


def update_country_info():
    D = {}
    db = connect_db()
    gover = open('government.txt', 'r')
    postion = open('dominate_position_v1.txt', 'r')
    for line in gover:
        L = line.strip('\n').split('\t')
        country = L[0]
        government_type = ','.join(L[1:])
        D[country] = {}
        D[country]['government'] = government_type
    for line in postion:
        L = line.strip('\n').split('\t')
        country = L[1]
        leading_position = L[2]
        D[country]['leading_position'] = leading_position
    for k in D:
        sql = "insert into country(country,government,leading_position) values\
         ('%s','%s','%s')" % (k, D[k]['government'], D[k]['leading_position'])
        insert_db(db, sql)
    return


def insert_db(db, sql):
    cursor = db.cursor()

    try:
        cursor.execute(sql)
        db.commit()
    except:
        print("insert fails")
        db.rollback()


def connect_db():
    user = 'root'
    password = open('pass.txt', 'r').readline(100)
    database = 'political_research'
    db = mysql.connector.connect(user=user, password=password, database=database)
    return db


def create_table(db):
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS Test")
    sql = """CREATE TABLE Test (
            ID CHAR(10) NOT NULL,
            Name CHAR(8),
            Grade INT )"""
    cursor.execute(sql)


def get_dominate_position():
    f = open("government.txt","r")
    w = open("dominate_position_v1.txt","w")
    count = 1
    for line in f.readlines():
        L = line.strip('\n').split("\t")
        if L[1] == '':
            w.write((str(count)) + "\t" + L[0] + "\t" + "no_source\n")
            count += 1
            continue
        if L[0] in ['Germany','Austria']:
            w.write(str(count) + "\t" + L[0] + "\t" + "chancellor\n")
            count += 1
        elif 'presidential' in L or 'semi-presidential' in L:
            w.write(str(count) + "\t" + L[0] + "\t" + "president\n")
            count += 1
        elif 'parliamentary' in L or 'parliamentary republic' in L or 'unitary parliamentary republic' in L:
            w.write(str(count) + "\t" + L[0] + "\t" + "prime_minister\n")
            count += 1
        else:
            if 'China' in L or 'France' in L:
                w.write(str(count) + "\t" + L[0] + "\t" + "president\n")
            else:
                print(L)
                w.write(str(count) + "\t" + L[0] + "\t" + "unknown\n")
            count += 1


if __name__ == "__main__":
    main()
