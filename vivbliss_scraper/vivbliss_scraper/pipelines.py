import pymongo
import time
import logging
from itemadapter import ItemAdapter


class MongoDBPipeline:
    collection_name = 'vivbliss_items'
    max_retries = 3
    
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def retry_connection(self, spider):
        """重试连接 MongoDB"""
        for attempt in range(self.max_retries):
            try:
                spider.logger.info(f"Attempting MongoDB connection (attempt {attempt + 1}/{self.max_retries})")
                self.client = pymongo.MongoClient(
                    self.mongo_uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000
                )
                # 测试连接
                self.client.admin.command('ping')
                self.db = self.client[self.mongo_db]
                spider.logger.info("MongoDB connection established successfully")
                return True
            except Exception as e:
                spider.logger.warning(f"MongoDB connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    spider.logger.error("All MongoDB connection attempts failed")
                    return False
        return False

    def open_spider(self, spider):
        if not self.retry_connection(spider):
            raise Exception("Could not connect to MongoDB after all retries")

    def close_spider(self, spider):
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        try:
            self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
            return item
        except Exception as e:
            spider.logger.error(f"Error inserting item to MongoDB: {e}")
            # 尝试重新连接
            if self.retry_connection(spider):
                self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
                return item
            else:
                raise