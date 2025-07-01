import streamlit as st
import pandas as pd
import numpy as np
from typing import Union, List
import io
import re

# Page configuration
st.set_page_config(
    page_title="Striking Distance SEO Analysis",
    page_icon="🎯",
    layout="wide"
)

# Title and description
st.title("🎯 Striking Distance SEO Analysis Tool")
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

# Settings
min_position = st.sidebar.number_input("Minimum Position", value=4, min_value=1, max_value=100)
max_position = st.sidebar.number_input("Maximum Position", value=20, min_value=1, max_value=100)
min_volume = st.sidebar.number_input("Minimum Search Volume", value=10, min_value=0)
top_keywords_count = st.sidebar.number_input("Top Keywords to Analyze", value=10, min_value=1, max_value=20)

# File uploaders
col1, col2 = st.columns(2)

with col1:
    st.header("📊 Google Search Console Data")
    gsc_file = st.file_uploader(
        "Upload GSC Performance Report (CSV)",
        type=['csv'],
        help="Export from GSC with Query, Landing Page, Clicks, Impressions, CTR, Position"
    )

with col2:
    st.header("🕷️ Screaming Frog Data")
    sf_file = st.file_uploader(
        "Upload Screaming Frog Internal HTML Export (CSV)",
        type=['csv'],
        help="Export with Address, Title 1, H1-1, Meta Description 1, Copy 1, Indexability"
    )

