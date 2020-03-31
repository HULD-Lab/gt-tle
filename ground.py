from orbit_predictor.sources import NoradTLESource
from orbit_predictor.locations import Location
from plotly.graph_objs import Figure, FigureWidget
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import urllib
import urllib3
import http.cookiejar
import datetime
from flask import Flask, jsonify
plt.ion()
#import cartopy.crs as ccrs

fecha = '2014/04/01'
app = Flask(__name__)
#Loading credentials
with open("secret.json", encoding="UTF-8") as f:
    jsonConfig = json.load(f, encoding="utf8")

#Loading settings
with open("settings.json", encoding="UTF-8") as sf:
    jsonSetting = json.load(sf, encoding="utf8")

@app.route("/get/<id>")
def doEverything(id):
#!Refactoring needed
    tle_api = jsonConfig["tle_api"]
    baseURL = tle_api["baseUrl"]
    username = tle_api["user"]
    password = tle_api["password"]

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
    
    satid = str(id)
    #satid = '25544'
    queryString = "https://www.space-track.org/basicspacedata/query/class/tle_latest/ORDINAL/1/NORAD_CAT_ID/"+satid+"/orderby/TLE_LINE1%20ASC/format/tle"
    #queryString = baseURL +"/basicspacedata/query/class/tle/format/tle/NORAD_CAT_ID/"+satid+"/EPOCH/"+dstr+"%2000:00:00--"+d1str+"%2000:00:00"
    resp = opener.open(queryString)
    #print(str(queryString))
    #print(str(resp))


    TLE = resp.read()
    TLE_utf = str(TLE, "utf-8")
    TLE_handled = "\n".join(TLE_utf.splitlines())
    print("---------------------------------TLE---------------------------------\n")
    #print(TLE)

    opener.close()

    TLE_file = "SAT\n" +TLE_handled
    print(TLE_file)


    #print("input satellite name:")
    #source = NoradTLESource.from_file("/home/niels/python_test/resources.txt")
    #source = NoradTLESource.from_url("https://www.space-track.org/basicspacedata/query/class/tle_latest/ORDINAL/1/NORAD_CAT_ID/44406/orderby/TLE_LINE1%20ASC/format/tle")
    #print()

    #print(str(source))

    f = open("sat.txt", "w")
    print(TLE_file, file=f)
    f.close()
    source = NoradTLESource.from_file("sat.txt")
    predictor = source.get_predictor("SAT") #TIROS N for example

    print("Input time: (ex. 2020-01-28 23:00)")
    start_time = datetime.datetime.utcnow()
    #start_time="2020-01-28 23:00"
    dates = pd.date_range(start=start_time, periods=jsonSetting["n-points"],
                          freq=str(jsonSetting["time-resolution"])+"S")

    latlon = pd.DataFrame(index=dates, columns=['lat', 'lon'])

    for date in dates:
        lat, lon, _ = predictor.get_position(date).position_llh
        latlon.loc[date] = (lat, lon)
    #DEAD CODE for cartopy
    '''
    fig = FigureWidget()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()

    plt.plot(latlon["lon"], latlon["lat"], 'k',
            transform=ccrs.Geodetic())

    plt.show(fig)
    print("latitude:",lat,"longitude:",lon)
    '''

    return jsonify(latlon.to_dict(orient='split'))


if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True)
    