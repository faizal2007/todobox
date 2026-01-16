/**
 * Work Session Manager
 * Handles modal-based work session tracking with timer
 * Only 1 active work session at a time - starting new todo auto-pauses previous
 */

var WorkSessionManager = (function() {
    'use strict';

    let currentSessionTodoId = null;
    let previousSessionTodoId = null;
    let timerInterval = null;
    let elapsedSeconds = 0;
    let isSessionRunning = false;
    let isPaused = false;
    let csrfToken = '';
    let sessionStartTime = null;
    let pausedTime = 0;

    /**
     * Initialize the work session manager
     * @param {string} token - CSRF token for API calls
     */
    function initialize(token) {
        csrfToken = token;
        setupCardClickHandlers();
    }

    /**
     * Setup click handlers for start work session buttons
     */
    function setupCardClickHandlers() {
        document.addEventListener('click', function(e) {
            const startBtn = e.target.closest('.work-start-btn');
            if (!startBtn) return;

            e.preventDefault();
            e.stopPropagation();

            const card = startBtn.closest('.card');
            const todoId = card.id.replace('todo-', '');
            
            if (todoId) {
                openSessionModal(todoId, card);
            }
        });
    }

    /**
     * Open the work session modal
     * @param {string} todoId - The ID of the todo
     * @param {Element} cardElement - The card element
     */
    function openSessionModal(todoId, cardElement) {
        // ALWAYS stop any running timer when opening modal
        stopTimer();
        
        // If another session is running, pause it first
        if (isSessionRunning && currentSessionTodoId !== todoId) {
            pauseSessionSilent();
        }

        // Check if we're resuming an existing session
        const isResumingSession = currentSessionTodoId === todoId && isPaused && elapsedSeconds > 0;

        // Only reset elapsed time if this is a NEW session (not same todo resuming)
        if (currentSessionTodoId !== todoId) {
            elapsedSeconds = 0;
        }
        
        currentSessionTodoId = todoId;
        isSessionRunning = false;

        const todoTitle = cardElement.querySelector('.card-title')?.textContent || 'Untitled';

        // Create modal HTML
        let modalHtml = `
            <div class="modal fade" id="workSessionModal" tabindex="-1" role="dialog" aria-labelledby="workSessionModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered" role="document">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title" id="workSessionModalLabel">Work Session</h5>
                            <button type="button" class="close text-white" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body text-center">
                            <h6 class="mb-3">${escapeHtml(todoTitle)}</h6>
                            <div class="work-session-timer mb-4">
                                <div class="timer-display" style="font-size: 48px; font-weight: bold; font-family: monospace; color: #667eea;">
                                    00:00:00
                                </div>
                            </div>
                            <div class="work-session-actions">
                                <button type="button" class="btn btn-success btn-lg" id="startBtn" onclick="WorkSessionManager.startSession()">
                                    <i class="mdi mdi-play"></i> Start
                                </button>
                                <button type="button" class="btn btn-warning btn-lg" id="pauseBtn" style="display: none;" onclick="WorkSessionManager.pauseSession()">
                                    <i class="mdi mdi-pause"></i> Pause
                                </button>
                                <button type="button" class="btn btn-danger btn-lg ml-2" id="endBtn" style="display: none;" onclick="WorkSessionManager.endSession()">
                                    <i class="mdi mdi-stop"></i> End
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove any existing modal
        const existingModal = document.getElementById('workSessionModal');
        if (existingModal) {
            // Make sure to stop timer before removing modal
            stopTimer();
            $('#workSessionModal').off('hidden.bs.modal');
            existingModal.remove();
        }

        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Show the modal
        const modal = document.getElementById('workSessionModal');
        
        // Set up modal close handler
        $('#workSessionModal').on('hidden.bs.modal', function() {
            handleModalClose();
        });

        $('#workSessionModal').modal('show');
        updateTimerDisplay();

        // If resuming a paused session, show the START button (not Pause) so user can click to continue
        if (isResumingSession) {
            document.getElementById('startBtn').style.display = 'inline-block';
            document.getElementById('pauseBtn').style.display = 'none';
            document.getElementById('endBtn').style.display = 'inline-block';
        }
    }

    /**
     * Start the work session
     */
    function startSession() {
        isSessionRunning = true;
        isPaused = false;

        // Update button visibility - be more explicit
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const endBtn = document.getElementById('endBtn');

        if (startBtn) startBtn.style.display = 'none';
        if (pauseBtn) pauseBtn.style.display = 'inline-block';
        if (endBtn) endBtn.style.display = 'inline-block';

        // Start timer
        startTimer();

        // Call API to start session - use absolute path, not SCRIPT_ROOT
        const startUrl = '/' + currentSessionTodoId + '/start';
        console.log('Calling /start API:', startUrl);
        
        fetch(startUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: '_csrf_token=' + encodeURIComponent(csrfToken)
        })
        .then(response => {
            console.log('Start response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Session started successfully:', data);
        })
        .catch(error => {
            console.error('Error starting session:', error);
            alert('Failed to start session. Please try again.');
            pauseSession();
        });
    }

    /**
     * Pause the work session
     */
    function pauseSession() {
        isSessionRunning = false;
        isPaused = true;

        // Update button visibility - be more explicit
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const endBtn = document.getElementById('endBtn');

        if (startBtn) startBtn.style.display = 'inline-block';
        if (pauseBtn) pauseBtn.style.display = 'none';
        if (endBtn) endBtn.style.display = 'inline-block';

        // Stop timer (but keep elapsed time)
        stopTimer();

        // Call API to pause session - use absolute path, not SCRIPT_ROOT
        const pauseUrl = '/' + currentSessionTodoId + '/pause';
        
        fetch(pauseUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: '_csrf_token=' + encodeURIComponent(csrfToken)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Session paused:', data);
        })
        .catch(error => {
            console.error('Error pausing session:', error);
            alert('Failed to pause session. Please try again.');
            startSession();
        });
    }

    /**
     * Pause session silently (for auto-pause when starting new session)
     */
    function pauseSessionSilent() {
        if (!isSessionRunning) return;
        
        isSessionRunning = false;
        isPaused = true;
        stopTimer();
        previousSessionTodoId = currentSessionTodoId;

        // Call API to pause session - use absolute path, not SCRIPT_ROOT
        const pauseUrl = '/' + previousSessionTodoId + '/pause';
        
        fetch(pauseUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: '_csrf_token=' + encodeURIComponent(csrfToken)
        })
        .catch(error => {
            console.error('Error pausing previous session:', error);
        });
    }

    /**
     * End the work session (just stop timer and close modal)
     */
    function endSession() {
        stopTimer();
        isSessionRunning = false;
        isPaused = false;

        // Call API to pause/end session - use absolute path, not SCRIPT_ROOT
        const endUrl = '/' + currentSessionTodoId + '/pause';
        console.log('Calling /pause API on End:', endUrl);
        
        fetch(endUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: '_csrf_token=' + encodeURIComponent(csrfToken)
        })
        .then(response => {
            console.log('End response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Session ended successfully:', data);
            $('#workSessionModal').modal('hide');
        })
        .catch(error => {
            console.error('Error ending session:', error);
            alert('Failed to end session. Please try again.');
        });
    }

    /**
     * Handle modal close/dismiss
     */
    function handleModalClose() {
        // Auto-pause the session when modal closes if it's running
        if (isSessionRunning) {
            isSessionRunning = false;
            isPaused = true;
            stopTimer();
        }
    }

    /**
     * Start the timer
     */
    function startTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
        }

        timerInterval = setInterval(function() {
            elapsedSeconds++;
            updateTimerDisplay();
        }, 1000);
    }

    /**
     * Stop the timer
     */
    function stopTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }

    /**
     * Update timer display in modal
     */
    function updateTimerDisplay() {
        const hours = Math.floor(elapsedSeconds / 3600);
        const minutes = Math.floor((elapsedSeconds % 3600) / 60);
        const seconds = elapsedSeconds % 60;

        const timeString = String(hours).padStart(2, '0') + ':' +
                          String(minutes).padStart(2, '0') + ':' +
                          String(seconds).padStart(2, '0');

        const timerDisplay = document.querySelector('.timer-display');
        if (timerDisplay) {
            timerDisplay.textContent = timeString;
        }
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    // Public API
    return {
        initialize: initialize,
        startSession: startSession,
        pauseSession: pauseSession,
        endSession: endSession,
        handleModalClose: handleModalClose
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || '';
    if (csrfToken) {
        WorkSessionManager.initialize(csrfToken);
    }
});
