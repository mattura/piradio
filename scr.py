import gaugette.ssd1306
import time
import sys
import spidev
import font5x8

from gaugette.fonts import verdana_15
from gaugette.fonts import verdana_24
from subprocess import Popen, PIPE

RESET_PIN = 0 #15
DC_PIN    = 1 #16

def show_scr(scrollinglist,index):
   scrollinglist.ssd1306.display_block(scrollinglist.bitmaps[index],0,0,scrollinglist.cols)
   scrollinglist.position=index*32

def draw_text(bmp, x, y, string):
  font=font5x8.Font5x8
  font_bytes = font.bytes
  font_rows = font.rows
  font_cols = font.cols
  for c in string:
    p = ord(c) * font_cols
    for col in range(0,font_cols):
       mask = font_bytes[p]
       p+=1
       for row in range(0,8):
         draw_pixel(bmp,x,y+row,mask & 0x1)
         mask >>= 1
       x += 1

def draw_pixel(bmp, x, y, on=True):
            if (x<0 or x>=bmp.cols or y<0 or y>=bmp.rows):
                return
            mem_col = x
            mem_row = y / 8
            bit_mask = 1 << (y % 8)
            offset = mem_row + bmp.rows/8 * mem_col    
            if on:
                bmp.data[offset] |= bit_mask
            else:
                bmp.data[offset] &= (0xFF - bit_mask)

led = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN)
led.begin()
scr = gaugette.ssd1306.SSD1306.ScrollingList(led,[""],verdana_15)
bmp=gaugette.ssd1306.SSD1306.Bitmap(1200,32) #new bmp of fixed width
draw_text(bmp,0,0,"TITLE")
draw_text(bmp,0,16,"Scroller /\ (ascii set)")
draw_text(bmp,0,24,"Stationary text")
scr.bitmaps=[bmp]

y=1		#column for scroller
char_sep=15	#separation between characters
alph=gaugette.ssd1306.SSD1306.Bitmap(95*char_sep+128,8) #buffer holds alpha chars
for i in range(0,95):  #draw alpha chars in buffer
 draw_text(alph,64+i*char_sep,0,chr(i+32))

wid=alph.cols-128
scr.ssd1306.display_block(scr.bitmaps[0],0,0,128,0) #show screen

while True:
 for i in range(0,wid,1):
  scr.ssd1306.display_block(alph,y*8,0,128,i)
 for i in range(wid,0,-1):
  scr.ssd1306.display_block(alph,y*8,0,128,i)
