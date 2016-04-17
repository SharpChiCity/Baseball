#! /usr/bin/python
from __future__ import division
from bs4 import BeautifulSoup
import requests, re, sys, os, codecs

date_input = raw_input("Please enter an date (mm-dd):")

path = "C:\\Users\\spesh\\Python"
f=open(path+'\\fgdaily.txt', "w")

date = '2013-'+str(date_input)
raw_data = requests.get('http://www.fangraphs.com/livescoreboard.aspx?date='+date)
soup = BeautifulSoup(raw_data.text)

chart = soup.find_all('div', id='LiveBoard1_LiveBoard1_litGamesPanel')[0].find_all('table')[0]
lineups = chart.find_all('tr')

w = 0
x = 0
y = 0
z = 0
for i in range(0,len(lineups)):
	x = len(lineups[i].find_all('table'))
	if	x > w:
		z = y
		w = x
	y += 1


x = lineups[z].find_all('td')

counter = 0
A = []
H = []
linkA = []
linkH = []

for i in range(0,len(x)):
	if x[i].get_text().strip()[:9] == "Box Score":
		pass
	else:
		if x[i].get_text().strip() == "":
			if counter == 3:
				for a in range(0,9):
					A.append('')
					linkA.append('')
			if counter == 4:
				for a in range(0,9):
					H.append('')
					linkH.append('')
			if counter < 3: 
				A.append('')
				linkA.append('')
				H.append('')
				linkH.append('')
			counter += 1
		else:
			y = x[i].find_all('a')
			if counter >= 5:
					counter = 0
			if counter == 0:
					num = 1
			else:
					num = len(y)
			for j in range(0,num):
					print(str(i) + ',' + str(j) + ',' + str(counter) + ',' + str(len(y)))
					print(y[j].get_text())
					if counter == 0:
							A.append(y[j].get_text().strip())
							H.append(y[j+1].get_text().strip())
							linkA.append('')
							linkH.append('')
					if counter == 1:
							A.append(y[0].get_text().strip())
							linkA.append('http://www.fangraphs.com/'+y[0].get('href'))
					if counter == 2:
							H.append(y[0].get_text().strip())
							linkH.append('http://www.fangraphs.com/'+y[0].get('href'))
	#### Need to account for when only one team posts lineups!
					if counter == 3:
							A.append(y[j].get_text().strip())
							linkA.append('http://www.fangraphs.com/'+y[j].get('href'))
					if counter == 4:
							H.append(y[j].get_text().strip())
							linkH.append('http://www.fangraphs.com/'+y[j].get('href'))
	########
				
			counter += 1
			
lenA = len(A)
lenH = len(H)
f.write('\n')
for z in range(0,min(lenA,lenH)):
	# if int(z/11) == z/11:
		# f.write('\n')
	f.write(A[z]+"|"+linkA[z]+'|'+H[z]+'|'+linkH[z]+'\n')
        

f.close
