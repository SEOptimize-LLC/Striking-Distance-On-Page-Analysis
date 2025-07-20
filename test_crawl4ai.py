#!/usr/bin/env python3
"""
Test script to verify crawl4ai integration works correctly.
This script tests basic functionality before running the enhanced app.
"""

import asyncio
import sys
from typing import Dict, Any

def test_crawl4ai_import():
    """Test if crawl4ai can be imported successfully."""
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
        from crawl4ai.content_filter_strategy import PruningContentFilter
        from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
        print("✅ crawl4ai imports successful")
        return True
    except ImportError as e:
        print(f"❌ crawl4ai import failed: {e}")
        return False

async def test_single_url_crawl(url: str = "https://httpbin.org/html") -> Dict[str, Any]:
    """Test crawling a single URL."""
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
        from crawl4ai.content_filter_strategy import PruningContentFilter
        from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
        from bs4 import BeautifulSoup
        
        browser_config = BrowserConfig(
            headless=True,
            verbose=False
        )
        
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_for=10,
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(
                    threshold=0.48,
                    threshold_type="fixed",
                    min_word_threshold=0
                )
            )
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            
            if result.success:
                # Extract SEO elements
                soup = BeautifulSoup(result.html, 'html.parser')
                
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ""
                
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                meta_desc_text = meta_desc.get('content', '').strip() if meta_desc else ""
                
                h1_tags = soup.find_all('h1')
                h1_text = ' '.join([h.get_text().strip() for h in h1_tags]) if h1_tags else ""
                
                h2_tags = soup.find_all('h2')
                h2_text = ' '.join([h.get_text().strip() for h in h2_tags[:5]]) if h2_tags else ""
                
                body_content = result.markdown.fit_markdown if hasattr(result.markdown, 'fit_markdown') else result.markdown
                
                return {
                    'success': True,
                    'url': url,
                    'title': title_text,
                    'meta_description': meta_desc_text,
                    'h1': h1_text,
                    'h2': h2_text,
                    'content_length': len(body_content),
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'url': url,
                    'error': str(result.error) if hasattr(result, 'error') else 'Unknown error'
                }
                
    except Exception as e:
        return {
            'success': False,
            'url': url,
            'error': str(e)
        }

async def main():
    """Main test function."""
    print("🧪 Testing crawl4ai integration...")
    
    # Test imports
    if not test_crawl4ai_import():
        print("\n💡 To install crawl4ai, run:")
        print("pip install crawl4ai")
        print("crawl4ai-setup")
        return
    
    # Test crawling
    print("\n🌐 Testing URL crawling...")
    test_urls = [
        "https://httpbin.org/html",
        "https://example.com"
    ]
    
    for url in test_urls:
        print(f"\n📍 Testing: {url}")
        result = await test_single_url_crawl(url)
        
        if result['success']:
            print(f"✅ Success!")
            print(f"   Title: {result['title'][:50]}...")
            print(f"   H1: {result['h1'][:50]}...")
            print(f"   Content Length: {result['content_length']} characters")
        else:
            print(f"❌ Failed: {result['error']}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
