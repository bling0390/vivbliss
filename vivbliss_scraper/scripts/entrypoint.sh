#!/bin/bash
set -e

echo "Starting Vivbliss Scraper Container..."

# 等待 MongoDB 就绪
echo "Waiting for MongoDB to be ready..."
python scripts/wait_for_mongo.py

# 检查健康状态
echo "Performing health checks..."
python scripts/health_check.py

# 执行传入的命令
echo "Executing command: $@"
exec "$@"