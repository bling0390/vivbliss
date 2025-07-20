FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements 文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY . .

# 安装项目
RUN pip install -e .

# 创建非 root 用户
RUN useradd -m -u 1000 scraper && chown -R scraper:scraper /app
USER scraper

# 创建日志和数据目录
RUN mkdir -p /app/logs /app/data

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python scripts/health_check.py

# 入口点
ENTRYPOINT ["./scripts/entrypoint.sh"]

# 默认命令
CMD ["python", "-m", "scrapy", "crawl", "vivbliss"]