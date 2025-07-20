import streamlit as st
import pandas as pd
import numpy as np
import asyncio
import json
import re
from typing import Union, List, Dict, Any
import io
import os
from pathlib import Path

# Import crawl4ai components
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    from crawl4ai.content_filter_strategy import PruningContentFilter
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    st.error("⚠️ crawl4ai is not installed. Please install it using: pip install crawl4ai")

# Page configuration
st.set_page_config(
    page_title="Enhanced Striking Distance On Page Analysis",
    page_icon="🎯",
    layout="wide"
)

# Title and description
st.title("🎯 Enhanced Striking Distance On Page Analysis")
st.markdown("""
This enhanced tool uses **crawl4ai** to extract clean, SEO-relevant content directly from URLs, 
eliminating the need for Screaming Frog exports. It cross-references Google Search Console data 
with AI-powered content extraction to identify keyword optimization opportunities.
""")

# Sidebar for settings
st.sidebar.header("⚙️ Configuration")

# Branded terms input
branded_terms = st.sidebar.text_area(
    "Branded Terms to Exclude (one per line)",
    placeholder="yourbrand\ncompany name\nbrand variations",
    help="Enter branded terms to exclude from analysis"
).strip().split('\n') if st.sidebar.text_area else []

# URL exclusions input
excluded_urls = st.sidebar.text_area(
    "URLs to Exclude (one per line - EXACT MATCH)",
    placeholder="https://www.trysnow.com/blogs/news\n/admin\n/search",
    help="Enter exact URLs to exclude. Will NOT exclude sub-pages"
).strip().split('\n') if st.sidebar.text_area else []

# Top keywords setting
top_keywords_count = st.sidebar.number_input(
    "Top Keywords to Analyze (by Clicks)", 
    value=10, 
    min_value=1, 
    max_value=20,
    help="Number of top-performing keywords to analyze per URL"
)

# crawl4ai settings
st.sidebar.header("🤖 crawl4ai Settings")
use_cache = st.sidebar.checkbox("Use Cache", value=True, help="Cache crawled content for faster subsequent runs")
headless = st.sidebar.checkbox("Headless Mode", value=True, help="Run browser in headless mode")
max_wait_time = st.sidebar.number_input("Max Wait Time (seconds)", value=30, min_value=10, max_value=120)

# Fixed settings
min_position = 4
max_position = 20

# File uploaders
st.header("📊 Google Search Console Data")
gsc_file = st.file_uploader(
    "Upload GSC Performance Report",
    type=['csv', 'xlsx', 'xls'],
    help="Export from GSC with Query, Landing Page, Clicks, Impressions, CTR, Position"
)

# Helper functions
def load_file(file):
    """Load CSV or Excel file into pandas DataFrame"""
    try:
        file_ext = file.name.lower().split('.')[-1]
        
        if file_ext == 'csv':
            file_content = file.read()
            file.seek(0)
            
            first_line = file_content.decode('utf-8').split('\n')[0]
            if ';' in first_line and ',' not in first_line:
                df = pd.read_csv(file, delimiter=';')
            elif '\t' in first_line:
                df = pd.read_csv(file, delimiter='\t')
            else:
                df = pd.read_csv(file)
            
            df.columns = df.columns.str.strip()
            return df
            
        elif file_ext == 'xlsx':
            return pd.read_excel(file, engine='openpyxl')
        elif file_ext == 'xls':
            return pd.read_excel(file, engine='xlrd')
        else:
            if hasattr(file, 'type'):
                if 'csv' in file.type:
                    return pd.read_csv(file)
                elif 'excel' in file.type or 'spreadsheet' in file.type:
                    return pd.read_excel(file)
            raise ValueError(f"Unsupported file format: {file.name}")
    except Exception as e:
        st.error(f"Error reading file {file.name}: {str(e)}")
        raise

