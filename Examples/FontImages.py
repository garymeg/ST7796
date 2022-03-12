# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
import ST7796 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI


# Raspberry Pi configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0

# Create TFT LCD display class.
disp = TFT.ST7796(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))

# Initialize display.
disp.begin()

# Clear the display to a red background.
# Can pass any tuple of red, green, blue values (from 0 to 255 each).
disp.clear((255, 0, 0))

# Alternatively can clear to a black screen by calling:
# disp.clear()

# Get a PIL Draw object to start drawing on the display buffer.
draw = disp.draw()

# Alternatively load a TTF font.
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
#font = ImageFont.truetype('Minecraftia.ttf', 16)

# Define a function to create rotated text.  Unfortunately PIL doesn't have good
# native support for rotated fonts, but this function can be used to make a
# text image and rotate it so it's easy to paste in the buffer.
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
    rotated = textimage.rotate(angle, expand=True)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)

# Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
font = ImageFont.truetype('Assets/Poppins-BoldItalic.ttf',20)
draw_rotated_text(disp.buffer, 'Here are some ttf font Examples', (20, 140), 90, font, fill=(255,255,255))
font = ImageFont.truetype('Assets/Pacifico.ttf',30)
draw_rotated_text(disp.buffer, 'Just save the font to the Pi', (50, 110), 90, font, fill=(255,255,255))
font = ImageFont.truetype('Assets/ShadowsIntoLight.ttf',30)
draw_rotated_text(disp.buffer, 'in your Python sketch folder', (100, 140), 90, font, fill=(255,255,255))
font = ImageFont.truetype('Assets/Sansita.ttf',30)
draw_rotated_text(disp.buffer, 'And set the font file name', (150, 140), 90, font, fill=(255,255,255))
font = ImageFont.truetype('Assets/PressStart2P.ttf',15)
draw_rotated_text(disp.buffer, 'And set', (225, 370), 90, font, fill=(255,255,255))
font = ImageFont.truetype('Assets/PressStart2P.ttf',45)
draw_rotated_text(disp.buffer, 'The size', (200, 5), 90, font, fill=(255,255,255))
font = ImageFont.truetype('Assets/Monoton.ttf',50)
draw_rotated_text(disp.buffer, 'Fancy fonts', (250, 90), 90, font, fill=(255,255,255))

# Write buffer to display hardware, must be called to make things visible on the
# display!
disp.display()
time.sleep(5)
width, height = 320, 480
# Create a new image with transparent background to store the text.
image = Image.new('RGBA', (width, height), (0,0,0,0))   
image = Image.open('Assets/Python.png')
image = image.rotate(90).resize((320, 480))
disp.display(image)
time.sleep(2)
image = Image.open('Assets/Ras-py.jpg')
image = image.rotate(90).resize((320, 480))
disp.display(image)
time.sleep(2)
image = Image.open('Assets/Raspberry.jpg')
image = image.rotate(90).resize((320, 480))
disp.display(image)
time.sleep(2)
image = Image.open('Assets/Tiger.jpg')
image = image.rotate(90).resize((320, 480))
disp.display(image)
time.sleep(2)