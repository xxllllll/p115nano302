# 115网盘 Nano 302跳转服务

一个基于p115nano302的轻量级115网盘302跳转服务，提供美观的Web界面和实时日志显示。

![Docker Build Status](https://github.com/xxllllll/p115nano302/actions/workflows/docker-build.yml/badge.svg)
![Docker Pulls](https://img.shields.io/docker/pulls/xxllllll/p115nano302)
![Docker Image Version](https://img.shields.io/docker/v/xxllllll/p115nano302/latest)

## 特性

- 🚀 基于 FastAPI 和 p115nano302 的高性能302跳转
- 💻 现代化的Web管理界面
- 📊 实时彩色日志显示
- 🐳 完整的Docker支持
- 🔄 自动保存最近100条日志
- 🎨 美观的TailwindCSS界面设计
- 🔒 不依赖于 p115client 和 pycryptodome
- ⚡ 支持URL缓存功能

## 快速开始

### Docker方式

```bash
# 拉取镜像
docker pull xxllllll/p115nano302:latest

# 运行容器
docker run -d \
  -p 8000:8000 \
  -p 8001:8001 \
  -v /path/to/115-cookies.txt:/app/115-cookies.txt \
  --name p115nano302 \
  xxllllll/p115nano302
```

### 手动安装

1. 克隆仓库
```bash
git clone https://github.com/xxllllll/p115nano302.git
cd p115nano302
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行服务
```bash
python -m p115nano302.main
```

## 配置说明

1. 准备cookies文件
- 创建 `115-cookies.txt` 文件
- 将115网盘的cookies内容粘贴到文件中（必须包含UID和CID）

2. 环境变量
- `COOKIES`: 可选，直接设置cookies字符串
- `TZ`: 时区设置，默认 Asia/Shanghai

## 服务访问

- 302跳转服务: http://localhost:8000
- Web管理界面: http://localhost:8001

## 自动构建

本项目通过 GitHub Actions 实现自动化构建和发布：

- 每天北京时间凌晨 0 点自动检查 PyPI 更新
- 发现新版本时自动构建并推送到 Docker Hub
- 使用 p115nano302 的版本号作为 Docker 标签
- 支持手动触发构建
- 使用 Docker 层缓存加速构建
- 避免重复构建相同版本

## 开发说明

- Python 3.12+ 
- 使用 Rich 提供彩色日志输出
- FastAPI 提供Web服务
- TailwindCSS 构建界面

## 注意事项

1. 确保cookies内容正确且有效
2. 建议使用反向代理进行部署
3. 定期检查日志确保服务正常运行

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License 