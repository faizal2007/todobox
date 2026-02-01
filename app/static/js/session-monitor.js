/**
 * Session Expiration Monitor - Client-Side
 * 
 * Monitors user session activity and automatically logs out or shows warnings
 * when the user is inactive for extended periods.
 * 
 * Works seamlessly with server-side SessionExpirationHandler (app/session_handler.py)
 */

class SessionExpirationMonitor {
    /**
     * Initialize the session monitor
     * 
     * @param {Object} options - Configuration options
     * @param {number} options.checkInterval - Check interval in milliseconds (default: 1 minute)
     * @param {number} options.warningTime - Time before logout to show warning in minutes (default: 10)
     * @param {boolean} options.autoLogout - Auto logout on expiration (default: true)
     * @param {Function} options.onWarning - Callback when warning should be shown
     * @param {Function} options.onExpired - Callback when session expires
     * @param {Function} options.onExtended - Callback when session is extended
     */
    constructor(options = {}) {
        this.checkInterval = options.checkInterval || 60000; // 1 minute
        this.warningTime = options.warningTime || 10; // minutes
        this.autoLogout = options.autoLogout !== false;
        this.onWarning = options.onWarning || this.defaultWarningHandler;
        this.onExpired = options.onExpired || this.defaultExpiredHandler;
        this.onExtended = options.onExtended || null;
        
        this.monitoringActive = false;
        this.monitoringTimer = null;
        this.lastSessionStatus = null;
        this.warningShown = false;
        this.sessionExpiredMessageShown = false;
        
        // Track visibility changes (tab switch)
        this.visibilityHidden = document.hidden;
        
        this.init();
    }
    