def clean_url(url):
    """Standardize URL format"""
    if pd.isna(url):
        return ""
    url = str(url).strip()
    url = url.rstrip('/')
    return url

def should_exclude_url(url, excluded_urls):
    """Check if URL should be excluded based on exact match or parameters"""
    if any(param in str(url) for param in ['?', '=', '#']):
        return True
    
    if excluded_urls:
        normalized_url = str(url).rstrip('/')
        
        for excluded in excluded_urls:
            excluded = excluded.strip()
            if excluded:
                excluded_normalized = excluded.rstrip('/')
                
                if normalized_url == excluded_normalized:
                    return True
                
                if not excluded_normalized.startswith('http'):
                    if (normalized_url == f"https://{excluded_normalized}" or 
                        normalized_url == f"http://{excluded_normalized}" or
                        normalized_url.endswith(f"/{excluded_normalized}")):
                        return True
    
    return False

def check_keyword_presence(keyword, text):
    """Check if keyword exists in text with smart matching"""
    if pd.isna(keyword) or pd.isna(text) or keyword == "" or text == "":
        return None
    
    keyword_lower = str(keyword).lower().strip()
    text_lower = str(text).lower()
    
    if keyword_lower in text_lower:
        return True
    
    punctuation_variations = [
        keyword_lower + "?",
        keyword_lower + "!",
        keyword_lower + ".",
        keyword_lower + ":"
    ]
    for variant in punctuation_variations:
        if variant in text_lower:
            return True
    
    words = keyword_lower.split()
    article_variations = []
    articles = ['a', 'an', 'the']
    
    for i in range(len(words) + 1):
        for article in articles:
            variant_words = words[:i] + [article] + words[i:]
            article_variations.append(' '.join(variant_words))
    
    words_no_articles = [w for w in words if w not in articles]
    if len(words_no_articles) < len(words):
        article_variations.append(' '.join(words_no_articles))
    
    for variant in article_variations:
        if variant in text_lower:
            return True
    
    if keyword_lower.endswith('s'):
        singular = keyword_lower[:-1]
        if singular in text_lower:
            return True
    elif keyword_lower.endswith('es'):
        singular = keyword_lower[:-2]
        if singular in text_lower:
            return True
    else:
        if keyword_lower + 's' in text_lower or keyword_lower + 'es' in text_lower:
            return True
    
    return False

def process_gsc_data(df, branded_terms, excluded_urls):
    """Process Google Search Console data"""
    df.columns = df.columns.str.strip()
    
    missing_cols = []
    
    query_col = None
    for col in df.columns:
        if col.lower() == 'query':
            query_col = col
            break
    if not query_col:
        missing_cols.append('Query')
    
    landing_page_col = None
    landing_page_variants = ['landing page', 'landing pages', 'address', 'url', 'urls', 'page', 'top pages']
    for col in df.columns:
        if col.lower() in landing_page_variants:
            landing_page_col = col
            break
    if not landing_page_col:
        missing_cols.append('Landing Page (or Address/URL)')
    
    clicks_col = None
    for col in df.columns:
        if col.lower() == 'clicks':
            clicks_col = col
            break
    if not clicks_col:
        missing_cols.append('Clicks')
    
    if missing_cols:
        st.error(f"Missing required columns in GSC data: {missing_cols}")
        st.info("Expected columns: Query, Landing Page (or URL/Address), Clicks")
        st.write("Available columns in your file:", list(df.columns))
        return None
    
    if query_col:
        df.rename(columns={query_col: 'Keyword'}, inplace=True)
    if landing_page_col:
        df.rename(columns={landing_page_col: 'URL'}, inplace=True)
    if clicks_col and clicks_col != 'Clicks':
        df.rename(columns={clicks_col: 'Clicks'}, inplace=True)
    
    df['URL'] = df['URL'].apply(clean_url)
    df = df[df['URL'].notna() & (df['URL'] != '')]
    df = df[df['Keyword'].notna() & (df['Keyword'] != '')]
    
    initial_count = len(df)
    df = df[~df['URL'].apply(lambda x: should_exclude_url(x, excluded_urls))]
    excluded_count = initial_count - len(df)
    if excluded_count > 0:
        st.info(f"Excluded {excluded_count} URLs (parameter URLs and exact matches from exclusion list)")
    
    df['Clicks'] = pd.to_numeric(df['Clicks'], errors='coerce').fillna(0)
    df = df[df['Clicks'] > 0]
    
    if 'Position' in df.columns:
        df['Position'] = pd.to_numeric(df['Position'], errors='coerce')
        df_with_position = df[df['Position'].notna()]
        if len(df_with_position) > 0:
            df = df_with_position[(df_with_position['Position'] >= min_position) & 
                                 (df_with_position['Position'] <= max_position)]
        else:
            df['Position'] = 10.0
    else:
        df['Position'] = 10.0
        st.info("No position data found. Analyzing all keywords regardless of ranking position.")
    
    if branded_terms:
        branded_terms_clean = [term.strip() for term in branded_terms if term.strip()]
        if branded_terms_clean:
            pattern = '|'.join([re.escape(term) for term in branded_terms_clean])
            df = df[~df['Keyword'].str.contains(pattern, case=False, na=False)]
    
    df = df.sort_values(['URL', 'Clicks'], ascending=[True, False])
    
    if len(df) == 0:
        st.warning("No keywords found with clicks > 0 after filtering")
    
    return df

