#! /usr/bin/python
from bs4 import BeautifulSoup
import requests, re, sys, os, codecs
from datetime import date,time,timedelta, datetime
import time
import psycopg2

date_input =  raw_input("Please enter an date (m-d) or # days in past:")
if date_input == '':
        tdate = str(date.today())[-5:]
elif len(date_input) < 3:
        tdate = str(date.today() - timedelta(days=int(date_input)))[-5:]
else:
        tdate = date_input
print(tdate)
        
conn = psycopg2.connect("host='localhost' dbname='baseball' user='postgres' password='password'")
conn.autocommit = True
c = conn.cursor()

fp=open(os.path.dirname(os.path.realpath(__file__)) + '/bbpress.txt', 'w')

# print('http://www.baseballpress.com/lineups/2016-'+tdate)
created_at_stamp = datetime.now()
raw_data = requests.get('http://www.baseballpress.com/lineups/2016-'+tdate)

soup = BeautifulSoup(raw_data.text,'html.parser')

Team = []
Pitcher = []
Lineup = []
Lineup_database = []

team_datas = soup.find_all('div', 'team-data') # Team Names and SP
lineup_datas = soup.find_all('div', 'team-lineup clearfix') # Lineup and handedness

def break_up_hitter_info(hitter_info):
    x = re.search('(?P<hitter>.*?) \((?P<hand>[L|R|S])\) (?P<pos>.{1,2})', hitter_info)
    if x == None:
        return (None, None, None)
    else:
        return (x.group('hitter'), x.group('pos'), x.group('hand'))
        
for i in range(0, len(team_datas)):
    team_name = team_datas[i].find_all('div')[2].get_text()
    Team.append(team_name)

    pitcher_name_hand = team_datas[i].find_all('div')[3].get_text()
    Pitcher.append(pitcher_name_hand)

for j in range(0, len(lineup_datas)):
    lu = lineup_datas[j].find_all('div')
    if len(lu) < 11:
        for l in range(0,9):
            Lineup.append('')
            Lineup_database.append(break_up_hitter_info(''))

    else: 
        for k in range(2,11):
            player = lu[k].get_text()[3:]
            Lineup.append(player[:player.find(')')+1])
            Lineup_database.append(break_up_hitter_info(player))
            
lineup_rev = Lineup[:]
lineup_rev.reverse()
lineup_database_rev = Lineup_database[:]
lineup_database_rev.reverse()

A = []
H = []
A_database = []
H_database = []
counter = 0

for n in range(0, len(Team)):
    if counter == 0:
        A.append(Team[n])
        A_database.append(Team[n])
        A.append(Pitcher[n])
        A_database.append(Pitcher[n])
        for o in range(0, 9):
            A.append(Lineup[n*9+o])
            A_database.append(Lineup_database[n*9+o])
        counter = 1
    else:
        H.append(Team[n])
        H_database.append(Team[n])
        H.append(Pitcher[n])
        H_database.append(Pitcher[n])
        for o in range(0, 9):
            H.append(Lineup[n*9+o])
            H_database.append(Lineup_database[n*9+o])
        counter = 0

counter2 = 0

fp.write(tdate + '\n')

for x in range(0, len(A)):
	if counter2 == 11:
		counter2 = 1
	else:
		counter2 += 1
		
	if counter2 == 1:
		fp.write(A[x]+"||"+H[x]+"\n")
	else:
		Aparen = A[x].find('(')
		Aside = A[x][Aparen + 1:Aparen + 2]
		Aname = A[x][:Aparen - 1]
		
		Hparen = H[x].find('(')
		Hside = H[x][Hparen + 1:Hparen + 2]
		Hname = H[x][:Hparen - 1]
		fp.write('%s|%s|%s|%s\n' % (Aname, Aside, Hname, Hside))
# print(A)
# print(H)	
fp.close


date_month, date_day = tdate[:2], tdate[-2:]

gameday_url = ('http://gd2.mlb.com/components/game/mlb/year_2016/month_%s/day_%s/' % (date_month,date_day))
all_game_ids = []
soup_day = BeautifulSoup(requests.get(gameday_url).text, 'html.parser')

for day_link in soup_day.find_all('a'):
    if day_link['href'][:3] == 'gid':
        all_game_ids.append(day_link['href'])
      
