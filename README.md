# 🎯 Striking Distance On-Page Analysis Tool

This advanced SEO tool uses **crawl4ai** to extract clean, SEO-relevant content directly from URLs, eliminating the need for Screaming Frog exports. It cross-references Google Search Console data with AI-powered content extraction to identify keyword optimization opportunities.

## 🚀 What's New

- **AI-Powered Content Extraction**: Uses crawl4ai to intelligently extract main content while excluding navigation, footers, ads, and sidebars
- **No Screaming Frog Required**: Direct URL crawling eliminates the need for HTML exports
- **Real-time Progress Tracking**: See live progress as URLs are crawled
- **Smart Content Filtering**: Automatically removes boilerplate content
- **Enhanced Error Handling**: Detailed feedback for failed crawls

## 📋 Requirements

- Python 3.8+
- Google Search Console performance report (CSV, XLSX, or XLS)
- Internet connection for URL crawling

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SEOptimize-LLC/Striking-Distance-On-Page-Analysis.git
   cd Striking-Distance-On-Page-Analysis
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install crawl4ai** (if not included):
   ```bash
   pip install crawl4ai
   ```

## 🎯 How to Use

### 1. Export Google Search Console Data
- Go to Google Search Console → Performance → Search Results
- Set your date range (recommend 3-6 months)
- Export with these columns:
  - **Query** (keyword)
  - **Landing Page** (URL)
  - **Clicks**
  - **Position** (optional but recommended)
  - **Impressions** (optional)

### 2. Run the Tool
```bash
streamlit run app.py
```

### 3. Configure Settings
- **Branded Terms**: Add your brand names to exclude
- **URL Exclusions**: Exclude specific URLs (exact match)
- **Keywords to Analyze**: Set how many top keywords per URL
- **crawl4ai Settings**: Adjust caching, headless mode, and timeout

### 4. Upload & Analyze
- Upload your GSC file
- Click "Start Analysis"
- Watch real-time crawling progress
- Download your optimized report

## 📊 Understanding Your Report

The tool generates a comprehensive report with these columns:

| Column | Description |
|--------|-------------|
| **URL** | The page being analyzed |
| **Keyword** | Search query in striking distance (positions 4-20) |
| **Clicks** | Current clicks from GSC |
| **Position** | Current ranking position |
| **In Title** | Keyword appears in page title |
| **In Meta Description** | Keyword appears in meta description |
| **In H1** | Keyword appears in H1 heading |
| **In H2** | Keyword appears in H2 headings |
| **In Body** | Keyword appears in main content |

## 🔍 Key Features

### AI Content Extraction
- **Smart Filtering**: Removes navigation, footers, sidebars, ads
- **Content Focus**: Extracts only the main article/content
- **SEO Elements**: Captures titles, meta descriptions, headings
- **Clean Data**: No boilerplate or template content

### Keyword Optimization
- **Striking Distance**: Focuses on keywords ranking 4-20
- **Smart Matching**: Handles variations, plurals, and articles
- **Priority Scoring**: Ranks by click potential
- **Gap Analysis**: Identifies missing keyword placements

### URL Management
- **Parameter Filtering**: Automatically excludes URLs with ?, =, #
- **Exact Exclusions**: Precise URL matching for exclusions
- **Bulk Processing**: Handles hundreds of URLs efficiently
- **Error Reporting**: Detailed logs for failed crawls

## 🎯 Optimization Strategy

### High Priority
- Keywords with high clicks but missing from title/meta
- Keywords in positions 4-10 with optimization gaps
- High-volume keywords not in H1/H2

### Medium Priority
- Keywords in positions 11-15 with content gaps
- Keywords present but could be better optimized
- Long-tail keywords with good click potential

### Low Priority
- Keywords already well-optimized
- Very low-volume keywords
- Keywords in positions 16-20

## 🛠️ Troubleshooting

### Common Issues

**"No crawl4ai" error**:
```bash
pip install crawl4ai
```

**"Failed to crawl URLs"**:
- Check internet connection
- Verify URLs are accessible
- Increase timeout in settings
- Try disabling headless mode

**"No keywords found"**:
- Ensure GSC file has correct columns
- Check position range settings
- Verify branded terms aren't filtering everything

**"File format error"**:
- Save Excel files as CSV
- Ensure required columns exist
- Check for special characters in column names

### Performance Tips

- **Use cache**: Speeds up repeated crawls
- **Batch processing**: Process 50-100 URLs at a time
- **Timeout settings**: Increase for slow-loading sites
- **Headless mode**: Disable for debugging visual issues

## 📈 Advanced Usage

### Custom CSS Selectors
While the tool automatically detects main content, you can customize extraction by modifying the `exclude_classes` and `exclude_ids` parameters in the crawler configuration.

### API Integration
The tool can be integrated into larger SEO workflows:
```python
from app import crawl_urls_async, create_striking_distance_report
# Use functions programmatically
```

### Batch Processing
For large sites, process URLs in chunks:
1. Export GSC data in date ranges
2. Process 100 URLs at a time
3. Combine results for comprehensive analysis

## 🔄 Updates & Maintenance

- **crawl4ai updates**: Regularly update for latest features
- **GSC format changes**: Tool adapts to GSC export changes
- **Performance improvements**: Ongoing optimization for speed

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review failed crawl logs
3. Test with a small sample first
4. Ensure all dependencies are updated

---

**Note**: This tool respects robots.txt and includes appropriate delays between requests. Always use responsibly and consider rate limits for your target sites.
