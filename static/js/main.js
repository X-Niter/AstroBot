document.addEventListener('DOMContentLoaded', function() {
    // Theme initialization - check for premium themes
    initializeTheme();

    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // Initialize popovers
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => {
        new bootstrap.Popover(popover);
    });

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm actions
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // Toggle sidebar on mobile
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('d-none');
        });
    }

    // Highlight active sidebar item
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-item a');
    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.parentElement.classList.add('active');
        }
    });

    // Handle copy to clipboard
    const clipboardButtons = document.querySelectorAll('.btn-clipboard');
    clipboardButtons.forEach(button => {
        button.addEventListener('click', function() {
            const target = document.querySelector(this.dataset.clipboardTarget);
            if (target) {
                navigator.clipboard.writeText(target.textContent).then(function() {
                    const originalText = button.innerHTML;
                    button.innerHTML = '<i class="bi bi-check"></i> Copied!';
                    setTimeout(() => {
                        button.innerHTML = originalText;
                    }, 2000);
                }).catch(function(err) {
                    console.error('Could not copy text: ', err);
                });
            }
        });
    });

    // Add animation to elements with fade-in class
    const fadeElements = document.querySelectorAll('.fade-in');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });

    fadeElements.forEach(element => {
        element.style.opacity = 0;
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(element);
    });

    // Theme switcher in settings
    const themeSwitchers = document.querySelectorAll('.theme-switcher');
    themeSwitchers.forEach(switcher => {
        switcher.addEventListener('click', function(e) {
            e.preventDefault();
            const theme = this.dataset.theme;
            if (theme) {
                updateTheme(theme);
                // Send to server via fetch (for logged in users)
                if (this.dataset.savePreference === 'true') {
                    fetch('/api/preferences/theme', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken()
                        },
                        body: JSON.stringify({ theme: theme })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showToast('Theme updated successfully!', 'success');
                        } else {
                            showToast('Failed to update theme preference', 'danger');
                        }
                    })
                    .catch(error => {
                        console.error('Error updating theme preference:', error);
                    });
                }
            }
        });
    });
});

/**
 * Initialize the theme based on user preferences
 */
function initializeTheme() {
    const body = document.body;
    const themePreference = body.dataset.theme || 'dark';
    const htmlElement = document.documentElement;
    
    // Apply the appropriate Bootstrap theme
    if (themePreference === 'light') {
        htmlElement.setAttribute('data-bs-theme', 'light');
    } else {
        htmlElement.setAttribute('data-bs-theme', 'dark');
    }
    
    // Apply theme class to body
    body.className = body.className.replace(/theme-\w+/g, '').trim();
    body.classList.add(`theme-${themePreference}`);
    
    // Apply custom theme CSS for premium themes
    if (['space', 'neon', 'contrast'].includes(themePreference)) {
        applyCustomThemeCSS(themePreference);
    }
    
    // Store theme preference in localStorage for guests
    localStorage.setItem('theme_preference', themePreference);
    
    // Set theme color variables based on the chosen theme
    setThemeColorVariables(themePreference);
}

/**
 * Set CSS variables for colors based on the active theme
 * This ensures consistent color usage throughout the app
 */
function setThemeColorVariables(theme) {
    const root = document.documentElement;
    
    // Default color values (can be overridden by theme-specific CSS)
    let primaryColor = getComputedStyle(root).getPropertyValue('--primary-color').trim();
    let primaryColorRGB = hexToRgb(primaryColor.replace('#', ''));
    
    // Set RGB variables for transparency operations
    if (primaryColorRGB) {
        root.style.setProperty('--primary-color-rgb', `${primaryColorRGB.r}, ${primaryColorRGB.g}, ${primaryColorRGB.b}`);
    }
    
    // Calculate light and dark variants of the primary color if not already set
    if (!getComputedStyle(root).getPropertyValue('--primary-color-light').trim()) {
        const lightVariant = adjustColorBrightness(primaryColor, 20);
        root.style.setProperty('--primary-color-light', lightVariant);
    }
    
    if (!getComputedStyle(root).getPropertyValue('--primary-color-dark').trim()) {
        const darkVariant = adjustColorBrightness(primaryColor, -20);
        root.style.setProperty('--primary-color-dark', darkVariant);
    }
}

