# 🚀 P115nano302 Docker

这是 [p115nano302](https://pypi.org/project/p115nano302/) 的 Docker 镜像，提供了便捷的部署方式和 Web 日志查看功能。让部署变得简单而优雅！

## ✨ 核心特性

- 🔄 基于最新的 p115nano302 版本，每日自动更新
- 📊 内置美观的 Web 日志查看器
- 💾 支持日志持久化存储
- 🏗️ 多架构支持 (amd64/arm64)
- 🛡️ 安全可靠的部署方案

## 🚀 快速开始

### 1️⃣ 拉取镜像

```bash
docker pull xxllllll/p115nano302:latest
```

### 2️⃣ 准备配置
- 📝 从浏览器获取 115 的 cookies
- 💾 保存到本地文件 (例如: `cookies.txt`)

### 3️⃣ 启动容器

```bash
docker run -d \
  --name p115nano302 \
  -p 8000:8000 \
  -p 8001:8001 \
  -v /path/to/cookies.txt:/app/115-cookies.txt \
  -v /path/to/logs:/app/logs \
  xxllllll/p115nano302 \
  -cp /app/115-cookies.txt
```

## 🔧 配置说明

### 📡 端口配置
- `8000`: p115nano302 主服务端口
- `8001`: Web 日志查看器端口

### 📂 数据卷
- 📄 `/app/115-cookies.txt`: cookies 文件
- 📊 `/app/logs`: 日志目录（可选）

### ⚙️ 环境变量
- `HOST`: 监听地址 (默认: 0.0.0.0)
- `PORT`: 服务端口 (默认: 8000)
- `LOG_FILE`: 日志文件路径 (默认: /app/logs/p115nano302.log)

### 🎮 命令行参数
- `-cp/--cookies-path`: cookies 文件路径
- `-c/--cookies`: cookies 字符串
- `-p/--password`: 后台操作密码
- `-t/--token`: 签名 token
- `-d/--debug`: 调试模式
- `-cu/--cache-url`: 启用 URL 缓存

## 📊 日志查看器

访问 `http://your-ip:8001` 即可查看实时日志，提供以下功能：

- ⚡ 自动每 5 秒刷新
- 📜 显示最近 1000 行日志
- 🔄 支持手动刷新
- 💾 持久化存储

## 🏷️ 版本说明

- `latest`: 最新版本
- `x.y.z`: 特定版本号

## 🔄 自动更新机制

- 🕐 每天凌晨 0 点自动检查 PyPI 更新
- 🏗️ 自动构建最新版本镜像
- 📦 自动发布到 Docker Hub

## 🛡️ 安全建议

- 🏠 建议在内网环境使用
- 🔒 妥善保管 cookies 信息
- 🔑 建议设置访问密码

## 💬 问题反馈

发现问题或有建议？欢迎在 GitHub 仓库提交 Issue！

## 📜 许可证

遵循原项目许可证
