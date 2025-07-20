# 🚀 Quick Start Guide

## 1. Install & Run (2 minutes)

```bash
# Navigate to the project folder
cd "C:\Users\admin\Documents\Marketing\Roger SEO\Scripts\Striking-Distance-On-Page-Analysis"

# Install dependencies
pip install -r requirements.txt

# Run the tool
streamlit run app.py
```

## 2. Get Your Data (3 minutes)

### From Google Search Console:
1. Go to [Google Search Console](https://search.google.com/search-console)
2. Select your property
3. Go to **Performance → Search Results**
4. Set date range (recommend last 3-6 months)
5. Click **Export → Download CSV**

### Required columns in your CSV:
- **Query** (keyword)
- **Landing Page** (URL)
- **Clicks**
- **Position** (optional)

## 3. Upload & Analyze (1 minute)

1. **Upload your GSC CSV file**
2. **Configure settings**:
   - Add branded terms to exclude
   - Set URL exclusions if needed
   - Adjust keywords per URL (default: 10)
3. **Click "Start Analysis"**
4. **Download your report**

## 4. Read Your Results

Your report will show:
- **URLs** with striking distance keywords (positions 4-20)
- **Keywords** ranked by clicks
- **Optimization gaps** (missing from title, meta, H1, H2, body)
- **Click potential** for improvements

## 🎯 Example Workflow

1. **Export GSC data** for last 3 months
2. **Upload to tool** and run analysis
3. **Focus on keywords** with:
   - High clicks but missing from title/meta
   - Positions 4-10 with content gaps
   - Your brand terms filtered out
4. **Optimize pages** by adding missing keywords
5. **Track improvements** in GSC after 2-4 weeks

## 📊 Sample Output

| URL | Keyword | Clicks | Position | In Title | In Meta | In H1 | In H2 | In Body |
|-----|---------|--------|----------|----------|---------|-------|-------|---------|
| /product-page | best running shoes | 150 | 8 | ❌ | ✅ | ❌ | ✅ | ✅ |
| /blog-post | running tips | 89 | 12 | ✅ | ❌ | ✅ | ❌ | ✅ |

**Action**: Add "best running shoes" to title and H1 for first URL

## ⚡ Pro Tips

- **Start small**: Test with 50-100 URLs first
- **Use cache**: Enable caching for repeated runs
- **Filter smart**: Exclude parameter URLs automatically
- **Focus on wins**: Prioritize keywords in positions 4-10
- **Monitor**: Check results in GSC after 2-4 weeks

## 🆘 Need Help?

- **No crawl4ai?** → `pip install crawl4ai`
- **File issues?** → Save as CSV instead of Excel
- **Failed crawls?** → Increase timeout or disable headless mode
- **No keywords?** → Check position range and branded filters

**Ready to go?** Run `streamlit run app.py` and start optimizing!
