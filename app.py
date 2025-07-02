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
branded_terms_input = st.sidebar.text_area(
    "Branded Terms to Exclude (one per line)",
    placeholder="yourbrand\ncompany name\nbrand variations",
    help="Enter branded terms to exclude from analysis"
)

branded_terms = branded_terms_input.strip().split('\n') if branded_terms_input.strip() else []

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
    """Load CSV or Excel file into pandas DataFrame with robust parsing"""
    if file.name.endswith('.csv'):
        file.seek(0)
        return pd.read_csv(
            file,
            engine='python',
            on_bad_lines='skip',
            encoding='utf-8-sig',  # Auto-removes BOM
            skipinitialspace=True  # Strips spaces after delimiter
        )
    elif file.name.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file, engine='openpyxl' if file.name.endswith('.xlsx') else 'xlrd')
    else:
        raise ValueError("Unsupported file format")

def normalize_columns(df):
    """Normalize column names to handle various formats and encodings"""
    df.columns = (
        df.columns
        .str.strip()           # Remove leading/trailing spaces
        .str.replace('\ufeff', '')  # Remove BOM if present
        .str.replace(' ', '_')      # Replace spaces with underscores
        .str.lower()               # Convert to lowercase
    )
    return df

def clean_url(url):
    """Standardize URL format"""
    if pd.isna(url):
        return ""
    url = str(url).strip()
    # Remove protocol variations
    url = re.sub(r'^https?://', '', url)
    # Remove trailing slash
    url = url.rstrip('/')
    return url

def check_keyword_presence(keyword, text):
    """Check if keyword exists in text (case-insensitive)"""
    if pd.isna(keyword) or pd.isna(text) or keyword == "" or text == "":
        return False
    return str(keyword).lower() in str(text).lower()

def process_gsc_data(df, branded_terms):
    """Process Google Search Console data"""
    # Normalize column names first
    df = normalize_columns(df)
    
    # Comprehensive column mapping for GSC data
    gsc_column_mapping = {
        'query': 'keyword',
        'queries': 'keyword',
        'search_query': 'keyword',
        'landing_page': 'url',
        'landing_pages': 'url',
        'address': 'url',
        'page': 'url',
        'urls': 'url',
        'url': 'url',
        'average_position': 'position',
        'avg._position': 'position',
        'avg_position': 'position',
        'position': 'position',
        'clicks': 'clicks',
        'impressions': 'impressions',
        'ctr': 'ctr'
    }
    
    # Apply column mapping
    df.rename(columns=gsc_column_mapping, inplace=True)
    
    # Ensure required columns exist
    required_cols = ['keyword', 'url', 'clicks']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns in GSC data: {missing_cols}")
        st.info("Expected columns: Query, Landing Page (or Address/URLs), Clicks")
        st.write("Available columns after processing:", list(df.columns))
        return None
    
    # Clean data
    df['url'] = df['url'].apply(clean_url)
    df = df[df['url'].notna() & (df['url'] != '')]
    df = df[df['keyword'].notna() & (df['keyword'] != '')]
    
    # Convert to appropriate data types
    df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)
    
    # If Position column exists, use it for filtering, otherwise assume all are in range
    if 'position' in df.columns:
        df['position'] = pd.to_numeric(df['position'], errors='coerce')
        df = df[(df['position'] >= min_position) & (df['position'] <= max_position)]
    else:
        # If no position data, assign a default position in the middle of the range
        df['position'] = 10.0
        st.warning("No position data found in GSC export. Analyzing all keywords.")
    
    # Exclude branded terms
    if branded_terms:
        pattern = '|'.join([re.escape(term.strip()) for term in branded_terms if term.strip()])
        if pattern:
            df = df[~df['keyword'].str.contains(pattern, case=False, na=False)]
    
    # Sort by clicks (descending) and get top keywords per URL
    df = df.sort_values(['url', 'clicks'], ascending=[True, False])
    
    return df

