from PIL import Image, ImageDraw, ImageFont
from time import sleep
import math
import ST7796 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

# Raspberry Pi configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0

# Create TFT LCD display class.
disp = TFT.ST7796(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=400000000))

# Initialize display.
disp.begin()

# Clear the display to a red background.
# Can pass any tuple of red, green, blue values (from 0 to 255 each).
disp.clear((255, 0, 0))

#Colours
white = (255,255,255)
black = (0,0,0)
red = (255, 0, 0)
d_red = (128, 0, 0)
green = (0, 255, 0)
d_green = (0, 128, 0)
blue = (0, 0, 255)
d_blue = (0, 0, 128)
yellow = (255, 255, 0)
d_yellow = (128, 128, 0)
black = (0, 0, 0)
white = (255,255,255)
purple = (120, 37, 179)
cyan = (100, 179, 179) 
brown = (100, 54, 42) 
magenta = (255, 0, 255)
gray = (180,180,180)
none = ''

pi = math.pi

size = 2500
width = 320
height = 480
d = 4
px = [-d,  d,  d, -d, -d,  d,  d, -d]
py = [-d, -d,  d,  d, -d, -d,  d,  d]
pz = [-d, -d, -d, -d,  d,  d,  d,  d]

p2x = [0,0,0,0,0,0,0,0]
p2y = [0,0,0,0,0,0,0,0]
r = [0,0,0]
image_size = (width,height)
font = ImageFont.load_default()

#draw.line(((10,10),(100,100)),black)
def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)

def drawCube():
    global image
    r[0] = r[0] + pi / 180.0
    r[1] = r[1] + pi / 180.0
    r[2] = r[2] + pi / 180.0
    if (r[0] >= 360.0 * pi / 180.0):
        r[0] = 0
    if (r[1] >= 360.0 * pi / 180.0):
        r[1] = 0
    if (r[2] >= 360.0 * pi / 180.0):
        r[2] = 0
    image =Image.new('RGB', image_size, black)
    draw = ImageDraw.Draw(image)
    for i in range(8):
        px2 = px[i]
        py2 = math.cos(r[0]) * py[i] - math.sin(r[0]) * pz[i]
        pz2 = math.sin(r[0]) * py[i] + math.cos(r[0]) * pz[i]
      
        px3 = math.cos(r[1]) * px2 + math.sin(r[1]) * pz2
        py3 = py2
        pz3 = -math.sin(r[1]) * px2 + math.cos(r[1]) * pz2

        ax = math.cos(r[2]) * px3 - math.sin(r[2]) * py3
        ay = math.sin(r[2]) * px3 + math.cos(r[2]) * py3
        az = pz3 - 150

        p2x[i] = width // 2 + ax * size // az
        p2y[i] = height // 2 + ay * size // az
     

    setpen = red
    for i in range(3):
        draw.line((int(p2x[i]),   int(p2y[i]),   int(p2x[i+1]), int(p2y[i+1])),setpen)
        draw.line((int(p2x[i+4]), int(p2y[i+4]), int(p2x[i+5]), int(p2y[i+5])),setpen)
        draw.line((int(p2x[i]),   int(p2y[i]),   int(p2x[i+4]), int(p2y[i+4])),setpen)
    draw.line((int(p2x[3]), int(p2y[3]), int(p2x[0]), int(p2y[0])),setpen)
    draw.line((int(p2x[7]), int(p2y[7]), int(p2x[4]), int(p2y[4])),setpen)
    draw.line((int(p2x[3]), int(p2y[3]), int(p2x[7]), int(p2y[7])),setpen)
    draw_rotated_text(disp.buffer, 'Hello World!', (10, 10), 90, font, fill=(255,255,255))

while True:
    drawCube()
    #image.save('Test.png')
    disp.display(image)
    

