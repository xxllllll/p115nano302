FROM python:3.12-slim-bullseye as builder

# 设置工作目录
WORKDIR /app

# 安装编译工具和依赖，完成后立即清理
RUN apt-get update && apt-get install -y \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --only-binary :all: -U p115nano302 flask

# 使用更小的基础镜像作为最终镜像
FROM python:3.12-slim-bullseye

WORKDIR /app

# 从builder阶段复制Python包
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# 创建日志目录并复制必要文件
RUN mkdir -p /app/logs
COPY log_viewer.py start.sh ./
RUN chmod +x /app/start.sh

# 设置环境变量
ENV HOST=0.0.0.0 \
    PORT=8000 \
    LOG_FILE=/app/logs/p115nano302.log

# 暴露端口
EXPOSE 8000 8001

ENTRYPOINT ["/app/start.sh"]