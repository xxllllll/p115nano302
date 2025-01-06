// 日志更新函数
function updateLogs() {
    fetch('/api/logs')
        .then(response => response.json())
        .then(logs => {
            const logContent = document.getElementById('logContent');
            if (logs && logs.length > 0) {
                const wasAtBottom = isScrolledToBottom(logContent);
                
                const newHtml = logs.map(log => `
                    <div class="log-entry log-${log.level || 'info'}" data-timestamp="${log.timestamp}">
                        <span class="timestamp">${formatTimestamp(log.timestamp)}</span>
                        <span class="message ${log.level || 'info'}">${escapeHtml(log.message)}</span>
                    </div>
                `).join('');

                if (logContent.innerHTML !== newHtml) {
                    logContent.innerHTML = newHtml;
                    if (wasAtBottom) {
                        scrollToBottom(logContent);
                    }
                }
            } else {
                logContent.innerHTML = '<div class="log-entry">等待日志...</div>';
            }
        })
        .catch(error => {
            console.error('Error fetching logs:', error);
            const logContent = document.getElementById('logContent');
            logContent.innerHTML = `
                <div class="log-entry log-error">
                    <span class="timestamp">${new Date().toLocaleTimeString()}</span>
                    <span class="message error">获取日志失败: ${error.message}</span>
                </div>
            `;
        });
}

// 辅助函数
function isScrolledToBottom(element) {
    const threshold = 50;
    return (element.scrollHeight - element.scrollTop - element.clientHeight) <= threshold;
}

function scrollToBottom(element) {
    element.scrollTop = element.scrollHeight;
}

function formatTimestamp(timestamp) {
    return timestamp;
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    updateLogs();
    const logContent = document.getElementById('logContent');
    scrollToBottom(logContent);
});

// 定时更新
setInterval(updateLogs, 1000);

// 页面可见性变化时更新
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        updateLogs();
    }
}); 