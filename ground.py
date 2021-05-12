from orbit_predictor.sources import NoradTLESource
from orbit_predictor.locations import Location
from orbit_predictor.sources import get_predictor_from_tle_lines
from plotly.graph_objs import Figure, FigureWidget
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import urllib
import urllib3
import http.cookiejar
import datetime
from flask import Flask, jsonify, request
from collections import namedtuple
from flask_caching import Cache
import sys


config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 3600
}

g_credentials =""
g_settings = ""

app = Flask(__name__)

# tell Flask to use the above defined config
app.config.from_mapping(config)
cache = Cache(app)

plt.ion()

class CacheablePredictor():
    def __init__(self,predictor):
        self.predictor = predictor
    
    def __repr__(self):
        return f"Predictor_for_{self.predictor.sate_id}_{self.predictor.tle.lines}"


def load_file(filename):
    # Loading settings
    with open(filename, encoding="UTF-8") as sf:
        json_data = json.load(sf, encoding="utf8")
    
    return json_data

def initialiaze_app(cred_file, setting_file):
    json_config = load_file(cred_file)
    json_setting = load_file(setting_file)

    tle_api = json_config["tle_api"]
    base_url = tle_api["baseUrl"]
    username = tle_api["user"]
    password = tle_api["password"]
    credentials = [base_url,username,password]
    print(f"CONFIGURATION files parsed.", file=sys.stderr)
    return credentials, json_setting

@cache.memoize(timeout=3600)
def get_tle(id,credentials):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    parameters = urllib.parse.urlencode({'identity': credentials[1], 'password': credentials[2]}).encode("utf-8")
    
    opener.open(credentials[0] + '/ajaxauth/login', parameters)
    satid = str(id)
    
    query_string = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/ORDINAL/1/NORAD_CAT_ID/{satid}/orderby/TLE_LINE1%20ASC/format/tle"
    print(f"DOWNLOADING TLE from {query_string}", file=sys.stderr)
    resp = opener.open(query_string)
    TLE = resp.read()
    tle_utf = str(TLE, "utf-8")
    opener.close()   
    return tle_utf.splitlines()


def predict_gt(predictor,start_time, time_resolution, n_points ):
    #!! if the start time is moved inside the function, then the function can be memoized but side effect would be that the predictions would always start at the cached time
    dates = pd.date_range(start=start_time, periods=n_points,
                          freq=time_resolution)

    latlon = pd.DataFrame(index=dates, columns=['lat', 'lon','height'])

    for date in dates:
        lat, lon, height = predictor.get_position(date).position_llh
        latlon.loc[date] = (lat, lon, height)
    print(f"PREDICTED Ground Track (GT) for SATID={id} @:{start_time}", file=sys.stderr)
    return latlon

@cache.memoize(timeout=600)
def predict_gt_cacheable(predictor_c,time_resolution, n_points ):
    #cacheable version of predict_gt
    start_time = datetime.datetime.utcnow()
    print(f"CACHING GT results for start time: {start_time} and n-points: {n_points} and res: {time_resolution}", file=sys.stderr)
    return predict_gt(predictor_c.predictor,start_time,time_resolution, n_points)
    

@app.route("/get/<id>")
def calc_ground_track(id):
    start_t = datetime.datetime.now()
    tle_lines = get_tle(id,g_credentials)
    print(f"PROCESSING TLE: {tle_lines}", file=sys.stderr )

    predictor = get_predictor_from_tle_lines(tle_lines)

    start_time = datetime.datetime.utcnow()
    n_points = int(request.args.get("n-points") or g_settings["n-points"])
    time_resolution = str(request.args.get("time-resolution") or g_settings["time-resolution"]) + "S"
    
    latlon = ""
    if request.args.get("cache") is not None :
        #cached version
        predictor_c = CacheablePredictor(predictor)
        latlon = predict_gt_cacheable(predictor_c,time_resolution, n_points)
    else:
        latlon = predict_gt(predictor,start_time,time_resolution, n_points)
   
    # DEAD CODE for cartopy
    '''
    fig = FigureWidget()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()

    plt.plot(latlon["lon"], latlon["lat"], 'k',
            transform=ccrs.Geodetic())

    plt.show(fig)
    print("latitude:",lat,"longitude:",lon)
    '''
    
    end_t = datetime.datetime.now()
    duration_req = (end_t - start_t).seconds
    print(f"SERVING THE REQUEST for {n_points} points and resolution of {time_resolution} took || {duration_req} seconds ||", file=sys.stderr)
    return jsonify(latlon.to_dict(orient='split'))


if __name__ == "__main__":
    cred_file = "secret.json"
    setting_file = "settings.json"
    g_credentials, g_settings= initialiaze_app(cred_file, setting_file)
    app.run(host='0.0.0.0', port=5000, debug=True)
