
// USA AI News Tool - Main JavaScript

// DOM Elements
const fetchNewsBtn = document.getElementById('fetch-news-btn');
const quickUpdateBtn = document.getElementById('quick-update-btn');
const updateRecentNewsBtn = document.getElementById('update-recent-news-btn');
const updateInternationalNewsBtn = document.getElementById('update-international-news-btn');
const updateAiNewsBtn = document.getElementById('update-ai-news-btn');
const downloadAllImagesBtn = document.getElementById('download-all-images-btn');
const exportForVercelBtn = document.getElementById('export-for-vercel-btn');
const refreshNewsBtn = document.getElementById('refresh-news-btn');
const newsFilter = document.getElementById('news-filter');
const settingsBtn = document.getElementById('settings-btn');
const toastContainer = document.getElementById('toast-container');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');
const modalContainer = document.getElementById('modal-container');
const modalTitle = document.getElementById('modal-title');
const modalContent = document.getElementById('modal-content');
const modalClose = document.getElementById('modal-close');
const modalCancel = document.getElementById('modal-cancel');
const modalConfirm = document.getElementById('modal-confirm');

// Navigation
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', function() {
        navLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
});

// Set active nav link based on current page
const currentPath = window.location.pathname;
navLinks.forEach(link => {
    const linkPath = link.getAttribute('href');
    if (currentPath === linkPath || (currentPath === '/' && linkPath === '/')) {
        link.classList.add('active');
    } else {
        link.classList.remove('active');
    }
});

// Dashboard Stats
function updateDashboardStats() {
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            if (document.getElementById('total-articles')) {
                document.getElementById('total-articles').textContent = data.total_articles;
            }
            if (document.getElementById('total-images')) {
                document.getElementById('total-images').textContent = data.total_images;
            }
            if (document.getElementById('total-pages')) {
                document.getElementById('total-pages').textContent = data.total_pages;
            }
            if (document.getElementById('last-update')) {
                document.getElementById('last-update').textContent = data.last_update ? new Date(data.last_update).toLocaleString() : 'Never';
            }
        })
        .catch(error => {
            console.error('Error fetching dashboard stats:', error);
            showToast('Error fetching dashboard stats', 'error');
        });
}

