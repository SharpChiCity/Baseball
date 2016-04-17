#! /usr/bin/python
from bs4 import BeautifulSoup
import requests
import sys
import time
import codecs
from datetime import date,time,timedelta, datetime
import os
import psycopg2
import re

# from unidecode import unidecode

conn = psycopg2.connect("host='localhost' dbname='baseball' user='postgres' password='password'")
conn.autocommit = True
c = conn.cursor()

sbr_to_mlb = {'ARI':'ari','ATL':'atl','BAL':'bal','BOS':'bos','CHC':'chn','CIN':'cin','CLE':'cle','COL':'col', \
             'CWS':'cha','DET':'det','HOU':'hou', 'KC':'kca','LAA':'ana','LAD':'lan','MIA':'mia','MIL':'mil', \
             'MIN':'min','NYM':'nyn','NYY':'nya','OAK':'oak','PHI':'phi','PIT':'pit','SD':'sdn','SEA':'sea', \
              'SF':'sfn','STL':'sln', 'TB':'tba','TEX':'tex','TOR':'tor','WSH':'was'}


            
def unidecode(str):
    # replace u'\xa0' and u'xbd'
    str_new = str.replace(u'\xa0',' ').replace(u'\xbd','.5')
    return str_new
### I've replaced this code with unidecode(str).

def getinfo(s, t, nbr, i, c):
    return unidecode(s.find_all('div', 'el-div eventLine-'+t, rel=nbr)[i].find_all('div')[c].get_text().strip())


date_input = raw_input("Please enter a date (yyyymmdd, yyyy-mm-dd, mmdd, or, mm-dd) or # days in past:")
if date_input == '':
    tdate = str(date.today()).replace('-','')
elif len(date_input) < 3:
    tdate = str(date.today() - timedelta(days=int(date_input))).replace("-",'')
else:
        tdate = date_input
print(tdate)

date_month, date_day = tdate[4:6], tdate[-2:]   

gameday_url = ('http://gd2.mlb.com/components/game/mlb/year_2016/month_%s/day_%s/' % (date_month,date_day))
all_game_ids = []
soup_day = BeautifulSoup(requests.get(gameday_url).text, 'html.parser')

for day_link in soup_day.find_all('a'):
    if day_link['href'][:3] == 'gid':
        all_game_ids.append(day_link['href'])


url_paths_lines = {'ml':'' \
            ,'ff_ml':'1st-half/' \
           }
url_paths_totals = {'tot':'totals/' \
            ,'ff_tot':'totals/1st-half/' \
            ,'rl':'pointspread/' \
            ,'ff_rl':'pointspread/1st-half/' \
           }

for key, value in url_paths_lines.items():
    
    created_at_stamp = datetime.now()
    raw_data = requests.get('http://www.sportsbookreview.com/betting-odds/mlb-baseball/{}?date={}'.format(value,tdate))
    soup = BeautifulSoup(raw_data.text,'html.parser')
    print('~~~{}~~~'.format(key))

    number_of_games = len(soup.find_all('div', 'el-div eventLine-rotation'))

    for i in range(0, number_of_games):
        print(str(i+1)+'/'+str(number_of_games))
        
        consensus_data = soup.find_all('div', 'el-div eventLine-consensus')[i].get_text()
        con_data = re.search('(\d{1,3}\..)%(\d{1,3}\..)', consensus_data)
        
        con1 =      con_data.group(1)
        gm_info1 =  getinfo(soup,'team','',i,0)
        gm_details1 = re.search('(.{2,3})()()',gm_info1) if len(gm_info1) < 4 else re.search('(.{2,3}) - (.*?) \((.)\)', gm_info1)
        team1 =     gm_details1.group(1)
        pitcher1 =  gm_details1.group(2)
        hand1 =     gm_details1.group(3)
        ope1 =      getinfo(soup,'opener','',i,0) or 0
        fiv1 =      getinfo(soup,'book','19',i,0) or 0
        pin1 =      getinfo(soup,'book','238',i,0) or 0
        her1 =      getinfo(soup,'book','169',i,0) or 0
        bet1 =      getinfo(soup,'book','1096',i,0) or 0
        best1 =     max(fiv1,her1,bet1)
    #
        con2 =      con_data.group(2)
        gm_info2 =  getinfo(soup,'team','',i,1)
        gm_details2 = re.search('(.{2,3})()()',gm_info1) if len(gm_info1) < 4 else re.search('(.{2,3}) - (.*?) \((.)\)', gm_info1)
        team2 =     gm_details2.group(1)
        pitcher2 =  gm_details2.group(2)
        hand2 =     gm_details2.group(3)
        
        ope2 =      getinfo(soup,'opener','',i,1) or 0
        fiv2 =      getinfo(soup,'book','19',i,1) or 0
        pin2 =      getinfo(soup,'book','238',i,1) or 0
        her2 =      getinfo(soup,'book','169',i,1) or 0
        bet2 =      getinfo(soup,'book','1096',i,1) or 0
        best2 =     max(fiv2,her2,bet2)
    #	
        
        mlb_id1 = sbr_to_mlb[team1]
        for id in all_game_ids:
            if mlb_id1 in id:
                game_id1 = id[4:-1].replace('mlb','')
        
        mlb_id2 = sbr_to_mlb[team2]
        for id in all_game_ids:
            if mlb_id2 in id:
                game_id2 = id[4:-1].replace('mlb','')
            
        final_flag = False
        if datetime.strptime(str(date.today()), '%Y-%m-%d') > datetime.strptime(tdate + '', '%Y%m%d'):
            final_flag = True

        
        sql = '''
        INSERT INTO {}_odds
        (game_id, team, final_flag, consensus, opening, pin, fiv, bet, her, best, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        '''.format(key)
        c.execute(sql, (game_id1, mlb_id1, final_flag, con1, ope1, pin1, fiv1, bet1, her1, best1, created_at_stamp))
        c.execute(sql, (game_id2, mlb_id2, final_flag, con2, ope2, pin2, fiv2, bet2, her2, best2, created_at_stamp))
        conn.commit()

