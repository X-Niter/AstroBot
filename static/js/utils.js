/**
 * AstroBot Utilities
 * Collection of helper functions for the AstroBot web dashboard
 */

// Create global namespace for our utilities
window.AstroBotUtils = window.AstroBotUtils || {};

/**
 * Socket.IO utilities for real-time communication
 */
AstroBotUtils.socket = {
    /**
     * Create a socket connection
     * @returns {Socket} Socket.IO connection
     */
    createSocketConnection: function() {
        // Create socket connection with auto-reconnect
        const socket = io({
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            timeout: 20000
        });
        
        // Setup default event handlers
        socket.on('connect', function() {
            console.log('Socket connected');
            
            // Add connected class to body for styling
            document.body.classList.add('socket-connected');
            
            // Show connection indicator if it exists
            const indicator = document.getElementById('connection-indicator');
            if (indicator) {
                indicator.classList.remove('bg-danger');
                indicator.classList.add('bg-success');
                indicator.setAttribute('data-tippy-content', 'Connected to server');
            }
        });
        
        socket.on('disconnect', function() {
            console.log('Socket disconnected');
            
            // Remove connected class from body
            document.body.classList.remove('socket-connected');
            
            // Update connection indicator
            const indicator = document.getElementById('connection-indicator');
            if (indicator) {
                indicator.classList.remove('bg-success');
                indicator.classList.add('bg-danger');
                indicator.setAttribute('data-tippy-content', 'Disconnected from server');
            }
        });
        
        socket.on('error', function(error) {
            console.error('Socket error:', error);
        });
        
        return socket;
    },
    
    /**
     * Setup event handlers for socket events
     * @param {Socket} socket - Socket.IO connection
     * @param {Object} handlers - Event handlers mapping
     */
    setupSocketEventHandlers: function(socket, handlers) {
        if (!socket) return;
        
        // Register all provided event handlers
        for (const event in handlers) {
            if (handlers.hasOwnProperty(event)) {
                socket.on(event, handlers[event]);
            }
        }
    }
};

/**
 * Chart utilities for data visualization
 */
AstroBotUtils.charts = {
    /**
     * Create a responsive Chart.js chart
     * @param {string} selector - CSS selector for canvas element
     * @param {string} type - Chart type (line, bar, pie, etc.)
     * @param {Object} data - Chart data
     * @param {Object} options - Chart options
     * @returns {Chart} Chart.js instance
     */
    createChart: function(selector, type, data, options = {}) {
        const ctx = document.querySelector(selector);
        if (!ctx) return null;
        
        // Set default options for all charts
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: getComputedStyle(document.body).getPropertyValue('--text-color')
                    }
                },
                tooltip: {
                    backgroundColor: getComputedStyle(document.body).getPropertyValue('--card-bg'),
                    titleColor: getComputedStyle(document.body).getPropertyValue('--text-color'),
                    bodyColor: getComputedStyle(document.body).getPropertyValue('--text-color'),
                    borderColor: getComputedStyle(document.body).getPropertyValue('--border-color'),
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: {
                        color: getComputedStyle(document.body).getPropertyValue('--border-color')
                    },
                    ticks: {
                        color: getComputedStyle(document.body).getPropertyValue('--text-color')
                    }
                },
                y: {
                    grid: {
                        color: getComputedStyle(document.body).getPropertyValue('--border-color')
                    },
                    ticks: {
                        color: getComputedStyle(document.body).getPropertyValue('--text-color')
                    }
                }
            }
        };
        
        // Merge options
        const mergedOptions = { ...defaultOptions, ...options };
        
        // Create and return the chart
        return new Chart(ctx, {
            type: type,
            data: data,
            options: mergedOptions
        });
    },
    
    /**
     * Update chart theme based on current app theme
     * @param {Chart} chart - Chart.js instance to update
     */
    updateChartTheme: function(chart) {
        if (!chart) return;
        
        // Get current theme colors
        const textColor = getComputedStyle(document.body).getPropertyValue('--text-color');
        const borderColor = getComputedStyle(document.body).getPropertyValue('--border-color');
        const cardBg = getComputedStyle(document.body).getPropertyValue('--card-bg');
        
        // Update legend colors
        chart.options.plugins.legend.labels.color = textColor;
        
        // Update tooltip colors
        chart.options.plugins.tooltip.backgroundColor = cardBg;
        chart.options.plugins.tooltip.titleColor = textColor;
        chart.options.plugins.tooltip.bodyColor = textColor;
        chart.options.plugins.tooltip.borderColor = borderColor;
        
        // Update axis colors
        if (chart.options.scales) {
            if (chart.options.scales.x) {
                chart.options.scales.x.grid.color = borderColor;
                chart.options.scales.x.ticks.color = textColor;
            }
            if (chart.options.scales.y) {
                chart.options.scales.y.grid.color = borderColor;
                chart.options.scales.y.ticks.color = textColor;
            }
        }
        
        // Apply the updates
        chart.update();
    }
};

