import requests 
from urllib.parse import quote
import time
import hashlib
import json

IP_FILE="ip.txt"

# FLAG_FORMAT=r'[a-fA-F0-9]{32}' #FLAG格式
FLAG_FORMAT=r'flag\{'

salt='dwjlajdwofenjefneio'

def md5(s):
	return hashlib.md5(s.encode()).hexdigest()



# 选手ip

def g_ip():
    """从 IP_FILE 文件中读取目标列表，自动补全 http:// 前缀，返回 URL 列表"""
    try:
        with open(IP_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"[ERROR] 找不到文件: {IP_FILE}")
        return []  # 返回空列表而不是 None，避免后续报错

    urls = []
    for line in lines:
        # if not line.startswith("http://") and not line.startswith("https://"):
        #     line = "http://" + line
        urls.append(line)
    # urls=[f'10.50.{i}.3' for i in range(1,30) if i!=15]# 假设15是自己
    return urls


def get_flag(flag_file):
	flags = set()
	with open(flag_file,"r",encoding="utf-8") as f:
		for line in f:
			line =line.strip()
			if not line or "failed" in line:
				continue
			try:
				flag=line.split("->")[-1].strip()
				if len(flag) >= 6:
					flags.add(flag)
			except:
				print(f"[-] 无法解析行: {line}")
	return flags

# flags=get_flag('flag.txt')
# print(flags)


def real_submit_flag(flag):
	# print("提交成功")
	# print(flag)
	# import requests
	session = requests.session()

	burp0_url = "http://172.16.100.5:4000/conflict"
	burp0_cookies = {"MacaronSession": "8d7ad6c28674695b"}
	burp0_headers = {"Cache-Control": "max-age=0", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Referer": "http://172.16.100.5:4000/challenge", "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6", "Connection": "close", "Content-Type": "application/x-www-form-urlencoded"}
	r=session.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies)
	print(f"[*] {flag}",json.loads(r.text)['msg'])


def submit_flag(flag,ip):
	if flag:
		if flag not in open('flag.txt').read():
			print("[+] submitflag: ",flag)
			with open('flag.txt','a+') as f:
				f.write(f"{int(time.time())} {ip} {flag}\n")
			real_submit_flag(flag)
		else:
			print("[-] flag已经提交过: ",flag)



def log(url,filename):
	if url not in open(filename).read():
		with open(filename,'a+') as f:
			f.write(url+'\n')


# ips=g_ip()
# print(ips)

