import time,sys,spidev
import gaugette.ssd1306
import ir
from gaugette.fonts import verdana_15,verdana_24
from subprocess import Popen, PIPE

RESET_PIN = 0 #15
DC_PIN    = 1 #16
ADC_CHANNEL = 0

DMIN=10
DMAX=110        #max distance (=no hand)

def draw_dist(scr,v): #pixel draw slider
   scr.clear_block(0,0,128,16)
   scr.draw_text3(0,0,"Distance: "+str(v)+" : "+str(state),sfont)
   draw_line(scr,v)
   scr.display()

def draw_line(scr,v): #draw bar
   s=v*scr.cols/100
   scr.bitmap.data[3] = 0xFF #left bound
   scr.bitmap.data[scr.cols*8-1] = 0xFF #right bound
   for i in range(0,scr.cols-1):
      p=i*8+3
      if (i<s):
         scr.bitmap.data[p] = 0xFF #filled
      else:
         scr.bitmap.data[p] = 0x81 #top & bottom line

#Initialise:
led = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN)
led.begin()
#led.invert_display()
led.clear_display()
sfont=verdana_15

sharp=ir.IR()

DMAX=100
DTIM=1.1
state=1
timer=time.time()
deviceon=True

while deviceon:
 d=sharp.get_dist()
 draw_dist(led,d)
# time.sleep(0.1)
 if (d>=DMAX): #away
  d=DMAX
  if (state==2):
   state=3
  if (state==3): #Hand away after vol -> timeout
   dif=time.time()-timer
   if (dif>=DTIM):
    state=1   
  if (state==4):
   state=1
 else: # Hand
  if (state==1):
   state=2
   timer=time.time()
  if (state==3):
   dif=time.time()-timer
   print dif
   state=4

