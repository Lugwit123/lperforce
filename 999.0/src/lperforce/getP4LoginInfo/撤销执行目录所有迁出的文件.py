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
                    port="192.168.110.26:1666",
                    wsDir=r'H:/',
)

# 登录 Perforce


# 设置需要撤销的文件夹路径 (对应Perforce中的路径)
folder_path = "//H/HZW/12.UE/HWZ/..."  # 将本地路径 h:\HZW\12.UE\HWZ\ 映射到 depot 上的路径

# 获取指定路径下的迁出文件
opened_files = p4.run_opened('-a',folder_path)
print("opened_files",opened_files)
# 获取所有工作区的名称并进行去重
workspaces = set()
for file in opened_files:
    workspace = file['client']  # 获取迁出文件的工作区名称
    workspaces.add(workspace)

# 遍历每个工作区并撤销文件
for workspace in workspaces:
    print(f"正在撤销工作区: {workspace} 的文件迁出...")
    # 设置当前工作区为需要撤销的工作区
    p4.client = workspace
    
    # 执行撤销命令，撤销该工作区下的文件迁出
    p4.run_revert('-C',p4.client,folder_path)
    print(f"已撤销工作区: {workspace} 的文件迁出。")



