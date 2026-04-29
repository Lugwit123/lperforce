# -*- coding: utf-8 -*-


import os
import sys
import io
from pathlib import Path
import traceback

import codecs
import datetime
import time
import json
import subprocess
#os.environ["Lugwit_Debug"]="none"
# 将控制台输出重定向到文件
# sys.stdout = open(r'D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\trayapp\Lib\LPerforce\p4_trigger\autoExFbx\output_log.log', 'w')
# 设置路径
LugwitToolDir = os.environ["LugwitToolDir"]

import Lugwit_Module as LM  # noqa: E402


lprint = LM.lprint
# lprint(f'sys.argv>>>>>>>>>>>>>>>{sys.argv},')
date_time_format = "%Y_%m_%d"
now = datetime.datetime.now()
formatted_date_time = now.strftime(date_time_format)
# syncErrorFile=fr'D:\temp\Log\SyncProject\{formatted_date_time}_sync_error_{LM.hostName}.log'
# sync_logFile=fr'A:\temp\Log\SyncProject\{formatted_date_time}_sync_{LM.hostName}.log'
syncErrorFile = "D:\TD_Depot\Log\p4_triggers_error.log"
sync_logFile = "D:\TD_Depot\Log\p4_triggers.log"

# 获取当前目录
curDir = os.path.dirname(os.path.realpath(__file__))
curDir_Path = Path(curDir)
par_dir = curDir_Path.parent

sys.path.insert(0, str(par_dir))
from lperforce import loginP4
from lperforce.P4LoginInfoModule import p4_loginInfo
p4 = loginP4.p4_login(userName=p4_loginInfo['project']['User'],
                      port=p4_loginInfo['project']['port'],
                      wsDir=p4_loginInfo['project']['clientRoot'])
p4.exception_level = 1

if len(sys.argv)==1:
    changeNum = 32836
else:
    changeNum=sys.argv[1]
# lprint(f'sys.argv>>>>>>>>>>>>>>>{sys.argv},{changeNum}')



sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')



changelist = p4.run_describe(changeNum)[0]
p4.charset = "utf8"  # 设置字符集
# lprint(changelist)

deletePermissionList={
        '制片':['hanxue','lvhangdong'],
        '模型':['gaoyanfeng','zhangqiang','wutiantian','yanjianxiang'],
        '特效':['tangziying','liuhao'],
        '绑定':['zhangzong'],
        '解算':['zhouhuafeng'],
        '灯光':['liujunlong'],  
        '地编':['lipengcheng','lipengchen'],
        '动画':['wangranran','dingwei','zenruijie','xinyuhai'],         
        '原画':['qiugaoxaing'],
        '影视后期':['wangzhong'],
        '编剧':['bianxiaozhen'],
        '研发':['liuzuo','zhangqunzhong','kongsiqi','zhaiwenpeng']
}

allowList=[y for x in deletePermissionList.values() for y in x]
# lprint (changelist)
user = changelist.get("user")
actionList = changelist.get("action",[])
depotFileList=changelist.get("depotFile",[])
deleteList=[]
if "delete" in actionList and user not in allowList:
    for i,x in enumerate(actionList):
        if x=="delete":
            deleteList.append(depotFileList[i])
    lprint("delete_list",deleteList)
    #lprint(deleteList)
    sys.exc_info(1)







