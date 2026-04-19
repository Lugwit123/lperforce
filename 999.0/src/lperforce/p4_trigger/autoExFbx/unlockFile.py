import ctypes
from ctypes import wintypes
import subprocess
import os
import win32api
import win32con
import win32file
import pywintypes
import traceback
import socket
import os,sys,time,inspect,threading
LugwitToolDir = os.getenv('LugwitToolDir')
sys.path.append(LugwitToolDir+'/Lib')
from ctypes import WinDLL, wintypes, byref, POINTER, Structure
from ctypes.wintypes import DWORD, LPWSTR

ip = socket.gethostbyname(socket.gethostname())
if  ip == '192.168.110.26':
    wsDir= r'D:\H'
else:
    wsDir= r'H:/'

from Lugwit_Module import lprint
# 定义所需常量
MAX_PREFERRED_LENGTH = -1
NERR_Success = 0

# 定义FILE_INFO_3结构体
class FILE_INFO_3(ctypes.Structure):
    _fields_ = [
        ("fi3_id", wintypes.DWORD),
        ("fi3_permissions", wintypes.DWORD),
        ("fi3_num_locks", wintypes.DWORD),
        ("fi3_pathname", wintypes.LPWSTR),
        ("fi3_username", wintypes.LPWSTR),
    ]

# 加载Netapi32.dll
netapi32 = WinDLL('Netapi32.dll')



# API 函数原型
netapi32.NetFileEnum.argtypes = [wintypes.LPWSTR, wintypes.LPWSTR, wintypes.LPWSTR, DWORD, POINTER(POINTER(FILE_INFO_3)), DWORD, POINTER(DWORD), POINTER(DWORD), POINTER(DWORD)]
netapi32.NetFileEnum.restype = DWORD

netapi32.NetFileClose.argtypes = [wintypes.LPWSTR, DWORD]
netapi32.NetFileClose.restype = DWORD

def close_shared_file(target_path):
    FILE_INFO_LEVEL = 3  # 使用FILE_INFO_3结构
    pref_max_len = DWORD(-1)  # 无限制
    entries_read = DWORD(0)
    total_entries = DWORD(0)
    resume_handle = DWORD(0)
    buffer = POINTER(FILE_INFO_3)()

    # 调用 NetFileEnum
    result = netapi32.NetFileEnum(None, None, None, FILE_INFO_LEVEL, byref(buffer), pref_max_len, byref(entries_read), byref(total_entries), byref(resume_handle))
    
    if result == 0:  # 如果调用成功
        g_file=target_path.lower().replace(wsDir.lower(),'g:')
        # if file_info['pathname'].lower() ==  g_file or file_info['pathname'].lower()==target_path.lower():
        for i in range(entries_read.value):
            file_info = buffer[i]
            if  file_info.fi3_pathname.lower() ==  g_file or file_info.fi3_pathname.lower()==target_path.lower():
                print(f"Closing file: {file_info.fi3_pathname} (ID: {file_info.fi3_id})")
                # 关闭文件
                if netapi32.NetFileClose(None, file_info.fi3_id) == 0:
                    print("File closed successfully.")
                else:
                    print("Failed to close the file.")

    # 释放内存
    if buffer:
        netapi32.NetApiBufferFree(buffer)

LPFILE_INFO_3 = ctypes.POINTER(FILE_INFO_3)

# 定义NetFileEnum函数原型
NetFileEnum = ctypes.windll.Netapi32.NetFileEnum
NetFileEnum.argtypes = [
    wintypes.LPWSTR,       # ServerName
    wintypes.LPWSTR,       # BasePath
    wintypes.LPWSTR,       # UserName
    wintypes.DWORD,        # Level
    ctypes.POINTER(ctypes.c_void_p),  # BufPtr
    wintypes.DWORD,        # PrefMaxLen
    ctypes.POINTER(wintypes.DWORD),   # EntriesRead
    ctypes.POINTER(wintypes.DWORD),   # TotalEntries
    ctypes.POINTER(wintypes.DWORD)    # ResumeHandle
]
NetFileEnum.restype = wintypes.DWORD

