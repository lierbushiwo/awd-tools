#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AWD 混淆流量生成器（支持 ip.txt 批量目标）
格式:127.0.0.1:10001 每行一个
"""

import requests
import random
import time
import threading
from urllib.parse import urljoin
import logging
import os

# ================== 配置区 ==================
IP_FILE = "ip.txt"            # IP 列表文件
THREAD_PER_TARGET = 3         # 每个目标启动的线程数
INTERVAL = 0.1                # 每个请求间隔（秒）
TIMEOUT = 10                   # 请求超时时间

# ===== 可访问的正常页面路径 =====
NORMAL_PATHS = [
    "/index.php",
    "/login.php",
    "/user.php",
    "/info.php",
    "/upload.php",
    "/api.php",
    "/test.php",
    "/"
]

# ===== 常见 Webshell 路径（干扰用）=====
WEBSHELL_HINTS = [
    "/shell.php",
    "/x.php",
    "/upload/shell.php",
    "/images/1.php",
    "/cache/web.php",
    "/backup.php",
    "/admin/x.php",
    "/tmp/upload.php",
    "/data/cmd.php",
    "/cmd.php"
]

# ===== 表单数据模拟 =====
FORM_DATA = {
    'username': ['admin', 'guest', 'test', 'user', 'root'],
    'password': ['123456', 'admin888', 'password', 'toor', 'secret'],
    'action': ['login', 'submit', 'update', 'go'],
    'content': ['hello', 'test', 'data', 'flag', 'info']
}

# ===== 文件上传模拟 =====
def get_file_payload():
    filename = random.choice(['photo.jpg', 'avatar.png', 'doc.txt', 'a.php'])
    content = ''.join(random.choices('abcdef1234567890', k=1024))
    return { 'file': (filename, content, 'application/octet-stream') }

# ================== 混淆逻辑函数 ==================
def generate_confuse_traffic(target_url):
    session = requests.Session()
    session.headers.update({
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'curl/7.68.0',
            'Python-requests/' + requests.__version__,
            'AWD-Defense-Bot/1.0'
        ]),
        'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
        'Connection': 'close'
    })

    logging.info(f"[Worker] Start confusing: {target_url}")

    while True:
        try:
            action = random.randint(1, 4)

            if action == 1:
                # 访问正常页面
                path = random.choice(NORMAL_PATHS)
                url = urljoin(target_url, path)
                params = {'t': random.randint(1000, 9999)} if random.random() > 0.7 else {}
                session.get(url, params=params, timeout=TIMEOUT)

            elif action == 2:
                # 提交表单
                path = random.choice(NORMAL_PATHS)
                url = urljoin(target_url, path)
                data = {k: random.choice(v) for k, v in FORM_DATA.items()}
                session.post(url, data=data, timeout=TIMEOUT)

            elif action == 3:
                # 上传文件
                path = random.choice(['/upload.php', '/user.php', '/index.php'])
                url = urljoin(target_url, path)
                files = get_file_payload()
                session.post(url, files=files, timeout=TIMEOUT)

            elif action == 4:
                # 干扰 Webshell 路径
                path = random.choice(WEBSHELL_HINTS)
                url = urljoin(target_url, path)
                payloads = [
                    {'cmd': 'whoami'},
                    {'p': 'cat /flag'},
                    {'shell': 'id'},
                    {'a': 'ls -la'},
                    {'pass': 'xxx', 'cmd': 'echo hacked'},
                    {'action': 'exec', 'c': 'uname -a'}
                ]
                data = random.choice(payloads)
                try:
                    session.post(url, data=data, timeout=2)
                except:
                    pass  # 忽略失败

            time.sleep(INTERVAL + random.uniform(0, 0.5))

        except Exception as e:
            logging.debug(f"[Error] {target_url} - {e}")
            time.sleep(1)

# ================== 读取 ip.txt 并启动任务 ==================
def load_targets():
    if not os.path.exists(IP_FILE):
        logging.error(f"❌ 文件 {IP_FILE} 不存在！请创建该文件，每行一个 IP:Port")
        exit(1)

    targets = []
    with open(IP_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # 跳过空行和注释
            if ':' in line:
                ip, port = line.split(':', 1)
                url = f"http://{ip}:{port}"
                targets.append(url)
            else:
                logging.warning(f"跳过无效行: {line}")

    if not targets:
        logging.error("❌ 没有从 ip.txt 读取到有效目标！")
        exit(1)

    logging.info(f"✅ 成功加载 {len(targets)} 个目标：{targets}")
    return targets

# ================== 主函数 ==================
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    logging.info("🚀 AWD 混淆流量生成器启动...")

    targets = load_targets()

    # 为每个目标启动多个混淆线程
    for target in targets:
        for i in range(THREAD_PER_TARGET):
            t = threading.Thread(
                target=generate_confuse_traffic,
                args=(target,),
                daemon=True,
                name=f"Confuser-{target.replace('://', '-').replace(':', '-')}-T{i+1}"
            )
            t.start()
            logging.info(f"🧵 启动混淆线程: {t.name}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("🛑 混淆流量已停止。")

if __name__ == '__main__':
    main()