def process_crawl_data(df):
    """Process Screaming Frog crawl data"""
    # Normalize column names first
    df = normalize_columns(df)
    
    # Look for URL column variants
    url_columns = ['address', 'url', 'landing_page', 'landing_pages', 'urls']
    url_col = None
    for col in url_columns:
        if col in df.columns:
            url_col = col
            df.rename(columns={col: 'url'}, inplace=True)
            break
    
    if not url_col:
        st.error("No URL/Address column found in Screaming Frog data")
        st.write("Available columns:", list(df.columns))
        return None
    
    df['url'] = df['url'].apply(clean_url)
    
    # Filter only indexable pages if column exists
    if 'indexability' in df.columns:
        df = df[df['indexability'].str.lower() == 'indexable']
    
    # Expected columns mapping (flexible for missing data)
    expected_cols = {
        'title_1': 'title',
        'h1-1': 'h1',
        'h1_1': 'h1',
        'meta_description_1': 'meta_description',
        'h2-1': 'h2_1',
        'h2_1': 'h2_1',
        'h2-2': 'h2_2',
        'h2_2': 'h2_2',
        'h2-3': 'h2_3',
        'h2_3': 'h2_3',
        'h2-4': 'h2_4',
        'h2_4': 'h2_4',
        'h2-5': 'h2_5',
        'h2_5': 'h2_5',
        'copy_1': 'copy'
    }
    
    # Create processed dataframe
    processed_df = pd.DataFrame()
    processed_df['url'] = df['url']
    
    # Add each column if it exists, otherwise create empty column
    for orig_col, new_col in expected_cols.items():
        if orig_col in df.columns:
            processed_df[new_col] = df[orig_col].fillna('')
        else:
            processed_df[new_col] = ''
    
    return processed_df

