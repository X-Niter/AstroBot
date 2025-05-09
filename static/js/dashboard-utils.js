/**
 * AstroBot Dashboard Utilities
 * A collection of utility functions for the analytics dashboard
 */

// Create a namespace for AstroBot utilities if it doesn't exist
window.AstroBotUtils = window.AstroBotUtils || {};

// Animation utilities using GSAP
AstroBotUtils.animation = {
  /**
   * Safely check if GSAP is available and if elements exist before animating
   * @param {string} selector - CSS selector for target elements
   * @returns {boolean} - Whether GSAP is available and elements exist
   */
  canAnimate: function(selector) {
    if (typeof gsap === 'undefined') {
      console.warn('GSAP is not available');
      return false;
    }
    
    if (!selector) {
      console.warn('No selector provided for animation');
      return false;
    }
    
    const elements = document.querySelectorAll(selector);
    if (elements.length === 0) {
      console.warn(`No elements found for selector: ${selector}`);
      return false;
    }
    
    return true;
  },
  /**
   * Animate elements with an entrance animation
   * @param {string} selector - CSS selector for target elements
   * @param {Object} options - GSAP animation options
   */
  animateEntrance: function(selector, options = {}) {
    // Use our utility to check if we can animate
    if (this.canAnimate(selector)) {
      try {
        const elements = document.querySelectorAll(selector);
        gsap.from(elements, {
          opacity: 0,
          y: 20,
          duration: 0.5,
          stagger: 0.1,
          ease: 'power2.out',
          ...options
        });
      } catch (err) {
        console.warn('GSAP animation error:', err);
      }
    }
  },

  /**
   * Add hover effects to elements
   * @param {string} selector - CSS selector for target elements
   * @param {Object} options - GSAP animation options for hover effect
   */
  addHoverEffects: function(selector, options = {}) {
    try {
      // Use our utility to check if we can animate
      if (!this.canAnimate(selector)) {
        return; // Exit if we can't animate
      }
      
      const elements = document.querySelectorAll(selector);
      
      // For each element, safely add event listeners
      elements.forEach(element => {
        if (!element) return; // Skip null elements
        
        try {
          // Add mouseenter listener
          element.addEventListener('mouseenter', () => {
            if (typeof gsap !== 'undefined') {
              gsap.to(element, {
                scale: 1.02,
                duration: 0.3,
                ease: 'power1.out',
                ...options
              });
            }
          });
          
          // Add mouseleave listener
          element.addEventListener('mouseleave', () => {
            if (typeof gsap !== 'undefined') {
              gsap.to(element, {
                scale: 1,
                duration: 0.3,
                ease: 'power1.out',
                ...options
              });
            }
          });
        } catch (listenerErr) {
          console.warn(`Error adding event listeners to element: ${listenerErr.message}`);
        }
      });
    } catch (err) {
      console.warn('GSAP hover effect error:', err);
    }
  },

  /**
   * Animate notification or toast elements
   * @param {HTMLElement} element - Element to animate
   */
  animateNotification: function(element) {
    try {
      // Check if GSAP is available and element exists
      if (typeof gsap === 'undefined') {
        console.warn('GSAP not available for notification animation');
        return;
      }
      
      if (!element) {
        console.warn('No element provided for notification animation');
        return;
      }
      
      // Initial state - with try/catch for safety
      try {
        gsap.set(element, { opacity: 0, y: -20 });
      } catch (setErr) {
        console.warn('Error setting initial animation state:', setErr);
        return;
      }
      
      // Animate in - with try/catch for safety
      try {
        gsap.to(element, {
          opacity: 1,
          y: 0,
          duration: 0.5,
          ease: 'power2.out'
        });
      } catch (animateInErr) {
        console.warn('Error animating notification in:', animateInErr);
        return;
      }
      
      // Auto-remove after delay - with try/catch for safety
      setTimeout(() => {
        try {
          // Ensure element still exists before animating out
          if (!element || !element.parentNode) {
            console.warn('Element no longer in DOM for animation out');
            return;
          }
          
          gsap.to(element, {
            opacity: 0,
            y: -20,
            duration: 0.5,
            ease: 'power2.in',
            onComplete: () => {
              try {
                // Additional check before removal
                if (element && element.parentNode) {
                  element.remove();
                }
              } catch (removeErr) {
                console.warn('Error removing notification element:', removeErr);
              }
            }
          });
        } catch (animateOutErr) {
          console.warn('Error animating notification out:', animateOutErr);
        }
      }, 5000);
    } catch (err) {
      console.warn('GSAP notification animation error:', err);
    }
  }
};

