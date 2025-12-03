# jQuery to Vanilla JavaScript Migration Guide

**For:** Developers, Code Reviewers  
**Read Time:** 15 minutes  
**Status:** Complete  
**Last Updated:** December 3, 2025  
**Related Documentation:** [JavaScript Optimization](JAVASCRIPT_OPTIMIZATION.md), [Code Review](CODE_REVIEW.md), [API Documentation](API.md)

## Overview

Quick reference guide for developers maintaining TodoBox after the jQuery optimization. Contains pattern mappings, common use cases, and solutions to typical migration issues.

---

## Key Patterns Used

### 1. Event Listeners

**Old (jQuery):**

```javascript
$('.btn-delete').click(function() { ... });
$(document.body).on('click', '#save', function() { ... });
```

**New (Vanilla):**

```javascript
document.querySelectorAll('.btn-delete').forEach(function(btn) {
    btn.addEventListener('click', function() { ... });
});

document.addEventListener('click', function(e) {
    if (e.target && e.target.id === 'save') { ... }
});
```

### 2. AJAX Requests

**Old (jQuery):**

```javascript
$.post('/api/endpoint', {
    'data': value,
    '_csrf_token': '{{ csrf_token() }}'
}, function(data) {
    console.log(data);
}).fail(function(error) {
    console.error(error);
});
```

**New (Vanilla):**

```javascript
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': '{{ csrf_token() }}'
    },
    body: new URLSearchParams({
        'data': value,
        '_csrf_token': '{{ csrf_token() }}'
    })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error(error));
```

### 3. DOM Manipulation

**Old (jQuery):**

```javascript
$('#element').val(value);
$('#element').prop('disabled', true);
$('#element').addClass('active');
$('#element').hide();
$('.items').each(function() { ... });
```

**New (Vanilla):**

```javascript
document.getElementById('element').value = value;
document.getElementById('element').disabled = true;
document.getElementById('element').classList.add('active');
document.getElementById('element').style.display = 'none';
document.querySelectorAll('.items').forEach(function(item) { ... });
```

### 4. Data Attributes

**Old (jQuery):**

```javascript
var id = $button.data('id');
$button.data('email', 'user@example.com');
```

**New (Vanilla):**

```javascript
var id = button.dataset.id;
button.dataset.email = 'user@example.com';
```

### 5. Modal Operations (Bootstrap 4)

**Old (jQuery):**

```javascript
$('#modal').modal('show');
$('#modal').modal('hide');
```

**New (Vanilla):**

```javascript
// Show
var modal = document.getElementById('modal');
modal.classList.add('show');
modal.style.display = 'block';
document.body.classList.add('modal-open');

// Hide
modal.classList.remove('show');
modal.style.display = 'none';
document.body.classList.remove('modal-open');
```

---

## Common Use Cases

### Finding Elements

```javascript
// Single element
var element = document.getElementById('id');
var element = document.querySelector('.class');

// Multiple elements
var elements = document.querySelectorAll('.class');
var elements = document.getElementsByClassName('class');
```

### Checking if Element Has Class

```javascript
// jQuery
if ($element.hasClass('active')) { ... }

// Vanilla
if (element.classList.contains('active')) { ... }
```

### Getting Text Content

```javascript
// jQuery
var text = $element.text();

// Vanilla
var text = element.textContent;
```

### Setting HTML

```javascript
// jQuery
$element.html('<div>content</div>');

// Vanilla
element.innerHTML = '<div>content</div>';
```

### Finding Parent/Sibling

```javascript
// jQuery
var parent = $element.closest('.parent');
var next = $element.next();

// Vanilla
var parent = element.closest('.parent');
var next = element.nextElementSibling;
```

---

## CSS Class Management

```javascript
// Add class
element.classList.add('active');

// Remove class
element.classList.remove('active');

// Toggle class
element.classList.toggle('active');

// Check if has class
if (element.classList.contains('active')) { ... }

// Add/remove multiple classes
element.classList.add('active', 'primary');
element.classList.remove('active', 'primary');
```

