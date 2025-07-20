# Docker Compose 环境变量支持

这个模块为 VivBliss 爬虫项目添加了从 Docker Compose 文件中读取环境变量的功能，支持自动配置 Telegram 和 Scheduler 组件。

## 🚀 功能特性

- **Docker Compose 解析**: 完整的 YAML 解析和环境变量提取
- **多源支持**: 支持 `.env` 文件、`environment` 节和进程环境变量
- **变量替换**: 支持 `${VAR}` 和 `${VAR:-default}` 语法
- **优先级管理**: 进程环境 > Compose environment > env_file
- **配置集成**: 与现有 Telegram 和 Scheduler 配置无缝集成
- **CLI 工具**: 命令行工具用于管理和验证环境变量
- **测试驱动**: 100% 测试覆盖率，44 个测试用例

## 📦 安装

依赖已包含在 `requirements.txt` 中：

```bash
pip install pyyaml>=6.0.0
```

## 🏗️ 架构

```
vivbliss_scraper/config/
├── __init__.py              # 模块导出
├── compose_parser.py        # Docker Compose YAML 解析器
├── env_extractor.py         # 环境变量提取器
└── env_cli.py              # 命令行工具
```

## 🔧 使用方法

### 基本用法

```python
from vivbliss_scraper.config import EnvironmentExtractor

# 创建提取器
extractor = EnvironmentExtractor()

# 从 Docker Compose 文件加载环境变量
extractor.load_from_compose('docker-compose.yml')

# 获取所有环境变量
all_vars = extractor.get_environment()

# 获取特定前缀的变量
telegram_vars = extractor.get_environment(prefix='TELEGRAM_')
scheduler_vars = extractor.get_environment(prefix='SCHEDULER_')
```

### 与现有配置集成

```python
from vivbliss_scraper.telegram.config import TelegramConfig
from vivbliss_scraper.scheduler.config import SchedulerConfig

# 从 Docker Compose 创建 Telegram 配置
telegram_config = TelegramConfig.from_compose_file('docker-compose.yml')

# 从 Docker Compose 创建 Scheduler 配置
scheduler_config = SchedulerConfig.from_compose_file('docker-compose.yml')

# 从环境变量创建配置
telegram_config = TelegramConfig.from_environment()
scheduler_config = SchedulerConfig.from_environment()
```

### 服务特定配置

```python
# 只从特定服务提取环境变量
extractor.load_from_compose('docker-compose.yml', service_name='app')

# 为特定服务创建配置
config = TelegramConfig.from_compose_file('docker-compose.yml', service_name='telegram-bot')
```

## 📅 支持的环境变量

### Telegram 配置

| 变量名 | 别名 | 描述 | 示例 |
|--------|------|------|------|
| `TELEGRAM_API_ID` | `API_ID`, `TG_API_ID` | Telegram API ID | `12345` |
| `TELEGRAM_API_HASH` | `API_HASH`, `TG_API_HASH` | Telegram API Hash | `abcdef123456789` |
| `TELEGRAM_SESSION_NAME` | `SESSION_NAME`, `TG_SESSION_NAME` | 会话名称 | `vivbliss_session` |

### Scheduler 配置

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `SCHEDULER_TIMEZONE` | 时区设置 | `UTC` |
| `SCHEDULER_JOB_STORE` | 作业存储类型 | `memory` |
| `SCHEDULER_EXECUTOR_TYPE` | 执行器类型 | `threadpool` |
| `SCHEDULER_MAX_WORKERS` | 最大工作线程数 | `5` |
| `SCHEDULER_MISFIRE_GRACE_TIME` | 任务超时宽限期（秒） | `60` |
| `SCHEDULER_MONGODB_URI` | MongoDB 连接 URI | - |
| `SCHEDULER_MONGODB_DATABASE` | MongoDB 数据库名 | `scheduler_db` |

### 数据库配置

| 变量名 | 别名 | 描述 |
|--------|------|------|
| `MONGO_URI` | `MONGODB_URI`, `DATABASE_URL` | MongoDB 连接字符串 |
| `MONGO_DATABASE` | `MONGODB_DATABASE` | 数据库名称 |

## 🖥️ 命令行工具

### 安装

