import gaugette.ssd1306
import time
import sys
import spidev

from gaugette.fonts import verdana_15
from gaugette.fonts import verdana_24
from subprocess import Popen, PIPE

RESET_PIN = 0 #15
DC_PIN    = 1 #16
ADC_CHANNEL = 0

DMIN=10
DMAX=110        #max distance (=no hand)
DC_SECS=0.9     #number of seconds within which 'double click' registers

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
    v = (a/1023.0)*3.3
    d = 16.2537 * v**4 - 129.893 * v**3 + 382.268 * v**2 - 512.611 * v + 306.439
    cm = int(round(d))
    val = '%d cm' % cm
    pc = int(cm/1.5)
    return pc

def get_station():
   p=Popen(['mpc','current'],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()
   t=t.rstrip() #int(t.rstrip().strip('volume: %'))
   if (t==""):
      t=station_list[0]
   return t

def get_stations():
   p=Popen(['mpc','lsplaylists'],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()
   t=t.split('\n')#rstrip() #int(t.rstrip().strip('volume: %'))
   t.pop() #last item is empty string
   t.sort() #put in alphabetical order
   return t
def set_station(s):
   p=Popen(['mpc','clear'],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()
   p=Popen(['mpc','load',str(s)],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()
#   print t,err
   p=Popen(['mpc','play'],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()
#   print t,err
#   t=t.rstrip() #int(t.rstrip().strip('volume: %'))

def sl_append(scrollinglist, string): #Append 'string' to Scrolling List
   bmp=gaugette.ssd1306.SSD1306.Bitmap(scrollinglist.cols,scrollinglist.rows)
   bmp.draw_text(0,0,string,verdana_24)
   scrollinglist.bitmaps.append(bmp)
   scrollinglist.list.append(string)

def get_vol():
   p=Popen(['mpc','volume'],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()
   t=int(t.rstrip().strip('volume: %'))
   return t

def set_vol(v):
   p=Popen(['mpc','volume',str(v)],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()

def show_scr(scrollinglist,index):
   scrollinglist.ssd1306.display_block(scrollinglist.bitmaps[index],0,0,scrollinglist.cols)
   scrollinglist.position=index*32

def draw_vol(scrollinglist,v): #pixel draw volume slider
   scrollinglist.bitmaps[1].clear_block(0,0,128,16)
   scrollinglist.bitmaps[1].draw_text(0,0,"Volume: "+str(v),sfont)
   draw_vol_line(scrollinglist.bitmaps[1],v)
   show_scr(scrollinglist,1)
   pass

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

def draw_cur(scrollinglist):
   scrollinglist.bitmaps[0].clear_block(0,0,128,16)
   scrollinglist.bitmaps[0].draw_text(0,0,scrollinglist.list[current_station],sfont)
#show extra information...?
   show_scr(scr,0)

#Initialise:
relt=time.time()
led = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN)
led.begin()
led.clear_display()
sfont=verdana_15
led.draw_text3(0,0,"Loading...",sfont)
led.display()
current_station=3 #get from mpc or 3
state=1
device_on=True

p=Popen(['mpc','clear'],stdout=PIPE,stderr=PIPE)
(t,err)=p.communicate()
p=Popen(['bash','/home/pi/.mpd/bbc.sh'],stdout=PIPE,stderr=PIPE)
(t,err)=p.communicate()


#Create station list:
station_list=get_stations()
print station_list

#station_list=["BBC Radio 1","BBC Radio 4","BBC 6 Music","Absolute Radio","XFM","Russkoe Radio"]

list=["Ready","",""]+station_list+[""]  #3 pre screens - current, volume, settings; bounce end
scr = gaugette.ssd1306.SSD1306.ScrollingList(led,list,sfont)

show_scr(scr,0)

#scr.bitmaps[0].draw_text(0,0,"Welcome",sfont)
scr.bitmaps[1].draw_text(0,0,"Volume",sfont)
scr.bitmaps[2].draw_text(0,0,"Settings",sfont)
scr.ssd1306.display_block(scr.bitmaps[0],0,0,scr.cols)

#sl_append(scr,"Apples")
#sl_append(scr,"Bananas")
#sl_append(scr,"Cherries")
#for i in range(1,51):
#  sl_append(scr,"Station: "+str(i))
c=2
while c<1:
   c=time.time()-relt

scr.bitmaps[0].clear_block(0,0,128,32)
scr.bitmaps[0].draw_text(0,0,"Welcome",sfont)
show_scr(scr,0)
d=0
od=0
inid=0
vol=get_vol()
offt=time.time()

while device_on:
   d=get_dist()
#   time.sleep(0.05)
   if (d>=DMAX): #no hand, or hand taken away:
      d=DMAX
      if (state==2): #hand taken away
         state=4
         relt=time.time() #start the clock
         pass
      if (state==3): #set station
         p=Popen(['mpc','status'],stdout=PIPE,stderr=PIPE)
         (t,err)=p.communicate()
         scr.align()
         current_station=scr.position/32
         draw_cur(scr)
         set_station(current_station-3) #scr.list[current_station])
         state=1
         show_scr(scr,0)
         pass
      if (state==4): #4 second hold state
         if (time.time()-relt>3): #put message back
            state=1
            show_scr(scr,0)
      else:
         pass #normal, no hand

   else: #hand
      if (state==1 or state==4): #hand from first state/hold state
         timt=time.time()-relt
         if (timt>DC_SECS):# or abs(od-d)>20): #too long for double click or didnt significantly change vol
            show_scr(scr,1) #display volume screen
            state=2
            iniv=get_vol()
            d=get_dist() #read again in case of bad 1st value
            inid=d
            stpd=(d-DMIN)/iniv
            stpu=(DMAX-d)/iniv
            od=d
            pass
         else: #double click
            state=3 #change channel
            d=get_dist() #read again in case of bad 1st value
            inid=d
            show_scr(scr,current_station)
            pass
      if (state==2): #adjust volume
#         time.sleep(0.02) #smoother/CPU?
         if (d<inid): #vol down
            vol=iniv-(inid-d) #d*stpd/inid
         else: #vol up
            vol=iniv+(d-inid) #d*stpu/inid
         if (vol<=1):
            vol=1
            tt=time.time()-offt
            if (tt>4):
              device_on=False
         else:
            offt=time.time()
         if (vol>100):
            vol=100
         draw_vol(scr,vol)
         set_vol(vol)
         pass #get new
      if (state==3): #adjust scroll speed for station
         scrs=int((d-inid)/5)
         smax=len(scr.list)-2
         time.sleep(0.02) #float(scrs)/100)
         ind=scr.position/32
#         print d,scr.position,ind,smax
         if (d<inid): #scroll down
            if (ind>2):
               scr.scroll(scrs)
         else: #scroll up
            if (scr.position+scrs<=smax*32):
               scr.scroll(scrs)
            elif (scr.position<smax*32):
               scr.scroll(1)



show_scr(scr,len(scr.list)-1)

p=Popen(['mpc','stop'],stdout=PIPE,stderr=PIPE)
(t,err)=p.communicate()

time.sleep(0.1)

exit()
