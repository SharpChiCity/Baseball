from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
from datetime import timedelta
import os
import pandas

game_number = 1

abbr_nickname_league_dict = {
    # AL EAST
    'BAL' : {'Nickname' : 'Orioles',    'League' : 'AL'}
    , 'BOS' : {'Nickname' : 'Red Sox',  'League' : 'AL'}
    , 'NYY' : {'Nickname' : 'Yankees',  'League' : 'AL'}
    , 'TAM' : {'Nickname' : 'Rays',     'League' : 'AL'}
    , 'TOR' : {'Nickname' : 'Blue Jays','League' : 'AL'}
    # AL CENT
    , 'CLE' : {'Nickname' : 'Indians',  'League' : 'AL'}
    , 'DET' : {'Nickname' : 'Tigers',   'League' : 'AL'}
    , 'KAN' : {'Nickname' : 'Royals',   'League' : 'AL'}
    , 'MIN' : {'Nickname' : 'Twins',    'League' : 'AL'}
    , 'CHW' : {'Nickname' : 'White Sox','League' : 'AL'}
    , 'CWS' : {'Nickname' : 'White Sox','League' : 'AL'}
    # AL WEST
    , 'HOU' : {'Nickname' : 'Astros',   'League' : 'AL'}
    , 'LAA' : {'Nickname' : 'Angels',   'League' : 'AL'}
    , 'OAK' : {'Nickname' : 'Athletics','League' : 'AL'}
    , 'SEA' : {'Nickname' : 'Mariners', 'League' : 'AL'}
    , 'TEX' : {'Nickname' : 'Rangers', 'League' : 'AL'}
    # NL EAST
    , 'ATL' : {'Nickname' : 'Braves',   'League' : 'NL'}
    , 'MIA' : {'Nickname' : 'Marlins',  'League' : 'NL'}
    , 'PHI' : {'Nickname' : 'Phillies', 'League' : 'NL'}
    , 'NYM' : {'Nickname' : 'Mets',     'League' : 'NL'}
    , 'WAS' : {'Nickname' : 'Nationals','League' : 'NL'}
    # NL CENT
    , 'CIN' : {'Nickname' : 'Reds',     'League' : 'NL'}
    , 'MIL' : {'Nickname' : 'Brewers',  'League' : 'NL'}
    , 'STL' : {'Nickname' : 'Cardinals','League' : 'NL'}
    , 'PIT' : {'Nickname' : 'Pirates',  'League' : 'NL'}
    , 'CUB' : {'Nickname' : 'Cubs',     'League' : 'NL'}
    , 'CHC' : {'Nickname' : 'Cubs',     'League' : 'NL'}
    # NL WEST
    , 'COL' : {'Nickname' : 'Rockies',  'League' : 'NL'}
    , 'SFO' : {'Nickname' : 'Giants',   'League' : 'NL'}
    , 'SDG' : {'Nickname' : 'Padres',   'League' : 'NL'}
    , 'ARI' : {'Nickname' : 'Diamondbacks', 'League' : 'NL'}
    , 'LOS' : {'Nickname' : 'Dodgers',  'League' : 'NL'}
    , 'LAD' : {'Nickname' : 'Dodgers',  'League' : 'NL'}
}    

opp_name_abbr_dict = {
'Atlanta':'ATL'
, 'Baltimore':'BAL'
, 'Boston':'BOS'
, 'Cincinnati':'CIN'
, 'Cleveland':'CLE'
, 'Colorado':'COL'
, 'Cubs':'CUB'
, 'White Sox':'CWS'
, 'Detroit':'DET'
, 'Houston':'HOU'
, 'Kansas City':'KAN'
, 'LA Angels':'LAA'
, 'LA Dodgers':'LOS'
, 'Miami':'MIA'
, 'Milwaukee':'MIL'
, 'Minnesota':'MIN'
, 'NY Mets':'NYM'
, 'NY Yankees':'NYY'
, 'Oakland':'OAK'
, 'Philadelphia':'PHI'
, 'Pittsburgh':'PIT'
, 'San Diego':'SDG'
, 'Seattle':'SEA'
, 'San Francisco':'SFO'
, 'St. Louis':'STL'
, 'Tampa Bay':'TAM'
, 'Texas':'TEX'
, 'Toronto':'TOR'
, 'Washington':'WAS'
, 'Arizona':'ARI'
, 'White Sox':'CHW'
, 'Cubs':'CHC'
, 'Dodgers':'LAD'
}