def create_striking_distance_report(gsc_df, crawl_df):
    """Create the final striking distance report"""
    # Get top keywords per URL
    top_keywords = []
    
    for url in gsc_df['url'].unique():
        url_data = gsc_df[gsc_df['url'] == url].head(top_keywords_count)
        if len(url_data) > 0:
            top_keywords.append({
                'url': url,
                'total_clicks': url_data['clicks'].sum(),
                'keywords_count': len(url_data),
                'keywords': url_data[['keyword', 'clicks', 'position']].to_dict('records')
            })
    
    # Create report dataframe
    report_data = []
    
    for item in top_keywords:
        row = {
            'url': item['url'],
            'total_clicks': item['total_clicks'],
            'keywords_count': item['keywords_count']
        }
        
        # Add top keywords
        for i, kw_data in enumerate(item['keywords'][:10], 1):
            row[f'keyword_{i}'] = kw_data['keyword']
            row[f'kw{i}_clicks'] = kw_data['clicks']
            row[f'kw{i}_position'] = round(kw_data['position'], 1)
        
        report_data.append(row)
    
    report_df = pd.DataFrame(report_data)
    
    # Merge with crawl data
    report_df = pd.merge(report_df, crawl_df, on='url', how='left')
    
    # Check keyword presence in on-page elements
    for i in range(1, 11):
        kw_col = f'keyword_{i}'
        if kw_col in report_df.columns:
            # Check in Title
            report_df[f'kw{i}_in_title'] = report_df.apply(
                lambda row: check_keyword_presence(row.get(kw_col), row.get('title', '')), 
                axis=1
            )
            # Check in H1
            report_df[f'kw{i}_in_h1'] = report_df.apply(
                lambda row: check_keyword_presence(row.get(kw_col), row.get('h1', '')), 
                axis=1
            )
            # Check in Meta Description
            report_df[f'kw{i}_in_meta_desc'] = report_df.apply(
                lambda row: check_keyword_presence(row.get(kw_col), row.get('meta_description', '')), 
                axis=1
            )
            # Check in H2s (combine all H2s for checking)
            def check_in_h2s(row, keyword):
                h2_content = ' '.join([
                    str(row.get('h2_1', '')),
                    str(row.get('h2_2', '')),
                    str(row.get('h2_3', '')),
                    str(row.get('h2_4', '')),
                    str(row.get('h2_5', ''))
                ])
                return check_keyword_presence(keyword, h2_content)
            
            report_df[f'kw{i}_in_h2s'] = report_df.apply(
                lambda row: check_in_h2s(row, row.get(kw_col)), 
                axis=1
            )
            # Check in Copy
            report_df[f'kw{i}_in_copy'] = report_df.apply(
                lambda row: check_keyword_presence(row.get(kw_col), row.get('copy', '')), 
                axis=1
            )
    
    # Sort by total clicks
    report_df = report_df.sort_values('total_clicks', ascending=False)
    
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
            processed_gsc = process_gsc_data(gsc_df, branded_terms)
            
        if processed_gsc is not None and len(processed_gsc) > 0:
            with st.spinner("Processing crawl data..."):
                processed_crawl = process_crawl_data(crawl_df)
            
            if processed_crawl is not None:
                with st.spinner("Creating striking distance report..."):
                    report = create_striking_distance_report(processed_gsc, processed_crawl)
                
                # Display results
                st.success(f"✅ Analysis complete! Found {len(report)} URLs with striking distance opportunities.")
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total URLs Analyzed", len(report))
                with col2:
                    total_keywords = report['keywords_count'].sum()
                    st.metric("Total Keywords in Striking Distance", int(total_keywords))
                with col3:
                    total_clicks = report['total_clicks'].sum()
                    st.metric("Total Clicks Potential", int(total_clicks))
                
                # Display top opportunities
                st.header("🎯 Top Optimization Opportunities")
                
                # Filter to show only URLs with missing keywords in elements
                opportunities = []
                for idx, row in report.iterrows():
                    missing_elements = []
                    for i in range(1, 11):
                        kw_col = f'keyword_{i}'
                        if kw_col in row and pd.notna(row[kw_col]) and row[kw_col] != '':
                            elements_missing = []
                            if not row.get(f'kw{i}_in_title', True):
                                elements_missing.append('Title')
                            if not row.get(f'kw{i}_in_h1', True):
                                elements_missing.append('H1')
                            if not row.get(f'kw{i}_in_meta_desc', True):
                                elements_missing.append('Meta Desc')
                            if not row.get(f'kw{i}_in_h2s', True):
                                elements_missing.append('H2s')
                            if not row.get(f'kw{i}_in_copy', True):
                                elements_missing.append('Copy')
                            
                            if elements_missing:
                                missing_elements.append({
                                    'keyword': row[kw_col],
                                    'clicks': row.get(f'kw{i}_clicks', 0),
                                    'position': row.get(f'kw{i}_position', 0),
                                    'missing_in': elements_missing
                                })
                    
                    if missing_elements:
                        opportunities.append({
                            'url': row['url'],
                            'total_clicks': row['total_clicks'],
                            'missing_keywords': missing_elements
                        })
                
                # Display opportunities
                if opportunities:
                    st.write(f"Found {len(opportunities)} URLs with optimization opportunities:")
                    
                    for opp in opportunities[:10]:  # Show top 10
                        with st.expander(f"🔗 {opp['url']} (Potential: {int(opp['total_clicks'])} clicks)"):
                            for mk in opp['missing_keywords']:
                                st.write(f"**Keyword:** {mk['keyword']}")
                                st.write(f"- Clicks: {int(mk['clicks'])}")
                                st.write(f"- Position: {mk['position']:.1f}")
                                st.write(f"- Missing in: {', '.join(mk['missing_in'])}")
                                st.write("---")
                else:
                    st.info("🎉 Great news! All your striking distance keywords are already well-optimized in your on-page elements.")
                
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
                st.subheader("Report Preview (First 10 rows)")
                # Select columns to display
                display_cols = ['url', 'total_clicks', 'keywords_count']
                for i in range(1, 4):  # Show first 3 keywords
                    if f'keyword_{i}' in report.columns:
                        display_cols.extend([
                            f'keyword_{i}', 
                            f'kw{i}_clicks',
                            f'kw{i}_in_title',
                            f'kw{i}_in_h1',
                            f'kw{i}_in_h2s',
                            f'kw{i}_in_copy'
                        ])
                
                available_display_cols = [col for col in display_cols if col in report.columns]
                st.dataframe(report[available_display_cols].head(10))
            else:
                st.error("Failed to process Screaming Frog data. Please check the file format and column names.")
        else:
            st.warning("No keywords found in the specified position range after filtering.")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please check that your files have the correct format and columns.")
        st.write("Supported formats: CSV, XLSX, XLS")

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
        
        Note: Missing optional columns will not stop the analysis - the tool will work with whatever data is available.
        
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
        """)
