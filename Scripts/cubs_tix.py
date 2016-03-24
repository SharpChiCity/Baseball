from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
import time

dr = webdriver.Chrome()


tickets_url = 'http://chicago.cubs.mlb.com/ticketing/singlegame.jsp?c_id=chc'

dr.get(tickets_url)
time.sleep(5)
s = BeautifulSoup(dr.page_source, 'html.parser')

games = s.find_all('li', id = re.compile('(^gm)\d{6}'))


class GameInfo:
	"all information related to a game"
	def __init__(self, game_date = '', game_link = '', bleacher_ticket_status = 'unknown'):
		self.date = game_date
		self.link = game_link
		self.status = bleacher_ticket_status
		self.prices =  {}


objs = list()

for i in range(len(games)):
    objs.append(GameInfo())



for n, game in enumerate(games[1:]):	
    cl = objs[n]
    #
    game_date_raw = game.find('li', class_ = 'game_date').text
    game_date_date = datetime.strptime(game_date_raw + ' 2016', '%b %d %Y')
    # game_date = datetime.strftime(game_date_date, '%m/%d/%Y')
    cl.date = datetime.strftime(game_date_date, '%m/%d/%Y')
    print(cl.date)
    #
    cl.link = game.find('a', class_ = 'bam-button bam-button-tickets')['href']
    #
    if 'soldout' in cl.link:
        cl.status = 'soldout'
    dr.get(cl.link)
    time.sleep(2)
    availability_raw = s2.find('div', id = 'availability_right_column')
    #
    for r in availability_raw.find_all('div', class_ = 'price_level_row')[1:]:
        section_name = r.find('div', class_ = 'price_level_header').get_text().strip()
        section_price = r.find('div', class_ = 'price_amount').get_text().strip()
        cl.prices[section_name] = section_price
    #
    try:
        cl.status = cl.prices['Budweiser Bleachers']
    except KeyError:
        cl.status = 'soldout'
