#!/usr/bin/env python3
"""
测试 MongoDB 认证连接
"""
import os
import sys
import pymongo
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_mongo_connection():
    """测试 MongoDB 连接（支持认证）"""
    # 获取环境变量
    mongo_host = os.getenv('MONGO_HOST', 'localhost')
    mongo_port = int(os.getenv('MONGO_PORT', '27017'))
    mongo_username = os.getenv('MONGO_USERNAME')
    mongo_password = os.getenv('MONGO_PASSWORD')
    mongo_database = os.getenv('MONGO_DATABASE', 'vivbliss_db')
    
    # 构建 MongoDB URI
    if mongo_username and mongo_password:
        mongo_uri = f'mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_database}?authSource=admin'
        print(f"使用认证连接: {mongo_host}:{mongo_port} (用户: {mongo_username})")
    else:
        mongo_uri = f'mongodb://{mongo_host}:{mongo_port}'
        print(f"使用无认证连接: {mongo_host}:{mongo_port}")
    
    # 允许环境变量覆盖
    mongo_uri = os.getenv('MONGO_URI', mongo_uri)
    
    try:
        # 创建客户端
        client = pymongo.MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB 连接成功!")
        
        # 获取数据库
        db = client[mongo_database]
        print(f"✅ 成功连接到数据库: {mongo_database}")
        
        # 列出集合
        collections = db.list_collection_names()
        if collections:
            print(f"📋 现有集合: {', '.join(collections)}")
        else:
            print("📋 数据库中暂无集合")
        
        # 测试写入
        test_collection = db['test_auth']
        test_doc = {'test': 'auth_check', 'timestamp': pymongo.datetime.datetime.now()}
        result = test_collection.insert_one(test_doc)
        print(f"✅ 测试文档写入成功，ID: {result.inserted_id}")
        
        # 测试读取
        found_doc = test_collection.find_one({'_id': result.inserted_id})
        print(f"✅ 测试文档读取成功: {found_doc}")
        
        # 清理测试数据
        test_collection.delete_one({'_id': result.inserted_id})
        print("✅ 测试数据已清理")
        
        # 关闭连接
        client.close()
        print("\n🎉 所有测试通过！MongoDB 认证配置正确。")
        return True
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print("❌ 无法连接到 MongoDB 服务器")
        print("   请检查:")
        print("   - MongoDB 是否正在运行")
        print("   - 主机和端口配置是否正确")
        return False
        
    except pymongo.errors.OperationFailure as e:
        print(f"❌ MongoDB 操作失败: {e}")
        print("   请检查:")
        print("   - 用户名和密码是否正确")
        print("   - 用户是否有相应的权限")
        print("   - authSource 参数是否正确")
        return False
        
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

if __name__ == "__main__":
    print("=== MongoDB 认证连接测试 ===\n")
    
    # 显示当前配置
    print("当前环境变量配置:")
    print(f"MONGO_HOST: {os.getenv('MONGO_HOST', 'localhost')}")
    print(f"MONGO_PORT: {os.getenv('MONGO_PORT', '27017')}")
    print(f"MONGO_USERNAME: {os.getenv('MONGO_USERNAME', '(未设置)')}")
    print(f"MONGO_PASSWORD: {'***' if os.getenv('MONGO_PASSWORD') else '(未设置)'}")
    print(f"MONGO_DATABASE: {os.getenv('MONGO_DATABASE', 'vivbliss_db')}")
    print(f"MONGO_URI: {os.getenv('MONGO_URI', '(未设置)')}")
    print()
    
    # 运行测试
    success = test_mongo_connection()
    sys.exit(0 if success else 1)