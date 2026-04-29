import asyncio
import websockets



async def handler(websocket, path):
    client_ip = websocket.remote_address[0]
    print(f"客户端已连接: {client_ip}")

    try:
        async for message in websocket:
            print(f"收到来自 {client_ip} 的消息: {message}")
            # 立即回复客户端
            response = f"服务器收到: {message}"
            await websocket.send(response)
            print(f"已回复客户端 {client_ip}: {response}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"客户端 {client_ip} 已断开连接")


# 定义服务器的主函数
async def main():
    # 设置服务器的主机和端口
    host = '0.0.0.0'  # 监听所有可用的网络接口
    port = 8765

    async with websockets.serve(handler, host, port):
        print(f"WebSocket 服务器正在运行，监听 {host}:{port}")
        await asyncio.Future()  # 运行直到手动停止

print(__name__)
if __name__ == "__main__":
    asyncio.run(main())
