# VivBliss 项目完整文档

> 📚 这是一个统一的项目文档，整合了所有模块、配置和使用指南

---

## 📋 目录

- [项目概述](#项目概述)
- [SPARC 开发环境](#sparc-开发环境)
- [Claude-Flow 设置](#claude-flow-设置)
- [内存管理系统](#内存管理系统)
- [智能体协调系统](#智能体协调系统)
- [VivBliss 爬虫系统](#vivbliss-爬虫系统)
- [调度器系统](#调度器系统)
- [Telegram 集成](#telegram-集成)
- [Docker 环境配置](#docker-环境配置)
- [MongoDB 认证配置](#mongodb-认证配置)
- [Scrapy 配置详解](#scrapy-配置详解)
- [故障排除和最佳实践](#故障排除和最佳实践)

---

## 🎯 项目概述

VivBliss 是一个基于 SPARC 方法论的智能网络爬虫项目，集成了 Claude-Flow 编排系统、多智能体协调、Telegram 自动化上传和高级调度功能。

### 核心特性

- **🧠 SPARC 方法论**: 规范、伪代码、架构、精炼、完成的系统化开发流程
- **🤖 Claude-Flow 编排**: AI 智能体协调和内存管理系统
- **🕷️ 智能爬虫**: 基于 Scrapy 的高性能网页爬取系统
- **📱 Telegram 集成**: 自动文件上传和通知系统
- **⏰ 高级调度**: 支持 Cron 表达式的定时任务系统
- **🐳 Docker 支持**: 完整的容器化部署方案
- **🔒 安全认证**: MongoDB 用户认证和环境变量管理

### 技术栈

- **Python 3.8+**: 核心开发语言
- **Scrapy**: 网络爬虫框架
- **MongoDB**: 数据存储
- **Docker**: 容器化部署
- **APScheduler**: 任务调度
- **Pyrogram**: Telegram 客户端
- **Claude Code**: AI 辅助开发

---

## 🚀 SPARC 开发环境

### 关键原则：所有操作必须并发执行

**绝对规则**：所有操作必须在单个消息中并发/并行执行：

#### 🔴 强制并发模式

1. **TodoWrite**: 始终在一次调用中批量处理所有待办事项（最少5-10个待办事项）
2. **Task 工具**: 始终在一条消息中生成所有智能体并提供完整指令
3. **文件操作**: 始终在一条消息中批量处理所有读取/写入/编辑操作
4. **Bash 命令**: 始终在一条消息中批量处理所有终端操作
5. **内存操作**: 始终在一条消息中批量处理所有内存存储/检索操作

#### ⚡ 黄金法则："1条消息 = 所有相关操作"

**正确并发执行的示例：**
```javascript
// ✅ 正确：所有内容在一条消息中
[单条消息]:
  - TodoWrite { todos: [10+个待办事项，包含所有状态/优先级] }
  - Task("智能体1，包含完整指令和钩子")
  - Task("智能体2，包含完整指令和钩子")  
  - Task("智能体3，包含完整指令和钩子")
  - Read("file1.js")
  - Read("file2.js")
  - Write("output1.js", content)
  - Write("output2.js", content)
  - Bash("npm install")
  - Bash("npm test")
  - Bash("npm run build")
```

### SPARC 开发命令

#### 核心 SPARC 命令
- `./claude-flow sparc modes`: 列出所有可用的 SPARC 开发模式
- `./claude-flow sparc run <mode> "<task>"`: 为特定任务执行指定的 SPARC 模式
- `./claude-flow sparc tdd "<feature>"`: 使用 SPARC 方法论运行完整的 TDD 工作流
- `./claude-flow sparc info <mode>`: 获取特定模式的详细信息

#### 标准构建命令
- `npm run build`: 构建项目
- `npm run test`: 运行测试套件
- `npm run lint`: 运行代码检查和格式化检查
- `npm run typecheck`: 运行 TypeScript 类型检查

### SPARC 方法论工作流

#### 1. 规范阶段 (Specification Phase)
```bash
# 创建详细规范和需求
./claude-flow sparc run spec-pseudocode "定义用户认证需求"
```
- 定义清晰的功能需求
- 记录边缘情况和约束条件
- 创建用户故事和验收标准
- 建立非功能性需求

#### 2. 伪代码阶段 (Pseudocode Phase)
```bash
# 开发算法逻辑和数据流
./claude-flow sparc run spec-pseudocode "创建认证流程伪代码"
```
- 将复杂逻辑分解为步骤
- 定义数据结构和接口
- 规划错误处理和边缘情况
- 创建模块化、可测试的组件

#### 3. 架构阶段 (Architecture Phase)
```bash
# 设计系统架构和组件结构
./claude-flow sparc run architect "设计认证服务架构"
```
- 创建系统图和组件关系
- 定义 API 契约和接口
- 规划数据库模式和数据流
- 建立安全性和可扩展性模式

#### 4. 精炼阶段 (Refinement Phase) - TDD 实现
```bash
# 执行测试驱动开发周期
./claude-flow sparc tdd "实现用户认证系统"
```

**TDD 周期：**
1. **红灯 (Red)**: 首先编写失败测试
2. **绿灯 (Green)**: 实现最小代码使测试通过
3. **重构 (Refactor)**: 优化和清理代码
4. **重复 (Repeat)**: 继续直到功能完成

#### 5. 完成阶段 (Completion Phase)
```bash
# 集成、文档和验证
./claude-flow sparc run integration "将认证与用户管理集成"
```
- 集成所有组件
- 进行端到端测试
- 创建全面文档
- 根据原始需求进行验证

### SPARC 模式参考

#### 开发模式
- **`architect`**: 系统设计和架构规划
- **`code`**: 清洁、模块化代码实现
- **`tdd`**: 测试驱动开发和测试
- **`spec-pseudocode`**: 需求和算法规划
- **`integration`**: 系统集成和协调

#### 质量保证模式
- **`debug`**: 故障排除和错误解决
- **`security-review`**: 安全分析和漏洞评估
- **`refinement-optimization-mode`**: 性能优化和重构

#### 支持模式
- **`docs-writer`**: 文档创建和维护
- **`devops`**: 部署和基础设施管理
- **`mcp`**: 外部服务集成
- **`swarm`**: 复杂任务的多智能体协调

---

## 🔧 Claude-Flow 设置

### 已安装的文件
- `.claude/` - Claude Code 配置和斜杠命令
- `.roo/` - SPARC 方法论配置和工作流
- `.roomodes` - 开发模式定义文件
- `claude-flow` - 本地执行脚本
- `CLAUDE.md` - 项目指导文档
- `coordination.md` - 多智能体协调说明
- `memory-bank.md` - 内存系统配置
- `memory/` - 内存数据存储目录

### 验证安装
```bash
# 测试 claude-flow 是否正常工作
./claude-flow --help

# 检查配置文件
ls -la .claude .roo .roomodes
```

### 快速开始

#### SPARC 方法论
```bash
# TDD 模式开发
./claude-flow sparc --mode=tdd "你的任务描述"

# 架构设计
./claude-flow sparc --mode=architect "设计系统架构"

# 代码实现
./claude-flow sparc --mode=coder "实现具体功能"

# 规范定义
./claude-flow sparc --mode=spec-pseudocode "定义功能需求"
```

#### Swarm 多智能体协作
```bash
# 研究阶段
./claude-flow swarm --strategy=research "技术调研"

# 开发阶段
./claude-flow swarm --strategy=development "功能开发"

# 测试阶段
./claude-flow swarm --strategy=testing "测试优化"
```

#### 内存管理
```bash
# 查询存储信息
./claude-flow memory query "搜索内容"

# 查看内存统计
./claude-flow memory stats

# 导出内存数据
./claude-flow memory export backup.json
```

---

## 🧠 内存管理系统

### 概述
Claude-Flow 内存系统提供跨智能体会话的持久存储和智能信息检索。它采用混合方法，结合 SQL 数据库和语义搜索功能。

### 存储后端
- **主要存储**: JSON 数据库（`./memory/claude-flow-data.json`）
- **会话存储**: 基于文件的存储（`./memory/sessions/`）
- **缓存**: 频繁访问数据的内存缓存

### 内存组织
- **Namespaces**: 相关信息的逻辑分组
- **Sessions**: 有时间界限的对话上下文
- **Indexing**: 自动内容索引，快速检索
- **Replication**: 可选的分布式存储支持

### 命令
- `npx claude-flow memory query <search>`: 搜索存储的信息
- `npx claude-flow memory stats`: 显示内存使用统计
- `npx claude-flow memory export <file>`: 将内存导出到文件
- `npx claude-flow memory import <file>`: 从文件导入内存

### 配置
内存设置在 `claude-flow.config.json` 中配置：
```json
{
  "memory": {
    "backend": "json",
    "path": "./memory/claude-flow-data.json",
    "cacheSize": 1000,
    "indexing": true,
    "namespaces": ["default", "agents", "tasks", "sessions"],
    "retentionPolicy": {
      "sessions": "30d",
      "tasks": "90d",
      "agents": "permanent"
    }
  }
}
```

### 内存类型
- **情景记忆 (Episodic)**: 对话和交互历史
- **语义记忆 (Semantic)**: 事实知识和关系
- **过程记忆 (Procedural)**: 任务模式和工作流
- **元记忆 (Meta)**: 系统配置和偏好

---

## 🤖 智能体协调系统

### 概述
Claude-Flow 协调系统负责管理多个 AI 智能体协同完成复杂任务。它提供智能任务分发、资源管理和智能体间通信功能。

### 智能体类型与能力
- **研究员 (Researcher)**: 网络搜索、信息收集、知识整合
- **编程员 (Coder)**: 代码分析、开发、调试、测试
- **分析师 (Analyst)**: 数据处理、模式识别、洞察生成
- **协调员 (Coordinator)**: 任务规划、资源分配、工作流管理
- **通用型 (General)**: 具备均衡能力的多用途智能体

### 任务管理
- **优先级层次**: 1（最低）到 10（最高）
- **依赖关系**: 任务可以依赖其他任务的完成
- **并行执行**: 独立任务并发运行
- **负载均衡**: 基于智能体容量的自动分发

### 协调命令
```bash
# Agent Management
npx claude-flow agent spawn <type> --name <name> --priority <1-10>
npx claude-flow agent list
npx claude-flow agent info <agent-id>
npx claude-flow agent terminate <agent-id>

# Task Management  
npx claude-flow task create <type> <description> --priority <1-10> --deps <task-ids>
npx claude-flow task list --verbose
npx claude-flow task status <task-id>
npx claude-flow task cancel <task-id>

# System Monitoring
npx claude-flow status --verbose
npx claude-flow monitor --interval 5000
```

### 工作流执行
工作流以 JSON 格式定义，可以编排复杂的多智能体操作：
```bash
npx claude-flow workflow examples/research-workflow.json
npx claude-flow workflow examples/development-config.json --async
```

### 配置
协调设置在 `claude-flow.config.json` 中：
```json
{
  "orchestrator": {
    "maxConcurrentTasks": 10,
    "taskTimeout": 300000,
    "defaultPriority": 5
  },
  "agents": {
    "maxAgents": 20,
    "defaultCapabilities": ["research", "code", "terminal"],
    "resourceLimits": {
      "memory": "1GB",
      "cpu": "50%"
    }
  }
}
```

---

## 🕷️ VivBliss 爬虫系统

### 概述
基于 Scrapy 的高性能网络爬虫，用于从 vivbliss.com 提取文章内容并存储到 MongoDB。

### 核心功能
- **测试驱动开发 (TDD)** 方法
- **多重回退选择器**的稳健文章提取
- **自动分页跟踪**
- **MongoDB 持久化存储**
- **速率限制和礼貌爬取**
- **全面的测试覆盖**

### 项目结构
```
vivbliss_scraper/
├── vivbliss_scraper/
│   ├── __init__.py
│   ├── items.py          # 数据模型
│   ├── pipelines.py      # MongoDB 管道（带重试逻辑）
│   ├── settings.py       # Scrapy 设置
│   ├── spiders/
│   │   ├── __init__.py
│   │   └── vivbliss.py   # 主爬虫
│   ├── config/           # 配置管理
│   ├── scheduler/        # 调度系统
│   ├── telegram/         # Telegram 集成
│   └── utils/           # 工具类
├── scripts/
│   ├── entrypoint.sh     # Docker 容器入口点
│   ├── health_check.py   # 容器健康检查
│   ├── wait_for_mongo.py # MongoDB 就绪检查
│   └── run_spider.sh     # 爬虫执行脚本
├── tests/               # 测试套件
├── docker-compose.yml   # Docker Compose 配置
├── Dockerfile          # Docker 镜像定义
└── requirements.txt    # Python 依赖
```

### 数据模型
爬虫提取以下字段：
- `title`: 文章标题
- `url`: 文章完整 URL
- `content`: 文章摘要或内容
- `date`: 发布日期
- `category`: 文章分类（默认为 "Uncategorized"）

### MongoDB 存储
数据以以下结构存储在 MongoDB 中：
```json
{
  "_id": "ObjectId",
  "title": "文章标题",
  "url": "https://vivbliss.com/article-url",
  "content": "文章内容...",
  "date": "2024-01-01",
  "category": "技术"
}
```

### 使用方法

#### Docker 运行（推荐）
```bash
# 克隆项目
git clone <repository-url>
cd vivbliss_scraper

# 使用 Docker Compose 运行
docker-compose up -d
```

#### 本地运行
```bash
# 运行爬虫
scrapy crawl vivbliss

# 使用特定设置运行
scrapy crawl vivbliss -s MONGO_DATABASE=my_custom_db

# 保存为 JSON 文件（用于测试）
scrapy crawl vivbliss -o output.json
```

#### 运行测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_spider.py -v

# 运行覆盖率测试
pytest tests/ --cov=vivbliss_scraper --cov-report=html
```

---

## ⏰ 调度器系统

### 概述
基于 APScheduler 的强大调度系统，支持使用 Cron 表达式和基于间隔的调度来自动化 Scrapy 爬虫执行。

### 🚀 功能特性
- **基于 Cron 的调度**: 完整的 cron 表达式支持及别名
- **间隔调度**: 以特定间隔运行爬虫（分钟、小时、天）
- **任务管理**: 创建、更新、启用/禁用和移除计划任务
- **持久化**: 导出/导入任务配置
- **CLI 界面**: 命令行管理工具
- **监控**: 任务状态跟踪和日志记录
- **测试驱动开发**: 100% 测试覆盖率

### 架构
```
vivbliss_scraper/scheduler/
├── __init__.py              # 包初始化
├── config.py                # 调度器配置
├── scheduler.py             # 主调度器类
├── task_manager.py          # 任务管理逻辑
├── cron_parser.py           # Cron 表达式解析器
├── cli.py                   # 命令行界面
└── example_usage.py         # 使用示例
```

### 基本使用
```python
from vivbliss_scraper.scheduler import SpiderScheduler

scheduler = SpiderScheduler()

# 添加每日任务，上午 10:30 执行
task = scheduler.add_spider_task(
    task_id='daily_scrape',
    name='每日 VivBliss 爬取',
    spider_name='vivbliss',
    cron_expression='30 10 * * *',
    description='每日 10:30 AM 爬取'
)

# 添加间隔任务（每 2 小时）
task = scheduler.add_interval_spider_task(
    task_id='hourly_scrape',
    name='双小时爬取',
    spider_name='vivbliss',
    hours=2
)

# 启动调度器
scheduler.start()
```

### Cron 表达式指南

#### 基本语法
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── 星期几 (0-7, Sunday = 0 or 7)
│ │ │ └───── 月 (1-12)
│ │ └─────── 月中日 (1-31)
│ └───────── 时 (0-23)
└─────────── 分 (0-59)
```

#### 常用示例
| 表达式 | 描述 |
|------------|-------------|
| `* * * * *` | 每分钟 |
| `0 * * * *` | 每小时 |
| `0 0 * * *` | 每日午夜 |
| `30 10 * * *` | 每日上午 10:30 |
| `0 9 * * 1-5` | 工作日上午 9:00 |
| `*/15 * * * *` | 每 15 分钟 |

### 命令行界面
```bash
# 启动调度器守护程序
python -m vivbliss_scraper.scheduler.cli start

# 添加 cron 任务
python -m vivbliss_scraper.scheduler.cli add-cron daily_task vivbliss "0 10 * * *" \
    --name "每日爬取" \
    --description "每日上午 10 点爬取"

# 列出任务
python -m vivbliss_scraper.scheduler.cli list

# 显示任务详情
python -m vivbliss_scraper.scheduler.cli show daily_task

# 启用/禁用任务
python -m vivbliss_scraper.scheduler.cli disable daily_task
python -m vivbliss_scraper.scheduler.cli enable daily_task
```

---

## 📱 Telegram 集成

### 概述
基于 Pyrogram 的 Telegram 文件上传功能，集成到 VivBliss 爬虫中。

### 🚀 功能特性
- **自动文件上传**: 上传爬取的图片和视频到 Telegram 频道/聊天
- **文件验证**: 对支持格式和文件大小的全面验证
- **错误处理**: 强大的重试机制和错误处理
- **进度跟踪**: 监控批量操作的上传进度
- **Scrapy 集成**: 与现有爬虫的无缝管道集成
- **测试驱动开发**: 95%+ 测试覆盖率

### 要求
- Python 3.8+
- Pyrogram 2.0+
- Telegram API 凭证（api_id、api_hash）
- 目标聊天/频道 ID

### 安装
```bash
pip install pyrogram
```

### 环境变量设置
```bash
# .env 文件
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_SESSION_NAME=vivbliss_bot
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_ENABLE_UPLOAD=True
```

### 模块结构
```
vivbliss_scraper/telegram/
├── __init__.py              # 包初始化
├── config.py                # Telegram 客户端配置
├── file_validator.py        # 文件验证逻辑
├── file_uploader.py         # 上传功能
├── pipeline.py              # Scrapy 管道集成
└── example_usage.py         # 使用示例
```

### 支持的文件格式

#### 图片
- JPG/JPEG、PNG、GIF、WebP、BMP

#### 视频
- MP4、AVI、MKV、MOV、WebM、FLV

#### 文件大小限制
- 最大文件大小: 50MB（Telegram 限制）

### 基本使用
```python
import asyncio
from vivbliss_scraper.telegram.config import TelegramConfig
from vivbliss_scraper.telegram.file_uploader import FileUploader

async def upload_file():
    # 配置客户端
    config = TelegramConfig(
        api_id="YOUR_API_ID",
        api_hash="YOUR_API_HASH",
        session_name="my_session"
    )
    
    # 创建并启动客户端
    client = await config.create_client()
    await client.start()
    
    # 上传文件
    uploader = FileUploader(client)
    result = await uploader.upload_file(
        chat_id=-1001234567890,
        file_path="/path/to/image.jpg",
        caption="来自 VivBliss 爬虫的上传"
    )
    
    print(f"上传结果: {result}")
    await client.stop()

# 运行上传
asyncio.run(upload_file())
```

### Scrapy 集成
在 `settings.py` 中添加：
```python
ITEM_PIPELINES = {
    'vivbliss_scraper.pipelines.MongoDBPipeline': 300,
    'vivbliss_scraper.telegram.pipeline.TelegramUploadPipeline': 400,
}
```

---

## 🐳 Docker 环境配置

### Docker Compose 环境变量支持
这个模块为 VivBliss 爬虫项目添加了从 Docker Compose 文件中读取环境变量的功能，支持自动配置 Telegram 和 Scheduler 组件。

### 🚀 功能特性
- **Docker Compose 解析**: 完整的 YAML 解析和环境变量提取
- **多源支持**: 支持 `.env` 文件、`environment` 节和进程环境变量
- **变量替换**: 支持 `${VAR}` 和 `${VAR:-default}` 语法
- **优先级管理**: 进程环境 > Compose environment > env_file
- **配置集成**: 与现有 Telegram 和 Scheduler 配置无缝集成
- **CLI 工具**: 命令行工具用于管理和验证环境变量

### 架构
```
vivbliss_scraper/config/
├── __init__.py              # 模块导出
├── compose_parser.py        # Docker Compose YAML 解析器
├── env_extractor.py         # 环境变量提取器
└── env_cli.py              # 命令行工具
```

### 基本使用
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

### 支持的环境变量

#### Telegram 配置
| 变量名 | 别名 | 描述 | 示例 |
|--------|------|------|------|
| `TELEGRAM_API_ID` | `API_ID`, `TG_API_ID` | Telegram API ID | `12345` |
| `TELEGRAM_API_HASH` | `API_HASH`, `TG_API_HASH` | Telegram API Hash | `abcdef123456789` |
| `TELEGRAM_SESSION_NAME` | `SESSION_NAME`, `TG_SESSION_NAME` | 会话名称 | `vivbliss_session` |

#### Scheduler 配置
| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `SCHEDULER_TIMEZONE` | 时区设置 | `UTC` |
| `SCHEDULER_JOB_STORE` | 作业存储类型 | `memory` |
| `SCHEDULER_EXECUTOR_TYPE` | 执行器类型 | `threadpool` |
| `SCHEDULER_MAX_WORKERS` | 最大工作线程数 | `5` |

### 命令行工具
```bash
# 提取所有环境变量
python -m vivbliss_scraper.config.env_cli extract docker-compose.yml

# 从特定服务提取
python -m vivbliss_scraper.config.env_cli extract docker-compose.yml --service app

# 验证配置
python -m vivbliss_scraper.config.env_cli validate docker-compose.yml

# 导出到 .env 文件
python -m vivbliss_scraper.config.env_cli export docker-compose.yml --output .env
```

### Docker Compose 文件示例
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
      - MONGO_HOST=mongodb
      - MONGO_PORT=27017
      - MONGO_USERNAME=admin
      - MONGO_PASSWORD=password
      - MONGO_DATABASE=vivbliss_db
```

---

## 🔒 MongoDB 认证配置

### 概述
本项目支持 MongoDB 用户名/密码认证，可以通过环境变量灵活配置。

### 环境变量配置

#### 基础配置（无认证）
```env
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DATABASE=vivbliss_db
```

#### 认证配置
```env
# MongoDB 连接配置
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DATABASE=vivbliss_db

# MongoDB 认证凭证
MONGO_USERNAME=your_username
MONGO_PASSWORD=your_password
```

#### 使用完整 URI
```env
MONGO_URI=mongodb://username:password@localhost:27017/vivbliss_db?authSource=admin
```

### Docker Compose 配置

#### MongoDB 服务配置
```yaml
services:
  mongodb:
    image: mongo:7.0
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USERNAME:-admin}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD:-password}
```

#### 应用服务配置
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

### 测试连接
```bash
# 测试本地连接
python test_mongo_auth.py

# 使用环境变量测试
MONGO_USERNAME=admin MONGO_PASSWORD=password python test_mongo_auth.py

# 测试 Docker 环境
docker-compose exec vivbliss-scraper python test_mongo_auth.py
```

### 配置优先级
环境变量按以下优先级生效：
1. `MONGO_URI`（如果设置，将覆盖所有其他配置）
2. 单独的配置变量（`MONGO_HOST`, `MONGO_PORT`, `MONGO_USERNAME`, `MONGO_PASSWORD`）
3. 默认值（`localhost:27017`，无认证）

### 连接测试工具

#### wait_for_mongo.py
等待 MongoDB 服务就绪：
```bash
# 使用默认设置（30次重试，间隔2秒）
python3 scripts/wait_for_mongo.py

# 自定义重试参数（5次重试，间隔1秒）
python3 scripts/wait_for_mongo.py 5 1
```

#### test_mongo_auth.py
完整的连接测试和验证：
```bash
python3 test_mongo_auth.py
```

---

## ⚙️ Scrapy 配置详解

### 概述
本文档说明了针对 vivbliss_scraper 项目进行的 Scrapy 配置修改，旨在降低请求频率、增加日志输出并绕过 robots.txt 限制。

### 主要配置变更

#### 1. Robot.txt 策略调整
```python
# 修改前
ROBOTSTXT_OBEY = True

# 修改后  
ROBOTSTXT_OBEY = False
```

**变更原因**: 绕过网站的 robots.txt 限制，允许爬取更多内容。

#### 2. 请求频率控制
```python
# 修改前
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS = 16

# 修改后
DOWNLOAD_DELAY = int(os.getenv('DOWNLOAD_DELAY', '3'))  # 默认 3 秒
CONCURRENT_REQUESTS = int(os.getenv('CONCURRENT_REQUESTS', '4'))  # 默认 4
```

**变更说明**:
- **下载延迟**: 从 1 秒增加到 3 秒，降低请求频率
- **并发请求**: 从 16 降低到 4，减少服务器压力
- 支持环境变量配置，便于不同环境调整

#### 3. 自动限速功能
```python
# 新增配置
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = os.getenv('AUTOTHROTTLE_DEBUG', 'False').lower() == 'true'
```

**功能说明**:
- 自动调整请求延迟以维持目标并发数
- 根据响应时间动态调整延迟
- 避免因请求过快导致的封禁

#### 4. 重试机制优化
```python
# 新增配置
RETRY_TIMES = int(os.getenv('RETRY_TIMES', '3'))
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]
```

**改进内容**:
- 增加重试次数配置
- 针对特定 HTTP 状态码进行重试
- 包含 429 (Too Many Requests) 状态码的重试处理

#### 5. 日志和调试配置
```python
# 新增配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_ENABLED = True
RANDOMIZE_DOWNLOAD_DELAY = 0.5
```

**功能增强**:
- 支持环境变量配置日志级别
- 随机化延迟以模拟人类行为
- 详细的爬取过程日志记录

### 爬虫日志增强

#### 启动和结束日志
```
🚀 开始爬取 vivbliss 爬虫
🎯 目标域名: vivbliss.com
📋 起始URL数量: 1
⚙️  爬虫配置:
   ROBOTSTXT_OBEY: False
   DOWNLOAD_DELAY: 3 秒
   CONCURRENT_REQUESTS: 4
   AUTOTHROTTLE_ENABLED: True
```

#### 页面处理日志
```
=== 开始解析页面 ===
URL: https://vivbliss.com
状态码: 200
响应大小: 45620 bytes
Content-Type: text/html; charset=utf-8
当前下载延迟: 3 秒
```

#### 内容提取日志
```
✅ 提取文章 #1:
   标题: 示例文章标题...
   URL: https://vivbliss.com/article/1
   分类: 技术
   日期: 2024-01-15
   内容长度: 1250 字符
```

### 环境变量支持
所有关键配置都支持环境变量覆盖：

#### 基础设置
```bash
export DOWNLOAD_DELAY=5          # 下载延迟（秒）
export CONCURRENT_REQUESTS=2     # 并发请求数
export LOG_LEVEL=DEBUG           # 日志级别
```

#### 自动限速设置
```bash
export AUTOTHROTTLE_DEBUG=true       # 启用限速调试
export AUTOTHROTTLE_MAX_DELAY=15     # 最大延迟（秒）
```

#### 重试设置
```bash
export RETRY_TIMES=5             # 重试次数
```

### 中间件配置
```python
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}
```

---

## 🔧 故障排除和最佳实践

### 常见问题

#### 1. 容器启动失败
```bash
# 检查容器日志
docker-compose logs vivbliss-scraper
docker-compose logs mongodb

# 检查容器状态
docker-compose ps

# 重建容器
docker-compose down
docker-compose up --build
```

#### 2. MongoDB 连接问题
```bash
# 检查 MongoDB 健康状态
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# 重启 MongoDB 服务
docker-compose restart mongodb

# 查看 MongoDB 日志
docker-compose logs mongodb
```

#### 3. Telegram 上传问题
- 验证 `api_id` 和 `api_hash` 是否正确
- 检查文件是否存在且可读
- 确认文件大小在 50MB 以下
- 验证聊天 ID 格式正确

#### 4. 调度器问题
- 检查 cron 表达式语法
- 验证任务启用状态
- 确认爬虫名称正确

### 最佳实践

#### 1. 合规性
- 遵守目标网站的服务条款
- 尊重 robots.txt（虽然被绕过）
- 避免对网站造成过大负担
- 在合理时间段内运行

#### 2. 监控和调试
```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
export AUTOTHROTTLE_DEBUG=true

# 监控爬取性能
python3 -m scrapy crawl vivbliss -L INFO
```

#### 3. 速率调整
根据目标网站的响应情况调整配置：

```bash
# 对于敏感网站，增加延迟
export DOWNLOAD_DELAY=10
export CONCURRENT_REQUESTS=1

# 对于稳定网站，适度提高效率
export DOWNLOAD_DELAY=2
export CONCURRENT_REQUESTS=6
```

#### 4. 安全建议
- 不要在代码中硬编码密码
- 使用强密码，避免使用默认密码
- 限制 MongoDB 访问，只允许必要的 IP 地址连接
- 使用不同的密码用于开发和生产环境
- 定期更新密码并轮换凭证
- 不要将 `.env` 文件提交到版本控制

#### 5. 性能优化
- 监控资源使用情况
- 根据爬虫需求配置适当的工作线程数
- 对于 CPU 密集型爬虫使用进程池
- 在生产环境中使用持久存储
- 实施适当的日志记录和警报

### 调试模式

#### 启用调试日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用所有调度器组件的调试日志
```

#### 健康检查
```python
# 检查调度器健康状态
status = scheduler.get_scheduler_status()
if not status['running']:
    print("调度器未运行！")

# 验证任务配置
for task in scheduler.list_tasks():
    task_info = scheduler.get_task_info(task.task_id)
    if not task_info['next_run_time']:
        print(f"任务 {task.task_id} 没有下次运行时间！")
```

### 联系支持
如果遇到问题：
1. 检查故障排除部分
2. 查看测试文件以了解使用示例
3. 验证配置和权限
4. 查看项目文档和 README 文件

---

## 📝 许可证和贡献

### 许可证
本项目遵循开源许可证条款。

### 贡献指南
1. **编写测试**: 为新功能添加测试用例
2. **遵循 TDD**: 使用测试驱动开发流程
3. **代码风格**: 遵循现有代码模式
4. **文档更新**: 为新功能更新文档
5. **测试覆盖**: 维持 90%+ 的测试覆盖率

### 开发原则
- **模块化设计**: 保持文件在500行以下，拆分为逻辑组件
- **环境安全**: 永远不要硬编码机密或环境特定值
- **测试优先**: 始终在实现前编写测试（红-绿-重构）
- **清洁架构**: 分离关注点，使用依赖注入
- **文档**: 维护清晰、最新的文档

---

## 📞 支持和联系

### 问题报告
请在项目的 GitHub 仓库中提交 issue。

### 技术支持
查看相关文档：
- 项目 README 文件
- 各模块的专门文档
- 测试文件中的使用示例
- Docker 和配置文档

### 社区
欢迎加入项目讨论和贡献！

---

*📄 本文档由 SPARC documenter 模式生成，整合了项目的所有主要组件和配置指南。*

*🔄 最后更新: 2024年1月*