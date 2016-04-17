#! /usr/bin/python
from datetime import date, time, timedelta, datetime
import os
from bs4 import BeautifulSoup
import requests
import time
from sqlalchemy import create_engine
import re
import psycopg2

# Main goal: Pull starting pitchers from bbpress. load dictionary of all starting pitchers. 
# get SP data from fangraphs


def get_date(date_input):
    # create a normalized date input 
    date_input = str(date_input)
    if date_input == '':
        tdate = str(date.today())[-5:]
    elif len(date_input) < 3:
        tdate = str(date.today() - timedelta(days=int(date_input)))[-5:]
    else:
        tdate = date_input
    return tdate


def build_SP_dict():
    # compile MLB & MiLB pitchers into a single file 
    # (only needs to be done when new FG files are downloaded)
    os.system(os.path.dirname(os.path.realpath(__file__))+'/merge_fangraphs_pitchers.py')

    # create dictionary of all pitchers for lookup later in file
    dict = {}
    with open(os.path.dirname(os.path.realpath(__file__)) + '/FGSPs.csv') as f:
        for line in f:
            lst = line.split('|')
            dict[lst[0]] = lst[1].replace('\n','')
    return dict


def add_key_to_dict(dict, SP_name, SP_id):
    # this is called if a pitcher id isn't already in FGSPs.csv
    dict[SP_name] = SP_id
    with open(os.path.dirname(os.path.realpath(__file__)) + '/FGSPs.csv', 'a') as f:
        f.write('%s|%s\n' %(SP_name, SP_id))
    with open(os.path.dirname(os.path.realpath(__file__)) + '/Fangraphs_MLB_pitchers.csv', 'a') as f:
        f.write('%s,,,,,,,,,,,,,,,,,,,%s\n' %(SP_name, SP_id))
    return dict


