import time
import sys
from subprocess import Popen, PIPE

def get_url(s):
  suf=s.rsplit('.',1)[1]
  cmd=['wget','-U','Mozilla/5.0 (X11; U; Linux i686; rv:1.9) Gecko Firefox/3.6','-q',str(s),'-O-']
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

sid=[
'BBC Radio 1',
'Absolute Radio',
'Capital FM',
'Russkoe Radio',
'Jackie'
]
url=[
'http://www.bbc.co.uk/radio/listen/live/r1_aaclca.pls',
'http://mp3-vr-128.as34763.net/listen.pls',
'http://media-ice.musicradio.com/CapitalMP3.m3u',
'http://84.242.240.246:8000',
'http://95.154.211.15:80'
]

# Clear Playlist:
p=Popen(['mpc','clear'],stdout=PIPE,stderr=PIPE)
(rvl,err)=p.communicate()

# Add all URLs to playlist
for k,v in zip(sid,url):
  print get_url(v)
  p=Popen(['mpc','add',get_url(v)],stdout=PIPE,stderr=PIPE)
  (rvl,err)=p.communicate()
