# Nigeria-news
# 🇳🇬 Nigeria Economic News Aggregator

A free, open-source web application that aggregates Nigerian economic news from multiple sources. Deploys automatically to GitHub Pages.

## 🚀 Live Demo
[https://yourusername.github.io/nigeria-news-aggregator/](https://yourusername.github.io/nigeria-news-aggregator/)

## 📋 Features

- **Real-time News Aggregation**: Fetches from 7+ Nigerian news sources
- **Automatic Updates**: Updates every 4 hours via GitHub Actions
- **Mobile Responsive**: Works perfectly on phones, tablets, and desktops
- **Search & Filter**: Filter by source, category, and time period
- **No Backend Needed**: Runs entirely on GitHub Pages
- **Free Forever**: No hosting costs, no API limits

## 🗞️ Sources

- BusinessDay Nigeria
- Nairametrics
- Central Bank of Nigeria (CBN)
- Premium Times
- The Cable
- Punch Nigeria
- Guardian Nigeria

## 🛠️ Setup Instructions

### Option 1: Fork & Deploy (5 minutes)
1. **Fork this repository** (click Fork button above)
2. **Enable GitHub Pages**:
   - Go to Settings → Pages
   - Source: Deploy from branch
   - Branch: main, folder: / (root)
   - Click Save
3. **Wait 2 minutes** for deployment
4. **Visit**: `https://yourusername.github.io/nigeria-news-aggregator/`

### Option 2: Manual Updates
To update news data manually:
1. Clone the repository
2. Run: `python scripts/fetch-news.py`
3. Commit and push changes

## 🔧 Customization

### Add New Sources
Edit `api/sources.json`:

```json
{
  "name": "New Source Name",
  "url": "https://example.com/feed/",
  "category": "business",
  "type": "rss",
  "icon": "newspaper",
  "description": "Source description"
}
