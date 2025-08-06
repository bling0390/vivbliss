# wait_for_mongo.py 使用指南

`wait_for_mongo.py` 是一个用于等待 MongoDB 服务就绪的工具脚本，支持灵活的环境变量配置和认证。

## 🚀 功能特性

- ✅ **灵活的环境变量配置**
- ✅ **支持 MongoDB 用户名/密码认证**
- ✅ **密码隐藏保护**
- ✅ **详细的错误提示**
- ✅ **可配置的重试机制**
- ✅ **命令行参数支持**

## 📋 支持的环境变量

### 优先级顺序
1. `MONGO_URI` - 完整的 MongoDB URI（最高优先级）
2. 单独的配置变量组合
3. 默认值

### 环境变量列表

| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `MONGO_URI` | 完整的 MongoDB URI | - | `mongodb://user:pass@host:27017/db` |
| `MONGO_HOST` | MongoDB 主机地址 | `mongodb` | `localhost`, `mongodb` |
| `MONGO_PORT` | MongoDB 端口 | `27017` | `27017`, `27018` |
| `MONGO_USERNAME` | MongoDB 用户名 | - | `admin`, `user` |
| `MONGO_PASSWORD` | MongoDB 密码 | - | `password`, `secret` |
| `MONGO_DATABASE` | 数据库名称 | `vivbliss_db` | `mydb`, `test` |

## 🔧 使用方法

### 基本用法

```bash
# 使用默认设置（30次重试，间隔2秒）
python3 scripts/wait_for_mongo.py

# 自定义重试次数和间隔
python3 scripts/wait_for_mongo.py <最大重试次数> <重试间隔秒数>

# 例如：5次重试，每次间隔1秒
python3 scripts/wait_for_mongo.py 5 1
```

### 环境变量配置

#### 场景1: 无认证连接
```bash
export MONGO_HOST=localhost
export MONGO_PORT=27017
python3 scripts/wait_for_mongo.py
```

#### 场景2: 带认证连接
```bash
export MONGO_HOST=localhost
export MONGO_PORT=27017
export MONGO_USERNAME=admin
export MONGO_PASSWORD=password
export MONGO_DATABASE=mydb
python3 scripts/wait_for_mongo.py
```

#### 场景3: 使用完整URI
```bash
export MONGO_URI="mongodb://admin:password@localhost:27017/mydb?authSource=admin"
python3 scripts/wait_for_mongo.py
```

### Docker 环境使用

#### 在 Docker Compose 中使用

```yaml
services:
  app:
    build: .
    depends_on:
      mongodb:
        condition: service_healthy
    environment:
      - MONGO_HOST=mongodb
      - MONGO_USERNAME=admin
      - MONGO_PASSWORD=password
    command: |
      sh -c "
        python3 scripts/wait_for_mongo.py &&
        python3 -m scrapy crawl vivbliss
      "
```

#### 手动在容器中测试

```bash
# 测试连接
docker-compose exec vivbliss-scraper python3 scripts/wait_for_mongo.py

# 快速测试（1次重试）
docker-compose exec vivbliss-scraper python3 scripts/wait_for_mongo.py 1 0
```

## 📊 输出示例

### 成功连接
```
MongoDB 连接配置:
  主机: localhost
  端口: 27017
  数据库: vivbliss_db
  用户: admin
  最大重试: 30 次
  重试间隔: 2 秒

Waiting for MongoDB at mongodb://admin:****@localhost:27017/vivbliss_db?authSource=admin...
✓ MongoDB is ready after 1 attempt
```

### 连接失败
```
MongoDB 连接配置:
  主机: localhost
  端口: 27017
  数据库: vivbliss_db
  最大重试: 3 次
  重试间隔: 1 秒

Waiting for MongoDB at mongodb://localhost:27017...
Attempt 1/3 failed: Connection refused
Attempt 2/3 failed: Connection refused
Attempt 3/3 failed: Connection refused
✗ MongoDB connection timeout

检查以下事项：
1. MongoDB 服务是否正在运行
2. 主机地址和端口是否正确
```

## 🔒 安全特性

### 密码隐藏
脚本会自动在输出中隐藏密码信息：
- `mongodb://user:password@host:27017/db` → `mongodb://user:****@host:27017/db`

### 环境变量保护
- 密码不会出现在进程列表中
- 支持从环境变量或 `.env` 文件读取配置

## 🧪 测试和验证

项目包含多个测试文件来验证功能：

```bash
# 基础功能测试
python3 test_uri_simple.py

# 完整功能验证
python3 test_wait_for_mongo_final.py

# 完整连接测试（需要实际 MongoDB）
python3 test_mongo_auth.py
```

## 🔄 集成到应用中

### 作为依赖检查
```bash
#!/bin/bash
# 启动脚本示例

# 等待 MongoDB 就绪
python3 scripts/wait_for_mongo.py
if [ $? -ne 0 ]; then
    echo "MongoDB 不可用，退出"
    exit 1
fi

# 启动应用
python3 -m scrapy crawl vivbliss
```

### 在 Python 代码中使用
```python
import subprocess
import sys

def wait_for_mongodb():
    """等待 MongoDB 服务就绪"""
    result = subprocess.run([
        "python3", "scripts/wait_for_mongo.py", "10", "1"
    ])
    return result.returncode == 0

if not wait_for_mongodb():
    print("MongoDB 服务不可用")
    sys.exit(1)

# 继续应用逻辑
```

## 🛠️ 高级配置

### 自定义超时和重试
```bash
# 快速检查（1次重试，无延迟）
python3 scripts/wait_for_mongo.py 1 0

# 长时间等待（60次重试，间隔5秒）
python3 scripts/wait_for_mongo.py 60 5
```

### 组合不同配置方式
```bash
# 环境变量 + 命令行参数
export MONGO_USERNAME=admin
export MONGO_PASSWORD=secret
python3 scripts/wait_for_mongo.py 5 1
```

## 🐛 故障排除

### 常见错误和解决方案

1. **Connection refused**
   - MongoDB 服务未启动
   - 端口配置错误
   - 防火墙阻止连接

2. **Authentication failed**
   - 用户名或密码错误
   - 用户不存在
   - authSource 参数错误

3. **Connection timeout**
   - 网络延迟过高
   - MongoDB 负载过重
   - 增加重试次数和间隔

### 调试技巧
```bash
# 显示详细配置信息
python3 scripts/wait_for_mongo.py 1 0

# 检查环境变量
env | grep MONGO_

# 测试不同配置
MONGO_HOST=localhost python3 scripts/wait_for_mongo.py 1 0
```

## 📈 性能建议

- **开发环境**: 使用较短的重试间隔 (1-2秒)
- **生产环境**: 使用较长的重试间隔 (3-5秒) 避免过度重试
- **CI/CD**: 设置合理的总超时时间，避免构建卡死

这个工具确保了应用在 MongoDB 完全就绪后才开始运行，提高了系统的可靠性和稳定性。