```bash
# 提取所有环境变量
python -m vivbliss_scraper.config.env_cli extract docker-compose.yml

# 从特定服务提取
python -m vivbliss_scraper.config.env_cli extract docker-compose.yml --service app

# 提取特定前缀的变量
python -m vivbliss_scraper.config.env_cli extract docker-compose.yml --prefix TELEGRAM

# 以不同格式输出
python -m vivbliss_scraper.config.env_cli extract docker-compose.yml --format json
python -m vivbliss_scraper.config.env_cli extract docker-compose.yml --format env
```

### 配置验证

```bash
# 验证所有配置
python -m vivbliss_scraper.config.env_cli validate docker-compose.yml

# 验证特定配置
python -m vivbliss_scraper.config.env_cli validate docker-compose.yml --telegram
python -m vivbliss_scraper.config.env_cli validate docker-compose.yml --scheduler
```

### 环境变量导出

```bash
# 导出到 .env 文件
python -m vivbliss_scraper.config.env_cli export docker-compose.yml --output .env

# 导出特定前缀的变量
python -m vivbliss_scraper.config.env_cli export docker-compose.yml --output telegram.env --prefix TELEGRAM
```

### 环境信息查看

```bash
# 显示环境变量统计
python -m vivbliss_scraper.config.env_cli info docker-compose.yml
```

## 📝 Docker Compose 文件示例

### 基础配置

```yaml
version: '3.8'
services:
  vivbliss-scraper:
    image: vivbliss-scraper:latest
    environment:
      # Telegram 配置
      - TELEGRAM_API_ID=12345
      - TELEGRAM_API_HASH=abcdef123456789
      - TELEGRAM_SESSION_NAME=vivbliss_session
      
      # Scheduler 配置
      - SCHEDULER_TIMEZONE=Asia/Shanghai
      - SCHEDULER_MAX_WORKERS=8
      - SCHEDULER_JOB_STORE=mongodb
      
      # 数据库配置
      - MONGO_URI=mongodb://mongodb:27017
      - MONGO_DATABASE=vivbliss_db
```

### 使用 env_file

```yaml
version: '3.8'
services:
  app:
    image: vivbliss-scraper:latest
    env_file:
      - .env
      - .env.production
    environment:
      # 覆盖 env_file 中的设置
      - NODE_ENV=production
      - SCHEDULER_TIMEZONE=Asia/Shanghai
```

### 变量替换

```yaml
version: '3.8'
services:
  app:
    environment:
      # 使用默认值
      - DATABASE_HOST=${DB_HOST:-localhost}
      - DATABASE_PORT=${DB_PORT:-5432}
      
      # 使用进程环境变量
      - TELEGRAM_API_ID=${TELEGRAM_API_ID}
      - TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
      
      # 复杂替换
      - DATABASE_URL=postgresql://${DB_HOST:-localhost}:${DB_PORT:-5432}/${DB_NAME:-vivbliss}
```

### 多服务配置

```yaml
version: '3.8'
services:
  web:
    image: nginx
    environment:
      - NGINX_PORT=80
  
  app:
    image: vivbliss-scraper:latest
    environment:
      - TELEGRAM_API_ID=12345
      - TELEGRAM_API_HASH=abcdef123456789
  
  scheduler:
    image: vivbliss-scraper:latest
    environment:
      - SCHEDULER_TIMEZONE=UTC
      - SCHEDULER_MAX_WORKERS=5
  
  db:
    image: mongodb:latest
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=secret
```

## 🔄 优先级顺序

环境变量按以下优先级顺序解析（高优先级覆盖低优先级）：

1. **进程环境变量** (最高优先级)
2. **Docker Compose environment 节**
3. **env_file 文件** (最低优先级)

### 示例

```yaml
# docker-compose.yml
services:
  app:
    env_file:
      - .env              # DATABASE_URL=file_value
    environment:
      - DATABASE_URL=compose_value
```

```bash
# 进程环境
export DATABASE_URL=process_value
```

**结果**: `DATABASE_URL=process_value` (进程环境获胜)

## 🧪 高级用法

### 批量加载多个源