/**
 * Convert hex color to RGB
 */
function hexToRgb(hex) {
    if (!hex) return null;
    
    const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    hex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
    
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

/**
 * Adjust color brightness (positive value for lighter, negative for darker)
 */
function adjustColorBrightness(color, percent) {
    if (!color) return null;
    
    const rgb = hexToRgb(color.replace('#', ''));
    if (!rgb) return color;
    
    const adjustValue = (value) => {
        value = Math.floor(value * (1 + percent / 100));
        return Math.min(255, Math.max(0, value));
    };
    
    const r = adjustValue(rgb.r);
    const g = adjustValue(rgb.g);
    const b = adjustValue(rgb.b);
    
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}

/**
 * Update the theme based on selection
 */
function updateTheme(theme) {
    const body = document.body;
    const htmlElement = document.documentElement;
    
    // Update data-theme attribute
    body.dataset.theme = theme;
    body.className = body.className.replace(/theme-\w+/g, `theme-${theme}`);
    
    // Update Bootstrap's data-bs-theme
    if (theme === 'light') {
        htmlElement.setAttribute('data-bs-theme', 'light');
    } else {
        htmlElement.setAttribute('data-bs-theme', 'dark');
    }
    
    // Remove any previously injected theme stylesheets
    const existingThemeStyle = document.getElementById('dynamic-theme-style');
    if (existingThemeStyle) {
        existingThemeStyle.remove();
    }
    
    // Apply custom theme CSS for premium themes
    if (['space', 'neon', 'contrast'].includes(theme)) {
        applyCustomThemeCSS(theme);
    }
    
    // Store theme preference in localStorage for guests
    localStorage.setItem('theme_preference', theme);
    
    // Update theme color variables after a slight delay to allow the CSS to load
    setTimeout(() => {
        setThemeColorVariables(theme);
    }, 50);
    
    // Update theme card selections in settings page
    updateThemeCardSelections(theme);
    
    // Add a subtle transition effect for theme change
    const transitionOverlay = document.createElement('div');
    transitionOverlay.style.position = 'fixed';
    transitionOverlay.style.top = '0';
    transitionOverlay.style.left = '0';
    transitionOverlay.style.width = '100%';
    transitionOverlay.style.height = '100%';
    transitionOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.15)';
    transitionOverlay.style.zIndex = '9999';
    transitionOverlay.style.opacity = '0';
    transitionOverlay.style.pointerEvents = 'none';
    transitionOverlay.style.transition = 'opacity 0.3s ease';
    document.body.appendChild(transitionOverlay);
    
    setTimeout(() => {
        transitionOverlay.style.opacity = '0.15';
        setTimeout(() => {
            transitionOverlay.style.opacity = '0';
            setTimeout(() => {
                transitionOverlay.remove();
            }, 300);
        }, 100);
    }, 0);
}

/**
 * Apply custom theme CSS 
 */
function applyCustomThemeCSS(theme) {
    const link = document.createElement('link');
    link.id = 'dynamic-theme-style';
    link.rel = 'stylesheet';
    link.href = `/static/css/themes/${theme}.css`;
    document.head.appendChild(link);
}

/**
 * Get CSRF token from meta tag
 */
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

/**
 * Update theme card selections (highlight active card, remove highlights from others)
 */
function updateThemeCardSelections(theme) {
    // Find all theme cards in the settings page
    const themeCards = document.querySelectorAll('[data-theme]');
    
    if (themeCards.length > 0) {
        // Remove border-primary from all theme cards
        themeCards.forEach(card => {
            card.classList.remove('border-primary');
        });
        
        // Add border-primary to the selected theme card
        const selectedCard = document.querySelector(`[data-theme="${theme}"]`);
        if (selectedCard) {
            selectedCard.classList.add('border-primary');
            
            // Check the radio button
            const radioButton = document.getElementById(`theme-${theme}`);
            if (radioButton) {
                radioButton.checked = true;
            }
            
            // Show toast notification
            showToast(`${theme.charAt(0).toUpperCase() + theme.slice(1)} theme applied`, 'success');
        }
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    document.getElementById('toast-container').appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Auto-remove after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}