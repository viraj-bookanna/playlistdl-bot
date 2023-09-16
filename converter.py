import os,sys,urllib.parse,re,requests,time,platform
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

redir = '1>NUL 2>"{}"' if platform.system()=='Windows' else '1> "{}" 2>&1'
inFileName = sys.argv[1]
headers = ''
if 'aplusewings' in inFileName:
    proxy = os.environ["HTTP_PROXY"]
    cookie = decode_captcha(requests.get(inFileName, proxies={"http":proxy,"https":proxy}, headers={'User-Agent': 'android'}, verify=False).text)
    headers = f' -http_proxy {proxy}  -headers "Cookie: {cookie}"'
outFilePath = sys.argv[2]
logFilePath = f"{outFilePath}.log"
redir = redir.format(logFilePath)
cmd = f'ffmpeg{headers} -i "{inFileName}" -c copy "{outFilePath}" {redir}'
print(cmd)
os.system(cmd)
cmd2 = f'ffmpeg -i {outFilePath} -ss 00:00:01 -vframes 1 {outFilePath}.jpg'
os.system(cmd2)
time.sleep(3)
os.remove(logFilePath)