// Chart utilities
AstroBotUtils.charts = {
  /**
   * Create a responsive chart with proper sizing
   * @param {string} elementId - Canvas element ID
   * @param {string} type - Chart type (line, bar, pie, etc.)
   * @param {Object} data - Chart data
   * @param {Object} options - Chart options
   * @returns {Chart} Chart instance
   */
  createResponsiveChart: function(elementId, type, data, options = {}) {
    try {
      // Validate inputs
      if (!elementId) {
        console.warn('No element ID provided for chart creation');
        return null;
      }
      
      if (!type) {
        console.warn('No chart type provided');
        return null;
      }
      
      if (!data) {
        console.warn('No data provided for chart');
        data = { datasets: [] }; // Provide empty data to avoid errors
      }
      
      // Check if Chart.js is available
      if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not available');
        return null;
      }
      
      // Get the canvas element
      const element = document.getElementById(elementId);
      if (!element) {
        console.warn(`Canvas element not found: ${elementId}`);
        return null;
      }
      
      // Check if element is a canvas
      if (element.tagName.toLowerCase() !== 'canvas') {
        console.warn(`Element ${elementId} is not a canvas`);
        return null;
      }
      
      // Safely get the 2D context
      let context;
      try {
        context = element.getContext('2d');
        if (!context) {
          console.warn(`Could not get 2D context for ${elementId}`);
          return null;
        }
      } catch (contextErr) {
        console.error(`Error getting canvas context for ${elementId}:`, contextErr);
        return null;
      }
      
      // Default options for responsive charts
      const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          tooltip: {
            enabled: true
          }
        },
        onResize: (chart, size) => {
          // Improve chart resizing behavior
          try {
            if (size.width <= 0 || size.height <= 0) {
              console.warn('Invalid chart size detected during resize');
              return;
            }
          } catch (resizeErr) {
            console.warn('Error in resize handler:', resizeErr);
          }
        }
      };
      
      // Safely check for and destroy existing chart instance
      try {
        const existingChartInstance = Chart.getChart(element);
        if (existingChartInstance) {
          try {
            existingChartInstance.destroy();
            console.log(`Previous chart instance on ${elementId} destroyed successfully`);
          } catch (destroyErr) {
            console.warn(`Failed to destroy existing chart on ${elementId}:`, destroyErr);
          }
        }
      } catch (chartInstanceErr) {
        console.warn(`Error checking for existing chart instance on ${elementId}:`, chartInstanceErr);
      }
      
      // Safely create chart with merged options
      try {
        const newChart = new Chart(context, {
          type: type,
          data: data,
          options: { ...defaultOptions, ...options }
        });
        
        console.log(`Chart created successfully on ${elementId}`);
        return newChart;
      } catch (createErr) {
        console.error(`Failed to create chart on ${elementId}:`, createErr);
        return null;
      }
    } catch (err) {
      console.error(`Unexpected error creating chart (${elementId}):`, err);
      return null;
    }
  },
  
  /**
   * Update chart data
   * @param {Chart} chart - Chart instance
   * @param {Object} newData - New data for the chart
   */
  updateChartData: function(chart, newData) {
    try {
      // Validate inputs
      if (!chart) {
        console.warn('No chart instance provided for update');
        return;
      }
      
      if (!newData) {
        console.warn('No data provided for chart update');
        return;
      }
      
      // Check if chart is a valid Chart.js instance
      if (typeof chart !== 'object' || typeof chart.update !== 'function') {
        console.warn('Invalid chart instance provided');
        return;
      }
      
      // Safely update the chart data
      try {
        // First, backup existing data in case of failure
        const originalData = { ...chart.data };
        
        // Update the data
        chart.data = { ...originalData, ...newData };
        
        // Check for empty datasets to avoid Chart.js errors
        if (!chart.data.datasets || chart.data.datasets.length === 0) {
          console.warn('Chart update attempted with empty datasets, providing default empty dataset');
          chart.data.datasets = [{ data: [] }];
        }
        
        // Safely call update
        try {
          chart.update();
          console.log('Chart updated successfully');
        } catch (updateErr) {
          console.error('Error during chart update operation:', updateErr);
          
          // Attempt to restore original data
          try {
            chart.data = originalData;
            chart.update();
            console.log('Restored chart to original data after update failure');
          } catch (restoreErr) {
            console.error('Failed to restore chart to original data:', restoreErr);
          }
        }
      } catch (dataErr) {
        console.error('Error manipulating chart data:', dataErr);
      }
    } catch (err) {
      console.error('Unexpected error updating chart:', err);
    }
  }
};

