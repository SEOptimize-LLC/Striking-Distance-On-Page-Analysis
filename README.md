# Enhanced Striking Distance Analysis Tool

This enhanced version replaces the original Striking Distance tool with AI-powered content extraction using **crawl4ai**, eliminating the need for Screaming Frog exports.

## 🚀 Key Improvements

- **No Screaming Frog Required**: Direct URL crawling with AI-powered content extraction
- **Clean Content Extraction**: Removes navigation, footers, ads, and sidebars automatically
- **Flexible Column Mapping**: Handles various GSC export formats automatically
- **Real-time Progress**: Live crawling progress with status updates
- **Enhanced Error Handling**: Detailed error reporting for failed URLs

## 📋 Installation

1. **Install crawl4ai**:
   ```bash
   pip install -r requirements_enhanced.txt
   ```

2. **Setup crawl4ai**:
   ```bash
   crawl4ai-setup
   ```

3. **Run the enhanced app**:
   ```bash
   streamlit run enhanced_app.py
   ```

## 🎯 How to Use

### 1. Export from Google Search Console
- Go to Google Search Console → Performance → Search Results
- Set your date range (recommend 3-6 months)
- Export as CSV/Excel with these columns:
  - **Query** (or "Keyword", "Search Term")
  - **Landing Page** (or "URL", "Address", "Page")
  - **Clicks**
  - **Position** (optional)

### 2. Upload and Configure
- Upload your GSC export file
- Add branded terms to exclude (one per line)
- Add exact URLs to exclude (one per line)
- Set number of top keywords to analyze per URL

### 3. Run Analysis
- Click "Start Analysis"
- Watch real-time crawling progress
- Download your optimized report

## 📊 Report Output

The tool generates a CSV with these columns:
- **URL**: The page URL
- **Keyword**: The search query
- **Clicks**: Current clicks from GSC
- **Position**: Current ranking position
- **In Title**: Keyword found in page title
- **In Meta Description**: Keyword found in meta description
- **In H1**: Keyword found in H1 heading
- **In H2**: Keyword found in H2 headings
- **In Body**: Keyword found in main content

## 🔧 Column Mapping

The tool automatically detects columns with these names:

**Query/Keyword columns:**
- Query, Queries, Keyword, Keywords, Search Term

**URL columns:**
- Landing Page, Landing Pages, URL, URLs, Address, Page, Pages, Link, Links, Path, URI

**Clicks columns:**
- Clicks, Click, Visits, Traffic

**Position columns:**
- Position, Rank, Ranking, Avg Position, Average Position

## 🛠️ Troubleshooting

### crawl4ai Installation Issues
```bash
# If crawl4ai-setup fails, try:
python -m playwright install chromium
```

### Memory Issues
- Reduce the number of URLs by filtering your GSC export
- Use shorter date ranges in GSC exports
- Exclude low-traffic URLs

### Failed URL Crawls
- Check if URLs are accessible
- Verify URLs don't require authentication
- Check for rate limiting on target sites

## 📈 Optimization Tips

1. **Focus on high-click keywords**: Prioritize keywords with >10 clicks
2. **Look for missing keywords**: Keywords not in Title/H1 are quick wins
3. **Check meta descriptions**: Often overlooked but important for CTR
4. **Review H2 usage**: Good for long-tail keyword targeting
5. **Body content gaps**: Ensure keywords appear naturally in content

## 🔄 Migration from Original Tool

If you were using the original tool:
1. **No Screaming Frog needed**: Skip the SF crawl entirely
2. **Same GSC format**: Your existing GSC exports work directly
3. **Enhanced accuracy**: AI extracts cleaner content than SF's "Copy" field
4. **Faster setup**: No need to configure SF custom extractions

## 🆘 Support

For issues:
1. Check the "View failures" expander for failed URLs
2. Verify your GSC export has the required columns
3. Ensure crawl4ai is properly installed
4. Check internet connectivity for URL crawling
