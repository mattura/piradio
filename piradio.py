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

DC_SECS=1.1     #number of seconds within which 'double click' registers

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
#    a = get_val()
    v = (a/1023.0)*3.3
    d = 16.2537 * v**4 - 129.893 * v**3 + 382.268 * v**2 - 512.611 * v + 306.439
    cm = int(round(d))
    val = '%d cm' % cm
    pc = int(cm/1.5)
    return pc

def get_url(s):
   suf=s.rsplit('.',1)[1]
   cmd=['wget','-U',"Mozilla/5.0 (X11; U; Linux i686; rv:1.9) Gecko Firefox/3.6",'-q',str(s),'-O-']
   if (suf == 'pls'):
      p=Popen(cmd,stdout=PIPE)
      (rvl,err)=p.communicate()
      ind=rvl.find("File1=")+6
      return rvl[ind:rvl.find("\n",ind)]
   elif (suf == 'm3u'):
      p=Popen(cmd,stdout=PIPE)
      (rvl,err)=p.communicate()
      return rvl.rstrip()
   else:
      return s

def get_station():
   p=Popen(['mpc','current'],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()
   t=t.rstrip() #int(t.rstrip().strip('volume: %'))
   if (t==""):
      t=station_list[0]
   return t

def set_station(s):
   p=Popen(['mpc','play',str(s)],stdout=PIPE,stderr=PIPE)
   (t,err)=p.communicate()

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
   scrollinglist.bitmaps[1].clear_block(64,0,80,16)
   scrollinglist.bitmaps[1].draw_text(64,0,str(v),sfont)
   draw_vol_line(scrollinglist.bitmaps[1],v)
   show_scr(scrollinglist,1)

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

# Clear mpc
p=Popen(['mpc','clear'],stdout=PIPE,stderr=PIPE)
(t,err)=p.communicate()
p=Popen(['mpc','volume','75'],stdout=PIPE,stderr=PIPE)
(t,err)=p.communicate()

sid=[
'BBC Radio 1',
#'BBC Radio 2',
#'BBC Radio 3',
#'BBC Radio 4',
#'BBC 6 Music',
#'BBC Radio 1 Xtra',
#'BBC Radio 4 Xtra',
'Absolute Radio',
#'Capital FM',
'Jackie',
'XFM London',
#'Magic',
#'Heart',
'Kiss 100',
'LBC',
'Russkoe Radio'
]
url=[
'http://www.bbc.co.uk/radio/listen/live/r1_aaclca.pls',
#'http://www.bbc.co.uk/radio/listen/live/r2_aaclca.pls',
#'http://www.bbc.co.uk/radio/listen/live/r3_aaclca.pls',
#'http://www.bbc.co.uk/radio/listen/live/r4_aaclca.pls',
#'http://www.bbc.co.uk/radio/listen/live/r6_aaclca.pls',
#'http://www.bbc.co.uk/radio/listen/live/r1x_aaclca.pls',
#'http://www.bbc.co.uk/radio/listen/live/r4x_aaclca.pls',
'http://mp3-vr-128.as34763.net/listen.pls',
#'http://media-ice.musicradio.com/CapitalMP3.m3u',
'http://95.154.211.15:80',
'http://media-ice.musicradio.com/XFMMP3.m3u',
#'http://tx.whatson.com/icecast.php?i=magic1054.mp3.m3u',
#'http://media-ice.musicradio.com/HeartLondonMP3.m3u',
'http://tx.whatson.com/icecast.php?i=kiss100.mp3.m3u',
'http://media-ice.musicradio.com/LBC973.m3u',
'http://84.242.240.246:8000'
]

# Create station list:
for k,v in zip(sid,url):
   print get_url(v)
   p=Popen(['mpc','add',get_url(v)],stdout=PIPE,stderr=PIPE)
   (rvl,err)=p.communicate()

list=["Ready","",""]+sid+[""]  #3 pre screens - current, volume, settings; bounce end
scr = gaugette.ssd1306.SSD1306.ScrollingList(led,list,sfont)
show_scr(scr,0)

#scr.bitmaps[0].draw_text(0,0,"Welcome",sfont)
scr.bitmaps[1].draw_text(0,0,"Volume:",sfont)
scr.bitmaps[2].draw_text(0,0,"Settings",sfont)
scr.ssd1306.display_block(scr.bitmaps[0],0,0,scr.cols)

#sl_append(scr,"Cherries")
#for i in range(1,51):
#  sl_append(scr,"Station: "+str(i))
c=2
while c<1:
   c=time.time()-relt

scr.bitmaps[0].clear_block(0,0,128,32)
d=get_dist()
while (d<30): #dont allow too small range
   d=get_dist()
   scr.bitmaps[0].clear_block(0,15,20,16)
   scr.bitmaps[0].draw_text(0,0,"Sensor blocked!",sfont)
   scr.bitmaps[0].draw_text(0,15,str(d),sfont)
   show_scr(scr,0)
   time.sleep(0.3)
DMAX=d*0.9 #10% error margin for max distance
if (DMAX>100):
   DMAX=100
DMIN=10

print DMAX

scr.bitmaps[0].clear_block(0,0,128,32)
scr.bitmaps[0].draw_text(0,0,"Welcome",sfont)
show_scr(scr,0)
od=0
inid=0
vc=0 #volume counter for set vol
vol=get_vol()
ovol=vol
offt=time.time()
state=1
device_on=True

while device_on:
   d=get_dist()
   if (d>=DMAX): #no hand, or hand taken away:
      if (state==2): #hand taken away
#         print "State 2->3 H rem",d
         state=3
         vol=ovol
         draw_vol(scr,vol)
         set_vol(vol)
      if (state==3): #Hand away after vol -> timeout
         if (time.time()-timer>DC_SECS):
#            print "State 3->1 timeout"
            state=1
            show_scr(scr,0)
      if (state==4): #set station
#         print "State 3->1 H rem",d
         scr.align()
         current_station=scr.position/32
         draw_cur(scr)
         set_station(current_station-2) #scr.list[current_station])
         state=1
         show_scr(scr,0)
      else:
         pass #normal, no hand

   else: #hand
      if (state==1): #hand from first state
         print "State 1->2 H",d
         state=2
         timer=time.time()
         show_scr(scr,1) #display volume screen
         iniv=get_vol()
         time.sleep(0.05)
         d=get_dist() #read again in case of bad 1st value
         inid=d
         stpd=(d-DMIN)/iniv
         stpu=(DMAX-d)/iniv
         od=d
      if (state==2): #adjust volume
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
#         time.sleep(0.05) #smoother/CPU?
         vc=vc+1
         if (vc==5): #only when x increments, change volume
            draw_vol(scr,vol)
            vc=0
            set_vol(ovol)
            ovol=vol
      if (state==3):
#         print "State 3->4 H",d
         state=4 #change channel
         time.sleep(0.05)
         d=get_dist() #read again in case of bad 1st value
         inid=d
         show_scr(scr,current_station)
      if (state==4): #adjust scroll speed for station
         scrs=int((d-inid)/5)
         smax=len(scr.list)-2
         time.sleep(0.02) #float(scrs)/100)
         ind=scr.position/32
#         print d,inid,scr.position,ind,smax,scrs
         if (d<inid): #scroll down
            if (ind>2):
               scr.scroll(scrs)
         if (d>inid): #scroll up
            if (scr.position+scrs<=smax*32):
               scr.scroll(scrs)
            elif (scr.position<smax*32):
               scr.scroll(1)

show_scr(scr,len(scr.list)-1)
p=Popen(['mpc','stop'],stdout=PIPE,stderr=PIPE)
(t,err)=p.communicate()
time.sleep(0.1)
exit()
