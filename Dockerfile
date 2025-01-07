# 使用更小的基础镜像
FROM python:3.12-slim-bullseye as builder

# 设置工作目录
WORKDIR /app

# 只安装必要的编译工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装依赖
RUN pip install --no-cache-dir p115nano302 flask

# 使用多阶段构建
FROM python:3.12-slim-bullseye

WORKDIR /app

# 从builder阶段复制Python包
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# 创建日志目录
RUN mkdir -p /app/logs

# 复制应用文件
COPY log_viewer.py start.sh /app/
RUN chmod +x /app/start.sh

# 设置环境变量
ENV HOST=0.0.0.0 \
    PORT=8000 \
    LOG_FILE=/app/logs/p115nano302.log \
    PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000 8001

# 启动应用
ENTRYPOINT ["/app/start.sh"]
