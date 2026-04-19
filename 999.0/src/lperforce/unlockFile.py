import ctypes
from ctypes import wintypes
import subprocess
import os
import win32api
import win32con
import win32file
import pywintypes

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
        # 错误代码 32 表示文件正在被使用
        if e.winerror == 32:
            return True
        else:
            raise

def unlock_file(file=''):
    open_files = get_open_files()
    server_name = None  # 替换为实际的服务器名称
    g_file=file.lower().replace(r'f:\共享盘\h','g:')
    print ('g_file',g_file)
    for file_info in open_files:
        if file_info['pathname'].lower() ==  g_file or file_info['pathname'].lower()==file.lower():
            print("该文件被占用")
            detailed_info = get_file_info(server_name, file_info['id'])
            if detailed_info:
                print (file_info['pathname'].lower())
        
                print(f"详细信息 - ID: {detailed_info.fi3_id}, Path: {detailed_info.fi3_pathname}, User: {detailed_info.fi3_username}, Locks: {detailed_info.fi3_num_locks}")
                if is_file_locked(file_info['pathname']) :
                    print("该文件被锁定,现在为你解锁文件")
                    #subprocess.run(['net', 'file', str(detailed_info.fi3_id), '/close'])
                    subprocess.run(['net', 'file', str(detailed_info.fi3_num_locks), '/close'])
                else:
                    print("该文件未被锁定")

if  __name__=="__main__":
    unlock_file(r'f:\共享盘\H\CCC\ep005_sc001_shot0030_chenchangsheng_toufa_cfx.abc')
