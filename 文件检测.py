import hashlib
import os
import time

web_www='/var/www/html'
logfile='/tmp/file_moniter.txt' #不要放在网站根目录下

IS_DELETE_NEWFILE=True          #是否检测到文件后删除该文件

round=1
all_file={}

def myprint(s):
	nowtime=time.strftime("%H:%M:%S",time.localtime())
	s=f"{nowtime} {s}"
	print(s)
	with open(logfile,'a+') as f:
		f.write(s+"\n")

def bytemd5(s):
	return hashlib.md5(s).hexdigest()


def check_file_dir(path):
	try:
		for file in os.listdir(path):
			newpath=os.path.join(path,file)
			#文件
			if not os.path.isdir(newpath):
				md5_value=bytemd5(open(newpath,'rb').read())
				if newpath not in all_file:
					if round !=1:
						myprint("[+] 检测到文件生成 "+newpath)
						if(IS_DELETE_NEWFILE):
							os.remove(newpath)
							myprint("[-] 新生成文件删除 "+newpath)
							del all_file[newpath]
					all_file[newpath]=md5_value
				else:
					if all_file[newpath]!=md5_value:
						myprint(f"[*] 检测到文件修改 "+newpath)
						all_file[newpath]=md5_value
			#目录
			else:
				check_file_dir(os.path.join(path,file))
	except:
		pass

def check_file_delete():
	for path in list(all_file):
		if not os.path.exists(path):
			myprint(f"[-] 检测到文件删除 " + path)
			del all_file[path]

if __name__=='__main__':
	while True:
		check_file_dir(web_www)
		check_file_delete()
		round+=1
		time.sleep(0.5)