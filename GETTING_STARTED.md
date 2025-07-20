# 🚀 Quick Start Guide

## 5-Minute Setup

### 1. Install & Run
```bash
# Navigate to the project directory
cd "C:\Users\admin\Documents\Marketing\Roger SEO\Scripts\Striking-Distance-On-Page-Analysis"

# Run setup (recommended)
python setup.py

# Or install manually
pip install -r requirements.txt

# Start the app
streamlit run app.py
```

### 2. Get Your Google Search Console Data

**Option A: Google Search Console Export**
1. Go to [Google Search Console](https://search.google.com/search-console/)
2. Select your property
3. Go to "Performance" → "Search results"
4. Click "Export" → "Download CSV"

**Option B: Google Analytics 4 (if linked)**
1. Go to GA4 → Reports → Search Console → Queries
2. Export the report

### 3. Upload & Configure
1. **Upload your GSC file** in the app
2. **Add branded terms** to exclude (one per line):
   ```
   your company name
   yourbrand
   trademark
   ```
3. **Exclude URLs** you don't want analyzed (exact match):
   ```
   https://example.com/blog
   https://example.com/contact
   ```

### 4. Start Analysis
Click "Start Analysis" and watch the AI crawl your URLs in real-time!

## 🎯 Pro Tips

### For Best Results
- **Use 30-90 days of data** for statistical significance
- **Focus on keywords with 10+ clicks** for actionable insights
- **Prioritize positions 8-15** for quick wins
- **Check 5-10 keywords per URL** for comprehensive analysis

### Sample Data Format
Your CSV should have these columns:
```
Query,Landing Page,Clicks,Position
best seo tools,https://example.com/seo-tools,245,12
keyword research,https://example.com/keyword-research,189,8
```

### Common Issues & Fixes

**"crawl4ai not found"**
```bash
pip install crawl4ai --upgrade
```

**"Chrome not found"**
- Install Google Chrome
- Or disable headless mode in settings

**"No data found"**
- Ensure your CSV has "Query" and "Landing Page" columns
- Check that URLs don't have parameters (?, =, #)

## 📊 Understanding Your Results

### What the Colors Mean
- **Green ✅**: Keyword is present
- **Red ❌**: Keyword is missing (optimization opportunity)
- **Gray ⚪**: No data available

### Quick Actions
1. **Sort by Clicks**: Focus on high-impact keywords
2. **Filter by "Missing"**: Find immediate opportunities
3. **Export CSV**: Share with your team
4. **Track changes**: Re-run monthly to measure improvements

## 🔄 Next Steps

1. **Week 1**: Fix missing keywords in titles and meta descriptions
2. **Week 2**: Add keywords to H1 and H2 headings
3. **Week 3**: Naturally incorporate keywords into body content
4. **Week 4**: Re-run analysis to measure improvements

## 📞 Need Help?

- **Check the README.md** for detailed documentation
- **Review failed URLs** in the app for troubleshooting
- **Start with 10-20 URLs** for testing before scaling up
