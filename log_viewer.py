from flask import Flask, render_template_string
import os
import re
import html
from urllib.parse import unquote

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🌰Emby 302 Logs</title>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .log-entry {
            transition: background-color 0.2s;
            font-family: 'Cascadia Code', 'Source Code Pro', Consolas, monospace;
            padding: 2px 8px;
            border-bottom: 1px solid #f0f0f0;
        }
        .log-entry:hover {
            background-color: #f3f4f6;
        }
        .log-info { color: #3b82f6; }
        .log-error { color: #ef4444; }
        .log-warning { color: #f59e0b; }
        .log-debug { color: #6b7280; }
        .log-time { color: #6b7280; }
        .log-ip { color: #8b5cf6; }
        .log-method { color: #059669; }
        .log-status { color: #d97706; }
        .log-duration { color: #059669; }
        .animate-fade {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .title-emoji {
            font-size: 1.5em;
            margin-right: 0.3em;
        }
        .log-container-wrapper {
            height: calc(100vh - 200px);  /* 动态高度 */
            min-height: 400px;
            background-color: white;
            border: 1px solid #e5e7eb;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
        }
        #log-container {
            flex: 1;
            overflow-y: auto;
            font-size: 0.875rem;
            line-height: 1.5;
            padding: 0.5rem 0;
            background-color: #ffffff;
        }
        .log-empty {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #6b7280;
            font-style: italic;
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen p-4">
    <div class="max-w-7xl mx-auto">
        <div class="bg-white rounded-lg shadow-sm p-4 mb-4">
            <div class="flex justify-between items-center">
                <h1 class="text-2xl font-bold text-gray-800 flex items-center">
                    <span class="title-emoji">🌰</span>
                    <span>Emby 302 Logs</span>
                </h1>
                <div class="space-x-2">
                    <button onclick="refreshLogs()" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded transition duration-200">
                        刷新日志
                    </button>
                    <button onclick="clearLogs()" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded transition duration-200">
                        清空显示
                    </button>
                </div>
            </div>
        </div>
        
        <div class="log-container-wrapper">
            <div id="log-container" class="relative">
                {{ logs | safe }}
            </div>
        </div>
        
        <div class="mt-4 text-gray-600 text-sm flex space-x-4">
            <span>自动刷新间隔：5秒</span>
            <span>显示最近1000行日志</span>
        </div>
    </div>

    <script>
        function refreshLogs() {
            fetch('/logs')
                .then(response => response.text())
                .then(data => {
                    const container = document.getElementById('log-container');
                    container.innerHTML = data;
                    container.scrollTop = container.scrollHeight;
                });
        }
        
        function clearLogs() {
            document.getElementById('log-container').innerHTML = '';
        }
        
        // 自动刷新
        setInterval(refreshLogs, 5000);
        
        // 首次加载时滚动到底部
        window.onload = function() {
            const container = document.getElementById('log-container');
            container.scrollTop = container.scrollHeight;
        }
    </script>
</body>
</html>
"""

def clean_ansi(text):
    """移除ANSI转义序列"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def decode_url(match):
    """解码URL编码的文件名"""
    encoded = match.group(1)
    try:
        return unquote(encoded)
    except:
        return encoded

def format_log_line(line):
    """格式化日志行，添加颜色和样式"""
    # 处理乱码
    try:
        line = line.encode('latin1').decode('utf-8')
    except:
        try:
            line = line.encode('latin1').decode('gbk')
        except:
            pass
    
    # 移除ANSI转义序列
    line = clean_ansi(line)
    
    # 转义HTML特殊字符
    line = html.escape(line)
    
    # 解码URL编码的文件名
    line = re.sub(r'GET /([^?\s]+)\?', lambda m: f'GET /{unquote(m.group(1))}?', line)
    
    # 格式化不同部分
    # 处理时间戳
    line = re.sub(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', r'<span class="log-time">\1</span>', line)
    
    # 处理IP地址
    line = re.sub(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)', r'<span class="log-ip">\1</span>', line)
    
    # 处理HTTP方法
    line = re.sub(r'(GET|POST|PUT|DELETE|HEAD)', r'<span class="log-method">\1</span>', line)
    
    # 处理状态码
    line = re.sub(r'(302 Found)', r'<span class="log-status">\1</span>', line)
    
    # 处理响应时间
    line = re.sub(r'(\d+\.\d+) ms', r'<span class="log-duration">\1 ms</span>', line)
    
    # 根据日志级别添加颜色
    if 'INFO' in line:
        css_class = 'log-info'
    elif 'ERROR' in line:
        css_class = 'log-error'
    elif 'WARNING' in line:
        css_class = 'log-warning'
    elif 'DEBUG' in line:
        css_class = 'log-debug'
    else:
        css_class = ''
    
    return f'<div class="log-entry py-1 {css_class}">{line}</div>'

@app.route('/')
def index():
    logs = get_logs()
    return render_template_string(HTML_TEMPLATE, logs=logs)

@app.route('/logs')
def logs():
    return get_logs()

def get_logs():
    log_file = os.getenv('LOG_FILE', '/app/logs/p115nano302.log')
    try:
        # 如果文件不存在，创建它
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('')
            return '<div class="log-entry log-info">日志文件已创建，等待日志输出...</div>'
            
        # 读取日志文件
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-1000:] if f.readable() else []
            if not lines:  # 如果没有日志
                return '<div class="log-entry log-info">暂无日志记录</div>'
            formatted_lines = [format_log_line(line) for line in lines]
            return ''.join(formatted_lines)
    except Exception as e:
        return f'<div class="log-entry log-error">无法读取日志文件: {str(e)}</div>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001) 