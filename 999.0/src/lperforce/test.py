import threading
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

import random

# 计算密集型任务
def cpu_task(n):
    count = 0
    for i in range(n):
        count += i * i
    return count

# IO密集型任务
def io_task(n):
    for _ in range(n):
        time.sleep(0.001)

# 复杂运算任务：纯Python实现矩阵乘法
def matrix_multiply_task(size):
    # 生成两个随机矩阵
    a = [[random.random() for _ in range(size)] for _ in range(size)]
    b = [[random.random() for _ in range(size)] for _ in range(size)]
    # 结果矩阵初始化
    result = [[0.0 for _ in range(size)] for _ in range(size)]
    # 矩阵乘法
    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] += a[i][k] * b[k][j]

def test_single_thread(task, n_tasks, n):
    start = time.time()
    for _ in range(n_tasks):
        task(n)
    end = time.time()
    print(f"单线程耗时: {end - start:.4f} 秒")


def test_multi_thread(task, n_tasks, n, n_threads):
    start = time.time()
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        futures = [executor.submit(task, n) for _ in range(n_tasks)]
        for f in futures:
            f.result()
    end = time.time()
    print(f"多线程({n_threads}线程)耗时: {end - start:.4f} 秒")


def test_multi_process(task, n_tasks, n, n_processes):
    start = time.time()
    with Pool(processes=n_processes) as pool:
        pool.starmap(task, [(n,) for _ in range(n_tasks)])
    end = time.time()
    print(f"多进程({n_processes}进程)耗时: {end - start:.4f} 秒")


if __name__ == "__main__":
    n_tasks = 20
    n = 1000000
    n_threads = 20

    print("--- 计算密集型任务对比 ---")
    test_single_thread(cpu_task, n_tasks, n)
    test_multi_thread(cpu_task, n_tasks, n, n_threads)

    print("\n--- IO密集型任务对比 ---")
    test_single_thread(io_task, n_tasks, 100)
    test_multi_thread(io_task, n_tasks, 100, n_threads)

    print("\n--- 复杂运算任务（矩阵乘法）对比 ---")
    matrix_size = 100  # 可根据机器性能调整
    test_single_thread(matrix_multiply_task, n_tasks, matrix_size)
    test_multi_thread(matrix_multiply_task, n_tasks, matrix_size, n_threads)
    test_multi_process(matrix_multiply_task, n_tasks, matrix_size, n_threads)