def get_game_id(team_name):
    mlb_id = bbpress_to_gameday[team_name]
    for game_id_option in all_game_ids:
        if mlb_id in game_id_option:
            id = game_id_option[4:-1].replace('mlb','')
    return id
            
bbpress_to_gameday = {'Angels':'ana','Astros':'hou','Athletics':'oak','Blue Jays':'tor','Braves':'atl','Brewers':'mil','Cardinals':'sln','Cubs':'chn','Diamondbacks':'ari','Dodgers':'lan','Giants':'sfn','Indians':'cle','Mariners':'sea','Marlins':'mia','Mets':'nyn','Nationals':'was','Orioles':'bal','Padres':'sdn','Phillies':'phi','Pirates':'pit','Rangers':'tex','Rays':'tba','Red Sox':'bos','Reds':'cin','Rockies':'col','Royals':'kca','Tigers':'det','Twins':'min','White Sox':'cha','Yankees':'nya'}

           
final_flag = False
if datetime.strptime(str(date.today()), '%Y-%m-%d') > datetime.strptime(tdate + '-2016', '%m-%d-%Y'):
    final_flag = True


    
x = 0
while x < len(A):
    sql = ''' INSERT INTO lineups (
        game_id, final_flag, team, home_away_flag
        , hit_one_name  , hit_one_pos   , hit_one_hand
        , hit_two_name  , hit_two_pos   , hit_two_hand
        , hit_three_name, hit_three_pos , hit_three_hand
        , hit_four_name , hit_four_pos  , hit_four_hand
        , hit_five_name , hit_five_pos  , hit_five_hand
        , hit_six_name  , hit_six_pos   , hit_six_hand
        , hit_seven_name, hit_seven_pos , hit_seven_hand
        , hit_eight_name, hit_eight_pos , hit_eight_hand
        , hit_nine_name , hit_nine_pos  , hit_nine_hand
        , created_at)
    VALUES (
    %s, %s, %s, %s, 
    %s, %s, %s, 
    %s, %s, %s, 
    %s, %s, %s, 
    %s, %s, %s, 
    %s, %s, %s, 
    %s, %s, %s, 
    %s, %s, %s, 
    %s, %s, %s, 
    %s, %s, %s, 
    %s) '''


    c.execute(sql, \
    (get_game_id(A_database[0+x]), final_flag, bbpress_to_gameday[A_database[0+x]], 'A' \
    , A_database[2+x][0], A_database[2+x][1], A_database[2+x][2] \
    , A_database[3+x][0], A_database[3+x][1], A_database[3+x][2] \
    , A_database[4+x][0], A_database[4+x][1], A_database[4+x][2] \
    , A_database[5+x][0], A_database[5+x][1], A_database[5+x][2] \
    , A_database[6+x][0], A_database[6+x][1], A_database[6+x][2] \
    , A_database[7+x][0], A_database[7+x][1], A_database[7+x][2] \
    , A_database[8+x][0], A_database[8+x][1], A_database[8+x][2] \
    , A_database[9+x][0], A_database[9+x][1], A_database[9+x][2] \
    , A_database[10+x][0], A_database[10+x][1], A_database[10+x][2] \
    , created_at_stamp))
    
    c.execute(sql, (get_game_id(H_database[0+x]), final_flag, bbpress_to_gameday[H_database[0+x]], 'H' \
    , H_database[2+x][0], H_database[2+x][1], H_database[2+x][2] \
    , H_database[3+x][0], H_database[3+x][1], H_database[3+x][2] \
    , H_database[4+x][0], H_database[4+x][1], H_database[4+x][2] \
    , H_database[5+x][0], H_database[5+x][1], H_database[5+x][2] \
    , H_database[6+x][0], H_database[6+x][1], H_database[6+x][2] \
    , H_database[7+x][0], H_database[7+x][1], H_database[7+x][2] \
    , H_database[8+x][0], H_database[8+x][1], H_database[8+x][2] \
    , H_database[9+x][0], H_database[9+x][1], H_database[9+x][2] \
    , H_database[10+x][0], H_database[10+x][1], H_database[10+x][2] \
    , created_at_stamp))
    
    x += 11
    
conn.close()