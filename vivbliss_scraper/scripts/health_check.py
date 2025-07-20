#!/usr/bin/env python3
"""
Docker 健康检查脚本
检查 MongoDB 连接和 Scrapy 爬虫就绪状态
"""

import sys
import os
import pymongo
import logging
from time import sleep

# 添加项目路径
sys.path.insert(0, '/app')

from vivbliss_scraper.pipelines import MongoDBPipeline

def check_mongodb_connection():
    """检查 MongoDB 连接"""
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongodb:27017')
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # 尝试 ping 数据库
        client.admin.command('ping')
        client.close()
        
        print("✓ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False

def check_spider_readiness():
    """检查 Scrapy 爬虫就绪状态"""
    try:
        # 尝试导入爬虫模块
        from vivbliss_scraper.spiders.vivbliss import VivblissSpider
        
        # 检查爬虫配置
        spider = VivblissSpider()
        assert spider.name == 'vivbliss'
        assert hasattr(spider, 'parse')
        
        print("✓ Spider readiness check passed")
        return True
    except Exception as e:
        print(f"✗ Spider readiness check failed: {e}")
        return False

def main():
    """主健康检查函数"""
    print("Performing health checks...")
    
    mongodb_ok = check_mongodb_connection()
    spider_ok = check_spider_readiness()
    
    if mongodb_ok and spider_ok:
        print("All health checks passed")
        sys.exit(0)
    else:
        print("Health checks failed")
        sys.exit(1)

if __name__ == "__main__":
    main()