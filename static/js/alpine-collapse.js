/** 
 * Alpine.js collapse plugin implementation 
 * This is a simplified version for our usage
 */
document.addEventListener('alpine:init', () => {
    window.Alpine.directive('collapse', (el, { modifiers, expression }, { effect, evaluateLater, cleanup }) => {
        const evaluate = evaluateLater(expression);
        
        // Get duration from modifiers or use default
        const duration = modifiers.includes('slow') 
            ? 300 
            : modifiers.includes('fast') 
                ? 100 
                : 200;
                
        // Handle initial state
        let isCollapsed = !el.style.height;
        
        // Default to closed if no initial height
        if (isCollapsed) {
            el.style.height = '0px';
            el.style.overflow = 'hidden';
        }
        
        // Watch for changes
        effect(() => {
            evaluate(value => {
                if (value) {
                    expand();
                } else {
                    collapse();
                }
            });
        });
        
        // Clean up transitions when element is removed
        cleanup(() => {
            if (transitionEndCallback) el.removeEventListener('transitionend', transitionEndCallback);
        });
        
        // Collapse function
        let transitionEndCallback;
        function collapse() {
            if (isCollapsed) return;
            
            // Get current height
            const height = el.scrollHeight;
            el.style.height = height + 'px';
            
            // Force a reflow
            void el.offsetHeight;
            
            // Add transition
            el.style.transition = `height ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
            el.style.overflow = 'hidden';
            
            // Set height to 0
            el.style.height = '0px';
            
            // Remove transition after animation completes
            transitionEndCallback = () => {
                el.style.transition = '';
                isCollapsed = true;
                el.removeEventListener('transitionend', transitionEndCallback);
            };
            el.addEventListener('transitionend', transitionEndCallback);
        }
        
        // Expand function
        function expand() {
            if (!isCollapsed) return;
            
            // Set transition
            el.style.transition = `height ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
            
            // Get target height
            const height = el.scrollHeight;
            
            // Set height
            el.style.height = height + 'px';
            
            // Reset after transition
            transitionEndCallback = () => {
                el.style.height = 'auto';
                el.style.transition = '';
                el.style.overflow = '';
                isCollapsed = false;
                el.removeEventListener('transitionend', transitionEndCallback);
            };
            el.addEventListener('transitionend', transitionEndCallback);
        }
    });
    
    // Add the x-collapse attribute directive for more convenient usage
    window.Alpine.magic('collapse', el => ({
        toggle() {
            let isOpen = (el.style.height !== '0px' && el.style.height !== '');
            
            if (isOpen) {
                // Current height
                const height = el.scrollHeight;
                el.style.height = height + 'px';
                
                // Force reflow
                void el.offsetHeight;
                
                // Collapse
                el.style.transition = 'height 200ms cubic-bezier(0.4, 0, 0.2, 1)';
                el.style.overflow = 'hidden';
                el.style.height = '0px';
            } else {
                // Expand
                el.style.transition = 'height 200ms cubic-bezier(0.4, 0, 0.2, 1)';
                
                // Scroll height
                const height = el.scrollHeight;
                el.style.height = height + 'px';
                
                // Listen for transition end
                el.addEventListener('transitionend', function handler() {
                    el.style.height = 'auto';
                    el.style.overflow = '';
                    el.removeEventListener('transitionend', handler);
                }, { once: true });
            }
        }
    }));
});