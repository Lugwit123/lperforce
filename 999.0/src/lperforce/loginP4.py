# coding:utf-8

import sys,os,time
import traceback
print ('sys.argv',sys.argv)

import threading
import queue
# 添加模块所在路径
st=time.time()

LugwitToolDir=os.environ["LugwitToolDir"]

import Lugwit_Module as LM
from Lugwit_Module.l_src import getExecuteExe
if getExecuteExe.isUEnv():
    os.environ['TCL_LIBRARY'] = sys.executable.replace('Win64\\UnrealEditor.exe','ThirdParty\\Python3\\Win64\\tcl\\tcl8.6')
    os.environ['TK_LIBRARY'] =  sys.executable.replace('Win64\\UnrealEditor.exe','ThirdParty\\Python3\\Win64\\tcl\\tk8.6')
import tkinter as tk
from tkinter import ttk


# P4_API 路径由 lperforce/package.py 的 commands() 注入，无需手动添加

from P4 import P4, P4Exception, Progress, OutputHandler,ReportHandler
from Lugwit_Module.l_src import l_subprocess
lprint=LM.lprint
import  socket
import getpass

# try:
#     userName=os.getlogin()
# except:
#     userName=getpass.getuser()
print("LM",LM)
@LM.try_exp
def p4_login(userName='',
             hostName='',
             wsDir=r'',
             port='',
             password='',
             clientName=''):
    # lprint(locals())
    wsDir=wsDir.replace('\\','/')
    p4 = P4() 
    p4.charset = 'utf8'
    if  port:
        p4.port=port
    else:
        p4.port = os.getenv('P4PORT')

    if userName:
        p4.user = userName
    elif os.getenv('P4UESR'):
        p4.user = os.getenv('P4USER')
    # lprint (p4.user)
    if password:
        p4.password = password
    try:
        p4.connect()
    except:
        lprint (u'登陆失败>>{}'.format(l_subprocess.ps_win)) 
        l_subprocess.showMessageWin(text=traceback.format_exc(), 
                        title=u'登陆插件服务器失败,请联系开发人员', 
                        fontSize=12,
                        timeout=50,
                        icon_size=(32,32))
        return False
    if not userName:
        userName=p4.user
        if not userName:
            userName=os.getlogin()
    if not hostName:
        hostName=socket.gethostname()

    
    allUsers=[x['User'] for x in p4.run("users", "-a")]
    # group = p4.run('group', '-o',"Staff")
    # lprint (allUsers)

    
    # staff_group = p4.fetch_group('Staff')
    # print ('staff_group',staff_group)
    if userName not in allUsers:
        new_user = {
            "User": userName,
            "Email": userName+'@qq.com',
            "FullName": userName,
            "Type": "standard",
            # "Group": "Staff",
        }
        p4.run("user", "-if", input=new_user)
        # staff_group['Users'].append(userName)
        # p4.save_group(staff_group)
        # group = p4.run('group', '-o',"Staff")
        # print (group)
        # print (f'创建用户{new_user}成功')
            
    p4.user = userName

    if clientName:
        p4.client = clientName
        # p4.set_env('clientDir',p4.client.get("ROOT"))
    elif wsDir:
        st_get_client = time.time()
        while True:
            try:
                allClients=p4.run('clients')
                for client in allClients:
                    clentName=client['client']
                    ClientDir=client['Root']
                    ClientDir=ClientDir.replace('\\','/')
                    clientHost=client['Host']
                    ClientDir =  ClientDir[:-1] if  ClientDir.endswith('/') else ClientDir
                    wsDir =  wsDir[:-1] if  wsDir.endswith('/') else wsDir
                    if clientHost==hostName and ClientDir.lower()==wsDir.lower() and clentName.lower()!=hostName.lower():
                        p4.client=clentName
                        p4.set_env('clientDir',ClientDir)
                        break
                if time.time()-st_get_client>5:
                    raise Exception("get client error for user {}".format(p4.user))
                time.sleep(1)
                break
            except:
                print(u"获取工作区失败")


    p4.charset='utf8'
    # p4.disconnect()
    # lprint(p4)
    try:
        p4.run_login()
        os.environ["P4USER"] = p4.user
        os.environ["P4CLIENT"] = p4.client
        os.environ["P4PORT"] = p4.port
        # os.system('p4 set P4CLENT={}'.format(p4.client))
        # os.system('p4 login')
        # lprint(os.environ.get("P4USER"))
        # lprint (u'登陆成功>>{}'.format(p4))
        # p4.exception_level = 1
        return p4
    except:
        l_subprocess.ps_win.showMessageWin(text=traceback.format_exc(), 
                        title=u'提示', 
                        fontSize=12,
                        timeout=5,
                        icon_size=(32,32))










if __name__ == '__main__':
    p4=p4_login(userName='p4_operator',
                        password='123',
                        port="192.168.110.61:1666")
    # print (p4.client)
    # print ('\n')
    print (p4.fetch_client())

