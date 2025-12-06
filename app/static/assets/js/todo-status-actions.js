/**
 * Centralized Todo Status Actions
 * Handles marking todos as done, KIV, or deleting them across all pages
 * This prevents regressions by maintaining consistent behavior
 */

var TodoStatusActions = (function() {
    'use strict';

    /**
     * Mark a todo as done
     * @param {string} todoId - The ID of the todo to mark as done
     * @param {string} csrfToken - CSRF token for the request
     * @param {string} redirectUrl - Where to redirect after success (optional)
     */
    function markAsDone(todoId, csrfToken, redirectUrl = null) {
        return fetch('/' + todoId + '/done', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: '_csrf_token=' + encodeURIComponent(csrfToken)
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            // Redirect to specified URL or stay on current page
            if (redirectUrl) {
                window.location.href = redirectUrl;
            } else {
                window.location.reload();
            }
        });
    }

    /**
     * Mark a todo as KIV (Keep In View)
     * Always redirects to undone page with KIV tab active
     * @param {string} todoId - The ID of the todo to mark as KIV
     * @param {string} csrfToken - CSRF token for the request
     */
    function markAsKiv(todoId, csrfToken) {
        return fetch('/' + todoId + '/kiv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: '_csrf_token=' + encodeURIComponent(csrfToken)
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            // Always redirect to undone page with KIV tab active
            window.location.href = '/undone?tab=kiv';
        });
    }

    /**
     * Delete a todo
     * @param {string} todoId - The ID of the todo to delete
     * @param {string} csrfToken - CSRF token for the request
     * @param {string} redirectUrl - Where to redirect after success (optional)
     */
    function deleteTodo(todoId, csrfToken, redirectUrl = null) {
        return fetch('/' + todoId + '/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: '_csrf_token=' + encodeURIComponent(csrfToken)
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            // Redirect to specified URL or reload page
            if (redirectUrl) {
                window.location.href = redirectUrl;
            } else {
                window.location.reload();
            }
        });
    }

    /**
     * Setup loading state for a button during action
     * @param {Element} button - The button element
     * @param {boolean} isLoading - Whether to show loading state
     */
    function setLoadingState(button, isLoading) {
        if (!button) return;
        
        const icon = button.querySelector('.done-icon, .kiv-icon, .close-icon') || 
                    button.querySelector('.mdi:not(.mdi-loading)');
        const loading = button.querySelector('.done-loading, .kiv-loading, .close-loading') || 
                       button.querySelector('.mdi-loading');
        
        if (isLoading) {
            if (icon) icon.style.display = 'none';
            if (loading) loading.style.display = '';
            button.disabled = true;
        } else {
            if (icon) icon.style.display = '';
            if (loading) loading.style.display = 'none';
            button.disabled = false;
        }
    }

    /**
     * Initialize status actions for a page with event delegation
     * This prevents issues with dynamic content and ensures all actions work consistently
     * @param {string} csrfToken - CSRF token for requests
     * @param {Object} options - Configuration options
     */
    function initialize(csrfToken, options = {}) {
        if (!csrfToken) {
            console.error('TodoStatusActions: CSRF token is required');
            return;
        }

        // Use event delegation to handle dynamically added elements
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.done, .kiv, .close-todo');
            if (!btn) return;
            
            e.preventDefault();
            
            const todoId = btn.dataset.id;
            if (!todoId) {
                console.error('TodoStatusActions: Button missing data-id attribute');
                return;
            }
            
            setLoadingState(btn, true);
            
            let actionPromise;
            
            if (btn.classList.contains('done')) {
                actionPromise = markAsDone(todoId, csrfToken, options.doneRedirectUrl);
            } else if (btn.classList.contains('kiv')) {
                actionPromise = markAsKiv(todoId, csrfToken);
            } else if (btn.classList.contains('close-todo')) {
                // Show confirmation before deleting
                const todoTitle = btn.closest('.card-body')?.querySelector('.card-title')?.textContent?.trim() || 'this todo';
                
                if (confirm('Are you sure you want to delete "' + todoTitle + '"? This action cannot be undone.')) {
                    actionPromise = deleteTodo(todoId, csrfToken, options.deleteRedirectUrl);
                } else {
                    setLoadingState(btn, false);
                    return;
                }
            }
            
            if (actionPromise) {
                actionPromise.catch(function(error) {
                    console.error('TodoStatusActions: Action failed', error);
                    setLoadingState(btn, false);
                    // Optional: Show user-friendly error message
                    if (options.showErrors) {
                        alert('An error occurred. Please try again.');
                    }
                });
            }
        });
    }

    /**
     * Handle auto-switching to KIV tab based on URL parameter
     * Should be called on the undone page
     */
    function handleKivTabSwitch() {
        const urlParams = new URLSearchParams(window.location.search);
        const tabParam = urlParams.get('tab');
        
        if (tabParam === 'kiv') {
            // Wait for DOM to be ready
            setTimeout(function() {
                const kivTab = document.querySelector('#taskTabs a[href="#kiv"]');
                if (kivTab) {
                    // Trigger click to switch tab
                    kivTab.click();
                    // Clean up URL parameter
                    window.history.replaceState({}, '', window.location.pathname);
                }
            }, 100);
        }
    }

    // Public API
    return {
        initialize: initialize,
        markAsDone: markAsDone,
        markAsKiv: markAsKiv,
        deleteTodo: deleteTodo,
        setLoadingState: setLoadingState,
        handleKivTabSwitch: handleKivTabSwitch
    };
})();