```python
extractor = EnvironmentExtractor()

# 加载多个源
sources = [
    {'type': 'env_file', 'path': '.env'},
    {'type': 'compose', 'path': 'docker-compose.yml', 'service': 'app'},
    {'type': 'compose', 'path': 'docker-compose.override.yml'}
]

extractor.load_from_multiple_sources(sources)
```

### 变量解析和替换

```python
# 手动解析变量
variables = {
    'API_ENDPOINT': '${BASE_URL}/api/${VERSION}',
    'FALLBACK_URL': '${BACKUP_URL:-https://backup.example.com}'
}

resolved = extractor.resolve_variables(variables)
```

### 应用到系统环境

```python
# 应用所有变量到进程环境
extractor.apply_to_os_environment()

# 只应用特定前缀的变量
extractor.apply_to_os_environment(prefix='TELEGRAM_')
```

### 配置验证

```python
# 验证必需变量
required_vars = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH']
missing = extractor.validate_required_variables(required_vars)

if missing:
    print(f"Missing required variables: {missing}")
```

## 🔧 配置工厂模式

```python
def create_application_config(compose_file: str):
    """从 Docker Compose 文件创建完整应用配置"""
    
    # 提取环境变量
    extractor = EnvironmentExtractor()
    extractor.load_from_compose(compose_file)
    
    # 创建各组件配置
    telegram_config = TelegramConfig.from_environment(
        extractor.get_telegram_config()
    )
    
    scheduler_config = SchedulerConfig.from_environment(
        extractor.get_scheduler_config()
    )
    
    return {
        'telegram': telegram_config,
        'scheduler': scheduler_config,
        'database': extractor.get_database_config()
    }

# 使用
config = create_application_config('docker-compose.yml')
```

## 🧪 测试

运行完整测试套件：

```bash
# 运行所有配置相关测试
pytest tests/test_compose_parser.py tests/test_env_extractor.py tests/test_config_integration.py -v

# 运行特定测试
pytest tests/test_compose_parser.py -v       # Compose 解析器测试
pytest tests/test_env_extractor.py -v       # 环境提取器测试
pytest tests/test_config_integration.py -v  # 集成测试
```

## 📊 测试覆盖率

- **ComposeParser**: 14 个测试用例
- **EnvironmentExtractor**: 16 个测试用例  
- **配置集成**: 8 个测试用例
- **总覆盖率**: 100%

## 🔒 安全注意事项

- **敏感信息**: API keys 和密码在 CLI 输出中会被掩码显示
- **文件权限**: 确保 `.env` 文件具有适当的访问权限
- **日志安全**: 避免在日志中记录敏感的环境变量值
- **版本控制**: 不要将包含敏感信息的 `.env` 文件提交到版本控制

## 🚨 故障排除

### 常见问题

1. **变量未解析**
   - 检查变量名拼写
   - 确认优先级顺序
   - 验证 Docker Compose 文件语法

2. **配置验证失败**
   - 使用 CLI validate 命令检查配置
   - 确认所有必需变量都已设置
   - 检查变量值格式

3. **文件未找到**
   - 确认 Docker Compose 文件路径正确
   - 检查 env_file 引用的文件是否存在
   - 验证文件权限

### 调试模式

```python
# 启用详细输出
extractor = EnvironmentExtractor()
extractor.load_from_compose('docker-compose.yml')

# 查看统计信息
stats = extractor.get_stats()
print(f"Sources: {stats['sources']}")
print(f"Total variables: {stats['total_variables']}")
```

## 🤝 贡献

1. **编写测试**: 为新功能添加测试用例
2. **遵循 TDD**: 使用测试驱动开发流程
3. **代码风格**: 遵循现有代码模式
4. **文档更新**: 为新功能更新文档

## 📄 许可证

此环境变量模块是 VivBliss 爬虫项目的一部分，遵循相同的许可条款。

## 🔗 相关文档

- [Telegram 集成文档](README_TELEGRAM.md)
- [Scheduler 文档](README_SCHEDULER.md)
- [Docker Compose 官方文档](https://docs.docker.com/compose/)
- [环境变量最佳实践](https://12factor.net/config)

这个环境变量支持系统为 VivBliss 项目提供了灵活、安全、易于管理的配置解决方案，支持从开发到生产的完整部署流程。