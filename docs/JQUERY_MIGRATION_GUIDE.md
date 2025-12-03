# jQuery to Vanilla JavaScript Migration Guide

Quick reference for developers maintaining TodoBox after the jQuery optimization.

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

### 5. Modal Operations

**Old (jQuery):**
```javascript
$('#modal').modal('show');
$('#modal').modal('hide');
```

**New (Vanilla - Bootstrap 4):**
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

// Add multiple classes
element.classList.add('active', 'primary');

// Remove multiple classes
element.classList.remove('active', 'primary');
```

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

// Create URLSearchParams
var params = new URLSearchParams({
    'key1': 'value1',
    'key2': 'value2'
});
```

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

## Common Issues and Solutions

### Issue: Elements added dynamically not getting handlers

**Solution:** Use event delegation
```javascript
// Won't work for dynamically added elements
document.querySelector('.btn').addEventListener('click', handler);

// Will work for dynamically added elements
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

## When to Keep Using jQuery

1. **DataTables** - Complex table widget, kept as is
2. **SimpleMDE** - Markdown editor, kept as is
3. **Bootstrap plugin initialization** - Theme/layout management

Don't remove these - they require jQuery for proper functionality.

## Resources

- [MDN: DOM API](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model)
- [MDN: Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [MDN: Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)
- [MDN: querySelector](https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector)

---

Last updated: December 3, 2025
