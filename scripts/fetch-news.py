#!/usr/bin/env python3
"""
Script to fetch Nigerian economic news and update the GitHub repository
Run this locally or via GitHub Actions
"""

import feedparser
import json
import datetime
import os
from pathlib import Path

def fetch_rss_feed(url, source_name):
    """Fetch and parse RSS feed"""
    try:
        feed = feedparser.parse(url)
        articles = []
        
        for entry in feed.entries[:15]:  # Get latest 15
            article = {
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "summary": entry.get("summary", "")[:200],
                "source": source_name,
                "published_at": entry.get("published", datetime.datetime.utcnow().isoformat()),
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            articles.append(article)
        
        return articles
    except Exception as e:
        print(f"Error fetching {source_name}: {e}")
        return []

def main():
    # Define sources
    sources = [
        {"name": "BusinessDay Nigeria", "url": "https://businessday.ng/category/business-economy/feed/", "category": "business"},
        {"name": "Nairametrics", "url": "https://nairametrics.com/feed/", "category": "economic_analysis"},
        {"name": "Central Bank of Nigeria", "url": "https://www.cbn.gov.ng/rss/cbnnews.asp", "category": "monetary_policy"},
        {"name": "Premium Times", "url": "https://www.premiumtimesng.com/feed/", "category": "general"},
        {"name": "The Cable", "url": "https://www.thecable.ng/feed", "category": "politics_economy"},
    ]
    
    all_articles = []
    
    # Fetch from all sources
    for source in sources:
        print(f"Fetching from {source['name']}...")
        articles = fetch_rss_feed(source["url"], source["name"])
        
        # Add category
        for article in articles:
            article["category"] = source["category"]
        
        all_articles.extend(articles)
        print(f"  Found {len(articles)} articles")
    
    # Create output directory
    api_dir = Path("api")
    api_dir.mkdir(exist_ok=True)
    
    # Save articles
    news_data = {
        "last_updated": datetime.datetime.utcnow().isoformat(),
        "articles": all_articles
    }
    
    with open(api_dir / "news.json", "w") as f:
        json.dump(news_data, f, indent=2)
    
    # Save update timestamp
    with open(api_dir / "update.txt", "w") as f:
        f.write(datetime.datetime.utcnow().isoformat())
    
    print(f"\n✅ Successfully fetched {len(all_articles)} articles")
    print(f"📁 Data saved to {api_dir}/")

if __name__ == "__main__":
    main()
