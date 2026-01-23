import asyncio
import websockets
from aiohttp import web
import json
import pyautogui
import threading
import time

# 全局变量存储鼠标位置
mouse_positions = {"x": 0, "y": 0}
clients = set()

# 鼠标监听线程


def mouse_listener():
    """监听鼠标点击事件"""
    try:
        import pynput
        from pynput import mouse

        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left:
                # 获取屏幕尺寸
                screen_width, screen_height = pyautogui.size()

                # 归一化坐标
                norm_x = x / screen_width
                norm_y = y / screen_height

                # 更新全局变量
                mouse_positions["x"] = norm_x
                mouse_positions["y"] = norm_y

                # 打印调试信息
                print(
                    f"鼠标点击位置: ({x}, {y}) -> 归一化: ({norm_x:.3f}, {norm_y:.3f})")

        # 创建鼠标监听器
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    except ImportError:
        print("请安装pynput库: pip install pynput")
        # 如果没有pynput，使用简单的鼠标模拟
        while True:
            time.sleep(0.1)
            # 模拟鼠标点击（实际使用时请安装pynput）
            mouse_positions["x"] = (mouse_positions["x"] + 0.1) % 1
            mouse_positions["y"] = (mouse_positions["y"] + 0.05) % 1

# SSE处理器


async def sse_handler(request):
    """处理SSE连接"""
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'text/event-stream'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Access-Control-Allow-Origin'] = '*'

    await response.prepare(request)

    client_id = id(response)
    clients.add(response)
    print(f"新客户端连接: {client_id}")

    try:
        # 发送初始数据
        await response.write(f"data: {json.dumps(mouse_positions)}\n\n".encode())

        # 持续发送更新
        last_pos = None
        while True:
            await asyncio.sleep(0.1)  # 10Hz更新频率

            current_pos = (mouse_positions["x"], mouse_positions["y"])
            if current_pos != last_pos:
                data = json.dumps({
                    "x": mouse_positions["x"],
                    "y": mouse_positions["y"],
                    "timestamp": time.time()
                })
                await response.write(f"data: {data}\n\n".encode())
                last_pos = current_pos

    except Exception as e:
        print(f"客户端断开: {client_id}, 错误: {e}")
    finally:
        clients.remove(response)

    return response

# 主页处理器


async def index_handler(request):
    """提供测试页面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SSE鼠标位置测试</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #container { display: flex; gap: 20px; }
            #left-panel { flex: 1; }
            #right-panel { flex: 1; }
            #mouse-display { 
                border: 2px solid #333;
                width: 400px;
                height: 300px;
                position: relative;
                background: #f0f0f0;
                margin-top: 20px;
            }
            #cursor {
                position: absolute;
                width: 10px;
                height: 10px;
                background: red;
                border-radius: 50%;
                transform: translate(-50%, -50%);
            }
            .coord { margin: 10px 0; }
            .status { margin: 10px 0; padding: 5px; }
            .connected { background: #d4edda; }
            .disconnected { background: #f8d7da; }
        </style>
    </head>
    <body>
        <h1>SSE鼠标位置实时显示</h1>
        <div id="container">
            <div id="left-panel">
                <h2>控制面板</h2>
                <button onclick="connectSSE()">连接SSE</button>
                <button onclick="disconnectSSE()">断开连接</button>
                
                <div class="coord">
                    <h3>鼠标位置：</h3>
                    <p>X: <span id="x-value">0</span></p>
                    <p>Y: <span id="y-value">0</span></p>
                </div>
                
                <div class="coord">
                    <h3>原始像素坐标：</h3>
                    <p>X: <span id="raw-x">0</span> px</p>
                    <p>Y: <span id="raw-y">0</span> px</p>
                </div>
                
                <div id="status" class="status disconnected">
                    状态：未连接
                </div>
            </div>
            
            <div id="right-panel">
                <h2>鼠标位置可视化</h2>
                <div id="mouse-display">
                    <div id="cursor"></div>
                </div>
                <p>红色圆点表示鼠标点击位置</p>
            </div>
        </div>
        
        <script src="/static/sse-client.js"></script>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

# 启动服务器


async def main():
    app = web.Application()

    # 添加路由
    app.router.add_get('/', index_handler)
    app.router.add_get('/sse', sse_handler)

    # 启动鼠标监听线程
    mouse_thread = threading.Thread(target=mouse_listener, daemon=True)
    mouse_thread.start()

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, 'localhost', 8693)

    print(f"SSE服务器启动在: http://localhost:8693")
    print("请在浏览器中访问以上地址测试")
    print("点击页面上的'连接SSE'按钮开始接收鼠标位置")

    await site.start()

    # 保持服务器运行
    await asyncio.Future()  # 永久运行

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务器关闭")
