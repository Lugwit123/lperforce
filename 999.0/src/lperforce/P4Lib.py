# coding:utf-8

import os,sys,re,codecs,time,shutil
sys.path.append(os.path.dirname(__file__))
from tqdm import tqdm
import time
import sys
import glob
from typing import List,Dict,Tuple,Union
import multiprocessing
from perforce_datatype.datatype import RunFstat
import json
from importlib import reload
import tempfile


LugwitToolDir=os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir+'/Lib') 
from Lugwit_Module import *
import Lugwit_Module as LM
from Lugwit_Module.l_src.UILib.QTLib import PySideLib
reload (PySideLib)
from Lugwit_Module.l_src.UILib.QTLib import self_qss
from Lugwit_Module.l_src import l_subprocess

curdir=os.path.dirname(__file__)

QT_API=os.environ.get('QT_API')
if not QT_API:
    QT_API='PySide6'
if 'maya' in sys.executable:
    QT_API='PyQt6'
print ('QT_API:',QT_API,__file__)


sys.path.append(r'D:\\TD_Depot\\Software\\LUGWIT~1\\LUGWIT~1\\trayapp/Lib\\Lugwit_Module\\l_src\\l_qtpy{}'.format(sys.version_info.major))

from qtpy.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
    QStatusBar, QSizePolicy, QDialog, QSpacerItem,QLabel,QWidget,QComboBox,QProgressDialog,
    QSpinBox)
from qtpy.QtCore import Qt, QTimer, QEvent, QCoreApplication, QRect,QPoint,Signal,QThread

from qtpy.QtCore import Qt, QMimeData, QEvent, QPoint,QObject
from qtpy.QtGui import QDragEnterEvent, QDropEvent


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
import loginP4
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


from enum import Enum

class P4OperationAction(Enum):
    SUBMIT = "submit"    # 提交文件
    DELETE = "delete"    # 删除文件
    CHECKOUT = "checkout" # 迁出文件
    ADD = "add"          # 添加文件
    GET = "get"          # 获取文件





    
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
    print ('rootdir>>>>>>',rootdir)
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
    lprint (_files_size)
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

def get_file_sizes(depot_files):
    try:
        sizes_results = p4.run_sizes(*depot_files)
        return {result['depotFile']: result.get('fileSize', -1) for result in sizes_results}
    except Exception as e:
        lprint(f"Error fetching sizes for {depot_files}: {e}")
        return {file: -1 for file in depot_files}
    
