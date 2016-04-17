#! /usr/bin/python
from bs4 import BeautifulSoup
import requests
import sys
import time
import codecs
from datetime import date,time,timedelta
import os
import psycopg2

# from unidecode import unidecode


def unidecode(str):
    # replace u'\xa0' and u'xbd'
    str_new = str.replace(u'\xa0',' ').replace(u'\xbd','.5')
    return str_new
### I've replaced this code with unidecode(str).


date_input = raw_input("Please enter a date (yyyymmdd, yyyy-mm-dd, mmdd, or, mm-dd) or # days in past:")
if date_input == '':
    tdate = str(date.today()).replace('-','')
elif len(date_input) < 3:
    tdate = str(date.today() - timedelta(days=int(date_input))).replace("-",'')
else:
        tdate = date_input
print(tdate)

fp=open(os.path.dirname(os.path.realpath(__file__)) + "/SBRmlb.txt", "w")

raw_data = requests.get('http://www.sportsbookreview.com/betting-odds/mlb-baseball/?date=' + tdate)
soup = BeautifulSoup(raw_data.text,'html.parser')
print(1)
raw_data2 = requests.get('http://www.sportsbookreview.com/betting-odds/mlb-baseball/totals/?date=' + tdate)
soup2 = BeautifulSoup(raw_data2.text,'html.parser')
print(2)

number_of_games = len(soup.find_all('div', 'el-div eventLine-rotation'))

for i in range(0, number_of_games):
    print(str(i+1)+'/'+str(number_of_games))
    consensus_data =     soup.find_all('div', 'el-div eventLine-consensus')[i].get_text()
    
    rotation1 =     soup.find_all('div', 'el-div eventLine-rotation')[i].find_all('div')[0].get_text().strip()
    team1 =         soup.find_all('div', 'el-div eventLine-team')[i].find_all('div')[0].get_text().strip()
    opener1 =       soup.find_all('div', 'el-div eventLine-opener')[i].find_all('div')[0].get_text().strip()
    fivedimes1 =    soup.find_all('div', 'el-div eventLine-book', rel='19')[i].find_all('div')[0].get_text().strip()
    pinnacle1 =     soup.find_all('div', 'el-div eventLine-book', rel='238')[i].find_all('div')[0].get_text().strip()
    bovada1 =       '' # soup.find_all('div', 'el-div eventLine-book', rel='999996')[i].find_all('div')[0].get_text().strip()
    BO1 =           soup.find_all('div', 'el-div eventLine-book', rel='1096')[i].find_all('div')[0].get_text().strip()
#
    rotation2 =     soup.find_all('div', 'el-div eventLine-rotation')[i].find_all('div')[1].get_text().strip()
    team2 =         soup.find_all('div', 'el-div eventLine-team')[i].find_all('div')[2].get_text().strip()
    opener2 =       soup.find_all('div', 'el-div eventLine-opener')[i].find_all('div')[1].get_text().strip()
    fivedimes2 = 	soup.find_all('div', 'el-div eventLine-book', rel='19')[i].find_all('div')[1].get_text().strip()
    pinnacle2 = 	soup.find_all('div', 'el-div eventLine-book', rel='238')[i].find_all('div')[1].get_text().strip()
    bovada2 = 		'' # soup.find_all('div', 'el-div eventLine-book', rel='999996')[i].find_all('div')[1].get_text().strip()
    BO2 = 		    soup.find_all('div', 'el-div eventLine-book', rel='1096')[i].find_all('div')[1].get_text().strip()
#	
    consensus_data2 = 	soup2.find_all('div', 'el-div eventLine-consensus')[i].get_text()
#
    opener3 = 		soup2.find_all('div', 'el-div eventLine-opener')[i].find_all('div')[0].get_text().strip()
    fivedimes3 = 	soup2.find_all('div', 'el-div eventLine-book', rel='19')[i].find_all('div')[0].get_text().strip()
    pinnacle3 = 	soup2.find_all('div', 'el-div eventLine-book', rel='238')[i].find_all('div')[0].get_text().strip()
    bovada3 = 		'' # soup2.find_all('div', 'el-div eventLine-book', rel='999996')[i].find_all('div')[0].get_text().strip()
    BO3 = 			soup2.find_all('div', 'el-div eventLine-book', rel='1096')[i].find_all('div')[0].get_text().strip()
#
    opener4 = 		soup2.find_all('div', 'el-div eventLine-opener')[i].find_all('div')[1].get_text().strip()
    fivedimes4 = 	soup2.find_all('div', 'el-div eventLine-book', rel='19')[i].find_all('div')[1].get_text().strip()
    pinnacle4 = 	soup2.find_all('div', 'el-div eventLine-book', rel='238')[i].find_all('div')[1].get_text().strip()
    bovada4 = 		'' # soup2.find_all('div', 'el-div eventLine-book', rel='999996')[i].find_all('div')[1].get_text().strip()
    BO4 = 	        soup2.find_all('div', 'el-div eventLine-book', rel='1096')[i].find_all('div')[1].get_text().strip()
#	
    # consensus_data3 = 	soup3.find_all('div', 'el-div eventLine-consensus')[i].get_text()
