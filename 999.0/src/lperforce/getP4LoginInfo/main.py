import os
import sys
from pathlib import Path


LugwitToolDir = os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir + '/Lib')

import Lugwit_Module as LM  # noqa: E402

# 获取当前目录
curDir = os.path.dirname(os.path.realpath(__file__))
curDir_Path = Path(curDir)
par_dir = curDir_Path.parent

sys.path.insert(0, str(par_dir))
import loginP4
import p4_baselib

p4=loginP4.p4_login(userName='p4_operator',
                    password='123',
                    port="192.168.110.26:1666")
client = p4_baselib.getH_projectClient(p4)

username = client.get("Owner")
user_info = p4.run("user", "-o", username)
user_groups = p4_baselib.get_user_groups(p4, username)
print (user_info)
print (user_groups)

p4.disconnect()

