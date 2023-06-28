import asyncio,logging,os,random,string,re,subprocess,time,shutil
from telethon import TelegramClient, events
from dotenv import load_dotenv
from datetime import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
load_dotenv(override=True)

API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_GROUP = int(os.getenv("LOG_GROUP_ID"))

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def humanify(byte_size):
    siz_list = ['KB', 'MB', 'GB']
    for i in range(len(siz_list)):
        if byte_size/1024**(i+1) < 1024:
            return "{} {}".format(round(byte_size/1024**(i+1), 2), siz_list[i])
def progress_bar(percentage):
    prefix_char = '█'
    suffix_char = '▒'
    progressbar_length = 10
    prefix = round(percentage/progressbar_length) * prefix_char
    suffix = (progressbar_length-round(percentage/progressbar_length)) * suffix_char
    return "{}{} {}%".format(prefix, suffix, percentage)
def check(log_file):
    try:
        with open(log_file, 'r') as file:
            content = file.read()
        duration_match = re.search(r"Duration: (.*?), start:", content)
        raw_duration = duration_match.group(1)
        duration = datetime.strptime(raw_duration, "%H:%M:%S.%f")
        time_matches = re.findall(r"time=(.*?) bitrate", content)
        raw_time = time_matches[-1]
        time = datetime.strptime(raw_time, "%H:%M:%S.%f")
        fraction = 0 if duration == 0 else (time - datetime(1900, 1, 1)) / (duration - datetime(1900, 1, 1))
        progress = progress_bar(round(fraction * 100, 2))
        status = f"Downloading: {progress}\nDuration: {raw_duration}\nCurrent Time: {raw_time}"
        return status
    except Exception as e:
        print(repr(e))
        return ''
async def show_ffmpeg_status(cmd, msg, logfile):
    subprocess.Popen(cmd, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    await asyncio.sleep(10)
    last = ''
    last_edit_time = time.time()
    while os.path.isfile(logfile):
        status = check(logfile)
        if last_edit_time+5 < time.time() and last != status:
            await msg.edit(status)
            last = status
            last_edit_time = time.time()
        await asyncio.sleep(2)
class TimeKeeper:
    last = 0
    last_edited_time = 0
async def upload_callback(current, total, event, file_org_name, tk):
    percentage = round(current/total*100, 2)
    if tk.last+2 < percentage and tk.last_edited_time+5 < time.time():
        await event.edit("Uploading {}\nFile Name: {}\nSize: {}\nUploaded: {}".format(progress_bar(percentage), file_org_name, humanify(total), humanify(current)))
        tk.last = percentage
        tk.last_edited_time = time.time()
async def upload_and_send(event, msg, outFilePath, outFileName, caption):
    tk = TimeKeeper()
    file = await bot.upload_file(
        outFilePath,
        progress_callback=lambda c,t:upload_callback(c,t,msg,outFileName,tk),
    )
    await bot.send_file(
        event.chat,
        file=file,
        thumb=f'{outFilePath}.jpg',
        caption=caption,
        supports_streaming=True
    )
    await bot.send_file(
        LOG_GROUP,
        file=file,
        thumb=f'{outFilePath}.jpg',
        caption=caption,
        supports_streaming=True
    )

@bot.on(events.NewMessage(pattern=r"^(https?://[a-zA-Z0-9./\-&=?_]+\.m3u8)(?: ?\| ?([a-zA-Z0-9./\- ]+))$", func=lambda e: e.is_private))
async def handler(event):
    msg = await event.respond('wait...')
    tmpdir = os.path.join('files', ''.join([random.choice(string.ascii_letters+string.digits) for i in range(15)]))
    os.makedirs(tmpdir)
    inFileName = event.pattern_match[1]
    outFileName = f'{event.pattern_match[2]}.mp4'
    outFilePath = os.path.join(tmpdir, outFileName)
    cmd = ['python', 'converter.py', inFileName, outFilePath]
    await show_ffmpeg_status(cmd, msg, f"{outFilePath}.log")
    await msg.edit('Now uploading...')
    parts = 1
    if os.path.getsize(outFilePath) > 1024**3*4:
        await msg.edit('Now uploading...')
    elif 1024**3*2 < os.path.getsize(outFilePath) < 1024**3*4:
        cmd = ['python', 'splitter.py', outFilePath]
        await show_ffmpeg_status(cmd, msg, f"{outFilePath}.log")
        with open(f"{outFilePath}.parts", 'r') as f:
            parts = int(f.read().strip())
    for i in range(parts):
        i+=1
        await upload_and_send(event,
            msg,
            outFilePath if parts==1 else f'{outFilePath}{i}.mp4',
            outFileName if parts==1 else f'{outFileName}_{i}',
            event.pattern_match[2] if parts==1 else f'{event.pattern_match[2]} part {i}'
        )
    shutil.rmtree(tmpdir)

with bot:
    bot.run_until_disconnected()