# #
    # opener5 = 		soup3.find_all('div', 'el-div eventLine-opener')[i].find_all('div')[0].get_text().strip()
    # fivedimes5 = 	soup3.find_all('div', 'el-div eventLine-book', rel='19')[i].find_all('div')[0].get_text().strip()
    # pinnacle5 = 	soup3.find_all('div', 'el-div eventLine-book', rel='238')[i].find_all('div')[0].get_text().strip()
    # bovada5 = 		soup3.find_all('div', 'el-div eventLine-book', rel='999996')[i].find_all('div')[0].get_text().strip()
    # BO5 = 	        soup3.find_all('div', 'el-div eventLine-book', rel='1096')[i].find_all('div')[0].get_text().strip()
# #
    # opener6 = 		soup3.find_all('div', 'el-div eventLine-opener')[i].find_all('div')[1].get_text().strip()
    # fivedimes6 = 	soup3.find_all('div', 'el-div eventLine-book', rel='19')[i].find_all('div')[1].get_text().strip()
    # pinnacle6 = 	soup3.find_all('div', 'el-div eventLine-book', rel='238')[i].find_all('div')[1].get_text().strip()
    # bovada6 = 		soup3.find_all('div', 'el-div eventLine-book', rel='999996')[i].find_all('div')[1].get_text().strip()
    # BO6 = 	        soup3.find_all('div', 'el-div eventLine-book', rel='1096')[i].find_all('div')[1].get_text().strip()
# #	
    # consensus_data4 = 	soup4.find_all('div', 'el-div eventLine-consensus')[i].get_text()
# #
    # opener7 = 		soup4.find_all('div', 'el-div eventLine-opener')[i].find_all('div')[0].get_text().strip()
    # fivedimes7 = 	soup4.find_all('div', 'el-div eventLine-book', rel='19')[i].find_all('div')[0].get_text().strip()
    # pinnacle7 = 	soup4.find_all('div', 'el-div eventLine-book', rel='238')[i].find_all('div')[0].get_text().strip()
    # bovada7 = 		soup4.find_all('div', 'el-div eventLine-book', rel='999996')[i].find_all('div')[0].get_text().strip()
    # BO7 = 	        soup4.find_all('div', 'el-div eventLine-book', rel='1096')[i].find_all('div')[0].get_text().strip()
# #
    # opener8 = 		soup4.find_all('div', 'el-div eventLine-opener')[i].find_all('div')[1].get_text().strip()
    # fivedimes8 = 	soup4.find_all('div', 'el-div eventLine-book', rel='19')[i].find_all('div')[1].get_text().strip()
    # pinnacle8 = 	soup4.find_all('div', 'el-div eventLine-book', rel='238')[i].find_all('div')[1].get_text().strip()
    # bovada8 = 		soup4.find_all('div', 'el-div eventLine-book', rel='999996')[i].find_all('div')[1].get_text().strip()
    # BO8 = 	        soup4.find_all('div', 'el-div eventLine-book', rel='1096')[i].find_all('div')[1].get_text().strip()
#
    
    fp.write("%s, %s, %s, %s, %s, %s, %s, %s," % (unidecode(rotation1), unidecode(team1), unidecode(opener1), unidecode(consensus_data[:4]), unidecode(fivedimes1), unidecode(pinnacle1), unidecode(bovada1), unidecode(BO1)))
    fp.write("%s, %s, %s, %s, %s, %s," % (unidecode(opener3), unidecode(consensus_data2[:4]), unidecode(fivedimes3), unidecode(pinnacle3), unidecode(bovada3), unidecode(BO3)))
    # fp.write(".%s, %s, %s, %s, %s, %s," % (unidecode(opener5), unidecode(consensus_data3[:4]), unidecode(fivedimes5), unidecode(pinnacle5), unidecode(bovada5), unidecode(BO5)))
    # fp.write("%s, %s, %s, %s, %s, %s" % (unidecode(opener7), unidecode(consensus_data4[:4]), unidecode(fivedimes7), unidecode(pinnacle7), unidecode(bovada7), unidecode(BO7)))
    fp.write('\n')
    fp.write("%s, %s, %s, %s, %s, %s, %s, %s," % (unidecode(rotation2), unidecode(team2), unidecode(opener2), unidecode(consensus_data[5:-1]), unidecode(fivedimes2), unidecode(pinnacle2), unidecode(bovada2), unidecode(BO2)))
    fp.write("%s, %s, %s, %s, %s, %s," % (unidecode(opener4), unidecode(consensus_data2[5:-1]), unidecode(fivedimes4), unidecode(pinnacle4), unidecode(bovada4), unidecode(BO4)))
    # fp.write(".%s, %s, %s, %s, %s, %s," % (unidecode(opener6), unidecode(consensus_data3[5:-1]), unidecode(fivedimes6), unidecode(pinnacle6), unidecode(bovada6), unidecode(BO6)))
    # fp.write("%s, %s, %s, %s, %s, %s" % (unidecode(opener8), unidecode(consensus_data4[5:-1]), unidecode(fivedimes8), unidecode(pinnacle8), unidecode(bovada8), unidecode(BO8)))
    fp.write('\n')
fp.close

