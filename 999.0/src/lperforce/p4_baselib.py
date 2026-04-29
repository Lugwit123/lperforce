import sys,os,time
import traceback
from typing import Dict, List, Optional
# 添加模块所在路径
st=time.time()

LugwitToolDir=os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir+'/Lib') 
from Lugwit_Module import *
import  Lugwit_Module as LM
from  Lugwit_Module.l_src.l_subprocess import showMessage_ps
curDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(curDir)
import loginP4
from lperforce.dataType import login_info as login_info_dataType
from typing import Literal
import P4 

import  socket
import getpass

p4=None

# 清理工作区
def cleanWorkSpace(self=None,workSpacePath='D:/TD_Depot',workName='plug'):
    if userName == 'qqfeng':
        return
    print ('清理建工作空间')
    os.system('taskkill /f /t /im p4.exe')
    workSpacePath=workSpacePath.replace('\\', '/')
    if workSpacePath.endswith('/'):
        workSpacePath=workSpacePath[:-1]
    for x in [r'//TD_Depot/plug_in/Lugwit_plug',
            r'//TD_Depot/Software/Lugwit_syncPlug',
            r'//TD_Depot/plug_in//Python/Python39']:
        try:
            print ('清理工作空间')
            #os.chdir(x)
            command=f'{LM.perforceInsDir}\p4.exe -c {p4.client} -p {P4Port} clean {x}/...'
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process=subprocess.Popen(fr'{LM.perforceInsDir}\p4.exe -c {p4.client} -p {P4Port} clean {x}/...',
                            shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
                            )
            stdout, stderr = process.communicate()
            print (stdout, stderr)
            print (f'清理工作空间成功,清理命令是{command}')
        except Exception as e:
            print (f'清理工作空间失败,原因是{e}')
    # client = p4.fetch_client(p4.client)
# cleanWorkSpace()
# sys.exit()


# 创建工作区
def createWorkSpace(p4,userName,workSpacePath='D:/TD_Depot',workName='',
                    client_options=["noclobber","nomodtime",'noallwrite'],
                    client_views=[r"//TD_Depot/... //{Client}/... "],
                    description="default"):
    print ('创建工作空间')
    lprint (locals())
    workSpacePath=workSpacePath.replace('\\', '/')
    if workSpacePath.endswith('/') and workSpacePath.count('/')>1:
        workSpacePath=workSpacePath[:-1]
    hostName = socket.gethostname()
    all_clients = p4.run_clients('-a')
    clients = [client for client in all_clients if client.get('Host') == hostName]
    client = p4.fetch_client(p4.client) 
    print (u'fetch_client:{}'.format(client))
    print (f'当前主机的工作区{client}')
    p4.user=userName
    client = p4.fetch_client(workName)
    lprint (f'即将创建新的工作区{client}')
    #如果P4工作区Root路径存在就不创建工作区
    hasWorkSpace=False
    for x in clients:
        if x['Host']!=hostName:
            continue
        rootDir=x['Root'].replace('\\', '/')
        if rootDir.endswith('/') and len(rootDir)>3:
            rootDir=rootDir[:-1]
        if os.path.samefile(rootDir, workSpacePath ):
            print  (f"已经存在用户{userName}的工作区{x}")
            if workName == x['client']:
                hasWorkSpace=True
                return client
    
    if not hasWorkSpace:
        if not os.path.exists(workSpacePath):
            os.system('md {}'.format(workSpacePath))
        client._root = workSpacePath
        client._submitOptions='revertunchanged'
        client._description = description
        options = client['Options'].split(" ")
        client['Options'] = " ".join(options)
        for i,client_view in enumerate(client_views):
            client_view= client_view.replace('{Client}',client['Client']) 
            client_views[i]=client_view
        client["View"] = client_views
        setClientAttr(p4,client_options,client=client,saveAttr=False)
        p4.save_client(client)
        lprint ('创建工作区成功{}'.format(client))
        return client
    # client = p4.fetch_client(p4.client)
# createWorkSpace()
# sys.exit()

def getOldClient(p4,userName=""):
    hostName = socket.gethostname().lower()
    all_clients = p4.run_clients('-a')
    if userName:
        clients = [client for client in all_clients if client.get('Host').lower() == hostName
                                and client.get('User') == userName]
    else:
        clients = [client for client in all_clients if client.get('Host').lower() == hostName ]

    return clients

