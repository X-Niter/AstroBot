/**
 * AstroBot AI Dashboard Main JavaScript
 * Sets up all components and initializes the application
 */

// Main init function that runs on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips for any element with data-tippy-content
    if (window.tippy) {
        tippy('[data-tippy-content]', {
            theme: document.body.classList.contains('dark') ? 'dark' : 'light',
            placement: 'bottom',
            arrow: true,
            animation: 'scale'
        });
    }
    
    // Initialize theme-related features
    initThemeSystem();
    
    // Setup responsive navigation
    initNavigation();
    
    // Initialize collapse plugin for Alpine.js if available
    if (window.Alpine && window.Alpine.plugin && typeof window.Alpine.collapse === 'function') {
        Alpine.plugin(Alpine.collapse);
    }
    
    // Setup charts and data visualization
    initCharts();
    
    // Initialize any socket connections if user is authenticated
    if (document.body.getAttribute('data-user-authenticated') === 'true') {
        initSocketConnection();
    }
    
    // Initialize premium features if available
    if (AstroBotUtils.auth && AstroBotUtils.auth.isPremiumUser()) {
        initPremiumFeatures();
    }
});

/**
 * Initialize the theme system
 */
function initThemeSystem() {
    // Observe theme changes to update charts and other components
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'class' || mutation.attributeName === 'data-theme') {
                // Update theme for charts
                updateChartsTheme();
                
                // Update theme for tooltips
                updateTooltipsTheme();
                
                // Update theme for any custom components
                updateCustomComponentsTheme();
            }
        });
    });
    
    // Start observing the document body for theme changes
    observer.observe(document.body, { attributes: true });
}

/**
 * Initialize responsive navigation
 */
function initNavigation() {
    // Setup dropdown menus to close when clicking outside
    document.addEventListener('click', function(event) {
        // Check if the click was outside a dropdown
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        dropdowns.forEach(function(dropdown) {
            if (dropdown.classList.contains('show') && !dropdown.contains(event.target) && !event.target.matches('.dropdown-toggle')) {
                dropdown.classList.remove('show');
            }
        });
    });
    
    // Setup mobile navigation toggle
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileToggle && mobileMenu) {
        mobileToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
}

/**
 * Update charts to match current theme
 */
function updateChartsTheme() {
    if (!window.AstroBotUtils || !window.AstroBotUtils.charts) return;
    
    // If we have a global charts collection, update all charts
    if (window.dashboardCharts && Array.isArray(window.dashboardCharts)) {
        window.dashboardCharts.forEach(function(chart) {
            AstroBotUtils.charts.updateChartTheme(chart);
        });
    }
}

/**
 * Update tooltips to match current theme
 */
function updateTooltipsTheme() {
    if (!window.tippy) return;
    
    // Get the current theme
    const theme = document.body.classList.contains('dark') ? 'dark' : 'light';
    
    // Update all tooltips
    const all = document._tippy;
    if (all) {
        Object.values(all).forEach(function(instance) {
            instance.setProps({ theme: theme });
        });
    }
}

/**
 * Update custom components to match current theme
 */
function updateCustomComponentsTheme() {
    // Update any custom components that need theme adjustments
    // This is a placeholder for component-specific theme updates
}

/**
 * Initialize charts and data visualization
 */
function initCharts() {
    // Create a global array to store chart instances for later updates
    window.dashboardCharts = [];
    
    // Initialize any charts on the page
    const chartContainers = document.querySelectorAll('[data-chart]');
    
    chartContainers.forEach(function(container) {
        const chartType = container.getAttribute('data-chart-type') || 'line';
        const chartId = container.getAttribute('id');
        const chartUrl = container.getAttribute('data-chart-url');
        
        if (chartId && chartUrl) {
            // Load chart data from the server
            fetch(chartUrl)
                .then(response => response.json())
                .then(data => {
                    // Create the chart
                    if (window.AstroBotUtils && window.AstroBotUtils.charts) {
                        const chart = AstroBotUtils.charts.createChart(
                            `#${chartId} canvas`, 
                            chartType, 
                            data
                        );
                        
                        // Store the chart instance
                        if (chart) {
                            window.dashboardCharts.push(chart);
                        }
                    } else if (window.Chart) {
                        // Fallback to direct Chart.js if our utility isn't available
                        const ctx = container.querySelector('canvas').getContext('2d');
                        const chart = new Chart(ctx, {
                            type: chartType,
                            data: data,
                            options: {
                                responsive: true,
                                maintainAspectRatio: false
                            }
                        });
                        
                        // Store the chart instance
                        window.dashboardCharts.push(chart);
                    }
                })
                .catch(error => {
                    console.error('Error loading chart data:', error);
                    container.innerHTML = '<div class="alert alert-danger">Error loading chart data</div>';
                });
        }
    });
}

/**
 * Initialize socket connection for real-time updates
 */
