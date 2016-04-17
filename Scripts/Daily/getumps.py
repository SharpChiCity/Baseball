from bs4 import BeautifulSoup
import requests
from datetime import datetime, date,time,timedelta
import os
import re
import psycopg2
from sqlalchemy import create_engine

gameday_to_xlsx = {'ari':'ARI','atl':'ATL','bal':'BAL','bos':'BOS','chn':'CHC','cha':'CHW','cin':'CIN','cle':'CLE','col':'COL','det':'DET','hou':'HOU','kca':'KC','ana':'LAA','lan':'LAD','mia':'MIA','mil':'MIL','min':'MIN','nyn':'NYM','nya':'NYY','oak':'OAK','phi':'PHI','pit':'PIT','sdn':'SD','sea':'SEA','sfn':'SF','sln':'STL','tba':'TB','tex':'TEX','tor':'TOR','was':'WAS'}
umps_dict = {'baker':'Baker','barber':'Barber','barksdale':'Barksdale','barry':'Barry','basner':'Basner','bellino':'Bellino','bill welke':'Bwelke','blakney':'Blakney','blaser':'Blaser','bucknor':'Bucknor','carapazza':'Carapazza','carlson':'Carlson','cederstrom':'Cederstrom','conroy':'Conroy','cooper':'Cooper','culbreth':'Culbreth','cuzzi':'Cuzzi','danley':'Danley','davidson':'Davidson','davis':'Davis','demuth':'Demuth','diaz':'Diaz','dimuro':'Dimuro','drake':'Drake','dreckman':'Dreckman','eddings':'Eddings','emmel':'Emmel','estabrook':'Estabrook','everitt':'Everitt','fagan':'Fagan','fairchild':'Fairchild','fletcher':'Fletcher','foster':'Foster','gonzalez':'Gonzalez','gorman':'Gorman','greg gibson':'Ggibson','guccione':'Guccione','hal gibson':'Hgibson','hallion':'Hallion','hamari':'Hamari','hernandez':'Hernandez','hickox':'Hickox','hirschbeck':'Hirschbeck','hoberg':'Hoberg','holbrook':'Holbrook','hoye':'Hoye','hudson':'Hudson','iassogna':'Iassogna','johnson':'Johnson','joyce':'Joyce','kellogg':'Kellogg','knight':'Knight','kulpa':'Kulpa','lance barrett':'Lbarrett','layne':'Layne','little':'Little','marquez':'Marquez','meals':'Meals','miller':'Miller','morales':'Morales','muchlinski':'Muchlinski','nauert':'Nauert','nelson':'Nelson',"o'nora":'Onora','pattillo':'Pattillo','porter':'Porter','rackley':'Rackley','randazzo':'Randazzo','reyburn':'Reyburn','reynolds':'Reynolds','ripperger':'Ripperger','schrieber':'Schrieber','scott':'Scott','segal':'Segal','ted barrett':'Tbarrett','tichenor':'Tichenor','tim welke':'Twelke','timmons':'Timmons','tripp gibson':'Hgibson','tumpane':'Tumpane','vanover':'Vanover','wegner':'Wegner','wendelstedt':'Wendelstedt','west':'West','winters':'Winters','wolcott':'Wolcott','wolf':'Wolf','woodring':'Woodring'}
year = '2016'

def get_date(date_input):
    date_input = str(date_input)
    if date_input == '':
        tdate = str(date.today())[-5:]
    elif len(date_input) < 3:
        tdate = str(date.today() - timedelta(days=int(date_input)))[-5:]
    else:
        tdate = date_input
    return tdate


    
def get_umps_on_date(game_date):
    print('------------------------------------------------')
    print(game_date)
    date_month, date_day = game_date[:2], game_date[-2:]
    
    created_at_stamp = datetime.now()
    gameday_url = ('http://gd2.mlb.com/components/game/mlb/year_2016/month_%s/day_%s/' % (date_month,date_day))
    
    soup_day = BeautifulSoup(requests.get(gameday_url).text)

    for day_link in soup_day.find_all('a'):
        if day_link['href'][:3] == 'gid':
            print(day_link['href'])
            # this link leads to a game that potentially has ump info
            game_url = gameday_url + day_link['href']
            
            soup_game = BeautifulSoup(requests.get(game_url).text)
            
            for game_link in soup_game.find_all('a'):
                if game_link['href'] == 'boxscore.xml':
                    print('retrieved umps')
                    # this link looks for the boxscore.xml table which houses the umpire info
                    
                    soup_boxscore = BeautifulSoup(requests.get(game_url+'boxscore.xml').text, 'html.parser')
                    
                    s = str(soup_boxscore.find_all('game_info'))                
                    
                    # hp = homeplate, fb = firstbase, sb = secondbase, tb = thirdbase#
                    
                    umps = re.search('HP: (.*?)\. 1B: (.*?)\. 2B: (.*?)\. 3B: (.*?)\.', s)
                    try:
                        hp_ump = umps.group(1)
                    except:
                        hp_ump = ''
                    try:
                        fb_ump = umps.group(2)
                    except:
                        fb_ump = ''
                    try:
                        sb_ump = umps.group(3)
                    except:
                        sb_ump = ''
                    try:
                        tb_ump = umps.group(4)
                    except:
                        tb_ump = ''
                    
                    # write date, home team, hp ump, 1b ump, 2b ump, 3b ump
                    f.write('%s|%s|%s|%s|%s|%s|%s\n' % (gameday_to_xlsx[day_link['href'][22:25]]+game_date, game_date, gameday_to_xlsx[day_link['href'][22:25]], hp_ump, fb_ump, sb_ump, tb_ump))
                    
                    final_flag = False
                    if datetime.strptime(str(date.today()), '%Y-%m-%d') > datetime.strptime(game_date + '-' + year, '%m-%d-%Y'):
                        final_flag = True

    
                    sql = '''
                    INSERT INTO umpires 
                    (game_id, final_flag, hp_ump, fb_ump, sb_ump, tb_ump, created_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    '''
                    c.execute(sql, (day_link['href'][4:-1].replace('mlb',''), final_flag, hp_ump, fb_ump, sb_ump, tb_ump, created_at_stamp))
                    conn.commit()
                    
                else:
                    'no umps'
            # print('----')
        else:
            pass


what_date_do_you_want = raw_input("Please enter an date (m-d) or # days in past:")

engine = create_engine('postgresql://postgres:password@localhost:5432/baseball')
connecter = engine.connect()
conn = connecter.connection
conn.autocommit = True
c = conn.cursor()

path = os.path.dirname(os.path.realpath(__file__))
f=open(path+'/getumps.txt', "w")

get_umps_on_date(get_date(what_date_do_you_want))
get_umps_on_date(str(datetime.strptime(year[-2:]+'-'+get_date(what_date_do_you_want),'%y-%m-%d') - timedelta(days = 1))[5:10])

f.close()
c.close()
conn.close()
