"""
目录优先级调度器
实现先完成当前目录下所有商品的提取，再进入下一个目录的逻辑
"""

import logging
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime

try:
    import scrapy
    from scrapy import Request
    from scrapy.utils.request import request_fingerprint
    SCRAPY_AVAILABLE = True
except ImportError:
    SCRAPY_AVAILABLE = False
    # 定义模拟类供测试使用
    class Request:
        def __init__(self, url, **kwargs):
            self.url = url
            self.meta = kwargs.get('meta', {})
    
    def request_fingerprint(request):
        """模拟请求指纹生成"""
        return f"fp_{hash(request.url)}"


class DirectoryTracker:
    """目录进度跟踪器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 目录状态跟踪
        self.directories: Dict[str, Dict] = {}  # 目录路径 -> 目录信息
        self.directory_products: Dict[str, Set[str]] = defaultdict(set)  # 目录 -> 产品URL集合
        self.completed_directories: Set[str] = set()  # 已完成的目录
        self.active_directories: Set[str] = set()  # 当前活跃的目录
        
        # 产品状态跟踪
        self.discovered_products: Dict[str, str] = {}  # 产品URL -> 所属目录
        self.completed_products: Set[str] = set()  # 已完成的产品
        self.failed_products: Set[str] = set()  # 失败的产品
        
        # 统计信息
        self.stats = {
            'directories_discovered': 0,
            'directories_completed': 0,
            'products_discovered': 0,
            'products_completed': 0,
            'products_failed': 0
        }
    
    def add_directory(self, directory_path: str, directory_info: Dict) -> None:
        """添加新发现的目录"""
        if directory_path not in self.directories:
            self.directories[directory_path] = {
                'path': directory_path,
                'info': directory_info,
                'discovered_at': datetime.now(),
                'level': directory_info.get('level', 1),
                'parent': directory_info.get('parent_category'),
                'products_discovered': 0,
                'products_completed': 0,
                'status': 'discovered'  # discovered, active, completed
            }
            self.stats['directories_discovered'] += 1
            self.logger.info(f"📁 发现新目录: {directory_path} (级别: {directory_info.get('level', 1)})")
    
    def add_product_to_directory(self, directory_path: str, product_url: str) -> None:
        """将产品添加到目录中"""
        if directory_path not in self.directories:
            # 如果目录不存在，创建一个默认目录
            self.add_directory(directory_path, {'level': 1})
        
        self.directory_products[directory_path].add(product_url)
        self.discovered_products[product_url] = directory_path
        self.directories[directory_path]['products_discovered'] += 1
        self.stats['products_discovered'] += 1
        
        self.logger.debug(f"🛍️  添加产品到目录 {directory_path}: {product_url}")
    
    def mark_product_completed(self, product_url: str) -> bool:
        """标记产品为已完成"""
        if product_url in self.discovered_products:
            self.completed_products.add(product_url)
            directory_path = self.discovered_products[product_url]
            self.directories[directory_path]['products_completed'] += 1
            self.stats['products_completed'] += 1
            
            self.logger.debug(f"✅ 产品提取完成: {product_url}")
            
            # 检查目录是否完成
            self._check_directory_completion(directory_path)
            return True
        return False
    
    def mark_product_failed(self, product_url: str) -> bool:
        """标记产品提取失败"""
        if product_url in self.discovered_products:
            self.failed_products.add(product_url)
            directory_path = self.discovered_products[product_url]
            self.stats['products_failed'] += 1
            
            self.logger.warning(f"❌ 产品提取失败: {product_url}")
            
            # 检查目录是否完成（包括失败的产品）
            self._check_directory_completion(directory_path)
            return True
        return False
    
    def _check_directory_completion(self, directory_path: str) -> None:
        """检查目录是否已完成"""
        if directory_path in self.completed_directories:
            return
        
        directory_info = self.directories[directory_path]
        total_products = len(self.directory_products[directory_path])
        completed_count = directory_info['products_completed']
        failed_count = len([url for url in self.failed_products 
                           if self.discovered_products.get(url) == directory_path])
        
        if completed_count + failed_count >= total_products and total_products > 0:
            self.completed_directories.add(directory_path)
            self.active_directories.discard(directory_path)
            directory_info['status'] = 'completed'
            directory_info['completed_at'] = datetime.now()
            self.stats['directories_completed'] += 1
            
            self.logger.info(f"🎯 目录完成: {directory_path} "
                           f"(成功: {completed_count}, 失败: {failed_count}, 总计: {total_products})")
    
    def get_next_priority_directory(self) -> Optional[str]:
        """获取下一个优先处理的目录"""
        # 优先选择已激活但未完成的目录
        for directory_path in self.active_directories:
            if not self.is_directory_completed(directory_path):
                return directory_path
        
        # 如果没有激活的目录，选择最高优先级的未完成目录
        available_directories = [
            (path, info) for path, info in self.directories.items()
            if path not in self.completed_directories
        ]
        
        if not available_directories:
            return None
        
        # 按级别排序（级别越低优先级越高）
        available_directories.sort(key=lambda x: x[1]['level'])
        selected_directory = available_directories[0][0]
        
        self.active_directories.add(selected_directory)
        self.directories[selected_directory]['status'] = 'active'
        
        return selected_directory
    
    def is_directory_completed(self, directory_path: str) -> bool:
        """检查目录是否已完成"""
        return directory_path in self.completed_directories
    
    def get_directory_progress(self, directory_path: str) -> Dict:
        """获取目录进度信息"""
        if directory_path not in self.directories:
            return {}
        
        directory_info = self.directories[directory_path]
        total_products = len(self.directory_products[directory_path])
        completed_count = directory_info['products_completed']
        failed_count = len([url for url in self.failed_products 
                           if self.discovered_products.get(url) == directory_path])
        
        return {
            'path': directory_path,
            'total_products': total_products,
            'completed_products': completed_count,
            'failed_products': failed_count,
            'remaining_products': total_products - completed_count - failed_count,
            'completion_rate': (completed_count + failed_count) / max(total_products, 1),
            'status': directory_info['status'],
            'level': directory_info['level']
        }
    
    def get_stats(self) -> Dict:
        """获取整体统计信息"""
        return {
            **self.stats,
            'active_directories': len(self.active_directories),
            'completed_directories': len(self.completed_directories),
            'remaining_directories': len(self.directories) - len(self.completed_directories)
        }


class PriorityRequestQueue:
    """优先级请求队列"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 分类别的请求队列
        self.category_requests: deque = deque()  # 分类发现请求
        self.product_requests: Dict[str, deque] = defaultdict(deque)  # 按目录分组的产品请求
        self.other_requests: deque = deque()  # 其他请求
        
        # 请求指纹去重
        self.seen_requests: Set[str] = set()
    
    def add_category_request(self, request: Request) -> bool:
        """添加分类请求"""
        fingerprint = request_fingerprint(request)
        if fingerprint in self.seen_requests:
            return False
        
        self.seen_requests.add(fingerprint)
        self.category_requests.append(request)
        self.logger.debug(f"📁 添加分类请求: {request.url}")
        return True
    
    def add_product_request(self, request: Request, directory_path: str) -> bool:
        """添加产品请求到指定目录队列"""
        fingerprint = request_fingerprint(request)
        if fingerprint in self.seen_requests:
            return False
        
        self.seen_requests.add(fingerprint)
        self.product_requests[directory_path].append(request)
        self.logger.debug(f"🛍️  添加产品请求到目录 {directory_path}: {request.url}")
        return True
    
    def add_other_request(self, request: Request) -> bool:
        """添加其他类型请求"""
        fingerprint = request_fingerprint(request)
        if fingerprint in self.seen_requests:
            return False
        
        self.seen_requests.add(fingerprint)
        self.other_requests.append(request)
        self.logger.debug(f"📄 添加其他请求: {request.url}")
        return True
    
    def get_next_request(self, priority_directory: Optional[str] = None) -> Optional[Request]:
        """获取下一个请求"""
        # 1. 优先处理指定目录的产品请求
        if priority_directory and priority_directory in self.product_requests:
            directory_queue = self.product_requests[priority_directory]
            if directory_queue:
                return directory_queue.popleft()
        
        # 2. 处理分类发现请求
        if self.category_requests:
            return self.category_requests.popleft()
        
        # 3. 处理其他目录的产品请求（如果优先目录为空）
        for directory_path, queue in self.product_requests.items():
            if queue and directory_path != priority_directory:
                return queue.popleft()
        
        # 4. 处理其他请求
        if self.other_requests:
            return self.other_requests.popleft()
        
        return None
    
    def get_queue_stats(self) -> Dict:
        """获取队列统计信息"""
        product_queues_stats = {
            directory: len(queue) 
            for directory, queue in self.product_requests.items()
        }
        
        return {
            'category_requests': len(self.category_requests),
            'product_requests_by_directory': product_queues_stats,
            'total_product_requests': sum(len(queue) for queue in self.product_requests.values()),
            'other_requests': len(self.other_requests),
            'total_requests': (
                len(self.category_requests) + 
                sum(len(queue) for queue in self.product_requests.values()) + 
                len(self.other_requests)
            )
        }


