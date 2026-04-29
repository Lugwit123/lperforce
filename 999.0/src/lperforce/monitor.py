import os,sys,time,psutil,fire

LugwitToolDir=os.environ["LugwitToolDir"]
sys.path.append(LugwitToolDir+'/Lib') 
import Lugwit_Module as LM
from Lugwit_Module.l_src import l_subprocess

def switchHolderPermission(open=1):
    LM.lprint(locals())
    import loginP4
    open=int(open)
    p4=loginP4.p4_login(port='192.168.110.26:1666')
    fetch_protect=p4.fetch_protect()
    Protections=fetch_protect.get('Protections')
    permission_str = f'super user {p4.user} * //.../.holder'
    LM.lprint(permission_str)  # 记录权限更改尝试

    if open == 1:
        # 添加权限，如果它还不在列表中
        if permission_str not in Protections:
            Protections.append(permission_str)
        print ("添加权限成功")
    else:
        # 尝试移除权限，如果它在列表中
        if permission_str in Protections:
            time.sleep(5)
            Protections.remove(permission_str)
            l_subprocess.ps_win.showMessageWin(title='提示',text=f'操作完毕,关闭权限{permission_str}',timeout=4)
        else:
            print("尝试移除不存在的权限: {}".format(permission_str))
    fetch_protect['Protections']=Protections
    p4.save_protect(fetch_protect)

def monitor_function(parent_pid):
    """
    监控函数，检查主进程是否仍在运行。
    """
    print ('parent_pid',parent_pid)
    
    while True:
        if not psutil.pid_exists(parent_pid):
            # 如果主进程不存在，执行清理操作
            print("主进程已终止，执行清理操作。")
            print ('关闭创建空文件夹权限,创建文件夹成功')
            switchHolderPermission(open=0)
            break
        time.sleep(1)
        

if __name__=='__main__':
    print('sys.argv',sys.argv)
    fire.Fire()