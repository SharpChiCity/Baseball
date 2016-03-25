from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
import time
from datetime import datetime
import dataset
import re

class DriverSetup:
    "use to compile all Selenium Driver related code"
    def __init__(self, dr = '', soup = '', search_results = ''):
        self.dr = webdriver.Chrome()
        self.soup = soup
        self.search_results = search_results
        #
    def close(self):
        self.dr.close()
        #
    def go_to_page(self, link, sleeper = 5):
        self.dr.get(link)
        time.sleep(sleeper)
        self.soup = BeautifulSoup(self.dr.page_source, 'html.parser')
        #
    def f_a(self, t):
        '''
        Take a tag (t) and pass to the find_all bs4 method
        '''
        self.search_results = self.soup.find_all(t, id = i)
        #
    def f_a_i(self, t, i):
        '''
        Take a tag (t) and an id (i) and pass to the find_all bs4 method
        '''
        self.search_results = self.soup.find_all(t, id = i)
        #
    def f_a_c(self, t, c):
        '''
        Take a tag (t) and a class (c) and pass to the find_all bs4 method
        '''
        self.search_results = self.soup.find_all(t, class_ = i)


class GameInfo:
    "all information related to a game"
    def __init__(self, game_date = '', game_link = '', bleacher_ticket_status = 'unknown'):
        self.date = game_date
        self.link = game_link
        self.status = bleacher_ticket_status
        self.prices =  {}

def convert_text_to_date(string):
    return datetime.strftime(datetime.strptime(string + ' 2016', '%b %d %Y'), '%m/%d/%Y')
        


if __name__ == '__main__':

    tickets_url = 'http://chicago.cubs.mlb.com/ticketing/singlegame.jsp?c_id=chc'

    dr = DriverSetup()
    dr.go_to_page(tickets_url)

    dr.f_a_i('li',re.compile('(^gm)\d{6}'))


    objs = list()

    for i in range(len(dr.search_results)):
        objs.append(GameInfo())


    for n, game in enumerate(dr.search_results):
        cl = objs[n]
        #
        cl.date = convert_text_to_date(game.find('li', class_ = 'game_date').text)
        print(cl.date)
        #
        cl.link = game.find('a', class_ = 'bam-button bam-button-tickets')['href']
        #
        if 'soldout' in cl.link:
            cl.status = 'soldout'
        else:
            dr.go_to_page(cl.link, 2)
            #
            dr.f_a_i('div','availability_right_column')
            #
            for r in dr.search_results[0].find_all('div', class_ = 'price_level_row')[1:]:
                section_name = r.find('div', class_ = 'price_level_header').get_text().strip()
                section_price = r.find('div', class_ = 'price_amount').get_text().strip()
                section_price_with_tax = float(section_price.replace('$','')) * 0.12 + 4.75 * 1.09
                cl.prices[section_name] = section_price_with_tax
            # 
            try:
                cl.status = cl.prices['Budweiser Bleachers']
            except KeyError:
                cl.status = 'soldout'

    f = open('C:/users/monstar/downloads/cubs_tix.txt','w')
    for i in objs:
        f.write('{0}|{1}\n'.format(i.date, i.status))
    f.close()

    dr.close()