// Socket.io event utilities
AstroBotUtils.socket = {
  /**
   * Setup event handlers for socket.io events
   * @param {SocketIO.Socket} socket - Socket.io socket instance
   * @param {Object} handlers - Object mapping event names to handler functions
   */
  setupSocketEventHandlers: function(socket, handlers = {}) {
    try {
      // Validate inputs
      if (!socket) {
        console.warn('No socket instance provided');
        return;
      }
      
      if (typeof socket !== 'object') {
        console.warn('Socket is not a valid object');
        return;
      }
      
      if (typeof socket.on !== 'function') {
        console.warn('Socket does not have an "on" method');
        return;
      }
      
      if (!handlers || typeof handlers !== 'object') {
        console.warn('No handlers provided or handlers is not an object');
        return;
      }
      
      // Register event handlers with error handling for each
      let registeredCount = 0;
      
      Object.entries(handlers).forEach(([event, handler]) => {
        try {
          if (!event) {
            console.warn('Empty event name detected, skipping');
            return;
          }
          
          if (typeof handler !== 'function') {
            console.warn(`Handler for event "${event}" is not a function, skipping`);
            return;
          }
          
          // Create a wrapped handler with its own try/catch
          const safeHandler = (...args) => {
            try {
              handler(...args);
            } catch (handlerErr) {
              console.error(`Error in socket event handler for "${event}":`, handlerErr);
            }
          };
          
          // Register the handler
          socket.on(event, safeHandler);
          registeredCount++;
        } catch (registerErr) {
          console.error(`Failed to register handler for event "${event}":`, registerErr);
        }
      });
      
      console.log(`Socket event handlers registered successfully (${registeredCount} handlers)`);
      
      // Add a generic error handler if not already present
      if (!handlers.error && typeof socket.on === 'function') {
        try {
          socket.on('error', (err) => {
            console.error('Socket.io error:', err);
          });
          console.log('Added generic socket error handler');
        } catch (errorHandlerErr) {
          console.warn('Failed to add generic socket error handler:', errorHandlerErr);
        }
      }
      
      // Add a disconnect handler if not already present
      if (!handlers.disconnect && typeof socket.on === 'function') {
        try {
          socket.on('disconnect', (reason) => {
            console.warn(`Socket disconnected: ${reason}`);
          });
          console.log('Added socket disconnect handler');
        } catch (disconnectHandlerErr) {
          console.warn('Failed to add socket disconnect handler:', disconnectHandlerErr);
        }
      }
      
      // Add reconnect handler if not already present
      if (!handlers.reconnect && typeof socket.on === 'function') {
        try {
          socket.on('reconnect', (attemptNumber) => {
            console.log(`Socket reconnected after ${attemptNumber} attempts`);
          });
          console.log('Added socket reconnect handler');
        } catch (reconnectHandlerErr) {
          console.warn('Failed to add socket reconnect handler:', reconnectHandlerErr);
        }
      }
    } catch (err) {
      console.error('Error setting up socket event handlers:', err);
    }
  }
};

