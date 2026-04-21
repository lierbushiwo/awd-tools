import os

# 设置 web 根路径
base_dir = '/Users/apple/Documents/data'  # 修改为你的实际路径

def modifyip(tfile, sstr, rstr):
    """
    在文件中查找 sstr，并替换为 rstr
    """
    try:
        with open(tfile, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        with open(tfile, 'w', encoding='utf-8') as f:
            for line in lines:
                if sstr in line and not modified:
                    # 只替换第一次出现的，并插入新代码
                    line = line.replace(sstr, rstr)
                    modified = True
                f.write(line)
    except Exception as e:
        print(f"Error modifying file {tfile}: {e}")

def scandir(startdir):
    """
    递归扫描目录，对 .php 文件插入代码
    """
    for item in os.listdir(startdir):
        path = os.path.join(startdir, item)
        if os.path.isfile(path) and item.endswith('.php'):
            print(f"Processing: {path}")
            modifyip(path, '<?php', '<?php\nrequire_once(\'/tmp/waf.php\');')
        elif os.path.isdir(path):
            scandir(path)  # 递归进入子目录

# 执行扫描
if __name__ == '__main__':
    if os.path.exists(base_dir):
        scandir(base_dir)
        print("Scan and injection completed.")
    else:
        print(f"Directory not found: {base_dir}")import os

# 设置 web 根路径
base_dir = '/Users/apple/Documents/data'  # 修改为你的实际路径

def modifyip(tfile, sstr, rstr):
    """
    在文件中查找 sstr，并替换为 rstr
    """
    try:
        with open(tfile, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        with open(tfile, 'w', encoding='utf-8') as f:
            for line in lines:
                if sstr in line and not modified:
                    # 只替换第一次出现的，并插入新代码
                    line = line.replace(sstr, rstr)
                    modified = True
                f.write(line)
    except Exception as e:
        print(f"Error modifying file {tfile}: {e}")

def scandir(startdir):
    """
    递归扫描目录，对 .php 文件插入代码
    """
    for item in os.listdir(startdir):
        path = os.path.join(startdir, item)
        if os.path.isfile(path) and item.endswith('.php'):
            print(f"Processing: {path}")
            modifyip(path, '<?php', '<?php\nrequire_once(\'/tmp/waf.php\');')
        elif os.path.isdir(path):
            scandir(path)  # 递归进入子目录

# 执行扫描
if __name__ == '__main__':
    if os.path.exists(base_dir):
        scandir(base_dir)
        print("Scan and injection completed.")
    else:
        print(f"Directory not found: {base_dir}")