@LM.try_exp
def get_ws_depot_size_List(files,method='auto|p4|local',ws_depot_size_List=[],
                           include_deleteFile=False,action_param=P4OperationAction.GET):
    if not isinstance(files,list):
        files=[files]
    # lprint (locals())
    getFileInfo_Start=time.time()
    tempList=set()
    print ("修改本地不存在但标记为本地存在的文件")
    # p4.exception_level = 0
    # files_filterList=[]
    file_haves_in_local = []
    try:
        # 如果显示了回收站的文件,在被回收的文件上运行p4.run_have会报错,
        # 文件不在工作区
        file_haves_in_local = p4.run_have(files)  # 获取目录下所有文件的信息
    except Exception as e:
        if  '- file(s) not on client'.lower() in str(e):
            print ("\n\n请检查你是否在获取回收站的文件,请切换到>>>\"隐藏已删除的仓库文件\",否则,请忽略这个信息")
            print (f"错误信息如下\n{str(e)[:200]}...")
            # sys.exit(0)

    try:
        lprint (file_haves_in_local)
    except:
        ("这里的错误可能是UnicodeEncodeError:'gbk' codec can't encode character '\uad6c' in position 44914500: illegal multibyte sequence")
        file_haves_in_local = []
    
    fileNoExist_index=0
    noExists=set()
    if file_haves_in_local:
        for file in tqdm(file_haves_in_local, desc="修复文件状态",ncols=100):
            localFile=file["path"]
            if not os.path.exists(file["path"]):
                #cmd = file['depotFile']+'#0'
                try:
                    p4.run_revert('-k',file['depotFile'])
                except:
                    pass
                p4.run_sync('-f',  file['depotFile']+'#0')
                # p4.run_revert('-k',f"{depotFile}")
                # p4.run_sync('-f',f"{depotFile}#0")
                fileNoExist_index+=1
                noExists.add(localFile)
        print (f"修改本地不存在但标记为本地存在的文件一共有{fileNoExist_index}个")
        if fileNoExist_index:
            lprint (noExists)
    fileList = []
    try:
        #fileList=p4.run_files(files) 这个不包含未添加的文件
        fileList=p4.run_opened(files)
    except Exception as e:
        if 'no such file(s)' in str(e):
            print ("没有要获取的文件")
            return None
        else:
            print ('capitalize')
    # print (len(fileList))
    callback=loginP4.MyProgressHandler(p4cmd='fstat',file_count=len(fileList))
    print ("获取文件信息中...");run_fstat_starttime=time.time()

    # Ol的意思是输出文件信息 ,Op的意思是输出本地文件路径
    file_details_in_depot :List[RunFstat] = \
                    p4.run_fstat(
                            '-Ol',
                            '-Op',
                            '-Or',
                            files,
                            progress=callback,
                            handler=callback)
    print (f"run_fstat花费时间{time.time()-run_fstat_starttime}s")

    # reconcile_preview = p4.run_reconcile('-mn',files) # type: ignore
    # file_details_in_local =[]

    # for x in reconcile_preview:
    #     if isinstance(x,str):
    #         continue
    #     if x.get('action')=="add":
    #         file_details_in_local.append(x)

    ''' run_reconcile 返回结果
    [
        {
            "action": "add",
            "clientFile": "H:/CCC\\本地文件.txt",
            "depotFile": "//H/CCC/本地文件.txt",
            "type": "text+l",
            "workRev": "1"
        }
    ]
    }
        run_fstat 返回结果
        {
        "clientFile": "H:/DPCQ\\1.制作规范\\1.模型制作规范\\角色灯光\\hdri-31_color.tx",
        "depotFile": "//H/DPCQ/1.制作规范/1.模型制作规范/角色灯光/hdri-31_color.tx",
        "headAction": "add",
        "headChange": "101",
        "headModTime": "1645898423",
        "haveRev": "1", # NOTE : 本地版本,
        "headRev": "2", # NOTE : 仓库最新版本,
        "headTime": "1714751764",
        "headType": "binary",
        "isMapped": ""
    },
    '''

    totalSizeNeedToDownload=0
    lprint (file_details_in_depot)
    new_files=[]
    for file_detail in tqdm(file_details_in_depot, desc="获取文件信息", mininterval=0.1,ncols=100):  
        # clientFile,depotFile = file_detail.get('clientFile',''),file_detail.get('depotFile','')
        headAction = file_detail.get('headAction','')
        action = file_detail.get('action','')
        actionList = ['add','edit',"integrate",'branch'] 
        if headAction in actionList or action in actionList:
            try:
                file_size=file_detail.get("fileSize",-1)
                file_size=int( file_size)
                file_size=round(file_size/1024.0/1024,3)
                file_detail['fileSize'] = file_size
                lprint (file_detail.get("haveRev" , file_detail.get("headRev")))
                lprint (action_param,P4OperationAction.SUBMIT)
                if not  file_detail.get("headRev"):# 新文件,在本地
                    new_files.append(file_detail)
                    totalSizeNeedToDownload += file_size
                elif action_param==P4OperationAction.SUBMIT:
                    totalSizeNeedToDownload += file_size
                    new_files.append(file_detail)
                elif action_param==P4OperationAction.GET:
                    if file_detail.get("haveRev") != file_detail.get("headRev"):
                        totalSizeNeedToDownload += file_size
                        new_files.append(file_detail)
                    
            except Exception as e:
                file_detail['fileSize'] = -1
                print (e)

    listLength=len(file_details_in_depot)
    # lprint (new_files)
    if listLength>10:
        lprint (u'ws_depot_size_List--结果-->>{}'.format(new_files[:9]))
    else:
        lprint (u'ws_depot_size_List--结果-->>{}'.format(new_files))
    print (f"获取文件信息花费时间{time.time()-getFileInfo_Start}秒")
    return new_files,totalSizeNeedToDownload

# get_ws_depot_size_List(r'e:\BUG_Project\addFolder\cc.txt',)
# sys.exit(0)
@try_exp
def getNeedToConcileFile(p4,files,ignore_files=[]):
    try:
        lprint (files)
        temp_ignore_file = "temp_ignore.txt"
        with open(temp_ignore_file, "w") as f:
            f.write("\n".join(ignore_files))
        os.environ['P4IGNORE'] = temp_ignore_file
        dict_list = p4.run_reconcile('-emn',files)
        lprint (dict_list)
        result = [RunFstat(item) for item in dict_list if isinstance(item,dict)]
        print (result)
        return result
    except Exception as e:
        error_files = []
        for warning in e.warnings:
            if "can't edit exclusive file already opened" in warning:
                # 提取文件名
                start_index = warning.find("//")
                end_index = warning.find(" - can't edit exclusive file already opened")
                if start_index != -1 and end_index != -1:
                    error_file = warning[start_index:end_index]
                    error_files.append(error_file)
        if error_files:
            result = [RunFstat(item) for item in p4.run_fstat(error_files) if isinstance(item,dict)]
            print(result)
            return result
        if 'no file(s) to reconcile' in str(e).lower():
            print ('没有文件冲突')
        elif 'unknown command' in str(e).lower():
            pass
        else:
            traceback.print_exc()
        return []





