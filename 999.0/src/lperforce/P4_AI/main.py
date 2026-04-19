import os
import sys
import concurrent.futures
sys.path.append(r'D:\TD_Depot\plug_in\Python\py39Lib')
import fire

Lugwit_publicPath = os.environ.get('Lugwit_publicPath')
LugwitToolDir = os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir + '/Lib')
import Lugwit_Module as LM
lprint=LM.lprint
from lperforce import (loginP4, p4_baselib, P4Lib)
from lperforce.P4LoginInfoModule import p4_loginInfo
from P4 import P4, P4Exception

# 使用登录信息进行 P4 登录
p4 = loginP4.p4_login(userName=p4_loginInfo['project']['User'],
                      port=p4_loginInfo['project']['port'],
                      wsDir='H:/')
P4Lib.p4 = p4
submitChange=P4Lib.submitChange
# p4.run_add(r'h:\AI\Demo\component[2].gif')
# 上传文件
# P4Lib.submitChange(files=[r'h:\AI\Demo\diskette.png'],
#                    description='testAA')
# # 获取文件
# P4Lib.getFile(files=[r'h:\AI\Demo\diskette.png'],)
# # # 获取文件信息
# print (p4.run_files(r'h:\AI\Demo\...'))

if __name__ == '__main__':
    fire.Fire()
