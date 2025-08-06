# MongoDB 认证配置指南

本项目支持 MongoDB 用户名/密码认证，可以通过环境变量灵活配置。

## 🔐 环境变量配置

### 基础配置（无认证）

如果你的 MongoDB 没有启用认证：

```env
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DATABASE=vivbliss_db
```

### 认证配置

如果你的 MongoDB 启用了认证：

```env
# MongoDB 连接配置
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DATABASE=vivbliss_db

# MongoDB 认证凭证
MONGO_USERNAME=your_username
MONGO_PASSWORD=your_password
```

### 使用完整 URI

你也可以直接提供完整的 MongoDB URI（将覆盖上述单独的配置）：

```env
MONGO_URI=mongodb://username:password@localhost:27017/vivbliss_db?authSource=admin
```

## 🐳 Docker Compose 配置

### 1. MongoDB 服务配置

`docker-compose.yml` 中的 MongoDB 服务已配置认证：

```yaml
services:
  mongodb:
    image: mongo:7.0
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USERNAME:-admin}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD:-password}
```

### 2. 应用服务配置

爬虫服务会自动使用环境变量连接 MongoDB：

```yaml
services:
  vivbliss-scraper:
    environment:
      - MONGO_HOST=mongodb
      - MONGO_PORT=27017
      - MONGO_USERNAME=${MONGO_USERNAME:-admin}
      - MONGO_PASSWORD=${MONGO_PASSWORD:-password}
      - MONGO_DATABASE=${MONGO_DATABASE:-vivbliss_db}
```

### 3. 环境变量文件

创建 `.env` 文件（用于本地开发）：

```env
MONGO_USERNAME=admin
MONGO_PASSWORD=your_secure_password
MONGO_DATABASE=vivbliss_db
```

或使用 `.env.docker`（用于 Docker 环境）：

```env
# MongoDB 认证凭证
MONGO_USERNAME=admin
MONGO_PASSWORD=password
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=password
```

## 🧪 测试连接

使用提供的测试脚本验证 MongoDB 连接：

```bash
# 测试本地连接
python test_mongo_auth.py

# 使用环境变量测试
MONGO_USERNAME=admin MONGO_PASSWORD=password python test_mongo_auth.py

# 测试 Docker 环境
docker-compose exec vivbliss-scraper python test_mongo_auth.py
```

## 🔧 配置优先级

环境变量按以下优先级生效：

1. `MONGO_URI`（如果设置，将覆盖所有其他配置）
2. 单独的配置变量（`MONGO_HOST`, `MONGO_PORT`, `MONGO_USERNAME`, `MONGO_PASSWORD`）
3. 默认值（`localhost:27017`，无认证）

## 📝 代码实现

在 `settings.py` 中的实现：

```python
# MongoDB Configuration
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
MONGO_USERNAME = os.getenv('MONGO_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'vivbliss_db')

# Build MongoDB URI with optional authentication
if MONGO_USERNAME and MONGO_PASSWORD:
    MONGO_URI = f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}?authSource=admin'
else:
    MONGO_URI = f'mongodb://{MONGO_HOST}:{MONGO_PORT}'

# Allow direct URI override
MONGO_URI = os.getenv('MONGO_URI', MONGO_URI)
```

## ⚠️ 安全建议

1. **不要在代码中硬编码密码**
2. **使用强密码**，避免使用默认密码
3. **限制 MongoDB 访问**，只允许必要的 IP 地址连接
4. **使用不同的密码**用于开发和生产环境
5. **定期更新密码**并轮换凭证
6. **不要将 `.env` 文件提交到版本控制**

## 🚀 快速开始

1. 复制环境变量示例文件：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，设置你的 MongoDB 凭证

3. 启动服务：
   ```bash
   # 使用 Docker Compose
   docker-compose up -d
   
   # 或本地运行
   python -m scrapy crawl vivbliss
   ```

## 🔍 故障排除

### 连接测试工具

项目提供了多个工具来测试 MongoDB 连接：

1. **wait_for_mongo.py** - 等待 MongoDB 服务就绪
   ```bash
   # 使用默认设置（30次重试，间隔2秒）
   python3 scripts/wait_for_mongo.py
   
   # 自定义重试参数（5次重试，间隔1秒）
   python3 scripts/wait_for_mongo.py 5 1
   ```

2. **test_mongo_auth.py** - 完整的连接测试和验证
   ```bash
   python3 test_mongo_auth.py
   ```

### 连接失败

如果遇到连接问题，请检查：

1. MongoDB 服务是否正在运行
2. 用户名和密码是否正确
3. 用户是否有访问指定数据库的权限
4. `authSource` 参数是否正确（通常是 `admin`）

`wait_for_mongo.py` 现在会显示详细的连接信息和错误提示。

### 认证失败

如果认证失败：

1. 确认 MongoDB 是否启用了认证
2. 检查用户是否存在于正确的认证数据库中
3. 验证用户权限是否足够

### Docker 环境问题

在 Docker 环境中：

1. 确保服务名称正确（使用 `mongodb` 而不是 `localhost`）
2. 检查环境变量是否正确传递到容器
3. 查看容器日志：`docker-compose logs mongodb`
4. 使用 `wait_for_mongo.py` 脚本进行连接测试：
   ```bash
   docker-compose exec vivbliss-scraper python3 scripts/wait_for_mongo.py
   ```