def get_odds_lines(helper, data):
    if helper in ['tot', 'ff_tot']:
        r = re.search('(.*?) (....)',data)
    else:
        r = re.search('(.1\.5) (....)', data)
    if r == 0 or r == None:
        return None, None
    else:
        return r.group(1),r.group(2)
    

for key, value in url_paths_totals.items():
    
    created_at_stamp = datetime.now()
    raw_data = requests.get('http://www.sportsbookreview.com/betting-odds/mlb-baseball/{}?date={}'.format(value,tdate))
    soup = BeautifulSoup(raw_data.text,'html.parser')
    print('~~~{}~~~'.format(key))

    number_of_games = len(soup.find_all('div', 'el-div eventLine-rotation'))

    for i in range(0, number_of_games):
        print('{}/{}'.format(str(i+1), str(number_of_games)))
        
        consensus_data = soup.find_all('div', 'el-div eventLine-consensus')[i].get_text()
        con_data = re.search('(\d{1,3}\..)%(\d{1,3}\..)', consensus_data)
        
        con1 =          con_data.group(1)
        gm_info1 =      getinfo(soup,'team','',i,0)
        gm_details1 =   re.search('(.{2,3})()()',gm_info1) if len(gm_info1) < 4 else re.search('(.{2,3}) - (.*?) \((.)\)', gm_info1)
        team1 =         gm_details1.group(1)
        pitcher1 =      gm_details1.group(2)
        hand1 =         gm_details1.group(3)
        ope1 =          getinfo(soup,'opener','',i,0)
        ope1_line, ope1_odds = get_odds_lines(key, ope1)    
        fiv1 =          getinfo(soup,'book','19',i,0)
        fiv1_line, fiv1_odds = get_odds_lines(key, fiv1)
        pin1 =          getinfo(soup,'book','238',i,0)
        pin1_line, pin1_odds = get_odds_lines(key, pin1)
        her1 =          getinfo(soup,'book','169',i,0)
        her1_line, her1_odds = get_odds_lines(key, her1)
        bet1 =          getinfo(soup,'book','1096',i,0)
        bet1_line, bet1_odds = get_odds_lines(key, bet1)
        
        #
        con2 =      con_data.group(2)
        gm_info2 =  getinfo(soup,'team','',i,1)
        gm_details2 = re.search('(.{2,3})()()',gm_info1) if len(gm_info1) < 4 else re.search('(.{2,3}) - (.*?) \((.)\)', gm_info1)
        team2 =     gm_details2.group(1)
        pitcher2 =  gm_details2.group(2)
        hand2 =     gm_details2.group(3)
        
        con2 =          con_data.group(1)
        gm_info2 =      getinfo(soup,'team','',i,0)
        gm_details2 =   re.search('(.{2,3})()()',gm_info2) if len(gm_info2) < 4 else re.search('(.{2,3}) - (.*?) \((.)\)', gm_info2)
        team2 =         gm_details2.group(1)
        pitcher2 =      gm_details2.group(2)
        hand2 =         gm_details2.group(3)
        ope2 =          getinfo(soup,'opener','',i,0)
        ope2_line, ope2_odds = get_odds_lines(key, ope2)    
        fiv2 =          getinfo(soup,'book','19',i,0)
        fiv2_line, fiv2_odds = get_odds_lines(key, fiv2)
        pin2 =          getinfo(soup,'book','238',i,0)
        pin2_line, pin2_odds = get_odds_lines(key, pin2)
        her2 =          getinfo(soup,'book','169',i,0)
        her2_line, her2_odds = get_odds_lines(key, her2)
        bet2 =          getinfo(soup,'book','1096',i,0)
        bet2_line, bet2_odds = get_odds_lines(key, bet2)
        
        
        mlb_id1 = sbr_to_mlb[team1]
        for id in all_game_ids:
            if mlb_id1 in id:
                game_id1 = id[4:-1].replace('mlb','')
        
        mlb_id2 = sbr_to_mlb[team2]
        for id in all_game_ids:
            if mlb_id2 in id:
                game_id2 = id[4:-1].replace('mlb','')
            
        final_flag = False
        if datetime.strptime(str(date.today()), '%Y-%m-%d') > datetime.strptime(tdate + '', '%Y%m%d'):
            final_flag = True

        
        sql = '''
        INSERT INTO {}_odds
        (game_id, team, final_flag, consensus, opening_line, opening_odds
        , pin_line, pin_odds, fiv_line,fiv_odds,bet_line, bet_odds, her_line, her_odds, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        '''.format(key)
        c.execute(sql, (game_id1, mlb_id1, final_flag, con1, ope1_line, ope1_odds, \
            pin1_line, pin1_odds, fiv1_line, fiv1_odds, bet1_line, bet1_odds, her1_line, her1_odds, created_at_stamp))
        c.execute(sql, (game_id2, mlb_id2, final_flag, con2, ope2_line, ope2_odds, \
            pin2_line, pin2_odds, fiv2_line, fiv2_odds, bet2_line, bet2_odds, her2_line, her2_odds, created_at_stamp))
        conn.commit()
        
conn.close()
