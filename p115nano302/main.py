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
        try:
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
                if self.connected_clients:
                    try:
                        await self.broadcast(log_entry)
                    except Exception as e:
                        console.print(f"[error]广播日志失败: {str(e)}[/]")
                else:
                    console.print("[warning]没有连接的WebSocket客户端[/]")
        except Exception as e:
            console.print(f"[error]添加日志失败: {str(e)}[/]")

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.connected_clients.append(websocket)
            console.print(f"[info]新的WebSocket客户端连接，当前连接数: {len(self.connected_clients)}[/]")
            # 发送现有日志
            for log in self.logs:
                try:
                    await websocket.send_json(log)
                except Exception as e:
                    console.print(f"[error]发送历史日志失败: {str(e)}[/]")
        except Exception as e:
            console.print(f"[error]WebSocket连接失败: {str(e)}[/]")

    async def disconnect(self, websocket: WebSocket):
        try:
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)
                await websocket.close()
        except:
            pass

    async def broadcast(self, log_entry: dict):
        if not self.connected_clients:
            return

        disconnected = []
        for client in self.connected_clients:
            try:
                await client.send_json(log_entry)
            except Exception as e:
                console.print(f"[error]发送日志失败: {str(e)}[/]")
                disconnected.append(client)
        
        # 移除断开的客户端
        for client in disconnected:
            if client in self.connected_clients:
                self.connected_clients.remove(client)

# 创建日志管理器实例
log_manager = LogManager()

# WebSocket路由
@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    console.print("[info]收到新的WebSocket连接请求[/]")
    try:
        await websocket.accept()
        log_manager.connected_clients.append(websocket)
        console.print(f"[info]新的WebSocket客户端连接，当前连接数: {len(log_manager.connected_clients)}[/]")
        
        # 发送现有日志
        for log in log_manager.logs:
            try:
                await websocket.send_json(log)
                await asyncio.sleep(0.01)  # 添加小延迟避免消息堆积
            except Exception as e:
                console.print(f"[error]发送历史日志失败: {str(e)}[/]")
                break
        
        # 保持连接
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except Exception as e:
                console.print(f"[warning]WebSocket错误: {str(e)}[/]")
                break
    except Exception as e:
        console.print(f"[error]WebSocket连接错误: {str(e)}[/]")
    finally:
        if websocket in log_manager.connected_clients:
            log_manager.connected_clients.remove(websocket)
        console.print("[info]WebSocket连接关闭[/]")

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
            if ' 302 Found' in msg and 'pickcode=' in msg:
                try:
                    # 使用更简单的方式提取信息
                    parts = msg.split(' - ')
                    if len(parts) >= 4:
                        ip = parts[0].split(':')[0].strip()
                        url = parts[1].strip('"')
                        duration = parts[-1].strip()
                        
                        # 解码URL
                        url = unquote(url.replace('GET ', '').split(' HTTP')[0])
                        
                        # 构造日志消息
                        log_message = f"302跳转 [{ip}]: {url} ({duration})"
                        console.print(f"[debug]发送302日志: {log_message}[/]")
                        
                        # 使用create_task发送日志
                        loop = asyncio.get_event_loop()
                        loop.create_task(log_manager.add_log(log_message, "success"))
                except Exception as e:
                    console.print(f"[error]处理302日志失败: {str(e)}[/]")
                return False

            # 处理其他重要日志
            if any((
                'Starting 302 service' in msg,
                'Cookies length:' in msg,
                'Error:' in msg,
                'Exception in ASGI application' in msg,
            )):
                loop = asyncio.get_event_loop()
                loop.create_task(log_manager.add_log(msg.strip(), "error" if "Exception" in msg else "info"))
                return False
                
            return False
            
        except Exception as e:
            console.print(f"[error]日志过滤器错误: {str(e)}[/]")
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