// Topic Distribution Chart
function updateTopicDistributionChart() {
    const topicsChart = document.getElementById('topics-chart');
    if (!topicsChart) return;
    
    fetch('/api/dashboard/topic-distribution')
        .then(response => response.json())
        .then(data => {
            new Chart(topicsChart, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: [
                            '#3b82f6', // blue
                            '#10b981', // green
                            '#8b5cf6', // purple
                            '#f59e0b', // amber
                            '#ef4444', // red
                            '#06b6d4'  // cyan
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#d1d5db'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching topic distribution:', error);
        });
}

// Recent News
function updateRecentNewsList(topic = 'all') {
    const recentNewsList = document.getElementById('recent-news-list');
    if (!recentNewsList) return;
    
    fetch(`/api/dashboard/recent-news?topic=${topic}`)
        .then(response => response.json())
        .then(data => {
            if (data.articles.length === 0) {
                recentNewsList.innerHTML = `
                    <div class="text-center text-gray-400 py-8">
                        <i class="fas fa-newspaper text-4xl mb-4"></i>
                        <p>No news articles yet. Click "Fetch Latest News" to get started.</p>
                    </div>
                `;
                return;
            }
            
            recentNewsList.innerHTML = '';
            data.articles.forEach(article => {
                const articleElement = document.createElement('div');
                articleElement.className = 'bg-gray-700 rounded-lg p-4 border border-gray-600 hover:border-blue-500 transition';
                articleElement.innerHTML = `
                    <div class="flex justify-between items-start mb-2">
                        <h4 class="text-lg font-semibold text-blue-400">${article.title}</h4>
                        <span class="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded">${article.topic}</span>
                    </div>
                    <p class="text-gray-300 text-sm mb-3">${article.content.substring(0, 150)}...</p>
                    <div class="flex justify-between items-center">
                        <div class="text-xs text-gray-400">
                            <span class="mr-3"><i class="fas fa-newspaper mr-1"></i> ${article.source}</span>
                            <span><i class="fas fa-calendar-alt mr-1"></i> ${new Date(article.published_date).toLocaleDateString()}</span>
                        </div>
                        <a href="${article.url}" target="_blank" class="text-blue-400 hover:text-blue-300 text-sm">
                            Read More <i class="fas fa-external-link-alt ml-1"></i>
                        </a>
                    </div>
                `;
                recentNewsList.appendChild(articleElement);
            });
        })
        .catch(error => {
            console.error('Error fetching recent news:', error);
            showToast('Error fetching recent news', 'error');
        });
}

// Fetch News
function fetchLatestNews() {
    showLoading('Fetching latest news...');
    
    fetch('/api/news/fetch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast(`Successfully fetched ${data.count} news articles`, 'success');
            updateDashboardStats();
            updateRecentNewsList();
            updateTopicDistributionChart();
        } else {
            showToast('Error fetching news', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error fetching news:', error);
        showToast('Error fetching news', 'error');
    });
}

// Quick Update
function quickUpdate() {
    showLoading('Performing quick update...');
    
    fetch('/api/quick-actions/quick-update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('Successfully updated all news pages', 'success');
        } else {
            showToast('Error updating news pages', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error performing quick update:', error);
        showToast('Error performing quick update', 'error');
    });
}

// Update Recent News Page
function updateRecentNewsPage() {
    showLoading('Updating Recent News page...');
    
    fetch('/api/quick-actions/update-recent-news', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('Successfully updated Recent News page', 'success');
        } else {
            showToast('Error updating Recent News page', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error updating Recent News page:', error);
        showToast('Error updating Recent News page', 'error');
    });
}

// Update International News Page
function updateInternationalNewsPage() {
    showLoading('Updating International News page...');
    
    fetch('/api/quick-actions/update-international-news', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('Successfully updated International News page', 'success');
        } else {
            showToast('Error updating International News page', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error updating International News page:', error);
        showToast('Error updating International News page', 'error');
    });
}

// Update AI News Page
function updateAiNewsPage() {
    showLoading('Updating AI News page...');
    
    fetch('/api/quick-actions/update-ai-news', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('Successfully updated AI News page', 'success');
        } else {
            showToast('Error updating AI News page', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error updating AI News page:', error);
        showToast('Error updating AI News page', 'error');
    });
}

// Download All Images
function downloadAllImages() {
    showLoading('Downloading all images...');
    
    fetch('/api/images/download-all', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast(`Successfully downloaded ${data.count} images`, 'success');
            updateDashboardStats();
        } else {
            showToast('Error downloading images', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error downloading images:', error);
        showToast('Error downloading images', 'error');
    });
}

// Export for Vercel
function exportForVercel() {
    showModal(
        'Export for Vercel',
        `
        <p class="text-gray-300 mb-4">This will export all published pages and assets for deployment to Vercel.</p>
        <div class="space-y-2">
            <div class="flex items-center">
                <input type="checkbox" id="export-include-images" class="mr-2" checked>
                <label for="export-include-images" class="text-gray-300">Include Images</label>
            </div>
            <div class="flex items-center">
                <input type="checkbox" id="export-include-css" class="mr-2" checked>
                <label for="export-include-css" class="text-gray-300">Include CSS Files</label>
            </div>
            <div class="flex items-center">
                <input type="checkbox" id="export-include-js" class="mr-2" checked>
                <label for="export-include-js" class="text-gray-300">Include JavaScript Files</label>
            </div>
        </div>
        `,
        'Export',
        () => {
            const includeImages = document.getElementById('export-include-images').checked;
            const includeCss = document.getElementById('export-include-css').checked;
            const includeJs = document.getElementById('export-include-js').checked;
            
            showLoading('Exporting for Vercel...');
            
            // Get all published pages
            fetch('/api/pages?status=published')
                .then(response => response.json())
                .then(data => {
                    const pageIds = data.pages.map(page => page.id);
                    
                    // Export the pages
                    return fetch('/api/export', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            format: 'zip',
                            include_images: includeImages,
                            include_css: includeCss,
                            include_js: includeJs,
                            optimize_images: true,
                            minify_html: true,
                            minify_css: true,
                            minify_js: true,
                            pages: pageIds
                        })
                    });
                })
                .then(response => response.json())
                .then(data => {
                    hideLoading();
                    if (data.success) {
                        showToast('Successfully exported for Vercel', 'success');
                        // Trigger download
                        const link = document.createElement('a');
                        link.href = data.export_path;
                        link.download = 'vercel_export.zip';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    } else {
                        showToast('Error exporting for Vercel', 'error');
                    }
                })
                .catch(error => {
                    hideLoading();
                    console.error('Error exporting for Vercel:', error);
                    showToast('Error exporting for Vercel', 'error');
                });
        }
    );
}

