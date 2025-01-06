#!/bin/bash

# 启动p115nano302并将输出重定向到日志文件
p115nano302 "$@" 2>&1 | tee -a /app/logs/p115nano302.log &

# 启动日志查看器
python /app/log_viewer.py 