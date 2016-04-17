from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
from datetime import date
import dataset
import re


class DriverSetup:
    ''' use to compile all selenium driver related code.
    This includes initializing and closing the browser, pointing to
    specific web pages, and parsing the HTML to store results within the class.

    Currently there is no ability to do two bs.find_all()
    searches within this class.
    '''
    def __init__(self, dr='', soup='', search_results=''):
        self.dr = webdriver.Chrome()
        self.soup = soup
        self.search_results = search_results

    def close(self):
        self.dr.close()

    def go_to_page(self, link, sleeper=5):
        self.dr.get(link)
        time.sleep(sleeper)
        self.soup = BeautifulSoup(self.dr.page_source, 'html.parser')

    def f_a(self, t):
        '''
        Take a tag (t) and pass to the find_all bs4 method
        '''
        self.search_results = self.soup.find_all(t, id=i)

    def fai(self, t, i):
        '''
        Take a tag (t) and an id (i) and pass to the find_all bs4 method
        '''
        self.search_results = self.soup.find_all(t, id=i)

    def fac(self, t, c):
        '''
        Take a tag (t) and a class (c) and pass to the find_all bs4 method
        '''
        self.search_results = self.soup.find_all(t, class_=i)


class GameInfo:
    '''
    Stores all information related to a game
    '''
    def __init__(self, game_date='', game_link='',
                 bleacher_ticket_status='unknown'):
        self.date = game_date
        self.link = game_link
        self.status = bleacher_ticket_status
        self.prices = {}


def convert_text_to_date(string):
    # single line of code to convert date in the form of "Apr 16" to 04/16/2016
    return datetime.strftime(
        datetime.strptime(string + ' 2016', '%b %d %Y'),
        '%m/%d/%Y')


if __name__ == '__main__':
    ''' this function points to the cubs ticket website, grabs all games where
    tickets are being sold (via dr.fai), stores all info for each particular
    game in a list of classes. WIll then parse through that list into a db
    '''

    # GET TICKET INFORMATION
    tickets_url = 'http://chicago.cubs.mlb.com/ticketing/singlegame.jsp?c_id=chc'

    dr = DriverSetup()
    dr.go_to_page(tickets_url)

    dr.fai('li', re.compile('(^gm)\d{6}'))

    # BUILD LIST OF CLASSES TO STORE GAME INFO
    objs = list()
    for i in range(len(dr.search_results)):
        objs.append(GameInfo())

    # FOR EACH GAME, GET INFO
    for n, game in enumerate(dr.search_results):
        cl = objs[n]

        cl.date = convert_text_to_date(game.find('li', class_='game_date').text)
        print(cl.date)

        cl.link = game.find('a', class_='bam-button bam-button-tickets')['href']

        if 'soldout' in cl.link:
            cl.status = 'soldout'
        else:
            dr.go_to_page(cl.link, 2)

            dr.fai('div', 'availability_right_column')

            for r in dr.search_results[0].find_all('div', class_='price_level_row')[1:]:
                section_name = r.find('div', class_ = 'price_level_header').get_text().strip()
                section_price = r.find('div', class_ = 'price_amount').get_text().strip()
                section_price_with_tax = round(
                    float(section_price.replace('$', '')) * 1.12 + 4.75 * 1.09, 2)
                cl.prices[section_name] = section_price_with_tax

            try:
                cl.status = cl.prices['Budweiser Bleachers']
            except KeyError:
                cl.status = 'soldout'

    f = open(os.path.dirname(os.path.realpath(__file__)) + '/cubs_tix.txt','w')
    g = open(os.path.dirname(os.path.realpath(__file__)) + '/cubs_tix_all.txt','a')
    for i in objs:
        f.write('{0}|{1}\n'.format(i.date, i.status))
        g.write('{0}|{1}|{2}\n'.format(str(date.today())[:],i.date, i.status))
    f.close()
    g.close()


    dr.close()
