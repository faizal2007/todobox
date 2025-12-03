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
            
            $.post('/' + $(this).data('id') + '/todo', {
                '_csrf_token': csrfToken
            },
            function(data){
                $('#info-header-modal').modal('show');
                $('#title-input-normal').val(data['title']);
                $("input[name='todo_id']").val(data['id']);
                simplemde.value(data['activities']);
                
                // Load reminder data
                loadReminderData(data);
                
                // Hide loading state if it was shown
                if (showLoadingState) {
                    $icon.show();
                    $loading.hide();
                    $button.prop('disabled', false);
                }
            }).fail(function() {
                // Hide loading state on error
                if (showLoadingState) {
                    $icon.show();
                    $loading.hide();
                    $button.prop('disabled', false);
                }
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
            let activities = simplemde.value();
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
                
                $.post('/add', {
                    '_csrf_token': csrfToken,
                    'todo_id': todo_id != null && todo_id !== '' ? todo_id : '',
                    'title': title,
                    'activities': activities,
                    'schedule_day': schedule_day,
                    'custom_date': custom_date,
                    'reminder_enabled': reminderData.enabled,
                    'reminder_type': reminderData.type,
                    'reminder_datetime': reminderData.datetime,
                    'reminder_before_minutes': reminderData.beforeMinutes,
                    'reminder_before_unit': reminderData.beforeUnit
                },
                function(data) {
                    // Determine redirect URL
                    let targetUrl;
                    if (typeof redirectUrl === 'function') {
                        targetUrl = redirectUrl(schedule_day);
                    } else {
                        targetUrl = redirectUrl;
                    }
                    window.location.href = targetUrl;
                }).fail(function() {
                    // Hide loading state on error
                    $icon.show();
                    $loading.hide();
                    $button.prop('disabled', false);
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
            if ($(this).val() === 'custom') {
                $('#custom-date-picker').show();
            } else {
                $('#custom-date-picker').hide();
            }
        });

        // Handle label clicks for button group
        $('label[for="today"], label[for="tomorrow"], label[for="custom_day"]').click(function() {
            const targetInput = $(this).attr('for');
            const inputValue = $('#' + targetInput).val();
            
            // Remove active class from all labels
            $('label[for="today"], label[for="tomorrow"], label[for="custom_day"]').removeClass('active');
            // Add active class to clicked label
            $(this).addClass('active');
            
            if (inputValue === 'custom') {
                $('#custom-date-picker').show();
            } else {
                $('#custom-date-picker').hide();
            }
        });
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
