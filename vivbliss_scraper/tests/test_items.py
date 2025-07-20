import pytest
from vivbliss_scraper.items import VivblissItem


class TestVivblissItem:
    def test_item_has_required_fields(self):
        item = VivblissItem()
        required_fields = ['title', 'url', 'content', 'date', 'category']
        for field in required_fields:
            assert field in item.fields
    
    def test_item_can_store_data(self):
        item = VivblissItem()
        item['title'] = 'Test Title'
        item['url'] = 'https://vivbliss.com/test'
        item['content'] = 'Test content'
        item['date'] = '2024-01-01'
        item['category'] = 'Test Category'
        
        assert item['title'] == 'Test Title'
        assert item['url'] == 'https://vivbliss.com/test'
        assert item['content'] == 'Test content'
        assert item['date'] == '2024-01-01'
        assert item['category'] == 'Test Category'