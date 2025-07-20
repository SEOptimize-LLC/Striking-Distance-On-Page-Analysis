# 🚀 Getting Started with Enhanced Striking Distance Analysis

## Quick Setup Guide

### 1. Install Required Dependencies

```bash
# Install crawl4ai
pip install crawl4ai

# Install other dependencies
pip install streamlit pandas numpy openpyxl xlrd

# Setup crawl4ai browser
crawl4ai-setup
```

### 2. Run the Application

```bash
# Navigate to the project directory
cd "C:\Users\admin\Documents\Marketing\Roger SEO\Scripts\Striking-Distance-On-Page-Analysis"

# Start the Streamlit app
streamlit run app.py
```

### 3. How to Use

1. **Upload your Google Search Console data** - Export from GSC with Query, Landing Page, and Clicks columns
2. **Configure settings** - Add branded terms to exclude, URLs to exclude, etc.
3. **Start analysis** - Click "Start Analysis" to begin AI-powered crawling
4. **Review results** - Get actionable insights for keyword optimization

## Key Features

✅ **No Screaming Frog Required** - Uses AI-powered crawl4ai for content extraction
✅ **Clean Content Extraction** - Automatically removes nav, footer, ads, sidebars
✅ **Smart Keyword Matching** - Handles variations, plurals, and articles
✅ **Real-time Progress** - See crawling progress with live updates
✅ **Export Results** - Download CSV reports for further analysis

## Troubleshooting

### Common Issues

1. **crawl4ai not found**: Run `pip install crawl4ai`
2. **Browser setup issues**: Run `python -m playwright install chromium`
3. **Large datasets**: Increase max wait time in settings
4. **Failed crawls**: Check if URLs are accessible and not blocked

### Data Format Requirements

Your GSC export should have these columns:
- **Query** or **Keyword** - Search terms
- **Landing Page** or **URL** - Page URLs
- **Clicks** - Number of clicks
- **Position** (optional) - Ranking position

## Support

The tool is ready to use! The remaining linting warnings don't affect functionality - they're just style recommendations.
