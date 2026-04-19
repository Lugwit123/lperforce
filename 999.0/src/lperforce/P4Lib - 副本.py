# coding:utf-8
from operator import index
import os,sys,re,codecs,time
import time
import sys
import glob
from typing import List,Dict,Tuple,Union

LugwitToolDir=os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir+'/Lib') 
from Lugwit_Module import *
import Lugwit_Module as LM
# from Lugwit_Module.l_src.UILib.QTLib import PySideLib
from Lugwit_Module.l_src.UILib.QTLib import self_qss
from Lugwit_Module.l_src import l_subprocess

QT_API=os.environ.get('QT_API')
if not QT_API:
    QT_API='PySide6'
if 'maya' in sys.executable:
    QT_API='PyQt6'
print ('QT_API:',QT_API,__file__)


exec('from {} import QtWidgets'.format(QT_API))
exec('from {}  import QtCore'.format(QT_API))
exec('from {}  import QtGui'.format(QT_API))



import time,subprocess,getpass,traceback
import socket,traceback

if sys.version_info[0] == 3:
	from importlib import reload

USERPROFILE=os.environ['USERPROFILE']

#加载第三方模块
sys.path.append(LugwitPath+r'\mayaPlug\l_scripts\ThridLib')
sys.path.append(Lugwit_PluginPath+r'\Python\Python27\Lib\site-packages')


moduleFile=__file__
modeleDir=os.path.dirname(moduleFile)
sys.path.append(modeleDir)
os.environ['Lugwit_Debug']=''

if 'UnrealEditor.exe' in sys.executable:
    import unreal


class QWidget():#不要删除 这个有用
    pass


sys.path.append(Lugwit_PluginPath+r'\Python\Python{}\Lib\site-packages'.format(sys.version_info[0]+sys.version_info[1]))
sys.path.append(Lugwit_PluginPath+r'\Lugwit_plug\Python\PythonLib\UILib')



userName=getpass.getuser()
from pprint import pprint

# 因为导入p4模块并登陆需要一到两秒，尤其是在很多人登陆p4的时候
# 所以只在实际需要的时候才导入,这样能快一点打开UI
# 创建p4=P4_class()这个类之后,第一次运行p4.函数的时候,会创建一个全局变量p4,这里的p4就是
# P4模块里面的p4类了,而不是P4_class的实例,后面调用p4.函数的时候,就不会运行P4_class了
class P4_class():
    def __init__(self,clientRootDir=r''):
        self.clientRootDir=clientRootDir
    def __getattr__(self,name):
        import loginP4
        global p4
        p4=loginP4.p4_login(wsDir=self.clientRootDir)
        func=getattr(p4, name)
        return func
p4=P4_class()


import functools

def cache(func):
    cache_dict = {}
    @functools.wraps(func)
    def wrapper(*args):
        if args in cache_dict:
            return cache_dict[args]
        else:
            result = func(*args)
            cache_dict[args] = result
            return result
    return wrapper


def get_clientRootDir():
    return fetch_clent()._root.replace('\\','/')

@cache
def fetch_clent():
    return p4.fetch_client()








    
def depotFileToClientFile(depotFile):
    # lprint (locals(),p4)
    # lprint (fetch_clent())
    workspace_view=fetch_clent()["View"][0].split('... ',1)[1]
    # lprint (workspace_view)
    workspace_view=workspace_view.replace('...','')
    #lprint (workspace_view)
    clientFile=workspace_view.replace('//'+p4.client,get_clientRootDir())
    depotName=re.search(r'(//.+?/)',depotFile).group(1)
    clientFile=depotFile.replace(depotName,clientFile)
    clientFile=clientFile.replace('\\','/')
    # lprint ('depotFileToClientFile',depotFile,clientFile)
    return clientFile
# lprint(depotFileToClientFile('//B024/UE/'))
# sys.exit(0)

def clientFileToDepotFile(clientFile):
    clientFile=clientFile.replace('\\','/')
    result = p4.run_where(clientFile)
    DepotFile = result[0]['depotFile']
    #get_clientRootDir()可能已/结尾也可能不是,如果实在根目录的工作区,肯定是/结尾的,不过不是,很有可能不是/结尾
    DepotFile=DepotFile.replace('///','//')
    return DepotFile
# clientFile=r'E:/BUG_Project/B003_S78/Shot_work/UE/shot03/Fbx/shot03_props_CL25_AniWithGeo.fbx'
# lprint(clientFileToDepotFile(clientFile))
# sys.exit(0)



def list_all_files_and_size(rootdir):
    import os
    lprint (rootdir)
    _files_size = []
    if os.path.isfile(rootdir):
        _files_size.append({'fileSize':os.path.getsize(rootdir),'clientFile':rootdir})
        lprint (_files_size)
        return _files_size
    childs = os.walk(rootdir)
    for child in childs:
        for x in child[2]:
            file=child[0]+'/'+x
            _files_size.append({'fileSize':os.path.getsize(file),'clientFile':file})
    # lprint (_files_size)
    return _files_size

def convertPathToClientAndDepotFmt(file):
    #//B024/UE/
    lprint (locals())
    if file.endswith('/'):
            file=file[:-1]
    file=file.replace('/...','')
    file=file.replace('\\...','')
    file=file.replace('\\','/')
    lprint (file)
    if '//' in file:
        clientFile=depotFileToClientFile(file)
        depotFile=file
    else:
        depotFile=clientFileToDepotFile(file)
        clientFile=file
    if '.' not in depotFile:
        if '*' not in depotFile:
            if not os.path.isfile(clientFile):
                depotFile=depotFile+'/...'
    lprint (clientFile,depotFile)
    return clientFile,depotFile


