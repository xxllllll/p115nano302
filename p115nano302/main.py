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
    return list(logs)

class UvicornLogFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        
        # 过滤掉常规的访问日志
        if any((
            'GET /api/logs' in msg,
            'GET /static/' in msg,
            'GET / HTTP' in msg,
            ' 304 ' in msg,  # 静态资源未修改的响应
            ' 200 ' in msg   # 成功的响应
        )):
            return False
            
        # 只保留重要的系统日志和302跳转相关的日志
        return any((
            '302' in msg,
            '404' in msg,
            'Starting' in msg,
            'Application' in msg,
            'Error' in msg,
            'Exception' in msg,
            'Cookies length' in msg,
            'pickcode' in msg.lower(),
            'Uvicorn running' in msg,
            'Started server process' in msg,
            'Waiting for application startup' in msg,
            'Application startup complete' in msg
        ))

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
        
        from p115nano302 import make_application
        app_302 = make_application(
            cookies, 
            debug=True,
            cache_url=True  # 启用URL缓存功能，相当于命令行的 -cu 参数
        )

        # 配置uvicorn日志
        log_config = uvicorn.config.LOGGING_CONFIG
        log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(message)s"
        log_config["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
        
        config = uvicorn.Config(
            app_302, 
            host="0.0.0.0", 
            port=8000,
            log_config=log_config,
            access_log=False,
            proxy_headers=True,
            server_header=False,
            forwarded_allow_ips="*",
            timeout_graceful_shutdown=1
        )
        server = uvicorn.Server(config)
        
        # 添加日志过滤器
        for handler in logging.getLogger("uvicorn").handlers:
            handler.addFilter(UvicornLogFilter())
        
        await server.serve()
    except Exception as e:
        add_log(f"Error in 302 service: {str(e)}", "error")
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
        access_log=False
    )
    server = uvicorn.Server(config)
    
    # 添加日志过滤器
    for handler in logging.getLogger("uvicorn").handlers:
        handler.addFilter(UvicornLogFilter())
    
    await server.serve()

async def main():
    # 并发运行两个服务
    await asyncio.gather(
        run_302_service(),
        run_web_interface()
    )

if __name__ == "__main__":
    asyncio.run(main())