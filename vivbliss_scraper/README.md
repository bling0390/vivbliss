# Vivbliss.com Web Scraper

This is a Scrapy-based web scraper for vivbliss.com that extracts articles and stores them in MongoDB.

## Features

- Test-Driven Development (TDD) approach
- Robust article extraction with multiple fallback selectors
- Automatic pagination following
- MongoDB persistence
- Rate limiting and polite crawling
- Comprehensive test coverage

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd vivbliss_scraper
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=vivbliss_db
```

### Spider Settings

The spider includes the following safety features:
- Download delay: 1 second between requests
- Concurrent requests: Limited to 2
- Auto-throttle enabled
- Respects robots.txt

## Usage

### Running with Docker (推荐)

#### 快速开始

```bash
# 克隆项目
git clone <repository-url>
cd vivbliss_scraper

# 使用 Docker Compose 运行
docker-compose up -d
```

#### Docker 命令

```bash
# 构建和启动所有服务
docker-compose up --build

# 仅启动 MongoDB
docker-compose up mongodb

# 运行一次性爬取
docker-compose run --rm vivbliss-scraper

# 查看日志
docker-compose logs -f vivbliss-scraper

# 停止所有服务
docker-compose down

# 停止并清理数据卷
docker-compose down -v
```

#### 环境配置

复制并编辑 Docker 环境文件：
```bash
cp .env.docker .env.docker.local
# 编辑 .env.docker.local 根据需要调整配置
```

### 本地运行

```bash
# Run the spider
scrapy crawl vivbliss

# Run with specific settings
scrapy crawl vivbliss -s MONGO_DATABASE=my_custom_db

# Save to JSON file (for testing)
scrapy crawl vivbliss -o output.json
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_spider.py -v

# Run with coverage
pytest tests/ --cov=vivbliss_scraper --cov-report=html
```

## Project Structure

```
vivbliss_scraper/
├── vivbliss_scraper/
│   ├── __init__.py
│   ├── items.py          # Data models
│   ├── pipelines.py      # MongoDB pipeline (with retry logic)
│   ├── settings.py       # Scrapy settings
│   └── spiders/
│       ├── __init__.py
│       └── vivbliss.py   # Main spider
├── scripts/
│   ├── entrypoint.sh     # Docker container entry point
│   ├── health_check.py   # Container health checks
│   ├── wait_for_mongo.py # MongoDB readiness check
│   └── run_spider.sh     # Spider execution script
├── tests/
│   ├── test_items.py     # Item tests
│   ├── test_pipelines.py # Pipeline tests
│   ├── test_settings.py  # Settings tests
│   ├── test_spider.py    # Spider tests
│   ├── test_integration.py # Integration tests
│   ├── test_docker.py    # Docker configuration tests
│   └── test_docker_connectivity.py # Docker connectivity tests
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Docker image definition
├── .env.docker         # Docker environment variables
├── .env.example        # Environment template
├── scrapy.cfg
├── requirements.txt
├── setup.py
└── README.md
```

## Data Model

The spider extracts the following fields:

- `title`: Article title
- `url`: Full URL to the article
- `content`: Article excerpt or content
- `date`: Publication date
- `category`: Article category (defaults to "Uncategorized")

## MongoDB Storage

Data is stored in MongoDB with the following structure:

```json
{
  "_id": "ObjectId",
  "title": "Article Title",
  "url": "https://vivbliss.com/article-url",
  "content": "Article content...",
  "date": "2024-01-01",
  "category": "Technology"
}
```

## Development

This project follows TDD principles:

1. **Red**: Write failing tests first
2. **Green**: Implement minimal code to pass tests
3. **Refactor**: Improve code while keeping tests green

### Adding New Features

1. Write tests for the new feature
2. Run tests to see them fail
3. Implement the feature
4. Run tests to ensure they pass
5. Refactor if needed

## Troubleshooting

### Docker Issues

#### 容器启动失败
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

#### MongoDB 连接问题
```bash
# 检查 MongoDB 健康状态
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# 重启 MongoDB 服务
docker-compose restart mongodb

# 查看 MongoDB 日志
docker-compose logs mongodb
```

#### 权限问题
```bash
# 确保脚本有执行权限
chmod +x scripts/*.sh scripts/*.py

# 检查 Docker 用户权限
docker-compose exec vivbliss-scraper whoami
```

### 本地开发问题

#### MongoDB Connection Issues

If you encounter connection errors:
1. Ensure MongoDB is running: `sudo systemctl status mongod`
2. Check the connection string in `.env`
3. Verify network connectivity

#### No Articles Found

The spider uses multiple selectors to find articles. If no articles are found:
1. Check the website structure
2. Update selectors in `vivbliss.py`
3. Add new selectors to the `article_selectors` list

## License

[Your License Here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Implement your changes
5. Ensure all tests pass
6. Submit a pull request