/**
 * Centralized Todo Operations
 * Shared JavaScript functionality for todo management across different pages
 */

var TodoOperations = (function() {
    'use strict';

    /**
     * Load reminder data into the form when editing a todo
     * @param {Object} data - Todo data from server
     */
    function loadReminderData(data) {
        if (data['reminder_enabled']) {
            $('#reminder-enabled').prop('checked', true);
            $('#reminder-options').show();
            
            // Determine reminder type from reminder_time
            if (data['reminder_time']) {
                // Set reminder type to custom time (the backend stores actual datetime values)
                $('input[name="reminder_type"][value="custom"]').prop('checked', true).trigger('change');
                // Extract just the date-time part (YYYY-MM-DDTHH:mm) from ISO format
                let reminderDateTime = data['reminder_time'];
                // Extract the first 16 characters to get YYYY-MM-DDTHH:mm format
                // ISO format: 2024-12-03T14:30:00.000Z -> We need: 2024-12-03T14:30
                if (reminderDateTime && reminderDateTime.length >= 16) {
                    reminderDateTime = reminderDateTime.substring(0, 16);
                }
                $('#reminder-datetime').val(reminderDateTime);
            }
        } else {
            $('#reminder-enabled').prop('checked', false);
            $('#reminder-options').hide();
        }
    }

    /**
     * Setup edit click handler for todo items
     * @param {Object} simplemde - SimpleMDE editor instance
     * @param {String} csrfToken - CSRF token for requests
     * @param {Boolean} showLoadingState - Whether to show loading state (default: false)
     */
    function setupEditHandler(simplemde, csrfToken, showLoadingState) {
        showLoadingState = showLoadingState !== undefined ? showLoadingState : false;

        $('.edit').click(function() {
            var $button = $(this);
            var $icon = $button.find('.edit-icon');
            var $loading = $button.find('.edit-loading');
            
            // Show loading state if requested
            if (showLoadingState) {
                $icon.hide();
                $loading.show();
                $button.prop('disabled', true);
            }
            
            // Try new GET API endpoint first, fallback to old POST route
            var todoId = $(this).data('id');
            console.log('Raw Todo ID from data attribute:', todoId);
            
            // Ensure we extract just the numeric ID if it contains path information
            var numericId = String(todoId).split('/').pop();
            console.log('Cleaned numeric ID:', numericId);
            
            // Use absolute paths for API endpoints (not relative to current page)
            var newApiUrl = '/api/todo/' + numericId;
            var fallbackUrl = '/' + numericId + '/todo';
            
            console.log('Attempting to fetch todo data...');
            console.log('New API URL:', newApiUrl);
            console.log('Fallback URL:', fallbackUrl);
            console.log('Cleaned Todo ID:', numericId);
            
            $.ajax({
                url: newApiUrl,
                method: 'GET',
                dataType: 'json',
                timeout: 10000
            })
            .done(function(data){
                if (data.success) {
                    $('#info-header-modal').modal('show');
                    $('#title-input-normal').val(data['title'] || '');
                    $("input[name='todo_id']").val(data['id']);
                    
                    // Always populate SimpleMDE with the full description (markdown content)
                    // This ensures both simple and advanced content are available if user switches modes
                    simplemde.value(data['description'] || '');
                    
                    // Check if this is a simple or advanced todo
                    var todoType = data['todo_type'] || 'advanced';
                    console.log('Loading todo with type (GET API):', todoType);
                    
                    // Set the correct mode and populate content based on type
                    if (todoType === 'simple') {
                        // Switch to simple mode
                        var modeSimpleRadio = $('#mode-simple');
                        var modeAdvancedRadio = $('#mode-advanced');
                        
                        // Set checked state
                        modeSimpleRadio.prop('checked', true);
                        modeAdvancedRadio.prop('checked', false);
                        
                        // Update visual button state for Bootstrap button group
                        $('label[for="mode-simple"], label[for="mode-advanced"]').removeClass('active');
                        $('label[for="mode-simple"]').addClass('active');
                        
                        // Update previousMode tracking
                        window.previousMode = 'simple';
                        console.log('[EDIT DEBUG] Set previousMode to simple');
                        
                        // Explicitly call updateModeDisplay to ensure the display updates immediately
                        if (typeof window.updateModeDisplay === 'function') {
                            window.updateModeDisplay();
                        }
                        modeSimpleRadio.trigger('change');
                        
                        // Parse and render checklist items with visual checkboxes
                        var items = data['description'] || '';
                        var parsedItems = parseMarkdownItems(items);
                        renderChecklist(parsedItems);
                        
                        // Store markdown in hidden textarea for form submission
                        $('#simple-items').val(items);
                        console.log('Loaded simple todo items (GET API):', parsedItems);
                    } else {
                        // Switch to advanced mode
                        var modeSimpleRadio = $('#mode-simple');
                        var modeAdvancedRadio = $('#mode-advanced');
                        
                        // Set checked state
                        modeAdvancedRadio.prop('checked', true);
                        modeSimpleRadio.prop('checked', false);
                        
                        // Update visual button state for Bootstrap button group
                        $('label[for="mode-simple"], label[for="mode-advanced"]').removeClass('active');
                        $('label[for="mode-advanced"]').addClass('active');
                        
                        // Update previousMode tracking
                        window.previousMode = 'advanced';
                        console.log('[EDIT DEBUG] Set previousMode to advanced');
                        
                        // Explicitly call updateModeDisplay to ensure the display updates immediately
                        if (typeof window.updateModeDisplay === 'function') {
                            window.updateModeDisplay();
                        }
                        
                        // Ensure SimpleMDE has the correct value and is refreshed
                        var content = data['description'] || '';
                        simplemde.value(content);
                        
                        // Refresh CodeMirror to ensure it displays correctly
                        setTimeout(function() {
                            if (simplemde && simplemde.codemirror) {
                                simplemde.codemirror.refresh();
                            }
                        }, 100);
                        
                        modeAdvancedRadio.trigger('change');
                        console.log('Loaded advanced todo (GET API)');
                    }
                    
                    // Set schedule and ensure proper active state
                    var schedule = data['schedule'] || 'today';
                    var scheduleInput = $('input[name="schedule_day"][value="' + schedule + '"]');
                    if (scheduleInput.length > 0) {
                        scheduleInput.prop('checked', true);
                        scheduleInput.trigger('change');
                    }
                    
                    // Set custom date if needed (handle both 'custom' and 'custom_day' values from backend)
                    if ((schedule === 'custom' || schedule === 'custom_day') && data['custom_date']) {
                        $('#custom_date').val(data['custom_date']);
                        $('#custom-date-picker').show();
                        // Ensure custom date button is active if schedule is a custom type
                        $('label[for="today"], label[for="tomorrow"], label[for="custom_day"]').removeClass('active');
                        $('label[for="custom_day"]').addClass('active');
                        $('#custom_day').prop('checked', true);
                    }
                    
                    // Handle reminder data - enhanced version
                    if (data['reminder_enabled']) {
                        $('#reminder-enabled').prop('checked', true);
                        $('#reminder-options').show();
                        
                        // Set reminder datetime
                        if (data['reminder_time']) {
                            // Backend now sends format YYYY-MM-DDTHH:MM directly for Flatpickr
                            $('#reminder-datetime').val(data['reminder_time']);
                            
                            // Initialize Flatpickr if not already done
                            var reminderInput = document.getElementById('reminder-datetime');
                            if (reminderInput && !reminderInput._flatpickr) {
                                flatpickr('#reminder-datetime', {
                                    enableTime: true,
                                    dateFormat: 'Y-m-d\\TH:i',
                                    altInput: true,
                                    altFormat: 'Y-m-d h:i K',
                                    time_24hr: false,
                                    minuteIncrement: 1,
                                    minDate: 'today',
                                    static: false,
                                    inline: false,
                                    mode: 'single',
                                    theme: 'light',
                                    weekNumbers: true,
                                    allowInput: true
                                });
                            }
                            
                            // Set the value in Flatpickr
                            if (reminderInput._flatpickr) {
                                reminderInput._flatpickr.setDate(data['reminder_time']);
                            }
                        }
                        
                        // Set reminder type
                        if (data['reminder_type']) {
                            var reminderTypeRadio = $('#reminder-' + data['reminder_type']);
                            if (reminderTypeRadio.length > 0) {
                                reminderTypeRadio.prop('checked', true);
                                reminderTypeRadio.trigger('change');
                            }
                        }
                        
                        // Set reminder before values
                        if (data['reminder_before_minutes']) {
                            $('#reminder-before-minutes').val(data['reminder_before_minutes']);
                        }
                        if (data['reminder_before_unit']) {
                            $('#reminder-before-unit').val(data['reminder_before_unit']);
                        }
                    } else {
                        // Ensure reminder is unchecked
                        $('#reminder-enabled').prop('checked', false);
                        $('#reminder-options').hide();
                    }
                } else {
                    console.error('Failed to fetch todo data:', data.message);
                }
                
                // Hide loading state
                if (showLoadingState) {
                    $icon.show();
                    $loading.hide();
                    $button.prop('disabled', false);
                }
            })
            .fail(function(xhr, status, error) {
                console.log('GET API failed, trying fallback POST route...');
                console.log('Error details:', { status: status, error: error, statusCode: xhr.status });
                
                // Fallback to the original POST route
                $.post(fallbackUrl, {
                    '_csrf_token': csrfToken
                }, function(data) {
                    console.log('Fallback POST route succeeded');
                    // Use the old loadReminderData function for this legacy data format
                    if (data) {
                        $('#info-header-modal').modal('show');
                        $('#title-input-normal').val(data['title'] || '');
                        $("input[name='todo_id']").val(data['id']);
                        
                        // Always populate SimpleMDE with the full content (markdown)
                        // This ensures both simple and advanced content are available if user switches modes
                        simplemde.value(data['activities'] || '');
                        
                        // Check if this is a simple or advanced todo
                        var todoType = data['todo_type'] || 'advanced';
                        console.log('Loading todo with type (POST fallback):', todoType);
                        
                        // Set the correct mode
                        if (todoType === 'simple') {
                            // Switch to simple mode
                            var modeSimpleRadio = $('#mode-simple');
                            var modeAdvancedRadio = $('#mode-advanced');
                            
                            // Set checked state
                            modeSimpleRadio.prop('checked', true);
                            modeAdvancedRadio.prop('checked', false);
                            
                            // Update visual button state for Bootstrap button group
                            $('label[for="mode-simple"], label[for="mode-advanced"]').removeClass('active');
                            $('label[for="mode-simple"]').addClass('active');
                            
                            // Update previousMode tracking
                            window.previousMode = 'simple';
                            console.log('[EDIT DEBUG] Set previousMode to simple (POST fallback)');
                            
                            // Explicitly call updateModeDisplay to ensure the display updates immediately
                            if (typeof window.updateModeDisplay === 'function') {
                                window.updateModeDisplay();
                            }
                            modeSimpleRadio.trigger('change');
                            
                            // Parse and render checklist items with visual checkboxes
                            var items = data['activities'] || '';
                            var parsedItems = parseMarkdownItems(items);
                            renderChecklist(parsedItems);
                            
                            // Store markdown in hidden textarea for form submission
                            $('#simple-items').val(items);
                            console.log('Loaded simple todo items (POST fallback):', parsedItems);
                        } else {
                            // Switch to advanced mode
                            var modeSimpleRadio = $('#mode-simple');
                            var modeAdvancedRadio = $('#mode-advanced');
                            
                            // Set checked state
                            modeAdvancedRadio.prop('checked', true);
                            modeSimpleRadio.prop('checked', false);
                            
                            // Update visual button state for Bootstrap button group
                            $('label[for="mode-simple"], label[for="mode-advanced"]').removeClass('active');
                            $('label[for="mode-advanced"]').addClass('active');
                            
                            // Update previousMode tracking
                            window.previousMode = 'advanced';
                            console.log('[EDIT DEBUG] Set previousMode to advanced (POST fallback)');
                            
                            // Explicitly call updateModeDisplay to ensure the display updates immediately
                            if (typeof window.updateModeDisplay === 'function') {
                                window.updateModeDisplay();
                            }
                            
                            // Ensure SimpleMDE has the correct value and is refreshed
                            var content = data['activities'] || '';
                            simplemde.value(content);
                            
                            // Refresh CodeMirror to ensure it displays correctly
                            setTimeout(function() {
                                if (simplemde && simplemde.codemirror) {
                                    simplemde.codemirror.refresh();
                                }
                            }, 100);
                            
                            modeAdvancedRadio.trigger('change');
                            console.log('Loaded advanced todo (POST fallback)');
                        }
                        
                        // Load reminder data using the old function
                        loadReminderData(data);
                    }
                    
                    // Hide loading state
                    if (showLoadingState) {
                        $icon.show();
                        $loading.hide();
                        $button.prop('disabled', false);
                    }
                }).fail(function(xhr, status, error) {
                    // Both routes failed
                    if (showLoadingState) {
                        $icon.show();
                        $loading.hide();
                        $button.prop('disabled', false);
                    }
                    console.error('Both API routes failed:', {
                        status: status,
                        error: error,
                        statusCode: xhr.status,
                        responseText: xhr.responseText
                    });
                });
            });
        });
    }

    /**
     * Collect reminder data from form
     * @returns {Object} Reminder data object
     */
    function collectReminderData() {
        let reminderEnabled = $('#reminder-enabled').is(':checked');
        return {
            enabled: reminderEnabled,
            type: reminderEnabled ? $('input[name="reminder_type"]:checked').val() : null,
            datetime: reminderEnabled ? $('#reminder-datetime').val() : null,
            beforeMinutes: reminderEnabled ? $('#reminder-before-minutes').val() : null,
            beforeUnit: reminderEnabled ? $('#reminder-before-unit').val() : null
        };
    }

    /**
     * Setup save/create todo handler
     * @param {Object} simplemde - SimpleMDE editor instance
     * @param {String} csrfToken - CSRF token for requests
     * @param {String|Function} redirectUrl - URL to redirect after saving, or function that returns URL based on schedule_day
     */
    function setupSaveHandler(simplemde, csrfToken, redirectUrl) {
        $('.create-todo').click(function() {
            let title = $('#title-input-normal').val();
            let todoMode = document.getElementById('todo_mode') ? document.getElementById('todo_mode').value : 'simple';
            let activities = '';
            let simpleItems = '';
            
            // Get content based on mode
            if (todoMode === 'simple') {
                simpleItems = $('#simple-items').val();
                console.log('Simple mode - items to save:', simpleItems);
            } else {
                // Only access simplemde in advanced mode
                if (typeof window.simplemde !== 'undefined' && window.simplemde) {
                    activities = window.simplemde.value();
                    console.log('Advanced mode - SimpleMDE content to save:', activities);
                } else {
                    activities = $('#details-textarea').val();
                    console.log('Advanced mode - Fallback textarea content to save:', activities);
                }
            }
            
            let todo_id = $("input[name='todo_id']").val();
            let schedule_day = $('input[name="schedule_day"]:checked').val();
            let custom_date = $('#custom_date').val();
            
            // Collect reminder data
            let reminderData = collectReminderData();
            
            if (title) {
                var $button = $(this);
                var $icon = $button.find('.create-icon');
                var $loading = $button.find('.create-loading');
                
                // Show loading state
                $icon.hide();
                $loading.show();
                $button.prop('disabled', true);
                
                // Choose the right endpoint based on mode
                let endpoint = todoMode === 'simple' && !todo_id ? '/add_simple' : '/add';
                let postData = {
                    '_csrf_token': csrfToken,
                    'todo_id': todo_id != null && todo_id !== '' ? todo_id : '',
                    'title': title,
                    'todo_type': todoMode,  // Explicitly send the todo_type to ensure it's set correctly
                    'schedule_day': schedule_day,
                    'custom_date': custom_date,
                    'reminder_enabled': reminderData.enabled,
                    'reminder_type': reminderData.type,
                    'reminder_datetime': reminderData.datetime,
                    'reminder_before_minutes': reminderData.beforeMinutes,
                    'reminder_before_unit': reminderData.beforeUnit
                };
                
                // Add content based on mode
                if (todoMode === 'simple') {
                    postData.items = simpleItems;
                } else {
                    postData.activities = activities;
                }
                
                console.log('Submitting to endpoint:', endpoint, 'with mode:', todoMode, 'data:', postData);
                
                $.post(endpoint, postData,
                function(data) {
                    console.log('Success response:', data);
                    // Determine redirect URL
                    let targetUrl;
                    
                    // If todo exited KIV status, redirect to the scheduled date's list
                    if (data.exitedKIV) {
                        // Redirect to the date the task was scheduled to
                        if (data.scheduledDate) {
                            const today = new Date().toISOString().split('T')[0];
                            const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];
                            
                            if (data.scheduledDate === today) {
                                targetUrl = '/today/list';
                            } else if (data.scheduledDate === tomorrow) {
                                targetUrl = '/tomorrow/list';
                            } else {
                                // For other dates, go to the specific date view if available, otherwise go to dashboard
                                targetUrl = '/today/list';
                            }
                        } else {
                            // Fallback to today if no date provided
                            targetUrl = '/today/list';
                        }
                    } else {
                        // For non-KIV exits, use the redirect URL with schedule_day
                        if (typeof redirectUrl === 'function') {
                            targetUrl = redirectUrl(schedule_day);
                        } else if (schedule_day === 'tomorrow') {
                            // If we scheduled to tomorrow but redirectUrl is not a function,
                            // redirect to tomorrow list instead of using the string URL
                            targetUrl = '/tomorrow/list';
                        } else if (schedule_day === 'custom') {
                            // If custom date, check if we should redirect to a specific list
                            // For now, use the provided redirectUrl
                            targetUrl = typeof redirectUrl === 'function' ? redirectUrl(schedule_day) : redirectUrl;
                        } else {
                            // Default case: use the provided redirectUrl
                            targetUrl = redirectUrl;
                        }
                    }
                    console.log('Redirecting to:', targetUrl);
                    window.location.href = targetUrl;
                }).fail(function(xhr, status, error) {
                    console.error('Error submitting form:', status, error, xhr);
                    console.error('Response:', xhr.responseText);
                    // Hide loading state on error
                    $icon.show();
                    $loading.hide();
                    $button.prop('disabled', false);
                    
                    // Show error message if available
                    try {
                        let response = JSON.parse(xhr.responseText);
                        if (response.msg) {
                            alert('Error: ' + response.msg);
                        } else {
                            alert('Error creating todo. Please try again.');
                        }
                    } catch (e) {
                        alert('Error creating todo. Please try again.');
                    }
                });
            } else {
                $('#title-input-normal').last().addClass('is-invalid');
            }
        });
    }

    /**
     * Setup reminder UI event handlers
     */
    function setupReminderHandlers() {
        // Reminder enabled/disabled toggle
        $('#reminder-enabled').change(function() {
            if ($(this).is(':checked')) {
                $('#reminder-options').slideDown(200);
            } else {
                $('#reminder-options').slideUp(200);
            }
        });

        // Reminder type selection
        $('input[name="reminder_type"]').change(function() {
            if ($(this).val() === 'custom') {
                $('#reminder-custom-time').show();
                $('#reminder-before-options').hide();
            } else {
                $('#reminder-custom-time').hide();
                $('#reminder-before-options').show();
            }
        });
    }

    /**
     * Setup schedule day handlers
     */
    function setupScheduleHandlers() {
        // Handle schedule day radio change
        $('input[name="schedule_day"]').change(function() {
            // Remove active class from all labels first
            $('label[for="today"], label[for="tomorrow"], label[for="custom_day"]').removeClass('active');
            // Add active class to parent label of checked radio
            $(this).closest('label').addClass('active');
            
            if ($(this).val() === 'custom') {
                $('#custom-date-picker').show();
            } else {
                $('#custom-date-picker').hide();
            }
        });

        // Handle label clicks for button group (ensure radio gets checked)
        $('label[for="today"], label[for="tomorrow"], label[for="custom_day"]').click(function(e) {
            const targetInput = $(this).attr('for');
            const radio = $('#' + targetInput);
            
            // Ensure radio button is checked
            radio.prop('checked', true).trigger('change');
            
            // Prevent default if needed
            e.preventDefault();
        });
        
        // Initialize active state on page load based on current selection
        const checkedRadio = $('input[name="schedule_day"]:checked');
        if (checkedRadio.length > 0) {
            $('label[for="today"], label[for="tomorrow"], label[for="custom_day"]').removeClass('active');
            checkedRadio.closest('label').addClass('active');
        } else {
            // If no radio is checked, check if we should default to custom based on other indicators
            // For example, if custom date picker is visible or has a value
            if ($('#custom-date-picker').is(':visible') || $('#custom_date').val()) {
                $('#custom_day').prop('checked', true);
                $('label[for="custom_day"]').addClass('active');
                $('#custom-date-picker').show();
            }
        }
    }

    /**
     * Setup modal event handlers
     * @param {Object} simplemde - SimpleMDE editor instance
     */
    function setupModalHandlers(simplemde) {
        $('#info-header-modal').on('shown.bs.modal', function() {
            $(this).find('[autofocus]').focus();
            simplemde.codemirror.refresh();
        });
        
        // Reset form when modal is hidden
        $('#info-header-modal').on('hidden.bs.modal', function() {
            // Reset all form fields
            $('input[name="title-input-normal"]').val('');
            $('input[name="todo_id"]').val('');
            $('input[name="custom_date"]').val('');
            
            // Reset mode to simple
            $('#mode-simple').prop('checked', true).trigger('change');
            $('#todo_mode').val('simple');
            
            // Reset schedule to today
            $('#today').prop('checked', true).trigger('change');
            $('#custom-date-picker').hide();
            
            // Reset reminder
            $('#reminder-enabled').prop('checked', false);
            $('#reminder-options').hide();
            $('#reminder-custom').prop('checked', true);
            $('#reminder-datetime').val('');
            $('#reminder-before-minutes').val('30');
            $('#reminder-before-unit').val('minutes');
            
            // Clear SimpleMDE editor
            if (typeof simplemde !== 'undefined' && simplemde) {
                simplemde.value('');
            }
            
            // Clear checklist items
            $('#simple-items').val('');
            const container = document.getElementById('items-container');
            if (container) {
                container.innerHTML = '<p class="text-muted mb-0"><em>No items yet. Add one below.</em></p>';
            }
            document.getElementById('new-item-input').value = '';
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    function setupKeyboardShortcuts() {
        $(document).keydown(function(event) {
            // Only if modal is visible
            if ($('#info-header-modal').hasClass('show')) {
                // Detect Ctrl + Enter to save
                if ((event.ctrlKey || event.metaKey) && event.which === 13) {
                    event.preventDefault();
                    $('.create-todo').click();
                }
                
                // Detect Ctrl + S to save
                if ((event.ctrlKey || event.metaKey) && event.key === 's') {
                    event.preventDefault();
                    $('.create-todo').click();
                }
            }
        });
    }

    /**
     * Escape HTML special characters
     * @param {String} text - Text to escape
     * @returns {String} Escaped text
     */
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    /**
     * Parse markdown to extract checklist items
     * @param {String} markdown - Markdown content
     * @returns {Array} Array of item objects with text and completed properties
     */
    function parseMarkdownItems(markdown) {
        if (!markdown) return [];
        
        return markdown.split('\n')
            .filter(line => line.trim().startsWith('- ['))
            .map(line => {
                const trimmed = line.trim();
                const completed = trimmed.includes('[x]');
                // Remove checkbox format, handling both single and multiple occurrences
                let text = trimmed.replace(/^- \[[^\]]\]\s*/, '');
                
                // In case of doubled checkboxes (malformed), remove any additional checkbox patterns
                text = text.replace(/^- \[[^\]]\]\s*/, '');
                
                return { text, completed };
            });
    }

    /**
     * Render checklist items in the simple mode UI
     * @param {Array} items - Array of item objects with text and completed properties
     */
    function renderChecklist(items) {
        const container = document.getElementById('items-container');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (items.length === 0) {
            container.innerHTML = '<p class="text-muted mb-0"><em>No items yet. Add one below.</em></p>';
            return;
        }
        
        items.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'form-check mb-2';
            itemDiv.style.display = 'flex';
            itemDiv.style.alignItems = 'center';
            itemDiv.innerHTML = `
                <input class="form-check-input item-checkbox" type="checkbox" id="item-${index}" data-index="${index}" 
                       ${item.completed ? 'checked' : ''} style="cursor: pointer;">
                <label class="form-check-label flex-grow-1 mb-0 ${item.completed ? 'text-muted' : ''}" 
                       for="item-${index}" style="cursor: pointer; ${item.completed ? 'text-decoration: line-through;' : ''}">
                    ${escapeHtml(item.text)}
                </label>
                <button type="button" class="btn btn-sm btn-outline-danger delete-item-btn" data-index="${index}" 
                        title="Delete item" style="padding: 0.25rem 0.5rem;">
                    <i class="mdi mdi-delete"></i>
                </button>
            `;
            container.appendChild(itemDiv);
        });
    }

    /**
     * Update the hidden markdown textarea with current checklist data
     * @param {Array} items - Array of item objects
     */
    function updateMarkdownStorage(items) {
        const markdown = items.map(item => {
            const checkbox = item.completed ? '[x]' : '[ ]';
            // Clean item text in case it has checkbox patterns from malformed data
            let cleanText = item.text.replace(/^-\s*\[\s*[x ]\s*\]\s*/gi, '').trim();
            return `- ${checkbox} ${cleanText}`;
        }).join('\n');
        
        document.getElementById('simple-items').value = markdown;
    }

    /**
     * Setup simple checklist item handlers
     */
    function setupChecklistHandlers() {
        const container = document.getElementById('items-container');
        const addBtn = document.getElementById('add-item-btn');
        const input = document.getElementById('new-item-input');
        const modal = document.getElementById('info-header-modal');
        
        if (!container || !addBtn || !input) return;
        
        // Load existing items from markdown storage on page load
        const markdown = document.getElementById('simple-items').value;
        if (markdown) {
            const items = parseMarkdownItems(markdown);
            renderChecklist(items);
        }
        
        // Use event delegation on modal to prevent duplicate listeners
        // Attach listeners to the modal element which is never recreated
        modal.addEventListener('click', function(e) {
            // Handle add button clicks
            if (e.target.closest('#add-item-btn')) {
                const text = input.value.trim();
                if (!text) return;
                
                const markdown = document.getElementById('simple-items').value;
                const items = parseMarkdownItems(markdown);
                items.push({ text, completed: false });
                
                updateMarkdownStorage(items);
                renderChecklist(items);
                input.value = '';
                input.focus();
                return;
            }
            
            // Handle item deletion
            const deleteBtn = e.target.closest('.delete-item-btn');
            if (deleteBtn) {
                const index = parseInt(deleteBtn.dataset.index);
                const markdown = document.getElementById('simple-items').value;
                const items = parseMarkdownItems(markdown);
                
                items.splice(index, 1);
                updateMarkdownStorage(items);
                renderChecklist(items);
            }
        });
        
        // Handle Enter key on input field
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addBtn.click();
            }
        });
        
        // Handle checkbox changes via event delegation on modal
        modal.addEventListener('change', (e) => {
            if (e.target.classList.contains('item-checkbox')) {
                const index = parseInt(e.target.dataset.index);
                const markdown = document.getElementById('simple-items').value;
                const items = parseMarkdownItems(markdown);
                
                if (items[index]) {
                    items[index].completed = e.target.checked;
                    updateMarkdownStorage(items);
                    renderChecklist(items);
                }
            }
        });
    }

    /**
     * Initialize all todo operations for a page
     * @param {Object} options - Configuration options
     *   - simplemde: SimpleMDE editor instance (required)
     *   - csrfToken: CSRF token for requests (required)
     *   - redirectUrl: URL to redirect after saving (required)
     *   - showLoadingState: Whether to show loading state on edit (optional, default: false)
     */
    function initialize(options) {
        if (!options.simplemde || !options.csrfToken || !options.redirectUrl) {
            console.error('TodoOperations: Missing required initialization options:', {
                simplemde: !!options.simplemde,
                csrfToken: !!options.csrfToken,
                redirectUrl: !!options.redirectUrl
            });
            return;
        }

        setupEditHandler(options.simplemde, options.csrfToken, options.showLoadingState);
        setupSaveHandler(options.simplemde, options.csrfToken, options.redirectUrl);
        setupReminderHandlers();
        setupScheduleHandlers();
        setupModalHandlers(options.simplemde);
        setupKeyboardShortcuts();
        setupChecklistHandlers();
    }

    // Public API
    return {
        initialize: initialize,
        loadReminderData: loadReminderData,
        collectReminderData: collectReminderData,
        setupEditHandler: setupEditHandler,
        setupSaveHandler: setupSaveHandler,
        setupReminderHandlers: setupReminderHandlers,
        setupScheduleHandlers: setupScheduleHandlers,
        setupModalHandlers: setupModalHandlers,
        setupKeyboardShortcuts: setupKeyboardShortcuts
    };
})();