async def crawl_url_with_crawl4ai(url: str, config: Dict[str, Any]) -> Dict[str, str]:
    """Crawl a single URL using crawl4ai and extract SEO-relevant content"""
    try:
        browser_config = BrowserConfig(
            headless=config.get('headless', True),
            verbose=False
        )
        
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED if config.get('use_cache', True) else CacheMode.BYPASS,
            wait_for=config.get('max_wait_time', 30),
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
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(result.html, 'html.parser')
                
                # Extract title
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ""
                
                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                meta_desc_text = meta_desc.get('content', '').strip() if meta_desc else ""
                
                # Extract H1
                h1_tags = soup.find_all('h1')
                h1_text = ' '.join([h.get_text().strip() for h in h1_tags]) if h1_tags else ""
                
                # Extract H2s
                h2_tags = soup.find_all('h2')
                h2_text = ' '.join([h.get_text().strip() for h in h2_tags[:5]]) if h2_tags else ""
                
                # Use clean markdown content for body
                body_content = result.markdown.fit_markdown if hasattr(result.markdown, 'fit_markdown') else result.markdown
                
                return {
                    'URL': url,
                    'Title': title_text,
                    'Meta Description': meta_desc_text,
                    'H1': h1_text,
                    'H2': h2_text,
                    'Copy': body_content,
                    'Success': True,
                    'Error': None
                }
            else:
                return {
                    'URL': url,
                    'Title': '',
                    'Meta Description': '',
                    'H1': '',
                    'H2': '',
                    'Copy': '',
                    'Success': False,
                    'Error': str(result.error) if hasattr(result, 'error') else 'Unknown error'
                }
                
    except Exception as e:
        return {
            'URL': url,
            'Title': '',
            'Meta Description': '',
            'H1': '',
            'H2': '',
            'Copy': '',
            'Success': False,
            'Error': str(e)
        }

async def crawl_multiple_urls(urls: List[str], config: Dict[str, Any]) -> List[Dict[str, str]]:
    """Crawl multiple URLs using crawl4ai"""
    results = []
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, url in enumerate(urls):
        status_text.text(f"Crawling URL {idx + 1} of {len(urls)}: {url}")
        result = await crawl_url_with_crawl4ai(url, config)
        results.append(result)
        progress_bar.progress((idx + 1) / len(urls))
    
    progress_bar.empty()
    status_text.empty()
    
    return results

