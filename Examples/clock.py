from PIL import Image, ImageDraw, ImageFont
import math
import ST7796 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import time
from math import sin, cos, radians

############################################################################
#         Set up display

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
########################################################
#Set up some Variables

size = 2500
width = 320 
height = 480
d = 4
reverse = False
radius = 120
centerx = width/2
centery = height/2
dirx = 2
diry = 2
px = [-d,  d,  d, -d, -d,  d,  d, -d]
py = [-d, -d,  d,  d, -d, -d,  d,  d]
pz = [-d, -d, -d, -d,  d,  d,  d,  d]
p2x = [0,0,0,0,0,0,0,0]
p2y = [0,0,0,0,0,0,0,0]
r = [0,0,0]
pi = math.pi
image_size = (width,height)
font = ImageFont.truetype('Assets/Poppins-BoldItalic.ttf', 20)

def drawRotatedText(image, text, position, angle, font, fill=(255,255,255)):
    
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=True)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)

def calc_point(x,y,val,fsd,dia, r=False):
    # x y = center of clock
    # val = item number
    # fsd total number of items in circle (12 hours 60 mins etc)
    # dia clock radius
    valTeta = (360/fsd)*val
    if r == True:
        valX=int((x)-(dia-10)*-cos(radians(valTeta)))
    else:
        valX=int((x)-(dia-10)*cos(radians(valTeta)))
    valY=int((y)-(dia-10)*sin(radians(valTeta)))
    return valX, valY

def drawhand(centerx,centery,X,Y, colour):   
    draw.line((centerx+8,centery-8,X,Y), fill = colour)
    draw.line((centerx,centery+8,X,Y), fill = colour)
    draw.line((centerx-8,centery,X,Y), fill = colour)
    draw.line((centerx,centery-8,X,Y), fill = colour)
   
def drawclock(centerx,centery,radius, r = False, colour=(255,255,255)):
    #Draw clocl face
    
    #draw circle
    x1 = centerx-(radius)
    x2 = centerx+(radius) 
    y1 = centery-(radius)
    y2 = centery+(radius)
    draw.ellipse((x1,y1,x2,y2), outline = (255,255,255),fill = None, width = 2)
    #draw hand center    
    draw.ellipse((x1+(radius/1.1),y1+(radius/1.1),x2-(radius/1.1),y2-(radius/1.1)), outline = (255,255,255),fill = colour)
    
    #draw hour, ticks and numbers
    for i in range (0, 12,1):
        x1,y1 = calc_point(centerx,centery,i, 12, radius)
        x2,y2 = calc_point(centerx,centery,i, 12, radius+8)
        x3,y3 = calc_point(centerx-12,centery-4,i, 12, radius-15,r)
        num = i
        if i ==0:num += 12  # so when i = 0 we dont draw a 0 we draw 12 at top of clock
        if reverse == True: 
            num +=6
            if num >12: num -=12
        drawRotatedText(image,str(num),(x3,y3),90, font=font, fill = (255,255,255))
        draw.line((x1,y1,x2,y2), fill = (255,255,255))
    #draw minute ticks    
    for i in range (0, 60,1):
        x1,y1 = calc_point(centerx,centery,i, 60, radius+4)
        x2,y2 = calc_point(centerx,centery,i, 60, radius+8)
        draw.line((x1,y1,x2,y2), fill = (255,255,255))

#main loop
while True:
    
    # get time
    timenow = time.localtime()
    hour = timenow[3] 
    minute = timenow[4]
    second = timenow[5]
    
    #calculate hand tip positions
    secondTeta = 6*second
    if reverse == True:
        secondY=int((centery)-(radius-5)*-sin(radians(secondTeta)))
    else:
        secondY=int((centery)-(radius-5)*sin(radians(secondTeta)))
    secondX=int((centerx)-(radius-5)*cos(radians(secondTeta)))
    
    minuteTeta = 6*(minute+second/90)
    if reverse == True:
        minuteY=int((centery)-(radius-20)*-sin(radians(minuteTeta)))
    else:
        minuteY=int((centery)-(radius-20)*sin(radians(minuteTeta)))
    minuteX=int((centerx)-(radius-20)*cos(radians(minuteTeta)))
    
    hourTeta = 30*(hour+minute/90)
    if reverse == True:
        hourY=int((centery)-(radius-40)*-sin(radians(hourTeta)))
    else:
        hourY=int((centery)-(radius-40)*sin(radians(hourTeta)))
    hourX=int((centerx)-(radius-40)*cos(radians(hourTeta)))
    
    # do all drwaing on screen
    # clear screen
    image =Image.new('RGB', image_size, black)
    draw = ImageDraw.Draw(image)
    
    
    # draw clock face
   
    drawhand(centerx,centery,secondX,secondY, red)
    #draw minute hand
   
    drawhand(centerx,centery,minuteX,minuteY, yellow)
    #draw hour hand
  
    drawhand(centerx,centery,hourX,hourY, green)
    
    #draw second hand
    drawclock(centerx, centery, radius, reverse, white)
    

    
    # update display to draw everything
    
    disp.display(image)

