# coding:utf-8
import os,subprocess,sys,time,traceback
import Lugwit_Module as LM
lprint=LM.lprint
pyfile=LM.LugwitLibDir+ r'\\LPerforce\P4Lib.py'
pythonExe=r'D:\TD_Depot\Software\Lugwit_syncPlug\lugwit_insapp\python_env\lugwit_python.exe'
import re
from lperforce import loginP4
from lperforce.P4LoginInfoModule import p4_loginInfo


# 使用登录信息进行 P4 登录
p4 = loginP4.p4_login(userName=p4_loginInfo['project']['User'],
                      port=p4_loginInfo['project']['port'],
                      wsDir='H:/')
print(p4_loginInfo)

def checkOut(file,fileType='binary'):
    
    with open (LM.Lugwit_PluginPath+r'\Lugwit_plug\mayaPlug\l_scripts\Data\vscodePyhonEnv.txt','r') as f:
        env=f.read()
    env=eval(env)
    if isinstance(file,str):
        fileList=[file]
    else:
        fileList=file
    for i,file in enumerate(fileList):
        file=file.replace('\\','/')
        file=file.encode('gbk')
        fileList[i]=file
        if not (file.startswith('//') or file.startswith('E:') or file.startswith('e:')):
            fileList.remove(file)
    if not fileList:
        return
    ss=r'{} {} checkOut({})'.format(pythonExe,pyfile,str(fileList).replace(' ',''))
    lprint (ss,'------------')
    #subprocess.call(ss,cwd=r'e:\BUG_Project',env=env)
    return ss

# checkOut(r'e:\BUG_Project\addFolder\TestCleanFile.ma')
# sys.exit()
    
def getFile(file,forceGet=0,onlyGetMayaFile=0,fileType='',cleanFile=0):
    
    with open (LM.Lugwit_PluginPath+r'\Lugwit_plug\mayaPlug\l_scripts\Data\vscodePyhonEnv.txt','r') as f:
        env=f.read()
    env=eval(env)
    if isinstance(file,str):
        fileList=[file]
    else:
        fileList=file
    for i,file in enumerate(fileList):
        file=file.replace('\\','/')
        file=file.encode('gbk')
        fileList[i]=file
        if not (file.startswith('//') or file.startswith('E:') or file.startswith('e:')):
            fileList.remove(file)
    if not fileList:
        return
    ss=r'{} {} getFile({},forceGet=0,onlyGetMayaFile={})'.format(
        pythonExe,pyfile,str(fileList).replace(' ',''),onlyGetMayaFile)
    print (ss)
    #sys.exit(0)
    subprocess.call(ss,cwd=r'e:\BUG_Project',env=env)



def submitChange(file,description,submitOption='submitunchanged'):
    #file=file.encode('gbk')
    ss=u'{} {} submitChange --files \"{}\" --description \"{}\" --submitoption \"{}\"'.format(pythonExe,pyfile,file,description,submitOption)
    ss=ss.replace('\\\\','/')
    lprint(ss,)
    lprint(os.environ.get("P4USER"))
    subprocess.call(ss,env=os.environ)
    
# submitChange(r'e:\BUG_Project\addFolder\cc.txt',description=r'//172.21.1.2/P4Triggers/Triggers/exAniClip_wlxx_sc009_ani_v001_UE_comment.txt')
# sys.exit()
#'Z:\\plug_in/Python/Python37/python.exe Z:\\plug_in\\Lugwit_plug/Python/PythonLib/Perforce/P4Lib.py submitChange(u\\"E:/BUG_Project/B003_S78/Shot_work/UE/shot09/shot09_Cam_1001_1114.fbx\\",description=\\"//172.21.1.2/P4Triggers/Triggers/exAniClip_wlxx_sc009_ani_v001_UE_comment.txt\\",submitOption=\\"submitunchanged\\")'

if __name__=='__main__':
    pass
    file='E:/BUG_Project/B003_S78/Shot_work/UE/shot14/shot14_Cam_1001_1059.fbx'
    #checkOut(r'E:/BUG_Project/B024/Shot_work/UE/shot_03/B024_shot_03_1001_1050.mov')
    submitChange(r'h:\CCC\ss.txt',description='aa')
    #checkOut(r'e:\BUG_Project\B003_S78\Shot_work\UE\shot07\shot07_Cam_1001_1024.fbx')