// Toast Notifications
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-2"></i>
                <span>${message}</span>
            </div>
            <button class="text-white ml-4 hover:text-gray-200 toast-close">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Close button
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });
    
    // Auto remove after duration
    setTimeout(() => {
        toast.remove();
    }, duration);
}

// Loading Overlay
function showLoading(text = 'Loading...') {
    loadingText.textContent = text;
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

// Modal
function showModal(title, content, confirmText = 'Confirm', onConfirm = null) {
    modalTitle.textContent = title;
    modalContent.innerHTML = content;
    modalConfirm.textContent = confirmText;
    modalContainer.classList.remove('hidden');
    
    // Close button
    modalClose.onclick = () => {
        modalContainer.classList.add('hidden');
    };
    
    // Cancel button
    modalCancel.onclick = () => {
        modalContainer.classList.add('hidden');
    };
    
    // Confirm button
    modalConfirm.onclick = () => {
        if (onConfirm) onConfirm();
        modalContainer.classList.add('hidden');
    };
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard if on dashboard page
    if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
        updateDashboardStats();
        updateRecentNewsList();
        updateTopicDistributionChart();
    }
    
    // Fetch News button
    if (fetchNewsBtn) {
        fetchNewsBtn.addEventListener('click', fetchLatestNews);
    }
    
    // Quick Update button
    if (quickUpdateBtn) {
        quickUpdateBtn.addEventListener('click', quickUpdate);
    }
    
    // Update Recent News Page button
    if (updateRecentNewsBtn) {
        updateRecentNewsBtn.addEventListener('click', updateRecentNewsPage);
    }
    
    // Update International News Page button
    if (updateInternationalNewsBtn) {
        updateInternationalNewsBtn.addEventListener('click', updateInternationalNewsPage);
    }
    
    // Update AI News Page button
    if (updateAiNewsBtn) {
        updateAiNewsBtn.addEventListener('click', updateAiNewsPage);
    }
    
    // Download All Images button
    if (downloadAllImagesBtn) {
        downloadAllImagesBtn.addEventListener('click', downloadAllImages);
    }
    
    // Export for Vercel button
    if (exportForVercelBtn) {
        exportForVercelBtn.addEventListener('click', exportForVercel);
    }
    
    // Refresh News button
    if (refreshNewsBtn) {
        refreshNewsBtn.addEventListener('click', () => {
            updateRecentNewsList(newsFilter.value);
        });
    }
    
    // News Filter
    if (newsFilter) {
        newsFilter.addEventListener('change', () => {
            updateRecentNewsList(newsFilter.value);
        });
    }
    
    // Settings button
    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            window.location.href = '/settings';
        });
    }
});
        