---

## Form Operations

```javascript
// Get input value
var value = document.getElementById('input').value;

// Set input value
document.getElementById('input').value = 'new value';

// Disable input
document.getElementById('input').disabled = true;

// Get form data
var formData = new FormData(document.getElementById('form'));

// Create URL parameters
var params = new URLSearchParams({
    'key1': 'value1',
    'key2': 'value2'
});
```

---

## Event Handling

### Single Element

```javascript
button.addEventListener('click', function(e) {
    e.preventDefault();
    // handler code
});
```

### Multiple Elements

```javascript
document.querySelectorAll('.btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
        // handler code
    });
});
```

### Event Delegation

```javascript
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn-delete')) {
        // handler code
    }
    if (e.target && e.target.id === 'submit') {
        // handler code
    }
});
```

---

## Promise Patterns

### Success/Error Handling

```javascript
fetch(url)
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));
```

### Sequential Operations

```javascript
fetch(url1)
    .then(response => response.json())
    .then(data => {
        // Use data
        return fetch(url2);
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));
```

### Parallel Operations

```javascript
Promise.all([
    fetch(url1).then(r => r.json()),
    fetch(url2).then(r => r.json())
])
.then(([data1, data2]) => {
    console.log(data1, data2);
})
.catch(error => console.error(error));
```

---

## Common Issues and Solutions

### Issue: Dynamically added elements not responding to handlers

**Solution:** Use event delegation

```javascript
// Won't work for dynamic elements
document.querySelector('.btn').addEventListener('click', handler);

// Will work for dynamic elements
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn')) {
        handler();
    }
});
```

### Issue: CSRF token not sent in POST request

**Solution:** Add to headers or body

```javascript
fetch(url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': '{{ csrf_token() }}'  // Add to headers
    },
    body: new URLSearchParams({
        '_csrf_token': '{{ csrf_token() }}'   // Or add to body
    })
});
```

### Issue: Modal not displaying after fetch

**Solution:** Re-initialize modal classes and backdrop

```javascript
var modal = document.getElementById('modal');
modal.classList.add('show');
modal.style.display = 'block';
document.body.classList.add('modal-open');

// Add backdrop
var backdrop = document.createElement('div');
backdrop.className = 'modal-backdrop fade show';
document.body.appendChild(backdrop);
```

### Issue: Form data not submitting correctly

**Solution:** Proper URLSearchParams usage

```javascript
var params = new URLSearchParams();
params.append('key', 'value');
params.append('_csrf_token', '{{ csrf_token() }}');

fetch(url, {
    method: 'POST',
    body: params
});
```

---

## When to Keep Using jQuery

1. **DataTables** - Complex table widget, requires jQuery
2. **SimpleMDE** - Markdown editor, requires jQuery
3. **Bootstrap plugin initialization** - Theme/layout management

**Do not remove these** - they require jQuery for proper functionality.

---

## Troubleshooting

### Modal backdrop not showing

- Ensure `document.body.classList.add('modal-open')` is called
- Check that backdrop div is created and added to DOM
- Verify CSS classes match Bootstrap 4 specifications

### CSRF token missing

- Check that token is passed in headers or body
- Verify `{{ csrf_token() }}` is available in template context
- Use Network tab in browser DevTools to inspect requests

### Event handlers not firing

- Use event delegation for dynamically added elements
- Check that selector matches actual DOM structure
- Verify `preventDefault()` is called when needed
- Use console.log() to debug event handling

### Fetch request timing out

- Increase timeout if needed (timeout not built into Fetch)
- Use AbortController for timeout implementation
- Check network connectivity in DevTools

---

## Resources

- **[MDN: DOM API](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model)** - DOM manipulation reference
- **[MDN: Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)** - Fetch documentation
- **[MDN: Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)** - Promise reference
- **[MDN: querySelector](https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector)** - Element selection

---

**Last Updated:** December 3, 2025  
**Status:** Active Reference Guide  
**Version:** 1.0
