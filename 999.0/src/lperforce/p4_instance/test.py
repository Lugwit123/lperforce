import nuke
import os
import sys

def modify_file(file_path):
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在。")
        return

    # 打开 Nuke 文件
    nuke.scriptOpen(file_path)

    # 遍历所有节点
    for node in nuke.allNodes():
        for knob_name in node.knobs():
            knob = node[knob_name]
            if knob.Class() == 'File_Knob':  # 检查是否为文件路径
                value = knob.value()
                if "H:" in value:  # 如果路径包含 H:
                    new_value = value.replace("H:", "Z:")
                    knob.setValue(new_value)
                    print(f"修改节点 {node.name()} 的属性 {knob_name}: {value} -> {new_value}")

    # 保存修改后的文件
    output_file = file_path.replace(".nk", "_modified.nk")
    nuke.scriptSaveAs(output_file)
    print(f"文件已保存为 {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请提供 Nuke 文件路径作为参数。")
    else:
        modify_file(sys.argv[1])