function initSocketConnection() {
    if (!window.AstroBotUtils || !window.AstroBotUtils.socket) return;
    
    // Create socket connection
    const socket = AstroBotUtils.socket.createSocketConnection();
    
    // Setup event handlers for socket events
    AstroBotUtils.socket.setupSocketEventHandlers(socket, {
        'connect': function() {
            console.log('Connected to server');
        },
        'disconnect': function() {
            console.log('Disconnected from server');
        },
        'error': function(error) {
            console.error('Socket error:', error);
        },
        'notification': function(data) {
            showNotification(data.message, data.type);
        },
        'update_dashboard': function(data) {
            updateDashboardData(data);
        }
    });
}

/**
 * Show a notification to the user
 * @param {string} message - The notification message
 * @param {string} type - The notification type (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    // Check if we have a notification container
    let container = document.getElementById('notification-container');
    
    // Create one if it doesn't exist
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2';
        document.body.appendChild(container);
    }
    
    // Create the notification element
    const notification = document.createElement('div');
    notification.className = `notification shadow-lg rounded-lg p-4 max-w-md transform transition-all duration-300 ease-in-out translate-x-full opacity-0 ${getNotificationClass(type)}`;
    
    // Create the content
    notification.innerHTML = `
        <div class="flex items-center">
            <div class="flex-shrink-0">
                ${getNotificationIcon(type)}
            </div>
            <div class="ml-3">
                <p class="text-sm font-medium">${message}</p>
            </div>
            <div class="ml-auto pl-3">
                <button type="button" class="notification-close">
                    <span class="sr-only">Close</span>
                    <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                </button>
            </div>
        </div>
    `;
    
    // Add to container
    container.appendChild(notification);
    
    // Setup close button
    const closeButton = notification.querySelector('.notification-close');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            hideNotification(notification);
        });
    }
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full', 'opacity-0');
    }, 10);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            hideNotification(notification);
        }
    }, 5000);
}

/**
 * Hide a notification with animation
 * @param {HTMLElement} notification - The notification element
 */
function hideNotification(notification) {
    // Animate out
    notification.classList.add('opacity-0', 'translate-x-full');
    
    // Remove after animation
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

/**
 * Get CSS class for notification based on type
 * @param {string} type - Notification type
 * @returns {string} CSS class
 */
function getNotificationClass(type) {
    switch (type) {
        case 'success':
            return 'bg-green-50 text-green-800 dark:bg-green-900 dark:text-green-100';
        case 'error':
            return 'bg-red-50 text-red-800 dark:bg-red-900 dark:text-red-100';
        case 'warning':
            return 'bg-yellow-50 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100';
        default:
            return 'bg-blue-50 text-blue-800 dark:bg-blue-900 dark:text-blue-100';
    }
}

/**
 * Get SVG icon for notification based on type
 * @param {string} type - Notification type
 * @returns {string} SVG icon HTML
 */
function getNotificationIcon(type) {
    switch (type) {
        case 'success':
            return '<svg class="h-5 w-5 text-green-500 dark:text-green-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>';
        case 'error':
            return '<svg class="h-5 w-5 text-red-500 dark:text-red-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>';
        case 'warning':
            return '<svg class="h-5 w-5 text-yellow-500 dark:text-yellow-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>';
        default:
            return '<svg class="h-5 w-5 text-blue-500 dark:text-blue-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>';
    }
}

/**
 * Update dashboard data with real-time information
 * @param {Object} data - The dashboard data
 */
function updateDashboardData(data) {
    // Update any elements with matching data attributes
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            const value = data[key];
            const elements = document.querySelectorAll(`[data-live="${key}"]`);
            
            elements.forEach(function(element) {
                // Update based on element type
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.value = value;
                } else {
                    element.textContent = value;
                }
                
                // Add a highlight effect
                element.classList.add('highlight-update');
                setTimeout(() => {
                    element.classList.remove('highlight-update');
                }, 2000);
            });
        }
    }
    
    // If data contains chart updates, refresh the charts
    if (data.charts && window.dashboardCharts) {
        for (const chartId in data.charts) {
            if (data.charts.hasOwnProperty(chartId)) {
                // Find the chart by ID
                const chartIndex = window.dashboardCharts.findIndex(
                    chart => chart.canvas.id === chartId || chart.canvas.parentNode.id === chartId
                );
                
                if (chartIndex !== -1) {
                    const chart = window.dashboardCharts[chartIndex];
                    const newData = data.charts[chartId];
                    
                    // Update chart data
                    chart.data = newData;
                    chart.update();
                }
            }
        }
    }
}

/**
 * Initialize premium features for premium users
 */
function initPremiumFeatures() {
    // Enable premium theme selector
    const themeSelectors = document.querySelectorAll('[data-premium-theme]');
    themeSelectors.forEach(function(selector) {
        selector.classList.remove('disabled', 'opacity-50');
        selector.setAttribute('data-tippy-content', 'Click to apply this premium theme');
    });
    
    // Initialize premium theme options
    const premiumThemes = document.querySelectorAll('[data-theme-select]');
    premiumThemes.forEach(function(themeSelector) {
        themeSelector.addEventListener('click', function() {
            const theme = this.getAttribute('data-theme-value');
            AstroBotTheme.fade(theme);
        });
    });
    
    // Enable any premium-only features
    document.querySelectorAll('[data-premium-feature]').forEach(function(feature) {
        feature.classList.remove('hidden');
    });
}