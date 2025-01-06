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
    # 确保先卸载旧版本
    pip uninstall -y p115nano302 && \
    # 安装最新版本
    pip install --no-cache-dir p115nano302>=0.0.9 && \
    # 验证安装
    python -c "import p115nano302; print(f'p115nano302 version: {p115nano302.__version__}')"

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
    # 添加Python路径
    PYTHONPATH=/app

# 设置权限
RUN chmod -R 755 /app

# 暴露端口
EXPOSE 8000 8001

# 启动应用
CMD ["python", "-m", "p115nano302.main"]
