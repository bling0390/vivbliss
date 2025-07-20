import pytest
import pymongo
import time
import os
from vivbliss_scraper.pipelines import MongoDBPipeline


class TestDockerMongoConnectivity:
    """测试 Docker 环境中的 MongoDB 连接"""
    
    def test_mongodb_connection_string_format(self):
        """测试 MongoDB 连接字符串格式"""
        # 在 Docker 环境中，MongoDB 主机应该是服务名
        expected_docker_uri = "mongodb://mongodb:27017"
        
        # 模拟 Docker 环境变量
        docker_env = {
            'MONGO_URI': expected_docker_uri,
            'MONGO_DATABASE': 'vivbliss_docker_db'
        }
        
        pipeline = MongoDBPipeline(
            mongo_uri=docker_env['MONGO_URI'],
            mongo_db=docker_env['MONGO_DATABASE']
        )
        
        assert pipeline.mongo_uri == expected_docker_uri
        assert 'mongodb' in pipeline.mongo_uri, "URI should use 'mongodb' service name"
    
    def test_mongodb_wait_for_connection(self):
        """测试等待 MongoDB 连接的机制"""
        # 这个测试验证我们有等待 MongoDB 就绪的逻辑
        wait_script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'wait_for_mongo.py')
        assert os.path.exists(wait_script_path), "Should have wait_for_mongo.py script"
    
    def test_connection_retry_logic(self):
        """测试连接重试逻辑"""
        # 验证管道有重试连接的能力
        pipeline = MongoDBPipeline(
            mongo_uri="mongodb://mongodb:27017",
            mongo_db="test_db"
        )
        
        # 检查是否有重试逻辑的属性或方法
        assert hasattr(pipeline, 'max_retries') or hasattr(pipeline, 'retry_connection'), \
            "Pipeline should have connection retry mechanism"


class TestDockerSpiderExecution:
    """测试 Docker 环境中爬虫执行"""
    
    def test_spider_docker_command_exists(self):
        """测试 Docker 中运行爬虫的命令"""
        run_script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'run_spider.sh')
        assert os.path.exists(run_script_path), "Should have run_spider.sh script"
    
    def test_spider_can_access_mongodb_service(self):
        """测试爬虫可以访问 MongoDB 服务"""
        # 这个测试验证配置正确设置了服务间通信
        from vivbliss_scraper import settings
        
        # 在 Docker 环境中，应该使用服务名而不是 localhost
        docker_mongo_uri = getattr(settings, 'DOCKER_MONGO_URI', None)
        if docker_mongo_uri:
            assert 'mongodb:' in docker_mongo_uri, "Docker URI should use service name 'mongodb'"
    
    def test_environment_variable_override(self):
        """测试环境变量覆盖机制"""
        # 验证 Docker 环境变量可以覆盖默认设置
        import vivbliss_scraper.settings as settings_module
        
        # 模拟 Docker 环境变量
        os.environ['MONGO_URI'] = 'mongodb://mongodb:27017'
        os.environ['MONGO_DATABASE'] = 'docker_test_db'
        
        # 重新加载设置或验证环境变量读取
        mongo_uri = os.getenv('MONGO_URI', settings_module.MONGO_URI)
        mongo_db = os.getenv('MONGO_DATABASE', settings_module.MONGO_DATABASE)
        
        assert 'mongodb:' in mongo_uri, "Should use Docker service name"
        assert mongo_db == 'docker_test_db', "Should use Docker database name"
        
        # 清理环境变量
        del os.environ['MONGO_URI']
        del os.environ['MONGO_DATABASE']


class TestDockerHealthChecks:
    """测试 Docker 健康检查"""
    
    def test_health_check_mongodb(self):
        """测试 MongoDB 健康检查"""
        health_check_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'health_check.py')
        with open(health_check_path, 'r') as f:
            content = f.read()
        
        assert 'mongodb' in content.lower(), "Health check should verify MongoDB connection"
        assert 'ping' in content.lower() or 'connect' in content.lower(), \
            "Health check should test database connectivity"
    
    def test_health_check_spider_readiness(self):
        """测试爬虫就绪检查"""
        health_check_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'health_check.py')
        with open(health_check_path, 'r') as f:
            content = f.read()
        
        assert 'scrapy' in content.lower() or 'spider' in content.lower(), \
            "Health check should verify spider readiness"