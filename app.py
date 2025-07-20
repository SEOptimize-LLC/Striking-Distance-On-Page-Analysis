import streamlit as st
import pandas as pd
import re
import asyncio

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
eliminating the need for Screaming Frog exports.
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
    help="Enter exact URLs to exclude"
).strip().split('\n') if st.sidebar.text_area else []

# Top keywords setting
top_keywords_count = st.sidebar.number_input(
    "Top Keywords to Analyze (by Clicks)", 
    value=10, 
    min_value=1, 
    max_value=20
)

# Fixed settings
min_position = 4
max_position = 20

# File uploaders
st.header("📊 Google Search Console Data")
gsc_file = st.file_uploader(
    "Upload GSC Performance Report",
    type=['csv', 'xlsx', 'xls'],
    help="Export from GSC with Query, Landing Page, Clicks, Position"
)

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
    """Check if keyword exists in text"""
    if pd.isna(keyword) or pd.isna(text) or keyword == "" or text == "":
        return None
    
    keyword_lower = str(keyword).lower().strip()
    text_lower = str(text).lower()
    
    return keyword_lower in text_lower

def should_exclude_url(url, excluded_urls):
    """Check if URL should be excluded"""
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
    return False

def process_gsc_data(df, branded_terms, excluded_urls):
    """Process Google Search Console data"""
    df.columns = df.columns.str.strip()
    
    # Find required columns
    query_col = next((col for col in df.columns if col.lower() == 'query'), None)
    landing_col = next((col for col in df.columns 
                       if col.lower() in ['landing page', 'address', 'url']), None)
    clicks_col = next((col for col in df.columns if col.lower() == 'clicks'), None)
    
    if not all([query_col, landing_col, clicks_col]):
        missing = []
        if not query_col: missing.append('Query')
        if not landing_col: missing.append('Landing Page/URL')
        if not clicks_col: missing.append('Clicks')
        st.error(f"Missing required columns: {missing}")
        return None
    
    # Rename columns
    df = df.rename(columns={
        query_col: 'Keyword',
        landing_col: 'URL',
        clicks_col: 'Clicks'
    })
    
    # Clean data
    df['URL'] = df['URL'].apply(clean_url)
    df = df[df['URL'].notna() & (df['URL'] != '')]
    df = df[df['Keyword'].notna() & (df['Keyword'] != '')]
    
    # Exclude URLs
    initial_count = len(df)
    df = df[~df['URL'].apply(lambda x: should_exclude_url(x, excluded_urls))]
    excluded_count = initial_count - len(df)
    if excluded_count > 0:
        st.info(f"Excluded {excluded_count} URLs")
    
    # Convert data types
    df['Clicks'] = pd.to_numeric(df['Clicks'], errors='coerce').fillna(0)
    df = df[df['Clicks'] > 0]
    
    # Filter by position
    if 'Position' in df.columns:
        df['Position'] = pd.to_numeric(df['Position'], errors='coerce')
        df = df[(df['Position'] >= min_position) & (df['Position'] <= max_position)]
    else:
        df['Position'] = 10.0
    
    # Exclude branded terms
    if branded_terms:
        branded_terms_clean = [term.strip() for term in branded_terms if term.strip()]
        if branded_terms_clean:
            pattern = '|'.join([re.escape(term) for term in branded_terms_clean])
            df = df[~df['Keyword'].str.contains(pattern, case=False, na=False)]
    
    df = df.sort_values(['URL', 'Clicks'], ascending=[True, False])
    
    if len(df) == 0:
        st.warning("No keywords found after filtering")
    
    return df

async def crawl_url_simple(url, crawler):
    """Simple crawl function using crawl4ai"""
    try:
        result = await crawler.arun(url=url)
        if result.success:
            return {
                'URL': url,
                'Title': result.metadata.get('title', ''),
                'Meta Description': result.metadata.get('description', ''),
                'H1': result.metadata.get('h1', ''),
                'H2': ' '.join(result.metadata.get('h2', [])),
                'Body': result.markdown[:3000] if result.markdown else '',
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
        headless=True,
        verbose=False
    )
    
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED
    )
    
    results = []
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for i, url in enumerate(urls):
            if progress_bar:
                progress_bar.progress((i + 1) / len(urls))
            if status_text:
                status_text.text(f"Crawling {i + 1}/{len(urls)}: {url}")
            
            result = await crawl_url_simple(url, crawler)
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
    
    report_df = pd.DataFrame(report_data)
    report_df = report_df.sort_values(['URL', 'Clicks'], ascending=[True, False])
    return report_df

# Main processing
if gsc_file:
    st.success("✅ GSC file uploaded successfully!")
    if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
        st.session_state['start_analysis'] = True
else:
    st.info("👆 Please upload your Google Search Console CSV file to begin analysis.")