def tkProcess(total, queue_ins,title='进度条示例'):
    tkroot = tk.Tk()
    tkroot.title(title)
    tkroot.geometry("600x250")
     # 获取屏幕的宽度和高度
    screen_width = tkroot.winfo_screenwidth()
    screen_height = tkroot.winfo_screenheight()

    # 获取窗口的宽度和高度
    window_width = 600
    window_height = 250

    # 计算窗口在屏幕中央的位置
    position_right = int(screen_width/2 - window_width/2)
    position_down = int(screen_height/2 - window_height/2)

    # 设置窗口的位置
    tkroot.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    # 创建进度条
    tkprogress = ttk.Progressbar(
        tkroot, orient="horizontal", length=600, maximum=total, mode="determinate")
    tkprogress.pack(pady=20)

    # 创建标签显示百分比
    percent_label = tk.Label(tkroot, text="0%")
    percent_label.pack(pady=10)

    def update_progress():
        latest_value = 0
        while True:
            try:
                # 尝试获取最新的值，清空队列中的旧值
                while not queue_ins.empty():
                    latest_value = queue_ins.get()
                
                # 使用最新值更新进度条
                tkprogress['value'] = latest_value
                
                # 计算并更新百分比
                percent_complete = (latest_value / total) * 100
                percent_label.config(text=f"{percent_complete:.2f}%")
                
                tkroot.update_idletasks()

                if latest_value >= total:  # 如果进度达到100%，关闭窗口
                    tkroot.destroy()
                    break
                if latest_value == 'over':  # 如果进度达到100%，关闭窗口
                    tkroot.destroy()
                    break

            except queue.Empty:
                pass

            time.sleep(0.01)

    threading.Thread(target=update_progress, daemon=True).start()
    tkroot.mainloop()

class MyProgressHandler(Progress,OutputHandler,):
    def __init__(self,parent=None,fileInfoList=[],
                tqdm=None,
                showProcess=False,
                p4cmd='revert|fstat',
                file_count=0,
                progressWinTitle='还原文件'):
        Progress.__init__(self)
        OutputHandler.__init__(self)
        print ("初始化进度条")
        self.total = 0
        if file_count:
            self.total=file_count
            showProcess=True
        
        self.position = 0
        self.proccess='0'
        self.depotFile = None
        self.fileInfoList=fileInfoList
        self.parent=parent
        self.tqdm=tqdm
        self.output_message=''
        self.showProcess=showProcess
        self.isCountCmd=p4cmd in ['revert','fstat']
        self.p4cmd=p4cmd
        self.queue=None
        

        if self.showProcess:
            if self.total>0:
                self.progressWinTitle = {'revert':'还原文件','fstat':'获取文件信息'}.get(p4cmd)
                self.queue = queue.Queue()  # 创建队列用于进度更新
                self.thread=threading.Thread(target=tkProcess, args=(self.total, self.queue,self.progressWinTitle))
                self.thread.start()

    def init(self, type):
        self.startTime=time.time()-0.001
        if 'init' in self.fileInfoList:
            print("Progress initialized:", type)

    def setTotal(self, total):
        self.total = total
        if 'setTotal' in self.fileInfoList:
            print("Total set:", total)



    def update(self, position=0):
        self.position = position
        if self.total>0:
            self.proccess= position/self.total*100
            # self.processUI.set_additional_info(process)
            if self.tqdm:
                aa=time.time()-self.startTime
                bb=position/aa/1000
                self.tqdm.set_postfix_str(f"单文件进度: {self.proccess:.5f}%,速度,{bb:.2f}MB/s,用时：{aa:.2f}s")
                # self.tqdm.update(position - self.tqdm.n)  # 更新进度条

        # print (position)
        # print (f"\ncallback.tqdm--{repr(self.tqdm)},{type(self.tqdm)},{self.tqdm.update}")
        return self.position


    def done(self, fail):
        if fail:
            print("Progress done with failure")
        else:
            if 'done' in self.fileInfoList:
                print("Progress done successfully")
        if self.queue:
            print ('运行结束,发送game over')
            self.queue.put('over')  # 完成后发送结束信号

    
    def outputStat(self, stat):
        if 'outputStat' in self.fileInfoList:
            print('self.position',self.position)
        
        new_depotFile = stat.get('depotFile')
        if new_depotFile != self.depotFile:
            self.depotFile = new_depotFile
            if self.isCountCmd and self.queue:
                self.position+=1
                self.queue.put(self.position)  # 将进度信息放入队列
            # print(f"Depot file updated: {self.depotFile}")
    
        return OutputHandler.REPORT
    
    def outputInfo(self, info):
        print('outputInfo',info)
        
        return OutputHandler.HANDLED

    def outputMessage(self, msg):
        print('\noutputMsga',msg)
        self.output_message=str(msg)
        raise P4Exception(msg)
    
    def outputText(self, s):
        print('outputText',s)
        return OutputHandler.HANDLED
    
    def outputBinary(self, b):
        print('outputBinary',b)
        return OutputHandler.HANDLED















