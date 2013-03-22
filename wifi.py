import gaugette.ssd1306
import time,sys
import wiringpi

from gaugette.fonts import verdana_15
from gaugette.fonts import verdana_24
from subprocess import Popen, PIPE

LSRPIN = 8
RESET_PIN = 0 #15
DC_PIN    = 1 #16

def show_scr(scrollinglist,index):
   scrollinglist.ssd1306.display_block(scrollinglist.bitmaps[index],0,0,scrollinglist.cols)
   scrollinglist.position=index*32

def draw_vline(scr,x,y0,y1):
   bm= 1 << (y0%8)
   bm=0xFF
   os=x*4+3 #+128/8 * y0
   y0%8
   scr.data[os] |= bm

def draw_vol_line(scrollinglist,v): #draw volume bar
   s=v*scrollinglist.cols/100
   scrollinglist.data[3] = 0xFF #left bound
   scrollinglist.data[scrollinglist.cols*4-1] = 0xFF #right bound
   for i in range(0,scrollinglist.cols-1):
      p=i*4+3
      if (i<s):
         scrollinglist.data[p] = 0xFF #filled
      else:
         scrollinglist.data[p] = 0x81 #top & bottom line

def get_boot_time():
   p=Popen(['systemd-analyze','time'],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()
   tt=t.find("=")+2
   return t[tt:]

def get_ip():
   p=Popen(['ifconfig','wlan0'],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()
   t1=t.find("inet")+5
   t2=t.find("netmask")
   return t[t1:t2]

#Initialise:
led = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN)
led.begin()
led.clear_display()
sfont=verdana_15
list=[" "," "]
scr = gaugette.ssd1306.SSD1306.ScrollingList(led,list,sfont)

bt=get_boot_time()
ip=get_ip()
print ip
scr.bitmaps[0].draw_text(0,0,bt,sfont)
scr.bitmaps[0].draw_text(0,17,ip,sfont)
show_scr(scr,0)
time.sleep(10)
scr.bitmaps[0].clear_block(0,0,128,32)

lsr=wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_PINS)
lsr.pinMode(LSRPIN,lsr.OUTPUT)
def lsr_off():
 lsr.digitalWrite(LSRPIN,lsr.HIGH)
def lsr_on():
 lsr.digitalWrite(LSRPIN,lsr.LOW)

while True:
   p=Popen(['iwconfig','wlan0'],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()
   wi1=t.find("ESSID:")+7
   wi2=t.find("Bit Rate:")+9
   wi3=t.find("Signal level=")+13
   ssid=t[wi1:t.find("\"",wi1)]
#   print "Bitrate: "+t[wi2:t.find("s",wi2)+1]
   sig=int(t[wi3:t.find("/",wi3)])
   
   p=Popen(['ping','-c','1','-I','wlan0','www.google.com'],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()
   wi4=t.find("time=")+5
   png=t[wi4:t.find("ms",wi4)]
   scr.bitmaps[0].clear_block(0,0,128,16)
   scr.bitmaps[0].draw_text(0,0,ssid+": "+str(sig)+" / "+str(png),sfont)
   draw_vol_line(scr.bitmaps[0],sig)
   lsr_on()
   show_scr(scr,0)
   lsr_off()
   time.sleep(1.1)

