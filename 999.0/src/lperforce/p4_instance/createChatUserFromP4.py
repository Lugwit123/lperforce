import os
import sys
import json
import logging
import traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

import requests
from P4 import P4, P4Exception

# 添加自定义模块路径
sys.path.append(r'D:\TD_Depot\plug_in\Python\py39Lib')

import Lugwit_Module as LM
from lperforce import (loginP4, p4_baselib, P4Lib)
from lperforce.P4LoginInfoModule import p4_loginInfo

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("batch_register.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 后端API配置
BASE_URL = "http://127.0.0.1:1026"
REGISTER_ENDPOINT = f"{BASE_URL}/register"

# 默认配置
DEFAULT_PASSWORD = "666"
DEFAULT_ROLE = "user"
DEFAULT_GROUPS = ["default_group"]  # 替换为实际存在的组名

# 自定义用户配置
# 在这里为特定用户定义自定义的密码、角色和组
CUSTOM_USER_CONFIG = {
    "alice01": {
        "password": "password1",
        "role": "admin",

    },
    # 可以在此处添加更多用户的自定义配置
    # "bob02": {
    #     "password": "securePass123",
    #     "role": "user",
    #     "groups": ["group_users"]
    # },
}

def get_p4_connection():
    """
    初始化并返回一个P4连接。
    """
    try:
        p4 = loginP4.p4_login(
            userName=p4_loginInfo['project']['User'],
            port=p4_loginInfo['project']['port'],
            wsDir='H:/'
        )
        logger.info("成功登录到 Perforce 服务器")
        return p4
    except P4Exception as e:
        logger.error("登录 Perforce 失败:")
        for error in e.errors:
            logger.error(error)
        sys.exit(1)

def get_p4_users(p4_connection):
    """
    从P4获取所有用户的用户名和全名。
    """
    try:
        users = p4_connection.run_users()
        user_list = []
        for user in users:
            username = user.get('User', 'N/A')
            fullname = user.get('FullName', 'N/A')
            if username != 'N/A' and fullname != 'N/A':
                user_list.append({"username": username, "fullname": fullname})
            else:
                logger.warning(f"跳过用户，缺少必要信息: {user}")
        logger.info(f"获取到 {len(user_list)} 个有效的P4用户")
        return user_list
    except P4Exception as e:
        logger.error("获取P4用户信息时出错:")
        for error in e.errors:
            logger.error(error)
        return []

def register_user(user, retries=3, delay=5):
    """
    注册单个用户到后端API，支持重试机制。
    """
    username = user.get("username")
    fullname = user.get("fullname")
    email = f"{username}@qq.com"

    # 检查是否有自定义配置
    user_config = CUSTOM_USER_CONFIG.get(username, {})
    password = user_config.get("password", DEFAULT_PASSWORD)


    user_data = {
        "username": username,
        "nickname": fullname,  # P4的全名作为昵称
        "password": password,
        "email": email,
        "role": 'user',
    }

    headers = {"Content-Type": "application/json"}

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(REGISTER_ENDPOINT, data=json.dumps(user_data), headers=headers)
            if response.status_code == 200:
                logger.info(f"用户 '{username}' 注册成功: {response.json()}")
                return {"username": username, "status": "success", "detail": response.json()}
            else:
                logger.error(f"用户 '{username}' 注册失败 (尝试 {attempt}/{retries}): {response.status_code}, {response.text}")
                # 打印详细的错误信息
                try:
                    error_details = response.json()
                    logger.error(f"错误详情: {error_details}")
                except json.JSONDecodeError:
                    logger.error("无法解析错误详情为JSON格式")
        except Exception as e:
            logger.error(f"用户 '{username}' 注册过程中出错 (尝试 {attempt}/{retries}): {e}")
            logger.error(traceback.format_exc())

        if attempt < retries:
            logger.info(f"等待 {delay} 秒后重试用户 '{username}' 的注册")
            time.sleep(delay)

    # 如果所有尝试都失败
    logger.error(f"用户 '{username}' 注册最终失败")
    return {"username": username, "status": "failed", "detail": f"注册失败，已尝试 {retries} 次"}

def batch_register_users(users, max_workers=10):
    """
    批量注册用户，支持并发处理。
    """
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_user = {executor.submit(register_user, user): user for user in users}
        for future in as_completed(future_to_user):
            user = future_to_user[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                logger.error(f"用户 '{user['username']}' 注册时产生异常: {exc}")
                results.append({"username": user['username'], "status": "exception", "detail": str(exc)})
    return results

def load_users_from_p4():
    """
    获取P4用户列表。
    """
    p4_conn = get_p4_connection()
    p4_users = get_p4_users(p4_conn)
    p4_conn.disconnect()
    logger.info("已断开Perforce连接")
    return p4_users

if __name__ == "__main__":
    logger.info("开始批量注册用户...")

    # 获取P4用户列表
    p4_users = load_users_from_p4()

    if not p4_users:
        logger.error("未获取到任何P4用户，退出脚本。")
        sys.exit(1)

    # 执行批量注册
    registration_results = batch_register_users(p4_users, max_workers=10)

    # 汇总结果
    success_count = sum(1 for r in registration_results if r["status"] == "success")
    failed_count = sum(1 for r in registration_results if r["status"] == "failed")
    error_count = sum(1 for r in registration_results if r["status"] == "error")
    exception_count = sum(1 for r in registration_results if r["status"] == "exception")

    logger.info(f"批量注册完成: 成功 {success_count}, 失败 {failed_count}, 错误 {error_count}, 异常 {exception_count}")

    # 可选：将结果保存到文件
    with open("registration_results.json", "w", encoding="utf-8") as f:
        json.dump(registration_results, f, ensure_ascii=False, indent=4)

    logger.info("注册结果已保存到 'registration_results.json'")

