# 构建阶段
FROM python:3.12-alpine as builder

# 设置工作目录
WORKDIR /app

# 安装必要的编译工具和依赖
RUN apk add --no-cache \
    python3-dev \
    gcc \
    g++ \
    musl-dev \
    linux-headers \
    make

# 安装依赖
RUN pip install --no-cache-dir wheel setuptools
RUN pip install --no-cache-dir uvicorn flask

# 安装 p115nano302（使用预编译的wheel包）
RUN pip install --no-cache-dir --index-url https://pypi.org/simple p115nano302

# 最终阶段
FROM python:3.12-alpine

WORKDIR /app

# 从builder阶段复制Python包
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# 创建日志目录和文件
RUN mkdir -p /app/logs && \
    touch /app/logs/p115nano302.log && \
    chmod 777 /app/logs && \
    chmod 666 /app/logs/p115nano302.log

# 创建启动脚本
RUN echo '#!/bin/sh\n\
set -e\n\
\n\
# 初始化日志\n\
echo "[$(date "+%Y-%m-%d %H:%M:%S")] 容器启动" > /app/logs/p115nano302.log\n\
\n\
# 确保目录和权限正确\n\
mkdir -p /app/logs\n\
chmod 777 /app/logs\n\
touch /app/logs/p115nano302.log\n\
chmod 666 /app/logs/p115nano302.log\n\
\n\
# 启动日志查看器\n\
echo "[$(date "+%Y-%m-%d %H:%M:%S")] 启动日志查看器" >> /app/logs/p115nano302.log\n\
python /app/log_viewer.py &\n\
\n\
# 记录启动参数\n\
echo "[$(date "+%Y-%m-%d %H:%M:%S")] 启动参数: $@" >> /app/logs/p115nano302.log\n\
\n\
# 启动主程序\n\
echo "[$(date "+%Y-%m-%d %H:%M:%S")] 启动主程序 p115nano302" >> /app/logs/p115nano302.log\n\
exec p115nano302 "$@" 2>&1 | tee -a /app/logs/p115nano302.log\n' > /app/start.sh

# 复制应用文件
COPY log_viewer.py /app/
RUN chmod +x /app/start.sh

# 设置环境变量
ENV HOST=0.0.0.0 \
    PORT=8000 \
    LOG_FILE=/app/logs/p115nano302.log \
    PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000 8001

# 使用 ENTRYPOINT 来设置基础命令
ENTRYPOINT ["/bin/sh", "/app/start.sh"]

# 设置默认参数
CMD []
