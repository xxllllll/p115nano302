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

# 安装运行时依赖
RUN apk add --no-cache bash

# 创建日志目录
RUN mkdir -p /app/logs

# 创建启动脚本
RUN echo '#!/bin/sh\n\
python /app/log_viewer.py &\n\
p115nano302\n' > /app/start.sh

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

# 启动应用
ENTRYPOINT ["/bin/sh", "/app/start.sh"]
