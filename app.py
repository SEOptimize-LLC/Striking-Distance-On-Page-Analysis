import streamlit as st
import pandas as pd
import asyncio
import re
from typing import List

# Import crawl4ai components
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    st.error("⚠️ crawl4ai is not installed. Please install it using: pip install crawl4ai")

# Page configuration
st.set_page_config(
    page_title="Striking Distance On Page Analysis",
    page_icon="🎯",
    layout="wide"
)

# Title and description
st.title("🎯 Striking Distance On Page Analysis")
st.markdown("""
This tool uses **crawl4ai** to extract clean, SEO-relevant content directly from URLs,
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

def check_keyword_presence(keyword, text):
    """Check if keyword exists in text with smart matching"""
    if pd.isna(keyword) or pd.isna(text) or keyword == "" or text == "":
        return None
    
    keyword_lower = str(keyword).lower().strip()
    text_lower = str(text).lower()
    
    if keyword_lower in text_lower:
        return True
    
    # Smart matching for variations
    punctuation_variations = [
        keyword_lower + "?",
        keyword_lower + "!",
        keyword_lower + ".",
        keyword_lower + ":"
    ]
    for variant in punctuation_variations:
        if variant in text_lower:
            return True
    
    # Check for variations with articles
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
    
    # Check for plural/singular variations
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

async def crawl_url(url, crawler, config):
    """Crawl a single URL using crawl4ai"""
    try:
        result = await crawler.arun(url=url, config=config)
        if result.success:
            return {
                'URL': url,
                'Title': result.metadata.get('title', ''),
                'Meta Description': result.metadata.get('description', ''),
                'H1': result.metadata.get('h1', ''),
                'H2': ' '.join(result.metadata.get('h2', [])),
                'Body': result.markdown[:5000] if result.markdown else '',
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
                'Body': '',
                'Success': False,
                'Error': str(result.error)
            }
    except Exception as e:
        return {
            'URL': url,
            'Title': '',
            'Meta Description': '',
            'H1': '',
            'H2': '',
            'Body': '',
            'Success': False,
            'Error': str(e)
        }

async def crawl_urls_async(urls, progress_bar=None, status_text=None):
    """Crawl multiple URLs asynchronously"""
    if not CRAWL4AI_AVAILABLE:
        return []
    
    browser_config = BrowserConfig(
        headless=headless,
        verbose=False
    )
    
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED if use_cache else CacheMode.DISABLED,
        wait_for_selector="body",
        timeout=max_wait_time * 1000,
        remove_overlay=True,
        exclude_external_links=True,
        exclude_social_media_links=True,
        exclude_external_images=True,
        word_count_threshold=10,
        exclude_tags=['nav', 'footer', 'aside', 'header', 'script', 'style', 'noscript'],
        exclude_classes=['nav', 'navigation', 'menu', 'sidebar', 'footer', 'header', 'advertisement', 'ad', 'social', 'share', 'comment', 'related-posts', 'widget', 'popup', 'modal', 'overlay'],
        exclude_ids=['nav', 'navigation', 'menu', 'sidebar', 'footer', 'header', 'advertisement', 'ad', 'social', 'share', 'comment', 'related-posts', 'widget', 'popup', 'modal', 'overlay']
    )
    
    results = []
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for i, url in enumerate(urls):
            if progress_bar:
                progress_bar.progress((i + 1) / len(urls))
            if status_text:
                status_text.text(f"Crawling {i + 1}/{len(urls)}: {url}")
            
            result = await crawl_url(url, crawler, crawler_config)
            results.append(result)
    
    return results

def create_striking_distance_report(gsc_df, crawl_results):
    """Create the final striking distance report"""
    report_data = []
    
    # Create a mapping of URL to crawl data
    crawl_map = {result['URL']: result for result in crawl_results if result['Success']}
    
    # Group GSC data by URL and get top keywords
    url_keywords = {}
    for _, row in gsc_df.iterrows():
        url = row['URL']
        if url not in url_keywords:
            url_keywords[url] = []
        url_keywords[url].append({
            'Keyword': row['Keyword'],
            'Clicks': row['Clicks'],
            'Position': row['Position']
        })
    
    # Process each URL and its keywords
    for url, keywords in url_keywords.items():
        # Get top keywords for this URL
        top_keywords = sorted(keywords, key=lambda x: x['Clicks'], reverse=True)[:top_keywords_count]
        
        # Get crawl data for this URL
        crawl_data = crawl_map.get(url, {
            'Title': '',
            'Meta Description': '',
            'H1': '',
            'H2': '',
            'Body': ''
        })
        
        # Check each keyword against the content
        for keyword_data in top_keywords:
            keyword = keyword_data['Keyword']
            clicks = keyword_data['Clicks']
            position = keyword_data['Position']
            
            in_title = check_keyword_presence(keyword, crawl_data.get('Title', ''))
            in_meta = check_keyword_presence(keyword, crawl_data.get('Meta Description', ''))
            in_h1 = check_keyword_presence(keyword, crawl_data.get('H1', ''))
            in_h2 = check_keyword_presence(keyword, crawl_data.get('H2', ''))
            in_body = check_keyword_presence(keyword, crawl_data.get('Body', ''))
            
            report_data.append({
                'URL': url,
                'Keyword': keyword,
                'Clicks': clicks,
                'Position': position,
                'In Title': in_title if in_title is not None else False,
                'In Meta Description': in_meta if in_meta is not None else False,
                'In H1': in_h1 if in_h1 is not None else False,
                'In H2': in_h2 if in_h2 is not None else False,
                'In Body': in_body if in_body is not None else False
            })
    
    report_df = pd.DataFrame
