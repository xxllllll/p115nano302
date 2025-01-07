FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装编译工具和依赖
RUN apt-get update && apt-get install -y \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装p115nano302和所需依赖，使用预编译的二进制包
RUN pip install --only-binary :all: -U p115nano302 flask

# 创建日志目录
RUN mkdir -p /app/logs

# 复制日志查看器脚本
COPY log_viewer.py /app/

# 设置环境变量
ENV HOST=0.0.0.0
ENV PORT=8000
ENV LOG_FILE=/app/logs/p115nano302.log

# 暴露端口
EXPOSE 8000
EXPOSE 8001

# 使用启动脚本
COPY start.sh /app/
RUN chmod +x /app/start.sh
ENTRYPOINT ["/app/start.sh"]