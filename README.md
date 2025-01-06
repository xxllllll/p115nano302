# P115nano302 Docker

这是 [p115nano302](https://pypi.org/project/p115nano302/) 的Docker镜像，提供了便捷的部署方式和Web日志查看功能。

## 特性

- 基于最新的p115nano302版本
- 内置Web日志查看器
- 自动每日更新
- 支持日志持久化
- 多架构支持 (amd64/arm64)

## 快速开始

1. 拉取镜像:

    ```bash
    docker pull xxllllll/p115nano302:latest
    ```

2. 准备cookies文件:
   - 从浏览器获取115的cookies
   - 保存到本地文件 (例如: `cookies.txt`)

3. 运行容器:

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

## 端口说明

- `8000`: p115nano302主服务端口
- `8001`: Web日志查看器端口

## 卷挂载

- `/app/115-cookies.txt`: cookies文件
- `/app/logs`: 日志目录（可选）

## 环境变量

- `HOST`: 监听地址 (默认: 0.0.0.0)
- `PORT`: 服务端口 (默认: 8000)
- `LOG_FILE`: 日志文件路径 (默认: /app/logs/p115nano302.log)

## 命令行参数

支持所有p115nano302的命令行参数:

- `-cp/--cookies-path`: cookies文件路径
- `-c/--cookies`: cookies字符串
- `-p/--password`: 后台操作密码
- `-t/--token`: 签名token
- `-d/--debug`: 调试模式
- `-cu/--cache-url`: 启用URL缓存

## 日志查看

访问 `http://your-ip:8001` 查看实时日志。日志查看器功能：

- 自动每5秒刷新
- 显示最近1000行日志
- 支持手动刷新
- 持久化存储

## 版本标签

- `latest`: 最新版本
- `x.y.z`: 特定版本号

## 自动更新

镜像每天凌晨0点自动检查PyPI更新并构建最新版本。

## 安全提示

- 建议在内网环境使用
- 妥善保管cookies信息
- 建议设置访问密码

## 问题反馈

如有问题，请在GitHub仓库提交Issue。

## 许可证

遵循原项目许可证