/**
 * UI utilities for animations and effects
 */
AstroBotUtils.ui = {
    /**
     * Animate element with GSAP
     * @param {string} selector - CSS selector for target element
     * @param {Object} properties - Animation properties
     * @param {Object} options - Animation options
     * @returns {gsap.timeline} GSAP animation timeline
     */
    animate: function(selector, properties, options = {}) {
        return gsap.to(selector, {
            ...properties,
            ...options
        });
    },
    
    /**
     * Create a staggered animation for multiple elements
     * @param {string} selector - CSS selector for target elements
     * @param {Object} properties - Animation properties
     * @param {number} stagger - Stagger amount in seconds
     * @param {Object} options - Animation options
     * @returns {gsap.timeline} GSAP animation timeline
     */
    staggerAnimate: function(selector, properties, stagger = 0.1, options = {}) {
        return gsap.to(selector, {
            ...properties,
            stagger: stagger,
            ...options
        });
    },
    
    /**
     * Create a typing effect with GSAP
     * @param {string} selector - CSS selector for target element
     * @param {string} text - Text to type
     * @param {number} speed - Typing speed (chars per second)
     * @returns {gsap.timeline} GSAP animation timeline
     */
    typeText: function(selector, text, speed = 30) {
        const element = document.querySelector(selector);
        if (!element) return null;
        
        // Clear the element
        element.textContent = '';
        
        // Create a timeline
        const tl = gsap.timeline();
        
        // Split the text into characters
        const chars = text.split('');
        
        // Type each character
        chars.forEach((char, index) => {
            tl.add(() => {
                element.textContent += char;
            }, index / speed);
        });
        
        return tl;
    }
};

/**
 * Form utilities for validation and submission
 */
AstroBotUtils.forms = {
    /**
     * Initialize form validation
     * @param {string} formSelector - CSS selector for the form
     * @param {Function} submitCallback - Function to call on successful submission
     */
    initFormValidation: function(formSelector, submitCallback) {
        const form = document.querySelector(formSelector);
        if (!form) return;
        
        form.addEventListener('submit', function(event) {
            // Stop form from submitting normally
            event.preventDefault();
            
            // Check form validity
            if (form.checkValidity()) {
                // If valid, call the callback with form data
                const formData = new FormData(form);
                submitCallback(formData, form);
            } else {
                // If invalid, trigger validation UI
                form.classList.add('was-validated');
            }
        });
    },
    
    /**
     * Submit form data via AJAX
     * @param {string} url - Endpoint URL
     * @param {FormData} formData - Form data to submit
     * @param {Function} successCallback - Function to call on successful submission
     * @param {Function} errorCallback - Function to call on error
     */
    submitFormAjax: function(url, formData, successCallback, errorCallback) {
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (successCallback) successCallback(data);
        })
        .catch(error => {
            if (errorCallback) errorCallback(error);
        });
    }
};

/**
 * Session and authentication utilities
 */
AstroBotUtils.auth = {
    /**
     * Get the current user's information
     * @returns {Object|null} User info or null if not authenticated
     */
    getCurrentUser: function() {
        // Get user info from data attribute
        const isAuthenticated = document.body.getAttribute('data-user-authenticated') === 'true';
        if (!isAuthenticated) return null;
        
        // User is authenticated, build user info object
        // In a real app, this might come from a script tag with JSON data
        const userDataElement = document.getElementById('current-user-data');
        if (userDataElement) {
            try {
                return JSON.parse(userDataElement.textContent);
            } catch (e) {
                console.error('Error parsing user data', e);
                return { authenticated: true };
            }
        }
        
        return { authenticated: true };
    },
    
    /**
     * Check if the current user has a specific permission
     * @param {string} permission - Permission to check
     * @returns {boolean} Whether the user has the permission
     */
    hasPermission: function(permission) {
        const user = this.getCurrentUser();
        if (!user) return false;
        
        // Check user permissions
        if (user.permissions && Array.isArray(user.permissions)) {
            return user.permissions.includes(permission);
        }
        
        return false;
    },
    
    /**
     * Check if the current user is premium
     * @returns {boolean} Whether the user has premium status
     */
    isPremiumUser: function() {
        const user = this.getCurrentUser();
        return user && user.is_premium === true;
    }
};