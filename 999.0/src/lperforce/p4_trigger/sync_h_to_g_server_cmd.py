# -*- coding: utf-8 -*-

import os
import sys
import ctypes

# def is_debugger_present():
#     """检查当前进程是否被调试"""
#     return ctypes.windll.kernel32.IsDebuggerPresent()

# if is_debugger_present():
#     sys.exit()
# else:
#     print("未检测到调试器。")


from pathlib import Path
import traceback
import get_error_path
import unlockFile
import codecs
import datetime
import time
import json
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 设置路径
LugwitToolDir = os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir + '/Lib')

import Lugwit_Module as LM  # noqa: E402
#lprint = LM.#lprint
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

p4 = loginP4.p4_login(userName='OC6',
                      port='192.168.110.26:1666',
                      wsDir='D:/H/')
p4.exception_level = 1
import subprocess
with open("D:/aaa.txt",'w') as f:
    json.dump(sys.argv, f, indent=2)


if len(sys.argv)==1:
    changeNum = 8794
else:
    try:
        changeNum=eval(sys.argv[1])
    except :
        changeNum=eval(sys.argv[2])



changelist = p4.run_describe(changeNum)[0]
p4.charset = "utf8"  # 设置字符集

# #lprint (changelist)
changeDepotFile=changelist.get("depotFile")
if not changeDepotFile:
    sys.exit(0)
# if '/test/' in str(changeDepotFile).lower():
#     sys.exit(0)
st_syncTime=time.time()
syncList = []

for DepotFile in changeDepotFile:
    try:
        p4.run_sync(DepotFile)#这个适用于检查不正常的文件
        localPath :str  = os.path.normpath(p4.run_where(DepotFile)[0].get('path'))
        localPath=localPath.replace('\\','/')
        unlockFile.unlock_file(localPath)
        #lprint (f"同步文件{DepotFile}")
        with codecs.open(sync_logFile,'a+',encoding='utf8') as f:
           json.dump(DepotFile+'\n',f,ensure_ascii=False,indent=4)
        syncList.append(DepotFile)
    except:
        error=traceback.format_exc()
        if 'up-to-date' in error:
            print (u'没有要更新的文件')
        elif '系统找不到指定' in error or "failed to rename" in error or 'PermissionError' in error or '拒绝访问' in error:
            #lprint (f'文件更新出错:\n{error}')
            file_paths = get_error_path.extract_error_file_paths(error)
            #lprint  (f'出错的文件{file_paths}')
            for file_path in file_paths:
                os.system(f"cmd /c echo 解锁文件{file_path}")
                try:
                    unlockFile.unlock_file(file_path)
                    if 'os.remove' in error:
                        os.remove(file_path)
                except:
                    traceback.print_exc()
                    #lprint(f"解锁文件失败")
                    with codecs.open(syncErrorFile,'a+',encoding='utf8') as f:
                        f.write(error+'\n')
        else:
            pass
            #lprint(f"文件更新出错,尝试处理，但是处理失败，原因是{traceback.format_exc()}")
            # with codecs.open(syncErrorFile,'a+',encoding='utf8') as f:
            #     f.write(error)

print (f'同步完成到G盘{len(syncList)}/{len(changeDepotFile)}个文件,花费时间{time.time()-st_syncTime}s')

