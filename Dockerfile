FROM python:3.12-slim

# 添加构建参数
ARG BUILDTIME=unknown

WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装依赖
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade pip && \
    pip cache purge && \
    pip install --no-cache-dir p115nano302>=0.0.9 && \
    python -c "import p115nano302; print('p115nano302 installed successfully')"

# 创建必要的目录
RUN mkdir -p /app/p115nano302/static/css \
    /app/p115nano302/static/js \
    /app/p115nano302/templates

# 创建cookies文件
RUN touch /app/115-cookies.txt && \
    chmod 666 /app/115-cookies.txt

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    TZ=Asia/Shanghai \
    COOKIES="" \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1

# 设置权限
RUN chmod -R 755 /app

# 暴露端口
EXPOSE 8000 8001

# 启动应用
CMD ["python", "-u", "p115nano302/main.py"]