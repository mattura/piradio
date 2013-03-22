import time,sys,spidev
import gaugette.ssd1306
from gaugette.fonts import verdana_15,verdana_24
from subprocess import Popen, PIPE

RESET_PIN = 0 #15
DC_PIN    = 1 #16
ADC_CHANNEL = 0

DMIN=10
DMAX=110        #max distance (=no hand)

inp = spidev.SpiDev()
inp.open(0,1)   #Device chip select 1 - connect CS pin to GPIO7 (CE1) on Raspberry Pi

#read analogue value from ADC (MCP3008)
def get_val():
    r = inp.xfer2([1,(8+ADC_CHANNEL)<<4,0])
    v = ((r[1]&3) << 8) + r[2]
    return v

def get_dist():
    r = []
    for i in range (0,10):
        r.append(get_val())
    a = sum(r)/10.0
#    a=get_val() #single shot
    v = (a/1023.0)*3.3
    d = 16.2537 * v**4 - 129.893 * v**3 + 382.268 * v**2 - 512.611 * v + 306.439
    cm = int(round(d))
    val = '%d cm' % cm
    pc = int(cm/1.5)
    return pc

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

DMAX=100
DTIM=1.1
state=1
timer=time.time()
deviceon=True

while deviceon:
 d=get_dist()
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

