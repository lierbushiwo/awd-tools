<?php
error_reporting(0);
$lname='week2_';  //对应不通题目的日志流量名

function savelog($remote,$data){
	global $lname;
	$savename='/tmp/'.$lname.$remote;
	$fp=fopen($savename,'a+');
	fwrite($fp, $data);
	fclose($fp);
}

function logger(){
	$lierres=$_SERVER['REQUEST_METHOD'].''.$_SERVER['REQUEST_URI'].'\n';
	$lierres.="REMOTE_ADDR: ".$_SERVER['REMOTE_ADDR'];
	$lierres.="\nHeaders:\n";
	foreach ($_SERVER as $key => $value) {
		// code...
		if(preg_match('/HTTP.*/i',$key)){
			$key=preg_replace('/HTTP\_/', '', $key);
			$key=str_replace('_', '-', $key);
			$lierres.='		'.$key.': '.$value."\n";
		}
	}
	if ($_SERVER['REQUEST_METHOD'] == 'POST') {
        $lierres .= "POST:\n";
        if (!empty($_POST)) {
            $lierres .= http_build_query($_POST);
        } else {
            $post_data = file_get_contents("php://input");
            $lierres .= $post_data ? $post_data : '';
        }
        $lierres .= "\n";
    }
	$lierres.="\n\n";

	/*写入log文件*/
	savelog($_SERVER['REMOTE_ADDR'],$lierres);
	return $lierres;

}

logger();
?>