def getH_projectClient(p4) -> dict:
    if LM.localIP == '192.168.110.26':
        workSpacePath='D:\\H'
    else:
        workSpacePath='H:\\'
    OldClient = getOldClient(p4)
    OldClient_ = []
    for x in OldClient :
        if os.path.exists(x['Root']):
            if os.path.samefile(workSpacePath,x['Root']):
                OldClient_.append(x)
    OldClient = OldClient_
    lprint (OldClient)
    if not OldClient:
        showMessage_ps.showMessageWin(title='启动P4V',
                iconPath=LM.LugwitToolDir+'\\icons\\p4v.ico',         
                text='迁移工作区后才能从这里启动P4V', )
    for x in OldClient:
        if '个人H盘项目账号' in x.get('Description'):
            lprint("getH_projectClient",x)
            return x
        
def getPLugClient(p4) -> dict:
    workSpacePath='D:/TD_Depot'
    OldClient = getOldClient(p4)
    OldClient_ = []
    for x in OldClient :
        if os.path.exists(x['Root']):
            if os.path.samefile(workSpacePath,x['Root']):
                OldClient_.append(x)
    OldClient = OldClient_
    lprint (OldClient)
    if not OldClient:
        showMessage_ps.showMessageWin(title='插件工作区丢失',
                iconPath=LM.LugwitToolDir+'\\icons\\p4v.ico',         
                text='插件工作区丢失', )
    for x in OldClient:
        if '_plug' in x['client']:
            lprint("getPLugClient",x)
            return x



def refresh_H_project_Client(p4):
    OldClient = getH_projectClient(p4)
    if not OldClient:
        showMessage_ps.showMessageWin(title='启动P4V',
                iconPath=LM.LugwitToolDir+'\\icons\\p4v.ico',         
                text='迁移工作区后才能从这里启动P4V', )
        return
    if '个人H盘项目账号' in OldClient.get('Description'):
        user=  OldClient.get("Owner")
        client= OldClient.get('client')
        #os.system("chcp 65001")
        cmd = fr'D:\TD_Depot\Software\ProgramFilesLocal\Perforce\p4.exe -p {p4.port} -u {user} -c {client} flush'
        lprint (cmd)
        os.system(cmd)
        return OldClient
    



def setClientAttr(p4,client_options=["noclobber","nomodtime",'noallwrite'],client=None,saveAttr=True,*args):
    if not client:
        client = p4.fetch_client(p4.client)
    options = client['Options'].split(" ")
    for _ in client_options:
        if _ in options:
            options.remove(_)
            options.append(_[2:])
    client['Options'] = " ".join(options)
    if saveAttr:
        p4.save_client(client)
    print ('设置工作区属性{}'.format(client))
    
# setClientAttr()
# sys.exit(0)

# 删除存在于本机的根目录为"D:/"工作区
# 这个函数会关闭P4,建议手动关闭Maya
def deleteOldClient(p4,clientName):
    p4.client = clientName
    fetch_client = p4.fetch_client(p4.client)
    try:
        p4.run_client('-df',fetch_client['Client'])
    except:
        print (traceback.format_exc())


def createUser(username, fullname, password, email, user_type, group=None):
    """
    创建一个新的 Perforce 用户并设置用户类型。

    参数:
    username (str): 用户名
    fullname (str): 用户的全名
    email (str): 用户的电子邮件地址
    password (str): 用户的密码
    user_type (str): 用户类型，默认为 "standard"。可以是 "standard", "service", "operator"。

    返回:
    None
    """
    user_dict = {
        'User': username,
        'FullName': fullname,
        'Email': email,
        'Password': password,
        'Type': user_type
    }
    print('Creating user:', user_dict)
    p4.input = user_dict
    p4.run('user', '-i', '-f')

    # 将用户加入指定的组
    if group:
        group_spec = p4.fetch_group(group)
        
        # 检查用户是否已经在组中
        if username not in group_spec.get('Users', []):
            group_spec['Users'].append(username)
            p4.input = group_spec
            p4.run('group', '-i')
            print(f'Added user {username} to group {group}')
        else:
            print(f'User {username} is already in group {group}')

