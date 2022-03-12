# This ST7796 Module Is a Modified ILI9341 Base
# Modified by Gary Metheringham

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

import numbers
import time
import numpy as np

from PIL import Image
from PIL import ImageDraw

import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI


# Constants for interacting with display registers.
ST7796_HEIGHT   = 480
ST7796_WIDTH    = 320
ST7796_NOP      = 0x00
ST7796_SWRST    = 0x01
ST7796_RDDID    = 0x04
ST7796_RDDST    = 0x09

ST7796_SLPIN    = 0x10
ST7796_SLPOUT   = 0x11
ST7796_PTLON    = 0x12
ST7796_NORON    = 0x13

ST7796_RDMODE   = 0x0A
ST7796_RDMADCTL   = 0x0B
ST7796_RDPIXFMT   = 0x0C
ST7796_RDIMGFMT   = 0x0A
ST7796_RDSELFDIAG   = 0x0F

ST7796_INVOFF   = 0x20
ST7796_INVON    = 0x21
ST7796_DISPOFF  = 0x28
ST7796_DISPON   = 0x29
ST7796_CASET    = 0x2A
ST7796_PASET    = 0x2B
ST7796_RASET    = 0x2B
ST7796_RAMWR    = 0x2C
ST7796_RAMRD    = 0x2E

ST7796_PTLAR    = 0x30
ST7796_VSCRDEF  = 0x33
ST7796_MADCTL   = 0x36
ST7796_VSCRSADD = 0x37
ST7796_PIXFMT   = 0x3A
ST7796_MAD_MY   = 0x80
ST7796_MAD_MX   = 0x40
ST7796_MAD_MV   = 0x20
ST7796_MAD_ML   = 0x10
ST7796_MAD_BGR  = 0x08
ST7796_MAD_MH   = 0x04
ST7796_MAD_RGB  = 0x00
ST7796_INVOFF   = 0x20
ST7796_INVON    = 0x21

ST7796_WRDISBV   = 0x51
ST7796_RDDISBV   = 0x52
ST7796_WRCTRLD   = 0x53

ST7796_FRMCTR1  = 0xB1
ST7796_FRMCTR2  = 0xB2
ST7796_FRMCTR3  = 0xB3
ST7796_INVCTR   = 0xB4
ST7796_DFUNCTR  = 0xB6

ST7796_PWCTR1   = 0xC0
ST7796_PWCTR2   = 0xC1
ST7796_PWCTR3   = 0xC2

ST7796_VMCTR1   = 0xC5
ST7796_VMCOFF   = 0xC6

ST7796_RDID4    = 0xD3

ST7796_GMCTRP1  = 0xE0
ST7796_GMCTRN1  = 0xE1

ST7796_MADCTL_MY   = 0x80
ST7796_MADCTL_MX   = 0x40
ST7796_MADCTL_MV   = 0x20
ST7796_MADCTL_ML   = 0x10
ST7796_MADCTL_RGB  = 0x00
ST7796_MADCTL_BGR  = 0x08
ST7796_MADCTL_MH   = 0x04


def color565(r, g, b):
    """Convert red, green, blue components to a 16-bit 565 RGB value. Components
    should be values 0 to 255.
    """
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def image_to_data(image):
    """Generator function to convert a PIL image to 16-bit 565 RGB bytes."""
    #NumPy is much faster at doing this. NumPy code provided by:
    #Keith (https:#www.blogger.com/profile/02555547344016007163)
    pb = np.array(image.convert('RGB')).astype('uint16')
    color = ((pb[:,:,0] & 0xF8) << 8) | ((pb[:,:,1] & 0xFC) << 3) | (pb[:,:,2] >> 3)
    return np.dstack(((color >> 8) & 0xFF, color & 0xFF)).flatten().tolist()

