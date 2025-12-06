/*
Browser Console Debugging Script for Reminder Updates
============================================

Copy and paste this into your browser's developer console (F12) 
when you're on a page with the reminder form (like the today's todos page).

This will help debug the frontend reminder update functionality.
*/

// Step 1: Check if todo-operations.js is loaded
console.log('🔍 Step 1: Checking if TodoOperations is loaded...');
if (typeof TodoOperations !== 'undefined') {
    console.log('✅ TodoOperations module is available');
    console.log('   Available methods:', Object.keys(TodoOperations));
} else {
    console.log('❌ TodoOperations module is not loaded!');
    console.log('   This means the todo-operations.js file is not included or has an error.');
}

// Step 2: Check form elements
console.log('\n🔍 Step 2: Checking reminder form elements...');
const reminderElements = {
    'reminder-enabled': document.getElementById('reminder-enabled'),
    'reminder-datetime': document.getElementById('reminder-datetime'),
    'reminder-type-custom': document.querySelector('input[name="reminder_type"][value="custom"]'),
    'save-button': document.querySelector('.create-todo'),
    'csrf-token': document.querySelector('input[name="csrf_token"]')
};

for (const [name, element] of Object.entries(reminderElements)) {
    if (element) {
        console.log(`✅ ${name}: Found`);
        if (name === 'reminder-datetime' && element.value) {
            console.log(`   Current value: ${element.value}`);
        }
    } else {
        console.log(`❌ ${name}: Missing!`);
    }
}

// Step 3: Test data collection
console.log('\n🔍 Step 3: Testing reminder data collection...');
if (typeof TodoOperations !== 'undefined' && TodoOperations.collectReminderData) {
    try {
        const reminderData = TodoOperations.collectReminderData();
        console.log('✅ Reminder data collection successful:');
        console.log('   Enabled:', reminderData.enabled);
        console.log('   Type:', reminderData.type);
        console.log('   Datetime:', reminderData.datetime);
        console.log('   Before Minutes:', reminderData.beforeMinutes);
        console.log('   Before Unit:', reminderData.beforeUnit);
    } catch (error) {
        console.log('❌ Error collecting reminder data:', error);
    }
} else {
    console.log('❌ collectReminderData function not available');
}

// Step 4: Simulate form submission data
console.log('\n🔍 Step 4: Simulating form submission...');
try {
    const todoId = document.querySelector("input[name='todo_id']");
    const title = document.getElementById('title-input-normal');
    const csrfToken = document.querySelector('input[name="csrf_token"]');
    
    console.log('Form data that would be submitted:');
    console.log('   todo_id:', todoId ? todoId.value : 'MISSING');
    console.log('   title:', title ? title.value : 'MISSING');
    console.log('   csrf_token:', csrfToken ? csrfToken.value : 'MISSING');
    
    if (typeof TodoOperations !== 'undefined' && TodoOperations.collectReminderData) {
        const reminderData = TodoOperations.collectReminderData();
        console.log('   reminder_enabled:', reminderData.enabled);
        console.log('   reminder_type:', reminderData.type);
        console.log('   reminder_datetime:', reminderData.datetime);
    }
    
} catch (error) {
    console.log('❌ Error simulating form submission:', error);
}

// Step 5: Test network connectivity
console.log('\n🔍 Step 5: Testing network connectivity...');
console.log('You can manually test the backend by running this in console:');
console.log(`
// Test backend connection
fetch('/add', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: '_csrf_token=' + encodeURIComponent('${document.querySelector('input[name="csrf_token"]')?.value || 'TOKEN_NOT_FOUND'}') + '&title=Test'
}).then(response => {
    console.log('Backend response status:', response.status);
    return response.json();
}).then(data => {
    console.log('Backend response data:', data);
}).catch(error => {
    console.log('Backend request error:', error);
});
`);

// Step 6: Debug instructions
console.log('\n📝 Debugging Instructions:');
console.log('1. Check if all elements are found (✅) in Step 2');
console.log('2. If reminder data collection works in Step 3, the JavaScript logic is OK');
console.log('3. Try manually setting a reminder time and running Step 3 again');
console.log('4. Check browser Network tab when you save a todo with reminder');
console.log('5. Look for any JavaScript errors in Console tab');
console.log('6. If network requests are failing, check CSRF tokens');

console.log('\n🚀 Debugging script completed!');
console.log('If you see errors above, that\'s where the issue is.');
console.log('If everything looks good, the issue might be in form submission or server-side processing.');