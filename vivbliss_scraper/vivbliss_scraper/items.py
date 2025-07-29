import scrapy


class VivblissItem(scrapy.Item):
    """原始文章/内容项目"""
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    category = scrapy.Field()


class CategoryItem(scrapy.Item):
    """产品分类项目"""
    # 基础信息
    name = scrapy.Field()  # 分类名称
    url = scrapy.Field()   # 分类页面URL
    slug = scrapy.Field()  # URL slug
    
    # 层级信息
    parent_category = scrapy.Field()  # 父分类
    level = scrapy.Field()  # 分类层级 (1=顶级, 2=二级, etc.)
    path = scrapy.Field()   # 分类路径 (如: "服装/男装/衬衫")
    
    # 统计信息
    product_count = scrapy.Field()  # 该分类下的产品数量
    
    # 元数据
    description = scrapy.Field()  # 分类描述
    image_url = scrapy.Field()    # 分类图片
    created_at = scrapy.Field()   # 抓取时间
    
    # SEO信息
    meta_title = scrapy.Field()
    meta_description = scrapy.Field()


class ProductItem(scrapy.Item):
    """产品详情项目"""
    # 基础信息
    name = scrapy.Field()        # 产品名称
    url = scrapy.Field()         # 产品页面URL
    sku = scrapy.Field()         # 产品SKU
    brand = scrapy.Field()       # 品牌
    
    # 分类信息
    category = scrapy.Field()    # 所属分类
    category_path = scrapy.Field()  # 分类路径
    tags = scrapy.Field()        # 产品标签
    
    # 价格信息
    price = scrapy.Field()       # 当前价格
    original_price = scrapy.Field()  # 原价
    discount = scrapy.Field()    # 折扣信息
    currency = scrapy.Field()    # 货币单位
    
    # 库存和状态
    stock_status = scrapy.Field()  # 库存状态 (in_stock, out_of_stock, low_stock)
    stock_quantity = scrapy.Field()  # 库存数量
    availability = scrapy.Field()    # 可用性
    
    # 产品详情
    description = scrapy.Field()     # 产品描述
    short_description = scrapy.Field()  # 简短描述
    specifications = scrapy.Field()  # 产品规格 (JSON格式)
    features = scrapy.Field()       # 产品特性列表
    
    # 图片和媒体
    image_urls = scrapy.Field()     # 产品图片URL列表
    thumbnail_url = scrapy.Field()  # 缩略图URL
    video_urls = scrapy.Field()     # 产品视频URL列表
    
    # 评价和评分
    rating = scrapy.Field()         # 平均评分
    review_count = scrapy.Field()   # 评价数量
    reviews = scrapy.Field()        # 评价详情 (JSON格式)
    
    # 变体信息 (如颜色、尺寸等)
    variants = scrapy.Field()       # 产品变体 (JSON格式)
    options = scrapy.Field()        # 产品选项 (JSON格式)
    
    # 销售信息
    sales_count = scrapy.Field()    # 销售数量
    popularity_score = scrapy.Field()  # 热门度分数
    
    # 元数据
    created_at = scrapy.Field()     # 抓取时间
    updated_at = scrapy.Field()     # 更新时间
    
    # SEO信息
    meta_title = scrapy.Field()
    meta_description = scrapy.Field()
    meta_keywords = scrapy.Field()
    
    # 额外信息
    weight = scrapy.Field()         # 产品重量
    dimensions = scrapy.Field()     # 产品尺寸
    shipping_info = scrapy.Field()  # 运送信息
    warranty = scrapy.Field()       # 保修信息