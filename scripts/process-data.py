#!/usr/bin/env python3
"""
Advanced data processor for Nigerian economic news
- Sentiment analysis
- Trend detection
- Entity extraction
- Analytics generation
"""

import json
import datetime
from collections import Counter, defaultdict
import re
from pathlib import Path
import statistics

class NigeriaNewsProcessor:
    def __init__(self):
        self.data_dir = Path("api")
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        
        # Economic keywords with weights
        self.economic_indicators = {
            "inflation": {"weight": 10, "sentiment": -1},
            "growth": {"weight": 8, "sentiment": 1},
            "naira": {"weight": 9, "sentiment": 0},
            "dollar": {"weight": 9, "sentiment": 0},
            "CBN": {"weight": 8, "sentiment": 0},
            "interest rate": {"weight": 7, "sentiment": -1},
            "GDP": {"weight": 9, "sentiment": 0},
            "unemployment": {"weight": 7, "sentiment": -1},
            "budget": {"weight": 6, "sentiment": 0},
            "debt": {"weight": 6, "sentiment": -1},
            "oil": {"weight": 8, "sentiment": 0},
            "crude": {"weight": 8, "sentiment": 0},
            "export": {"weight": 6, "sentiment": 1},
            "import": {"weight": 6, "sentiment": -1},
            "trade": {"weight": 6, "sentiment": 0},
        }
        
        # Government entities
        self.government_entities = [
            "CBN", "Central Bank", "NNPC", "NDIC", "NBS", "DMO",
            "Finance Ministry", "Budget Office", "FIRS", "Customs"
        ]
        
    def load_articles(self):
        """Load raw articles from news.json"""
        try:
            with open(self.data_dir / "news.json", "r") as f:
                data = json.load(f)
            return data.get("articles", [])
        except FileNotFoundError:
            print("❌ news.json not found")
            return []
    
    def analyze_sentiment(self, text):
        """Simple sentiment analysis without external APIs"""
        text_lower = text.lower()
        
        # Positive indicators
        positive_words = [
            'growth', 'increase', 'rise', 'gain', 'profit', 'surplus',
            'recovery', 'improve', 'strong', 'bullish', 'optimistic',
            'positive', 'outperform', 'beat', 'exceed', 'record',
            'achievement', 'success', 'boom', 'expansion'
        ]
        
        # Negative indicators
        negative_words = [
            'decline', 'fall', 'drop', 'loss', 'deficit', 'recession',
            'worsen', 'weak', 'bearish', 'pessimistic', 'negative',
            'underperform', 'miss', 'below', 'crisis', 'slump',
            'inflation', 'debt', 'default', 'corruption'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate sentiment score (-1 to 1)
        total = positive_count + negative_count
        if total == 0:
            return 0
        
        sentiment = (positive_count - negative_count) / total
        
        # Categorize
        if sentiment > 0.2:
            return {"score": sentiment, "label": "positive", "confidence": min(abs(sentiment), 0.8)}
        elif sentiment < -0.2:
            return {"score": sentiment, "label": "negative", "confidence": min(abs(sentiment), 0.8)}
        else:
            return {"score": sentiment, "label": "neutral", "confidence": 0.5}
    
    def extract_economic_data(self, text):
        """Extract economic indicators and numbers from text"""
        patterns = {
            "inflation_rate": r'inflation.*?(\d+\.?\d*)\s*%',
            "policy_rate": r'MPR.*?(\d+\.?\d*)\s*%|policy rate.*?(\d+\.?\d*)\s*%',
            "exchange_rate": r'(\d+\.?\d*)\s*(?:naira|NGN)\s*(?:per|to)\s*(?:dollar|USD)',
            "gdp_growth": r'GDP.*?growth.*?(\d+\.?\d*)\s*%',
            "budget_amount": r'budget.*?₦\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:trillion|billion|million)?',
            "oil_price": r'oil.*?\$(\d+\.?\d*)|crude.*?\$(\d+\.?\d*)',
            "unemployment_rate": r'unemployment.*?(\d+\.?\d*)\s*%',
            "debt_amount": r'debt.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:trillion|billion|million)',
        }
        
        extracted = {}
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Flatten tuple matches and get first non-empty
                flat_matches = [m for match in matches for m in match if m]
                if flat_matches:
                    try:
                        # Clean number (remove commas)
                        clean_num = flat_matches[0].replace(',', '')
                        extracted[key] = float(clean_num)
                    except:
                        extracted[key] = flat_matches[0]
        
        return extracted
    
    def detect_trends(self, articles):
        """Detect trending topics and entities"""
        # Collect keywords from recent articles (last 24 hours)
        now = datetime.datetime.utcnow()
        recent_articles = [
            a for a in articles 
            if (now - datetime.datetime.fromisoformat(a.get('published_at', now.isoformat()))).days < 1
        ]
        
        # Analyze word frequencies
        word_counts = Counter()
        entity_counts = Counter()
        
        for article in recent_articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            
            # Count economic keywords
            for keyword in self.economic_indicators:
                if keyword in text:
                    word_counts[keyword] += 1
            
            # Count government entities
            for entity in self.government_entities:
                if entity.lower() in text:
                    entity_counts[entity] += 1
        
        # Calculate trend scores (normalize by total articles)
        total_recent = len(recent_articles)
        trending_keywords = [
            {
                "keyword": kw,
                "count": count,
                "score": count / max(total_recent, 1),
                "weight": self.economic_indicators.get(kw, {}).get("weight", 1)
            }
            for kw, count in word_counts.most_common(10)
        ]
        
        trending_entities = [
            {
                "entity": entity,
                "count": count,
                "score": count / max(total_recent, 1)
            }
            for entity, count in entity_counts.most_common(10)
        ]
        
        return {
            "trending_keywords": trending_keywords,
            "trending_entities": trending_entities,
            "total_recent_articles": total_recent,
            "analysis_time": now.isoformat()
        }
    
    def generate_analytics(self, articles):
        """Generate comprehensive analytics"""
        if not articles:
            return {}
        
        # Time-based analysis
        articles_by_hour = defaultdict(int)
        articles_by_source = Counter()
        articles_by_category = Counter()
        
        sentiment_scores = []
        article_lengths = []
        
        for article in articles:
            # Publication hour distribution
            try:
                pub_time = datetime.datetime.fromisoformat(article.get('published_at', ''))
                articles_by_hour[pub_time.hour] += 1
            except:
                pass
            
            # Source distribution
            articles_by_source[article.get('source', 'Unknown')] += 1
            
            # Category distribution
            articles_by_category[article.get('category', 'general')] += 1
            
            # Sentiment analysis
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            sentiment = self.analyze_sentiment(text)
            sentiment_scores.append(sentiment["score"])
            
            # Article length
            article_lengths.append(len(text))
        
        # Calculate statistics
        avg_sentiment = statistics.mean(sentiment_scores) if sentiment_scores else 0
        avg_length = statistics.mean(article_lengths) if article_lengths else 0
        
        # Most productive hours
        top_hours = sorted(articles_by_hour.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Sentiment distribution
        sentiment_dist = {
            "positive": len([s for s in sentiment_scores if s > 0.2]),
            "neutral": len([s for s in sentiment_scores if -0.2 <= s <= 0.2]),
            "negative": len([s for s in sentiment_scores if s < -0.2])
        }
        
        return {
            "total_articles": len(articles),
            "avg_sentiment": avg_sentiment,
            "avg_article_length": avg_length,
            "top_sources": articles_by_source.most_common(5),
            "top_categories": articles_by_category.most_common(5),
            "peak_hours": [{"hour": h, "count": c} for h, c in top_hours],
            "sentiment_distribution": sentiment_dist,
            "sources_count": len(articles_by_source),
            "categories_count": len(articles_by_category),
            "analysis_period": {
                "start": min([a.get('published_at') for a in articles if a.get('published_at')], default=""),
                "end": max([a.get('published_at') for a in articles if a.get('published_at')], default="")
            }
        }
    
    def process_sources_stats(self, articles):
        """Generate statistics for each news source"""
        sources_data = {}
        
        for article in articles:
            source = article.get('source', 'Unknown')
            if source not in sources_data:
                sources_data[source] = {
                    "count": 0,
                    "categories": Counter(),
                    "sentiments": [],
                    "avg_length": [],
                    "latest_article": ""
                }
            
            source_data = sources_data[source]
            source_data["count"] += 1
            
            # Track categories
            source_data["categories"][article.get('category', 'general')] += 1
            
            # Track sentiment
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            sentiment = self.analyze_sentiment(text)
            source_data["sentiments"].append(sentiment["score"])
            
            # Track article length
            source_data["avg_length"].append(len(text))
            
            # Track latest article
            article_time = article.get('published_at', '')
            if article_time > source_data["latest_article"]:
                source_data["latest_article"] = article_time
        
        # Calculate averages and format
        formatted_sources = {}
        for source, data in sources_data.items():
            avg_sentiment = statistics.mean(data["sentiments"]) if data["sentiments"] else 0
            avg_length = statistics.mean(data["avg_length"]) if data["avg_length"] else 0
            
            formatted_sources[source] = {
                "article_count": data["count"],
                "dominant_category": data["categories"].most_common(1)[0][0] if data["categories"] else "general",
                "category_distribution": dict(data["categories"]),
                "avg_sentiment": avg_sentiment,
                "sentiment_label": "positive" if avg_sentiment > 0.2 else "negative" if avg_sentiment < -0.2 else "neutral",
                "avg_article_length": avg_length,
                "latest_article": data["latest_article"],
                "update_frequency": self.calculate_update_frequency(data["latest_article"], data["count"])
            }
        
        return formatted_sources
    
    def calculate_update_frequency(self, latest_article, article_count):
        """Calculate how frequently a source updates"""
        if not latest_article or article_count < 2:
            return "unknown"
        
        try:
            latest = datetime.datetime.fromisoformat(latest_article)
            now = datetime.datetime.utcnow()
            hours_since_last = (now - latest).total_seconds() / 3600
            
            if hours_since_last < 2:
                return "very_frequent"
            elif hours_since_last < 6:
                return "frequent"
            elif hours_since_last < 24:
                return "daily"
            else:
                return "infrequent"
        except:
            return "unknown"
    
    def process_all(self):
        """Main processing pipeline"""
        print("🔄 Starting data processing...")
        
        # Load articles
        articles = self.load_articles()
        print(f"📄 Loaded {len(articles)} articles")
        
        if not articles:
            print("❌ No articles to process")
            return
        
        # Process each article with enhanced data
        processed_articles = []
        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            
            enhanced = article.copy()
            
            # Add sentiment analysis
            enhanced["sentiment_analysis"] = self.analyze_sentiment(text)
            
            # Extract economic data
            enhanced["extracted_data"] = self.extract_economic_data(text)
            
            # Add keyword matches
            matched_keywords = []
            for keyword in self.economic_indicators:
                if keyword.lower() in text.lower():
                    matched_keywords.append(keyword)
            enhanced["matched_keywords"] = matched_keywords
            
            # Add entity matches
            matched_entities = []
            for entity in self.government_entities:
                if entity.lower() in text.lower():
                    matched_entities.append(entity)
            enhanced["matched_entities"] = matched_entities
            
            # Calculate relevance score
            relevance = len(matched_keywords) * 0.3 + len(matched_entities) * 0.2
            enhanced["relevance_score"] = min(relevance, 1.0)
            
            processed_articles.append(enhanced)
        
        # Generate analytics
        print("📊 Generating analytics...")
        analytics = self.generate_analytics(articles)
        
        # Detect trends
        print("📈 Detecting trends...")
        trends = self.detect_trends(articles)
        
        # Process source statistics
        print("🏛️ Analyzing sources...")
        sources_stats = self.process_sources_stats(articles)
        
        # Save processed data
        self.save_processed_data(
            processed_articles=processed_articles,
            analytics=analytics,
            trends=trends,
            sources_stats=sources_stats
        )
        
        print("✅ Data processing complete!")
    
    def save_processed_data(self, processed_articles, analytics, trends, sources_stats):
        """Save all processed data to files"""
        
        # Save enhanced articles
        with open(self.processed_dir / "articles-enhanced.json", "w") as f:
            json.dump({
                "processed_at": datetime.datetime.utcnow().isoformat(),
                "articles": processed_articles
            }, f, indent=2, default=str)
        
        # Save analytics
        with open(self.processed_dir / "analytics.json", "w") as f:
            json.dump({
                "generated_at": datetime.datetime.utcnow().isoformat(),
                "analytics": analytics
            }, f, indent=2, default=str)
        
        # Save trends
        with open(self.processed_dir / "trending.json", "w") as f:
            json.dump({
                "generated_at": datetime.datetime.utcnow().isoformat(),
                "trends": trends
            }, f, indent=2, default=str)
        
        # Save source statistics
        with open(self.processed_dir / "sources-stats.json", "w") as f:
            json.dump({
                "generated_at": datetime.datetime.utcnow().isoformat(),
                "sources": sources_stats
            }, f, indent=2, default=str)
        
        # Create a summary file
        summary = {
            "processing_completed": datetime.datetime.utcnow().isoformat(),
            "total_articles_processed": len(processed_articles),
            "analytics_summary": {
                "avg_sentiment": analytics.get("avg_sentiment", 0),
                "top_sources": analytics.get("top_sources", []),
                "trending_keywords": trends.get("trending_keywords", [])[:3]
            }
        }
        
        with open(self.processed_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)

if __name__ == "__main__":
    processor = NigeriaNewsProcessor()
    processor.process_all()
