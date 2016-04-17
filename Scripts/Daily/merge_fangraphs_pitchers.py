import pandas as pd
import os

path = os.path.dirname(os.path.realpath(__file__))

mlb_p = pd.read_csv(path + '/Fangraphs_MLB_pitchers.csv')
milb_p = pd.read_csv(path + '/Fangraphs_MiLB_pitchers.csv')

all_pitchers = pd.concat([mlb_p[[0,-1]],milb_p[[0,-1]]])
all_pitchers.columns = ['playername','playerid']

all_pitchers.to_csv(path + '/FGSPs.csv', index=False, sep='|')
print 'major and minor league pitchers merged!'