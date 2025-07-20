# 🎯 Striking Distance On-Page Analysis Tool (AI-Powered)

This advanced SEO tool uses **crawl4ai** to extract clean, SEO-relevant content directly from URLs, eliminating the need for Screaming Frog exports. It cross-references Google Search Console data with AI-powered content extraction to identify keyword optimization opportunities.

## 🚀 Key Features

- **AI-Powered Content Extraction**: Uses state-of-the-art crawl4ai to extract clean content (removes nav, footer, ads, etc.)
- **No Screaming Frog Required**: Direct URL crawling with intelligent content filtering
- **Smart Keyword Matching**: Advanced keyword detection with variations and plural forms
- **Real-time Progress Tracking**: Live crawling progress with detailed status updates
- **Comprehensive Analysis**: Checks keywords against Title, Meta Description, H1, H2, and Body content
- **Flexible Filtering**: Branded term exclusion and URL filtering capabilities

## 📋 Requirements

- Python 3.8+
- Google Search Console performance report (CSV/Excel)
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

3. **Install crawl4ai** (if not included in requirements):
   ```bash
   pip install crawl4ai
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 📊 How to Use

### 1. Prepare Your Google Search Console Data
Export a performance report from GSC with these columns:
- **Query** - The search term/keyword
- **Landing Page** (or Address/URL) - The URL that appeared in search
- **Clicks** - Number of clicks received
- **Position** - Average ranking position (optional but recommended)

### 2. Configure Settings
- **Branded Terms**: Enter terms to exclude (one per line)
- **URL Exclusions**: Enter exact URLs to exclude
- **Top Keywords**: Set how many keywords to analyze per URL
- **crawl4ai Settings**: Adjust caching, headless mode, and timeout

### 3. Upload & Analyze
1. Upload your GSC file
2. Click "Start Analysis"
3. Watch real-time crawling progress
4. Download your comprehensive report

## 🔍 What Gets Analyzed

The tool checks each keyword against:
- **Title Tag**: Page title
- **Meta Description**: SEO description
- **H1 Heading**: Primary heading
- **H2 Subheadings**: All H2 tags combined
- **Body Content**: Clean, main content (excluding nav, footer, ads)

## 🎯 Understanding the Results

### Striking Distance Keywords
Keywords ranking in positions 4-20 where small optimizations can lead to significant traffic gains.

### Report Columns
- **URL**: The analyzed page
- **Keyword**: The search query
- **Clicks**: Current clicks from GSC
- **Position**: Current ranking position
- **In Title/Meta/H1/H2/Body**: Boolean indicators showing keyword presence

### Optimization Opportunities
- **Missing in Title**: Add keyword to page title
- **Missing in Meta**: Include keyword in meta description
- **Missing in H1**: Use keyword in main heading
- **Missing in H2**: Add keyword to subheadings
- **Missing in Body**: Naturally incorporate keyword in content

## ⚙️ crawl4ai Configuration

### Content Filtering
The tool automatically excludes:
- Navigation menus
- Footer content
- Sidebar widgets
- Advertisements
- Social media links
- Comments sections
- Related posts

### Performance Settings
- **Cache Mode**: Speeds up repeated crawls
- **Headless Mode**: Runs browser without GUI
- **Timeout**: Maximum wait time per URL

## 🐛 Troubleshooting

### Common Issues

**crawl4ai not installed**:
```bash
pip install crawl4ai
```

**Browser issues**:
- Ensure Chrome/Chromium is installed
- Try disabling headless mode in settings

**Failed URL crawls**:
- Check if URLs are accessible
- Verify robots.txt allows crawling
- Increase timeout in settings

**File format issues**:
- Save Excel files as CSV for better compatibility
- Ensure required columns are present

### Performance Tips
- Use cache mode for repeated analyses
- Start with a smaller dataset for testing
- Exclude low-value URLs to speed up crawling

## 📈 Example Workflow

1. **Export GSC Data**: 30-day performance report
2. **Filter**: Exclude branded terms and parameter URLs
3. **Analyze**: 500 URLs with 5,000 keywords
4. **Optimize**: Focus on keywords with 100+ clicks in positions 8-15
5. **Track**: Monitor improvements in GSC after optimization

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the tool.

## 📄 License

This project is open source and available under the MIT License.
