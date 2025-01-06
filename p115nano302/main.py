import os
import sys
import uvicorn
from fastapi import FastAPI, Request
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
from collections import deque
import re

# 获取当前文件所在目录
BASE_DIR = Path(__file__).resolve().parent

# 创建FastAPI应用
app = FastAPI()

# 设置静态文件和模板
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 日志存储
logs = deque(maxlen=100)

def add_log(message: str, level: str = "info"):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message,
        "level": level
    }
    logs.append(log_entry)
    print(f"{log_entry['timestamp']} {message}")

# 日志过滤器
class UvicornLogFilter(logging.Filter):
    def filter(self, record):
        try:
            msg = record.getMessage()
            
            # 过滤掉不需要的日志
            if any((
                'GET /static/' in msg,
                'GET /favicon.ico' in msg,
                'GET /api/logs' in msg,
                ' 304 ' in msg,
            )):
                return False
                
            # 处理302请求日志
            if ' 302 Found' in msg and 'pickcode=' in msg:
                try:
                    # 提取信息
                    parts = msg.split(' - ')
                    if len(parts) >= 4:
                        ip = parts[0].split(':')[0].strip()
                        url = parts[1].strip('"').replace('GET ', '')
                        url = url.split(' HTTP')[0]
                        duration = parts[-1].strip()
                        
                        # 解码URL并添加日志
                        url = unquote(url)
                        add_log(f"302跳转 [{ip}]: {url} ({duration})", "success")
                except Exception as e:
                    add_log(f"处理302日志失败: {str(e)}", "error")
                return False

            # 处理其他重要日志
            if any((
                'Starting 302 service' in msg,
                'Cookies length:' in msg,
                'Error:' in msg,
                'Exception in ASGI application' in msg,
            )):
                add_log(msg.strip(), "error" if "Exception" in msg else "info")
            
            return False
            
        except Exception as e:
            add_log(f"日志过滤器错误: {str(e)}", "error")
            return False

# API路由
@app.get("/api/logs")
async def get_logs():
    return list(logs)

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def run_302_service():
    try:
        # 获取cookies
        cookies = os.getenv('COOKIES', '')
        if not cookies and os.path.exists('115-cookies.txt'):
            with open('115-cookies.txt', 'r', encoding='utf-8') as f:
                cookies = f.read().strip()
        
        if not cookies:
            add_log("No cookies found. Please set COOKIES environment variable or create 115-cookies.txt file", "error")
            return
            
        if 'UID' not in cookies or 'CID' not in cookies:
            add_log("Invalid cookies format. Must contain UID and CID", "error")
            return
            
        add_log("Starting 302 service...", "success")
        add_log(f"Cookies length: {len(cookies)}", "info")
        
        # 创建302应用
        app_302 = p115nano302.make_application(cookies, debug=True)

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
            access_log=True
        )
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        add_log(f"302服务错误: {str(e)}", "error")
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