def create_striking_distance_report(gsc_df, crawl_results):
    """Create the final striking distance report"""
    report_data = []
    
    # Convert crawl results to DataFrame for easier lookup
    crawl_df = pd.DataFrame(crawl_results)
    
    for url in gsc_df['URL'].unique():
        url_data = gsc_df[gsc_df['URL'] == url].head(top_keywords_count)
        
        # Get crawl data for this URL
        crawl_row = crawl_df[crawl_df['URL'] == url]
        if len(crawl_row) > 0:
            crawl_row = crawl_row.iloc[0]
            title = crawl_row.get('Title', '')
            meta_desc = crawl_row.get('Meta Description', '')
            h1 = crawl_row.get('H1', '')
            h2 = crawl_row.get('H2', '')
            copy = crawl_row.get('Copy', '')
        else:
            title = meta_desc = h1 = h2 = copy = ''
        
        # Create a row for each keyword
        for _, kw_row in url_data.iterrows():
            keyword = kw_row['Keyword']
            
            in_title = check_keyword_presence(keyword, title)
            in_meta = check_keyword_presence(keyword, meta_desc)
            in_h1 = check_keyword_presence(keyword, h1)
            in_h2 = check_keyword_presence(keyword, h2)
            in_body = check_keyword_presence(keyword, copy)
            
            if in_body is None:
                in_body = "No Data"
            
            report_data.append({
                'URL': url,
                'Keyword': keyword,
                'Clicks': int(kw_row['Clicks']),
                'In Title': in_title if in_title is not None else False,
                'In Meta': in_meta if in_meta is not None else False,
                'In H1': in_h1 if in_h1 is not None else False,
                'In H2': in_h2 if in_h2 is not None else False,
                'In Body': in_body
            })
    
    report_df = pd.DataFrame(report_data)
    report_df = report_df.sort_values(['URL', 'Clicks'], ascending=[True, False])
    
    return report_df

# Main processing
if gsc_file:
    try:
        # Load data
        with st.spinner("Loading GSC data..."):
            gsc_df = load_file(gsc_file)
        
        # Process data
        with st.spinner("Processing GSC data..."):
            processed_gsc = process_gsc_data(gsc_df, branded_terms, excluded_urls)
            
        if processed_gsc is not None and len(processed_gsc) > 0:
            st.success(f"✅ GSC data processed! Found {len(processed_gsc['URL'].unique())} URLs with striking distance keywords.")
            
            # Get unique URLs to crawl
            unique_urls = processed_gsc['URL'].unique()
            st.info(f"🤖 Ready to crawl {len(unique_urls)} unique URLs using crawl4ai...")
            
            if st.button("🚀 Start Crawling with crawl4ai", type="primary"):
                if not CRAWL4AI_AVAILABLE:
                    st.error("crawl4ai is not installed. Please install it first:")
                    st.code("pip install crawl4ai")
                    st.code("crawl4ai-setup")
                else:
                    # Configure crawl settings
                    crawl_config = {
                        'use_cache': use_cache,
                        'headless': headless,
                        'max_wait_time': max_wait_time
                    }
                    
                    # Run crawling
                    with st.spinner("🤖 Crawling URLs with AI-powered content extraction..."):
                        crawl_results = asyncio.run(crawl_multiple_urls(unique_urls.tolist(), crawl_config))
                    
                    # Check for failed crawls
                    failed_crawls = [r for r in crawl_results if not r['Success']]
                    if failed_crawls:
                        st.warning(f"⚠️ {len(failed_crawls)} URLs failed to crawl. Check the error log below.")
                        with st.expander("View Failed Crawls"):
                            for fail in failed_crawls:
                                st.write(f"**{fail['URL']}**: {fail['Error']}")
                    
                    # Create report
                    with st.spinner("📊 Creating striking distance report..."):
                        report = create_striking_distance_report
