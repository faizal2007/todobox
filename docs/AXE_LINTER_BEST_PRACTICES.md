# Axe-Linter Best Practices Guide

This guide ensures all HTML templates are created with accessibility compliance and are free from axe-linter errors.

## Core Principles

### 1. ARIA Attributes - Numeric Values Only

All ARIA attributes that accept numeric values must use numbers, NOT strings with symbols.

**❌ WRONG:**

```html
<div role="progressbar" 
     aria-valuenow="75.5%" 
     aria-valuemin="0" 
     aria-valuemax="100%">
    75.5%
</div>
```yaml

**✅ CORRECT:**

```html
<div role="progressbar" 
     aria-valuenow="76" 
     aria-valuemin="0" 
     aria-valuemax="100">
    75.5%
</div>
```sql

**Key Points:**

- Remove `%` symbols from numeric ARIA values
- Use integers for `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
- For dynamic values, round to nearest integer: `{{ value | round(0) }}`
- For JavaScript, use `parseInt()` or `Math.round()`

### 2. Dynamic ARIA Attributes in Templates

When using Jinja2 templates with dynamic values, set ARIA attributes via JavaScript instead of templating:

**❌ WRONG (Linter can't parse Jinja2 in HTML attributes):**

```html
<div role="progressbar" 
     aria-valuenow="{{ completion_rate | round(0) }}">
    {{ completion_rate }}%
</div>
```yaml

**✅ CORRECT:**

```html
<!-- HTML: No complex Jinja2 in ARIA attributes -->
<div id="progressBar" 
     role="progressbar" 
     aria-valuemin="0" 
     aria-valuemax="100"
     aria-label="Completion rate: {{ completion_rate }}%">
    {{ completion_rate }}%
</div>

<!-- JavaScript: Set numeric values dynamically -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        const widthPercent = progressBar.style.width;
        const ariaValue = parseInt(widthPercent, 10) || 0;
        progressBar.setAttribute('aria-valuenow', ariaValue);
    }
});
</script>
```yaml

### 3. Form Labels and Accessibility

**❌ WRONG:**

```html
<input type="text" placeholder="Enter your name">
```yaml

**✅ CORRECT:**

```html
<label for="userName">Name:</label>
<input type="text" id="userName" placeholder="Enter your name">
```json

### 4. Image Alt Text

**❌ WRONG:**

```html
<img src="icon.png">
```json

**✅ CORRECT:**

```html
<img src="icon.png" alt="Description of image">
```json

### 5. Button Accessibility

**❌ WRONG:**

```html
<div class="btn" onclick="doSomething()">Click me</div>
```json

**✅ CORRECT:**

```html
<button type="button" onclick="doSomething()">Click me</button>
```json

### 6. Color Contrast

Ensure text has sufficient contrast ratio (minimum 4.5:1 for normal text, 3:1 for large text):

**❌ WRONG:**

```html
<p style="color: #999; background: #f5f5f5;">Light gray on light background</p>
```json

**✅ CORRECT:**

```html
<p style="color: #333; background: #f5f5f5;">Dark gray on light background</p>
```json

### 7. Heading Hierarchy

**❌ WRONG:**

```html
<h1>Main Title</h1>
<h3>Subsection</h3>  <!-- Missing h2 -->
<h2>Another Section</h2>
```yaml

**✅ CORRECT:**

```html
<h1>Main Title</h1>
<h2>Subsection</h2>
<h2>Another Section</h2>
```yaml

### 8. Navigation and Landmarks

**❌ WRONG:**

```html
<div>
    <a href="#">Home</a>
    <a href="#">About</a>
</div>
```json

**✅ CORRECT:**

```html
<nav>
    <a href="#">Home</a>
    <a href="#">About</a>
