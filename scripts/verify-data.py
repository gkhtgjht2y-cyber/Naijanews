#!/usr/bin/env python3
"""
Verify news data is current
"""

import json
import datetime
import sys

def verify_data():
    """Check data freshness"""
    try:
        with open("api/news.json", "r") as f:
            data = json.load(f)
        
        # Check last updated
        last_updated = data.get("last_updated", "")
        if not last_updated:
            return False
        
        # Check year
        if "2025" not in last_updated:
            print("❌ Data not from 2025")
            return False
        
        # Check articles
        articles = data.get("articles", [])
        if len(articles) < 3:
            print("❌ Too few articles")
            return False
        
        # Check article dates
        current_year = str(datetime.datetime.utcnow().year)
        for article in articles[:5]:
            if current_year not in article.get("published_at", ""):
                print("❌ Article not from current year")
                return False
        
        print("✅ Data verification passed")
        print(f"📅 Last updated: {last_updated[:10]}")
        print(f"📰 Articles: {len(articles)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if verify_data():
        sys.exit(0)
    else:
        sys.exit(1)