# 定义NetFileGetInfo函数原型
NetFileGetInfo = ctypes.windll.Netapi32.NetFileGetInfo
NetFileGetInfo.argtypes = [
    wintypes.LPWSTR,    # ServerName
    wintypes.DWORD,     # FileId
    wintypes.DWORD,     # Level
    ctypes.POINTER(ctypes.c_void_p)   # BufPtr
]
NetFileGetInfo.restype = wintypes.DWORD

# 定义NetApiBufferFree函数
NetApiBufferFree = ctypes.windll.Netapi32.NetApiBufferFree
NetApiBufferFree.argtypes = [ctypes.c_void_p]
NetApiBufferFree.restype = wintypes.DWORD

def get_open_files(server_name=None, base_path=None, user_name=None):
    """获取被占用的文件信息"""
    level = 3
    bufptr = ctypes.c_void_p()
    entries_read = wintypes.DWORD()
    total_entries = wintypes.DWORD()
    resume_handle = wintypes.DWORD(0)

    result = NetFileEnum(
        server_name,
        base_path,
        user_name,
        level,
        ctypes.byref(bufptr),
        MAX_PREFERRED_LENGTH,
        ctypes.byref(entries_read),
        ctypes.byref(total_entries),
        ctypes.byref(resume_handle)
    )

    if result != NERR_Success:
        raise ctypes.WinError(result)

    file_infos = []
    if entries_read.value > 0:
        array_type = FILE_INFO_3 * entries_read.value
        files = ctypes.cast(bufptr, ctypes.POINTER(array_type)).contents
        for file in files:
            file_info = {
                "id": file.fi3_id,
                "permissions": file.fi3_permissions,
                "num_locks": file.fi3_num_locks,
                "pathname": file.fi3_pathname,
                "username": file.fi3_username
            }
            file_infos.append(file_info)

        NetApiBufferFree(bufptr)

    return file_infos

def get_file_info(server_name, file_id):
    """获取特定文件的详细信息"""
    level = 3
    bufptr = ctypes.c_void_p()

    result = NetFileGetInfo(
        server_name,
        file_id,
        level,
        ctypes.byref(bufptr)
    )

    if result != NERR_Success:
        raise ctypes.WinError(result)

    file_info = None
    if bufptr:
        file_info = ctypes.cast(bufptr, LPFILE_INFO_3).contents
        NetApiBufferFree(bufptr)

    return file_info



def is_file_locked(file_path):
    """
    检查文件是否被占用。
    尝试以独占模式打开文件，如果被占用则捕获到异常。
    """
    file_path = os.path.normcase(file_path)

    try:
        # 打开文件
        handle = win32file.CreateFile(
            file_path,
            win32con.GENERIC_READ,
            0,  # 独占模式
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_ATTRIBUTE_NORMAL,
            None
        )
        win32file.CloseHandle(handle)
        return False
    except pywintypes.error as e:
        return True
        # 错误代码 32 表示文件正在被使用
        if e.winerror == 32:
            return True
        else:
            raise

def unlock_file(file=''):
    open_files = get_open_files()
    server_name = None  # 替换为实际的服务器名称
    g_file=file.lower().replace(wsDir.lower(),'g:')
    print ('g_file',g_file)
    for file_info in open_files:
        #lprint (file_info['pathname'].lower() , g_file,file_info['pathname'].lower(),file.lower())
        if file_info['pathname'].lower() ==  g_file or file_info['pathname'].lower()==file.lower():
            print("该文件被占用")
            detailed_info = get_file_info(server_name, file_info['id'])
            if detailed_info:
                print (file_info['pathname'].lower())
        
                print(f"详细信息 - ID: {detailed_info.fi3_id}, Path: {detailed_info.fi3_pathname}, User: {detailed_info.fi3_username}, Locks: {detailed_info.fi3_num_locks}")
                if is_file_locked(file_info['pathname']) :
                    try:
                        close_shared_file(file_info['pathname'])
                    except:
                        traceback.print_exc()
                    try:
                        close_shared_file(g_file)
                    except:
                        traceback.print_exc()
                else:
                    print("该文件未被锁定")

if  __name__=="__main__":
    unlock_file(r'f:\H\CCC\ep005_sc001_shot0030_chenchangsheng_toufa_cfx.abc')
