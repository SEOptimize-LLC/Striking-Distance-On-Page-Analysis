#!/usr/bin/env python3
"""
Simple test for crawl4ai
"""

import asyncio
from crawl4ai import AsyncWebCrawler

async def test_simple():
    """Simple test for crawl4ai"""
    print("Testing crawl4ai...")
    
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url="https://httpbin.org/html")
            
            if result.success:
                print("✅ crawl4ai is working!")
                print(f"Title: {result.metadata.get('title', 'No title')}")
                print(f"Content length: {len(result.markdown)} chars")
                return True
            else:
                print(f"❌ Failed: {result.error}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_simple())