if __name__ == '__main__':
    ################################
    tdate = get_date(raw_input("Please enter an date (m-d) or # days in past:"))

    date_month, date_day = tdate[:2], tdate[-2:]
    
    gameday_url = ('http://gd2.mlb.com/components/game/mlb/year_2016/month_%s/day_%s/' % (date_month,date_day))
    all_game_ids = []
    soup_day = BeautifulSoup(requests.get(gameday_url).text, 'html.parser')

    for day_link in soup_day.find_all('a'):
        if day_link['href'][:3] == 'gid':
            all_game_ids.append(day_link['href'])
    
    spdict = build_SP_dict()

    conn = psycopg2.connect("host='localhost' dbname='baseball' user='postgres' password='password'")
    conn.autocommit = True
    c = conn.cursor()

    print(tdate)

    created_at_stamp = datetime.now()
    raw_data = requests.get('http://www.baseballpress.com/lineups/2016-'+tdate)
    soup = BeautifulSoup(raw_data.text, 'html.parser')

    Starting_Pitcher_Names = []
    team_datas = soup.find_all('div', 'team-data') # Team Names and SP
    for t in team_datas:
        pitcher_name = t.find_all('div')[3].get_text().replace(' (R)','').replace(' (L)','')
        BPteam_name = t.find_all('div')[2].get_text()
        Starting_Pitcher_Names.append((pitcher_name, BPteam_name))

    for num,tuple in enumerate(Starting_Pitcher_Names):
        if tuple[0] == 'TBD' or tuple[0] == 'TBD ()':
            resp = raw_input('Do you know who is starting for the ' + tuple[1] + '?: ')
            if resp == 'yes' or  resp == 'y':
                Starting_Pitcher_Names[num] = (raw_input('Who is the starting pitcher for the ' + tuple[1] + '?: '),tuple[1])


    ## Prompt user for player's Fangraphs ID to enter into db
    [add_key_to_dict(spdict, id, raw_input(("What is %s's fangraphs ID? (There is no current record for this pitcher) He pitches for the %s:" % (id, team)))) for id,team in Starting_Pitcher_Names if id not in spdict]
        
        
    Starting_Pitcher_IDs = [(spdict[id], team) for id,team in Starting_Pitcher_Names]



    ################################
    tester = 1
    path = os.path.dirname(os.path.realpath(__file__))
    f=open(path+'\\fgsp.txt', "w")

    fg_to_gameday = {'Angels':'ana','Astros':'hou','Athletics':'oak','Blue Jays':'tor','Braves':'atl','Brewers':'mil','Cardinals':'sln','Cubs':'chn','Diamondbacks':'ari','Dodgers':'lan','Giants':'sfn','Indians':'cle','Mariners':'sea','Marlins':'mia','Mets':'nyn','Nationals':'was','Orioles':'bal','Padres':'sdn','Phillies':'phi','Pirates':'pit','Rangers':'tex','Rays':'tba','Red Sox':'bos','Reds':'cin','Rockies':'col','Royals':'kca','Tigers':'det','Twins':'min','White Sox':'cha','Yankees':'nya'}

    for spnum, dat in enumerate(Starting_Pitcher_IDs):
        if tester == 1:
            tester = 0
        else:
            tester = 1
        try:
            # need to put zips and steamer projections at top to reset field value
            ZiPSFIP = ''
            SteamerFIP = ""
            
            spid = Starting_Pitcher_IDs[spnum]
            raw_data = requests.get('http://www.fangraphs.com/statss.aspx?playerid='+dat[0])
            soup = BeautifulSoup(raw_data.text, 'html.parser')
            try:
                throws = soup.find_all('strong')[2].next_sibling.strip()[-1:]
                spname = soup.find_all('strong')[0].get_text()
            except:
                throws = '?'
                spname = '?'
            print('{}/{} -- {}'.format(str(spnum+1).zfill(2),str(len(Starting_Pitcher_IDs)),spname))

            
            battedchartid = 'SeasonStats1_dgSeason3_ctl00'
            basicchartid = 'SeasonStats1_dgSeason11_ctl00'
            standardchartid = 'SeasonStats1_dgSeason1_ctl00'
            
            BasicChart = soup.find_all('table', id=basicchartid)[0].find_all('tr')
            BattedChart = soup.find_all('table', id=battedchartid)[0].find_all('tr')
            StandardChart = soup.find_all('table', id=standardchartid)[0].find_all('tr')
            
            ### locates trnum in chart
            basic_trnum = 0
            ZiPS_rem = 0
            Steamer_rem = 0
            num_teams = 1
            try:
                for i in range(0,len(BasicChart)):
                    #print str(i)+','+str(basic_trnum)
                    # print str(i), '- 1)', BasicChart[i].get_text()[1:5], '2) ', BasicChart[i+1].get_text()[1:16], '3) ', BasicChart[i].get_text()[1:16]
                    if basic_trnum == 0 or ZiPS_rem == 0 or Steamer_rem == 0:
                        try:
                            if (BasicChart[i].get('class')[0] == 'rgAltRow' or BasicChart[i].get('class')[0] == 'rgRow') and BasicChart[i].find('a').get_text() == '2016':
                                basic_trnum = i
                                # print '2teams'                    
                        except:
                            pass
                        if (BasicChart[i].get_text()[1:5] == '2016' and BasicChart[i+1].get_text()[1:13] == '2016ZiPS (R)'):
                            basic_trnum = i
                            # print 'b1'
                        if (BasicChart[i].get_text()[1:5] == '2016' and BasicChart[i].get_text()[1:13] == '2016ZiPS (R)'):
                            ZiPS_rem = i
                            # print 'z'
                        if (BasicChart[i].get_text()[1:5] == '2016' and BasicChart[i].get_text()[1:9] == '2016ZiPS'):
                            ZiPS_rem = i
                            # print 'z'
                        if (BasicChart[i].get_text()[1:5] == '2016' and BasicChart[i].get_text()[1:16] == '2016Steamer (R)'):
                            Steamer_rem = i
                            # print 's'
                        if (BasicChart[i].get_text()[1:5] == '2016' and BasicChart[i].get_text()[1:12] == '2016Steamer'):
                            Steamer_rem = i
                            # print 's'
                        if (BasicChart[i].get_text()[1:5] == '2016' and BasicChart[i+1].get_text()[1:16] == '2016Steamer (R)' and basic_trnum == 0):
                            basic_trnum = i
                            # print 'b2'
                        if (BasicChart[i].get_text()[1:5] == '2016' and BasicChart[i].get_text()[8:14] == " Teams"):################
                            if len(BasicChart[i]['class']) == 1:
                                basic_trnum = i
                                # print 'b3'
                                num_teams = BasicChart[i].get_text()[7]
                            elif BasicChart[i].parent.tr['class'][1] != 'grid_minors_show':
                                basic_trnum = i
                                # print 'b4'
                                num_teams = BasicChart[i].get_text()[7]
            except:
                pass
                
            # print basic_trnum
            # print Steamer_rem
            # print ZiPS_rem
            
                ######

            standard_trnum = 0
            num_teams = 1
            for i in range(0,len(StandardChart)):
                #print str(i)+','+str(standard_trnum)
                if standard_trnum == 0:
                    try:
                        if (StandardChart[i].get('class')[0] == 'rgAltRow' or StandardChart[i].get('class')[0] == 'rgRow') and BasicChart[i].find('a').get_text() == '2016':
                            standard_trnum = i
                            # print '2teams'                    
                    except:
                        pass
                    # if (StandardChart[i].get_text()[:5] == '\n2016' and StandardChart[i].get_text()[:12] == '\n20162 Teams'):
                        # standard_trnum = i
                    # if (StandardChart[i].get_text()[:5] == '\n2016' and StandardChart[i+1].get_text()[:13] == '\n2016ZiPS (R)'):
                        # standard_trnum = i
                    # if (StandardChart[i].get_text()[:5] == '\n2016' and StandardChart[i+1].get_text()[:16] == '\n2016Steamer (R)'):
                        # standard_trnum = i
                    # if (StandardChart[i].get_text()[:5] == '\n2016' \
                    # and StandardChart[i].get_text()[8:14] == " Teams"):################
                        # if len(StandardChart[i]['class']) == 1:
                            # standard_trnum = i
                            # num_teams = StandardChart[i].get_text()[7]
                        # elif StandardChart[i].parent.tr['class'][1] != 'grid_minors_show':
                            # standard_trnum = i
                            # num_teams = StandardChart[i].get_text()[7]
                
                ######
                
                ### locates trnum in chart
            batted_trnum = 0
            for i in range(0,len(BattedChart)):
                if batted_trnum == 0:
                    if BattedChart[i].get_text()[:5] == '\n2016':
                        batted_trnum = i
                ######
                

            ### locates variables in BasicChart headers
            basicheaders = BasicChart[0].find_all('th')
            for j in range(0,len(basicheaders)):
                if basicheaders[j].get_text() == 'Team':
                    Teamcol = j
                if basicheaders[j].get_text() == 'IP':
                    IPcol = j
                if basicheaders[j].get_text() == 'ERA':
                    ERAcol = j
                if basicheaders[j].get_text() == 'FIP':
                    FIPcol = j
                if basicheaders[j].get_text() == 'xFIP':
                    xFIPcol = j
                if basicheaders[j].get_text() == 'BABIP':
                    BABIPcol = j
                if basicheaders[j].get_text() == 'HR/FB':
                    HRFBcol = j
                ######

            ### locates variables in BasicChart headers
            standardheaders = StandardChart[0].find_all('th')
            for j in range(0,len(standardheaders)):
                if standardheaders[j].get_text() == 'SO':
                    SOcol = j
                if standardheaders[j].get_text() == 'BB':
                    BBcol = j
                if standardheaders[j].get_text() == 'HBP':
                    HBPcol = j
                if standardheaders[j].get_text() == 'IBB':
                    IBBcol = j
                if standardheaders[j].get_text() == 'TBF':
                    TBFcol = j
                ######


            ZiPSFIP = ''
            SteamerFIP = ''
                
            BasicData = BasicChart[basic_trnum].find_all('td')
            if ZiPS_rem > 0:
                ZiPSData = BasicChart[ZiPS_rem].find_all('td')
                ZiPSFIP = ZiPSData[FIPcol].get_text()
            if Steamer_rem > 0:
                SteamerData = BasicChart[Steamer_rem].find_all('td')
                SteamerFIP = SteamerData[FIPcol].get_text()
            StandardData = StandardChart[standard_trnum].find_all('td')
            
            if num_teams != 1:
                team=BasicChart[Teamcol+int(num_teams)].find_all('td')[Teamcol].get_text()
            else:
                team=BasicData[Teamcol].get_text()

            ip_base=BasicData[IPcol].get_text().replace(u'\xa0','0')
            ip = round(float(ip_base.replace('.1','.333333333333').replace('.2','.6666666666')),2)
            era=BasicData[ERAcol].get_text().replace(u'\xa0','0')
            fip=BasicData[FIPcol].get_text().replace(u'\xa0','0')
            xfip=BasicData[xFIPcol].get_text().replace(u'\xa0','0')
            babip=BasicData[BABIPcol].get_text().replace(u'\xa0','0')
            hrfb=BasicData[HRFBcol]	.get_text().replace(u'\xa0','0')
            so=int(StandardData[SOcol].get_text().replace(u'\xa0','0'))
            bb=int(StandardData[BBcol].get_text().replace(u'\xa0','0'))
            ibb=int(StandardData[IBBcol].get_text().replace(u'\xa0','0'))
            hbp=int(StandardData[HBPcol].get_text().replace(u'\xa0','0'))
            try:
                tbf=int(StandardData[TBFcol].get_text())
            except ValueError:
                print(spid[0])
                tbf = int(raw_input('Please enter TBF in 2016:'))
            kwERA = round(5.4 - 12*(so-(bb+hbp-ibb))/float((tbf-ibb)), 3)
            
            ### locates variables in BattedChart headers
            battedheaders = BattedChart[0].find_all('th')
            for j in range(0,len(battedheaders)):
                if battedheaders[j].get_text() == 'SIERA':
                    SIERAcol = j
            ######

            BattedData = BattedChart[batted_trnum].find_all('td')
            siera=BattedData[SIERAcol].get_text()
            
        
            mlb_id = fg_to_gameday[dat[1]]
            for id in all_game_ids:
                if mlb_id in id:
                    game_id = id[4:-1].replace('mlb','')
            
            final_flag = False
            if datetime.strptime(str(date.today()), '%Y-%m-%d') > datetime.strptime(tdate + '-2016', '%m-%d-%Y'):
                final_flag = True
            
            f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (spname,spid[0],dat[1],ip,throws,era,ZiPSFIP,SteamerFIP,kwERA,siera,xfip))
            
            sql = '''
            INSERT INTO starting_pitchers 
            (game_id, final_flag, name, fg_id, team, ip, throws, era, fip_z, fip_s, kwera, siera, xfip, created_at)
            VALUES (%s,       %s,   %s,    %s,   %s, %s,     %s,  %s,    %s,    %s,    %s,    %s,   %s, %s)
            ON CONFLICT DO NOTHING
            '''
            ZiPSFIP = None if ZiPSFIP == '' else ZiPSFIP
            SteamerFIP = None if SteamerFIP == '' else SteamerFIP
            c.execute(sql, (game_id, final_flag,spname,str(spid[0]),mlb_id,ip,throws,era,ZiPSFIP, \
                            SteamerFIP,kwERA,siera,xfip,created_at_stamp))
           
            
        except IndexError:
            f.write('%s,%s,%s,0,%s,0,%s,%s,0,0,\n' %(spname,spid[0],dat[1], throws, ZiPSFIP, SteamerFIP))
        
        if tester == 1:
            f.write('\n')

    f.close
    c.close()
    conn.close()
	