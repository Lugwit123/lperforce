import sys
import os
import stat

def clean_file(maya_file_path):
    with open(maya_file_path, "rb") as f:
        maya_file_lines = f.readlines()
    allowed_lines = ['requires maya',
                    'requires "stereoCamera"',
                    'requires -nodeType "aiOptions"']
    count=str(maya_file_lines[:1000]).count('requires')
    print(maya_file_lines[100:110])
    print("count",count)
    if count<10:
        sys.exit(0)
        print(f"不需要清理{count}")

    new_conent_lines = []

    endLine = 0
    for i,line in enumerate(maya_file_lines):
        needToAdd = False
        line_to_str = line.decode('ascii')
        # print("line_to_str",line_to_str,line_to_str.startswith('requires'))
        
        
        if  line_to_str.startswith('currentUnit'):
            endLine = i
            break
        
        if '-nodeType' in line_to_str:
            continue
        
        if not line_to_str.startswith('requires')  :
            new_conent_lines.append(line)

        else:
            for allowed_line in allowed_lines:
                if line_to_str.startswith(allowed_line):
                    print("allowed_line",allowed_line,line_to_str.startswith(allowed_line))
                    needToAdd = True
                    break
            if needToAdd:
                new_conent_lines.append(line)
                
    new_conent_lines+=maya_file_lines[endLine:]
    print(len(new_conent_lines),len(maya_file_lines))
    os.chmod(maya_file_path, stat.S_IWRITE)  # 在 Windows 上取消只读
    with open(maya_file_path, "wb") as f:
        f.writelines(new_conent_lines)
        return True
        
if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1].endswith(".ma"):
        maya_file_path = sys.argv[1]
    else:
        maya_file_path = r"H:\WXXJDGD\5.Anima final\EP001\ani\ep001_sc001_shot0030_anim.ma"
    clean_file(maya_file_path)

