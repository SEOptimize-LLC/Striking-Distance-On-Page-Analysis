import streamlit as st
import pandas as pd
import numpy as np
from typing import Union, List
import io
import re

# Page configuration
st.set_page_config(
    page_title="Striking Distance On Page Analysis",
    page_icon="🎯",
    layout="wide"
)

# Title and description
st.title("🎯 Striking Distance On Page Analysis")
st.markdown("""
This tool cross-references Google Search Console performance data with Screaming Frog crawl data 
to identify keyword optimization opportunities in "striking distance" (positions 4-20).
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
    help="Enter exact URLs to exclude. Will NOT exclude sub-pages (e.g., /blogs/news won't exclude /blogs/news/article-title)"
).strip().split('\n') if st.sidebar.text_area else []

# Top keywords setting
top_keywords_count = st.sidebar.number_input(
    "Top Keywords to Analyze (by Clicks)", 
    value=10, 
    min_value=1, 
    max_value=20,
    help="Number of top-performing keywords to analyze per URL, sorted by clicks"
)

# Fixed settings (not shown to user)
min_position = 4
max_position = 20
min_volume = 0  # No minimum volume filter, rely on clicks instead

# File uploaders
col1, col2 = st.columns(2)

with col1:
    st.header("📊 Google Search Console Data")
    gsc_file = st.file_uploader(
        "Upload GSC Performance Report",
        type=['csv', 'xlsx', 'xls'],
        help="Export from GSC with Query, Landing Page, Clicks, Impressions, CTR, Position"
    )

with col2:
    st.header("🕷️ Screaming Frog Data")
    sf_file = st.file_uploader(
        "Upload Screaming Frog Internal HTML Export",
        type=['csv', 'xlsx', 'xls'],
        help="Export with Address, Title 1, H1-1, Meta Description 1, H2-1 to H2-5, Copy 1, Indexability"
    )

# Helper functions
def load_file(file):
    """Load CSV or Excel file into pandas DataFrame"""
    try:
        # Get file extension from name
        file_ext = file.name.lower().split('.')[-1]
        
        if file_ext == 'csv':
            # Try to detect delimiter
            # Read first line to check delimiter
            file_content = file.read()
            file.seek(0)  # Reset file pointer
            
            # Check first line for delimiter
            first_line = file_content.decode('utf-8').split('\n')[0]
            if ';' in first_line and ',' not in first_line:
                # Semicolon-delimited
                df = pd.read_csv(file, delimiter=';')
            elif '\t' in first_line:
                # Tab-delimited
                df = pd.read_csv(file, delimiter='\t')
            else:
                # Default comma-delimited
                df = pd.read_csv(file)
            
            # Clean column names (remove extra spaces)
            df.columns = df.columns.str.strip()
            return df
            
        elif file_ext == 'xlsx':
            return pd.read_excel(file, engine='openpyxl')
        elif file_ext == 'xls':
            return pd.read_excel(file, engine='xlrd')
        else:
            # Try to determine by content type
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
    # Don't remove protocol if it exists
    # Just remove trailing slash
    url = url.rstrip('/')
    return url

def check_keyword_presence(keyword, text):
    """Check if keyword exists in text with smart matching"""
    if pd.isna(keyword) or pd.isna(text) or keyword == "" or text == "":
        return None  # Return None for missing data
    
    # Convert to lowercase for comparison
    keyword_lower = str(keyword).lower().strip()
    text_lower = str(text).lower()
    
    # Direct match first
    if keyword_lower in text_lower:
        return True
    
    # Smart matching for variations
    
    # 1. Check with common punctuation at the end (?, !, ., :)
    punctuation_variations = [
        keyword_lower + "?",
        keyword_lower + "!",
        keyword_lower + ".",
        keyword_lower + ":"
    ]
    for variant in punctuation_variations:
        if variant in text_lower:
            return True
    
    # 2. Check for variations with articles (a, an, the)
    # Split the keyword into words
    words = keyword_lower.split()
    
    # Create variations by adding articles at different positions
    article_variations = []
    articles = ['a', 'an', 'the']
    
    for i in range(len(words) + 1):
        for article in articles:
            # Insert article at position i
            variant_words = words[:i] + [article] + words[i:]
            article_variations.append(' '.join(variant_words))
    
    # Also check if keyword exists without articles in the text
    # Remove common articles from the keyword
    words_no_articles = [w for w in words if w not in articles]
    if len(words_no_articles) < len(words):  # If we removed any articles
        article_variations.append(' '.join(words_no_articles))
    
    # Check all article variations
    for variant in article_variations:
        if variant in text_lower:
            return True
    
    # 3. Check for plural/singular variations (simple s/es endings)
    if keyword_lower.endswith('s'):
        # Try without the 's'
        singular = keyword_lower[:-1]
        if singular in text_lower:
            return True
    elif keyword_lower.endswith('es'):
        # Try without the 'es'
        singular = keyword_lower[:-2]
        if singular in text_lower:
            return True
    else:
        # Try adding 's' or 'es'
        if keyword_lower + 's' in text_lower or keyword_lower + 'es' in text_lower:
            return True
    
    return False

def should_exclude_url(url, excluded_urls):
    """Check if URL should be excluded based on exact match or parameters"""
    # Check for URL parameters
    if any(param in str(url) for param in ['?', '=', '#']):
        return True
    
    # Check against excluded URLs list - EXACT MATCH ONLY
    if excluded_urls:
        # Normalize the URL for comparison (remove trailing slashes)
        normalized_url = str(url).rstrip('/')
        
        for excluded in excluded_urls:
            excluded = excluded.strip()
            if excluded:
                # Normalize the excluded URL too
                excluded_normalized = excluded.rstrip('/')
                
                # Check for exact match (not substring)
                if normalized_url == excluded_normalized:
                    return True
                
                # Also check if the full URL matches when protocol is missing
                if not excluded_normalized.startswith('http'):
                    # Try matching with common protocols
                    if (normalized_url == f"https://{excluded_normalized}" or 
                        normalized_url == f"http://{excluded_normalized}" or
                        normalized_url.endswith(f"/{excluded_normalized}")):
                        return True
    
    return False

def process_gsc_data(df, branded_terms, excluded_urls):
    """Process Google Search Console data"""
    # Clean column names (remove extra spaces, normalize)
    df.columns = df.columns.str.strip()
    
    # First check if required columns exist BEFORE renaming
    missing_cols = []
    
    # Check for Query column (case-insensitive)
    query_col = None
    for col in df.columns:
        if col.lower() == 'query':
            query_col = col
            break
    if not query_col:
        missing_cols.append('Query')
    
    # Check for Landing Page (or variants) - case-insensitive
    landing_page_col = None
    landing_page_variants = ['landing page', 'landing pages', 'address', 'url', 'urls', 'page', 'top pages']
    for col in df.columns:
        if col.lower() in landing_page_variants:
            landing_page_col = col
            break
    if not landing_page_col:
        missing_cols.append('Landing Page (or Address/URL)')
    
    # Check for Clicks - case-insensitive
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
    
    # Now rename columns to standardized names
    if query_col:
        df.rename(columns={query_col: 'Keyword'}, inplace=True)
    if landing_page_col:
        df.rename(columns={landing_page_col: 'URL'}, inplace=True)
    if clicks_col and clicks_col != 'Clicks':
        df.rename(columns={clicks_col: 'Clicks'}, inplace=True)
    
    # Now rename columns to standardized names
    # Rename Query to Keyword
    if 'Query' in df.columns:
        df.rename(columns={'Query': 'Keyword'}, inplace=True)
    
    # Rename Landing Page variants to URL
    for col in landing_page_variants:
        if col in df.columns:
            df.rename(columns={col: 'URL'}, inplace=True)
            break
    
    # Clean data
    df['URL'] = df['URL'].apply(clean_url)
    df = df[df['URL'].notna() & (df['URL'] != '')]
    df = df[df['Keyword'].notna() & (df['Keyword'] != '')]
    
    # Exclude URLs with parameters or in exclusion list
    initial_count = len(df)
    df = df[~df['URL'].apply(lambda x: should_exclude_url(x, excluded_urls))]
    excluded_count = initial_count - len(df)
    if excluded_count > 0:
        st.info(f"Excluded {excluded_count} URLs (parameter URLs and exact matches from exclusion list)")
    
    # Convert to appropriate data types
    df['Clicks'] = pd.to_numeric(df['Clicks'], errors='coerce').fillna(0)
    
    # Filter out keywords with 0 clicks
    df = df[df['Clicks'] > 0]
    
    # If Position column exists, use it for filtering, otherwise assume all are in range
    if 'Position' in df.columns:
        df['Position'] = pd.to_numeric(df['Position'], errors='coerce')
        # Only filter if we have valid position data
        df_with_position = df[df['Position'].notna()]
        if len(df_with_position) > 0:
            df = df_with_position[(df_with_position['Position'] >= min_position) & 
                                 (df_with_position['Position'] <= max_position)]
        else:
            # No valid position data, keep all rows
            df['Position'] = 10.0
    else:
        # If no position column at all, assign default
        df['Position'] = 10.0
        st.info("No position data found. Analyzing all keywords regardless of ranking position.")
    
    # Exclude branded terms
    if branded_terms:
        branded_terms_clean = [term.strip() for term in branded_terms if term.strip()]
        if branded_terms_clean:
            pattern = '|'.join([re.escape(term) for term in branded_terms_clean])
            df = df[~df['Keyword'].str.contains(pattern, case=False, na=False)]
    
    # Sort by clicks (descending) and get top keywords per URL
    df = df.sort_values(['URL', 'Clicks'], ascending=[True, False])
    
    # Log filtering results
    if len(df) == 0:
        st.warning("No keywords found with clicks > 0 after filtering")
    
    return df

def process_crawl_data(df):
    """Process Screaming Frog crawl data"""
    # Clean URL - Address is the main column name
    url_columns = ['Address', 'URL', 'Landing Page', 'Landing Pages', 'URLs']
    url_col = None
    for col in url_columns:
        if col in df.columns:
            url_col = col
            df.rename(columns={col: 'URL'}, inplace=True)
            break
    
    if not url_col:
        st.error("No URL/Address column found in Screaming Frog data")
        return None
    
    df['URL'] = df['URL'].apply(clean_url)
    
    # Filter only indexable pages if column exists
    if 'Indexability' in df.columns:
        df = df[df['Indexability'] == 'Indexable']
    
    # Keep available columns from the expected set
    expected_cols = {
        'URL': 'URL',
        'Title 1': 'Title',
        'H1-1': 'H1',
        'Meta Description 1': 'Meta Description',
        'H2-1': 'H2-1',
        'H2-2': 'H2-2', 
        'H2-3': 'H2-3',
        'H2-4': 'H2-4',
        'H2-5': 'H2-5',
        'Copy 1': 'Copy'
    }
    
    # Create a new dataframe with only the columns that exist
    processed_df = pd.DataFrame()
    processed_df['URL'] = df['URL']
    
    # Add each column if it exists, otherwise create empty column
    for orig_col, new_col in expected_cols.items():
        if orig_col != 'URL':  # URL already processed
            if orig_col in df.columns:
                processed_df[new_col] = df[orig_col].fillna('')
            else:
                processed_df[new_col] = ''
    
    return processed_df

def create_striking_distance_report(gsc_df, crawl_df):
    """Create the final striking distance report in vertical format"""
    # Create report in vertical format - one row per keyword
    report_data = []
    
    for url in gsc_df['URL'].unique():
        url_data = gsc_df[gsc_df['URL'] == url].head(top_keywords_count)
        
        # Get crawl data for this URL
        crawl_row = crawl_df[crawl_df['URL'] == url]
        if len(crawl_row) > 0:
            crawl_row = crawl_row.iloc[0]
            title = crawl_row.get('Title', '')
            h1 = crawl_row.get('H1', '')
            meta_desc = crawl_row.get('Meta Description', '')
            copy = crawl_row.get('Copy', '')
            
            # Combine all H2s
            h2_content = ' '.join([
                str(crawl_row.get('H2-1', '')),
                str(crawl_row.get('H2-2', '')),
                str(crawl_row.get('H2-3', '')),
                str(crawl_row.get('H2-4', '')),
                str(crawl_row.get('H2-5', ''))
            ])
        else:
            title = h1 = meta_desc = copy = h2_content = ''
        
        # Create a row for each keyword
        for _, kw_row in url_data.iterrows():
            keyword = kw_row['Keyword']
            
            # Check keyword presence and handle missing data
            in_title = check_keyword_presence(keyword, title)
            in_meta = check_keyword_presence(keyword, meta_desc)
            in_h1 = check_keyword_presence(keyword, h1)
            in_h2 = check_keyword_presence(keyword, h2_content)
            in_body = check_keyword_presence(keyword, copy)
            
            # Convert None to "No Data" for Body column, keep TRUE/FALSE for others
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
    
    # Sort by URL and then by Clicks (descending)
    report_df = report_df.sort_values(['URL', 'Clicks'], ascending=[True, False])
    
    return report_df

# Main processing
if gsc_file and sf_file:
    try:
        # Load data
        with st.spinner("Loading data..."):
            gsc_df = load_file(gsc_file)
            crawl_df = load_file(sf_file)
        
        # Process data
        with st.spinner("Processing GSC data..."):
            processed_gsc = process_gsc_data(gsc_df, branded_terms, excluded_urls)
            
        if processed_gsc is not None and len(processed_gsc) > 0:
            with st.spinner("Processing crawl data..."):
                processed_crawl = process_crawl_data(crawl_df)
            
            with st.spinner("Creating striking distance report..."):
                report = create_striking_distance_report(processed_gsc, processed_crawl)
            
            # Display results
            st.success(f"✅ Analysis complete! Found {len(report['URL'].unique())} URLs with striking distance keywords.")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total URLs Analyzed", len(report['URL'].unique()))
            with col2:
                st.metric("Total Keywords Analyzed", len(report))
            with col3:
                # Calculate weighted average potential based on missing elements
                potential_clicks = 0
                for _, row in report.iterrows():
                    missing_count = 0
                    if row['In Title'] == False:
                        missing_count += 1
                    if row['In Meta'] == False:
                        missing_count += 1
                    if row['In H1'] == False:
                        missing_count += 1
                    if row['In H2'] == False:
                        missing_count += 1
                    if row['In Body'] == False:  # Don't count "No Data" as missing
                        missing_count += 1
                    
                    # Weight: assume 20% improvement potential per missing element, max 50%
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
            
        else:
            st.warning("No keywords found in the specified position range after filtering.")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please check that your files have the correct format and columns.")
        st.write("Supported formats: CSV, XLSX, XLS")
        
        # More detailed error info for debugging
        if "load_file" in str(e) or "read_excel" in str(e):
            st.info("💡 Tip: If you're having issues with Excel files, try saving as CSV format instead.")

else:
    # Instructions
    st.info("👆 Please upload both GSC and Screaming Frog CSV files to begin analysis.")
    
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
        
        ### Screaming Frog Export
        Required columns:
        - **Address** - The page URL
        - **Title 1** - Page title tag
        - **Meta Description 1** - Meta description tag
        - **H1-1** - Primary H1 heading
        
        Optional columns (will be used if present):
        - **H2-1** through **H2-5** - H2 subheadings
        - **Copy 1** - Main page content
        - **Indexability** - To filter only indexable pages
        
        Note: Missing optional columns won't stop the analysis - the tool will work with whatever data is available.
        
        ### Setting up Screaming Frog Custom Extraction
        1. Go to Configuration > Custom > Extraction
        2. Name the extractor "Copy"
        3. Select the CSS/XPath for your main content
        4. Choose "Extract Text" option
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
        - Exclude URLs with no SEO value (blogs, search pages, parameter URLs)
        
        **Automatic Exclusions:**
        - URLs containing parameters (?, =, #)
        - URLs you specify in the exclusion list (EXACT MATCH ONLY)
        
        **Important:** URL exclusion uses exact matching. For example:
        - Excluding `/blogs/news` will NOT exclude `/blogs/news/article-title`
        - Each URL must be excluded individually
        """)
