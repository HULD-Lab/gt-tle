from plotly.graph_objs import Figure, FigureWidget
import numpy as np
import matplotlib.pyplot as plt
plt.ion()
import cartopy.crs as ccrs
import pandas as pd
import urllib, urllib3, http.cookiejar
import datetime

from orbit_predictor.sources import NoradTLESource
from orbit_predictor.locations import Location

fecha = '2014/04/01'


baseURL = 'https://www.space-track.org'
username = 'huldspace123@gmail.com'
password = 'Huld12345678910'

d = datetime.datetime.strptime(fecha, "%Y/%m/%d")
d1 = d + datetime.timedelta(days=1)
dstr = d.strftime("%Y-%m-%d")
d1str = d1.strftime("%Y-%m-%d")

#print("Connecting...")
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
parameters = urllib.parse.urlencode({'identity': username ,'password': password}).encode("utf-8")
#opener.urllib.request.urlopen(baseURL + '/ajaxauth/login', parameters)
opener.open(baseURL + '/ajaxauth/login', parameters)
print("input satellite ID:")
satid = str(input())
#satid = '25544'
queryString = "https://www.space-track.org/basicspacedata/query/class/tle_latest/ORDINAL/1/NORAD_CAT_ID/"+satid+"/orderby/TLE_LINE1%20ASC/format/tle"
#queryString = baseURL +"/basicspacedata/query/class/tle/format/tle/NORAD_CAT_ID/"+satid+"/EPOCH/"+dstr+"%2000:00:00--"+d1str+"%2000:00:00"
resp = opener.open(queryString)
#print(str(queryString))
#print(str(resp))


TLE = resp.read()
TLE_utf = str(TLE, "utf-8")
print("---------------------------------TLE---------------------------------\n")
#print(TLE)

opener.close()

TLE_file = "SAT̈́\n" +TLE_utf
print(TLE_file)


#print("input satellite name:")
#source = NoradTLESource.from_file("/home/niels/python_test/resources.txt")
#source = NoradTLESource.from_url("https://www.space-track.org/basicspacedata/query/class/tle_latest/ORDINAL/1/NORAD_CAT_ID/44406/orderby/TLE_LINE1%20ASC/format/tle")
#print()

#print(str(source))

f = open("sat.txt", "w")

print(TLE_file, file=f)
f.close()
source = NoradTLESource.from_file("/home/niels/python_test/sat.txt")
predictor = source.get_predictor("SAT") #TIROS N for example

print("Input time: (ex. 2020-01-28 23:00)")
start_time = input()
#start_time="2020-01-28 23:00"
dates = pd.date_range(start=start_time, periods=5, freq="1S")

latlon = pd.DataFrame(index=dates, columns=["lat", "lon"])

for date in dates:
    lat, lon, _ = predictor.get_position(date).position_llh
    latlon.loc[date] = (lat, lon)

fig = FigureWidget()
ax = plt.axes(projection=ccrs.PlateCarree())
ax.stock_img()

plt.plot(latlon["lon"], latlon["lat"], 'k',
         transform=ccrs.Geodetic())

plt.show(fig)
print("latitude:",lat,"longitude:",lon)
