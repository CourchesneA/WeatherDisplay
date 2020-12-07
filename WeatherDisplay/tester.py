from waveshare_epd import epd2in7
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

epd = epd2in7.EPD()
epd.init()
EPD_WIDTH = epd2in7.EPD_WIDTH  # 176 pixels
EPD_HEIGHT = epd2in7.EPD_HEIGHT  # 264 pixels

teenytinyfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 10)
teenyfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 12)
tinyfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 14)
smallfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 18)
normalfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 22)
medfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 40)
bigfont = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeArial.ttf', 70)
  



def refresh_display():

    testicon = Image.open('icons/01n.png')
    print("Opened icon")
    
    # Coordinates are X, Y:
    # 0, 0 is top left of screen 176, 264 is bottom right
    # global mask
    mask = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
    # 255: clear the image with white
    draw = ImageDraw.Draw(mask)

    icon_object = {
        "im": testicon,
        "box": (EPD_WIDTH//2 - 96//2, EPD_HEIGHT//8)
    }

    mask.paste(**icon_object)

    text = "Test".upper()
    text_object = {
        'xy':(EPD_WIDTH//2, icon_object['box'][1]+96+25),
        'text':text,
        'font':normalfont,
        'anchor':'ma',
        'spacing':5,
        'align':'center',
        'stroke_width':2
    }
    draw.multiline_text(**text_object)


    #mask = mask.rotate(180)
    epd.display_frame(epd.get_frame_buffer(mask))
    print("Refreshed display")

if __name__ == '__main__':
    print("Starting refresh")
    refresh_display()