// Theme utilities
AstroBotUtils.theme = {
  /**
   * Get current theme from body class
   * @returns {string} Theme name ('light', 'dark', 'space', 'neon', 'contrast')
   */
  getCurrentTheme: function() {
    try {
      // Check if document.body exists
      if (!document || !document.body) {
        console.warn('Document body not available for theme detection');
        return 'light'; // Default to light theme if body is not accessible
      }
      
      // Safely get body classes
      const bodyClasses = document.body.className || '';
      
      // Check for theme classes in order of precedence
      if (bodyClasses.includes('theme-contrast')) return 'contrast';
      if (bodyClasses.includes('theme-neon')) return 'neon';
      if (bodyClasses.includes('theme-space')) return 'space';
      if (bodyClasses.includes('theme-dark')) return 'dark';
      
      // Default to light theme
      return 'light';
    } catch (err) {
      console.error('Error detecting current theme:', err);
      return 'light'; // Fail safely to light theme
    }
  },
  
  /**
   * Get color scheme for the current theme
   * @param {string} [specificTheme] - Optional specific theme to get colors for
   * @returns {Object} Color scheme object
   */
  getThemeColors: function(specificTheme) {
    try {
      // Get theme, either from parameter or current theme
      const theme = specificTheme || this.getCurrentTheme();
      
      // Define all theme color schemes
      const themeColors = {
        light: {
          primary: '#007bff',
          secondary: '#6c757d',
          success: '#28a745',
          info: '#17a2b8',
          warning: '#ffc107',
          danger: '#dc3545',
          purple: '#6f42c1',
          pink: '#e83e8c',
          orange: '#fd7e14',
          text: '#212529',
          background: '#ffffff',
          border: '#dee2e6'
        },
        dark: {
          primary: '#375a7f',
          secondary: '#6c757d',
          success: '#00bc8c',
          info: '#3498db',
          warning: '#f39c12',
          danger: '#e74c3c',
          purple: '#8c44ad',
          pink: '#e83e8c',
          orange: '#fd7e14',
          text: '#ffffff',
          background: '#212529',
          border: '#495057'
        },
        space: {
          primary: '#7269ef',
          secondary: '#6c757d',
          success: '#06d6a0',
          info: '#3fc5f0',
          warning: '#ffd166',
          danger: '#ef476f',
          purple: '#9681eb',
          pink: '#e83e8c',
          orange: '#fd7e14',
          text: '#e9ecef',
          background: '#121212',
          border: '#343a40'
        },
        neon: {
          primary: '#00eeff',
          secondary: '#6c757d',
          success: '#39ff14',
          info: '#00ffff',
          warning: '#ffff00',
          danger: '#ff0080',
          purple: '#bf00ff',
          pink: '#ff00ff',
          orange: '#ff8000',
          text: '#ffffff',
          background: '#0d0221',
          border: '#2d3748'
        },
        contrast: {
          primary: '#ffff00',
          secondary: '#ffffff',
          success: '#00ff00',
          info: '#00ffff',
          warning: '#ffaa00',
          danger: '#ff0000',
          purple: '#cc99ff',
          pink: '#ff66ff',
          orange: '#ffaa00',
          text: '#ffffff',
          background: '#000000',
          border: '#ffffff'
        }
      };
      
      // Return theme colors or fall back to light theme
      return themeColors[theme] || themeColors.light;
    } catch (err) {
      console.error('Error getting theme colors:', err);
      
      // Return basic light theme as a fallback
      return {
        primary: '#007bff',
        secondary: '#6c757d',
        success: '#28a745',
        danger: '#dc3545',
        text: '#212529',
        background: '#ffffff'
      };
    }
  },
  
  /**
   * Apply theme colors to a chart configuration
   * @param {Object} chartConfig - Chart.js configuration object
   * @returns {Object} Modified chart configuration with theme-appropriate colors
   */
  applyThemeToChart: function(chartConfig) {
    try {
      if (!chartConfig) {
        console.warn('No chart configuration provided');
        return {};
      }
      
      const colors = this.getThemeColors();
      const isLightTheme = this.getCurrentTheme() === 'light';
      
      // Create a deep copy to avoid modifying the original
      const modifiedConfig = JSON.parse(JSON.stringify(chartConfig));
      
      // Set defaults if they don't exist
      if (!modifiedConfig.options) modifiedConfig.options = {};
      if (!modifiedConfig.options.scales) modifiedConfig.options.scales = {};
      if (!modifiedConfig.options.plugins) modifiedConfig.options.plugins = {};
      
      // Apply theme to global options
      modifiedConfig.options.color = colors.text;
      
      // Apply theme to axes if they exist
      const axes = ['x', 'y', 'r'];
      axes.forEach(axis => {
        if (modifiedConfig.options.scales[axis]) {
          modifiedConfig.options.scales[axis].grid = modifiedConfig.options.scales[axis].grid || {};
          modifiedConfig.options.scales[axis].grid.color = isLightTheme ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)';
          modifiedConfig.options.scales[axis].ticks = modifiedConfig.options.scales[axis].ticks || {};
          modifiedConfig.options.scales[axis].ticks.color = colors.text;
        }
      });
      
      // Apply theme to legend
      if (modifiedConfig.options.plugins.legend) {
        modifiedConfig.options.plugins.legend.labels = modifiedConfig.options.plugins.legend.labels || {};
        modifiedConfig.options.plugins.legend.labels.color = colors.text;
      }
      
      // Apply theme to tooltip
      if (modifiedConfig.options.plugins.tooltip) {
        modifiedConfig.options.plugins.tooltip.backgroundColor = isLightTheme ? 'rgba(0,0,0,0.7)' : 'rgba(255,255,255,0.7)';
        modifiedConfig.options.plugins.tooltip.titleColor = isLightTheme ? '#fff' : '#000';
        modifiedConfig.options.plugins.tooltip.bodyColor = isLightTheme ? '#fff' : '#000';
      }
      
      return modifiedConfig;
    } catch (err) {
      console.error('Error applying theme to chart:', err);
      return chartConfig || {}; // Return original if there's an error
    }
  }
};