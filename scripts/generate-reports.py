#!/usr/bin/env python3
"""
Generate human-readable reports from processed data
"""

import json
import datetime
from pathlib import Path
import statistics

class ReportGenerator:
    def __init__(self):
        self.data_dir = Path("api/processed")
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_weekly_report(self):
        """Generate a weekly summary report"""
        try:
            with open(self.data_dir / "analytics.json", "r") as f:
                analytics = json.load(f)
            
            with open(self.data_dir / "trending.json", "r") as f:
                trends = json.load(f)
            
            with open(self.data_dir / "sources-stats.json", "r") as f:
                sources = json.load(f)
            
            # Generate markdown report
            report_date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
            
            report = f"""# 📊 Nigeria Economic News Weekly Report
**Report Period**: {report_date}

## 📈 Executive Summary

- **Total Articles Analyzed**: {analytics.get('analytics', {}).get('total_articles', 0)}
- **Overall Sentiment**: {self.get_sentiment_label(analytics.get('analytics', {}).get('avg_sentiment', 0))}
- **Most Active Sources**: {', '.join([s[0] for s in analytics.get('analytics', {}).get('top_sources', [])[:3]])}

## 🔥 Trending Topics This Week

"""
            
            # Add trending topics
            trending = trends.get('trends', {}).get('trending_keywords', [])[:5]
            for i, topic in enumerate(trending, 1):
                report += f"{i}. **{topic['keyword'].title()}** - Mentioned {topic['count']} times (Score: {topic['score']:.2f})\n"
            
            report += "\n## 🏛️ Government Entities in Focus\n\n"
            
            # Add trending entities
            entities = trends.get('trends', {}).get('trending_entities', [])[:5]
            for i, entity in enumerate(entities, 1):
                report += f"{i}. **{entity['entity']}** - Mentioned {entity['count']} times\n"
            
            report += "\n## 📰 Source Performance\n\n"
            report += "| Source | Articles | Dominant Category | Avg Sentiment |\n"
            report += "|--------|----------|-------------------|---------------|\n"
            
            # Add source statistics
            sources_data = sources.get('sources', {})
            for source, data in list(sources_data.items())[:10]:
                articles = data.get('article_count', 0)
                category = data.get('dominant_category', 'general').title()
                sentiment = data.get('avg_sentiment', 0)
                sentiment_label = self.get_sentiment_label(sentiment)
                
                report += f"| {source} | {articles} | {category} | {sentiment_label} |\n"
            
            report += f"\n## 📅 Peak News Hours\n\n"
            
            # Add peak hours
            peak_hours = analytics.get('analytics', {}).get('peak_hours', [])
            for hour_data in peak_hours:
                hour = hour_data.get('hour', 0)
                count = hour_data.get('count', 0)
                report += f"- **{hour:02d}:00**: {count} articles published\n"
            
            report += f"\n## 💡 Insights\n\n"
            
            # Generate insights
            total_articles = analytics.get('analytics', {}).get('total_articles', 0)
            if total_articles > 50:
                report += "- High volume of economic news indicates active market discussions\n"
            
            avg_sentiment = analytics.get('analytics', {}).get('avg_sentiment', 0)
            if avg_sentiment > 0.1:
                report += "- Overall positive sentiment suggests optimistic economic outlook\n"
            elif avg_sentiment < -0.1:
                report += "- Negative sentiment indicates economic concerns among analysts\n"
            
            # Most mentioned economic indicator
            if trending:
                top_topic = trending[0]['keyword']
                report += f"- **{top_topic.title()}** is the most discussed economic indicator\n"
            
            report += f"\n---\n*Report generated automatically on {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n"
            
            # Save report
            report_path = self.reports_dir / f"weekly-report-{report_date}.md"
            with open(report_path, "w") as f:
                f.write(report)
            
            print(f"✅ Weekly report saved: {report_path}")
            
            # Also save JSON version for API
            json_report = {
                "report_date": report_date,
                "total_articles": analytics.get('analytics', {}).get('total_articles', 0),
                "avg_sentiment": analytics.get('analytics', {}).get('avg_sentiment', 0),
                "trending_topics": trending,
                "top_sources": analytics.get('analytics', {}).get('top_sources', [])[:5],
                "insights": self.generate_insights(analytics, trends, sources)
            }
            
            with open(self.reports_dir / "weekly-report.json", "w") as f:
                json.dump(json_report, f, indent=2)
            
            print("✅ JSON report saved")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    def get_sentiment_label(self, score):
        """Convert sentiment score to label"""
        if score > 0.2:
            return "😊 Positive"
        elif score < -0.2:
            return "😟 Negative"
        else:
            return "😐 Neutral"
    
    def generate_insights(self, analytics, trends, sources):
        """Generate automated insights from data"""
        insights = []
        
        total_articles = analytics.get('analytics', {}).get('total_articles', 0)
        avg_sentiment = analytics.get('analytics', {}).get('avg_sentiment', 0)
        
        # Volume insights
        if total_articles > 100:
            insights.append("High volume of economic news indicates active market discussions")
        elif total_articles < 20:
            insights.append("Low news volume may indicate slower economic news cycle")
        
        # Sentiment insights
        if avg_sentiment > 0.3:
            insights.append("Strong positive sentiment suggests optimistic economic outlook")
        elif avg_sentiment < -0.3:
            insights.append("Strong negative sentiment indicates significant economic concerns")
        
        # Source diversity insights
        sources_count = analytics.get('analytics', {}).get('sources_count', 0)
        if sources_count >= 5:
            insights.append(f"Good source diversity with {sources_count} active sources")
        else:
            insights.append(f"Limited source coverage ({sources_count} sources), consider adding more")
        
        # Trending topics insights
        trending = trends.get('trends', {}).get('trending_keywords', [])
        if trending:
            top_topic = trending[0]
            insights.append(f"'{top_topic['keyword'].title()}' is the dominant economic topic")
        
        # Time-based insights
        peak_hours = analytics.get('analytics', {}).get('peak_hours', [])
        if peak_hours:
            peak_hour = max(peak_hours, key=lambda x: x['count'])
            insights.append(f"Peak news publishing hour: {peak_hour['hour']}:00")
        
        return insights
    
    def generate_daily_digest(self):
        """Generate a short daily digest"""
        try:
            with open(Path("api") / "news.json", "r") as f:
                news_data = json.load(f)
            
            today = datetime.datetime.utcnow().date()
            today_articles = []
            
            for article in news_data.get("articles", []):
                pub_date = article.get("published_at", "")
                if pub_date:
                    try:
                        article_date = datetime.datetime.fromisoformat(pub_date).date()
                        if article_date == today:
                            today_articles.append(article)
                    except:
                        continue
            
            if not today_articles:
                print("⚠️ No articles from today found")
                return
            
            # Generate digest
            digest_date = today.strftime("%Y-%m-%d")
            digest = f"""# 📰 Nigeria Economic News Daily Digest
**Date**: {digest_date}
**Total Articles Today**: {len(today_articles)}

## Top Stories Today

"""
            
            # Group by source
            by_source = {}
            for article in today_articles:
                source = article.get("source", "Unknown")
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(article)
            
            for source, articles in by_source.items():
                digest += f"\n### 🏛️ {source}\n\n"
                for i, article in enumerate(articles[:3], 1):
                    title = article.get("title", "No title")
                    summary = article.get("summary", "")[:100] + "..." if len(article.get("summary", "")) > 100 else article.get("summary", "")
                    digest += f"{i}. **{title}**\n"
                    if summary:
                        digest += f"   *{summary}*\n"
                    digest += "\n"
            
            digest += f"\n---\n*Automatically generated on {datetime.datetime.utcnow().strftime('%H:%M UTC')}*\n"
            
            # Save digest
            digest_path = self.reports_dir / f"daily-digest-{digest_date}.md"
            with open(digest_path, "w") as f:
                f.write(digest)
            
            print(f"✅ Daily digest saved: {digest_path}")
            
        except Exception as e:
            print(f"❌ Error generating daily digest: {e}")

if __name__ == "__main__":
    generator = ReportGenerator()
    print("📋 Generating weekly report...")
    generator.generate_weekly_report()
    print("📰 Generating daily digest...")
    generator.generate_daily_digest()
