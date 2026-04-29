import xlwings as xw
from pypinyin import pinyin, Style

# 使用 xlwings 打开 Excel 应用，并隐藏界面
with xw.App(visible=False, add_book=False) as app:
    # 打开 Excel 文件
    file_path = 'D:/Downloads/新建 XLSX 工作表.xlsx'  # 将此路径更改为你的文件路径
    wb = app.books.open(file_path)
    sheet = wb.sheets[0]  # 假设要操作的是第一个工作表

    # 获取人员列数据
    personnel_column = sheet['B:B'].value

    # 过滤掉空值（NoneType）
    personnel_column = [name for name in personnel_column if name is not None]

    # 将中文名转换为拼音
    pinyin_names = [p[0] for p in pinyin(personnel_column, style=Style.NORMAL)]

    # 将中文名和拼音结合:
    updated_personnel_column = []
    for i, name in enumerate(personnel_column):
        updated_personnel_column.append(name + '>>' + pinyin_names[i])

    # 确保 updated_personnel_column 是一个列向量
    updated_personnel_column = [[item] for item in updated_personnel_column]

    # 将更新后的数据写入新的列
    sheet['C:C'].value = updated_personnel_column

    # 保存新的 Excel 文件
    wb.save('updated_file.xlsx')
