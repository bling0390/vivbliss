# Docker 使用指南

本指南详细说明如何使用 Docker 运行 Vivbliss 爬虫。

## 🚀 快速开始

### 1. 环境准备

确保系统已安装：
- Docker Engine 20.10+
- Docker Compose 2.0+

### 2. 项目设置

```bash
# 克隆项目
git clone <repository-url>
cd vivbliss_scraper

# 复制环境配置文件
cp .env.docker .env.docker.local

# 编辑配置（可选）
nano .env.docker.local
```

### 3. 启动服务

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 或者前台运行查看日志
docker-compose up
```

## 📋 服务架构

### MongoDB 服务
- **镜像**: mongo:7.0
- **端口**: 27017
- **数据卷**: 持久化数据存储
- **健康检查**: 30秒间隔 ping 检查

### Vivbliss Scraper 服务
- **构建**: 基于项目 Dockerfile
- **依赖**: MongoDB 服务健康后启动
- **重试逻辑**: 内置 MongoDB 连接重试
- **日志**: 输出到 ./logs 目录

## 🔧 常用命令

### 服务管理

```bash
# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f vivbliss-scraper
docker-compose logs -f mongodb

# 重启特定服务
docker-compose restart vivbliss-scraper

# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 爬虫操作

```bash
# 运行一次性爬取
docker-compose run --rm vivbliss-scraper

# 使用自定义参数运行
docker-compose run --rm vivbliss-scraper python -m scrapy crawl vivbliss -L DEBUG

# 进入容器调试
docker-compose exec vivbliss-scraper bash
```

### 数据库操作

```bash
# 连接到 MongoDB
docker-compose exec mongodb mongosh

# 查看数据库
docker-compose exec mongodb mongosh --eval "show dbs"

# 查看集合中的数据
docker-compose exec mongodb mongosh vivbliss_docker_db --eval "db.vivbliss_items.find().limit(5)"
```

## ⚙️ 配置选项

### 环境变量

在 `.env.docker` 文件中可配置：

```env
# MongoDB 配置
MONGO_URI=mongodb://mongodb:27017
MONGO_DATABASE=vivbliss_docker_db
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=password

# Scrapy 配置
SCRAPY_LOG_LEVEL=INFO
DOWNLOAD_DELAY=1
CONCURRENT_REQUESTS=2

# 自定义 User-Agent
USER_AGENT=VivblissBot 1.0 Docker
```

### 数据卷映射

默认配置的数据卷：
- `./logs:/app/logs` - 爬虫日志
- `./data:/app/data` - 输出数据
- `mongodb_data:/data/db` - MongoDB 数据
- `mongodb_config:/data/configdb` - MongoDB 配置

## 🔍 监控与调试

### 健康检查

```bash
# 检查容器健康状态
docker-compose ps

# 手动运行健康检查
docker-compose exec vivbliss-scraper python scripts/health_check.py
```

### 日志分析

```bash
# 实时查看爬虫日志
docker-compose logs -f vivbliss-scraper

# 查看最近100行日志
docker-compose logs --tail=100 vivbliss-scraper

# 保存日志到文件
docker-compose logs vivbliss-scraper > scraper.log
```

### 性能监控

```bash
# 查看容器资源使用情况
docker stats

# 查看特定容器资源
docker stats vivbliss_scraper vivbliss_mongodb
```

## 🛠️ 开发与测试

### 开发模式

```bash
# 挂载源代码进行开发
docker-compose -f docker-compose.dev.yml up
```

### 测试

```bash
# 在容器中运行测试
docker-compose run --rm vivbliss-scraper pytest tests/ -v

# 运行 Docker 特定测试
docker-compose run --rm vivbliss-scraper pytest tests/test_docker*.py -v
```

## 🔐 安全注意事项

1. **环境变量**: 不要在 `.env.docker` 中放置敏感信息，使用 `.env.docker.local`
2. **网络隔离**: 默认配置使用 Docker 网络隔离
3. **用户权限**: 容器内使用非 root 用户运行
4. **数据卷权限**: 确保宿主机目录权限正确

## 📈 扩展和自定义

### 添加新的爬虫

1. 在 `vivbliss_scraper/spiders/` 目录添加新爬虫
2. 更新 `docker-compose.yml` 中的命令
3. 重新构建镜像：`docker-compose up --build`

### 自定义 MongoDB 配置

编辑 `docker-compose.yml` 中的 MongoDB 服务配置：

```yaml
mongodb:
  image: mongo:7.0
  environment:
    MONGO_INITDB_ROOT_USERNAME: your_username
    MONGO_INITDB_ROOT_PASSWORD: your_password
  volumes:
    - ./mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js
```

### 集群部署

使用 Docker Swarm 或 Kubernetes 进行生产环境部署时：
1. 使用外部 MongoDB 服务
2. 配置日志聚合
3. 设置监控和告警
4. 实现滚动更新策略

## 🐛 故障排除

### 常见问题

1. **MongoDB 连接失败**
   ```bash
   # 检查 MongoDB 是否就绪
   docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
   ```

2. **容器无法启动**
   ```bash
   # 查看详细错误信息
   docker-compose logs vivbliss-scraper
   ```

3. **权限错误**
   ```bash
   # 确保脚本可执行
   chmod +x scripts/*.sh scripts/*.py
   ```

4. **磁盘空间不足**
   ```bash
   # 清理未使用的 Docker 资源
   docker system prune -f
   ```

### 重置环境

```bash
# 完全重置（删除所有数据）
docker-compose down -v
docker-compose up --build
```