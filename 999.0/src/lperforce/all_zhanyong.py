import os

def is_file_locked(filepath):
    """
    检查文件是否被锁定。
    
    :param filepath: 文件路径
    :return: 如果文件被锁定返回 True，否则返回 False
    """
    locked = None
    try:
        file_object = open(filepath, 'a')
        file_object.close()
        locked = False
    except IOError:
        locked = True
    return locked

# 示例
file_path = r'f:\共享盘\H\JZXCL\5.Anima final\anim\ep037\mov\ep037_sc001_shot0110_anim.mov'
if is_file_locked(file_path):
    print(f"文件 {file_path} 被锁定。")
else:
    print(f"文件 {file_path} 未被锁定。")
