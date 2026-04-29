from P4 import P4, P4Exception

# Perforce服务器配置
P4PORT = "192.168.110.26:1666"  # 更新为你的Perforce服务器地址
P4USER = "qqfeng"          # 一个有权限的管理员用户名
P4PASSWD = ""  # 管理员密码
NEW_PASSWORD = ""  # 要设置的新密码

p4 = P4()
p4.port = P4PORT
p4.user = P4USER
p4.password = P4PASSWD

try:
    p4.connect()
    p4.run_login()

    # 获取所有用户
    users = p4.run_users()

    for user in users:
        username = user['User']
        # 设置新密码，使用 'p4 passwd' 命令
        try:
            p4.input = [NEW_PASSWORD, NEW_PASSWORD]  # 输入新密码两次
            p4.run_passwd("-P", NEW_PASSWORD, username)
            print(f"Password reset for {username}")
        except P4Exception as e:
            print(f"Failed to reset password for {username}: {e}")
    p4.disconnect()
except P4Exception as e:
    print(f"Error: {e}")
finally:
    if p4.connected():
        p4.disconnect()
