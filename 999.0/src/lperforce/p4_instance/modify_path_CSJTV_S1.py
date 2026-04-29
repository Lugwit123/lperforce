import os
import glob
import codecs
def modify_ma_files_with_glob(source_dir, target_dir, old_path, new_path):
    # 检查源目录是否存在
    if not os.path.exists(source_dir):
        print(f"源目录不存在: {source_dir}")
        return

    # 创建目标目录（如果不存在）
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"已创建目标目录: {target_dir}")

    # 使用glob获取所有.ma文件，递归遍历子目录
    pattern = os.path.join(source_dir, '**', '*.nk')
    ma_files = glob.glob(pattern, recursive=True)

    if not ma_files:
        print(f"在目录 {source_dir} 中未找到任何 .ma 文件。")
        return

    for source_file_path in ma_files:
        try:
            # 读取文件内容
            with open(source_file_path, 'r', encoding='gbk') as f:
                content = f.read()

            # 替换路径
            modified_content = content.replace(old_path, new_path)

            # 构建目标文件路径
            file_name = os.path.basename(source_file_path)
            target_file_path = os.path.join(target_dir, file_name)

            # 写入修改后的内容到目标文件
            with open(target_file_path, 'w', encoding='gbk') as f:
                f.write(modified_content)

            print(f"已修改并保存: {target_file_path}")
        except Exception as e:
            print(f"处理文件 {source_file_path} 时出错: {e}")

if __name__ == "__main__":
    # 源目录路径
    source_directory = r"G:/Project"

    # 目标目录路径
    target_directory = r"D:\xiugai"

    # 要替换的旧路径和新路径
    old_path_str = "H:/Project"
    new_path_str = "Z:/Project"

    modify_ma_files_with_glob(source_directory, target_directory, old_path_str, new_path_str)
