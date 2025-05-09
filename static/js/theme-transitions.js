/**
 * Theme Transitions
 * 
 * This file provides smooth transitions between themes
 * and handles theme-related UI effects.
 */

// Add transition classes to enable smooth theme changes
document.addEventListener('DOMContentLoaded', () => {
    // Add transition class to body after a small delay to prevent
    // transition on initial page load
    setTimeout(() => {
        document.body.classList.add('theme-transition');
        
        const elementsToTransition = [
            'a', 'button', 'input', 'select', 'textarea',
            '.card', '.navbar', '.sidebar', '.footer',
            '.bg-primary', '.bg-secondary', '.text-primary',
            '.border', '.shadow', '.modal', '.dropdown-menu',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span'
        ];
        
        elementsToTransition.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                el.classList.add('theme-transition');
            });
        });
    }, 300);
    
    // Listen for theme changes to add special effects
    window.addEventListener('theme-changed', ({ detail }) => {
        const { theme } = detail;
        
        // Special effects for premium themes
        if (theme === 'space') {
            addSpaceEffects();
        } else if (theme === 'neon') {
            addNeonEffects();
        } else if (theme === 'contrast') {
            addContrastEffects();
        } else {
            // Remove any special effects if switching to standard themes
            removeSpecialEffects();
        }
    });
});

// Space theme special effects
function addSpaceEffects() {
    // Create star background
    const starsContainer = document.createElement('div');
    starsContainer.id = 'stars-background';
    starsContainer.classList.add('fixed', 'inset-0', 'pointer-events-none', 'z-[-1]', 'opacity-70');
    starsContainer.style.background = 'radial-gradient(circle, rgba(255,255,255,0.8) 1px, transparent 1px)';
    starsContainer.style.backgroundSize = '30px 30px';
    document.body.appendChild(starsContainer);
    
    // Add subtle floating animation to certain elements
    document.querySelectorAll('.card, .navbar-brand, .btn-primary, img').forEach(el => {
        el.classList.add('hover:animate-float');
    });
}

// Neon theme special effects
function addNeonEffects() {
    // Add neon text glow to headings
    document.querySelectorAll('h1, h2, h3, h4, h5, h6, .navbar-brand').forEach(el => {
        el.classList.add('neon-glow');
        el.style.textShadow = '0 0 5px rgba(0, 255, 255, 0.8), 0 0 10px rgba(0, 255, 255, 0.5)';
    });
    
    // Add neon box glow to cards and buttons
    document.querySelectorAll('.card, .btn-primary').forEach(el => {
        el.classList.add('neon-box-glow');
        el.style.boxShadow = '0 0 5px rgba(0, 255, 255, 0.8), 0 0 15px rgba(0, 255, 255, 0.3)';
        
        // Add neon border
        el.style.borderColor = 'rgb(0, 255, 255)';
    });
}

// High contrast theme special effects
function addContrastEffects() {
    // Increase focus outlines for accessibility
    document.querySelectorAll('a, button, input, select, textarea').forEach(el => {
        el.addEventListener('focus', () => {
            el.style.outline = '4px solid rgb(255, 255, 0)';
        });
        
        el.addEventListener('blur', () => {
            el.style.outline = '';
        });
    });
    
    // Increase text size slightly
    document.body.style.fontSize = '1.05em';
}

// Remove all special theme effects
function removeSpecialEffects() {
    // Remove star background
    const starsBackground = document.getElementById('stars-background');
    if (starsBackground) {
        starsBackground.remove();
    }
    
    // Remove floating animations
    document.querySelectorAll('.hover\\:animate-float').forEach(el => {
        el.classList.remove('hover:animate-float');
    });
    
    // Remove neon glow effects
    document.querySelectorAll('.neon-glow, .neon-box-glow').forEach(el => {
        el.classList.remove('neon-glow', 'neon-box-glow');
        el.style.textShadow = '';
        el.style.boxShadow = '';
        el.style.borderColor = '';
    });
    
    // Reset font size
    document.body.style.fontSize = '';
    
    // Remove focus event listeners (not easily possible, but we can reset the styles)
    document.querySelectorAll('a, button, input, select, textarea').forEach(el => {
        el.style.outline = '';
    });
}