class DirectoryPriorityScheduler:
    """目录优先级调度器主类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.directory_tracker = DirectoryTracker()
        self.request_queue = PriorityRequestQueue()
        
        # 调度器状态
        self.current_priority_directory: Optional[str] = None
        self.scheduler_enabled = True
        
    def discover_category(self, category_path: str, category_info: Dict) -> None:
        """发现新分类"""
        self.directory_tracker.add_directory(category_path, category_info)
    
    def discover_product(self, product_url: str, directory_path: str) -> None:
        """发现新产品"""
        self.directory_tracker.add_product_to_directory(directory_path, product_url)
    
    def add_category_request(self, request: Request) -> bool:
        """添加分类请求"""
        return self.request_queue.add_category_request(request)
    
    def add_product_request(self, request: Request, directory_path: str) -> bool:
        """添加产品请求"""
        self.discover_product(request.url, directory_path)
        return self.request_queue.add_product_request(request, directory_path)
    
    def get_next_request(self) -> Optional[Request]:
        """获取下一个应该处理的请求"""
        if not self.scheduler_enabled:
            return self.request_queue.get_next_request()
        
        # 更新当前优先目录
        self._update_priority_directory()
        
        # 获取请求
        request = self.request_queue.get_next_request(self.current_priority_directory)
        
        if request:
            self.logger.debug(f"🎯 调度请求: {request.url} "
                            f"(优先目录: {self.current_priority_directory or '无'})")
        
        return request
    
    def _update_priority_directory(self) -> None:
        """更新当前优先处理的目录"""
        # 如果当前目录已完成，选择下一个目录
        if (self.current_priority_directory and 
            self.directory_tracker.is_directory_completed(self.current_priority_directory)):
            self.current_priority_directory = None
        
        # 选择新的优先目录
        if not self.current_priority_directory:
            self.current_priority_directory = self.directory_tracker.get_next_priority_directory()
            
            if self.current_priority_directory:
                self.logger.info(f"🎯 切换到优先目录: {self.current_priority_directory}")
    
    def mark_product_completed(self, product_url: str) -> None:
        """标记产品处理完成"""
        self.directory_tracker.mark_product_completed(product_url)
    
    def mark_product_failed(self, product_url: str) -> None:
        """标记产品处理失败"""
        self.directory_tracker.mark_product_failed(product_url)
    
    def get_scheduler_stats(self) -> Dict:
        """获取调度器统计信息"""
        directory_stats = self.directory_tracker.get_stats()
        queue_stats = self.request_queue.get_queue_stats()
        
        return {
            'scheduler_enabled': self.scheduler_enabled,
            'current_priority_directory': self.current_priority_directory,
            'directory_stats': directory_stats,
            'queue_stats': queue_stats,
            'active_directories': list(self.directory_tracker.active_directories),
            'completed_directories': list(self.directory_tracker.completed_directories)
        }
    
    def get_directory_progress_report(self) -> List[Dict]:
        """获取所有目录的进度报告"""
        report = []
        for directory_path in self.directory_tracker.directories:
            progress = self.directory_tracker.get_directory_progress(directory_path)
            report.append(progress)
        
        # 按级别和完成度排序
        report.sort(key=lambda x: (x['level'], -x['completion_rate']))
        return report
    
    def enable_scheduler(self) -> None:
        """启用优先级调度"""
        self.scheduler_enabled = True
        self.logger.info("🔄 优先级调度器已启用")
    
    def disable_scheduler(self) -> None:
        """禁用优先级调度"""
        self.scheduler_enabled = False
        self.logger.info("⏸️  优先级调度器已禁用")