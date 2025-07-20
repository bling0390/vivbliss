#!/usr/bin/env python3
"""
等待 MongoDB 服务就绪的脚本
"""

import sys
import os
import pymongo
import time
import logging

def wait_for_mongodb(max_retries=30, retry_interval=2):
    """
    等待 MongoDB 服务就绪
    
    Args:
        max_retries: 最大重试次数
        retry_interval: 重试间隔（秒）
    """
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongodb:27017')
    
    print(f"Waiting for MongoDB at {mongo_uri}...")
    
    for attempt in range(max_retries):
        try:
            client = pymongo.MongoClient(
                mongo_uri, 
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # 尝试 ping 数据库
            client.admin.command('ping')
            client.close()
            
            print(f"✓ MongoDB is ready after {attempt + 1} attempts")
            return True
            
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                print("✗ MongoDB connection timeout")
                return False
    
    return False

def main():
    """主函数"""
    if wait_for_mongodb():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()