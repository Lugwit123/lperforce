# -*- coding: utf-8 -*-


import os
import sys
from pathlib import Path
import traceback
import get_error_path
import unlockFile
import codecs
import datetime
import time
import json
import subprocess

# 将控制台输出重定向到文件
# sys.stdout = open(r'D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\trayapp\Lib\LPerforce\p4_trigger\autoExFbx\output_log.log', 'w')
# 设置路径
LugwitToolDir = os.environ["LugwitToolDir"]

import Lugwit_Module as LM  # noqa: E402


lprint = LM.lprint
lprint(f'sys.argv>>>>>>>>>>>>>>>{sys.argv},')
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
# lprint (sys.argv,len(sys.argv))

if len(sys.argv)==1:
    changeNum = 8794
else:
    changeNum=sys.argv[1]
lprint(f'sys.argv>>>>>>>>>>>>>>>{sys.argv},{changeNum}')


import sys
import io


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 打印中文，确保不出现乱码
print("AAA这是中文输出")


changelist = p4.run_describe(changeNum)[0]
p4.charset = "utf8"  # 设置字符集
lprint(changelist)

# lprint (changelist)
changeDepotFile=changelist.get("depotFile")
# if not changeDepotFile:
#     sys.exit(0)
st_syncTime=time.time()
syncList = []
lprint(changeDepotFile)

lprint(os.path.exists(r'\\Oc2\a'))
if not os.path.exists(r'A:/'):
    subprocess.run(r'net use A: \\192.168.110.61\A', shell=True)
lprint(os.path.exists(r'\\192.168.110.61\A'))
lprint(os.path.exists(r'A:/'))
import getpass
lprint(getpass.getuser())
lprint( os.environ.get('USERDOMAIN'))
lprint( os.environ)
from L_DeadLine.DeadLinePy3 import deadline_submit
for DepotFile in changeDepotFile:
    localPath :str  = os.path.normpath(p4.run_where(DepotFile)[0].get('path'))
    localPath=localPath.replace('\\','/')
    if not os.path.exists(localPath):
        continue
    if not localPath.endswith('.ma'):
        continue
    lprint (f"导出Fbx{DepotFile}",localPath)
    CallPyd=r'D:\TD_Depot\plug_in\Lugwit_plug\mayaPlug\l_scripts\IOLib\CallPyd.py'
    AniExbatFile=u'A:/TD/RenderFarm/MayaToUE/P4Triggers/autoExFile/发送到MayaToUE_不带日志_强制全部重新导出并发送到Deadline.bat'
    os.environ['PATH']=r'D:\maya2020\Maya2020\bin;'+os.environ['PATH']
    if '.Assets' in localPath:
        taskType ='AssetTask'
        cmd=fr'mayapy.exe  {CallPyd} exTpose --mayaFile="{localPath}" --openNewFile=1'
        Comment="导出Tpose"
        if '_rig' not in localPath.lower():
            continue
    elif '.anima final' in localPath.lower():
        taskType = 'ShotTask'
        cmd=fr'{AniExbatFile} "{localPath}"'
        Comment="导出骨骼动画Fbx数据准备"
    else:
        continue
    output_dir=os.path.dirname(localPath).replace(r'D:/H','G:')
    batName = localPath.replace(':/','@').replace('/','@')
    taskFile=fr"A:\temp\Log\DealineLine_ExFile\{batName}.bat"
    with codecs.open(taskFile,'w',encoding='utf8') as f:
        f.write(cmd)
    deadline_submit.submit_commandline_job(
                    jobName=localPath,
                    priority=80,
                    Arguments=taskFile,
                    OutputDir=output_dir,
                    BatchName=taskType,
                    TaskTimeoutSeconds=6000,
                    # ScriptFilename=taskFile,
                    Comment=Comment,
                    ScriptFilename=taskFile,
                    EnvironmentKeyValue0=f"PATH={os.environ['PATH']}",
                )
        # subprocess.Popen(cmd, shell=True)
        # os.system(cmd)
    # except:
    #     error=traceback.format_exc()
#         if 'up-to-date' in error:
#             lprint (u'没有要更新的文件')
#         elif '系统找不到指定' in error or "failed to rename" in error or 'PermissionError' in error or '拒绝访问' in error:
#             lprint (f'文件更新出错:\n{error}')
#             file_paths = get_error_path.extract_error_file_paths(error)
#             lprint  (f'出错的文件{file_paths}')
#             for file_path in file_paths:
#                 os.system(f"cmd /c echo 解锁文件{file_path}")
#                 try:
#                     unlockFile.unlock_file(file_path)
#                     if 'os.remove' in error:
#                         os.remove(file_path)
#                 except:
#                     traceback.print_exc()
#                     lprint(f"解锁文件失败")
#                     with codecs.open(syncErrorFile,'a+',encoding='utf8') as f:
#                         f.write(error+'\n')
#         else:
#             lprint(f"文件更新出错,尝试处理，但是处理失败，原因是{traceback.format_exc()}")
#             # with codecs.open(syncErrorFile,'a+',encoding='utf8') as f:
#             #     f.write(error)

# lprint (f'同步完成到G盘{len(syncList)}/{len(changeDepotFile)}个文件,花费时间{time.time()-st_syncTime}s')