class ST7796(object):
    """Representation of an ST7796 TFT LCD."""

    def __init__(self, dc, spi, rst=None, gpio=None, width=ST7796_WIDTH,
        height=ST7796_HEIGHT):
        """Create an instance of the display using SPI communication.  Must
        provide the GPIO pin number for the D/C pin and the SPI driver.  Can
        optionally provide the GPIO pin number for the reset pin as the rst
        parameter.
        """
        self._dc = dc
        self._rst = rst
        self._spi = spi
        self._gpio = gpio
        self.width = width
        self.height = height
        if self._gpio is None:
            self._gpio = GPIO.get_platform_gpio()
        # Set DC as output.
        self._gpio.setup(dc, GPIO.OUT)
        # Setup reset as output (if provided).
        if rst is not None:
            self._gpio.setup(rst, GPIO.OUT)
        # Set SPI to mode 0, MSB first.
        spi.set_mode(0)
        spi.set_bit_order(SPI.MSBFIRST)
        spi.set_clock_hz(64000000)
        # Create an image buffer.
        self.buffer = Image.new('RGB', (width, height))

    def send(self, data, is_data=True, chunk_size=4096):
        """Write a byte or array of bytes to the display. Is_data parameter
        controls if byte should be interpreted as display data (True) or command
        data (False).  Chunk_size is an optional size of bytes to write in a
        single SPI transaction, with a default of 4096.
        """
        # Set DC low for command, high for data.
        self._gpio.output(self._dc, is_data)
        # Convert scalar argument to list so either can be passed as parameter.
        if isinstance(data, numbers.Number):
            data = [data & 0xFF]
        # Write data a chunk at a time.
        for start in range(0, len(data), chunk_size):
            end = min(start+chunk_size, len(data))
            self._spi.write(data[start:end])

    def command(self, data):
        """Write a byte or array of bytes to the display as command data."""
        self.send(data, False)

    def data(self, data):
        """Write a byte or array of bytes to the display as display data."""
        self.send(data, True)

    def reset(self):
        """Reset the display, if reset pin is connected."""
        if self._rst is not None:
            self._gpio.set_high(self._rst)
            time.sleep(0.005)
            self._gpio.set_low(self._rst)
            time.sleep(0.02)
            self._gpio.set_high(self._rst)
            time.sleep(0.150)

    def _init(self):
        # Initialize the display.  Broken out as a separate function so it can
        # be overridden by other displays in the future.
        time.sleep(0.120);

        self.command(0x01); #Software reset
        time.sleep(0.120);

        self.command(0x11); #Sleep exit                                            
        time.sleep(0.120);

        self.command(0xF0); #Command Set control                                 
        self.data(0xC3);    #Enable extension command 2 partI
        
        self.command(0xF0); #Command Set control                                 
        self.data(0x96);    #Enable extension command 2 partII
        
        self.command(0x36); #Memory Data Access Control MX, MY, RGB mode                                    
        self.data(0x48);    #X-Mirror, Top-Left to right-Buttom, RGB  
        
        self.command(0x3A); #Interface Pixel Format                                    
        self.data(0x55);    #Control interface color format set to 16
        
        
        self.command(0xB4); #Column inversion 
        self.data(0x01);    #1-dot inversion

        self.command(0xB6); #Display Function Control
        self.data(0x80);    #Bypass
        self.data(0x02);    #Source Output Scan from S1 to S960, Gate Output scan from G1 to G480, scan cycle=2
        self.data(0x3B);    #LCD Drive Line=8*(59+1)


        self.command(0xE8); #Display Output Ctrl Adjust
        self.data(0x40);
        self.data(0x8A);	
        self.data(0x00);
        self.data(0x00);
        self.data(0x29);    #Source eqaulizing period time= 22.5 us
        self.data(0x19);    #Timing for "Gate start"=25 (Tclk)
        self.data(0xA5);    #Timing for "Gate End"=37 (Tclk), Gate driver EQ function ON
        self.data(0x33);
        
        self.command(0xC1); #Power control2                          
        self.data(0x06);    #VAP(GVDD)=3.85+( vcom+vcom offset), VAN(GVCL)=-3.85+( vcom+vcom offset)
        
        self.command(0xC2); #Power control 3                                      
        self.data(0xA7);    #Source driving current level=low, Gamma driving current level=High
        
        self.command(0xC5); #VCOM Control
        self.data(0x18);    #VCOM=0.9
        self.command(ST7796_CASET)        # Column addr set
        self.data(0x00)
        self.data(0x00)                    # XSTART
        self.data(0x01)
        self.data(0x5E)                    # XEND
        self.command(ST7796_PASET)        # Row addr set
        self.data(0x00)
        self.data(0x00)                    # YSTART
        self.data(0x00)
        self.data(0xE0)                    # YEND
        self.command(ST7796_RAMWR)        # write to RAM
        time.sleep(0.120);
        
        #ST7796 Gamma Sequence
        self.command(0xE0); #Gamma"+"                                             
        self.data(0xF0);
        self.data(0x09); 
        self.data(0x0b);
        self.data(0x06); 
        self.data(0x04);
        self.data(0x15); 
        self.data(0x2F);
        self.data(0x54); 
        self.data(0x42);
        self.data(0x3C); 
        self.data(0x17);
        self.data(0x14);
        self.data(0x18); 
        self.data(0x1B); 
        
        self.command(0xE1); #Gamma"-"                                             
        self.data(0xE0);
        self.data(0x09); 
        self.data(0x0B);
        self.data(0x06); 
        self.data(0x04);
        self.data(0x03); 
        self.data(0x2B);
        self.data(0x43); 
        self.data(0x42);
        self.data(0x3B); 
        self.data(0x16);
        self.data(0x14);
        self.data(0x17); 
        self.data(0x1B);

        time.sleep(0.120);
            
        self.command(0xF0); #Command Set control                                 
        self.data(0x3C);    #Disable extension command 2 partI

        self.command(0xF0); #Command Set control                                 
        self.data(0x69);    #Disable extension command 2 partII

      
        time.sleep(0.120);
    
        self.command(0x29); #Display on                                          	
    def begin(self):
        """Initialize the display.  Should be called once before other calls that
        interact with the display are called.
        """
        self.reset()
        self._init()

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        """Set the pixel address window for proceeding drawing commands. x0 and
        x1 should define the minimum and maximum x pixel bounds.  y0 and y1
        should define the minimum and maximum y pixel bound.  If no parameters
        are specified the default will be to update the entire display from 0,0
        to 239,319.
        """
        if x1 is None:
            x1 = self.width-1
        if y1 is None:
            y1 = self.height-1
        self.command(ST7796_CASET)        # Column addr set
        self.data(x0 >> 8)
        self.data(x0)                    # XSTART
        self.data(x1 >> 8)
        self.data(x1)                    # XEND
        self.command(ST7796_PASET)        # Row addr set
        self.data(y0 >> 8)
        self.data(y0)                    # YSTART
        self.data(y1 >> 8)
        self.data(y1)                    # YEND
        self.command(ST7796_RAMWR)        # write to RAM

    def display(self, image=None):
        """Write the display buffer or provided image to the hardware.  If no
        image parameter is provided the display buffer will be written to the
        hardware.  If an image is provided, it should be RGB format and the
        same dimensions as the display hardware.
        """
        # By default write the internal buffer to the display.
        if image is None:
            image = self.buffer
        # Set address bounds to entire display.
        self.set_window()
        # Convert image to array of 16bit 565 RGB data bytes.
        # Unfortunate that this copy has to occur, but the SPI byte writing
        # function needs to take an array of bytes and PIL doesn't natively
        # store images in 16-bit 565 RGB format.
        pixelbytes = list(image_to_data(image))
        # Write data to hardware.
        self.data(pixelbytes)

    def clear(self, color=(0,0,0)):
        """Clear the image buffer to the specified RGB color (default black)."""
        width, height = self.buffer.size
        self.buffer.putdata([color]*(width*height))

    def draw(self):
        """Return a PIL ImageDraw instance for 2D drawing on the image buffer."""
        return ImageDraw.Draw(self.buffer)
