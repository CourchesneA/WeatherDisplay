#!/usr/bin/python3
import pickle

from utils import get_weather_onecall
from constants import DATA_FILE


def write_data():
    data = get_weather_onecall()
    pickle.dump(data, open(DATA_FILE, "wb+" ))

def read_data():
    return pickle.load(open(DATA_FILE, 'rb'))
