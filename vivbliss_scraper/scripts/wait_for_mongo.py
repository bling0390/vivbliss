#!/usr/bin/env python3
"""
等待 MongoDB 服务就绪的脚本

支持通过环境变量配置 MongoDB 连接：
- MONGO_URI: 完整的 MongoDB URI（优先级最高）
- MONGO_HOST: MongoDB 主机地址
- MONGO_PORT: MongoDB 端口
- MONGO_USERNAME: MongoDB 用户名
- MONGO_PASSWORD: MongoDB 密码
- MONGO_DATABASE: 数据库名称
"""

import sys
import os
import pymongo
import time
import logging
from typing import Optional


def build_mongo_uri() -> str:
    """
    根据环境变量构建 MongoDB URI
    
    优先级：
    1. MONGO_URI - 完整的 MongoDB URI
    2. 单独的配置变量（MONGO_HOST, MONGO_PORT 等）
    3. 默认值
    
    Returns:
        str: MongoDB 连接 URI
    """
    # 如果直接提供了 MONGO_URI，优先使用
    mongo_uri = os.getenv('MONGO_URI')
    if mongo_uri:
        return mongo_uri
    
    # 获取各个配置项
    mongo_host = os.getenv('MONGO_HOST', 'mongodb')  # Docker 环境默认使用 mongodb
    mongo_port = os.getenv('MONGO_PORT', '27017')
    mongo_username = os.getenv('MONGO_USERNAME')
    mongo_password = os.getenv('MONGO_PASSWORD')
    mongo_database = os.getenv('MONGO_DATABASE', 'vivbliss_db')
    
    # 构建 URI
    if mongo_username and mongo_password:
        # 带认证的 URI
        mongo_uri = f'mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_database}?authSource=admin'
    else:
        # 无认证的 URI
        mongo_uri = f'mongodb://{mongo_host}:{mongo_port}'
    
    return mongo_uri


def wait_for_mongodb(max_retries: int = 30, retry_interval: int = 2) -> bool:
    """
    等待 MongoDB 服务就绪
    
    Args:
        max_retries: 最大重试次数。默认 30 次
        retry_interval: 重试间隔（秒）。默认 2 秒
        
    Returns:
        bool: MongoDB 是否就绪
    """
    mongo_uri = build_mongo_uri()
    
    # 隐藏密码信息用于日志输出
    display_uri = mongo_uri
    if '@' in mongo_uri:
        # 隐藏用户名和密码
        parts = mongo_uri.split('@')
        auth_part = parts[0].split('//')[-1]
        if ':' in auth_part:
            username = auth_part.split(':')[0]
            display_uri = mongo_uri.replace(auth_part, f'{username}:****')
    
    print(f"Waiting for MongoDB at {display_uri}...")
    
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
            
            print(f"✓ MongoDB is ready after {attempt + 1} attempt{'s' if attempt > 0 else ''}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            # 简化错误信息
            if 'Authentication failed' in error_msg:
                error_msg = 'Authentication failed'
            elif 'Connection refused' in error_msg:
                error_msg = 'Connection refused'
            elif 'timed out' in error_msg.lower():
                error_msg = 'Connection timeout'
                
            print(f"Attempt {attempt + 1}/{max_retries} failed: {error_msg}")
            
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                print("✗ MongoDB connection timeout")
                print("\n检查以下事项：")
                print("1. MongoDB 服务是否正在运行")
                print("2. 主机地址和端口是否正确")
                if os.getenv('MONGO_USERNAME'):
                    print("3. 用户名和密码是否正确")
                    print("4. 用户是否有权限访问指定数据库")
                return False
    
    return False

def main() -> None:
    """主函数"""
    # 支持通过命令行参数设置重试次数和间隔
    max_retries = 30
    retry_interval = 2
    
    if len(sys.argv) > 1:
        try:
            max_retries = int(sys.argv[1])
        except ValueError:
            print(f"错误: 无效的重试次数 '{sys.argv[1]}'")
            sys.exit(2)
    
    if len(sys.argv) > 2:
        try:
            retry_interval = int(sys.argv[2])
        except ValueError:
            print(f"错误: 无效的重试间隔 '{sys.argv[2]}'")
            sys.exit(2)
    
    # 显示配置信息
    print(f"MongoDB 连接配置:")
    print(f"  主机: {os.getenv('MONGO_HOST', 'mongodb')}")
    print(f"  端口: {os.getenv('MONGO_PORT', '27017')}")
    print(f"  数据库: {os.getenv('MONGO_DATABASE', 'vivbliss_db')}")
    if os.getenv('MONGO_USERNAME'):
        print(f"  用户: {os.getenv('MONGO_USERNAME')}")
    print(f"  最大重试: {max_retries} 次")
    print(f"  重试间隔: {retry_interval} 秒\n")
    
    if wait_for_mongodb(max_retries, retry_interval):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()