@try_exp
def checkOut_old(files,fileType='binary',onlyAddFile=0,UI=0):
    lprint (u'开始签出文件{}'.format(files))
    ws_depot_size_List=get_ws_depot_size_List(files)
    lprint (u'上传或者编辑文件{}'.format(ws_depot_size_List))
    if 'UI' in sys.argv or UI==1:
        process=PySideLib.L_ProgressDialog(title=u'签出文件',processList=ws_depot_size_List)
        
    for i,(file_detail) in enumerate(ws_depot_size_List):
        
        if 'UI' in sys.argv or UI==1:
            process.index=i
            process.ProgressDialog_Procecss()
        depotFile = file_detail.get('depotFile','')  
        #  签出之前先获取文件
        try:
            p4.run_sync(depotFile)
        except Exception as ex:
            pass
        
        if fileInLocalDisk:
            lprint(u'文件{}不在P4'.format(depotFile))
            #p4.run_add('-t',fileType,clientFile,)
            if 'UnrealEditor.exe' in sys.executable:
                unreal.SourceControl.mark_file_for_add(clientFile)
            else:
                p4.run_add(clientFile,)
            lprint (u'添加文件{}'.format(depotFile))
        if onlyAddFile:
            continue
        if not fileInLocalDisk :
            lprint (u'文件在P4,签出{}文件'.format(depotFile))
            getFile(depotFile)
            try:
                if 'UnrealEditor.exe' in sys.executable:
                    unreal.SourceControl.check_out_file(clientFile)
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
        # cmd_read='attrib -r {}'.format(clientFile)
        # os.system(cmd_read)
# checkOut(r'E:/BUG_Project/B003_S78/Shot_work/UE/shot06/Fbx/shot06_chars_wuji_AniWithGeo.fbx')
# sys.exit(0)


# def checkOut(p4,files,newCheckNum=True,commit=''): -> int
#     for file in files:
#         if newCheckNum==True and check_file_locked(file):
#             print (u'文件{}被占用'.format(file))
#             continue
#         try:
#             p4.run_sync('-f',file)
#             lprint ('签出文件{}成功'.format(file))
#         except Exception as e:
#             traceback.print_exc()
#     try:
#         p4.run_edit(depotFile,)
#     except:
#         p4.run_clean(depotFile,
    
    
    