    /**
     * Initialize the monitor
     */
    init() {
        // Start monitoring on page load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.start());
        } else {
            this.start();
        }
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => this.handleVisibilityChange());
        
        // Extend session on user activity
        this.registerActivityListeners();
    }
    
    /**
     * Start monitoring the session
     */
    start() {
        if (this.monitoringActive) return;
        
        console.log('[SessionMonitor] Starting session monitoring...');
        this.monitoringActive = true;
        this.warningShown = false;
        this.sessionExpiredMessageShown = false;
        
        // Check immediately
        this.checkSession();
        
        // Then check periodically
        this.monitoringTimer = setInterval(() => this.checkSession(), this.checkInterval);
    }
    
    /**
     * Stop monitoring the session
     */
    stop() {
        if (!this.monitoringActive) return;
        
        console.log('[SessionMonitor] Stopping session monitoring...');
        this.monitoringActive = false;
        
        if (this.monitoringTimer) {
            clearInterval(this.monitoringTimer);
            this.monitoringTimer = null;
        }
    }
    
    /**
     * Check current session status from server
     */
    async checkSession() {
        try {
            const response = await fetch('/api/session-status', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                console.warn('[SessionMonitor] Failed to check session status:', response.status);
                return;
            }
            
            const status = await response.json();
            this.handleSessionStatus(status);
            
        } catch (error) {
            console.error('[SessionMonitor] Error checking session:', error);
        }
    }
    
    /**
     * Handle session status response
     * 
     * @param {Object} status - Session status from server
     * @param {boolean} status.is_authenticated - User is logged in
     * @param {boolean} status.is_expired - Session has expired
     * @param {boolean} status.is_warning - Warning threshold reached
     * @param {number} status.remaining_minutes - Minutes until expiration
     */
    handleSessionStatus(status) {
        this.lastSessionStatus = status;
        
        // Not authenticated - no monitoring needed
        if (!status.is_authenticated) {
            this.stop();
            return;
        }
        
        // Session has expired
        if (status.is_expired) {
            if (!this.sessionExpiredMessageShown) {
                this.sessionExpiredMessageShown = true;
                console.log('[SessionMonitor] Session expired!');
                this.onExpired(status);
                
                if (this.autoLogout) {
                    this.handleExpiredSession();
                }
            }
            return;
        }
        
        // Warning threshold reached
        if (status.is_warning) {
            if (!this.warningShown) {
                this.warningShown = true;
                console.log('[SessionMonitor] Session warning:', status.remaining_minutes, 'minutes remaining');
                this.onWarning(status);
            }
        } else {
            // Session is valid and no warning
            this.warningShown = false;
            this.sessionExpiredMessageShown = false;
        }
    }
    
    /**
     * Handle expired session
     */
    handleExpiredSession() {
        console.log('[SessionMonitor] Handling expired session...');
        
        // Stop monitoring
        this.stop();
        
        // Redirect to login
        window.location.href = '/login?expired=true';
    }
    
    /**
     * Default warning handler - show modal/alert
     * 
     * @param {Object} status - Session status
     */
    defaultWarningHandler(status) {
        // Try to show in-app warning first
        if (typeof showSessionWarning === 'function') {
            showSessionWarning(status.remaining_minutes);
            return;
        }
        
        // Fallback to browser alert
        const message = `⏰ Your session will expire in ${status.remaining_minutes} minutes due to inactivity. ` +
            `Keep working to extend your session.`;
        console.warn('[SessionMonitor]', message);
    }
    
    /**
     * Default expired handler - show notification
     * 
     * @param {Object} status - Session status
     */
    defaultExpiredHandler(status) {
        const message = '❌ Your session has expired due to inactivity. You will be logged out.';
        console.error('[SessionMonitor]', message);
        
        // Show notification if available
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Session Expired', {
                body: message,
                icon: '/static/favicon.ico'
            });
        }
    }
    
    /**
     * Register activity listeners to extend session
     */
    registerActivityListeners() {
        // List of events that indicate user activity
        const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
        
        // Use event delegation with debouncing
        let activityTimeout = null;
        
        const handleActivity = () => {
            clearTimeout(activityTimeout);
            activityTimeout = setTimeout(() => {
                this.extendSession();
            }, 1000); // Debounce: only extend once per second of activity
        };
        
        activityEvents.forEach(event => {
            document.addEventListener(event, handleActivity, true);
        });
        
        console.log('[SessionMonitor] Activity listeners registered');
    }
    
    /**
     * Extend the session by making a keep-alive request
     */
    async extendSession() {
        try {
            const response = await fetch('/api/keep-alive', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                console.warn('[SessionMonitor] Keep-alive request failed:', response.status);
                return;
            }
            
            const data = await response.json();
            
            if (this.onExtended) {
                this.onExtended(data);
            }
            
            // Reset warning flag
            this.warningShown = false;
            this.sessionExpiredMessageShown = false;
            
            console.log('[SessionMonitor] Session extended. Remaining:', data.session_remaining, 'minutes');
            
        } catch (error) {
            console.error('[SessionMonitor] Error extending session:', error);
        }
    }
    
    /**
     * Handle page visibility changes (tab switch)
     */
    handleVisibilityChange() {
        if (document.hidden) {
            // Page is hidden
            console.log('[SessionMonitor] Page hidden, continuing to monitor in background');
            this.visibilityHidden = true;
        } else {
            // Page is visible again
            console.log('[SessionMonitor] Page visible again, checking session status');
            this.visibilityHidden = false;
            
            // Check session status immediately when tab becomes visible
            this.checkSession();
        }
    }
    
    /**
     * Get current session status
     * 
     * @returns {Object|null} Last known session status or null
     */
    getStatus() {
        return this.lastSessionStatus;
    }
    
    /**
     * Manually request session status check
     */
    async requestStatusCheck() {
        return this.checkSession();
    }
    
    /**
     * Destroy the monitor (cleanup)
     */
    destroy() {
        this.stop();
        console.log('[SessionMonitor] Monitor destroyed');
    }
}


/**
 * Session Warning Modal - Visual feedback to user
 * 
 * Shows a modal warning when session is about to expire
 */
class SessionWarningModal {
    constructor(options = {}) {
        this.containerId = options.containerId || 'session-warning-container';
        this.onKeepSession = options.onKeepSession || null;
        this.onLogout = options.onLogout || null;
        this.autoHideDuration = options.autoHideDuration || 10000; // 10 seconds
        this.countdownInterval = null;
    }
    
    /**
     * Show the warning modal
     * 
     * @param {number} remainingMinutes - Minutes until session expires
     */
    show(remainingMinutes) {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.warn('[SessionWarning] Container not found:', this.containerId);
            return;
        }
        
        const modal = this.createModalHTML(remainingMinutes);
        container.innerHTML = modal;
        container.style.display = 'block';
        
        // Add event listeners
        const keepBtn = container.querySelector('.session-warning-keep');
        const logoutBtn = container.querySelector('.session-warning-logout');
        
