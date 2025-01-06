from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>p115nano302 日志查看器</title>
    <style>
        body { font-family: monospace; padding: 20px; }
        #log-container { 
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            white-space: pre-wrap;
        }
        .refresh-btn {
            margin-bottom: 10px;
            padding: 5px 10px;
        }
    </style>
    <script>
        function refreshLogs() {
            fetch('/logs')
                .then(response => response.text())
                .then(data => {
                    document.getElementById('log-container').textContent = data;
                });
        }
        
        // 每5秒自动刷新一次
        setInterval(refreshLogs, 5000);
    </script>
</head>
<body>
    <h1>p115nano302 日志查看器</h1>
    <button class="refresh-btn" onclick="refreshLogs()">刷新日志</button>
    <div id="log-container">{{ logs }}</div>
</body>
</html>
"""

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
            return ''.join(lines)
    except Exception as e:
        return f"无法读取日志文件: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001) 