# 还原添加的文件
def revertAddFile(files='',UI=0):
    if not files:
        files=sys.argv[2:-1]
    ws_depot_size_List=get_ws_depot_size_List(files,method='local')
    lprint (u'上传或者编辑文件{}'.format(ws_depot_size_List))
    if 'UI' in sys.argv or UI==1:
        process=PySideLib.L_ProgressDialog(title=u'签出文件',processList=ws_depot_size_List)
        
    for i,(clientFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
        
        if 'UI' in sys.argv or UI==1:
            process.index=i
            process.ProgressDialog_Procecss()
        lprint('--depotFile--------------------------------',clientFile)
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


def smartCheckoutFile(files='',forceGet=0,onlyGetMayaFile=0,fileTypes=[],cleanFile=0,**kwargs):
    if isinstance (files,str):
        files=[files]
    # 加上tdqm
    for file in tqdm(files, desc="处理文件", ncols=100):
        try:
            p4.run_flush(file)
        except:
            pass
        try:
            p4.run_edit(file)
        except:
            pass
        try:
            p4.run_add(file)
        except:
            pass
    revertFile_New(files)


@try_exp
def getFile(files='',forceGet=0,onlyGetMayaFile=0,fileTypes=[],cleanFile=0,**kwargs):
    print(f'获取{len(files)}个文件')
    # print ('函数参数',locals())
    callback=loginP4.MyProgressHandler()
    # p4.exception_level = 1
    if cleanFile == "0":
        cleanFile=False
    elif cleanFile == "1":
        cleanFile=True
    # lprint (sys.executable,curdir)
    #执行获取文件时先检查有没有要解锁的文件
    print ("执行获取文件时先检查有没有要解锁的文件")
    if isinstance (files,str):
        files=[files]
    # checkFiles=p4.run_files(files)
    # print (checkFiles[:3])
    # checkFiles = [x.get('depotFile') for x in checkFiles if 'depotFile' in x]
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        json.dump(files, temp_file)
        temp_file_path = temp_file.name
    process=subprocess.run([sys.executable,f'{curdir}/find_lock_file.py','--recordOnlockFile',temp_file_path])
    if process.returncode==666:
        print ("程序退出,请关闭窗口")
        os._exit(0)
    # sys.exit(1)
    ws_depot_size_List = []
    totalSize = 0
    try:
        ws_depot_size_List,totalSize=get_ws_depot_size_List(files)
    except Exception as ex:
        if 'not enough values to unpack' in str(ex):
            print ("没有要获取的文件")
    getList=[];concileFiles=[]
    if isinstance(fileTypes,str):
        fileTypes=[fileTypes]
    lprint (u'获取文件类型{}'.format(fileTypes))
    ws_depot_size_List_len=len(ws_depot_size_List)
    lprint (ws_depot_size_List,totalSize)
    totalSize=int(totalSize)
    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {postfix}'
    if ws_depot_size_List:
        with tqdm(total=totalSize,
                    mininterval=0.1,
                    bar_format=bar_format,
                    desc=f"获取文件进度,一共{totalSize}MB",
                    ncols=120) as pbar:
            callback.tqdm = pbar
            Loop_st=time.time()
            processd_size=0
            for index,file_detail in enumerate(ws_depot_size_List):  
                localFile=file_detail.get("path").replace('\\','/')
                depotFile=file_detail.get("depotFile")
                clientFile=file_detail.get("path")
                try:
                    fileSize=file_detail.get("fileSize")
                    processd_size+=int(fileSize)
                    pbar.update(int(fileSize))
                except:
                    traceback.print_exc()
                    pbar.write(depotFile)
                    return
                pbar.write(f"进度信息: {fileSize}MB ,{index}/{ws_depot_size_List_len}, "+
                            f"{localFile[-80:]}")
                if fileTypes:
                    if localFile.rsplit('.',1)[-1] not in fileTypes:
                        lprint(u'非指定类型,不获取该文件{}'.format(localFile))
                        continue
                if onlyGetMayaFile:#如果不是maya文件不获取文件
                    lprint(u'仅获取maya文件,不获取该文件')
                    if not re.search('.ma|.ma' , localFile):
                        continue
                # lprint (u'开始获取文件{}'.format(localFile))
                try:
                    p4.run_sync(depotFile,progress=callback,
                                    handler=callback)
                    getList.append(depotFile)
                except Exception as e:
                    if 'up-to-date'  in str(e) :
                        print ("已经是最新版本")
                    elif 'clobber writable' in str(e):
                        print ("except_clobber writable,强制获取")
                        if os.path.exists(localFile):
                            os.remove(localFile)
                        p4.run_sync('-f',depotFile,
                                    progress=callback,
                                    handler=callback)
                        getList.append(depotFile)
                    else:
                        print (f"同步文件失败,原因是{e}")
                
                if index == ws_depot_size_List_len-1:
                    pbar.update(totalSize-processd_size)
                    break
        print ('更新结束')
    else:
        print ("暂无需要更新的文件")
    print ("检查是否有版本已经修改的文件")  
    print (f"同步文件{getList[:2]}...,一共{len(getList)}个文件")

    concileFiles = getNeedToConcileFile(p4,files,getList)
    try:
        run_opens = p4.run_opened(files)
    except Exception as e:
        if 'not opened on this client.' in str(e) :
            print ("没有已经打开的文件")
        run_opens = []
    # lprint (concileFiles,run_opens)
    needUserProcessFile=[x.get("clientFile") for x in concileFiles]
    for concileFile in run_opens:
        action=concileFile.get("action")
        if action=="delete":
            p4.run_revert(concileFile.get("depotFile"))
        if action=="edit":
            needUserProcessFile.append(concileFile.get("depotFile"))
    if needUserProcessFile:
        print ("\n以下文件已被你修改,你需要自己决定是否覆盖本地文件")
        print (json.dumps(needUserProcessFile,indent=4,ensure_ascii=False))
        #subprocess.run([sys.executable,f'{LugwitLibDir}/LPerforce/P4Tools/getFile.py','main',*needUserProcessFile])
        print ("\n以上文件已被你修改,你需要自己决定是否覆盖本地文件")
    if forceGet:
        print ("强制获取已修改文件")
        p4.run_sync('-f',needUserProcessFile)
    print ("获取结束,请关闭次窗口")
    return getList


# getFile(r'd:/TD_Depot/plug_in/Lugwit_plug/icons\\maya.pn')
# sys.exit(0)

def revertFile(files=''):
    if 'SmartGetFile' in sys.argv:
        files=sys.argv[2:-2]
    ws_depot_size_List=get_ws_depot_size_List(files)
    
    if 'UI' in sys.argv :
        process=PySideLib.L_ProgressDialog(title=u'杩樺師鏂囦欢',processList=ws_depot_size_List)
        
    for i,(clientFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
        if 'UI' in sys.argv :
            process.index=i
            process.ProgressDialog_Procecss()
        
        try:
            p4.run_revert('-a',depotFile)
        except:
            pass

def revertFile_New(dirs='',files='',changeNum='',revertFileNoInLoacl=0,*args,**kwargs):
    lprint(locals())
    openedFiles=[]
    if dirs:
        if isinstance(dirs,str):
            dirs=[dirs]
        for dir in dirs:
            try:
                _openedFiles=p4.run_opened(dir)
                if _openedFiles:
                    openedFiles.extend(_openedFiles)
            except:
                pass

    if files:
        try:
            _openedFiles=p4.run_opened(files)
            if _openedFiles:
                openedFiles+=_openedFiles
        except:
            pass
    if changeNum:
        try:
            changelist = p4.run_describe(changeNum)
            depotFiles=[]
            for x in changelist:
                depotFiles.append(x.get("depotFile"))
            _openedFiles=p4.run_opened(depotFiles)
            if _openedFiles:
                openedFiles+=_openedFiles
        except:
            pass
    lprint(f"{openedFiles[:2]}...等{len(openedFiles)}个")
    openedFile : dict
    for openedFile in tqdm(openedFiles, desc=f"正在还原", ncols=70):
        try:
            depotFile=openedFile.get("depotFile")
            localFile:dict=p4.run_where(depotFile)
            if not localFile:
                continue
            if not os.path.exists(localFile[0].get("path")):
                p4.run_revert('-k',f"{depotFile}")
                p4.run_sync('-f',f"{depotFile}#0")
            else:
                p4.run_revert('-a',f"{depotFile}")
                #lprint(f"{depotFile}#0")
        except:
            pass
    lprint(f"还原结束")


        
        
def convertUnicodeToText(files=r'd:/TD_Depot/plug_in/Lugwit_plug/mayaPlug/l_scripts/Rig',*args,**kwargs):
    lprint (locals())
    ws_depot_size_List=get_ws_depot_size_List(files)
    if 'UI' in kwargs :
        
        process=PySideLib.L_ProgressDialog(title=u'转换文件类型',processList=ws_depot_size_List)
        
    for i,(clientFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
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
        
    for i,(clientFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
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
    for i,(clientFile,depotFile,fileSize,fileInLocalDisk) in enumerate(ws_depot_size_List):
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
        local_modification_time = int(os.path.getmtime(clientFile))
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
    
@LM.try_exp
def submitChange(files, 
                 description='descriptionFile|descriptionText',
                 submitoption='submitunchanged',method='auto',
                 callback=None):
    action_param = P4OperationAction.SUBMIT
    try:
        p4.run_add(files)
    except Exception as e:
        print(f'add file error {e}')
    try:
        p4.run_edit(files)
    except Exception as e:
        print(f'add file error {e}')
        #sunmitOptionList=['revertunchanged','leaveunchanged','submitunchanged']
    lprint (locals(),p4.user)
    #lprint <<p4.user<<lprint.end
    # aa=os.environ.get('Lugwit_Debug','')
    # os.environ['Lugwit_Debug']='noprint'
    aa=get_ws_depot_size_List(files,
                            method,
                            [],
                            action_param=P4OperationAction.SUBMIT)
    ws_depot_size_List,totalSizeNeedToDownload=get_ws_depot_size_List(files,
                                                                    method,
                                                                    [],
                                                                    action_param=P4OperationAction.SUBMIT)
    # os.environ['Lugwit_Debug']=aa
    change = p4.fetch_change()
    change['Files'] = []
    change['Description'] = description
    changeNum = p4.save_change(change)[0].split()[1]
    submitList=[]
    changeList=[]
    descriptionFile=description
    if os.path.isfile(descriptionFile):
        with codecs.open(descriptionFile,'r',encoding='utf-8') as f:
            description=f.read()
            lprint ('description',description)
        description=re.split(u'exAniClip-->>|exTpose-->>',description,flags=re.I|re.M)[0]
        #lprint ("description.replace('\\u','\u'):",description.replace('\\u','\u').decode('utf8'))

    if not ws_depot_size_List:
        lprint (ws_depot_size_List)
        return
    
    for i,file_detail in enumerate(ws_depot_size_List):
        clientFile = file_detail.get('clientFile')
        depotFile = file_detail.get('depotFile')
        local_path = file_detail.get('path') 
        try:
            p4.run_sync(depotFile)
        except Exception as ex:
            pass
        if not file_detail.get("headRev"):
            try:
                p4.run_add(clientFile)
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

    try:
        p4.run_submit(change,'-f',submitoption,progress=callback,handler=callback)
    except Exception as e:
        traceback.print_exc()

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
        p4.disconnect()
        lprint (u'创建工作区成功,请关闭此窗口')
    lprint (u'工作区路径--{},名称--{}已存在'.format(workSpacePath,clientName))


def findRfs(path):
    sys.path.append(python37Lib)
    asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()  # ??????asset
    # i=[0]#锟斤拷为python2锟斤拷没锟斤拷nonlocal锟斤拷锟斤拷,锟斤拷锟斤拷使锟斤拷锟斤拷锟斤拷锟斤拷锟
    # #nonlocal锟斤拷示锟斤拷锟节猴拷锟斤拷锟斤拷锟斤拷霞锟斤拷锟斤拷锟斤拷锟斤拷锟
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
            clientFile=re.sub('//',get_clientRootDir(),depotFile)
            if fileType=='mayaFile':
                if '.ma' not in clientFile and '.mb' not in clientFile:
                    lprint ('不是maya文件')
                    return_depotFileList.append(depotFile)
                    return_wsList.append(clientFile)
                    continue
            else:
                return_depotFileList.append(depotFile)
                return_wsList.append(clientFile)
                
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
            if not _dir.startswith('//'):
                continue
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
    print ("获取空文件夹结束,请关闭这个窗口")
  

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
    
@LM.try_exp   
def createEmpthFolderToP4(folderToCreate):
    lprint ('folderToCreate',folderToCreate)
    file=folderToCreate +'/.holder'
    if not os.path.exists(folderToCreate):
        os.makedirs(folderToCreate)
    try:
        has_holder=False
        try:
            run_files = p4.run_files(u'{}/*'.format(folderToCreate))
            if run_files:
                for x in run_files:
                    if x['depotFile'].endswith('.holder'):
                        has_holder=True
                        return
        except Exception as e:
            if ' no such file' in str(e):
                has_holder=False
        if not has_holder:
            if not os.path.exists(file):
                with open (file,'w') as f:
                    f.write('1')
            return file
    except:
        traceback.print_exc()

    # if os.path.exists(file):
    #     print ('删除临时文件')
    #     os.remove(file)
        
            
    


def switchHolderPermission(open=1):
    import loginP4
    p4=loginP4.p4_login()
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

@try_exp
def P4_uploadEmptyFolder(dirs='',
                        **kwargs):
    lprint(locals())
    # os.environ['Lugwit_Debug']='noprint'
    
    
    print ('开始创建空文件夹')
    print ('开启创建文件夹权限')
    import monitor
    monitor.switchHolderPermission(open=1)
    env = os.environ.copy()
    env['parent_process_id']= str(os.getpid())
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200

    # 创建监控进程
    cmd = [sys.executable, 'D:\\TD_Depot\\Software\\Lugwit_syncPlug\\lugwit_insapp\\trayapp\\Lib\\LPerforce\\monitor.py','monitor_function','--parent_pid',str(os.getpid())]
    lprint (' '.join(cmd))
    with open("output.log", "w") as f:
        subprocess.Popen(cmd, env=env,
                        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                        close_fds=True,
                        stdout=f, stderr=f)
                    
    needToUpLoadFiles=[];index=0
    def P4_uploadEmptyFolder_recursive(dirs):
        try:
            if isinstance(dirs , str):
                dirs=[dirs]
            for dir in dirs:
                if dir.startswith('//'):
                    l_subprocess.ps_win.showMessageWin(title='警告',text='请选择工作区创建空目录')
                    return
                # localDir=convertPathToClientAndDepotFmt(dir)[0]
                localDir=dir.replace('\\...','')
                lprint(localDir)
                
                if os.path.isdir(localDir):
                    localDir_children=glob.glob(localDir+'/*')
                    # localDir_children.append(localDir)
                    lprint (localDir)
                    needToUpLoadFile=createEmpthFolderToP4(localDir)
                    if needToUpLoadFile:
                        needToUpLoadFiles.append(needToUpLoadFile)
                    nonlocal index
                    index+=1
                    for child in localDir_children:
                        if os.path.isdir(child):
                            P4_uploadEmptyFolder_recursive('{}'.format(child) )  # 递归调用
        except Exception as ex:
            print ("错误原因")
            traceback.print_exc()
    P4_uploadEmptyFolder_recursive(dirs)

    if needToUpLoadFiles:
        myfiles = []
        run_add = p4.run_add( needToUpLoadFiles )
        for x in run_add:
            if isinstance(x,str):
                if 'currently opened for add' in x :
                    x = re.search('.+\.holder',x)
                    if x :
                        x= x.group()
                        myfiles.append(x)
            elif isinstance(x,dict):
                if x.get("action") =="add":
                    myfiles.append(x.get("depotFile"))
        lprint (run_add)
        lprint (myfiles)

        change = p4.fetch_change()
        if isinstance(dirs , str):
            dirs=[dirs]
        dirs='\n'.join(dirs)
        change._description = f"上传空文件夹\n{dirs}\n..."
        changeNum = p4.save_change(change)[0].split()[1]

        try:# 将文件与更改列表关联
            p4.run_reopen("-c", changeNum, myfiles)
        except Exception as ex:
            pass

        p4.run_submit( '-c',changeNum )



    l_subprocess.ps_win.showMessageWin(title='提示',text=f'为你上传了{index}个空文件夹')
    for x in needToUpLoadFiles:
        if os.path.exists(x):
            x=os.path.normpath(x)
            print (x)
            subprocess.run(['del','/f', x], shell=True)
    print (f"创建结束")


    # glob.glob(localDir[0])
    # if not os.path.exists(localDir[0]):
    #     os.makedirs(localDir[0])
        
def monitor_function(parent_pid):
    """
    监控函数，检查主进程是否仍在运行。
    """
    while True:
        try:
            # 使用os.kill发送0信号，仅检查进程是否存在，不发送真正的信号
            os.kill(parent_pid, 0)
        except OSError:
            # 如果主进程不存在，执行清理操作
            print("主进程已终止，执行清理操作。")
            print ('关闭创建空文件夹权限,创建文件夹成功')
            switchHolderPermission(open=0)
            break
        time.sleep(1)  # 每秒检查一次

class P4CreateFolderUI(QWidget):
    def __init__(self,selFolder):
        self.selFolder=selFolder

        super(P4CreateFolderUI, self).__init__()
        self.setFixedWidth(490)
        self.setWindowTitle(u'添加空文件夹_{}'.format(self.selFolder))
        self.topLay = QVBoxLayout()
        self.AssetUI()
        self.shotUI()
        createBtn = QPushButton(u'创建')
        createBtn.clicked.connect(self.createFolder)
        createBtn.setFixedHeight(40)
        self.topLay.addWidget(createBtn)
        self.setLayout(self.topLay)
        #self.setStyleSheet(style_sheet)
        self.setWindowFlags(QtGui.Qt.WindowType.WindowMinimizeButtonHint |   # 使能最小化按钮
                    QtGui.Qt.WindowType.WindowCloseButtonHint |      # 使能关闭按钮
                    QtGui.Qt.WindowType.WindowStaysOnTopHint) 
        
    def AssetUI(self):
        self.assetGB=QGroupBox(u'资产文件夹创建')
        self.assetGB.setCheckable(1)
        
        assetLay = QVBoxLayout() 
        self.assetGB.setLayout(assetLay)
        
        assetTypeLay=QVBoxLayout()
        self.char_prop_setLay=QHBoxLayout()
        rig_tx_fxLay=QHBoxLayout()

        self.char_prop_setGB = QGroupBox(u'您要创建角色,道具抑或道具')
        charsRB=QRadioButton('chars')
        charsRB.setChecked(True)
        propsRB=QRadioButton('props')
        setsRB=QRadioButton('sets')
        self.char_prop_setLay.addWidget(charsRB)
        self.char_prop_setLay.addWidget(propsRB)
        self.char_prop_setLay.addWidget(setsRB)
        self.char_prop_setGB.setLayout(self.char_prop_setLay)
        
        self.rig_tx_fxGB = QGroupBox(u'您要创建模型,材质,绑定还是特效')
        modCB=QCheckBox('Mod')
        modCB.setChecked(1)
        mtxCB=QCheckBox('Texture')
        mtxCB.setChecked(1)
        rigCB=QCheckBox('Rig')
        rigCB.setChecked(1)
        fxCB=QCheckBox('Fx')
        fxCB.setChecked(0)
        InfoCB=QCheckBox('Info')
        InfoCB.setChecked(0)
        TexCB=QCheckBox('Tex')
        TexCB.setChecked(0)
        CFXCB=QCheckBox('Cfx')
        CFXCB.setChecked(0)
        XgenCB=QCheckBox('Xgen')
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
        
        imageLay=QVBoxLayout()
        self.imageGB = QGroupBox(u'请选择你要在资产文件夹下创建的文件夹(仅在Texture文件夹下创建)')
        sourceimagesCB=QCheckBox('sourceimages')
        sourceimagesCB.setChecked(1)
        xgenCB=QCheckBox('xgen')
        xgenCB.setChecked(1)
        imageLay.addWidget(sourceimagesCB)
        imageLay.addWidget(xgenCB)
        self.imageGB.setLayout(imageLay)
        
        assetNameLay=QVBoxLayout()
        assetNameGB = QGroupBox(u'请设置资产名称(多个资产名称用空格隔开,如"AA BB"会创建两个资产)')
        self.assetNameField=QLineEdit('')
        assetNameLay.addWidget(self.assetNameField)
        assetNameGB.setLayout(assetNameLay)

        
        assetTypeLay.addWidget(self.char_prop_setGB)
        assetTypeLay.addWidget(self.rig_tx_fxGB)
        assetLay.addLayout(assetTypeLay)
        assetLay.addWidget(self.imageGB )
        assetLay.addWidget(assetNameGB)

        self.topLay.addWidget(self.assetGB)
        
    def shotUI(self):
        shotLay = QVBoxLayout() 
        self.shotGB = QGroupBox(u'镜头文件夹创建')
        self.shotGB.setCheckable(1)
        self.shotGB.setChecked(False)
        self.shotGB.setLayout(shotLay)
        
        stEndLay=QHBoxLayout()
        shotRangeSelectGB = QGroupBox(u'请选择你要创建的镜头文件夹')
        shotNameList=['shot{}'.format(str(i).zfill(2)) for i in range(1,31)]
        self.startShotCB=QComboBox()
        self.startShotCB.addItems(shotNameList)
        self.startShotCB.currentIndexChanged.connect(self.setShotsToCreate)
        self.endShotCB=QComboBox()
        self.endShotCB.addItems(shotNameList)
        self.endShotCB.currentIndexChanged.connect(self.setShotsToCreate)
        stEndLay.addWidget(self.startShotCB,8)
        stEndLay.addWidget(QLabel('到'),1)
        stEndLay.addWidget(self.endShotCB,8)
        shotRangeSelectGB.setLayout(stEndLay)
        
        # 创建镜头文件夹下的文件夹
        folderInShotList=['Layout','Animation','Lighting','Comp','Fx','Sim','Pr','AE']
        shotFolderGB = QGroupBox(u'请选择你要在镜头文件夹下创建的文件夹')
        shotFolderLay=QHBoxLayout()
        shotFolderGB.setLayout(shotFolderLay)
        names=locals()
        self.folderInShotWidgetList=[]
        for i,shot in enumerate(folderInShotList):
            names[shot]=QCheckBox(shot)
            self.folderInShotWidgetList.append(names[shot])
            names[shot].setToolTip(shot)
            shotFolderLay.addWidget(names[shot])
            if i<4:
                names[shot].setChecked(1)
            #names[shot].setFixedWidth(len(shot)*5)

        resultLay=QHBoxLayout()
        resultGB = QGroupBox(u'创建的镜头文件夹为')
        self.shotsToCreateLineEdit=QLineEdit()
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
            char_prop_setRBs=self.char_prop_setGB.findChildren(QRadioButton)
            for char_prop_setRB in char_prop_setRBs:
                if char_prop_setRB.isChecked():
                    char_prop_set=char_prop_setRB.text()
                    break
            rig_tx_fxCBs=self.rig_tx_fxGB.findChildren(QCheckBox)
            folderInAssetFolderList=[]
            for rig_tx_fxCB in rig_tx_fxCBs:
                if rig_tx_fxCB.isChecked():
                    folderInAssetFolderList.append(rig_tx_fxCB.text())
                    
            imageRBs=self.imageGB.findChildren(QCheckBox)
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

        app = QApplication.instance()
        if not app:
            app=QApplication(sys.argv)
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
    



def get_latest_file_in_branch_mapping(*args,**kwargs):
    #在比较视图中使用   /c python_p4  D:/TD_Depot/Software/Lugwit_syncPlug/lugwit_insapp/trayapp/Lib/LPerforce/Analytic_path.py {LugwitLibDir}\LPerforce\P4Lib.py get_latest_file_in_branch_mapping --file "%D" --UI --P4V
    lprint(locals())

    #先更新选中的文件
    if isinstance(kwargs.get('file'),list):
        files=kwargs.get('file')
    else:
        files=[kwargs.get('file')]
    print('files',files)
    if  len(files)<1:
        return print('没有选择文件')
    for file in files:
        print('p4.run_fstat(file)',p4.run_fstat(file)[0])
        file_info=p4.run_fstat(file)[0]
        if file_info['headRev'] != file_info['haveRev']:
            p4.run_sync('-f',file)
            print(f"文件已经从{file_info['haveRev']}版本更新到了最新{file_info['headRev']}版本")
        else:
            print('文件已经是最新版本')
    #然后切换到分支的对面路径
    branches = p4.run_branches()
    mapped_files=[]
    for branch in branches:
        print(branch)
        branch_name = branch['branch']
        branch_details = p4.run_branch('-o',branch_name)
        for branch_detail in branch_details:
            print('branch_detail' ,branch_detail )
            mappings=branch_detail['View']
            for mapping in mappings:
                print('mapping',mapping)
                map0=mapping.split(' ')[0].replace('...','')
                map1=mapping.split(' ')[1].replace('...','')
                if map0 in files[0]:
                    print('文件在映射的源路径中')
                    mapped_files=[file.replace(map0,map1) for file in files]
                    mapped_files.append(0)
                elif map1 in files[0]:
                    print('文件在映射的目标路径中')
                    mapped_files=[file.replace(map1,map0) for file in files]
                    mapped_files.append(1)
    merge_file_to_branch(files,mapped_files)

def merge_file_to_branch(files,mapped_files):
#复制文件到映射的对面路径
    ADD=False
    for mapped_file in mapped_files[:-1]:
        dst = p4.run_where(mapped_file)[0]['path']
        if not os.path.exists(dst):#对面存在不复制
            ADD=True
            try:
                os.makedirs(os.path.dirname(dst))
            except:
                pass
            for file in files:
                src = p4.run_where(file)[0]['path']
                shutil.copy2(src,dst)
                p4.run_add(mapped_file)
                print(f"复制成功！添加了还未提交，成功将{src}复制到{dst}")
        else:
            try:
                p4.run_add(mapped_file)
            except:
                pass


    if not ADD:
    #如果选中的是分支文件，合并分支文件到主分支
        if mapped_files:
            if mapped_files[-1]==1:
                for i,mf in enumerate(mapped_files[:-1]):
                    try:
                        p4.run_integrate(files[i],mf)
                        print(f"合并成功！将{files[i]}合并到{mf}")
                    except:
                        print(f"合并失败！{files[i]}和{mf}不能合并")
                        traceback.print_exc()
                    try:
                        p4.run_resolve('-at',mf)
                        print(f"解决成功！解决了{mf}")
                    except:
                        print(f"解决失败！失败文件{mf}")
                        traceback.print_exc()
                    
        #如果选中的是主分支文件，从主分支复制文件并覆盖
            elif mapped_files[-1]==0:
                #复制文件到映射的对面路径
                for mapped_file in mapped_files[:-1]:
                    dst = p4.run_where(mapped_file)[0]['path']
                    for file in files:
                        src = p4.run_where(file)[0]['path']
                        shutil.copy2(src,dst)
                        try:
                            p4.run_add(mapped_file)
                            print(f"复制成功！添加了还未提交222，成功将{src}复制到{dst}")
                        except:
                            pass
                        try:
                            p4.run_edit(mapped_file)
                            print(f"复制成功！迁出了还未提交，成功将{src}复制到{dst}")
                        except:
                            pass
                        print(mapped_file)





if __name__=='__main__'  :
    import fire
    fire.Fire()