        if (keepBtn) {
            keepBtn.addEventListener('click', () => this.handleKeepSession());
        }
        
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }
        
        // Auto-hide after duration
        setTimeout(() => this.hide(), this.autoHideDuration);
        
        console.log('[SessionWarning] Warning modal shown');
    }
    
    /**
     * Hide the warning modal
     */
    hide() {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.style.display = 'none';
        }
        
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
        }
    }
    
    /**
     * Create modal HTML
     * 
     * @param {number} remainingMinutes - Minutes remaining
     * @returns {string} HTML string
     */
    createModalHTML(remainingMinutes) {
        return `
            <div class="alert alert-warning alert-dismissible fade show" role="alert" style="margin: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>⏰ Session Expiring Soon</strong>
                        <p style="margin: 10px 0 0 0;">
                            Your session will expire in <strong>${remainingMinutes} minutes</strong> 
                            due to inactivity.
                        </p>
                        <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #666;">
                            Click "Keep Session" to continue working, or you'll be logged out.
                        </p>
                    </div>
                    <div style="white-space: nowrap; margin-left: 20px;">
                        <button class="btn btn-primary session-warning-keep" type="button">
                            Keep Session
                        </button>
                        <button class="btn btn-secondary session-warning-logout" type="button" style="margin-left: 10px;">
                            Logout
                        </button>
                    </div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }
    
    /**
     * Handle keep session button click
     */
    handleKeepSession() {
        console.log('[SessionWarning] User clicked "Keep Session"');
        this.hide();
        
        if (this.onKeepSession) {
            this.onKeepSession();
        }
    }
    
    /**
     * Handle logout button click
     */
    handleLogout() {
        console.log('[SessionWarning] User clicked "Logout"');
        this.hide();
        
        if (this.onLogout) {
            this.onLogout();
        } else {
            // Default logout
            window.location.href = '/logout';
        }
    }
}


/**
 * Global helper function to show session warning
 * 
 * @param {number} remainingMinutes - Minutes remaining
 */
function showSessionWarning(remainingMinutes) {
    // Check if modal is already shown
    const container = document.getElementById('session-warning-container');
    if (container && container.style.display !== 'none') {
        return;
    }
    
    // Create and show warning modal
    const modal = new SessionWarningModal({
        containerId: 'session-warning-container',
        onKeepSession: () => {
            // Session is kept by continuing to use the app
            console.log('[SessionWarning] Callback: Keep session');
        },
        onLogout: () => {
            window.location.href = '/logout';
        }
    });
    
    modal.show(remainingMinutes);
}


/**
 * Initialize global session monitor on page load
 * 
 * Call this in your base template or main.js to enable monitoring
 */
function initSessionMonitor() {
    // Only initialize if user is authenticated
    const container = document.querySelector('[data-authenticated]');
    if (!container || container.getAttribute('data-authenticated') !== 'true') {
        console.log('[SessionMonitor] Not authenticated, skipping initialization');
        return;
    }
    
    // Create global instance
    window.sessionMonitor = new SessionExpirationMonitor({
        checkInterval: 60000, // Check every 1 minute
        warningTime: 10, // Warn 10 minutes before expiration
        autoLogout: true, // Auto logout on expiration
        onWarning: (status) => {
            console.log('[SessionMonitor] Warning callback triggered');
            showSessionWarning(status.remaining_minutes);
        },
        onExpired: (status) => {
            console.log('[SessionMonitor] Expired callback triggered');
            // Optional: Show notification
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('Session Expired', {
                    body: 'Your session has expired. You are being logged out.',
                    tag: 'session-expired'
                });
            }
        },
        onExtended: (data) => {
            console.log('[SessionMonitor] Session extended:', data);
        }
    });
    
    console.log('[SessionMonitor] Global monitor initialized');
}


/**
 * Request browser notifications permission
 * 
 * Call this from user preference settings
 */
function requestNotificationPermission() {
    if ('Notification' in window) {
        if (Notification.permission === 'granted') {
            console.log('[Notifications] Already granted');
            return;
        }
        
        if (Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    console.log('[Notifications] Permission granted');
                    new Notification('Notifications Enabled', {
                        body: 'You will be notified when your session is about to expire.'
                    });
                }
            });
        }
    }
}


/**
 * Export for use in other modules
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SessionExpirationMonitor,
        SessionWarningModal,
        showSessionWarning,
        initSessionMonitor,
        requestNotificationPermission
    };
}
