# AWD-tools

## 介绍

自己写的一套 AWD 小脚本。

这份 README 主要讲 `attack.py` 的主体逻辑，其他脚本只做简单说明。

## 主体思路

`attack.py` 本质上是一个批量打点和提交框架，核心流程很简单：

1. 从 `ip.txt` 读取目标
2. 对每个目标调用指定的利用函数
3. 从返回内容中匹配 flag
4. 调用 `submit_flag()` 做去重、记录、提交
5. 如果有文件写入能力，可以顺手写不死马或软连接做后续复用

也就是说，`attack.py` 的重点不是某一个 exp，而是：

- 批量遍历目标
- 统一取 flag
- 统一提交 flag
- 统一记录落点

## 相关文件

- `attack.py`：主攻击脚本
- `util.py`：读目标、匹配 flag、记录 flag、提交 flag
- `undead.py`：生成不死马内容
- `use_undead_link.py`：复用已经写进去的不死马和软连接
- `ip.txt`：目标列表
- `flag.txt`：已经记录过的 flag
- `links.txt`：软连接落点
- `undead.txt`：不死马落点

## attack.py 逻辑

文件末尾是主入口：

```python
if __name__=='__main__':
    ips=g_ip()
    def run_attack(func):
        for ip in ips:
            exec(f"submit_flag({func}('{ip}'),'{ip}')")

    run_attack('exp1_post')
```

当前执行逻辑就是：

- `g_ip()` 从 `ip.txt` 取目标
- `run_attack()` 遍历所有目标
- 每个目标调用一次指定函数
- 函数返回内容如果是 flag，就交给 `submit_flag()`

这里真正需要你比赛时去改的，通常只有两块：

1. 利用函数本身
2. 提交接口逻辑

## 利用函数怎么理解

`attack.py` 里现在放了几个 `exp`，它们只是例子，不是重点。

不要把 README 理解成“介绍这几个 exp 怎么打”，这里更重要的是统一接口：

```python
def exp_xxx(ip):
    ...
    return flag_or_false
```

也就是你自己写新的利用函数时，尽量保持这个形式：

- 输入是目标 `ip`
- 成功时返回 flag
- 失败时返回 `False`

只要遵守这个形式，就可以直接塞进 `run_attack()` 里批量跑。

## 你实际要改的地方

### 1. `ip.txt`

一行一个目标。

例如：

```text
10.10.10.2
10.10.10.3
10.10.10.4
```

### 2. `util.py`

这个文件里要重点看：

- `FLAG_FORMAT`
  比赛前改成你实际的 flag 格式
- `real_submit_flag(flag)`
  改成你比赛环境的提交接口
- `submit_flag(flag, ip)`
  这里会负责去重和落盘

### 3. `attack.py`

主要改：

- 你自己的利用函数
- 默认跑哪个函数
- 是否开启不死马 / 软连接辅助逻辑

## 不死马和软连接

`attack.py` 里还有两个辅助函数：

- `do_undead_shell(ip)`
- `do_link(ip)`

这两个不是主流程核心，只是当你已经拿到命令执行或文件写入后，顺手做持久化和复用。

作用分别是：

- 不死马：批量写隐藏马，后面继续取 flag
- 软连接：如果 `/flag` 能直接链出来，就记录 URL 备用

后续可以用：

```bash
python use_undead_link.py
```

去复用 `undead.txt` 和 `links.txt` 里的落点。

## 使用方式

安装依赖：

```bash
pip install requests
```

运行：

```bash
python attack.py
```

## 比赛时的推荐流程

1. 先写通一个自己的利用函数
2. 在单台目标上确认能稳定出 flag
3. 配好 `FLAG_FORMAT`
4. 配好提交接口
5. 再用 `attack.py` 批量跑
6. 如果能写文件，再考虑开不死马和软连接
7. 后面用 `use_undead_link.py` 接着收割

## 其他脚本

仓库里另外还有：

- `文件检测.py`：监控网站目录文件变化
- `抓流量.php`：记录请求流量
- `垃圾流量.py`：制造干扰流量
- `AWD WAF脚本/`、`渊龙 WAF/`：一些 WAF 相关脚本

这些都不是这份 README 的重点，主线还是 `attack.py`。

## 一句话总结

这个项目的核心不是某个现成 exp，而是把“利用函数 -> 取 flag -> 去重记录 -> 自动提交”这一套流程统一起来，比赛时你只需要不断往 `attack.py` 里替换或补新的利用函数即可。

