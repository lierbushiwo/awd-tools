# AWD-tools

## 介绍

AWD 脚本，自写。

当前仓库主要包含以下内容：

- 攻击框架：自动打点、取 flag、提交 flag、结果记录
- 不死马与软连接利用：批量写入、记录落点、二次复用
- 流量检测：记录请求方法、URI、Header、POST 数据
- 文件检测：监控站点目录文件新增、修改、删除
- 垃圾流量：主动制造干扰请求
- PHP WAF 脚本：简单拦截和日志记录

## 目录结构

```text
.
├─ attack.py                  主攻击脚本
├─ util.py                    通用函数、目标读取、flag 记录/提交
├─ undead.py                  生成不死马和 webshell
├─ use_undead_link.py         复用 links.txt / undead.txt 中的落点
├─ 文件检测.py                监控网站目录文件变化
├─ 抓流量.php                 记录请求流量到 /tmp
├─ 垃圾流量.py                对 ip.txt 内目标持续制造干扰流量
├─ ip.txt                     目标列表
├─ flag.txt                   已获取/已记录的 flag
├─ links.txt                  已验证可用的软连接 URL
├─ undead.txt                 已验证可用的不死马 URL
├─ AWD WAF脚本/              一组 PHP WAF 方案
└─ 渊龙 WAF/                  另一组 PHP WAF 及批量注入脚本
```

## 依赖

Python 部分当前只明显依赖：

```bash
pip install requests
```

建议 Python 3.10 以上。

## 使用前先改的配置

### 1. `util.py`

这里是全局配置中心，最少要看下面几个点：

- `IP_FILE="ip.txt"`
  目标列表文件。
- `FLAG_FORMAT=r'flag\{'`
  当前 flag 正则很宽松，只判断返回里是否出现 `flag{`。
  如果比赛 flag 格式固定，建议改成更严格的正则。
- `salt='dwjlajdwofenjefneio'`
  不死马密码相关盐值，`attack.py` 和 `use_undead_link.py` 会一起用。
- `real_submit_flag(flag)`
  这里写死了提交接口地址、Cookie、Header。
  开赛前必须改成你实际的提交接口逻辑。

### 2. `ip.txt`

一行一个目标，当前仓库里不同脚本对格式要求略有区别：

- `attack.py`：通常直接读成 `ip`，拼接为 `http://{ip}/...`
- `垃圾流量.py`：要求 `ip:port` 格式，然后自动补 `http://`

如果你的服务端口不是 80，建议统一写成 `ip:port`，并按实际脚本再微调。

示例：

```text
10.10.10.2
10.10.10.3
10.10.10.4:8080
```

## 使用教程

## 攻击脚本

主文件：`attack.py`

### 脚本作用

当前攻击脚本做的事情是：

1. 从 `ip.txt` 读取目标
2. 调用指定 exp 函数打目标
3. 正则匹配返回内容里的 flag
4. 通过 `submit_flag()` 去重、记录并提交
5. 可选写入不死马 / 软连接并把落点记录到文件

### 当前内置的几个利用函数

#### 1. `exp1_post(ip, cmd="cat /flag")`

默认向：

```text
http://{ip}/index.php
```

发送 POST：

```text
code=system('cat /flag');
```

适合目标已经存在一句话执行点，且参数名是 `code` 的情况。

你至少要改这几个地方：

- `url`
- 参数名 `code`
- 执行 payload

#### 2. `exp2_get(ip, cmd)`

当前实际也是 `POST`，目标写死为：

```text
http://{ip}/user/noname.php
```

参数示例：

```python
data = {
    'cmd': 'dwadwad'
}
```

这是一个占位 exp，需要你按题目实际漏洞点改成可用 payload。

#### 3. `exp3_get(ip, cmd="")`

直接 GET：

```text
http://{ip}/index.php?cmd=system('xxx');
```

适合参数直接进入命令执行的场景。

### 攻击主流程

入口在文件末尾：

```python
if __name__=='__main__':
    ips=g_ip()
    def run_attack(func):
        for ip in ips:
            exec(f"submit_flag({func}('{ip}'),'{ip}')")

    run_attack('exp1_post')
```

当前默认跑的是：

```python
run_attack('exp1_post')
```

也就是说，直接运行时会遍历 `ip.txt`，对每个目标调用 `exp1_post()`。

### 推荐修改方式

开赛前最少改下面几处：

1. 改目标漏洞点 URL
2. 改参数名和 payload
3. 改 `FLAG_FORMAT`
4. 改 `real_submit_flag()`
5. 本地先拿一台靶机测通，再全量跑

如果你想切换 exp，直接改：

```python
run_attack('exp1_post')
```

为：

```python
run_attack('exp2_get')
```

或：

```python
run_attack('exp3_get')
```

### 运行方式

```bash
python attack.py
```

### `attack.py` 里的不死马功能

函数：`do_undead_shell(ip)`

逻辑：

1. 调用 `undead.py` 生成 base64 后门内容
2. 通过已有 webshell 执行命令，把不死马写到目标
3. 主动访问一次触发
4. 尝试检测 `/static/` 下衍生出来的隐藏马
5. 成功后把 URL 追加到 `undead.txt`

当前要改的配置：

```python
undead_path='/var/www/html/static/undead.php'
```

这个路径必须改成目标实际可写目录。

默认生成出来的隐藏马名字规则和 IP 绑定，密码计算逻辑在：

- `undead.py`
- `util.py`

### `attack.py` 里的软连接功能

函数：`do_link(ip)`

