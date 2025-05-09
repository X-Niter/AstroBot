/** 
 * Alpine.js collapse plugin implementation 
 * This is a simplified version for our usage with robust error handling
 */
document.addEventListener('alpine:init', () => {
    try {
        // Make sure Alpine is available
        if (typeof window === 'undefined' || !window.Alpine) {
            console.warn('Alpine.js not found - cannot initialize alpine-collapse. Will try again later.');
            return;
        }
        
        // Skip if collapse is already registered
        if (window.Alpine.collapse) {
            console.log('Alpine.collapse already registered, skipping custom implementation');
            return;
        }
        
        console.log('Registering custom Alpine.js collapse plugin implementation');
    } catch (e) {
        console.error('Error during alpine-collapse initialization check:', e);
        return;
    }
    
    // Register the custom directive inside try/catch block
    try {
        window.Alpine.directive('collapse', (el, { modifiers, expression }, { effect, evaluateLater, cleanup }) => {
            try {
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
                    try {
                        evaluate(value => {
                            if (value) {
                                expand();
                            } else {
                                collapse();
                            }
                        });
                    } catch (e) {
                        console.warn('Error in collapse directive effect:', e);
                    }
                });
                
                // Clean up transitions when element is removed
                cleanup(() => {
                    try {
                        if (transitionEndCallback) el.removeEventListener('transitionend', transitionEndCallback);
                    } catch (e) {
                        console.warn('Error in collapse cleanup:', e);
                    }
                });
                
                // Collapse function
                let transitionEndCallback;
                function collapse() {
                    try {
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
                            try {
                                el.style.transition = '';
                                isCollapsed = true;
                                el.removeEventListener('transitionend', transitionEndCallback);
                            } catch (e) {
                                console.warn('Error in collapse transitionEnd:', e);
                            }
                        };
                        el.addEventListener('transitionend', transitionEndCallback);
                    } catch (e) {
                        console.warn('Error in collapse function:', e);
                    }
                }
                
                // Expand function
                function expand() {
                    try {
                        if (!isCollapsed) return;
                        
                        // Set transition
                        el.style.transition = `height ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
                        
                        // Get target height
                        const height = el.scrollHeight;
                        
                        // Set height
                        el.style.height = height + 'px';
                        
                        // Reset after transition
                        transitionEndCallback = () => {
                            try {
                                el.style.height = 'auto';
                                el.style.transition = '';
                                el.style.overflow = '';
                                isCollapsed = false;
                                el.removeEventListener('transitionend', transitionEndCallback);
                            } catch (e) {
                                console.warn('Error in expand transitionEnd:', e);
                            }
                        };
                        el.addEventListener('transitionend', transitionEndCallback);
                    } catch (e) {
                        console.warn('Error in expand function:', e);
                    }
                }
            } catch (e) {
                console.error('Error setting up collapse directive:', e);
            }
        });
        
        // Add the x-collapse attribute magic for more convenient usage
        window.Alpine.magic('collapse', el => {
            return {
                toggle() {
                    try {
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
                                try {
                                    el.style.height = 'auto';
                                    el.style.overflow = '';
                                    el.removeEventListener('transitionend', handler);
                                } catch (e) {
                                    console.warn('Error in toggle transitionEnd:', e);
                                }
                            }, { once: true });
                        }
                    } catch (e) {
                        console.warn('Error in collapse toggle function:', e);
                    }
                }
            };
        });
        
        console.log('Successfully registered collapse directive and magic');
    } catch (e) {
        console.error('Error registering collapse directive or magic:', e);
    }
});