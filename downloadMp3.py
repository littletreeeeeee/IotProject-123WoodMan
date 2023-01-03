import os
from pytube import YouTube

#yt=YouTube("https://www.youtube.com/watch?v=YIiWdy1XjQI")

yt=YouTube("https://www.youtube.com/watch?v=8S7B0_uhZRc")
print("download...")

yt.streams.filter().get_audio_only().download(filename='win.mp3')

print('OK')