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
    
    // Apply custom theme CSS for premium themes
    if (['space', 'neon', 'contrast'].includes(themePreference)) {
        applyCustomThemeCSS(themePreference);
    }
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
    
    // Update theme card selections in settings page
    updateThemeCardSelections(theme);
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