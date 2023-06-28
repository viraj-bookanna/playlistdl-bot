import os,sys,re,time
from datetime import datetime

def seconds_to_human_time(sec):
    hrs = sec // 3600
    sec %= 3600
    mins = sec // 60
    sec %= 60
    return "%02d:%02d:%02d" % (hrs, mins, sec) 

inFileName = sys.argv[1]
logFilePath = f"{inFileName}.log"
cmd = f'ffmpeg -i "{inFileName}" 1>NUL 2>"{inFileName}.info"'
os.system(cmd)
with open(f"{inFileName}.info", 'r') as f:
    content = f.read()
os.remove(f"{inFileName}.info")
duration_match = re.search(r"Duration: (.*?), start:", content)
raw_duration = duration_match.group(1)
duration = datetime.strptime(raw_duration, "%H:%M:%S.%f")
half = seconds_to_human_time((duration - datetime(1900, 1, 1)).total_seconds()/2)
cmd2 = f'ffmpeg -i {inFileName} -t {half} -c copy "{inFileName}1.mp4" 1>NUL 2>"{logFilePath}"'
os.system(cmd2)
cmd2 = f'ffmpeg -i {inFileName}1.mp4 -ss 00:00:01.000 -vframes 1 {inFileName}1.mp4.jpg'
os.system(cmd2)
cmd2 = f'ffmpeg -i {inFileName} -ss {half} -c copy "{inFileName}2.mp4" 1>NUL 2>"{logFilePath}"'
os.system(cmd2)
cmd2 = f'ffmpeg -i {inFileName}2.mp4 -ss 00:00:01.000 -vframes 1 {inFileName}2.mp4.jpg'
os.system(cmd2)
with open(f"{inFileName}.parts", 'w') as f:
    f.write('2')
time.sleep(3)
os.remove(logFilePath)
