# coding:utf-8

import os,sys,re,time,subprocess
from imp import reload
os.environ['PYTHONIOENCODING'] = 'utf-8'
reload (sys)
print ('----------------------------',sys.argv,)
from Lugwit_Module import *
try:
    sys.setdefaultencoding('gbk')
except:
    pass


from Lugwit_Module.l_src import generalLib  as gl
#添加deadline目录
sys.path.append(LugwitPath+'/Python\PythonLib\L_DeadLine/DeadLinePy3')

#加载第三方模块
sys.path.append(LugwitPath+r'\mayaPlug\l_scripts\ThridLib')



def l_main(mayaFile):
    try:
        mayaFile=mayaFile
    except:
        mayaFile=r'e:\BUG_Project\B003_S78\Asset_work\sets\shot16_A\work\B003_S78_sets_ZL_preview.ma'


    if 'updateMayaFile' in sys.argv:
        getPath=gl.getRefFileListFromMa(mayaFile,syncFile=1,updateMayaFile=1)
    else:
        getPath=gl.getRefFileListFromMa(mayaFile,syncFile=1,updateMayaFile=0)
    print (u'获取结束,现在你可以关闭窗口')



