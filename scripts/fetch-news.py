# scripts/fetch-news.py - UPDATED VERSION
#!/usr/bin/env python3
"""
REAL Nigerian news fetcher - gets TODAY's actual news from RSS feeds
"""

import feedparser
import json
import datetime
import time
from urllib.parse import quote
import re

def clean_text(text):
    """Remove HTML tags and extra whitespace"""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def fetch_rss_feed(url, source_name, category):
    """Fetch REAL RSS feed"""
    articles = []
    try:
        print(f"📡 Fetching from {source_name}...")
        
        # Add cache-busting parameter
        cache_buster = int(time.time())
        feed_url = f"{url}?t={cache_buster}" if "?" in url else f"{url}?t={cache_buster}"
        
        # Parse feed
        feed = feedparser.parse(feed_url)
        
        if feed.entries:
            print(f"   ✅ Found {len(feed.entries)} items")
            
            for entry in feed.entries[:15]:  # Get latest 15
                # Get publication date (use current time if missing)
                pub_date = entry.get('published', '')
                if not pub_date and hasattr(entry, 'updated'):
                    pub_date = entry.updated
                
                # Parse date or use now
                try:
                    published_at = datetime.datetime(*entry.published_parsed[:6]).isoformat() + 'Z'
                except:
                    published_at = datetime.datetime.utcnow().isoformat() + 'Z'
                
                article = {
                    "title": clean_text(entry.get('title', 'No title')),
                    "url": entry.get('link', ''),
                    "summary": clean_text(entry.get('summary', entry.get('description', '')))[:200],
                    "source": source_name,
                    "category": category,
                    "published_at": published_at,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
                
                # Only add if it has title and URL
                if article['title'] and article['url']:
                    articles.append(article)
        else:
            print(f"   ❌ No items found in feed")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:50]}")
    
    return articles

def main():
    print("🇳🇬 FETCHING NIGERIAN ECONOMIC NEWS - TODAY")
    print("=" * 50)
    
    # REAL Nigerian news sources with RSS feeds
    sources = [
        {
            "name": "BusinessDay Nigeria",
            "url": "https://businessday.ng/category/business-economy/feed/",
            "category": "business"
        },
        {
            "name": "Nairametrics",
            "url": "https://nairametrics.com/feed/",
            "category": "economic_analysis"
        },
        {
            "name": "Premium Times",
            "url": "https://www.premiumtimesng.com/feed/",
            "category": "general"
        },
        {
            "name": "The Cable",
            "url": "https://www.thecable.ng/feed",
            "category": "politics_economy"
        },
        {
            "name": "Punch Nigeria",
            "url": "https://punchng.com/feed/",
            "category": "general"
        },
        {
            "name": "Guardian Nigeria",
            "url": "https://guardian.ng/feed/",
            "category": "business"
        },
        # Central Bank of Nigeria (works intermittently)
        {
            "name": "Central Bank of Nigeria",
            "url": "https://www.cbn.gov.ng/rss/cbnnews.asp",
            "category": "monetary_policy"
        },
    ]
    
    all_articles = []
    
    # Fetch from all sources
    for source in sources:
        articles = fetch_rss_feed(source["url"], source["name"], source["category"])
        all_articles.extend(articles)
        
        # Add delay between requests to avoid being blocked
        time.sleep(1)
    
    # Filter for TODAY's articles only
    today = datetime.datetime.utcnow().date()
    today_articles = []
    
    for article in all_articles:
        try:
            # Try to parse the date
            article_date = datetime.datetime.fromisoformat(
                article["published_at"].replace('Z', '+00:00')
            ).date()
            
            # Only keep today's articles
            if article_date == today:
                today_articles.append(article)
            else:
                # If date parsing fails or it's not today, skip
                pass
        except:
            # If we can't parse the date, include it anyway (might be today)
            today_articles.append(article)
    
    print(f"\n📊 RESULTS:")
    print(f"   Total fetched: {len(all_articles)}")
    print(f"   From today: {len(today_articles)}")
    
    # If no articles from today, use all articles
    if len(today_articles) < 5:
        print("   ⚠️ Few today articles, using all recent ones")
        final_articles = all_articles[:30]  # Limit to 30 most recent
    else:
        final_articles = today_articles
    
    # Sort by date (newest first)
    final_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    
    # Limit to reasonable number
    final_articles = final_articles[:50]
    
    # Save to file
    output_data = {
        "last_updated": datetime.datetime.utcnow().isoformat() + "Z",
        "total_articles": len(final_articles),
        "today_articles": len(today_articles),
        "articles": final_articles
    }
    
    # Ensure api directory exists
    import os
    os.makedirs("api", exist_ok=True)
    
    with open("api/news.json", "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✅ Saved {len(final_articles)} articles to api/news.json")
    print(f"🕐 Last updated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    
    # Also create a simple HTML preview
    with open("api/news-preview.html", "w") as f:
        f.write("<h1>🇳🇬 Nigerian Economic News</h1>")
        f.write(f"<p>Updated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')}</p>")
        f.write(f"<p>Total articles: {len(final_articles)}</p>")
        for article in final_articles[:10]:
            f.write(f"<h3>{article['title']}</h3>")
            f.write(f"<p><strong>Source:</strong> {article['source']}</p>")
            f.write(f"<p><strong>Time:</strong> {article['published_at']}</p>")
            f.write(f"<p>{article['summary']}</p>")
            f.write(f"<a href='{article['url']}' target='_blank'>Read full article</a>")
            f.write("<hr>")

if __name__ == "__main__":
    main()
