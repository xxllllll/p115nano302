import os
import sys
import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import unquote
from datetime import datetime
import asyncio
import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from pathlib import Path
import p115nano302
import json
from typing import List, Dict, Any
import re

# 获取当前文件所在目录
BASE_DIR = Path(__file__).resolve().parent

# 自定义主题
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green",
    "timestamp": "dim blue"
})

console = Console(theme=custom_theme)

# 创建FastAPI应用
app = FastAPI()

# 确保静态文件和模板目录存在
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"
static_dir.mkdir(parents=True, exist_ok=True)
templates_dir.mkdir(parents=True, exist_ok=True)

# 设置静态文件和模板
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# 日志管理类
class LogManager:
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self.max_logs = 100
        self.connected_clients: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def add_log(self, message: str, level: str = "info"):
        async with self._lock:
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": message,
                "level": level
            }
            
            # 添加日志到列表
            self.logs.append(log_entry)
            if len(self.logs) > self.max_logs:
                self.logs.pop(0)
            
            # 打印到控制台
            console.print(f"[timestamp]{log_entry['timestamp']}[/] [{level}]{message}[/]")
            
            # 广播到所有连接的WebSocket客户端
            await self.broadcast(log_entry)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connected_clients.append(websocket)
        # 发送现有日志
        for log in self.logs:
            await websocket.send_json(log)

    async def disconnect(self, websocket: WebSocket):
        try:
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)
                await websocket.close()
        except:
            pass

    async def broadcast(self, log_entry: dict):
        disconnected_clients = []
        for client in self.connected_clients:
            try:
                await asyncio.wait_for(client.send_json(log_entry), timeout=1.0)
            except Exception as e:
                console.print(f"[error]广播日志失败: {str(e)}[/]")
                disconnected_clients.append(client)
        
        # 移除断开的客户端
        for client in disconnected_clients:
            try:
                await self.disconnect(client)
            except:
                pass

# 创建日志管理器实例
log_manager = LogManager()

# WebSocket路由
@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await log_manager.connect(websocket)
    try:
        while True:
            try:
                # 每5秒发送一次心跳
                await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            except asyncio.TimeoutError:
                try:
                    # 发送心跳
                    await websocket.send_text('ping')
                except:
                    break
            except:
                break
    finally:
        await log_manager.disconnect(websocket)

# 路由处理
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 日志过滤器
class UvicornLogFilter(logging.Filter):
    def filter(self, record):
        try:
            msg = record.getMessage()
            
            # 过滤掉不需要的日志
            if any((
                'GET /static/' in msg,
                'GET /favicon.ico' in msg,
                ' 304 ' in msg,
                'WebSocket /ws/logs' in msg,
                'connection open' in msg,
                'connection closed' in msg
            )):
                return False
                
            # 处理302请求日志
            if ' 302 Found' in msg:
                try:
                    # 修改正则表达式以更准确地匹配日志格式
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+):\d+ - "GET (.*?) HTTP/1\.1" - 302 Found - ([\d.]+) ms', msg)
                    if match:
                        ip = match.group(1)
                        url = match.group(2)
                        duration = match.group(3)
                        url = unquote(url)
                        if 'pickcode=' in url:
                            asyncio.create_task(log_manager.add_log(
                                f"302跳转 [{ip}]: {url} ({duration} ms)", 
                                "success"
                            ))
                    return False
                except Exception as e:
                    asyncio.create_task(log_manager.add_log(f"日志解析错误: {str(e)}", "error"))
                    return False

            # 处理其他重要日志
            if any((
                'Starting 302 service' in msg,
                'Cookies length:' in msg,
                'Error:' in msg,
                'Exception' in msg,
            )):
                asyncio.create_task(log_manager.add_log(msg.strip(), "info"))
                return False
                
            # 记录所有未被过滤的日志用于调试
            if not any((
                'GET /' in msg,
                'WebSocket' in msg
            )):
                asyncio.create_task(log_manager.add_log(f"其他日志: {msg.strip()}", "info"))
            
            return False  # 返回False表示不在控制台显示原始日志
            
        except Exception as e:
            asyncio.create_task(log_manager.add_log(f"日志过滤器错误: {str(e)}", "error"))
            return False

async def run_302_service():
    try:
        # 获取cookies
        cookies = os.getenv('COOKIES', '')
        if not cookies and os.path.exists('115-cookies.txt'):
            with open('115-cookies.txt', 'r', encoding='utf-8') as f:
                cookies = f.read().strip()
        
        if not cookies:
            await log_manager.add_log(
                "No cookies found. Please set COOKIES environment variable or create 115-cookies.txt file", 
                "error"
            )
            return
            
        if 'UID' not in cookies or 'CID' not in cookies:
            await log_manager.add_log("Invalid cookies format. Must contain UID and CID", "error")
            return
            
        await log_manager.add_log("Starting 302 service...", "success")
        await log_manager.add_log(f"Cookies length: {len(cookies)}", "info")
        
        # 创建302应用
        app_302 = p115nano302.make_application(
            cookies, 
            debug=True,
            cache_url=True
        )

        # 配置日志
        log_filter = UvicornLogFilter()
        for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
            logger = logging.getLogger(logger_name)
            logger.addFilter(log_filter)

        config = uvicorn.Config(
            app_302,
            host="0.0.0.0",
            port=8000,
            log_config=uvicorn.config.LOGGING_CONFIG,
            access_log=True,
            proxy_headers=True,
            server_header=False,
            forwarded_allow_ips="*",
            timeout_graceful_shutdown=1
        )
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        await log_manager.add_log(f"302服务错误: {str(e)}", "error")
        raise

async def run_web_interface():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8001,
        log_config=None,
        access_log=False
    )
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await asyncio.gather(
        run_302_service(),
        run_web_interface()
    )

if __name__ == "__main__":
    asyncio.run(main())
