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

def draw_p(scr,x,a):
  scr.bitmaps[0].data[(x+a)*4-1]=0x00
  scr.bitmaps[0].data[x*4-1]=0xFF

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
led.clear_display()

sfont=verdana_15

led.draw_text3(0,0,"Loading...",sfont)
led.display()

scr = gaugette.ssd1306.SSD1306.ScrollingList(led,["All your base are belong to us!"],sfont)
#led.invert_display()

draw_text(scr.bitmaps[0],0,0,"Hello test, we are off to see the wizard")

wid=scr.bitmaps[0].cols-128
str=0
scr.ssd1306.display_block(scr.bitmaps[0],0,0,128,str) #side scroll

time.sleep(1)

while True:
 for i in range(str,wid):  #row,col,count(width),offset
#  scr.ssd1306.display_block(scr.bitmaps[0],0,0,i,0) #wipe l-r
#  scr.ssd1306.display_block(scr.bitmaps[0],0,-i,i,0) #roll?
#  scr.ssd1306.display_block(scr.bitmaps[0],0,0,128,0) #standard
#  scr.ssd1306.display_block(scr.bitmaps[0],0,0,128,i) #side scroll
#  scr.ssd1306.display_block(scr.bitmaps[0],0,j,i,0) 

  draw_p(scr,63+i,-1)
  scr.ssd1306.display_block(scr.bitmaps[0],0,0,128,i) #side scroll
 time.sleep(0.1)
 for i in range(wid,str,-1):
  draw_p(scr,63+i,1)
  scr.ssd1306.display_block(scr.bitmaps[0],0,0,128,i) #side scroll
 time.sleep(0.1)