def get_ws_depot_size_List(files,method='auto|p4|local',ws_depot_size_List=[]):#返回库文件,工作区文件,文件尺寸
    if not isinstance(files,list):
        files=[files]
    for file in files:  
        file=file.replace('\\\\','/').replace('\\','/') 
        if not file.startswith('//') :
            if not re.search(get_clientRootDir().replace('/',r'[/\\]'),file,flags=re.I):
                # print (u'文件{}不在工作区{}目录下'.format(file,get_clientRootDir()))
                continue
        fileInLocalDisk=0 
        clientFile,depotFile=convertPathToClientAndDepotFmt(file)
        try:
            # 这里使用服务器的模式
            if method == 'local':
                raise Exception('use local mode')
            run_sizes=p4.run_sizes(depotFile)
            # lprint('run_sizes>>>>',run_sizes)
            for i,run_size in enumerate(run_sizes):
                clientFile,depotFile=convertPathToClientAndDepotFmt(run_size['depotFile'])
                run_sizes[i]['clientFile']=clientFile

        except Exception as ex:
            # lprint (u'本地文件获取提交信息方式')
            run_sizes=list_all_files_and_size(clientFile)
            fileInLocalDisk=1
            for i,run_size in enumerate(run_sizes):
                clientFile,depotFile=convertPathToClientAndDepotFmt(run_size['clientFile'])
                run_sizes[i]['depotFile']=depotFile
                lprint (run_size)
        for run_size in run_sizes:
            size=str(int(run_size['fileSize'])/1024.0/1024)[:6]
            ws_depot_size_List.append((run_size['clientFile'],run_size['depotFile'],size,fileInLocalDisk))
    
    listLength=len(ws_depot_size_List)
    if listLength>10:
        pass
        lprint (u'ws_depot_size_List--结果-->>{}'.format(ws_depot_size_List[:9]))
    else:
        pass
        lprint (u'ws_depot_size_List--结果-->>{}'.format(ws_depot_size_List))
    return ws_depot_size_List

# get_ws_depot_size_List(r'e:\BUG_Project\addFolder\cc.txt',)
# sys.exit(0)

