# 115网盘 Nano 302跳转服务

一个轻量级的115网盘302跳转服务，基于 p115nano302 包开发，提供美观的Web界面和实时日志显示。

![Python Version](https://img.shields.io/badge/Python-3.12+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 特性

- 🚀 基于 FastAPI 和 p115nano302 的高性能302跳转
- 💻 现代化的Web管理界面
- 📊 实时彩色日志显示
- 🐳 完整的Docker支持
- 🔄 自动保存最近100条日志
- 🎨 美观的TailwindCSS界面设计

## 快速开始

### Docker方式

```bash
# 拉取镜像
docker pull your-registry/p115nano302:latest

# 运行容器
docker run -d \
  -p 8000:8000 \
  -p 8001:8001 \
  -v /path/to/115-cookies.txt:/app/115-cookies.txt \
  --name p115nano302 \
  your-registry/p115nano302
```

### 手动安装

1. 克隆仓库
```bash
git clone https://github.com/your-username/p115nano302.git
cd p115nano302
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行服务
```bash
python main.py
```

## 配置说明

1. 准备cookies文件
- 创建 `115-cookies.txt` 文件
- 将115网盘的cookies内容粘贴到文件中

2. 环境变量
- `COOKIES`: 可选，直接设置cookies字符串
- `TZ`: 时区设置，默认 Asia/Shanghai

## 服务访问

- 302跳转服务: http://localhost:8000
- Web管理界面: http://localhost:8001

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