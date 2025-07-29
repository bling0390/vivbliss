#!/usr/bin/env python3
"""
wait_for_mongo.py 的测试用例
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import time

# 添加脚本目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestWaitForMongo(unittest.TestCase):
    """测试 wait_for_mongo 模块"""
    
    def setUp(self):
        """测试前设置"""
        # 清除相关环境变量
        env_vars = ['MONGO_URI', 'MONGO_HOST', 'MONGO_PORT', 
                   'MONGO_USERNAME', 'MONGO_PASSWORD', 'MONGO_DATABASE']
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
    
    def test_build_mongo_uri_without_auth(self):
        """测试无认证情况下构建 MongoDB URI"""
        # 设置环境变量
        os.environ['MONGO_HOST'] = 'testhost'
        os.environ['MONGO_PORT'] = '27017'
        os.environ['MONGO_DATABASE'] = 'testdb'
        
        # 导入模块以触发 URI 构建
        import scripts.wait_for_mongo
        build_mongo_uri = scripts.wait_for_mongo.build_mongo_uri
        
        uri = build_mongo_uri()
        self.assertEqual(uri, 'mongodb://testhost:27017')
    
    def test_build_mongo_uri_with_auth(self):
        """测试带认证情况下构建 MongoDB URI"""
        # 设置环境变量
        os.environ['MONGO_HOST'] = 'testhost'
        os.environ['MONGO_PORT'] = '27017'
        os.environ['MONGO_USERNAME'] = 'testuser'
        os.environ['MONGO_PASSWORD'] = 'testpass'
        os.environ['MONGO_DATABASE'] = 'testdb'
        
        import scripts.wait_for_mongo
        build_mongo_uri = scripts.wait_for_mongo.build_mongo_uri
        
        uri = build_mongo_uri()
        self.assertEqual(uri, 'mongodb://testuser:testpass@testhost:27017/testdb?authSource=admin')
    
    def test_build_mongo_uri_with_uri_override(self):
        """测试 MONGO_URI 覆盖其他配置"""
        # 设置环境变量
        os.environ['MONGO_HOST'] = 'testhost'
        os.environ['MONGO_PORT'] = '27017'
        os.environ['MONGO_URI'] = 'mongodb://custom:27017'
        
        import scripts.wait_for_mongo
        build_mongo_uri = scripts.wait_for_mongo.build_mongo_uri
        
        uri = build_mongo_uri()
        self.assertEqual(uri, 'mongodb://custom:27017')
    
    def test_build_mongo_uri_defaults(self):
        """测试使用默认值构建 MongoDB URI"""
        import scripts.wait_for_mongo
        build_mongo_uri = scripts.wait_for_mongo.build_mongo_uri
        
        uri = build_mongo_uri()
        # 默认应该是 mongodb:27017 (Docker 环境)
        self.assertIn('mongodb://', uri)
        self.assertIn(':27017', uri)
    
    @patch('pymongo.MongoClient')
    def test_wait_for_mongodb_uses_correct_uri(self, mock_client):
        """测试 wait_for_mongodb 使用正确的 URI"""
        # 设置环境变量
        os.environ['MONGO_HOST'] = 'testhost'
        os.environ['MONGO_PORT'] = '27018'
        os.environ['MONGO_USERNAME'] = 'admin'
        os.environ['MONGO_PASSWORD'] = 'secret'
        
        # 模拟成功连接
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        import scripts.wait_for_mongo
        wait_for_mongodb = scripts.wait_for_mongo.wait_for_mongodb
        result = wait_for_mongodb(max_retries=1)
        
        # 验证调用参数
        mock_client.assert_called()
        call_args = mock_client.call_args[0][0]
        
        # 应该包含认证信息
        self.assertIn('admin:secret', call_args)
        self.assertIn('testhost:27018', call_args)
        self.assertTrue(result)
    
    @patch('pymongo.MongoClient')
    def test_wait_for_mongodb_retry_logic(self, mock_client):
        """测试重试逻辑"""
        # 模拟前两次失败，第三次成功
        mock_client.side_effect = [
            Exception("Connection failed"),
            Exception("Connection failed"),
            MagicMock()  # 第三次成功
        ]
        
        import scripts.wait_for_mongo
        wait_for_mongodb = scripts.wait_for_mongo.wait_for_mongodb
        
        # 使用较短的重试间隔进行测试
        with patch('time.sleep') as mock_sleep:
            result = wait_for_mongodb(max_retries=3, retry_interval=0.1)
        
        self.assertTrue(result)
        self.assertEqual(mock_client.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)  # 前两次失败后会 sleep
    
    @patch('pymongo.MongoClient')
    def test_wait_for_mongodb_timeout(self, mock_client):
        """测试超时情况"""
        # 模拟持续失败
        mock_client.side_effect = Exception("Connection failed")
        
        import scripts.wait_for_mongo
        wait_for_mongodb = scripts.wait_for_mongo.wait_for_mongodb
        
        with patch('time.sleep'):  # 跳过实际的 sleep
            result = wait_for_mongodb(max_retries=2, retry_interval=0.1)
        
        self.assertFalse(result)
        self.assertEqual(mock_client.call_count, 2)


if __name__ == '__main__':
    unittest.main()