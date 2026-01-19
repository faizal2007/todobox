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
    let userTimezone = 'UTC';
    let sessionStartTime = null;
    let pausedTime = 0;
    let currentSessionTargetDate = null;
    let sessionWasStarted = false;  // Track if /start endpoint was called successfully

    /**
     * Initialize the work session manager
     * @param {Object|string} config - Config object or legacy token string
     */
    function initialize(config) {
        if (typeof config === 'string') {
            csrfToken = config;
            userTimezone = 'UTC';
        } else {
            const safeConfig = config || {};
            csrfToken = safeConfig.csrfToken || '';
            userTimezone = safeConfig.userTimezone || 'UTC';
        }
        setupCardClickHandlers();
        loadAllWorkTimeDisplays();
    }

    /**
     * Load work time for all todo cards on page
     */
    function loadAllWorkTimeDisplays() {
        const workTimeElements = document.querySelectorAll('.work-time-display');
        workTimeElements.forEach(elem => {
            const todoId = elem.getAttribute('data-todo-id');
            if (todoId) {
                loadWorkTimeForTodo(todoId);
                loadRecentSessionTimes(todoId);
            }
        });
    }

    /**
     * Fetch and display recent session times for a todo
     * @param {string} todoId - The todo ID
     */
    function loadRecentSessionTimes(todoId) {
        if (!todoId) return;
        
        fetch('/' + todoId + '/get_recent_session_times', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'Success' && data.has_sessions) {
                displayRecentSessionTimesOnCard(todoId, data.start_time, data.end_time);
            }
        })
        .catch(error => {
            console.error('[WorkSession] Error loading session times for todo', todoId, ':', error);
        });
    }

    /**
     * Display recent session times on a todo card
     * @param {string} todoId - The todo ID
     * @param {string} startTime - Formatted start time
     * @param {string} endTime - Formatted end time
     */
    function displayRecentSessionTimesOnCard(todoId, startTime, endTime) {
        const cardElement = document.querySelector(`#todo-${todoId}`);
        if (!cardElement) return;
        
        const displayElement = cardElement.querySelector('.recent-session-times');
        if (!displayElement) return;
        
        const startTimeElem = displayElement.querySelector('.recent-start-time');
        const endTimeElem = displayElement.querySelector('.recent-end-time');
        
        if (startTimeElem && startTime) {
            startTimeElem.textContent = startTime;
        }
        if (endTimeElem && endTime) {
            endTimeElem.textContent = endTime;
        }
        
        // Show the display if we have session times
        if (startTime || endTime) {
            displayElement.style.display = '';
            console.log('[WorkSession] Displayed session times for todo', todoId);
        }
    }

    /**
     * Fetch and display work time for a specific todo
     * @param {string} todoId - The todo ID
     */
    function loadWorkTimeForTodo(todoId) {
        if (!todoId) return;
        
        fetch('/' + todoId + '/get_work_time', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'Success' && typeof data.total_work_time_hours === 'number') {
                displayWorkTimeOnCard(todoId, data.total_work_time_hours);
            }
        })
        .catch(error => {
            console.error('[WorkSession] Error loading work time for todo', todoId, ':', error);
        });
    }

    /**
     * Display work time on a todo card
     * @param {string} todoId - The todo ID
     * @param {number} hours - Total work hours
     */
    function displayWorkTimeOnCard(todoId, hours) {
        const cardElement = document.querySelector(`#todo-${todoId}`);
        if (!cardElement) return;
        
        const displayElement = cardElement.querySelector('.work-time-display');
        if (!displayElement) return;
        
        const valueElement = displayElement.querySelector('.work-time-value');
        if (!valueElement) return;
        
        const formattedHours = (Math.round(hours * 100) / 100).toFixed(2);
        valueElement.textContent = formattedHours;
        
        // Show the display if hours > 0
        if (hours > 0) {
            displayElement.style.display = '';
            console.log('[WorkSession] Displayed work time for todo', todoId, ':', formattedHours, 'hrs');
        } else {
            displayElement.style.display = 'none';
        }
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
            console.log('[WorkSession] Clicked card with ID:', card.id, 'Extracted todoId:', todoId);
            
            if (todoId && todoId !== '' && todoId !== 'undefined') {
                openSessionModal(todoId, card);
            } else {
                console.error('[WorkSession] Invalid todoId extracted:', todoId, 'Card element:', card);
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

        // Check if we're resuming an existing session from browser memory
        const isResumingSession = currentSessionTodoId === todoId && isPaused && elapsedSeconds > 0;

        // Only reset elapsed time if this is a NEW session (not same todo resuming)
        if (currentSessionTodoId !== todoId) {
            elapsedSeconds = 0;
            sessionWasStarted = false;  // Reset flag for new session
        }
        
        currentSessionTodoId = todoId;
        isSessionRunning = false;

        const titleText = cardElement.querySelector('.card-title') ? cardElement.querySelector('.card-title').textContent : 'Untitled';
        const displayTimezone = userTimezone || 'UTC';
        const timezoneLabel = escapeHtml(displayTimezone);
        const targetDateFromCard = cardElement ? cardElement.getAttribute('data-target-date') : '';
        currentSessionTargetDate = targetDateFromCard || null;
        
        // Fetch active session info to calculate persistent elapsed time
        // Then continue with modal setup after we have the data
        console.log('[WorkSession] About to fetch active session for todoId:', todoId);
        fetch('/' + todoId + '/get_active_session', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin'  // Include session cookies for authentication
        })
        .then(response => response.json())
        .then(data => {
            console.log('[WorkSession] Active session fetch result:', data);
            if (data.elapsed_seconds !== undefined && data.elapsed_seconds > 0) {
                // Set elapsed time from server (works for both active and paused sessions)
                console.log('[WorkSession] Setting elapsed time from server:', data.elapsed_seconds, 'seconds');
                elapsedSeconds = data.elapsed_seconds;
                
                if (data.is_active) {
                    // Active session: mark as paused so user can resume
                    console.log('[WorkSession] Active session detected');
                    isPaused = true;
                } else {
                    // Paused session: already paused
                    console.log('[WorkSession] Paused session detected');
                    isPaused = true;
                }
                
                console.log('[WorkSession] Set elapsedSeconds to:', elapsedSeconds, 'isPaused to:', isPaused);
            } else {
                console.log('[WorkSession] No elapsed time found for this todo');
            }
        })
        .catch(error => {
            console.warn('[WorkSession] Could not fetch active session info:', error);
            // Continue with whatever elapsedSeconds we have in memory
        })
        .finally(() => {
            // Continue with modal setup regardless of fetch result
            continueModalSetup(todoId, cardElement, titleText, displayTimezone, timezoneLabel);
        });
    }

    /**
     * Continue with modal setup after active session data is loaded
     * @param {string} todoId - The ID of the todo
     * @param {Element} cardElement - The card element
     * @param {string} titleText - The title text
     * @param {string} displayTimezone - The display timezone
     * @param {string} timezoneLabel - The timezone label
     */
    function continueModalSetup(todoId, cardElement, titleText, displayTimezone, timezoneLabel) {
        const manualHelperText = escapeHtml(buildManualHelperText(currentSessionTargetDate, displayTimezone));

        // Check if we're resuming an existing session from browser memory
        const isResumingSession = currentSessionTodoId === todoId && isPaused && elapsedSeconds > 0;

        // Create modal HTML
        let modalHtml = `
            <div class="modal fade" id="midnightCrossingModal" tabindex="-1" role="dialog" aria-labelledby="midnightCrossingModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered" role="document">
                    <div class="modal-content">
                        <div class="modal-header bg-warning text-dark">
                            <h5 class="modal-title" id="midnightCrossingModalLabel">
                                <i class="mdi mdi-clock-outline mr-2"></i>Work Extends Past Midnight
                            </h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <p class="mb-3">Your work session extends past midnight to the next day.</p>
                            <div class="alert alert-info py-2 px-3 mb-3">
                                <strong>Work period:</strong><br>
                                <span id="midnightCrossingDisplay">-- to --</span>
                            </div>
                            <p class="text-muted mb-0">Do you want to log this work session continuing into tomorrow?</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal" id="midnightCrossingCancel">
                                Cancel
                            </button>
                            <button type="button" class="btn btn-primary" id="midnightCrossingConfirm">
                                <i class="mdi mdi-check mr-1"></i>Yes, Continue Tomorrow
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal fade" id="workSessionModal" tabindex="-1" role="dialog" aria-labelledby="workSessionModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered" role="document">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title" id="workSessionModalLabel">Work Session</h5>
                            <button type="button" class="close text-white" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <div class="text-center mb-3">
                                <h6 class="mb-1">${escapeHtml(titleText || 'Untitled')}</h6>
                                <p class="text-muted small mb-0">Track live time or log it manually.</p>
                            </div>
                            <div class="btn-group w-100 mb-3" role="group" aria-label="Work session mode selector">
                                <button type="button" class="btn btn-outline-primary active" data-session-mode="timer">
                                    <i class="mdi mdi-timer-outline mr-1"></i> Live Timer
                                </button>
                                <button type="button" class="btn btn-outline-primary" data-session-mode="manual">
                                    <i class="mdi mdi-calendar-edit mr-1"></i> Manual Entry
                                </button>
                            </div>
                            <div class="work-session-pane" data-pane="timer">
                                <div class="work-session-timer mb-4 text-center">
                                    <div class="timer-display" style="font-size: 48px; font-weight: bold; font-family: monospace; color: #667eea;">
                                        00:00:00
                                    </div>
                                </div>
                                <div class="work-session-actions text-center">
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
                            <div class="work-session-pane" data-pane="manual" style="display: none;">
                                <div class="manual-entry card border shadow-sm p-3">
                                    <div class="custom-control custom-radio mb-2">
                                        <input type="radio" class="custom-control-input" name="manualEntryMode" id="manualRangeMode" value="range" checked>
                                        <label class="custom-control-label font-weight-bold" for="manualRangeMode">
                                            Log start & end time
                                        </label>
                                        <small class="d-block text-muted">${manualHelperText}</small>
                                    </div>
                                    <!-- Previous Session Info -->
                                    <div id="previousSessionInfo" class="alert alert-info py-2 px-3 mb-3" style="font-size: 12px; display: none;">
                                        <strong>Last session:</strong> <span id="previousSessionDisplay">--</span>
                                    </div>
                                    <div id="manualRangeFields" class="mt-3">
                                        <label class="small font-weight-bold" for="manualStartTime">Start time</label>
                                        <div class="row g-2">
                                            <div class="col-4">
                                                <select class="form-control form-control-sm" id="manualStartHour">
                                                    <option value="">Hour</option>
                                                </select>
                                            </div>
                                            <div class="col-4">
                                                <select class="form-control form-control-sm" id="manualStartMinute">
                                                    <option value="">Minute</option>
                                                </select>
                                            </div>
                                            <div class="col-4">
                                                <select class="form-control form-control-sm" id="manualStartMeridiem">
                                                    <option value="">AM/PM</option>
                                                    <option value="am">AM</option>
                                                    <option value="pm">PM</option>
                                                </select>
                                            </div>
                                        </div>
                                        <small class="text-muted d-block mt-1">Selected: <span id="manualStartDisplay">--:-- --</span></small>
                                        
                                        <label class="small font-weight-bold mt-3">End time</label>
                                        <div class="row g-2">
                                            <div class="col-4">
                                                <select class="form-control form-control-sm" id="manualEndHour">
                                                    <option value="">Hour</option>
                                                </select>
                                            </div>
                                            <div class="col-4">
                                                <select class="form-control form-control-sm" id="manualEndMinute">
                                                    <option value="">Minute</option>
                                                </select>
                                            </div>
                                            <div class="col-4">
                                                <select class="form-control form-control-sm" id="manualEndMeridiem">
                                                    <option value="">AM/PM</option>
                                                    <option value="am">AM</option>
                                                    <option value="pm">PM</option>
                                                </select>
                                            </div>
                                        </div>
                                        <small class="text-muted d-block mt-1">Selected: <span id="manualEndDisplay">--:-- --</span></small>
                                    </div>
                                    <hr>
                                    <div class="custom-control custom-radio mb-2">
                                        <input type="radio" class="custom-control-input" name="manualEntryMode" id="manualDurationMode" value="duration">
                                        <label class="custom-control-label font-weight-bold" for="manualDurationMode">
                                            Log total duration
                                        </label>
                                    </div>
                                    <div id="manualDurationField" class="mt-3" style="display: none;">
                                        <label class="small font-weight-bold">Duration</label>
                                        <div class="row g-2">
                                            <div class="col-6">
                                                <select class="form-control form-control-sm" id="manualDurationHours">
                                                    <option value="">Hours</option>
                                                </select>
                                            </div>
                                            <div class="col-6">
                                                <select class="form-control form-control-sm" id="manualDurationMinutes">
                                                    <option value="">Minutes</option>
                                                </select>
                                            </div>
                                        </div>
                                        <small class="text-muted d-block mt-1">Selected: <span id="manualDurationDisplay">-- hrs -- mins</span></small>
                                    </div>
                                    <div id="manualEntryError" class="alert alert-danger py-2 px-3 mt-3" style="display: none;"></div>
                                    <div id="manualEntrySuccess" class="alert alert-success py-2 px-3 mt-2" style="display: none;"></div>
                                    <button type="button" class="btn btn-primary btn-block mt-3" id="manualEntrySubmit">
                                        <i class="mdi mdi-content-save"></i> Log Time
                                    </button>
                                </div>
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
        setupModeTabs(modal);
        setupManualEntryForm(modal, todoId, currentSessionTargetDate);

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

        // Disable manual entry tab since timer is now running
        updateManualEntryButtonState();

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
            sessionWasStarted = true;  // Mark that /start was successful
        })
        .catch(error => {
            // CRITICAL FIX: Don't call pauseSession() on error!
            // That would create a POST /pause with no matching POST /start succeeding
            console.error('Error starting session:', error);
            
            // Instead: Check server state and revert frontend state
            isSessionRunning = false;
            isPaused = true;
            stopTimer();
            sessionWasStarted = false;  // Mark that /start failed
            
            // Try to check actual session state
            fetch('/' + currentSessionTodoId + '/get_active_session', {
                method: 'GET',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_active) {
                    // Hmm, server shows active but our start failed
                    // This could mean: POST /start was received but response lost
                    // Resume the timer since session appears to be running
                    console.warn('[WorkSession] Start failed locally but server shows active session');
                    isSessionRunning = true;
                    isPaused = false;
                    startTimer();
                    alert('Network error. Timer appears to be running on server. Resumed locally.');
                } else {
                    // Server confirms not running, so our failed start is correct
                    console.log('[WorkSession] Start failed - server confirms session not active');
                    alert('Failed to start session. Please try again.');
                }
            })
            .catch(syncError => {
                console.error('Error checking session state after failed start:', syncError);
                alert('Failed to start session and cannot verify server state. Please refresh.');
            });
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
            // CRITICAL FIX: Don't call startSession() on error!
            // That would create duplicate START events
            console.error('Error pausing session:', error);
            
            // Instead: Try to sync with server state
            fetch('/' + currentSessionTodoId + '/get_active_session', {
                method: 'GET',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_active) {
                    // Server says session still running, resume timer
                    console.warn('[WorkSession] Pause failed but server shows active session');
                    isSessionRunning = true;
                    isPaused = false;
                    startTimer();
                    alert('Pause incomplete. Timer resumed. Please try pausing again.');
                } else {
                    // Server confirms paused, frontend already set to paused
                    console.log('[WorkSession] Pause completed on server despite fetch error');
                }
            })
            .catch(syncError => {
                // Both pause and sync failed, inform user
                console.error('Error syncing session state:', syncError);
                alert('Connection error. Session may be paused on server but not locally. Please refresh.');
            });
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

        // Re-enable manual entry tab since timer is now stopped
        updateManualEntryButtonState();

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
     * Get current elapsed time as object {hours, minutes, seconds, totalSeconds}
     */
    function getElapsedTimeObject() {
        const hours = Math.floor(elapsedSeconds / 3600);
        const minutes = Math.floor((elapsedSeconds % 3600) / 60);
        const seconds = elapsedSeconds % 60;
        return {
            hours: hours,
            minutes: minutes,
            seconds: seconds,
            totalSeconds: elapsedSeconds
        };
    }

    /**
     * Format elapsed seconds as "X hrs Y mins Z secs"
     */
    function formatElapsedTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        const parts = [];
        if (hours > 0) parts.push(hours + ' hr' + (hours > 1 ? 's' : ''));
        if (minutes > 0) parts.push(minutes + ' min' + (minutes > 1 ? 's' : ''));
        if (secs > 0 || parts.length === 0) parts.push(secs + ' sec' + (secs !== 1 ? 's' : ''));
        return parts.join(' ');
    }

    /**
     * Handle modal close/dismiss
     */
    function handleModalClose() {
        // CRITICAL FIX: Only auto-pause if we actually called /start successfully
        // If modal closed before /start completed, don't send orphaned /pause
        if (!sessionWasStarted && !isPaused) {
            console.log('[WorkSession] Modal closed without session being started - skipping pause');
            return;
        }
        
        // Warn user if closing with active timer
        if (isSessionRunning) {
            isSessionRunning = false;
            isPaused = true;
            stopTimer();
            
            console.log('[WorkSession] Modal closed with active timer - attempting to sync pause');
            console.log('[WorkSession] Elapsed time:', formatElapsedTime(elapsedSeconds), '- use Live Timer or Manual Entry to log');
            
            // CRITICAL FIX: Sync with backend when modal closes
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
                console.log('[WorkSession] Session auto-paused on modal close:', data);
            })
            .catch(error => {
                // If pause fails, we still stopped the timer locally
                // User can refresh to sync, or reopening modal will fetch correct state
                console.error('[WorkSession] Error pausing on modal close:', error);
                console.warn('[WorkSession] Timer stopped locally. Session may be out of sync with server.');
            });
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
     * Configure timer/manual tab switching inside the modal
     * @param {Element} modalEl - Modal element
     */
    function setupModeTabs(modalEl) {
        if (!modalEl) {
            return;
        }

        const toggleButtons = modalEl.querySelectorAll('[data-session-mode]');
        const panes = modalEl.querySelectorAll('.work-session-pane');
        const timerButton = modalEl.querySelector('[data-session-mode="timer"]');
        const manualButton = modalEl.querySelector('[data-session-mode="manual"]');

        function showPane(mode) {
            panes.forEach(pane => {
                if (pane.getAttribute('data-pane') === mode) {
                    pane.style.display = '';
                } else {
                    pane.style.display = 'none';
                }
            });
        }

        function updateManualButtonState() {
            if (!manualButton) return;
            
            if (isSessionRunning) {
                // Disable manual entry when timer is running
                manualButton.disabled = true;
                manualButton.style.opacity = '0.5';
                manualButton.style.cursor = 'not-allowed';
                manualButton.title = 'Stop the timer to use Manual Entry';
            } else {
                // Enable manual entry when timer is stopped
                manualButton.disabled = false;
                manualButton.style.opacity = '1';
                manualButton.style.cursor = 'pointer';
                manualButton.title = '';
            }
        }

        toggleButtons.forEach(button => {
            button.addEventListener('click', function() {
                const mode = this.getAttribute('data-session-mode');
                
                // Prevent switching to manual while timer is running
                if (mode === 'manual' && isSessionRunning) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    // Show confirmation dialog
                    const confirmSwitch = confirm(
                        'Timer is currently running.\n\n' +
                        'Would you like to save the current timer and switch to Manual Entry?\n\n' +
                        '• Click OK to save and switch\n' +
                        '• Click Cancel to continue with Live Timer'
                    );
                    
                    if (confirmSwitch) {
                        console.log('[WorkSession] User confirmed switch to manual - ending live timer');
                        // End the live timer
                        WorkSessionManager.endSession();
                        
                        // Wait for end session to complete, then switch modes
                        setTimeout(() => {
                            toggleButtons.forEach(btn => {
                                btn.classList.remove('active', 'btn-primary', 'text-white');
                                if (!btn.classList.contains('btn-outline-primary')) {
                                    btn.classList.add('btn-outline-primary');
                                }
                            });
                            this.classList.add('active', 'btn-primary', 'text-white');
                            this.classList.remove('btn-outline-primary');
                            showPane(mode);
                            updateManualButtonState();
                        }, 100);
                    }
                    return;
                }
                
                // Normal mode switching
                toggleButtons.forEach(btn => {
                    btn.classList.remove('active', 'btn-primary', 'text-white');
                    if (!btn.classList.contains('btn-outline-primary')) {
                        btn.classList.add('btn-outline-primary');
                    }
                });
                this.classList.add('active', 'btn-primary', 'text-white');
                this.classList.remove('btn-outline-primary');
                showPane(mode);
                updateManualButtonState();
            });
        });

        // Default view
        if (toggleButtons.length > 0) {
            toggleButtons.forEach((btn, index) => {
                if (index === 0) {
                    btn.classList.add('active', 'btn-primary', 'text-white');
                    btn.classList.remove('btn-outline-primary');
                } else {
                    btn.classList.remove('active', 'btn-primary', 'text-white');
                    if (!btn.classList.contains('btn-outline-primary')) {
                        btn.classList.add('btn-outline-primary');
                    }
                }
            });
        }
        showPane('timer');
        updateManualButtonState();
    }

    /**
     * Setup manual entry form behaviors
     * @param {Element} modalEl - Modal element
     * @param {string} todoId - Current todo id
     */
    function setupManualEntryForm(modalEl, todoId, todoTargetDate) {
        if (!modalEl) {
            return;
        }

        const rangeRadio = modalEl.querySelector('#manualRangeMode');
        const durationRadio = modalEl.querySelector('#manualDurationMode');
        const rangeFields = modalEl.querySelector('#manualRangeFields');
        const durationField = modalEl.querySelector('#manualDurationField');
        const submitBtn = modalEl.querySelector('#manualEntrySubmit');
        const errorEl = modalEl.querySelector('#manualEntryError');
        const successEl = modalEl.querySelector('#manualEntrySuccess');
        const previousSessionInfo = modalEl.querySelector('#previousSessionInfo');
        const previousSessionDisplay = modalEl.querySelector('#previousSessionDisplay');
        
        // Time picker elements (start/end times)
        const startHourSelect = modalEl.querySelector('#manualStartHour');
        const startMinuteSelect = modalEl.querySelector('#manualStartMinute');
        const startMeridiemSelect = modalEl.querySelector('#manualStartMeridiem');
        const startDisplay = modalEl.querySelector('#manualStartDisplay');
        
        const endHourSelect = modalEl.querySelector('#manualEndHour');
        const endMinuteSelect = modalEl.querySelector('#manualEndMinute');
        const endMeridiemSelect = modalEl.querySelector('#manualEndMeridiem');
        const endDisplay = modalEl.querySelector('#manualEndDisplay');
        
        // Duration picker elements
        const durationHoursSelect = modalEl.querySelector('#manualDurationHours');
        const durationMinutesSelect = modalEl.querySelector('#manualDurationMinutes');
        const durationDisplay = modalEl.querySelector('#manualDurationDisplay');
        
        const baseDateForEntry = normalizeDateString(todoTargetDate) || getTodayDateString();

        if (!submitBtn) {
            return;
        }

        // Load and display previous session times, and suggest for new entry
        
        // Helper function to update time display
        function updateTimeDisplay(hourSel, minSel, meridiemSel, display) {
            if (!hourSel || !minSel || !meridiemSel || !display) return;
            const h = hourSel.value;
            const m = minSel.value;
            const meridiem = meridiemSel.value;
            if (h && m && meridiem) {
                display.textContent = `${h}:${m} ${meridiem.toUpperCase()}`;
            } else {
                display.textContent = '--:-- --';
            }
        }

        /**
         * Validate that start time is before end time
         * Returns {valid: bool, reason: string}
         */
        function validateTimeRange() {
            const startTime = getTimeFromPicker(startHourSelect, startMinuteSelect, startMeridiemSelect);
            const endTime = getTimeFromPicker(endHourSelect, endMinuteSelect, endMeridiemSelect);
            
            if (!startTime || !endTime) {
                return {valid: false, reason: 'times not set'};
            }
            
            const startHours = parseInt(startTime.split(':')[0], 10);
            const startMins = parseInt(startTime.split(':')[1], 10);
            const endHours = parseInt(endTime.split(':')[0], 10);
            const endMins = parseInt(endTime.split(':')[1], 10);
            const startTotalMins = startHours * 60 + startMins;
            const endTotalMins = endHours * 60 + endMins;
            
            if (endTotalMins <= startTotalMins) {
                return {valid: false, reason: 'end time not after start time'};
            }
            
            return {valid: true, reason: 'ok'};
        }

        /**
         * Parse previous end time and suggest as new start time
         * Format: "Jan 17, 2:30 PM" -> extract hour and minute
         */
        function suggestStartTimeFromPrevious(timeStr) {
            if (!timeStr) return;
            // Format: "Jan 17, 2:30 PM" -> extract "2:30 PM"
            const match = timeStr.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
            if (match) {
                const hour = match[1];
                const minute = match[2];
                const meridiem = match[3].toLowerCase();
                
                console.log('[WorkSession] Suggesting START from previous end time:', timeStr, '→ parsed as', hour + ':' + minute, meridiem);
                
                // Pre-select these values in the dropdowns
                if (startHourSelect) {
                    startHourSelect.value = hour;
                    console.log('[WorkSession] Set start hour to:', hour);
                }
                if (startMinuteSelect) {
                    startMinuteSelect.value = minute;
                    console.log('[WorkSession] Set start minute to:', minute);
                }
                if (startMeridiemSelect) {
                    startMeridiemSelect.value = meridiem;
                    console.log('[WorkSession] Set start meridiem to:', meridiem);
                }
                
                // Update the display
                updateTimeDisplay(startHourSelect, startMinuteSelect, startMeridiemSelect, startDisplay);
                console.log('[WorkSession] Suggested start time:', hour, ':', minute, meridiem);
            }
        }

        /**
         * Parse previous end time and suggest a new end time (30 minutes after suggested start)
         */
        function suggestEndTimeFromPrevious(timeStr) {
            if (!timeStr) return;
            // Format: "Jan 17, 2:30 PM" -> extract "2:30 PM"
            const match = timeStr.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
            if (match) {
                let hour = parseInt(match[1], 10);
                let minute = parseInt(match[2], 10);
                const meridiem = match[3].toLowerCase();
                
                console.log('[WorkSession] Suggesting END from previous end time:', timeStr, '→ parsed as', hour + ':' + minute, meridiem);
                
                // Add 30 minutes to get suggested end time
                minute += 30;
                let suggestedMeridiem = meridiem;
                
                if (minute >= 60) {
                    minute -= 60;
                    hour += 1;
                    console.log('[WorkSession] Minutes >= 60, incrementing hour to:', hour);
                    // When hour reaches 12 or exceeds it, we're crossing into the next meridiem cycle
                    if (hour > 12) {
                        hour = 1;
                        suggestedMeridiem = meridiem === 'am' ? 'pm' : 'am';
                        console.log('[WorkSession] Hour > 12, wrapping to 1 and toggling meridiem to:', suggestedMeridiem);
                    } else if (hour === 12 && meridiem === 'pm') {
                        // 11:XX PM + 30 mins = 12:XX AM (next day), so toggle to AM
                        suggestedMeridiem = 'am';
                        console.log('[WorkSession] Reached 12 PM boundary, toggling to AM for midnight transition');
                    } else if (hour === 12 && meridiem === 'am') {
                        // 11:XX AM + 30 mins = 12:XX PM (noon), so toggle to PM
                        suggestedMeridiem = 'pm';
                        console.log('[WorkSession] Reached 12 AM boundary, toggling to PM for noon transition');
                    }
                }
                
                console.log('[WorkSession] Calculated end time: adding 30 mins to', match[1] + ':' + match[2], meridiem, '→', hour + ':' + String(minute).padStart(2, '0'), suggestedMeridiem);
                
                // Pre-select these values in the dropdowns
                if (endHourSelect) {
                    endHourSelect.value = String(hour);
                    console.log('[WorkSession] Set end hour to:', hour);
                }
                if (endMinuteSelect) {
                    endMinuteSelect.value = String(minute).padStart(2, '0');
                    console.log('[WorkSession] Set end minute to:', String(minute).padStart(2, '0'));
                }
                if (endMeridiemSelect) {
                    endMeridiemSelect.value = suggestedMeridiem;
                    console.log('[WorkSession] Set end meridiem to:', suggestedMeridiem);
                }
                
                // Update the display
                updateTimeDisplay(endHourSelect, endMinuteSelect, endMeridiemSelect, endDisplay);
                console.log('[WorkSession] Suggested end time:', hour + ':' + String(minute).padStart(2, '0'), suggestedMeridiem);
            }
        }
        
        /**
         * Suggest reasonable default times when no previous session exists
         * Suggests: start time = now (rounded to nearest 15 min), end time = start + 1 hour
         */
        function suggestDefaultTimes() {
            console.log('[WorkSession] No previous sessions - suggesting default times based on current time');
            
            const now = new Date();
            let hour = now.getHours();
            let minute = now.getMinutes();
            
            // Round to nearest 15 minutes
            const remainder = minute % 15;
            if (remainder < 8) {
                minute = minute - remainder;
            } else {
                minute = minute - remainder + 15;
            }
            
            if (minute >= 60) {
                minute = 0;
                hour += 1;
            }
            
            // Convert to 12-hour format
            const meridiem = hour >= 12 ? 'pm' : 'am';
            const hour12 = hour % 12 === 0 ? 12 : hour % 12;
            const minuteStr = String(minute).padStart(2, '0');
            
            console.log('[WorkSession] Current time rounded to nearest 15 min:', hour12 + ':' + minuteStr, meridiem);
            
            // Set START time to now
            if (startHourSelect) {
                startHourSelect.value = String(hour12);
            }
            if (startMinuteSelect) {
                startMinuteSelect.value = minuteStr;
            }
            if (startMeridiemSelect) {
                startMeridiemSelect.value = meridiem;
            }
            updateTimeDisplay(startHourSelect, startMinuteSelect, startMeridiemSelect, startDisplay);
            
            // Set END time to start + 1 hour (common work session duration)
            let endHour = hour12 + 1;
            let endMeridiem = meridiem;
            if (endHour > 12) {
                endHour = 1;
                endMeridiem = meridiem === 'am' ? 'pm' : 'am';
            } else if (endHour === 12 && meridiem === 'am') {
                endMeridiem = 'pm'; // 11 AM + 1h = 12 PM
            } else if (endHour === 12 && meridiem === 'pm') {
                endMeridiem = 'am'; // 11 PM + 1h = 12 AM (next day)
            }
            
            if (endHourSelect) {
                endHourSelect.value = String(endHour);
            }
            if (endMinuteSelect) {
                endMinuteSelect.value = minuteStr;
            }
            if (endMeridiemSelect) {
                endMeridiemSelect.value = endMeridiem;
            }
            updateTimeDisplay(endHourSelect, endMinuteSelect, endMeridiemSelect, endDisplay);
            
            console.log('[WorkSession] Suggested times: START', hour12 + ':' + minuteStr, meridiem, '→ END', endHour + ':' + minuteStr, endMeridiem);
        }

        if (previousSessionInfo && previousSessionDisplay) {
            fetch('/' + todoId + '/get_recent_session_times', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'Success' && data.has_sessions && (data.start_time || data.end_time)) {
                    const displayText = (data.start_time ? data.start_time : '--') + ' to ' + (data.end_time ? data.end_time : '--');
                    previousSessionDisplay.textContent = displayText;
                    previousSessionInfo.style.display = '';
                    console.log('[WorkSession] Displayed previous session:', displayText);
                    
                    // Apply suggestions NOW that we have the data
                    // For range mode: suggest start/end times
                    if (data.start_time && data.end_time) {
                        console.log('[WorkSession] Suggesting start time from:', data.start_time);
                        suggestStartTimeFromPrevious(data.start_time);
                        console.log('[WorkSession] Suggesting end time from:', data.end_time);
                        suggestEndTimeFromPrevious(data.end_time);
                    }
                    
                    // For duration mode: suggest duration from start and end times
                    if (data.start_time && data.end_time) {
                        console.log('[WorkSession] Suggesting duration from:', data.start_time, 'to', data.end_time);
                        suggestDurationFromPrevious(data.start_time, data.end_time);
                    }
                } else {
                    // NO previous sessions - suggest reasonable default times
                    console.log('[WorkSession] No previous sessions found - using default suggestions');
                    previousSessionInfo.style.display = 'none';
                    suggestDefaultTimes();
                }
            })
            .catch(error => {
                console.error('[WorkSession] Error loading previous session times:', error);
                // Even if fetch fails, suggest default times
                suggestDefaultTimes();
            });
        } else {
            // If previousSessionInfo doesn't exist, still suggest default times
            suggestDefaultTimes();
        }

        // Prevent multiple event listeners on same button by removing any existing ones first
        const newBtn = submitBtn.cloneNode(true);
        submitBtn.parentNode.replaceChild(newBtn, submitBtn);
        const freshBtn = modalEl.querySelector('#manualEntrySubmit');

        // Flag to prevent multiple simultaneous requests
        let isSubmitting = false;

        // Initialize time pickers with hours (1-12) and minutes (00-59)
        function initializeTimePickers() {
            const hours = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];
            const minutes = [];
            for (let i = 0; i < 60; i++) {
                minutes.push(String(i).padStart(2, '0'));
            }

            [startHourSelect, endHourSelect].forEach(select => {
                if (select) {
                    hours.forEach(h => {
                        const opt = document.createElement('option');
                        opt.value = h;
                        opt.textContent = h;
                        select.appendChild(opt);
                    });
                }
            });

            [startMinuteSelect, endMinuteSelect].forEach(select => {
                if (select) {
                    minutes.forEach(m => {
                        const opt = document.createElement('option');
                        opt.value = m;
                        opt.textContent = m;
                        select.appendChild(opt);
                    });
                }
            });
        }

        function updateTimeDisplay(hourSel, minSel, meridiemSel, display) {
            if (!hourSel || !minSel || !meridiemSel || !display) return;
            const h = hourSel.value;
            const m = minSel.value;
            const meridiem = meridiemSel.value;
            if (h && m && meridiem) {
                display.textContent = `${h}:${m} ${meridiem.toUpperCase()}`;
            } else {
                display.textContent = '--:-- --';
            }
        }

        function getTimeFromPicker(hourSel, minSel, meridiemSel) {
            const h = hourSel ? hourSel.value : '';
            const m = minSel ? minSel.value : '';
            const meridiem = meridiemSel ? meridiemSel.value : '';
            if (!h || !m || !meridiem) return '';
            // Return in 24-hour format HH:MM
            let hours = parseInt(h, 10);
            if (meridiem === 'pm' && hours !== 12) hours += 12;
            if (meridiem === 'am' && hours === 12) hours = 0;
            return `${String(hours).padStart(2, '0')}:${m}`;
        }

        // Set up event listeners for time pickers
        [startHourSelect, startMinuteSelect, startMeridiemSelect].forEach(sel => {
            if (sel) sel.addEventListener('change', () => updateTimeDisplay(startHourSelect, startMinuteSelect, startMeridiemSelect, startDisplay));
        });
        [endHourSelect, endMinuteSelect, endMeridiemSelect].forEach(sel => {
            if (sel) sel.addEventListener('change', () => updateTimeDisplay(endHourSelect, endMinuteSelect, endMeridiemSelect, endDisplay));
        });

        initializeTimePickers();

        // Initialize duration picker with hours (0-12) and minutes (0-59)
        function initializeDurationPicker() {
            const hours = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];
            const minutes = [];
            for (let i = 0; i < 60; i++) {
                minutes.push(String(i).padStart(2, '0'));
            }

            if (durationHoursSelect) {
                hours.forEach(h => {
                    const opt = document.createElement('option');
                    opt.value = h;
                    opt.textContent = h;
                    durationHoursSelect.appendChild(opt);
                });
            }

            if (durationMinutesSelect) {
                minutes.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m;
                    opt.textContent = m;
                    durationMinutesSelect.appendChild(opt);
                });
            }
        }

        function updateDurationDisplay() {
            if (!durationHoursSelect || !durationMinutesSelect || !durationDisplay) return;
            const h = durationHoursSelect.value;
            const m = durationMinutesSelect.value;
            if (h || m) {
                const hours = h ? parseInt(h, 10) : 0;
                const mins = m ? parseInt(m, 10) : 0;
                durationDisplay.textContent = `${hours} hrs ${mins} mins`;
            } else {
                durationDisplay.textContent = '-- hrs -- mins';
            }
        }

        /**
         * Suggest duration based on previous session
         * Calculate duration from previous start and end times
         */
        function suggestDurationFromPrevious(startTimeStr, endTimeStr) {
            if (!startTimeStr || !endTimeStr) return;
            
            // Parse "2:30 PM" format
            const parseTime = (timeStr) => {
                const match = timeStr.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
                if (!match) return null;
                let hours = parseInt(match[1], 10);
                const minutes = parseInt(match[2], 10);
                const meridiem = match[3].toLowerCase();
                
                // Convert to 24-hour format
                if (meridiem === 'pm' && hours !== 12) hours += 12;
                if (meridiem === 'am' && hours === 12) hours = 0;
                
                return { hours, minutes };
            };
            
            const start = parseTime(startTimeStr);
            const end = parseTime(endTimeStr);
            
            if (!start || !end) return;
            
            // Calculate duration
            let totalMinutes = (end.hours * 60 + end.minutes) - (start.hours * 60 + start.minutes);
            
            // Handle overnight (if duration is negative)
            if (totalMinutes < 0) {
                totalMinutes += 24 * 60; // Add 24 hours
            }
            
            const durationHours = Math.floor(totalMinutes / 60);
            const durationMins = totalMinutes % 60;
            
            console.log('[WorkSession] Suggested duration:', durationHours, 'hrs', durationMins, 'mins');
            
            // Pre-select in dropdowns
            if (durationHoursSelect) durationHoursSelect.value = String(durationHours);
            if (durationMinutesSelect) durationMinutesSelect.value = String(durationMins).padStart(2, '0');
            
            updateDurationDisplay();
        }

        // Set up event listeners for duration picker
        if (durationHoursSelect) {
            durationHoursSelect.addEventListener('change', updateDurationDisplay);
        }
        if (durationMinutesSelect) {
            durationMinutesSelect.addEventListener('change', updateDurationDisplay);
        }

        initializeDurationPicker();

        function toggleManualFields() {
            if (rangeRadio && rangeRadio.checked) {
                if (rangeFields) rangeFields.style.display = '';
                if (durationField) durationField.style.display = 'none';
            } else {
                if (rangeFields) rangeFields.style.display = 'none';
                if (durationField) durationField.style.display = '';
            }
        }

        if (rangeRadio) {
            rangeRadio.addEventListener('change', toggleManualFields);
        }
        if (durationRadio) {
            durationRadio.addEventListener('change', toggleManualFields);
        }
        toggleManualFields();

        function setLoadingState(isLoading) {
            if (!freshBtn) return;
            if (isLoading) {
                freshBtn.dataset.originalHtml = freshBtn.dataset.originalHtml || freshBtn.innerHTML;
                freshBtn.innerHTML = '<i class="mdi mdi-loading mdi-spin"></i> Logging...';
                freshBtn.disabled = true;
                console.log('[Manual Entry] Button locked (loading)');
            } else {
                if (freshBtn.dataset.originalHtml) {
                    freshBtn.innerHTML = freshBtn.dataset.originalHtml;
                }
                freshBtn.disabled = false;
                console.log('[Manual Entry] Button unlocked (ready)');
            }
        }

        function showSuccess(message) {
            if (!successEl) return;
            successEl.textContent = message;
            successEl.style.display = 'block';
        }

        function submitManualEntry(payload, startDate, endDate, startTime, endTime) {
            // Validation passed - mark as submitting and disable button
            isSubmitting = true;
            setLoadingState(true);

            console.log('[WorkSession] Submitting manual time with todoId:', todoId, 'Payload:', payload);
            if (!todoId || todoId === 'undefined' || todoId === '') {
                console.error('[WorkSession] Invalid todoId:', todoId);
                showError('Internal error: todo ID missing. Please refresh and try again.');
                isSubmitting = false;
                setLoadingState(false);
                return;
            }

            fetch('/' + todoId + '/log_manual_time', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(payload)
            })
            .then(response => {
                console.log('[WorkSession] Fetch response status:', response.status);
                return response.json().then(data => {
                    console.log('[WorkSession] Response data:', data);
                    return { ok: response.ok, status: response.status, data: data };
                }).catch(err => {
                    console.error('[WorkSession] Failed to parse response JSON:', err);
                    return { ok: response.ok, status: response.status, data: {} };
                });
            })
            .then(result => {
                console.log('[WorkSession] Final result:', result);
                if (result.ok && result.data && result.data.status === 'Success') {
                    const sessionHours = typeof result.data.session_duration_hours === 'number' ? result.data.session_duration_hours : 0;
                    const totalHours = typeof result.data.total_work_time_hours === 'number' ? result.data.total_work_time_hours : 0;
                    const formattedSession = formatHoursValue(sessionHours);
                    const formattedTotal = formatHoursValue(totalHours);
                    
                    // Check if this was a midnight crossing and end date is different
                    if (endDate && startDate && endDate !== startDate) {
                        console.log('[Manual Entry] Midnight crossing successful - work logged from ' + startDate + ' to ' + endDate);
                        showSuccess('Logged ' + formattedSession + ' hrs • Total ' + formattedTotal + ' hrs\nWork session spans ' + startDate + ' to ' + endDate);
                    } else {
                        showSuccess('Logged ' + formattedSession + ' hrs • Total ' + formattedTotal + ' hrs');
                    }

                    // Update work time display on the todo card
                    displayWorkTimeOnCard(todoId, totalHours);
                    
                    // Refresh recent session times on the card
                    loadRecentSessionTimes(todoId);

                    if (payload.mode === 'range') {
                        // Clear dropdowns and re-suggest new times based on just-logged session
                        if (startHourSelect) startHourSelect.value = '';
                        if (startMinuteSelect) startMinuteSelect.value = '';
                        if (startMeridiemSelect) startMeridiemSelect.value = '';
                        if (endHourSelect) endHourSelect.value = '';
                        if (endMinuteSelect) endMinuteSelect.value = '';
                        if (endMeridiemSelect) endMeridiemSelect.value = '';
                        if (startDisplay) startDisplay.textContent = '--:-- --';
                        if (endDisplay) endDisplay.textContent = '--:-- --';
                        
                        // Auto-suggest times for next entry based on just-logged session
                        // Wait a moment for backend to update, then fetch fresh suggestions
                        setTimeout(() => {
                            fetch('/' + todoId + '/get_recent_session_times', {
                                method: 'GET',
                                headers: {
                                    'Content-Type': 'application/json'
                                }
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.status === 'Success' && data.end_time) {
                                    console.log('[WorkSession] Auto-suggesting for next entry from:', data.end_time);
                                    suggestStartTimeFromPrevious(data.end_time);
                                    suggestEndTimeFromPrevious(data.end_time);
                                }
                            })
                            .catch(err => console.warn('[WorkSession] Could not auto-suggest times:', err));
                        }, 300);
                    } else {
                        // Duration mode: clear and refresh with suggested duration
                        if (durationHoursSelect) durationHoursSelect.value = '';
                        if (durationMinutesSelect) durationMinutesSelect.value = '';
                        if (durationDisplay) durationDisplay.textContent = '-- hrs -- mins';
                        
                        // Auto-suggest duration for next entry based on just-logged session
                        setTimeout(() => {
                            fetch('/' + todoId + '/get_recent_session_times', {
                                method: 'GET',
                                headers: {
                                    'Content-Type': 'application/json'
                                }
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.status === 'Success' && data.start_time && data.end_time) {
                                    console.log('[WorkSession] Auto-suggesting duration from:', data.start_time, 'to', data.end_time);
                                    suggestDurationFromPrevious(data.start_time, data.end_time);
                                }
                            })
                            .catch(err => console.warn('[WorkSession] Could not auto-suggest duration:', err));
                        }, 300);
                    }
                } else {
                    const message = result.data && result.data.message ? result.data.message : 'Unable to log time. Please try again.';
                    console.error('[WorkSession] Error response:', message, 'Status:', result.status);
                    showError(message);
                    // Clear dropdowns on error too so user doesn't accidentally re-submit
                    if (payload.mode === 'range') {
                        if (startHourSelect) startHourSelect.value = '';
                        if (startMinuteSelect) startMinuteSelect.value = '';
                        if (startMeridiemSelect) startMeridiemSelect.value = '';
                        if (endHourSelect) endHourSelect.value = '';
                        if (endMinuteSelect) endMinuteSelect.value = '';
                        if (endMeridiemSelect) endMeridiemSelect.value = '';
                        if (startDisplay) startDisplay.textContent = '--:-- --';
                        if (endDisplay) endDisplay.textContent = '--:-- --';
                    } else {
                        if (durationHoursSelect) durationHoursSelect.value = '';
                        if (durationMinutesSelect) durationMinutesSelect.value = '';
                        if (durationDisplay) durationDisplay.textContent = '-- hrs -- mins';
                    }
                }
                isSubmitting = false;
                setLoadingState(false);
            })
            .catch(error => {
                console.error('[WorkSession] Fetch error:', error);
                showError('Network error: ' + error.message);
                isSubmitting = false;
                setLoadingState(false);
            });
        }

        function showError(message) {
            if (!errorEl) return;
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }

        freshBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Prevent multiple simultaneous requests
            if (isSubmitting) {
                console.log('[Manual Entry] Submission already in progress, ignoring duplicate click');
                return;
            }

            if (errorEl) errorEl.style.display = 'none';
            if (successEl) successEl.style.display = 'none';

            const useRange = rangeRadio ? rangeRadio.checked : true;
            const payload = {
                mode: useRange ? 'range' : 'duration',
                user_timezone: userTimezone
            };

            if (payload.mode === 'range') {
                // Use new time picker logic
                const startTime = getTimeFromPicker(startHourSelect, startMinuteSelect, startMeridiemSelect);
                const endTime = getTimeFromPicker(endHourSelect, endMinuteSelect, endMeridiemSelect);
                
                console.log('[Manual Entry] Start picker:', startTime, 'End picker:', endTime);
                
                if (!startTime || !endTime) {
                    showError('Please select both start and end times using the dropdowns.');
                    return;
                }
                
                // Validate that start time is before end time
                const startHours = parseInt(startTime.split(':')[0], 10);
                const startMins = parseInt(startTime.split(':')[1], 10);
                const endHours = parseInt(endTime.split(':')[0], 10);
                const endMins = parseInt(endTime.split(':')[1], 10);
                const startTotalMins = startHours * 60 + startMins;
                const endTotalMins = endHours * 60 + endMins;
                
                // Detect midnight crossing: if end time < start time, work extends past midnight
                let endDateForEntry = baseDateForEntry;
                let midnightCrossing = false;
                let nextDayDate = null;
                
                if (endTotalMins <= startTotalMins) {
                    // Check if this is a midnight crossing (e.g., 11 PM to 12:26 AM)
                    // This happens when end is AM (00-11 hours) and start is PM (12-23 hours in 24-hr)
                    const startMeridiem = startMeridiemSelect ? startMeridiemSelect.value : 'am';
                    const endMeridiem = endMeridiemSelect ? endMeridiemSelect.value : 'am';
                    
                    if ((startMeridiem === 'pm' && endMeridiem === 'am') || 
                        (startHours >= 12 && endHours < 12)) {
                        // This is a legitimate midnight crossing
                        console.log('[Manual Entry] Detected midnight crossing: work extends to next day');
                        
                        // Increment end date to next day
                        const baseDateObj = new Date(baseDateForEntry + 'T00:00:00');
                        baseDateObj.setDate(baseDateObj.getDate() + 1);
                        const year = baseDateObj.getFullYear();
                        const month = String(baseDateObj.getMonth() + 1).padStart(2, '0');
                        const day = String(baseDateObj.getDate()).padStart(2, '0');
                        nextDayDate = year + '-' + month + '-' + day;
                        endDateForEntry = nextDayDate;
                        console.log('[Manual Entry] End date incremented to next day:', endDateForEntry);
                        
                        // SHOW CONFIRMATION MODAL for midnight crossing
                        // Set up the modal content
                        const midnightDisplay = document.getElementById('midnightCrossingDisplay');
                        const confirmBtn = document.getElementById('midnightCrossingConfirm');
                        const cancelBtn = document.getElementById('midnightCrossingCancel');
                        
                        if (midnightDisplay) {
                            // Build content safely without interpreting user-controlled values as HTML
                            midnightDisplay.textContent = '';
                            midnightDisplay.appendChild(
                                document.createTextNode(baseDateForEntry + ' ' + startTime + ' ')
                            );
                            midnightDisplay.appendChild(document.createElement('br'));
                            const arrowStrong = document.createElement('strong');
                            arrowStrong.textContent = '→';
                            midnightDisplay.appendChild(arrowStrong);
                            midnightDisplay.appendChild(document.createElement('br'));
                            midnightDisplay.appendChild(
                                document.createTextNode(' ' + endDateForEntry + ' ' + endTime)
                            );
                        }
                        
                        // Set up one-time click handlers
                        let handlerActive = true;
                        
                        const handleConfirm = function() {
                            if (!handlerActive) return;
                            handlerActive = false;
                            console.log('[Manual Entry] User confirmed midnight crossing - proceeding with next-day logging');
                            confirmBtn.removeEventListener('click', handleConfirm);
                            cancelBtn.removeEventListener('click', handleCancel);
                            $('#midnightCrossingModal').modal('hide');
                            
                            // Proceed with submission
                            const startDateTime = baseDateForEntry + 'T' + startTime + ':00';
                            const endDateTime = endDateForEntry + 'T' + endTime + ':00';
                            payload.start_time = startDateTime;
                            payload.end_time = endDateTime;
                            submitManualEntry(payload, baseDateForEntry, endDateForEntry, startTime, endTime);
                        };
                        
                        const handleCancel = function() {
                            if (!handlerActive) return;
                            handlerActive = false;
                            console.log('[Manual Entry] User declined midnight crossing');
                            confirmBtn.removeEventListener('click', handleConfirm);
                            cancelBtn.removeEventListener('click', handleCancel);
                            $('#midnightCrossingModal').modal('hide');
                            showError('Work session cancelled. Would you like to log work ending today, or start a new session tomorrow?');
                        };
                        
                        confirmBtn.addEventListener('click', handleConfirm);
                        cancelBtn.addEventListener('click', handleCancel);
                        
                        // Show the modal
                        console.log('[Manual Entry] Showing midnight crossing confirmation modal');
                        $('#midnightCrossingModal').modal('show');
                        return;  // Exit - modal handlers will take it from here
                    } else {
                        // This is an invalid time range on same day
                        showError('End time must be later than start time. Please adjust.');
                        console.warn('[Manual Entry] Validation failed: end time not after start time', {startTime, endTime, startTotalMins, endTotalMins});
                        return;
                    }
                }
                
                // Combine date with time (HH:MM format from picker)
                const startDateTime = baseDateForEntry + 'T' + startTime + ':00';
                const endDateTime = endDateForEntry + 'T' + endTime + ':00';
                
                console.log('[Manual Entry] Combined datetimes (same day):', startDateTime, endDateTime);
                
                if (!startDateTime || !endDateTime) {
                    showError('Invalid times selected.');
                    return;
                }
                payload.start_time = startDateTime;
                payload.end_time = endDateTime;
                
                // Submit the form
                submitManualEntry(payload, baseDateForEntry, endDateForEntry, startTime, endTime);
            } else {
                // Use duration picker (hours and minutes dropdowns)
                const durationHours = durationHoursSelect ? durationHoursSelect.value : '';
                const durationMinutes = durationMinutesSelect ? durationMinutesSelect.value : '';
                
                if (!durationHours && !durationMinutes) {
                    showError('Please select a duration (hours and/or minutes).');
                    return;
                }
                
                const hours = durationHours ? parseInt(durationHours, 10) : 0;
                const minutes = durationMinutes ? parseInt(durationMinutes, 10) : 0;
                const totalSeconds = (hours * 3600) + (minutes * 60);
                
                if (totalSeconds <= 0) {
                    showError('Duration must be greater than 0.');
                    return;
                }
                
                console.log('[Manual Entry] Duration picker:', hours, 'hrs', minutes, 'mins = ', totalSeconds, 'seconds');
                payload.duration_seconds = totalSeconds;
                
                // Submit duration mode
                submitManualEntry(payload, baseDateForEntry, baseDateForEntry, 'N/A', 'N/A');
            }
        });
    }

    function formatHoursValue(hours) {
        if (typeof hours !== 'number' || isNaN(hours)) {
            return '0.00';
        }
        return (Math.round(hours * 100) / 100).toFixed(2);
    }

    function buildManualHelperText(dateString, timezoneLabel) {
        const normalizedDate = normalizeDateString(dateString);
        if (!normalizedDate) {
            return `Times in ${timezoneLabel}`;
        }
        const humanDate = formatDateHuman(normalizedDate);
        return `Times on ${humanDate} (${timezoneLabel})`;
    }

    function formatDateHuman(dateStr) {
        if (!dateStr || !/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
            return dateStr || '';
        }
        try {
            const [year, month, day] = dateStr.split('-').map(Number);
            const dateObj = new Date(Date.UTC(year, month - 1, day));
            return new Intl.DateTimeFormat('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            }).format(dateObj);
        } catch (err) {
            console.warn('Unable to format manual entry date', err);
            return dateStr;
        }
    }

    function normalizeDateString(value) {
        if (!value) {
            return '';
        }
        if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
            return value;
        }
        const parsed = new Date(value);
        if (Number.isNaN(parsed.getTime())) {
            return '';
        }
        return parsed.toISOString().slice(0, 10);
    }

    function combineDateAndTime(dateStr, timeStr) {
        if (!dateStr || !timeStr) {
            return '';
        }
        const normalizedTime = normalizeTimeValue(timeStr);
        if (!normalizedTime) {
            return '';
        }
        return `${dateStr}T${normalizedTime}`;
    }

    function getTodayDateString() {
        return new Date().toISOString().slice(0, 10);
    }

    function normalizeTimeValue(rawValue) {
        if (!rawValue) {
            return '';
        }

        let value = String(rawValue).trim().toLowerCase();
        if (!value) {
            return '';
        }

        let meridiem = null;
        const meridiemMatch = value.match(/(am|pm)$/);
        if (meridiemMatch) {
            meridiem = meridiemMatch[1];
            value = value.slice(0, -meridiem.length).trim();
        } else {
            const inlineMeridiem = value.match(/(am|pm)/);
            if (inlineMeridiem) {
                meridiem = inlineMeridiem[1];
                value = value.replace(inlineMeridiem[1], '').trim();
            }
        }

        value = value.replace(/[^0-9:\.]/g, '');
        value = value.replace(/\.+/g, ':');
        value = value.replace(/::+/g, ':');

        let hours = 0;
        let minutes = 0;
        let seconds = 0;

        if (value.includes(':')) {
            const parts = value.split(':').filter(Boolean);
            if (!parts.length) {
                return '';
            }
            hours = parseInt(parts[0], 10);
            minutes = parts.length > 1 ? parseInt(parts[1], 10) : 0;
            seconds = parts.length > 2 ? parseInt(parts[2], 10) : 0;
        } else {
            const digitsOnly = value.replace(/\D/g, '');
            if (!digitsOnly) {
                return '';
            }

            if (digitsOnly.length <= 2) {
                hours = parseInt(digitsOnly, 10);
            } else if (digitsOnly.length === 3) {
                hours = parseInt(digitsOnly.slice(0, 1), 10);
                minutes = parseInt(digitsOnly.slice(1), 10);
            } else if (digitsOnly.length === 4) {
                hours = parseInt(digitsOnly.slice(0, 2), 10);
                minutes = parseInt(digitsOnly.slice(2), 10);
            } else if (digitsOnly.length === 6) {
                hours = parseInt(digitsOnly.slice(0, 2), 10);
                minutes = parseInt(digitsOnly.slice(2, 4), 10);
                seconds = parseInt(digitsOnly.slice(4, 6), 10);
            } else {
                return '';
            }
        }

        if ([hours, minutes, seconds].some(num => Number.isNaN(num))) {
            return '';
        }

        if (meridiem === 'pm' && hours < 12) {
            hours += 12;
        } else if (meridiem === 'am' && hours === 12) {
            hours = 0;
        }

        if (hours > 23 || minutes > 59 || seconds > 59 || hours < 0 || minutes < 0 || seconds < 0) {
            return '';
        }

        return [hours, minutes, seconds]
            .map(num => String(Math.max(0, num)).padStart(2, '0'))
            .join(':');
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

    /**
     * Update manual entry button state based on session status
     * Disable when timer is running, enable when stopped
     */
    function updateManualEntryButtonState() {
        const manualButton = document.querySelector('[data-session-mode="manual"]');
        if (!manualButton) return;
        
        if (isSessionRunning) {
            // Disable manual entry when timer is running
            manualButton.disabled = true;
            manualButton.style.opacity = '0.5';
            manualButton.style.cursor = 'not-allowed';
            manualButton.title = 'Stop the timer to use Manual Entry';
            console.log('[WorkSession] Manual Entry tab disabled (timer running)');
        } else {
            // Enable manual entry when timer is stopped
            manualButton.disabled = false;
            manualButton.style.opacity = '1';
            manualButton.style.cursor = 'pointer';
            manualButton.title = '';
            console.log('[WorkSession] Manual Entry tab enabled (timer stopped)');
        }
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
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    const timezoneInput = document.getElementById('current-user-timezone');
    const csrfValue = csrfInput ? csrfInput.value : '';
    const timezoneValue = timezoneInput ? timezoneInput.value : 'UTC';

    if (csrfValue) {
        WorkSessionManager.initialize({
            csrfToken: csrfValue,
            userTimezone: timezoneValue
        });
    }
});
