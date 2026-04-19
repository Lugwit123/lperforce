import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 创建三维坐标系
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# 定义 3x4x5 的矩阵维度
shape = (3, 4, 5)

# 创建 3x4x5 的矩阵，每个盒子表示一个元素，位置由其序号决定，并根据坐标设置颜色
for i in range(shape[0]):
    for j in range(shape[1]):
        for k in range(shape[2]):
            # 根据坐标设置颜色（颜色与坐标位置相关，例如根据 i, j, k 取值来计算一个颜色）
            color = (i / shape[0], j / shape[1], k / shape[2])  # RGB 颜色按坐标比例分配
            # 在 (i, j, k) 位置绘制一个盒子，颜色根据坐标变化
            ax.bar3d(i, j, k, 0.5, 0.5, 0.5, color=color)
            
            # 计算序号并在盒子表面显示其序号
            idx = i * shape[1] * shape[2] + j * shape[2] + k
            # 将序号标注在盒子的顶部，稍微靠上位置，并多次绘制使其更加清晰
            positions = [
                (i + 0.25, j + 0.25, k + 0.45),
                (i + 0.27, j + 0.25, k + 0.47),
                (i + 0.23, j + 0.25, k + 0.43),
                (i + 0.25, j + 0.27, k + 0.45),
                (i + 0.25, j + 0.23, k + 0.45)
            ]
            for pos in positions:
                ax.text(*pos, f'{idx}', color='black', ha='center', fontsize=10, weight='bold')

# 设置坐标轴的标签
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')

# 设置坐标轴的范围
ax.set_xlim([0, shape[0]])
ax.set_ylim([0, shape[1]])
ax.set_zlim([0, shape[2]])

# 显示图像
plt.show()
