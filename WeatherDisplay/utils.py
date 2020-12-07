import sys
import wifindme
import requests
import logging
from constants import LANG
from geopy.geocoders import Nominatim

#TODO save to file to reduce calls
#TODO logs instead of print

API_KEY = "73c571c7906c8b931987c39002c55da0"

logger = logging.getLogger('weather_display')


def get_location():
    try:
        accuracy, (lat,lon) = wifindme.locate(device="wlan0", service='m')
        if not lat or not lon:
            raise Exception("Invalid value from Mozilla")
    except:
        #Fallback1, IP-based location
        res = requests.get("http://ipinfo.io")
        assert res.status_code == 200
        lat, lon = res.text.strip().split(',')
    finally:
        if not lon or not lat:
            #Fallback2, hardcoded value
            lat, lon = (46.0442, -73.4545)
    return lat, lon

def get_city(lat,lon):
    locator = Nominatim(user_agent="myGeocoder")
    lat, lon = get_location()
    loc = locator.reverse((lat, lon), exactly_one = True, language="fr")
    return loc.raw['address']['city']

def get_weather_onecall():
    lat, lon = get_location()
    try:
        city = get_city(lat, lon)
    except:
        print()
        city = ", ".join((lat,lon))

    exclude_set = ["alerts","minutely"]
    query_list = [
        f"https://api.openweathermap.org/data/2.5/onecall?",
        f"lat={lat}&lon={lon}&",
        f"exclude={','.join(exclude_set)}&" if exclude_set else "",
        f"lang={LANG}&",
        f"units=metric&",
        f"appid={API_KEY}&",
    ]

    query = "".join(query_list)
    
    res = requests.get(query)
    if not 200 <= res.status_code <= 299:
        raise Exception
    
    output = {}
    output["city"] = city
    output["one_call"] = res.json()
    return output

if __name__=="__main__":
    data = get_weather_onecall()
    print(f"One call: {data['one_call'].__dict__}")