</nav>
```yaml

### 9. Links - Must Have Meaningful Text

**❌ WRONG:**

```html
<a href="/more">Click here</a>
<a href="/info">Read more</a>
```yaml

**✅ CORRECT:**

```html
<a href="/more">Learn more about our services</a>
<a href="/info">Read product information</a>
```yaml

### 10. Form Inputs - Proper Types

**❌ WRONG:**

```html
<input type="text" placeholder="Email">
<input type="text" placeholder="Phone">
```yaml

**✅ CORRECT:**

```html
<input type="email" placeholder="Email">
<input type="tel" placeholder="Phone">
```yaml

## Template Checklist

Before creating a new template, verify:

- [ ] All form inputs have associated labels with `for` attributes
- [ ] All buttons use `<button>` tag or have `role="button"`
- [ ] All images have `alt` text
- [ ] All ARIA numeric values are integers without symbols (%, px, etc.)
- [ ] Heading hierarchy is sequential (h1 → h2 → h3, not h1 → h3)
- [ ] Link text is descriptive and meaningful
- [ ] Color contrast meets WCAG standards
- [ ] Navigation uses `<nav>` landmark
- [ ] Main content uses `<main>` landmark
- [ ] Footer uses `<footer>` landmark
- [ ] No keyboard traps (all interactive elements are keyboard accessible)
- [ ] Dynamic ARIA attributes are set via JavaScript, not templates
- [ ] All form fields have proper `type` attributes

## Common Axe-Linter Errors and Fixes

### Error: aria-valid-attr-value: ARIA attributes must conform to valid values

**Cause:** ARIA attribute contains invalid format (strings with symbols)

**Fix:** Remove symbols, ensure numeric values only:

```javascript
// Convert percentage string to integer
const value = parseInt("75.5%", 10); // Result: 75
element.setAttribute('aria-valuenow', value);
```yaml

### Error: color-contrast: Elements must have sufficiently contrasting colors

**Cause:** Text color insufficient contrast against background

**Fix:** Use higher contrast colors:

```css
/* Bad */
color: #aaa; /* Too light */

/* Good */
color: #333; /* Dark enough */
```yaml

### Error: label: Form elements must have associated labels

**Cause:** Input without label

**Fix:** Add label with `for` attribute:

```html
<label for="email">Email:</label>
<input type="email" id="email">
```yaml

### Error: link-name: Links must have discernible text

**Cause:** Link has no meaningful text

**Fix:** Add descriptive text:

```html
<!-- Bad -->
<a href="/page">➜</a>

<!-- Good -->
<a href="/page">Go to next page ➜</a>
```yaml

## Testing Checklist

For each new template:

1. **Run axe DevTools** browser extension
2. **Check "Violations"** tab for errors
3. **Check "Best Practices"** tab for warnings
4. **Fix all violations** before merging
5. **Test keyboard navigation** (Tab, Enter, Escape)
6. **Test screen reader** (NVDA, JAWS, or VoiceOver)
7. **Test zoom** at 200% magnification
8. **Test color contrast** with Contrast Checker tool

## Tools and Resources

- **axe DevTools**: Browser extension for testing
- **WAVE**: Web accessibility evaluation tool
- **Lighthouse**: Built into Chrome DevTools
- **Contrast Checker**: <https://webaim.org/resources/contrastchecker/>
- **WCAG 2.1 Guidelines**: <https://www.w3.org/WAI/WCAG21/quickref/>

## For Dynamic Values

### In Jinja2 Templates (HTML)

```html
<!-- DO NOT put complex Jinja2 in ARIA attributes -->
<div id="myProgressBar" 
     role="progressbar"
     aria-valuemin="0"
     aria-valuemax="100"
     style="width: {{ completion_rate }}%">
</div>
```yaml

### In JavaScript (Set after page load)

```javascript
document.addEventListener('DOMContentLoaded', function() {
    const bar = document.getElementById('myProgressBar');
    const percent = parseInt(bar.style.width, 10);
    bar.setAttribute('aria-valuenow', percent);
});
```yaml

## Summary

**Key Rules:**

1. ✅ ARIA values = integers only
2. ✅ Dynamic ARIA = set via JavaScript
3. ✅ Forms = labels with `for` attributes
4. ✅ Links = descriptive meaningful text
5. ✅ Images = `alt` text
6. ✅ Hierarchy = sequential headings
7. ✅ Contrast = WCAG AA compliant
8. ✅ Semantics = use proper HTML elements

Following these guidelines ensures **zero axe-linter errors** in all templates.