# Helper functions
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
    # Rename columns if needed
    column_mapping = {
        'Query': 'Keyword',
        'Page': 'URL',
        'Landing Page': 'URL',
        'Average Position': 'Position',
        'Avg. position': 'Position'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
    
    # Ensure required columns exist
    required_cols = ['Keyword', 'URL', 'Clicks', 'Position']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns in GSC data: {missing_cols}")
        return None
    
    # Clean data
    df['URL'] = df['URL'].apply(clean_url)
    df = df[df['URL'].notna() & (df['URL'] != '')]
    df = df[df['Keyword'].notna() & (df['Keyword'] != '')]
    
    # Convert to appropriate data types
    df['Clicks'] = pd.to_numeric(df['Clicks'], errors='coerce').fillna(0)
    df['Position'] = pd.to_numeric(df['Position'], errors='coerce')
    
    # Filter by position
    df = df[(df['Position'] >= min_position) & (df['Position'] <= max_position)]
    
    # Exclude branded terms
    if branded_terms:
        pattern = '|'.join([re.escape(term.strip()) for term in branded_terms if term.strip()])
        if pattern:
            df = df[~df['Keyword'].str.contains(pattern, case=False, na=False)]
    
    # Sort by clicks (descending) and get top keywords per URL
    df = df.sort_values(['URL', 'Clicks'], ascending=[True, False])
    
    return df

def process_crawl_data(df):
    """Process Screaming Frog crawl data"""
    # Rename columns to standardized names
    column_mapping = {
        'Address': 'URL',
        'Title 1': 'Title',
        'H1-1': 'H1',
        'H1 1': 'H1',
        'Meta Description 1': 'Meta Description',
        'Copy 1': 'Copy'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
    
    # Clean URL
    df['URL'] = df['URL'].apply(clean_url)
    
    # Filter only indexable pages if column exists
    if 'Indexability' in df.columns:
        df = df[df['Indexability'] == 'Indexable']
    
    # Keep only necessary columns
    keep_cols = ['URL', 'Title', 'H1', 'Meta Description', 'Copy']
    available_cols = [col for col in keep_cols if col in df.columns]
    df = df[available_cols]
    
    # Fill NaN values with empty strings
    df = df.fillna('')
    
    return df

def create_striking_distance_report(gsc_df, crawl_df):
    """Create the final striking distance report"""
    # Get top keywords per URL
    top_keywords = []
    
    for url in gsc_df['URL'].unique():
        url_data = gsc_df[gsc_df['URL'] == url].head(top_keywords_count)
        if len(url_data) > 0:
            top_keywords.append({
                'URL': url,
                'Total_Clicks': url_data['Clicks'].sum(),
                'Keywords_Count': len(url_data),
                'Keywords': url_data[['Keyword', 'Clicks', 'Position']].to_dict('records')
            })
    
    # Create report dataframe
    report_data = []
    
    for item in top_keywords:
        row = {
            'URL': item['URL'],
            'Total Clicks (Top Keywords)': item['Total_Clicks'],
            'Keywords in Striking Distance': item['Keywords_Count']
        }
        
        # Add top keywords
        for i, kw_data in enumerate(item['Keywords'][:10], 1):
            row[f'Keyword {i}'] = kw_data['Keyword']
            row[f'KW{i} Clicks'] = kw_data['Clicks']
            row[f'KW{i} Position'] = round(kw_data['Position'], 1)
        
        report_data.append(row)
    
    report_df = pd.DataFrame(report_data)
    
    # Merge with crawl data
    report_df = pd.merge(report_df, crawl_df, on='URL', how='left')
    
    # Check keyword presence in on-page elements
    for i in range(1, 11):
        kw_col = f'Keyword {i}'
        if kw_col in report_df.columns:
            # Check in Title
            report_df[f'KW{i} in Title'] = report_df.apply(
                lambda row: check_keyword_presence(row.get(kw_col), row.get('Title', '')), 
                axis=1
            )
            # Check in H1
            report_df[f'KW{i} in H1'] = report_df.apply(
                lambda row: check_keyword_presence(row.get(kw_col), row.get('H1', '')), 
                axis=1
            )
            # Check in Meta Description
            report_df[f'KW{i} in Meta Desc'] = report_df.apply(
                lambda row: check_keyword_presence(row.get(kw_col), row.get('Meta Description', '')), 
                axis=1
            )
            # Check in Copy
            report_df[f'KW{i} in Copy'] = report_df.apply(
                lambda row: check_keyword_presence(row.get(kw_col), row.get('Copy', '')), 
                axis=1
            )
    
    # Sort by total clicks
    report_df = report_df.sort_values('Total Clicks (Top Keywords)', ascending=False)
    
    return report_df

# Main processing
if gsc_file and sf_file:
    try:
        # Load data
        with st.spinner("Loading data..."):
            gsc_df = pd.read_csv(gsc_file)
            crawl_df = pd.read_csv(sf_file)
        
        # Process data
        with st.spinner("Processing GSC data..."):
            processed_gsc = process_gsc_data(gsc_df, branded_terms)
            
        if processed_gsc is not None and len(processed_gsc) > 0:
            with st.spinner("Processing crawl data..."):
                processed_crawl = process_crawl_data(crawl_df)
            
            with st.spinner("Creating striking distance report..."):
                report = create_striking_distance_report(processed_gsc, processed_crawl)
            
            # Display results
            st.success(f"✅ Analysis complete! Found {len(report)} URLs with striking distance opportunities.")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total URLs Analyzed", len(report))
            with col2:
                total_keywords = sum([report[f'Keywords in Striking Distance'].sum()])
                st.metric("Total Keywords in Striking Distance", int(total_keywords))
            with col3:
                total_clicks = report['Total Clicks (Top Keywords)'].sum()
                st.metric("Total Clicks Potential", int(total_clicks))
            
            # Display top opportunities
            st.header("🎯 Top Optimization Opportunities")
            
            # Filter to show only URLs with missing keywords in elements
            opportunities = []
            for idx, row in report.iterrows():
                missing_elements = []
                for i in range(1, 11):
                    kw_col = f'Keyword {i}'
                    if kw_col in row and pd.notna(row[kw_col]) and row[kw_col] != '':
                        elements_missing = []
                        if not row.get(f'KW{i} in Title', True):
                            elements_missing.append('Title')
                        if not row.get(f'KW{i} in H1', True):
                            elements_missing.append('H1')
                        if not row.get(f'KW{i} in Meta Desc', True):
                            elements_missing.append('Meta Desc')
                        if not row.get(f'KW{i} in Copy', True):
                            elements_missing.append('Copy')
                        
                        if elements_missing:
                            missing_elements.append({
                                'keyword': row[kw_col],
                                'clicks': row.get(f'KW{i} Clicks', 0),
                                'position': row.get(f'KW{i} Position', 0),
                                'missing_in': elements_missing
                            })
                
                if missing_elements:
                    opportunities.append({
                        'URL': row['URL'],
                        'Total_Clicks': row['Total Clicks (Top Keywords)'],
                        'Missing_Keywords': missing_elements
                    })
            
            # Display opportunities
            if opportunities:
                st.write(f"Found {len(opportunities)} URLs with optimization opportunities:")
                
                for opp in opportunities[:10]:  # Show top 10
                    with st.expander(f"🔗 {opp['URL']} (Potential: {int(opp['Total_Clicks'])} clicks)"):
                        for mk in opp['Missing_Keywords']:
                            st.write(f"**Keyword:** {mk['keyword']}")
                            st.write(f"- Clicks: {int(mk['clicks'])}")
                            st.write(f"- Position: {mk['position']:.1f}")
                            st.write(f"- Missing in: {', '.join(mk['missing_in'])}")
                            st.write("---")
            
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
            display_cols = ['URL', 'Total Clicks (Top Keywords)', 'Keywords in Striking Distance']
            for i in range(1, 4):  # Show first 3 keywords
                if f'Keyword {i}' in report.columns:
                    display_cols.extend([
                        f'Keyword {i}', 
                        f'KW{i} Clicks',
                        f'KW{i} in Title',
                        f'KW{i} in H1',
                        f'KW{i} in Copy'
                    ])
            
            available_display_cols = [col for col in display_cols if col in report.columns]
            st.dataframe(report[available_display_cols].head(10))
            
        else:
            st.warning("No keywords found in the specified position range after filtering.")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please check that your CSV files have the correct format and columns.")

else:
    # Instructions
    st.info("👆 Please upload both GSC and Screaming Frog CSV files to begin analysis.")
    
    with st.expander("📋 Required File Formats"):
        st.markdown("""
        ### Google Search Console Export
        Required columns:
        - **Query** (or Keyword)
        - **Page** (or URL, Landing Page)
        - **Clicks**
        - **Impressions**
        - **CTR**
        - **Average Position** (or Position)
        
        ### Screaming Frog Export
        Required columns:
        - **Address** (URL)
        - **Title 1**
        - **H1-1** (or H1 1)
        - **Meta Description 1**
        - **Copy 1** (optional but recommended)
        - **Indexability** (optional but recommended)
        
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
