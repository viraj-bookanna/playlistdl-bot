import os,sys,urllib.parse,re,requests,time
from Crypto.Cipher import AES

def decode_captcha(data):
    pattern = 'var a=toNumbers\("([0-9a-f]{32})"\),b=toNumbers\("([0-9a-f]{32})"\),c=toNumbers\("([0-9a-f]{32})"\);document.cookie="([^"]+?)"'
    pattern2 = 'document.cookie="([^"]+?)"'
    m = re.search(pattern, data)
    m2 = re.search(pattern2, data)
    if m:
        cipher = AES.new(bytes.fromhex(m[1]), AES.MODE_CBC, bytes.fromhex(m[2]))
        plain = cipher.decrypt(bytes.fromhex(m[3])).hex()
        return m[4]+plain
    elif m2:
        return m2[1]
    return False

inFileName = sys.argv[1]
headers = ''
if 'aplusewings' in inFileName:
    cookie = decode_captcha(requests.get(inFileName, verify=False).text)
    headers = f' -headers "Cookie: {cookie}"'
outFilePath = sys.argv[2]
logFilePath = f"{outFilePath}.log"
cmd = f'ffmpeg{headers} -i "{inFileName}" -c copy "{outFilePath}" 1>NUL 2>"{logFilePath}"'
print(cmd)
os.system(cmd)
cmd2 = f'ffmpeg -i {outFilePath} -ss 00:00:01.000 -vframes 1 {outFilePath}.jpg'
os.system(cmd2)
time.sleep(3)
os.remove(logFilePath)
