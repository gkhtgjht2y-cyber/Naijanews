// Nigeria Economic News Aggregator - Frontend
const NewsApp = {
    config: {
        apiBase: 'api', // GitHub Pages API folder
        sources: [],
        articles: [],
        filters: {
            source: 'all',
            category: 'all',
            time: 'all',
            search: ''
        }
    },

    // Initialize the application
    init: function() {
        console.log('🇳🇬 Nigeria Economic News Aggregator Initializing...');
        
        // Load data
        this.loadData();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Set up auto-refresh (every 5 minutes)
        setInterval(() => this.loadData(), 5 * 60 * 1000);
    },

    // Load news data from JSON files
    loadData: async function() {
        try {
            // Show loading state
            this.showLoading(true);
            
            // Load multiple JSON files in parallel
            const [newsResponse, sourcesResponse, updateResponse] = await Promise.allSettled([
                fetch(`${this.config.apiBase}/news.json?t=${Date.now()}`),
                fetch(`${this.config.apiBase}/sources.json?t=${Date.now()}`),
                fetch(`${this.config.apiBase}/update.txt?t=${Date.now()}`)
            ]);
            
            // Process news data
            if (newsResponse.status === 'fulfilled' && newsResponse.value.ok) {
                const newsData = await newsResponse.value.json();
                this.config.articles = newsData.articles || [];
                this.config.lastUpdate = newsData.last_updated || new Date().toISOString();
            }
            
            // Process sources data
            if (sourcesResponse.status === 'fulfilled' && sourcesResponse.value.ok) {
                const sourcesData = await sourcesResponse.value.json();
                this.config.sources = sourcesData.sources || [];
            }
            
            // Process update timestamp
            if (updateResponse.status === 'fulfilled' && updateResponse.value.ok) {
                const updateTime = await updateResponse.value.text();
                this.config.lastUpdate = updateTime.trim();
            }
            
            // Update UI
            this.updateStats();
            this.updateSourcesDropdown();
            this.displaySources();
            this.applyFilters();
            
            // Update timestamp display
            this.updateLastUpdated();
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load news data. Please try again.');
        } finally {
            this.showLoading(false);
        }
    },

    // Update statistics display
    updateStats: function() {
        const totalArticles = this.config.articles.length;
        const totalSources = this.config.sources.length;
        
        // Calculate today's articles
        const today = new Date().toDateString();
        const todayArticles = this.config.articles.filter(article => {
            const articleDate = new Date(article.published_at || article.timestamp).toDateString();
            return articleDate === today;
        }).length;
        
        // Update DOM
        document.getElementById('totalArticles').textContent = totalArticles.toLocaleString();
        document.getElementById('totalSources').textContent = totalSources;
        document.getElementById('todayArticles').textContent = todayArticles;
        document.getElementById('lastUpdateTime').textContent = this.formatTime(this.config.lastUpdate);
        
        // Update footer
        document.getElementById('articleCount').textContent = totalArticles;
        document.getElementById('sourceCount').textContent = totalSources;
        document.getElementById('updateTimestamp').textContent = this.formatTime(this.config.lastUpdate);
    },

    // Update sources dropdown
    updateSourcesDropdown: function() {
        const sourceFilter = document.getElementById('sourceFilter');
        
        // Clear existing options (keeping "All Sources")
        while (sourceFilter.options.length > 1) {
            sourceFilter.remove(1);
        }
        
        // Add unique sources
        const uniqueSources = [...new Set(this.config.sources.map(s => s.name))];
        uniqueSources.sort();
        
        uniqueSources.forEach(source => {
            const option = document.createElement('option');
            option.value = source;
            option.textContent = source;
            sourceFilter.appendChild(option);
        });
    },

    // Display sources in the sources section
    displaySources: function() {
        const sourcesList = document.getElementById('sourcesList');
        
        if (this.config.sources.length === 0) {
            sourcesList.innerHTML = '<p class="no-sources">No sources configured</p>';
            return;
        }
        
        sourcesList.innerHTML = this.config.sources.map(source => `
            <div class="source-card">
                <div class="source-icon">
                    <i class="fas fa-${source.icon || 'newspaper'}"></i>
                </div>
                <div class="source-info">
                    <h4>${source.name}</h4>
                    <p>${source.category} • ${source.type}</p>
                    ${source.description ? `<small>${source.description}</small>` : ''}
                </div>
            </div>
        `).join('');
    },

    // Apply filters and display articles
    applyFilters: function() {
        let filteredArticles = [...this.config.articles];
        
        // Apply source filter
        if (this.config.filters.source !== 'all') {
            filteredArticles = filteredArticles.filter(article => 
                article.source === this.config.filters.source
            );
        }
        
        // Apply category filter
        if (this.config.filters.category !== 'all') {
            filteredArticles = filteredArticles.filter(article => 
                article.category === this.config.filters.category
            );
        }
        
        // Apply time filter
        if (this.config.filters.time !== 'all') {
            const now = new Date();
            filteredArticles = filteredArticles.filter(article => {
                const articleDate = new Date(article.published_at || article.timestamp);
                
                switch (this.config.filters.time) {
                    case 'today':
                        return articleDate.toDateString() === now.toDateString();
                    case 'week':
                        const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);
                        return articleDate >= weekAgo;
                    case 'month':
                        const monthAgo = new Date(now);
                        monthAgo.setMonth(monthAgo.getMonth() - 1);
                        return articleDate >= monthAgo;
                    default:
                        return true;
                }
            });
        }
        
        // Apply search filter
        if (this.config.filters.search.trim()) {
            const searchTerm = this.config.filters.search.toLowerCase();
            filteredArticles = filteredArticles.filter(article => 
                article.title.toLowerCase().includes(searchTerm) ||
                (article.summary && article.summary.toLowerCase().includes(searchTerm)) ||
                (article.content && article.content.toLowerCase().includes(searchTerm))
            );
        }
        
        // Sort by date (newest first)
        filteredArticles.sort((a, b) => {
            const dateA = new Date(a.published_at || a.timestamp);
            const dateB = new Date(b.published_at || b.timestamp);
            return dateB - dateA;
        });
        
        // Display filtered articles
        this.displayArticles(filteredArticles);
    },

    // Display articles in the grid
    displayArticles: function(articles) {
        const newsContainer = document.getElementById('newsContainer');
        const noResults = document.getElementById('noResults');
        
        if (articles.length === 0) {
            newsContainer.innerHTML = '';
            noResults.style.display = 'block';
            return;
        }
        
        noResults.style.display = 'none';
        
        newsContainer.innerHTML = articles.map(article => `
            <div class="news-card">
                <div class="news-card-header">
                    <div class="news-source">
                        <i class="fas fa-newspaper"></i>
                        ${article.source}
                        ${article.category ? `<span class="category-badge">${article.category}</span>` : ''}
                    </div>
                    <a href="${article.url}" target="_blank" class="news-title" title="${article.title}">
                        ${this.truncateText(article.title, 80)}
                    </a>
                    <div class="news-meta">
                        <div class="news-time">
                            <i class="far fa-clock"></i>
                            ${this.formatRelativeTime(article.published_at || article.timestamp)}
                        </div>
                        ${article.sentiment ? `
                            <span class="sentiment-badge sentiment-${article.sentiment}">
                                ${article.sentiment}
                            </span>
                        ` : ''}
                    </div>
                </div>
                <div class="news-card-body">
                    <p class="news-summary">
                        ${this.truncateText(article.summary || article.description || '', 150)}
                    </p>
                    ${article.keywords && article.keywords.length > 0 ? `
                        <div class="news-keywords">
                            ${article.keywords.slice(0, 3).map(keyword => 
                                `<span class="keyword">${keyword}</span>`
                            ).join('')}
                        </div>
                    ` : ''}
                    <div class="news-actions" style="margin-top: 15px;">
                        <a href="${article.url}" target="_blank" class="btn btn-secondary" style="font-size: 0.85rem; padding: 8px 15px;">
                            <i class="fas fa-external-link-alt"></i> Read Full Article
                        </a>
                        <button class="btn btn-secondary" style="font-size: 0.85rem; padding: 8px 15px;" onclick="NewsApp.bookmarkArticle('${article.url}')">
                            <i class="far fa-bookmark"></i> Bookmark
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    },

    // Setup event listeners
    setupEventListeners: function() {
        // Filter changes
        document.getElementById('sourceFilter').addEventListener('change', (e) => {
            this.config.filters.source = e.target.value;
            this.applyFilters();
        });
        
        document.getElementById('categoryFilter').addEventListener('change', (e) => {
            this.config.filters.category = e.target.value;
            this.applyFilters();
        });
        
        document.getElementById('timeFilter').addEventListener('change', (e) => {
            this.config.filters.time = e.target.value;
            this.applyFilters();
        });
        
        // Search
        document.getElementById('searchBtn').addEventListener('click', () => {
            this.config.filters.search = document.getElementById('searchInput').value;
            this.applyFilters();
        });
        
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.config.filters.search = e.target.value;
                this.applyFilters();
            }
        });
        
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadData();
        });
        
        // Export button
        document.getElementById('exportBtn').addEventListener('click', (e) => {
            e.preventDefault();
            this.exportData();
        });
        
        // Bookmark page button
        document.getElementById('bookmarkBtn').addEventListener('click', (e) => {
            e.preventDefault();
            this.bookmarkPage();
        });
        
        // Pull to refresh (for mobile)
        let touchStartY = 0;
        document.addEventListener('touchstart', (e) => {
            touchStartY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            const touchEndY = e.changedTouches[0].clientY;
            if (touchStartY - touchEndY > 100) {
                // Pull down to refresh
                this.loadData();
            }
        }, { passive: true });
    },

    // Utility functions
    formatRelativeTime: function(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 60) {
            return `${diffMins}m ago`;
        } else if (diffHours < 24) {
            return `${diffHours}h ago`;
        } else if (diffDays < 7) {
            return `${diffDays}d ago`;
        } else {
            return date.toLocaleDateString();
        }
    },

    formatTime: function(dateString) {
        if (!dateString) return '--:--';
        const date = new Date(dateString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },

    truncateText: function(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    updateLastUpdated: function() {
        const lastUpdatedEl = document.getElementById('lastUpdated');
        if (this.config.lastUpdate) {
            lastUpdatedEl.textContent = `Updated ${this.formatRelativeTime(this.config.lastUpdate)}`;
        }
    },

    showLoading: function(show) {
        const loadingEl = document.getElementById('loading');
        const newsContainer = document.getElementById('newsContainer');
        
        if (show) {
            loadingEl.style.display = 'block';
            newsContainer.style.opacity = '0.5';
        } else {
            loadingEl.style.display = 'none';
            newsContainer.style.opacity = '1';
        }
    },

    showError: function(message) {
        // Create error toast
        const toast = document.createElement('div');
        toast.className = 'error-toast';
        toast.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
        `;
        
        // Style the toast
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #fed7d7;
            color: #742a2a;
            padding: 15px 20px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            max-width: 400px;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    },

    bookmarkArticle: function(url) {
        // Simple bookmark using localStorage
        const bookmarks = JSON.parse(localStorage.getItem('nigeriaNewsBookmarks') || '[]');
        if (!bookmarks.includes(url)) {
            bookmarks.push(url);
            localStorage.setItem('nigeriaNewsBookmarks', JSON.stringify(bookmarks));
            alert('Article bookmarked!');
        } else {
            alert('Article already bookmarked');
        }
    },

    bookmarkPage: function() {
        if (window.navigator.share) {
            // Use Web Share API if available
            window.navigator.share({
                title: 'Nigeria Economic News Aggregator',
                url: window.location.href
            });
        } else {
            // Fallback to prompt
            alert(`Bookmark this page to stay updated!\n\nURL: ${window.location.href}`);
        }
    },

    exportData: function() {
        // Export filtered articles as JSON
        const exportData = {
            exported_at: new Date().toISOString(),
            filters: this.config.filters,
            articles: this.config.articles.filter(article => {
                // Apply current filters to export
                if (this.config.filters.source !== 'all' && article.source !== this.config.filters.source) {
                    return false;
                }
                if (this.config.filters.category !== 'all' && article.category !== this.config.filters.category) {
                    return false;
                }
                if (this.config.filters.search) {
                    const searchTerm = this.config.filters.search.toLowerCase();
                    if (!article.title.toLowerCase().includes(searchTerm) &&
                        !(article.summary && article.summary.toLowerCase().includes(searchTerm))) {
                        return false;
                    }
                }
                return true;
            })
        };
        
        // Create download link
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `nigeria-news-export-${new Date().toISOString().slice(0, 10)}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    NewsApp.init();
    
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .sentiment-badge {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .sentiment-positive {
            background: #c6f6d5;
            color: #22543d;
        }
        
        .sentiment-neutral {
            background: #e2e8f0;
            color: #4a5568;
        }
        
        .sentiment-negative {
            background: #fed7d7;
            color: #742a2a;
        }
        
        .category-badge {
            background: #ebf8ff;
            color: #2b6cb0;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.7rem;
            margin-left: 8px;
        }
    `;
    document.head.appendChild(style);
});
