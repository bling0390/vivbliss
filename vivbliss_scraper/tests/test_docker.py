import pytest
import yaml
import os
import subprocess
from pathlib import Path


class TestDockerConfiguration:
    """测试 Docker 配置文件的存在性和有效性"""
    
    def test_dockerfile_exists(self):
        """测试 Dockerfile 文件是否存在"""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        assert dockerfile_path.exists(), "Dockerfile should exist in project root"
    
    def test_docker_compose_exists(self):
        """测试 docker-compose.yml 文件是否存在"""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        assert compose_path.exists(), "docker-compose.yml should exist in project root"
    
    def test_docker_compose_valid_yaml(self):
        """测试 docker-compose.yml 是否为有效的 YAML"""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_path, 'r') as f:
            compose_data = yaml.safe_load(f)
        assert compose_data is not None, "docker-compose.yml should be valid YAML"
    
    def test_docker_compose_has_required_services(self):
        """测试 docker-compose.yml 包含必需的服务"""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_path, 'r') as f:
            compose_data = yaml.safe_load(f)
        
        assert 'services' in compose_data, "docker-compose.yml should have services section"
        services = compose_data['services']
        
        required_services = ['mongodb', 'vivbliss-scraper']
        for service in required_services:
            assert service in services, f"Service {service} should be defined in docker-compose.yml"
    
    def test_mongodb_service_configuration(self):
        """测试 MongoDB 服务配置"""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_path, 'r') as f:
            compose_data = yaml.safe_load(f)
        
        mongodb_service = compose_data['services']['mongodb']
        assert 'image' in mongodb_service, "MongoDB service should specify an image"
        assert 'ports' in mongodb_service, "MongoDB service should expose ports"
        assert 'volumes' in mongodb_service, "MongoDB service should have volume mounts"
    
    def test_scraper_service_configuration(self):
        """测试爬虫服务配置"""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_path, 'r') as f:
            compose_data = yaml.safe_load(f)
        
        scraper_service = compose_data['services']['vivbliss-scraper']
        assert 'build' in scraper_service, "Scraper service should specify build context"
        assert 'depends_on' in scraper_service, "Scraper service should depend on MongoDB"
        assert 'mongodb' in scraper_service['depends_on'], "Scraper should depend on mongodb service"


class TestDockerfile:
    """测试 Dockerfile 内容和结构"""
    
    def test_dockerfile_has_python_base(self):
        """测试 Dockerfile 使用 Python 基础镜像"""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        assert 'FROM python:' in content, "Dockerfile should use Python base image"
    
    def test_dockerfile_installs_dependencies(self):
        """测试 Dockerfile 安装依赖"""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        assert 'requirements.txt' in content, "Dockerfile should install from requirements.txt"
        assert 'pip install' in content, "Dockerfile should use pip to install dependencies"
    
    def test_dockerfile_copies_source_code(self):
        """测试 Dockerfile 复制源代码"""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        assert 'COPY' in content, "Dockerfile should copy source code"
    
    def test_dockerfile_sets_workdir(self):
        """测试 Dockerfile 设置工作目录"""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        assert 'WORKDIR' in content, "Dockerfile should set working directory"


class TestDockerEnvironment:
    """测试 Docker 环境配置"""
    
    def test_docker_env_file_exists(self):
        """测试 Docker 环境文件是否存在"""
        env_file_path = Path(__file__).parent.parent / ".env.docker"
        assert env_file_path.exists(), ".env.docker file should exist for Docker environment"
    
    def test_docker_env_has_mongodb_config(self):
        """测试 Docker 环境文件包含 MongoDB 配置"""
        env_file_path = Path(__file__).parent.parent / ".env.docker"
        with open(env_file_path, 'r') as f:
            content = f.read()
        
        assert 'MONGO_URI' in content, ".env.docker should contain MONGO_URI"
        assert 'mongodb' in content.lower(), ".env.docker should reference mongodb service"


class TestDockerIntegration:
    """测试 Docker 集成功能"""
    
    def test_docker_compose_syntax_valid(self):
        """测试 Docker Compose 语法有效性"""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_path, 'r') as f:
            compose_data = yaml.safe_load(f)
        
        # 基本语法检查
        assert 'version' in compose_data or 'services' in compose_data, \
            "docker-compose.yml should have version or services"
    
    def test_health_check_script_exists(self):
        """测试健康检查脚本是否存在"""
        health_script_path = Path(__file__).parent.parent / "scripts" / "health_check.py"
        assert health_script_path.exists(), "Health check script should exist"
    
    def test_entrypoint_script_exists(self):
        """测试入口脚本是否存在"""
        entrypoint_path = Path(__file__).parent.parent / "scripts" / "entrypoint.sh"
        assert entrypoint_path.exists(), "Entrypoint script should exist"