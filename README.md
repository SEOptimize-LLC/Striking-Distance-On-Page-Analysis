# Striking Distance On-Page Analysis Tool

This tool uses **crawl4ai** to extract clean, SEO-relevant content directly from URLs, eliminating the need for Screaming Frog exports. It cross-references Google Search Console data with AI-powered content extraction to identify keyword optimization opportunities.

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Usage
```bash
streamlit run app.py
```

## 📊 How It Works

1. **Upload Google Search Console Data** - Export your GSC performance report
2. **AI-Powered Crawling** - The tool automatically crawls your URLs using crawl4ai
3. **Clean Content Extraction** - Removes navigation, footers, sidebars, ads automatically
4. **Keyword Analysis** - Checks if keywords appear in key SEO elements
5. **Optimization Report** - Identifies quick wins for striking distance keywords

## 📋 Required File Format

### Google Search Console Export
Required columns:
- **Query** - The search term/keyword
- **Landing Page** (or Address/URL) - The URL that appeared in search
- **Clicks** - Number of clicks received

Optional but recommended:
- **Position** - Average ranking position
- **Impressions** - Number of times shown in search
- **CTR** - Click-through rate

## 🤖 crawl4ai Features

This enhanced version uses **crawl4ai** to:
- Extract clean, SEO-relevant content directly from your URLs
- Automatically identify and exclude navigation, footer, sidebar content
- Extract Title tags, Meta descriptions, H1, H2 headings, and main body content
- Cache results for faster subsequent runs

## 🎯 What are Striking Distance Keywords?

Striking Distance keywords are search queries where your website ranks between positions 4-20. These represent opportunities where small optimizations can lead to significant traffic gains.

This tool helps you:
- Identify keywords just outside the top 3 positions
- Check if these keywords appear in key on-page elements
- Prioritize optimization efforts based on click potential
- Exclude branded terms from analysis
- Exclude URLs with no SEO value (blogs, search pages, parameter URLs)

## ⚙️ Configuration Options

### Branded Terms
Enter branded terms to exclude from analysis (one per line):
```
yourbrand
company name
brand variations
```

### URL Exclusions
Enter exact URLs to exclude (one per line - EXACT MATCH):
```
https://www.example.com/blogs/news
/admin
/search
```

**Important:** URL exclusion uses exact matching. For example:
- Excluding `/blogs/news` will NOT exclude `/blogs/news/article-title`
- Each URL must be excluded individually

### crawl4ai Settings
- **Use Cache**: Cache crawled content for faster subsequent runs
- **Headless Mode**: Run browser in headless mode
- **Max Wait Time**: Maximum time to wait for page load (seconds)

## 🔄 Benefits Over Original Tool

- **No Screaming Frog required** - Direct URL crawling
- **Cleaner content extraction** - AI-powered filtering of irrelevant content
- **Faster setup** - Just upload GSC data and go
- **Better content quality** - Removes ads, navigation, footers automatically
- **Real-time progress** - Live crawling updates with progress bars
- **Caching support** - Faster subsequent runs with built-in caching

## 🛠️ Troubleshooting

### crawl4ai Installation Issues
If you encounter issues installing crawl4ai:
```bash
pip install --upgrade pip
pip install crawl4ai
```

### Browser Issues
- Ensure you have Chrome/Chromium installed
- Try disabling headless mode in settings if you encounter issues

### File Format Issues
- If Excel files don't work, try saving as CSV
- Ensure your GSC export has the required columns
