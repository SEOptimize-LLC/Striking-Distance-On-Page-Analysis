#!/usr/bin/env python3
"""
Test script to verify crawl4ai functionality
"""

import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def test_crawl():
    """Test crawl4ai with a sample URL"""
    print("🧪 Testing crawl4ai functionality...")
    
    test_url = "https://example.com"
    
    try:
        browser_config = BrowserConfig(
            headless=True,
            verbose=False
        )
        
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.DISABLED,
            wait_for_selector="body",
            timeout=30000,
            remove_overlay=True,
            exclude_external_links=True,
            exclude_social_media_links=True,
            exclude_tags=['nav', 'footer', 'aside', 'header', 'script', 'style'],
            exclude_classes=['nav', 'navigation', 'menu', 'sidebar', 'footer', 'header'],
            word_count_threshold=10
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=test_url, config=crawler_config)
            
            if result.success:
                print("✅ crawl4ai is working correctly!")
                print(f"📄 Title: {result.metadata.get('title', 'N/A')}")
                print(f"📝 Content length: {len(result.markdown)} characters")
                print(f"🏷️ H1 tags: {len(result.metadata.get('h1', []))}")
                print(f"🏷️ H2 tags: {len(result.metadata.get('h2', []))}")
                return True
            else:
                print(f"❌ Crawl failed: {result.error}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing crawl4ai: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_crawl())