逻辑：

1. 利用命令执行点执行 `ln -s /flag xxx`
2. 访问软连接 URL
3. 如果能直接读到 flag，就把 URL 记录到 `links.txt`

当前配置：

```python
link_path='/var/www/html/static/.style.css'
```

同样需要按实际站点目录调整。

### 建议的比赛使用流程

```text
1. 先写通单个 exp
2. 单台测试能稳定拿 flag
3. 配好提交接口
4. 再批量跑 attack.py
5. 如果目标能写文件，再开 do_undead_shell() / do_link()
6. 后续循环用 use_undead_link.py 复用历史落点
```

## 不死马与软连接复用脚本

主文件：`use_undead_link.py`

### 脚本作用

这个脚本用于二次利用已经记录下来的：

- `links.txt`
- `undead.txt`

不重新找洞，直接复用已经成功写入的落点继续取 flag。

### 工作逻辑

- `use_link(link_url)`：直接 GET 软连接 URL，若返回匹配 `FLAG_FORMAT` 就提交
- `use_undead(undead_url)`：计算密码后 POST 命令执行 payload，取 `/flag` 并提交

### 运行方式

```bash
python use_undead_link.py
```

### 注意

- `links.txt` 和 `undead.txt` 需要提前由 `attack.py` 写入
- `salt` 变了以后，旧不死马密码也会变，注意统一

## 不死马生成逻辑

主文件：`undead.py`

### 作用

- `generate_webshell(ip)`：生成一句话木马
- `generate_undead_shell(ip)`：生成递归写入隐藏马的不死马

### 当前行为

不死马会：

- 自删 `unlink(__FILE__)`
- 递归遍历 `/var/www/html/`
- 在目录下写入隐藏的 `.<md5>.php`
- 每秒重复一次

适合在目标存在文件写入能力时维持访问入口。

## 文件检测脚本

主文件：`文件检测.py`

### 作用

监控站点目录文件的：

- 新建
- 修改
- 删除

并把日志写到：

```text
/tmp/file_moniter.txt
```

### 当前默认配置

```python
web_www='/var/www/html'
logfile='/tmp/file_moniter.txt'
IS_DELETE_NEWFILE=True
```

### 特点

- 发现新文件时可自动删除
- 修改通过 md5 检测
- 删除也会记录

### 运行方式

```bash
python 文件检测.py
```

这个脚本更适合防守机本地常驻。

## 流量检测脚本

主文件：`抓流量.php`

### 作用

记录访问到当前页面的请求信息，包括：

- 请求方法
- 请求 URI
- 访问 IP
- HTTP Header
- POST 数据

### 日志位置

当前保存到：

```text
/tmp/week2_<REMOTE_ADDR>
```

其中前缀由：

```php
$lname='week2_';
```

控制。

### 使用方式

把这个文件放到想要观测的入口，访问后会在 `/tmp/` 下生成按来源 IP 区分的日志文件。

## 垃圾流量脚本

主文件：`垃圾流量.py`

### 作用

持续向 `ip.txt` 中的目标发送正常页访问、表单提交、伪上传、伪 webshell 请求，用于干扰对手流量分析。

### 当前配置

```python
IP_FILE = "ip.txt"
THREAD_PER_TARGET = 3
INTERVAL = 0.1
TIMEOUT = 10
```

### 目标格式

这个脚本按 `ip:port` 解析。

例如：

```text
10.10.10.2:80
10.10.10.3:8080
```

### 运行方式

```bash
python 垃圾流量.py
```

按 `Ctrl+C` 停止。

## WAF 脚本

### `AWD WAF脚本/`

包含：

- `waf.php`
- `waf1.php`
- `waf2.php`
- `php_waf_and_log_to_txt.php`

其中 `php_waf_and_log_to_txt.php` 的逻辑比较直观：

- 取 `GET/POST/Cookie/Header/File`
- 简单关键字匹配
- 命中后写 `log.txt`
- 对上传文件内容可直接覆写

### `渊龙 WAF/`

包含：

- `waf.php`
- `waf1.php`
- `secure.php`
- `批量加载waf.py`

其中 `批量加载waf.py` 会递归扫描 PHP 文件，在 `<?php` 后插入：

```php
require_once('/tmp/waf.php');
```

使用前要先把脚本里的：

```python
base_dir = '/Users/apple/Documents/data'
```

改成你实际的网站根目录。

## 常用文件说明

### `ip.txt`

目标列表。

### `flag.txt`

本地记录已拿到的 flag，`submit_flag()` 会用它去重。

### `links.txt`

记录已经验证成功的软连接 URL。

### `undead.txt`

记录已经验证成功的不死马 URL。

## 目前代码里的几个已知问题

这部分不是 bug report，只是提醒自己开赛前要再过一遍：

- `attack.py` 里的 exp 还是偏模板化，很多 URL 和参数是写死示例
- `exp2_get` 名字是 `get`，但当前实现实际走的是 `POST`
- `util.py` 里的提交接口是写死环境，必须手改
- `FLAG_FORMAT` 目前过宽，容易误判
- `垃圾流量.py` 和 `attack.py` 对 `ip.txt` 的格式假设不完全一致
- `渊龙 WAF/批量加载waf.py` 里有重复内容，后面可以顺手清一下

## 后续准备建议

如果后面继续补仓库，建议优先加：

- 多 exp 管理和自动切换
- 并发攻击
- 提交失败重试
- 成功率统计
- 异常日志单独落盘
- 对单目标进行 debug 模式输出



