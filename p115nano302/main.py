import os
import sys
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import unquote
from datetime import datetime
from collections import deque
import asyncio
import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from pathlib import Path
import p115nano302
from typing import Optional
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

# 修改日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(
        console=console,
        show_path=False,
        enable_link_path=False,
        markup=True,
        rich_tracebacks=True
    )]
)

logger = logging.getLogger(__name__)

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

# 日志存储
logs = deque(maxlen=100)

def add_log(message: str, level: str = "info"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "message": message,
        "level": level
    }
    logs.append(log_entry)
    
    if level == "error":
        console.print(f"[timestamp]{timestamp}[/] [error]{message}[/]")
    elif level == "warning":
        console.print(f"[timestamp]{timestamp}[/] [warning]{message}[/]")
    elif level == "success":
        console.print(f"[timestamp]{timestamp}[/] [success]{message}[/]")
    else:
        console.print(f"[timestamp]{timestamp}[/] [info]{message}[/]")

def log_request(host: str, method: str, path: str, status_code: int):
    try:
        path = unquote(path)
    except:
        pass
    add_log(f"{host} - {method} {path} - {status_code}")

# 路由处理
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/logs")
async def get_logs():
    return [{
        "timestamp": log["timestamp"],
        "message": log["message"],
        "level": log["level"],
        "formatted": f"[{log['timestamp']}] [{log['level']}] {log['message']}"
    } for log in logs]

class UvicornLogFilter(logging.Filter):
    def __init__(self):
        super().__init__()
    
    def filter(self, record):
        msg = record.getMessage()
        
        # 过滤掉不需要的日志
        if any((
            'GET /api/logs' in msg,
            'GET /static/' in msg,
            'GET / HTTP' in msg,
            ' 304 ' in msg,
        )):
            return False
            
        # 如果是302请求日志，添加到我们的日志系统
        if ' - 302 Found - ' in msg and 'pickcode=' in msg:
            try:
                # 提取URL和响应时间
                parts = msg.split(' - ')
                url = parts[1].strip('"')  # 获取URL部分
                duration = parts[-1].strip()  # 获取响应时间
                url = unquote(url.replace('[0m', '').strip())  # 清理URL
                add_log(f"302跳转: {url} ({duration})", "success")
            except Exception as e:
                add_log(f"日志解析错误: {str(e)}", "error")
            return False  # 不显示原始日志
            
        # 对于其他日志，如果包含重要信息则记录
        if any((
            'Starting 302 service' in msg,
            'Cookies length' in msg,
            'Error' in msg,
            'Exception' in msg,
        )):
            add_log(msg, "info")
            
        return True

async def run_302_service():
    try:
        # 首先尝试从环境变量获取cookies
        cookies = os.getenv('COOKIES', '')
        
        # 如果环境变量中没有，则尝试从文件读取
        if not cookies and os.path.exists('115-cookies.txt'):
            with open('115-cookies.txt', 'r', encoding='utf-8') as f:
                cookies = f.read().strip()
        
        # 如果还是没有cookies，记录错误并退出
        if not cookies:
            add_log("No cookies found. Please set COOKIES environment variable or create 115-cookies.txt file", "error")
            return
            
        # 验证cookies不为空且格式正确
        if not cookies or 'UID' not in cookies or 'CID' not in cookies:
            add_log("Invalid cookies format. Must contain UID and CID", "error")
            return
            
        add_log("Starting 302 service...", "success")
        add_log(f"Cookies length: {len(cookies)}", "info")
        
        make_application = p115nano302.make_application
        app_302 = make_application(
            cookies, 
            debug=True,
            cache_url=True  # 启用URL缓存功能，相当于命令行的 -cu 参数
        )

        # 配置uvicorn日志
        log_config = uvicorn.config.LOGGING_CONFIG
        # 使用简单的日志格式
        log_config["formatters"]["access"]["fmt"] = '%(asctime)s - %(message)s'
        log_config["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
        
        config = uvicorn.Config(
            app_302, 
            host="0.0.0.0", 
            port=8000,
            log_config=log_config,
            access_log=True,
            proxy_headers=True,
            server_header=False,
            forwarded_allow_ips="*",
            timeout_graceful_shutdown=1
        )
        server = uvicorn.Server(config)
        
        # 添加日志过滤器到所有相关的日志处理器
        log_filter = UvicornLogFilter()
        for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers:
                handler.addFilter(log_filter)
        
        await server.serve()
    except Exception as e:
        add_log(f"302服务错误: {str(e)}", "error")
        raise

async def run_web_interface():
    # 配置uvicorn日志
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(message)s"
    log_config["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8001,
        log_config=log_config,
        access_log=False  # 关闭Web界面的访问日志
    )
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    # 并发运行两个服务
    await asyncio.gather(
        run_302_service(),
        run_web_interface()
    )

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