@try_exp
def checkOut(files,fileType='binary',onlyAddFile=0,UI=0):
    ws_depot_size_List=get_ws_depot_size_List(files)
    lprint (u'上传或者编辑文件{}'.format(ws_depot_size_List))
    
    if 'UI' in sys.argv or UI==1:
        process=PySideLib.L_ProgressDialog(title=u'签出文件',processList=ws_depot_size_List)
        
    for i,(wsFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
        
        if 'UI' in sys.argv or UI==1:
            process.index=i
            process.ProgressDialog_Procecss()
            
        #  签出之前先获取文件
        try:
            p4.run_sync(depotFile)
        except Exception as ex:
            pass
        
        if fileInLocalDisk:
            lprint(u'文件{}不在P4'.format(depotFile))
            #p4.run_add('-t',fileType,wsFile,)
            if 'UnrealEditor.exe' in sys.executable:
                unreal.SourceControl.mark_file_for_add(wsFile)
            else:
                p4.run_add(wsFile,)
            lprint (u'添加文件{}'.format(depotFile))
        if onlyAddFile:
            continue
        if not fileInLocalDisk :
            lprint (u'文件在P4,签出{}文件'.format(depotFile))
            getFile(depotFile)
            try:
                if 'UnrealEditor.exe' in sys.executable:
                    unreal.SourceControl.check_out_file(wsFile)
                else:
                    try:
                        p4.run_edit(depotFile,)
                    except:
                        p4.run_clean(depotFile,)
                        p4.run_sync(depotFile,)
                        p4.run_edit(depotFile,)
            except Exception as ex:
                print(traceback.print_exc())
                lprint ('run edit {} failed'.format(depotFile))
        # cmd_read='attrib -r {}'.format(wsFile)
        # os.system(cmd_read)
# checkOut(r'E:/BUG_Project/B003_S78/Shot_work/UE/shot06/Fbx/shot06_chars_wuji_AniWithGeo.fbx')
# sys.exit(0)


    
    
    
    
    
# 还原添加的文件
def revertAddFile(files='',UI=0):
    if not files:
        files=sys.argv[2:-1]
    ws_depot_size_List=get_ws_depot_size_List(files,method='local')
    lprint (u'上传或者编辑文件{}'.format(ws_depot_size_List))
    if 'UI' in sys.argv or UI==1:
        process=PySideLib.L_ProgressDialog(title=u'签出文件',processList=ws_depot_size_List)
        
    for i,(wsFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
        
        if 'UI' in sys.argv or UI==1:
            process.index=i
            process.ProgressDialog_Procecss()
        lprint('--depotFile--------------------------------',wsFile)
        try:
            file=p4.run_fstat(depotFile)[0]
            lprint('--------file',file)
            if 'action' in file:
                if file['action']=='add':
                    try:
                        p4.run_revert(file['depotFile'])
                    except:
                        pass
        except:
            pass

# revertAddFile(r'e:\BUG_Project\addFolder')
# sys.exit(0)

def check_file_locked(filepath):
    try:
        # 尝试以读写模式打开文件
        with open(filepath, 'a'):
            pass
        return False  # 文件未被占用
    except IOError:
        return True  # 文件被占用
    
@try_exp    
def getFile(files='',forceGet=0,onlyGetMayaFile=0,fileTypes=[],cleanFile=0,**kwargs):
    
    if 'cleanFile=1' in sys.argv:
        cleanFile=1
    elif 'cleanFile=0' in sys.argv:
        cleanFile=0
    ws_depot_size_List=get_ws_depot_size_List(files)
    lprint (locals())
    getList=[]
    if 'UI' in sys.argv :
        title=u'获取文件'
        if cleanFile:
            title+=u'(clean file)'
        process=PySideLib.L_ProgressDialog(title,processList=ws_depot_size_List)
    if isinstance(fileTypes, str):
        fileTypes=[fileTypes]
    lprint (u'获取文件类型{}'.format(fileTypes))
    for i,(wsFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
        if fileTypes:
            if wsFile.rsplit('.',1)[-1] not in fileTypes:
                lprint(u'非指定类型,不获取该文件{}'.format(wsFile))
                continue
        if onlyGetMayaFile:#如果不是maya文件不获取文件
            lprint(u'仅获取maya文件,不获取该文件')
            if not re.search('.ma|.ma' , wsFile):
                continue
        lprint (u'开始获取文件{}'.format(wsFile))
        startGetFileTime=time.time()

        if 'UI' in sys.argv :
            process.index=i*2
            process.ProgressDialog_Procecss()
            
        if not os.path.exists(wsFile):
            if re.search('.pyd',wsFile,flags=re.I):
                if check_file_locked(wsFile):
                    continue
            try:
                p4.run_revert(depotFile)  
                lprint (u'文件不存在{},revert文件'.format(depotFile))
            except :
                pass
            
            if not os.path.exists(wsFile):
                lprint (u'文件不存在')
                try:
                    p4.run_sync('-f',depotFile)
                    if os.path.exists(wsFile):
                        lprint (u'文件不存在,强制获取文件{depotFile}成功'.format(depotFile=depotFile))
                    else:
                        lprint (u'文件不存在,强制获取文件{depotFile}失败'.format(depotFile=depotFile))
                except :
                    p4.run_clean(depotFile)
                    lprint (u'文件不存在,强制获取文件失败,cleanFile成功')
                    lprint (e)
            if os.path.exists(wsFile):
                getList.append(wsFile)

        elif os.path.exists(wsFile):
            lprint ('文件存在'+wsFile)
            try:
                if cleanFile:
                    p4.run_clean(depotFile)
                    print ('cleanFile')
                else:
                    try:
                        p4.run_sync(depotFile)
                        lprint (u'文件存在,更新文件成功')
                    except Exception as e:
                        lprint (u'文件存在,更新文件失败,原因是{}'.format(e))
                        if 'clobber writable' in str(e):
                            p4.run_sync('-f',depotFile)
                            lprint (u'非只读文件,强制更新文件成功')
                        elif 'up-to-date' in str(e):
                            lprint (u'文件已经是最新版本')
                        #p4.run_sync('-f',depotFile)
                    
                getList.append(wsFile)
            except Exception as e:
                lprint (u'文件存在,更新文件失败,原因是{}'.format(e))

        lprint (u'获取文件{}花费时间{}'.format(wsFile,time.time()-startGetFileTime))  
    if 'UI' in sys.argv :
        process.close()
    lprint (u'获取文件列表{}'.format(getList))
    return getList

    return ws_depot_size_List

# getFile(r'd:/TD_Depot/plug_in/Lugwit_plug/icons\\maya.pn')
# sys.exit(0)

def revertFile(files=''):
    if 'SmartGetFile' in sys.argv:
        files=sys.argv[2:-2]
    ws_depot_size_List=get_ws_depot_size_List(files)
    
    if 'UI' in sys.argv :
        process=PySideLib.L_ProgressDialog(title=u'还原文件',processList=ws_depot_size_List)
        
    for i,(wsFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
        if 'UI' in sys.argv :
            process.index=i
            process.ProgressDialog_Procecss()
        
        try:
            p4.run_revert('-a',depotFile)
        except:
            pass
        
def convertUnicodeToText(files=r'd:/TD_Depot/plug_in/Lugwit_plug/mayaPlug/l_scripts/Rig',*args,**kwargs):
    lprint (locals())
    ws_depot_size_List=get_ws_depot_size_List(files)
    if 'UI' in kwargs :
        
        process=PySideLib.L_ProgressDialog(title=u'转换文件类型',processList=ws_depot_size_List)
        
    for i,(wsFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
        if 'UI' in kwargs:
            process.index=i
            process.ProgressDialog_Procecss()
        
        try:
            lprint (depotFile)
            run_files=p4.run_files(depotFile)
            '''
                        [
                {
                    "depotFile": "//TD_Depot/plug_in/Lugwit_plug/CodeEncryption/CodeEncryptionUI.py",
                    "rev": "3",
                    "change": "101",
                    "action": "edit",
                    "type": "unicode",
                    "time": "1691607230"
                }
            ]
            '''
            if 'unicode' in run_files[0]["type"]:
                p4.run_edit(depotFile)
                p4.run_reopen("-t", "text+lm", depotFile)
                p4.run_submit("-d", "Changed file type to text+l")
        except Exception as e:
            print (traceback.format_exc())
    lprint (run_files)
    sys.exit(app.exec_())
    
def convertExeDllPydTobinary(files=r'd:/TD_Depot/plug_in/Lugwit_plug/mayaPlug/l_scripts/Rig',*args,**kwargs):
    lprint (locals())
    ws_depot_size_List=get_ws_depot_size_List(files)
    if 'UI' in kwargs :
        process=PySideLib.L_ProgressDialog(title=u'转换文件类型',processList=ws_depot_size_List)
        
    for i,(wsFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
        if 'UI' in kwargs:
            process.index=i
            process.ProgressDialog_Procecss()
        
        try:
            lprint (depotFile)
            run_files=p4.run_files(depotFile)
            lprint (run_files)
            '''
                        [
                {
                    "depotFile": "//TD_Depot/plug_in/Lugwit_plug/CodeEncryption/CodeEncryptionUI.py",
                    "rev": "3",
                    "change": "101",
                    "action": "edit",
                    "type": "unicode",
                    "time": "1691607230"
                }
            ]
            '''
            if run_files[0]["depotFile"].endswith('.pyd')\
                or run_files[0]["depotFile"].endswith('.exe')\
                or run_files[0]["depotFile"].endswith('.png')\
                or run_files[0]["depotFile"].endswith('.ico')\
                or run_files[0]["depotFile"].endswith('.webp')\
                or run_files[0]["depotFile"].endswith('.jpg')\
                or run_files[0]["depotFile"].endswith('.dll'):
                p4.run_edit(depotFile)
                p4.run_reopen("-t", "binary+m", depotFile)
                p4.run_submit("-d", "Changed file type to text+l")
        except Exception as e:
            print (traceback.format_exc())
    sys.exit(app.exec_())

def SmartProcessFile(files=r'd:/TD_Depot/plug_in/Lugwit_plug/mayaPlug/l_scripts/Rig',*args,**kwargs):
    lprint (locals())
    ws_depot_size_List=get_ws_depot_size_List(files)
    lprint (ws_depot_size_List)
    if 'UI' in kwargs :
        process=PySideLib.L_ProgressDialog(title=u'转换文件类型',processList=ws_depot_size_List)
    for i,(wsFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
        if 'UI' in kwargs:
            process.index=i
            process.ProgressDialog_Procecss()
        # 获取服务器文件的信息
        file_info = p4.run_files(depotFile)
        lprint (file_info)
        # 从文件信息中提取修改日期（时间戳）
        server_modification_time = int(file_info[0]['time'])
        lprint (server_modification_time)
        # 获取本地文件的修改日期（时间戳）
        local_modification_time = int(os.path.getmtime(wsFile))
        lprint (local_modification_time)
        # 比较日期
        if local_modification_time < server_modification_time:
            try:
                p4.run_have(depotFile)
                p4.run_sync('f',depotFile) ;print (u'同步文件') # 将文件同步到最新版本
            except:
                p4.run_sync(depotFile)  ;print (u'强制同步文件') # 将文件同步到最新版本
        elif local_modification_time > server_modification_time:
            try:
                p4.run_have(depotFile)
                p4.run_edit(depotFile) ;print (u'编辑文件') # 签出文件进行编辑
            except:
                p4.run_flush(depotFile);print (u'flush文件')
        elif local_modification_time == server_modification_time:
            p4.run_flush(depotFile)  # 签出文件进行编辑  # 文件已是最新版本
    
# checkOut(r'E:/BUG_Project/B003_S78/Shot_work/UE/shot06/Fbx/shot06_chars_wuji_AniWithGeo.fbx')
# sys.exit(0)
        
def getSubmitFileList(files=['//B018/Asset_work/chars/Texture/NvDi/HuangZhuang_C.ma']):
    lprint (locals())
    # if os.path.isdir(files):
    #     files+='\\...'
    opened=p4.run_opened(files)
    submitFiles=[(x['depotFile'],depotFileToClientFile(x['depotFile'])) for x in opened]
    return submitFiles

def getChangeByFile(fileDepotFmt):
    fileChangeDict={}
    lprint (p4.client)
    openedFiles= p4.run_opened()
    for openedFile in openedFiles:
        depotFile=openedFile['depotFile']
        if fileDepotFmt==depotFile:
            changeNum=openedFile['change']
            if changeNum=='default':
                changeNum='new'
            return changeNum
    
def submitChange(files, 
                 description='descriptionFile|descriptionText',
                 submitoption='submitunchanged',method='auto',
                 callback=None):
    #sunmitOptionList=['revertunchanged','leaveunchanged','submitunchanged']
    aa=os.environ.get('Lugwit_Debug','')
    os.environ['Lugwit_Debug']='noprint'
    ws_depot_size_List=get_ws_depot_size_List(files,method,[])
    os.environ['Lugwit_Debug']=aa
    change = p4.fetch_change()
    change['Files'] = []
    change['Description'] = description
    changeNum = p4.save_change(change)[0].split()[1]
    submitList=[]
    changeList=[]
    descriptionFile=description
    st=time.time()
    if os.path.isfile(descriptionFile):
        with codecs.open(descriptionFile,'r',encoding='utf-8') as f:
            description=f.read()
            lprint ('description',description)
        description=re.split(u'exAniClip-->>|exTpose-->>',description,flags=re.I|re.M)[0]
        #lprint ("description.replace('\\u','\u'):",description.replace('\\u','\u').decode('utf8'))

    if not ws_depot_size_List:
        return
    
    for i,(wsFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
        #  提交之前先获取文件
        try:
            p4.run_sync(depotFile)
        except Exception as ex:
            pass
        if fileInLocalDisk:
            try:
                p4.run_add(wsFile)
            except Exception as ex:
                pass
        
        depotFile=str(depotFile)
        submitList.append(depotFile)
    try:
        p4.run_reopen("-c", changeNum, submitList)
    except Exception as ex:
        pass
    
    change = p4.fetch_change(changeNum)
    change._description = description
    p4.input=change
    # lprint (submitoption,change)
    p4.progress = callback
    p4.handler = callback
    try:
        p4.run_submit(change,'-f',submitoption,progress=callback,handler=callback)
    except Exception as e:
        lprint(u'提交时失败,原因是{}'.format(traceback.print_exc()))
    p4.progress = None
    p4.handler = None
    return changeNum
    try:
        # p4.run_submit('--parallel','-f',submitoption,change)
        p4.run_submit('-f',submitoption,change)
    except Exception as e:
        lprint(u'提交时失败,原因是{}'.format(traceback.print_exc()))
        return
        try:
            p4.connect()
            p4.run_resolve('-ay',submitList)
            lprint(u'提交时失败,尝试解决冲突')
        except Exception as e:
            lprint(traceback.print_exc())
        try:
            NewChangeNum=re.search('p4 submit -c (\d+)',str(e)).group(1)
            change._change=NewChangeNum
            lprint ('change',change)
            p4.run_submit('-f',submitoption,change)
            lprint(u'提交时失败,尝试解决冲突后再次提交成功')
        except Exception as e:
            lprint(u'提交时失败,尝试解决冲突后再次提交失败,原因是{}'.format(traceback.print_exc()))
            lprint(u'接下来尝试最后一次提交--{}--'.format(submitList))
            try:
                p4.connect()
                lprint (submitoption,change)
                p4.run_submit('-f',submitoption,change)
            except:
                pass
    return changeList

# submitChange(r'//addFolder/aa.txt',description='test')
# sys.exit()

def submitChange_Py2(file,description):
    pyfile='Z:/plug_in/Lugwit_plug/Python/PythonLib/Perforce/P4Lib.py'
    pythonExe='Z:/plug_in/Python/Python37/python.exe'
    file=file.encode('gbk')
    with open (Lugwit_PluginPath+r'\Lugwit_plug\mayaPlug\l_scripts\Data\vscodePyhonEnv.txt','r') as f:
        env=f.read()
    env=eval(env)
    ss=r'{} {} submitChange(u\"{}\",description=\"{}\")'.format(pythonExe,pyfile,file,description)
    lprint (ss,'------------')
    subprocess.call(ss,cwd=r'e:\BUG_Project',env=env)
    
# submitChange_Py2(r'e:\BUG_Project\B003_S78\Shot_work\UE\shot03\BG\shot03_sets_JieDao_Shot03_Low_AniWithGeo.fbx',
#     description=Lugwit_PluginPath+r'\Lugwit_plug\Python\PythonLib\Perforce\P4Triggers\Triggers\exAniClip_wlxx_sc003_lay_v003_comment.txt')
# sys.exit(0)

def modifyDescription(changeNum,description):
    change=p4.fetch_change(str(changeNum))
    lprint('change',change)
    change._description=description
    p4.input=change
    lprint('change',p4.input)
    p4.run_change('-f', '-i')
# modifyDescription(15537,'testA')
# sys.exit(0)

def getChangeInfoFromFile(file):
    fileInfo=p4.run_files(file)
    changeNum=fileInfo[0]['change']
    changeInfo=getChangeInfoFromChangeNum(changeNum,fileType='all',specifyFile=file)
    return changeInfo

def setWorkSpace(workPath='D:/TD_Depot'):
    lprint('create workspace')
    user_name = getpass.getuser()
    hostname = socket.gethostname()
    lprint('user_name:', user_name)
    p4.user = user_name
    workSpacePath = workPath
    clientName = 'BUGWS_{}_{}'.format(p4.user,hostname)
    lprint('clientName:', clientName)
    lprint('hostname:', hostname)
    p4.client = clientName
    client = p4.fetch_client(p4.client)
    if not os.path.exists(workSpacePath):
        os.makedirs(workSpacePath)
        client._root = workSpacePath
        client._submitoptions='revertunchanged'
        # client["View"] = ["//A_General_Library/... //{}}/... ".format(),]
        p4.save_client(client)
        # p4.run_sync()
        p4.disconnect
        lprint (u'创建工作区成功,请关闭此窗口')
    lprint (u'工作区路径--{},名称--{}已存在'.format(workSpacePath,clientName))


def findRfs(path):
    sys.path.append(python37Lib)
    asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()  # ??????asset
    # i=[0]#锟斤拷为python2锟斤拷没锟斤拷nonlocal锟斤拷锟斤拷,锟斤拷锟斤拷使锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟�
    # #nonlocal锟斤拷示锟斤拷锟节猴拷锟斤拷锟斤拷锟斤拷霞锟斤拷锟斤拷锟斤拷锟斤拷锟�
    path = [path]
    outPathList = [[]]
    genList = [[]]
    index[0] = 0

    def childrenNode(pathList=path):
        #nonlocal outPathList, genList, index
        index[0] += 1
        if index[0] > 100:
            return None

        ll = []
        for pl in pathList:

            if not str(pl).startswith('/Engine/'):
                genList[0] = asset_reg.get_dependencies(
                    pl, unreal.AssetRegistryDependencyOptions(1, 1))

                _clearList = [x for x in genList[0] if not str(
                    x).startswith('/Engine/')]
                ll += _clearList
                outPathList[0] += _clearList
        ll = list(set(ll))
        if ll:
            return childrenNode(ll)
        else:
            return None
    childrenNode()
    return list(set(outPathList))




def syncFile(depotFolder='//B024/UE/Content/Chr/WuQi/Mat/') :           
    os.environ['chcp'] = '65001'
    # os.environ['P4CONFIG'] = 'C:\\Users\\{}\\.p4qt\\.p4config'.format(userName)
    lprint ('同步p4库目录{}...#head')
    os.system('p4 sync {}...#head'.format(depotFolder))
    clientDir=depotFolder.replace('//','E:/Bug_Project/')
    clientDir=clientDir.replace('/','\\')[:-1]
    lprint (clientDir)
    #lprint (subprocess.call('p4 clean',cwd=clientDir,shell=True))
    lprint (u'获取工程文件目录')



def getChangeInfoFromChangeNum(changeNum,fileType='all',specifyFile=''):
    u"返回工作区文件,库文件和备注信息和提交日期,用户和更改列表,版本列表"
    changes=p4.run_describe('-S',changeNum)
    changeInfo=[]
    return_wsList=[]
    return_depotFileList=[]

    for change in changes:  

        if specifyFile:
            depotFile=clientFileToDepotFile(specifyFile)
            depotFileList=[depotFile] 
        else:
            depotFileList=change['depotFile']    

        client=change['client']
        user=change['user']
        revList=change['rev']
        timeArray = time.localtime(int(change['time']))
        Time=time.strftime('%Y-%m-%d %H:%M:%S',timeArray)
        desc=change['desc'].split('\n')[0]
        for depotFile in depotFileList:
            lprint (time.time()-st)
            wsFile=re.sub('//',get_clientRootDir(),depotFile)
            if fileType=='mayaFile':
                if '.ma' not in wsFile and '.mb' not in wsFile:
                    lprint ('不是maya文件')
                    return_depotFileList.append(depotFile)
                    return_wsList.append(wsFile)
                    continue
            else:
                return_depotFileList.append(depotFile)
                return_wsList.append(wsFile)
                
    changeInfo.append((return_wsList,return_depotFileList,desc,Time,user,changeNum,revList))
    return changeInfo
# specifyFile='e:\BUG_Project\B024\Shot_work\Ani\shot_03\B024_Ani_shot03.ma'  
# lprint(str(getChangeInfoFromChangeNum('15',fileType='all',specifyFile=specifyFile))[:600])
# sys.exit(0)

def openDirFromP4V(dir:str,**kwargs):
    lprint(locals())
    if 'dir'.endswith('...'):
        dir=dir.replace('...','')
        isDir=1
    else:
        dir = dir.replace('\\','/').rsplit('/',maxsplit=1)[0]
    if '//' in dir:
        dir=depotFileToClientFile(dir)
    if not os.path.exists(dir):
        os.makedirs(dir)
    os.startfile(dir)

# 或获取文件夹下的所有子文件夹并且创建文件夹   
def getFolders(dir='',**kwargs):
    lprint(locals())
    files=dir.replace('...','*')
    run_dirs:List[Dict[str, str]] =p4.run_dirs(files)
    lprint (run_dirs)
    dirs=[files.rsplit('/',1)[0]]
    if run_dirs:
        for x in run_dirs:
            dirs += x.values()
    lprint('dirs--------',dirs,)
    dirList=[[]]
    def getFolder_recursive(dirs):
        for _dir in dirs:
            _dir=depotFileToClientFile(_dir)
            dirList[0].append(_dir)
            run_dirs= p4.run_dirs(_dir+'/*')
            if not os.path.exists(_dir):
                os.makedirs(_dir)
            if run_dirs:
                subDir=[list(x.values())[0] for x in run_dirs]
                print('subDir',subDir)
                getFolder_recursive(subDir)
                
                
    getFolder_recursive(dirs)

# getFolders(files='//addFolder/*')

def getFileListInfo_InP4Dir(fileDir=r'e:\BUG_Project\B003_S78\Asset_work\chars\Rig',fileTypes=['abc']):
    fileDir=fileDir.replace('\\','/')
    try:
        fileInP4Dir=p4.run_files(fileDir+'/*')
        fileInP4Dir=[convertPathToClientAndDepotFmt(x['depotFile'])[0] for x in fileInP4Dir]
        if fileTypes:
            fileInP4Dir=[x for x in fileInP4Dir if x.rsplit('.',1)[1] in fileTypes]
        return fileInP4Dir
    except Exception as e:
        pass
    
    
def createEmpthFolderToP4(folderToCreate):
    lprint ('folderToCreate',folderToCreate)
    file=folderToCreate +'/.holder'
    if not os.path.exists(folderToCreate):
        os.makedirs(folderToCreate)
    try:
        p4.run_files(u'{}/...'.format(folderToCreate))
        lprint (u'文件夹{}不存在'.format(folderToCreate))
        try:
            print ('为空文件夹的.holder文件添加删除标记')
            p4.run_delete(file)
            # submitChange(file,u'添加空文件夹')
        except:
            lprint(traceback.print_exc())
    except Exception as ex:
        lprint(traceback.print_exc())
        lprint(u'----文件夹{}不存在------------,创建文件'.format(file))
        if not os.path.exists(file):
            with open (file,'w') as f:
                f.write('1')
        try:
            p4.run_add(file)
            submitChange(file,u'添加空文件夹')
            p4.run_delete(file)
            # submitChange(file,u'添加空文件夹')
            lprint (u'添加文件到P4')
        except:
            pass

    if os.path.exists(file):
        print ('删除临时文件')
        os.remove(file)
        
            
    


def switchHolderPermission(open=1):
    fetch_protect=p4.fetch_protect()
    Protections=fetch_protect.get('Protections')
    for i,protection in enumerate(Protections):
        if '.holder' in protection:
            if open==1:
                Protections[i]= f'super user {p4.user}  {LM.hostName} //.../.holder'
            else:
                Protections[i]= f'list user *  * -//.../.holder' 
    fetch_protect['Protections']=Protections
    p4.save_protect(fetch_protect)

def P4_uploadEmptyFolder(dir='',**kwargs):
    
    lprint(locals())
    try:
        if dir.startswith('//'):
            l_subprocess.ps_win.showMessageWin(title='警告',text='请选择工作区创建空目录')
        print ('开启创建文件夹权限')
        switchHolderPermission(open=1)
        # localDir=convertPathToClientAndDepotFmt(dir)[0]
        localDir=dir.replace('\\...','')
        lprint(localDir)
        index=1
        if os.path.isdir(localDir):
            localDir_children=glob.glob(localDir+'/*')
            # localDir_children.append(localDir)
            createEmpthFolderToP4(localDir)
            index+=1
            for child in localDir_children:
                if os.path.isdir(child):
                    P4_uploadEmptyFolder('{}'.format(child))  # 递归调用
    except Exception as ex:
        lprint(traceback.print_exc())
    print ('关闭创建空文件夹权限,创建文件夹成功')
    l_subprocess.ps_win.showMessageWin(title='提示',text=f'为你上传了{index}个空文件夹')
    switchHolderPermission(open=0)
    
    # glob.glob(localDir[0])
    # if not os.path.exists(localDir[0]):
    #     os.makedirs(localDir[0])
        


class P4CreateFolderUI(QtWidgets.QWidget):
    def __init__(self,selFolder):
        self.selFolder=selFolder

        super(P4CreateFolderUI, self).__init__()
        self.setFixedWidth(490)
        self.setWindowTitle(u'添加空文件夹_{}'.format(self.selFolder))
        self.topLay = QtWidgets.QVBoxLayout()
        self.AssetUI()
        self.shotUI()
        createBtn = QtWidgets.QPushButton(u'创建')
        createBtn.clicked.connect(self.createFolder)
        createBtn.setFixedHeight(40)
        self.topLay.addWidget(createBtn)
        self.setLayout(self.topLay)
        #self.setStyleSheet(style_sheet)
        self.setWindowFlags(QtGui.Qt.WindowType.WindowMinimizeButtonHint |   # 使能最小化按钮
                    QtGui.Qt.WindowType.WindowCloseButtonHint |      # 使能关闭按钮
                    QtGui.Qt.WindowType.WindowStaysOnTopHint) 
        
    def AssetUI(self):
        self.assetGB=QtWidgets.QGroupBox(u'资产文件夹创建')
        self.assetGB.setCheckable(1)
        
        assetLay = QtWidgets.QVBoxLayout() 
        self.assetGB.setLayout(assetLay)
        
        assetTypeLay=QtWidgets.QVBoxLayout()
        self.char_prop_setLay=QtWidgets.QHBoxLayout()
        rig_tx_fxLay=QtWidgets.QHBoxLayout()

        self.char_prop_setGB = QtWidgets.QGroupBox(u'您要创建角色,道具抑或道具')
        charsRB=QtWidgets.QRadioButton('chars')
        charsRB.setChecked(True)
        propsRB=QtWidgets.QRadioButton('props')
        setsRB=QtWidgets.QRadioButton('sets')
        self.char_prop_setLay.addWidget(charsRB)
        self.char_prop_setLay.addWidget(propsRB)
        self.char_prop_setLay.addWidget(setsRB)
        self.char_prop_setGB.setLayout(self.char_prop_setLay)
        
        self.rig_tx_fxGB = QtWidgets.QGroupBox(u'您要创建模型,材质,绑定还是特效')
        modCB=QtWidgets.QCheckBox('Mod')
        modCB.setChecked(1)
        mtxCB=QtWidgets.QCheckBox('Texture')
        mtxCB.setChecked(1)
        rigCB=QtWidgets.QCheckBox('Rig')
        rigCB.setChecked(1)
        fxCB=QtWidgets.QCheckBox('Fx')
        fxCB.setChecked(0)
        InfoCB=QtWidgets.QCheckBox('Info')
        InfoCB.setChecked(0)
        TexCB=QtWidgets.QCheckBox('Tex')
        TexCB.setChecked(0)
        CFXCB=QtWidgets.QCheckBox('Cfx')
        CFXCB.setChecked(0)
        XgenCB=QtWidgets.QCheckBox('Xgen')
        XgenCB.setChecked(0)
        rig_tx_fxLay.addWidget(modCB)
        rig_tx_fxLay.addWidget(mtxCB)
        rig_tx_fxLay.addWidget(rigCB)
        rig_tx_fxLay.addWidget(fxCB)
        rig_tx_fxLay.addWidget(InfoCB)
        rig_tx_fxLay.addWidget(TexCB)
        rig_tx_fxLay.addWidget(CFXCB)
        rig_tx_fxLay.addWidget(XgenCB)
        self.rig_tx_fxGB.setLayout(rig_tx_fxLay)
        
        imageLay=QtWidgets.QVBoxLayout()
        self.imageGB = QtWidgets.QGroupBox(u'请选择你要在资产文件夹下创建的文件夹(仅在Texture文件夹下创建)')
        sourceimagesCB=QtWidgets.QCheckBox('sourceimages')
        sourceimagesCB.setChecked(1)
        xgenCB=QtWidgets.QCheckBox('xgen')
        xgenCB.setChecked(1)
        imageLay.addWidget(sourceimagesCB)
        imageLay.addWidget(xgenCB)
        self.imageGB.setLayout(imageLay)
        
        assetNameLay=QtWidgets.QVBoxLayout()
        assetNameGB = QtWidgets.QGroupBox(u'请设置资产名称(多个资产名称用空格隔开,如"AA BB"会创建两个资产)')
        self.assetNameField=QtWidgets.QLineEdit('')
        assetNameLay.addWidget(self.assetNameField)
        assetNameGB.setLayout(assetNameLay)

        
        assetTypeLay.addWidget(self.char_prop_setGB)
        assetTypeLay.addWidget(self.rig_tx_fxGB)
        assetLay.addLayout(assetTypeLay)
        assetLay.addWidget(self.imageGB )
        assetLay.addWidget(assetNameGB)

        self.topLay.addWidget(self.assetGB)
        
    def shotUI(self):
        shotLay = QtWidgets.QVBoxLayout() 
        self.shotGB = QtWidgets.QGroupBox(u'镜头文件夹创建')
        self.shotGB.setCheckable(1)
        self.shotGB.setChecked(False)
        self.shotGB.setLayout(shotLay)
        
        stEndLay=QtWidgets.QHBoxLayout()
        shotRangeSelectGB = QtWidgets.QGroupBox(u'请选择你要创建的镜头文件夹')
        shotNameList=['shot{}'.format(str(i).zfill(2)) for i in range(1,31)]
        self.startShotCB=QtWidgets.QComboBox()
        self.startShotCB.addItems(shotNameList)
        self.startShotCB.currentIndexChanged.connect(self.setShotsToCreate)
        self.endShotCB=QtWidgets.QComboBox()
        self.endShotCB.addItems(shotNameList)
        self.endShotCB.currentIndexChanged.connect(self.setShotsToCreate)
        stEndLay.addWidget(self.startShotCB,8)
        stEndLay.addWidget(QtWidgets.QLabel('到'),1)
        stEndLay.addWidget(self.endShotCB,8)
        shotRangeSelectGB.setLayout(stEndLay)
        
        # 创建镜头文件夹下的文件夹
        folderInShotList=['Layout','Animation','Lighting','Comp','Fx','Sim','Pr','AE']
        shotFolderGB = QtWidgets.QGroupBox(u'请选择你要在镜头文件夹下创建的文件夹')
        shotFolderLay=QtWidgets.QHBoxLayout()
        shotFolderGB.setLayout(shotFolderLay)
        names=locals()
        self.folderInShotWidgetList=[]
        for i,shot in enumerate(folderInShotList):
            names[shot]=QtWidgets.QCheckBox(shot)
            self.folderInShotWidgetList.append(names[shot])
            names[shot].setToolTip(shot)
            shotFolderLay.addWidget(names[shot])
            if i<4:
                names[shot].setChecked(1)
            #names[shot].setFixedWidth(len(shot)*5)

        resultLay=QtWidgets.QHBoxLayout()
        resultGB = QtWidgets.QGroupBox(u'创建的镜头文件夹为')
        self.shotsToCreateLineEdit=QtWidgets.QLineEdit()
        resultLay.addWidget(self.shotsToCreateLineEdit)
        resultGB.setLayout(resultLay)
        self.setShotsToCreate()

        shotLay.addWidget(shotRangeSelectGB)
        shotLay.addWidget(shotFolderGB)
        shotLay.addWidget(resultGB)

        self.topLay.addWidget(self.shotGB)
        
    def setShotsToCreate(self):
        self.shotsToCreateLineEdit.setText(self.startShotCB.currentText()+'-'+self.endShotCB.currentText())
    
    def createAssetFolder(self):
        if self.assetGB.isChecked():
            lprint (self.assetGB.isChecked())
            char_prop_setRBs=self.char_prop_setGB.findChildren(QtWidgets.QRadioButton)
            for char_prop_setRB in char_prop_setRBs:
                if char_prop_setRB.isChecked():
                    char_prop_set=char_prop_setRB.text()
                    break
            rig_tx_fxCBs=self.rig_tx_fxGB.findChildren(QtWidgets.QCheckBox)
            folderInAssetFolderList=[]
            for rig_tx_fxCB in rig_tx_fxCBs:
                if rig_tx_fxCB.isChecked():
                    folderInAssetFolderList.append(rig_tx_fxCB.text())
                    
            imageRBs=self.imageGB.findChildren(QtWidgets.QCheckBox)
            imageFolders=[]
            for imageRB in imageRBs: #RB QRadioButton
                if imageRB.isChecked():
                    image=imageRB.text()
                    imageFolders.append(image)

            assetName=self.assetNameField.text()
            if  not assetName:
                return
            assetNameList=assetName.split(' ')

            for rig_tx_fx_folder in folderInAssetFolderList:
                for imageFolder in imageFolders:
                    lprint(rig_tx_fx_folder,imageFolder)
                    for assetName in assetNameList:
                        if rig_tx_fx_folder=='Texture':
                            folderToCreate='{}/Asset_work/{}/{}/{}/{}'.\
                            format(self.selFolder,char_prop_set,assetName,rig_tx_fx_folder,imageFolder)
                        else:
                            folderToCreate='{}/Asset_work/{}/{}/{}'.\
                            format(self.selFolder,char_prop_set,assetName,rig_tx_fx_folder)
                        lprint(folderToCreate)
                        createEmpthFolderToP4(folderToCreate)


    def createShotFolder(self):
        if self.shotGB.isChecked(): 
            shotsToCreateLineEdit_text=self.shotsToCreateLineEdit.text()
            startShot,endShot=shotsToCreateLineEdit_text.split('-') 
            startShot=re.search('\d.+',startShot).group()
            endShot=re.search('\d.+',endShot).group()
            lprint ('startShot',startShot)
            lprint ('endShot',endShot)
            for i in range(int (startShot),int(endShot)+1):
                for folderInShotWidget in self.folderInShotWidgetList:
                    if folderInShotWidget.isChecked():
                        folderToCreate='{}/Shot_work/{}/shot{}'.format(self.selFolder,folderInShotWidget.text(),str(i).zfill(2))
                        createEmpthFolderToP4(folderToCreate)

                
    def createFolder(self,folder):
        lprint (u'创建资产文件夹')
        self.createAssetFolder()
        lprint (u'创建镜头文件夹')
        self.createShotFolder()

        
def show_P4CreateFolderUI(dir="",**kwargs):
    try:
        switchHolderPermission(open=1)
        Folder=dir
        clientFile,depotFile=convertPathToClientAndDepotFmt(Folder)
        Folder=clientFile.replace('\\','/')
        Folder='/'.join(Folder.split('/')[:3])
        lprint (Folder)

        app = QtWidgets.QApplication.instance()
        if not app:
            app=QtWidgets.QApplication(sys.argv)
        win = P4CreateFolderUI( Folder)  # 进入消息循环
        win.show()
        try:
            exec('sys.exit(app.exec())')
        except:
            pass
        switchHolderPermission(open=0)
        lprint(u'--------关闭权限--------')
    except Exception as ex:
        lprint(traceback.print_exc())
        switchHolderPermission(open=0)
# show_P4CreateFolderUI()
# sys.exit(0)

def rollBack(*args):
    pprint (sys.argv)
    
def rv_requence(*args):
    sys.argv=['//B017_6RW/Shot_work/Animation/...','//B017_6RW/Shot_work/Animation/...','//B017_6RW/Shot_work/Animation/...','//B017_6RW/Shot_work/Animation/...']
    ws_depot_size_List=getFile(sys.argv[2:-1],fileType='mov_avi')
    print ('ws_depot_size_List->>',ws_depot_size_List)
    # wsFileList=[x[0] for x in ws_depot_size_List if x[0].endswith('.mov')]
    # wsFileList.sort()
    # lprint('wsFileList=========',wsFileList)
    # cmdStr=r'"C:\Program Files\rv_player\bin\rv.exe" '+' '.join(wsFileList)
    # lprint ('cmdStr',cmdStr)
    # subprocess.Popen(cmdStr,shell=True)
# rv_requence()
# sys.exit()

def close_Protections(*args):
    fetch_protect=p4.fetch_protect()
    Protections=fetch_protect.get('Protections')
    lprint(Protections)
    aa=["B003_5_XJQX(测试)","B003_S67","B003_S82","B003_U14_4","B003_U14","B003_U17_3","B003_U17_4","B003_U17_5","B003_U18","B003_U22","B003_U25","B003_U30_C1","B003_U31","B003_U32_G86","B003_U34","B009_6","B016_ZZQ","B017_5(RO测试)","B017_8","B017_WLHB(测试)","B018","B021_TOPJOY"]
    for a in aa:
        a='list user * * -//{}...'.format(a)
        lprint(a)
        Protections.append(a)
    p4.save_protect(fetch_protect)   
    
    
if __name__=='__main__'  :
    pass