def addUserToGroup(p4, username, group):
    """
    将用户添加到指定的 Perforce 组中（如果用户不在组中）。

    参数:
    username (str): 用户名
    group (str): 组名

    返回:
    None
    """
    # 获取组的规范
    group_spec = p4.fetch_group(group)

    # 检查 'Users' 键是否存在，如果不存在则初始化为空列表
    if 'Users' not in group_spec:
        group_spec['Users'] = []

    # 检查用户是否已经在组中
    if username not in group_spec['Users']:
        group_spec['Users'].append(username)
        p4.input = group_spec
        p4.run('group', '-i')
        print(f'Added user {username} to group {group}')
    else:
        print(f'User {username} is already in group {group}')




def user_exist(username):
    try:
        # 获取所有用户信息
        users = p4.run("users")
        
        # 检查用户名是否在用户列表中
        for user in users:
            if user['User'] == username:
                return True
        return False
    except P4.P4Exception as e:
        print(f"Error: {e}")
        return False

def get_all_user_groups(p4)-> Dict[str, Dict[str, any]]:
    """
    获取所有用户组的信息，包括每个组中的用户信息

    参数:
        p4 (P4.P4): P4Python连接对象

    返回:
        dict: {
                组名称: {
                    'groupInfo': 组信息字典,
                    'userList': {
                        用户名: 用户信息字典,
                        ...
                    }
                },
                ...
        }
    """
    group_info_list=p4.run('groups')
    groupDict={}
    for i,group_info in enumerate(group_info_list):
        groupName=group_info['group']
        userName=group_info['user']
        user_info  = p4.run_user('-o',userName)[0]
        userDict = {userName: user_info}
        exist_user_list=groupDict.get(groupName,{}).get('user_infoList',{})
        exist_user_list|=userDict
        groupDict.setdefault(groupName,{}).setdefault('user_infoList',exist_user_list)
        groupDict.setdefault(groupName,{}).setdefault('groupInfo',group_info)
        # if i==0:print(group_info)
        # if i>10:break
    return groupDict



def get_changes(workspace):
    try:
        changes = p4.run("changes", "-c", workspace)
        return changes
    except P4.P4Exception as e:
        print(f"Failed to get changes: {e}")
        return None


def move_files_to_change_list(p4, files, change_number,oldClient,NewClient):
    lprint (locals())
    try:
        for file in files:
            p4.client=oldClient
            fstat = p4.run("fstat", file)[0]["type"]
            lprint (fstat)
            if '+l' in fstat:
                newType=fstat.replace('+l','')
                p4.run("reopen", "-t", newType, file)
                print (f"修改文件类型为解锁状态{file}")
            try:
                p4.run_unlock('-f',file)
                print (f"解锁文件{file}")
            except:
                print (f"文件{file}没有被锁定")
            p4.client=NewClient
            try:
                p4.run_flush(file)
            except:
                pass
            try:
                p4.run_edit( file)
            except:
                print (f"编辑文件{file}失败,原因是{traceback.format_exc()}")
            p4.run_reopen('-c', change_number, file)
            print(f"Moved {file} to change list {change_number}")
    except P4.P4Exception as e:
        print(f"Failed to move files to change list: {e}")

def create_new_change_list(p4, user, workspace, description="Automated change list"):
    try:
        change = p4.fetch_change()
        change['User'] = user
        change['Client'] = workspace
        change['Description'] = description
        result = p4.save_change(change)
        change_number = result[0].split()[1]
        return change_number
    except P4.P4Exception as e:
        print(traceback.format_exc())
        return None
    
def get_user_groups(p4, username):
    # 获取所有组的信息
    groups = p4.run("groups")

    # 查找当前用户所在的组
    user_groups = set()
    for group in groups:
        group_infos = p4.run("group", "-o", group['group'])
        for group_info in group_infos:
            if username in group_info.get('Users',''):
                user_groups.add((group['group'],group.get('description','').strip()))

    return user_groups

