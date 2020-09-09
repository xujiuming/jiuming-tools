import os
import re

# 版本号  setup.py  ming.py 引用  每次发布 版本+1
version = '1.47'

# 配置目录存放在 用户根目录
root_config_dir = '{}/.jiuming-tools'.format(os.path.expanduser('~'))
if not os.path.exists(root_config_dir):
    os.makedirs(root_config_dir)

# 功能配置目录
config_default_file = '{}/.jiuming-tools/config'.format(os.path.expanduser('~'))
if not os.path.exists(config_default_file):
    os.makedirs(config_default_file)

# 脚本默认文件夹
script_default_file = '{}/.jiuming-tools/config/script'.format(os.path.expanduser('~'))
if not os.path.exists(script_default_file):
    os.makedirs(script_default_file)
# 正则
compile_ip = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
compile_host_mame = re.compile('^[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?$')