# Analysis execution
if 'start_analysis' in st.session_state and st.session_state['start_analysis']:
    try:
        # Load data
        with st.spinner("Loading GSC data..."):
            gsc_df = load_file(gsc_file)
        
        # Process data
        with st.spinner("Processing GSC data..."):
            processed_gsc = process_gsc_data(gsc_df, branded_terms, excluded_urls)
            
        if processed_gsc is not None and len(processed_gsc) > 0:
            # Get unique URLs to crawl
            unique_urls = processed_gsc['URL'].unique()
            st.info(f"Found {len(unique_urls)} unique URLs to crawl")
            
            # Crawl URLs
            with st.spinner("Crawling URLs with AI..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Run async crawling
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                crawl_results = loop.run_until_complete(
                    crawl_urls_async(unique_urls, progress_bar, status_text)
                )
                
                # Filter successful crawls
                successful_crawls = [r for r in crawl_results if r['Success']]
                failed_crawls = [r for r in crawl_results if not r['Success']]
                
                if failed_crawls:
                    st.warning(f"Failed to crawl {len(failed_crawls)} URLs")
                    with st.expander("View failed URLs"):
                        for fail in failed_crawls:
                            st.write(f"- {fail['URL']}: {fail['Error']}")
                
                if len(successful_crawls) > 0:
                    # Create final report
                    with st.spinner("Creating striking distance report..."):
                        report = create_striking_distance_report(processed_gsc, successful_crawls)
                    
                    # Display results
                    st.success(f"✅ Analysis complete! Found {len(report['URL'].unique())} URLs with striking distance keywords.")
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total URLs Analyzed", len(report['URL'].unique()))
                    with col2:
                        st.metric("Total Keywords Analyzed", len(report))
                    with col3:
                        potential_clicks = 0
                        for _, row in report.iterrows():
                            missing_count = 0
                            if not row['In Title']:
                                missing_count += 1
                            if not row['In Meta Description']:
                                missing_count += 1
                            if not row['In H1']:
                                missing_count += 1
                            if not row['In H2']:
                                missing_count += 1
                            if not row['In Body']:
                                missing_count += 1
                            
                            weight = min(0.5, missing_count * 0.1)
                            potential_clicks += row['Clicks'] * weight
                        
                        st.metric("Weighted Click Potential", int(potential_clicks))
                    
                    # Full report
                    st.header("📊 Full Report")
                    
                    # Create download button
                    csv = report.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Full Report (CSV)",
                        data=csv,
                        file_name="striking_distance_report.csv",
                        mime="text/csv"
                    )
                    
                    # Display sample of report
                    st.subheader("Report Preview (First 20 rows)")
                    st.dataframe(report.head(20))
                    
                    # Reset analysis state
                    st.session_state['start_analysis'] = False
                else:
                    st.error("No URLs were successfully crawled. Please check the failed URLs and try again.")
                    
        else:
            st.warning("No keywords found in the specified position range after filtering.")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please check that your file has the correct format and columns.")
        st.write("Supported formats: CSV, XLSX, XLS")

else:
    # Instructions
    st.info("👆 Please upload your Google Search Console CSV file to begin analysis.")
    
    with st.expander("📋 Required File Formats"):
        st.markdown("""
        ### Google Search Console Export
        Required columns:
        - **Query** - The search term/keyword
        - **Landing Page** (or Address/URL) - The URL that appeared in search
        - **Clicks** - Number of clicks received
        
        Optional but recommended:
        - **Position** - Average ranking position
        - **Impressions** - Number of times shown in search
        - **CTR** - Click-through rate
        
        ### How This Tool Works
        1. Upload your GSC performance report
        2. The tool identifies keywords in striking distance (positions 4-20)
        3. AI-powered crawling extracts clean content from each URL
        4. Keywords are checked against Title, Meta Description, H1, H2, and Body content
        5. Get actionable insights for on-page optimization
        
        **Key Features:**
        - ✅ No need for Screaming Frog exports
        - ✅ AI-powered content extraction (removes nav, footer, ads, etc.)
        - ✅ Smart keyword matching with variations
        - ✅ Branded term filtering
        - ✅ URL exclusion capabilities
        - ✅ Real-time crawling with progress tracking
        """)
    
    with st.expander("🎯 What are Striking Distance Keywords?"):
        st.markdown("""
        Striking Distance keywords are search queries where your website ranks between positions 4-20. 
        These represent opportunities where small optimizations can lead to significant traffic gains.
        
        This tool helps you:
        - Identify keywords just outside the top 3 positions
        - Check if these keywords appear in key on-page elements
        - Prioritize optimization efforts based on click potential
        - Exclude branded terms from analysis
        - Exclude URLs with no SEO value
        
        **Automatic Exclusions:**
        - URLs containing parameters (?, =, #)
        - URLs you specify in the exclusion list (EXACT MATCH ONLY)
        """)
