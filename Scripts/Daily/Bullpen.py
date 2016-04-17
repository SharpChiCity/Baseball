#! /usr/bin/python	
from bs4 import BeautifulSoup
import requests, re, sys
import os
import psycopg2
from datetime import date

game_date = str(date.today())[-5:]
date_month, date_day = game_date[:2], game_date[-2:]

gameday_url = ('http://gd2.mlb.com/components/game/mlb/year_2016/month_%s/day_%s/' % (date_month,date_day))
all_game_ids = []
soup_day = BeautifulSoup(requests.get(gameday_url).text, 'html.parser')

for day_link in soup_day.find_all('a'):
    if day_link['href'][:3] == 'gid':
        all_game_ids.append(day_link['href'])

bbpress_to_gameday = {'Arizona Diamondbacks':'ari','Atlanta Braves':'atl','Baltimore Orioles':'bal','Boston Red Sox':'bos','Chicago Cubs':'chn','Chicago White Sox':'cha','Cincinnati Reds':'cin','Cleveland Indians':'cle','Colorado Rockies':'col','Detroit Tigers':'det','Houston Astros':'hou','Kansas City Royals':'kca','Los Angeles Angels':'ana','Los Angeles Dodgers':'lan','Miami Marlins':'mia','Milwaukee Brewers':'mil','Minnesota Twins':'min','New York Mets':'nyn','New York Yankees':'nya','Oakland Athletics':'oak','Philadelphia Phillies':'phi','Pittsburgh Pirates':'pit','San Diego Padres':'sdn','San Francisco Giants':'sfn','Seattle Mariners':'sea','St. Louis Cardinals':'sln','Tampa Bay Rays':'tba','Texas Rangers':'tex','Toronto Blue Jays':'tor','Washington Nationals':'was'}


url = 'http://dailybaseballdata.com/cgi-bin/bullpen.pl?lookback=7'

created_at_stamp = datetme.now()
rawPEN = requests.get(url)
PENsoup = BeautifulSoup(rawPEN.text,'html.parser')

fp=open(os.path.dirname(os.path.realpath(__file__)) + "\\BullpenData.txt", "w")
PEN = PENsoup.find_all('tr')
start_tr = 12
pitcher_counter = 0
PENpitcher_stats = PENsoup.find_all('td', bgcolor='#FFEBCD')

conn = psycopg2.connect("host='localhost' dbname='baseball' user='postgres' password='password'")
conn.autocommit = True
c = conn.cursor()

team = ''

while start_tr < len(PEN):
    # print str(start_tr+1)+'/'+str(len(PEN))
    PENdata = PEN[start_tr]
    

    if str(PENdata)[0:38] == '<tr><td align="left" bgcolor="#003399"':
        bbpress_team_name = PENdata.find_all('b')[0].get_text().strip()
        fp.write(bbpress_team_name + '\n')
        team = bbpress_to_gameday[bbpress_team_name]
        
        game_id = 'n/a'
        for id in all_game_ids:
            if team in id:
                game_id = id[4:-1].replace('mlb','')
            
        
    elif str(PENdata)[0:37] == '<tr><td align="left" bgcolor="#FFE4C4':
        
        PENpitcher_names = PENdata.find_all('td')

        name = PENpitcher_names[0].get_text().strip()

        fp.write(name + '|') ## write pitchers name
        # print PENpitcher_names[0].get_text().strip()

        #### pitcher_counter * 14 + ~~~~~~~~~~~ should go in a row from 0 to # of games - 1
        #### e.g. -- 7 games, IP data goes from 0 to 6, Pitches (Pit) data goes from 7 to 13

        def get_info(width, column, list =PENpitcher_stats, row = pitcher_counter):
            data = list[row * width + column].get_text()[:3].replace('.1','.33').replace('.2','.66')
            if data == '-':
                data = 0
            return data
            
            
        g1_inn = get_info(14, 0)    
        g2_inn = get_info(14, 1)
        g3_inn = get_info(14, 2)
        g4_inn = get_info(14, 3)
        g5_inn = get_info(14, 4)
        g6_inn = get_info(14, 5)
        g7_inn = get_info(14, 6)

        g1_pit = get_info(14, 7)
        g2_pit = get_info(14, 8)
        g3_pit = get_info(14, 9)
        g4_pit = get_info(14, 10)
        g5_pit = get_info(14, 11)
        g6_pit = get_info(14, 12)
        g7_pit = get_info(14, 13)

        flag = 'available'
        if g1_inn >= 2 \
            or g1_pit >= 35 \
            or sum(x > 0 for x in [g1_pit, g2_pit, g3_pit, g4_pit]) >= 3:
            flag = 'out'                

		# Pitches > 35 or IP >= 2
        sql = '''
        INSERT INTO bullpens
        (game_id, team, player, status, inn_day_one, pit_day_one, inn_day_two, pit_day_two, 
        inn_day_three, pit_day_three, inn_day_four, pit_day_four, inn_day_five, pit_day_five, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        '''
        c.execute(sql, (game_id, team, name, flag, g1_inn, g1_pit, g2_inn, g2_pit, g3_inn, g3_pit, g4_inn, g4_pit, g5_inn, g5_pit, created_at_stamp))
        conn.commit()


        pitcher_counter += 1
        fp.write('%s (%s)|%s (%s)|%s (%s)|%s (%s)|%s (%s)|%s (%s)|%s (%s)' % \
                (g1_inn, g1_pit, g2_inn, g2_pit, g3_inn, g3_pit, g4_inn, g4_pit, g5_inn, g5_pit, g6_inn, g6_pit, g7_inn, g7_pit))
        fp.write('||%s|%s|%s|%s|%s\n' % (g1_pit, g2_pit, g3_pit, g4_pit, g5_pit))
    start_tr += 1


fp.close
conn.close()