def get_teams():
    # fetch table of teams & scheduels from ESPN
    soup = BeautifulSoup(requests.get('http://espn.go.com/mlb/teams').text, 'html.parser')
    tbl = soup.find('div',{'class':'mod-container mod-table mod-no-header'})

    return tbl
    
def get_schedule(abbr, list_of_game_info):
    # build list of all game information
    global game_number
    
    n = 1
    for i in range(1,3):
        url = 'http://espn.go.com/mlb/team/schedule/_/name/%s/half/%s' % (abbr, i)
        listing_of_games = BeautifulSoup(requests.get(url).text, 'html.parser').find('table').find_all('tr')
        for row in listing_of_games:
            if row['class'][0] != 'colhead' and row['class'][0] != 'stathead':
                # will only return data for actual games and not title columns
                game_data = row.find_all('td')
                date = game_data[0].get_text()
                excel_date = time.strftime('%m/%d/%Y', time.strptime(date+',2016','%a, %b %d,%Y'))
                opp_dirty = game_data[1].get_text()
                if opp_dirty[0] == '@':
                    opp = opp_dirty[1:]
                else:
                    opp = opp_dirty[2:]
                opp_clean = opp_name_abbr_dict[opp]
                home_away_indicator = game_data[1].get_text()[0]
                if home_away_indicator == 'v':
                    home = abbr
                    away = opp_clean
                else:
                    away = abbr
                    home = opp_clean
                game_time = game_data[2].get_text()
                
                if game_time != 'TBA':
                    excel_time_template = time.mktime(time.strptime(game_time + ' - 1/1/2016', '%I:%M %p - %m/%d/%Y'))
                    excel_time_dirty = datetime.fromtimestamp(excel_time_template) + timedelta(hours = -1)
                    excel_time_clean = excel_time_dirty.strftime('%I:%M %p')
                else:
                    excel_time_clean = game_time
                
                # print('%s -- %s -- %s' % (abbr, str(n), str(game_number))
                
                list_of_game_info.append({
                            'year' : '2017'
                            , 'month' : excel_date[:2]
                            , 'day_of_month' : excel_date[3:5]
                            , 'full_date' : excel_date
                            , 'time_of_game' : excel_time_clean
                            , 'home_team_name' : abbr_nickname_league_dict[home]['Nickname']
                            , 'home_team_league' : abbr_nickname_league_dict[home]['League']
                            , 'away_team_name' : abbr_nickname_league_dict[away]['Nickname']
                            , 'away_team_league' : abbr_nickname_league_dict[away]['League']
                            })
       
                game_number += 1
                n += 1

    return list_of_game_info    

                
def navigate_to_schedule(links):
    # from soup, open link to each team's schedule
    # return list of all game information
    all_teams = links.find_all('li')
    l = []
    
    for team in all_teams:
        team_name = team.find('h5').get_text()
        team_abbr = team.find_all('a')[4]['href'][-3:].upper()
        print(team_abbr)
        l = get_schedule(team_abbr, l)

    return l
        
 
 
if __name__ == '__main__':
    # game_number = 1
    paste_path = os.path.dirname(os.path.realpath(__file__))
    schedule_soup = get_teams()
    d = navigate_to_schedule(schedule_soup)

    df = pandas.DataFrame(data=d) 
    df_clean = df.drop_duplicates().sort(columns=['full_date','time_of_game','home_team_name']).reset_index()
    df_clean.index += 1
    df_clean.to_csv(paste_path + '\ESPNschedules.txt'
        , columns = ['year', 'month', 'day_of_month', 'full_date', 'time_of_game', 
                    'away_team_name', 'away_team_league', 'home_team_name','home_team_league']
        , index_label='Key'
        , header=True
        , index=True
        , mode='w')