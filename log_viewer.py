from flask import Flask, render_template_string
import os
import re
import html

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>p115nano302 日志查看器</title>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .log-entry {
            transition: background-color 0.2s;
        }
        .log-entry:hover {
            background-color: #f3f4f6;
        }
        .log-info { color: #3b82f6; }
        .log-error { color: #ef4444; }
        .log-warning { color: #f59e0b; }
        .log-debug { color: #6b7280; }
        .animate-fade {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-3xl font-bold text-gray-800">p115nano302 日志查看器</h1>
            <div class="space-x-4">
                <button onclick="refreshLogs()" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition duration-200">
                    刷新日志
                </button>
                <button onclick="clearLogs()" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition duration-200">
                    清空显示
                </button>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-lg p-6">
            <div id="log-container" class="font-mono text-sm whitespace-pre-wrap h-[600px] overflow-y-auto">
                {{ logs | safe }}
            </div>
        </div>
        
        <div class="mt-4 text-gray-600 text-sm">
            <p>自动刷新间隔：5秒</p>
            <p>显示最近1000行日志</p>
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
    
    # 转义HTML特殊字符
    line = html.escape(line)
    
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
    
    # 格式化时间戳
    timestamp_pattern = r'\[(.*?)\]'
    line = re.sub(timestamp_pattern, r'<span class="text-gray-500">[\1]</span>', line)
    
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
        with open(log_file, 'r') as f:
            # 读取最后1000行日志
            lines = f.readlines()[-1000:]
            formatted_lines = [format_log_line(line) for line in lines]
            return ''.join(formatted_lines)
    except Exception as e:
        return f'<div class="log-entry log-error">无法读取日志文件: {str(e)}</div>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001) 