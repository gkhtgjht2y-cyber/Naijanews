#!/bin/bash
# Complete update script - fetches and processes data

echo "🚀 Starting complete Nigeria news update..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Step 1: Fetch new articles
echo "📡 Fetching new articles..."
python3 scripts/fetch-news.py

# Step 2: Process data
echo "🔄 Processing data..."
python3 scripts/process-data.py

# Step 3: Generate reports
echo "📊 Generating reports..."
python3 scripts/generate-reports.py

# Step 4: Archive old data (keep last 30 days)
echo "🗄️ Archiving old data..."
ARCHIVE_DIR="data/$(date +%Y)/$(date +%m)"
mkdir -p "$ARCHIVE_DIR"
cp api/news.json "$ARCHIVE_DIR/news-$(date +%Y%m%d-%H%M).json"

# Keep only last 30 archives
find data -name "news-*.json" -type f | sort -r | tail -n +31 | xargs rm -f

echo "✅ Update complete!"
echo "📊 Statistics:"
echo "  - Articles in api/news.json: $(jq '.articles | length' api/news.json)"
echo "  - Processed files in api/processed/: $(ls -1 api/processed/ | wc -l)"
echo "  - Reports generated: $(ls -1 reports/ | wc -l)"
