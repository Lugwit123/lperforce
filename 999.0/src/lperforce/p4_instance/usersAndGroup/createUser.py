import os
import sys
from pathlib import Path

import readExcel

# 设置路径
LugwitToolDir = os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir + '/Lib')

import Lugwit_Module as LM  # noqa: E402

# 获取当前目录
curDir = os.path.dirname(os.path.realpath(__file__))
curDir_Path = Path(curDir)
par_dir = curDir_Path.parent

sys.path.insert(0, str(par_dir))
import loginP4
# 获取用户信息
userInfos = readExcel.get_userInfos('D:/Downloads/人员_主机名.xlsx')
department_dict=readExcel.department_dict
department_dict_invert={val:key for key,val in department_dict.items()}



def addUserToGroup(p4, username, group):
    """
    将用户添加到组。

    参数:
    username (str): 用户名
    group (str): 组名

    返回:
    None
    """
    try:
        group_spec = p4.fetch_group(group)
        LM.lprint (group_spec)
        group_spec["Description"]=department_dict_invert.get(group)

        if 'Users' not in group_spec:
            group_spec['Users'] = []
        if username not in group_spec['Users']:
            group_spec['Users'].append(username)
        print(f'Adding user {username} to group {group}')
        p4.save_group(group_spec)
    except :
        for err in p4.errors:
            print(err)

if __name__ == '__main__':
    # 登录到 Perforce
    p4 = loginP4.p4_login(port='192.168.110.26:1666')
    
    for userInfo in userInfos:
        username = userInfo[0]
        fullname = userInfo[1]
        group = userInfo[2]

        loginP4.createUser(p4, username, fullname, "", f'{username}@qq.com', "standard")
        addUserToGroup(p4, username, group)
    
    p4.disconnect()
