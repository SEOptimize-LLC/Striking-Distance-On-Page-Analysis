# Striking Distance On Page Analysis

A powerful SEO tool that cross-references Google Search Console performance data with Screaming Frog crawl data to identify keyword optimization opportunities in "striking distance" (positions 4-20).

## 🎯 What is Striking Distance?

Striking Distance keywords are search queries where your website ranks between positions 4-20. These represent the best opportunities for quick SEO wins, as small on-page optimizations can often push these keywords into the top 3 positions, resulting in significant traffic gains.

## ✨ Features

- **Automated Analysis**: Quickly identify keywords that are close to ranking in top positions
- **On-Page Element Checking**: Verifies if target keywords appear in Title, H1, Meta Description, and Body Copy
- **Branded Term Exclusion**: Filter out branded keywords to focus on non-branded opportunities
- **Customizable Parameters**: Define your own position range and minimum search volume thresholds
- **Click-Based Prioritization**: Focuses on keywords with the highest click potential
- **Comprehensive Reporting**: Export detailed CSV reports for further analysis
- **Interactive Dashboard**: Real-time analysis with visual insights

## 📋 Prerequisites

### Required Data Exports

#### 1. Google Search Console Export
Export your performance data with the following columns:
- **Query** (or Keyword)
- **Page** (or URL/Landing Page)
- **Clicks**
- **Impressions**
- **CTR**
- **Average Position** (or Position)

#### 2. Screaming Frog Crawl Export
Configure and export with these columns:
- **Address** (URL)
- **Title 1**
- **H1-1** (or H1 1)
- **Meta Description 1**
- **Copy 1** (optional but recommended - requires custom extraction)
- **Indexability** (optional but recommended)

### Setting up Screaming Frog Custom Extraction
To extract page copy for comprehensive analysis:
1. Go to `Configuration > Custom > Extraction`
2. Add a new extractor named "Copy"
3. Select appropriate CSS/XPath selector for your main content area
4. Choose "Extract Text" option
5. Run the crawl with this configuration

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/striking-distance-analysis.git
cd striking-distance-analysis
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser to `http://localhost:8501`

3. Configure your analysis settings in the sidebar:
   - Enter branded terms to exclude (one per line)
   - Set position range (default: 4-20)
   - Define minimum search volume
   - Choose number of top keywords to analyze

4. Upload your CSV files:
   - Google Search Console performance export
   - Screaming Frog internal HTML export

5. Review the analysis results:
   - Summary metrics showing total opportunities
   - Top optimization opportunities with specific recommendations
   - Full report preview
   - Download complete CSV report

## 📊 Output Report Structure

The analysis generates a comprehensive report including:

- **URL**: The page URL
- **Total Clicks**: Sum of clicks from top keywords
- **Keywords in Striking Distance**: Count of qualifying keywords
- **Keyword Data** (for top 10 keywords):
  - Keyword text
  - Click volume
  - Current position
  - Presence in Title (TRUE/FALSE)
  - Presence in H1 (TRUE/FALSE)
  - Presence in Meta Description (TRUE/FALSE)
  - Presence in Copy (TRUE/FALSE)

## 🎯 Optimization Strategy

Use the report to:

1. **Identify Quick Wins**: Focus on keywords missing from key on-page elements
2. **Prioritize by Impact**: Start with high-click keywords in positions 4-10
3. **Natural Integration**: Add missing keywords naturally to titles, H1s, and body copy
4. **Monitor Progress**: Re-run analysis after optimizations to track improvements

## 🛠️ Troubleshooting

### Common Issues

1. **Missing Columns Error**: Ensure your CSV exports contain all required columns
2. **No Results Found**: Check that your position range includes actual keyword rankings
3. **Encoding Issues**: Save CSV files in UTF-8 format
4. **Memory Errors**: For large sites, consider filtering exports to specific sections

### File Format Tips

- Export from GSC in CSV format (not Excel)
- Ensure Screaming Frog export includes indexable pages only
- Remove any special characters from URLs that might cause parsing issues

## 📈 Best Practices

1. **Regular Analysis**: Run monthly to catch new opportunities
2. **Segment by Section**: Analyze different site sections separately for focused insights
3. **Combine with Other Data**: Cross-reference with conversion data for ROI-focused optimization
4. **Track Changes**: Document optimizations made based on recommendations
5. **Competitive Analysis**: Compare your striking distance keywords with competitor rankings

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by SEO best practices and the Python SEO community
- Built with Streamlit for easy deployment and sharing
- Thanks to the open-source community for continuous improvements
