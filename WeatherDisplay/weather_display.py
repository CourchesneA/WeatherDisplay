"""Weather e-ink display.

Weather forecast from Yr, delivered by the
Norwegian Meteorological Institute and NRK.

This code is specifically written for the
2.7 inch e-ink display, but can easily be
modified to fit another size.
"""


import json
import logging
import os
import pickle
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in7

from constants import DATA_FILE
from data_handler import read_data
from utils import get_weather_onecall



# Constants
IMG_SIZE = (96, 96)
MARGIN_LEFT = 4
MARGIN_TOP = 4
MARGIN_DEFAULT = 4

EPD_WIDTH = epd2in7.EPD_WIDTH  # 176 pixels
EPD_HEIGHT = epd2in7.EPD_HEIGHT  # 264 pixels
VCENTER = EPD_HEIGHT // 2
VHIGH = EPD_HEIGHT // 3
VLOW = 2 * (EPD_HEIGHT // 3)

HCENTER = EPD_WIDTH // 2
HLEFT = EPD_WIDTH // 3
HRIGHT = 2 * (EPD_WIDTH // 3)

DEG_SIGN= u'\N{DEGREE SIGN}'


# Fonts
teenytinyfont = ImageFont.truetype(
    "/usr/share/fonts/truetype/freefont/FreeArial.ttf", 10
)
teenyfont = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeArial.ttf", 12)
tinyfont = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeArial.ttf", 14)
smallfont = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeArial.ttf", 18)
normalfont = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeArial.ttf", 22)
medfont = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeArial.ttf", 40)
bigfont = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeArial.ttf", 70)


logger = logging.getLogger("weather_display")
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    filename="{}/logs/weather.log".format(os.getcwd()),
    filemode="w",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class WeatherDisplayer:
    def __init__(self):
        self.epd = epd2in7.EPD()
        self.epd.init()
        inp = self.read_data()
        self.city = inp["city"]
        self.data = inp["one_call"]

    def refresh_display(self):

        # Coordinates are X, Y:
        # 0, 0 is top left of screen 176, 264 is bottom right
        # global mask
        mask = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)
        # 255: clear the image with white
        draw = ImageDraw.Draw(mask)

        # Display city in "Today"
        greeting_msg = self.city
        greeting_object = {
            "xy": (MARGIN_LEFT, MARGIN_TOP),
            "text": greeting_msg,
            "font": normalfont,
            "anchor": "la",
            "align": "center",
            "stroke_width": 1,
            "language": "fr-CA",
        }
        draw.multiline_text(**greeting_object)

        # Display current weather icon
        weather_icon_name = self.data["current"]["weather"][0]["icon"]
        weather_icon = Image.open(f"icons/{weather_icon_name}.png")
        weather_icon_object = {
            "im": weather_icon,
            "box": (
                MARGIN_LEFT,
                greeting_object["xy"][1]
                + greeting_object["font"].getsize(greeting_msg)[1]
                + MARGIN_DEFAULT,
            ),
        }

        mask.paste(**weather_icon_object)

        # Display current weather numeric
        current_temp = str(round(self.data["current"]["temp"]))
        lpos = (
            MARGIN_LEFT + IMG_SIZE[0] + MARGIN_DEFAULT / 2
        )  # Left of the temp display area
        xpos = lpos + (EPD_WIDTH - lpos) / 2  # Middle of the temp display area
        temp_text = f"{current_temp}{DEG_SIGN}"
        current_temp_object = {
            "xy": (xpos, weather_icon_object["box"][1] + IMG_SIZE[0] // 2),
            "text": temp_text,
            "font": medfont,
            "anchor": "mm",
            "align": "center",
            "stroke_width": 1,
            "language": "fr-CA",
        }
        draw.multiline_text(**current_temp_object)

        # Display icon description
        weather_icon_desc = self.data["current"]["weather"][0]["description"]
        icon_desc_object = {
            "xy": (
                EPD_WIDTH / 2,
                weather_icon_object["box"][1] + IMG_SIZE[0] + MARGIN_DEFAULT,
            ),
            "text": weather_icon_desc,
            "font": normalfont,
            "anchor": "ma",
            "align": "center",
            "stroke_width": 1,
            "language": "fr-CA",
        }
        draw.multiline_text(**icon_desc_object)

        extra_spacing = MARGIN_DEFAULT*4

        # Show `PDP`
        pdp_str = "pluie"
        pdp_text_object = {
            "xy": (
                EPD_WIDTH // 4,
                weather_icon_object["box"][1]
                + IMG_SIZE[1]
                + icon_desc_object["font"].getsize(weather_icon_desc)[1]
                + MARGIN_DEFAULT * 2
                + extra_spacing,
            ),
            "text": pdp_str,
            "font": smallfont,
            "anchor": "ma",
            "align": "center",
            "stroke_width": 1,
            "language": "fr-CA",
        }
        draw.multiline_text(**pdp_text_object)
        print(f"printing at: {pdp_text_object['xy']}")

        # Display numerical PDP
        current_pdp = str(round(self.data["hourly"][0]["pop"]))
        pdp_text = f"{current_pdp}%"
        pdp_object = {
            "xy": (
                EPD_WIDTH // 4,
                pdp_text_object["xy"][1]
                + pdp_text_object["font"].getsize(pdp_str)[1]
                + MARGIN_DEFAULT,
            ),
            "text": pdp_text,
            "font": normalfont,
            "anchor": "ma",
            "align": "center",
            "stroke_width": 1,
            "language": "fr-CA",
        }
        draw.multiline_text(**pdp_object)

        # Show `ressenti`
        rst_str = "feel"
        rst_text_object = {
            "xy": (
                3 * (EPD_WIDTH // 4),
                weather_icon_object["box"][1]
                + IMG_SIZE[1]
                + icon_desc_object["font"].getsize(weather_icon_desc)[1]
                + MARGIN_DEFAULT * 2
                + extra_spacing,
            ),
            "text": rst_str,
            "font": smallfont,
            "anchor": "ma",
            "align": "center",
            "stroke_width": 1,
            "language": "fr-CA",
        }
        draw.multiline_text(**rst_text_object)

        # Display felt temp
        current_rst = str(round(self.data["current"]["feels_like"]))
        rst_text = f"{current_rst}{DEG_SIGN}"
        rst_object = {
            "xy": (
                3 * (EPD_WIDTH // 4),
                pdp_text_object["xy"][1]
                + rst_text_object["font"].getsize(pdp_str)[1]
                + MARGIN_DEFAULT,
            ),
            "text": rst_text,
            "font": normalfont,
            "anchor": "ma",
            "align": "center",
            "stroke_width": 1,
            "language": "fr-CA",
        }
        draw.multiline_text(**rst_object)



        # Show timestamp
        # TODO sync arrow image

        ts = int(self.data["current"]["dt"])
        converted_time = datetime.utcfromtimestamp(ts) - timedelta(hours=5)
        ts_str = converted_time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Refreshed at {ts_str}")
        ts_object = {
            "xy": (EPD_WIDTH - 2, EPD_HEIGHT - 2),
            "text": ts_str,
            "font": tinyfont,
            "anchor": "rd",
            "spacing": 5,
            "align": "center",
            "stroke_width": 1,
            "language": "fr-CA",
        }
        draw.multiline_text(**ts_object)

        # mask = mask.rotate(180)
        self.epd.display_frame(self.epd.get_frame_buffer(mask))
        print("Refreshed display")


if __name__ == "__main__":
    displayer = WeatherDisplayer()

    print("Starting refresh")
    displayer.refresh_display()
