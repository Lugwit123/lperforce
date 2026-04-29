# -*- coding: utf-8 -*-

import os
import sys
import ctypes




from pathlib import Path
import traceback
print(11)
import get_error_path
print(11)
import unlockFile
print(unlockFile)
import codecs
import datetime
import time
import json
import io
import schedule


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

p4 = loginP4.p4_login(userName='OC2',
                      port='1999',
                      wsDir='H:/')
p4.exception_level = 1

def update_61_file():
    changeDepotFileList=p4.run_sync('-n','//H/WXXJDGD/...')
    changeDepotFileList_len=len(changeDepotFileList)
    print(changeDepotFileList[:2])
    syncList=[]
    st_syncTime=time.time()
    for index,FileInfo in enumerate(changeDepotFileList):
        try:
            DepotFile=FileInfo.get('depotFile')
            localPath :str  = os.path.normpath(p4.run_where(DepotFile)[0].get('path'))
            localPath=localPath.replace('\\','/')
            print (f'解锁文件{localPath}')
            unlockFile.unlock_file(localPath)
            print (f'解锁文件{localPath}完成')
            print (f'开始同步{ DepotFile},{index}/{changeDepotFileList_len}')
            p4.run_sync('-f',DepotFile)#这个适用于检查不正常的文件
            with codecs.open(sync_logFile,'a+',encoding='utf8') as f:
                json.dump(DepotFile+'\n',f,ensure_ascii=False,indent=4)
            syncList.append(DepotFile)
            print (f'同步{localPath}完成')
        except:
            error=traceback.format_exc()
            print(error)
            if 'up-to-date' in error:
                print (u'没有要更新的文件')
            elif '系统找不到指定' in error or \
                "failed to rename" in error or \
                'PermissionError' in error or \
                '拒绝访问' in error or \
                'clobber writable' in error:
                #lprint (f'文件更新出错:\n{error}')
                file_paths = get_error_path.extract_error_file_paths(error)
                print  (f'出错的文件{file_paths}')
                for file_path in file_paths:
                    os.system(f"cmd /c echo 解锁文件{file_path}")
                    try:
                        unlockFile.unlock_file(file_path)
                        if 'os.remove' in error:
                            os.remove(file_path)
                        p4.run_sync('-f',DepotFile)#这个适用于检查不正常的文件
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

    print (f'同步完成到G盘{len(syncList)}/{changeDepotFileList_len}个文件,花费时间{time.time()-st_syncTime}s')




print("开始定时同步文件...")
update_61_file()
# 定时任务，每分钟执行一次
schedule.every(30).minutes.do(update_61_file)

# 循环执行定时任务
while True:
    schedule.run_pending()  # 检查并运行挂起的任务
    time.sleep(1)  # 等待1秒钟再检查

