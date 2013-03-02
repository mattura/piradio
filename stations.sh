#!/bin/bash
set -e
playlistdir=/home/pi/mpd/playlists

declare -A radios
radios["BBC Radio 1"]="http://www.bbc.co.uk/radio/listen/live/r1_aaclca.pls"
radios["BBC Radio 1 Xtra"]="http://www.bbc.co.uk/radio/listen/live/r1x_aaclca.pls"
radios["BBC Radio 2"]="http://www.bbc.co.uk/radio/listen/live/r2_aaclca.pls"
radios["BBC 6 Music"]="http://www.bbc.co.uk/radio/listen/live/r6_aaclca.pls"
radios["BBC Radio 3"]="http://www.bbc.co.uk/radio/listen/live/r3_aaclca.pls"
radios["BBC Radio 4"]="http://www.bbc.co.uk/radio/listen/live/r4_aaclca.pls"
radios["BBC Radio 4 Xtra"]="http://www.bbc.co.uk/radio/listen/live/r4x_aaclca.pls"
#radios["BBC Radio 5 Live"]="http://www.bbc.co.uk/radio/listen/live/r5l_aaclca.pls"
#radios["BBC World Service"]="http://www.bbc.co.uk/worldservice/meta/live/nb/eieuk_au_nb_aaclca.pls"
#radios["BBC World Service English News"]="http://www.bbc.co.uk/worldservice/meta/live/nb/einws_au_nb_aaclca.pls"

radios["Absolute Radio"]="http://mp3-vr-128.as34763.net/listen.pls"
radios["Absolute Classic Rock"]="http://mp3-vc-128.as34763.net/listen.pls"

radios["Jackie"]="http://95.154.211.15:80"
radios["Russkoe"]="http://84.242.240.246:8000"
radios["Captial FM"]="http://media-ice.musicradio.com/CapitalMP3.m3u"
radios["XFM London"]="http://media-ice.musicradio.com/XFMMP3.m3u"
radios["Magic"]="http://tx.whatson.com/icecast.php?i=magic1054.mp3.m3u"
radios["Heart London"]="http://media-ice.musicradio.com/HeartLondonMP3.m3u"
radios["LBC 97.3"]="http://media-ice.musicradio.com/LBC973.m3u"
radios["Kiss 100"]="http://tx.whatson.com/icecast.php?i=kiss100.mp3.m3u"

for k in "${radios[@]}"
do
suffix=${k##*.}
if [ "$suffix" = "mp3" ] ; then
   mpc add $1
else
   #Fake useragent
   alias wget='wget -U "Mozilla/5.0 (X11; U; Linux i686; it; rv:1.9.1.7) Gecko/20100106 Ubuntu/9.10 (karmic) Firefox/3.5.7"'
   #Download parse and add to mpd
   #result=$(wget -q $1 -O-)
   #echo "$result"
   if [ "$suffix" = "pls" ] ; then
      wget -q $k -O- | grep "File1=" | sed -e 's/^File[1]*=//' | tr -d "\r" | mpc add
   elif [ "$suffix" = "m3u" ] ; then
      wget -q $k -O- | cat | xargs -r mpc add
   else
      mpc add $k
   fi
fi
done

