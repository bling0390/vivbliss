#!/bin/bash
"""
在 Docker 环境中运行爬虫的脚本
"""

# 设置默认值
SPIDER_NAME=${1:-vivbliss}
LOG_LEVEL=${SCRAPY_LOG_LEVEL:-INFO}

echo "Running spider: $SPIDER_NAME with log level: $LOG_LEVEL"

# 等待 MongoDB
python scripts/wait_for_mongo.py

# 运行爬虫
python -m scrapy crawl $SPIDER_NAME \
    -L $LOG_LEVEL \
    -s MONGO_URI="${MONGO_URI}" \
    -s MONGO_DATABASE="${MONGO_DATABASE}"