import pandas as pd
import re

# 读取 Excel 文件
file_path = 'D:/Downloads/人员_主机名.xlsx'  # 请根据实际路径修改


departmentList_str='''
    三维制片部(SWZP)
    UE地编(DIPIAN)
    动画一组(ANI1)
    编剧部(BIANJV)
    动画二组(ANI2)
    研发部(YF)
    三维分镜(SWFJ)
    绑定组(RIG)
    模型二组(MOD2)
    TD(TD)
    TA(TA)
    灯光组(LIGHT)
    layout一组(LAY1)
    layout二组(Lay2)
    解算组(CFX)
    二维制片部(EWZP)
    原画组(YH)
    模型一组(MOD1)
    影视后期(HOUQI)
    特效组(FX)
    导演部(DY)
'''



# 去除首尾空白字符和多余空行
lines = [line.strip() for line in departmentList_str.strip().split('\n') if line.strip()]

# 使用正则表达式提取中文名称和缩写
department_dict = {}
for line in lines:
    match = re.match(r'(.+?)\((.+?)\)', line)
    if match:
        name, code = match.groups()
        if name in department_dict:
            # 如果名称已存在，则将其值改为列表，并追加新的缩写
            if isinstance(department_dict[name], list):
                department_dict[name].append(code)
            else:
                department_dict[name] = [department_dict[name], code]
        else:
            department_dict[name] = code

print(department_dict)


def get_userInfos(file_path):
    df = pd.read_excel(file_path, sheet_name=0, header=0)

    # 提取中文名、英文名和部门信息
    data = []

    for index, row in df.iterrows():
        department = row[0]
        people_info = row[1].split('>>') if pd.notna(row[1]) else []
        if len(people_info) == 2:
            chinese_name, english_name = people_info
            data.append((department, chinese_name, english_name))

    userInfos = []
    # 打印提取的信息
    for item in data:
        print(f"部门: {item[0]}, 中文名: {item[1]}, 英文名: {item[2]}",type(item[0]))
        department_item = item[0]
        print (department_item)
        if isinstance(department_item, str):
            department = department_item.strip()
            department=department.split('(')[0]
            department=department_dict.get(department,department)
        userInfos.append((item[2],item[1].replace('\u3000',''),department))

    return userInfos

if __name__ == '__main__':
    print (get_userInfos(file_path))