def get_all_groups(p4, username):
    # 获取所有组的信息
    groups = p4.run("groups")

    # 查找当前用户所在的组
    user_groups = set()
    for group in groups:
        group_infos = p4.run("group", "-o", group['group'])
        for group_info in group_infos:
            if username in group_info.get('Users',''):
                user_groups.add((group['group'],group.get('description','').strip()))

    return user_groups


@LM.try_exp
def checkOut(p4, files, newCheckNum=True, commit='', add=False,showProcess=False) -> int:
    checkSuccess_files = []
    try:
        # 如果需要生成新的变更号
        if newCheckNum:
            change = p4.fetch_change()
            change['Description'] = commit or 'Auto-generated changelist'
            result = p4.save_change(change)
            change_num = int(result[0].split()[1])
        else:
            changes = p4.run_changes('-m1', '-s', 'pending')
            if changes:
                change_num = changes[0]['change']
            else:
                print("No pending changelist found. Exiting.")
                return -1

        # 检查文件是否已经在某个挂起的更改列表中，并移动到新的更改列表中
        openedFile=[]
        for file in files:
            opened = p4.run_opened(file)
            if opened:openedFile.append(file)
        if openedFile:
            # old_change_num = opened[0]['change']
            p4.run_reopen('-c', change_num, openedFile)

        # 添加或签出文件
        if add:
            try:
                addFiles=p4.run_add('-c', change_num, files)
                addFiles = [x for x in addFiles if isinstance(x, dict)]
                lprint (addFiles[:5])
                # checkSuccess_files.append(file)
            except P4.P4Exception as e:
                lprint("Failed to add files:", e)

        
        try:
            p4.run_edit('-c', change_num,files)
            # checkSuccess_files.append(file)
            lprint ("签出文件")
        except P4.P4Exception as e:
            lprint("Failed to edit files:", e)

        return change_num
    except P4.P4Exception as e:
        print("P4Exception: ", e)
        return -1

def revert(p4, changeNum,showProcess=False,fileInfoList=[],) -> int:
    opened_files = p4.run_opened("-c", changeNum)
    # 计算文件数量
    file_count = len(opened_files)
    print ('file_count',file_count)
    callback=loginP4.MyProgressHandler(showProcess=True,
                                       fileInfoList=fileInfoList,
                                       file_count=file_count,
                                       p4cmd='revert')
    
    p4.run_revert('-a','-c',changeNum,progress=callback,
                            handler=callback)
    opened_files = p4.run_opened("-c", changeNum)
    if len(opened_files)==0:
        p4.run_change("-d", changeNum)
        return -1
    else:
        return changeNum
    
    
def getP4LoginInfo(infoSource:Literal["plug",'project'])->Optional[login_info_dataType.P4LoginInfo]:
    from lperforce import loginP4, p4_baselib
    port = "192.168.110.61:1666" if infoSource=='plug' else "192.168.110.26:1666"
    lprint(locals())
    p4 = loginP4.p4_login(userName='p4_operator',
                          password='123',
                          port=port)
    if not p4:
        return []
    lprint(f"获取登录信息,,使用通用账号登录P4{p4}成功")
    # 获取项目客户端
    client = p4_baselib.getPLugClient(p4) if infoSource=='plug' else p4_baselib.getH_projectClient(p4)
    if not client:
        return []
    client_Name = client.get("client", None)
    if not client_Name:
        return []

    # 获取用户名
    username = client.get("Owner")
    
    # 获取用户信息
    user_info = p4.run("user", "-o", username)
    lprint(user_info)
    # 获取用户组信息
    user_groups_raw = p4_baselib.get_user_groups(p4, username)
    lprint(user_groups_raw)
    client_root = client.get('Root')
    # 断开连接
    p4.disconnect()
    
    # 将 user_groups_raw 转换为 GroupInfo 列表
    user_groups = [login_info_dataType.GroupInfo(name=group[0], description=group[1]) for group in user_groups_raw if len(group) == 2]

    # 构造 P4LoginInfo 实例
    try:
        result = login_info_dataType.P4LoginInfo(
            **user_info[0],
            userGroups=user_groups,
            clientName=client_Name,
            clientType=infoSource,
            port=port,
            clientRoot=client_root
        )
        return result
    except:
        lprint(locals())
    


if __name__=="__main__":
    getP4LoginInfo(infoSource='project')
