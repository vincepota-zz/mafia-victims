from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd


###################
# Vittimedimafia
###################

wpage = 'http://www.vittimemafia.it/index.php?option=com_content&view=category&id=35&Itemid=67'
page = urlopen(wpage)
soup = BeautifulSoup(page, 'html5lib')

the_rows = soup.find_all("tr", attrs={"class": ["sectiontableentry1", "sectiontableentry2"]})
dates = pd.Series([the_rows[i].find_all('td')[2].get_text() for i in range(0,len(the_rows))])
dates = dates.str.strip()
df = dates.str.split(expand=True)
df = df[0:-3]
df.columns = ['weekday_name','weekday','month','year']
df['year'] =  df['year'].astype(int)

df_vittime = df.groupby('year').size().cumsum()
df_vittime.name = 'vittimedimafia.it'

###################
#Peppino impastato
###################

import re
wpage = 'http://www.peppinoimpastato.com/nomicognomi.htm'
page = urlopen(wpage)
soup = BeautifulSoup(page, 'html5lib')

the_table = soup.find('h2')
raw_txt = the_table.get_text()
df = pd.DataFrame({'names' : re.split(r'\s{2,}', raw_txt)[1:-2]}) # split with more than 2 whitespace 

df['dates'] = df[df['names'].str.isnumeric()]  #separate dates from names
df['dates'] = df.dates.fillna(method = 'ffill')


df = df[~(df['names'] == df['dates'])] #remove dates from names
df['dates'] =  df['dates'].astype(int)

df_peppino = df.groupby('dates').size().cumsum()
df_peppino.name = 'peppinoimpastato.com'

###################
#Libera
###################

wpage = 'http://www.libera.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/87'
page = urlopen(wpage)
soup = BeautifulSoup(page, 'html5lib')

the_rows = soup.find_all("div", attrs={"class": ["viewPar BLOBAlignLeft", "viewPar BLOBAlignLeft"]})
names = [the_rows[i].find_all('p')[0].get_text() for i in [1,2]]

names = names[0] + names[1]

tmp  = re.split('(\d+)',names)
tmp = pd.Series(tmp).str.split('.')

ser = pd.Series()
for t in tmp:
	ser = ser.append(pd.Series(t))

ser = ser[~(ser == '')]  # remove empty rows
ser.index = range(0,len(ser))

df = pd.DataFrame(ser)
df.columns = ['names']

df['dates'] = df[df.names.str.isnumeric()]  #separate dates from names
df['dates'] = df.dates.fillna(method = 'ffill')
df = df[~(df['names'] == df['dates'])] #remove dates from names
df['dates'] =  df['dates'].astype(int)

df_libera = df.groupby('dates').size().cumsum()
df_libera.name = 'libera.it'

###################
#Plots
###################

pd.concat([df_vittime, df_peppino, df_libera],axis=1).plot(figsize = (6,4))
plt.xlabel('year')
plt.ylabel('cumulative death tool')
plt.title('Mafia death tool since 1861')
plt.grid()

pd.to_datetime(df.dates, format = '%Y').hist(bins=100)
plt.grid()
plt.xlabel('year')
plt.ylabel('victims')
plt.title('Discrete death tool from libera.it')


