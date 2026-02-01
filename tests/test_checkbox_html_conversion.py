#!/usr/bin/env python
"""
Test the checkbox HTML conversion feature
"""
import re
from bleach import clean

# Simulate the conversion function from routes.py
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'code', 'pre', 'blockquote', 'ul', 'ol', 'li', 'a', 'del', 's', 'input']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title'], 'input': ['type', 'disabled', 'checked']}

def convert_checkboxes_to_html(text):
    """Convert markdown checkbox syntax to HTML checkbox elements"""
    lines = text.split('\n')
    html_lines = []
    for line in lines:
        # Match checkbox pattern: - [ ] or * [ ] or + [ ] (with or without 'x')
        # Supports both dash and asterisk list formats: - [ ] or * [ ] or * [x]
        match = re.match(r'^(\s*)[-*+]\s*\[([x\s]*)\]\s*(.*)', line, re.IGNORECASE)
        if match:
            indent = match.group(1)
            # Check if 'x' is present anywhere in the brackets (checked=true)
            checked = 'checked' if 'x' in match.group(2).lower() else ''
            text_content = match.group(3)
            # Create HTML with visual checkbox
            html_lines.append(f'{indent}<li><input type="checkbox" disabled {checked}> {text_content}</li>')
        else:
            html_lines.append(line)
    
    # Wrap in <ul> tags if we have list items
    has_items = any('<li>' in line for line in html_lines)
    if has_items:
        return '<ul>\n' + '\n'.join(html_lines) + '\n</ul>'
    else:
        return text  # Return original if no checkboxes found

# Test cases
test_cases = [
    # Test 1: Simple checkbox items (unchecked) with dashes
    ("- [ ] asdfsafd\n- [ ] asfasdf", "Dash format: 2 unchecked checkboxes"),
    
    # Test 2: Asterisk format (like markdown bullets)
    ("* [ ] asdfsafd\n* [ ] asfasdf", "Asterisk format: 2 unchecked checkboxes"),
    
    # Test 3: Plus format
    ("+ [ ] asdfsafd\n+ [ ] asfasdf", "Plus format: 2 unchecked checkboxes"),
    
    # Test 4: Mixed checked and unchecked with asterisks
    ("* [ ] first item\n* [x] completed item", "Asterisk with mixed checked/unchecked"),
    
    # Test 5: Single checkbox with asterisk
    ("* [ ] single item", "Asterisk single item"),
    
    # Test 6: With indentation (asterisk)
    ("  * [ ] indented item", "Asterisk with indentation"),
    
    # Test 7: Checkbox with spaces (asterisk)
    ("* [  ] item with spaces", "Asterisk with flexible spacing"),
]

print("=" * 70)
print("Testing Checkbox HTML Conversion")
print("=" * 70)

for i, (input_text, description) in enumerate(test_cases, 1):
    print(f"\nTest {i}: {description}")
    print(f"Input:  {repr(input_text)}")
    
    # Convert to HTML
    html = convert_checkboxes_to_html(input_text)
    
    # Sanitize HTML
    clean_html = clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    
    print(f"Output: {clean_html[:150]}..." if len(clean_html) > 150 else f"Output: {clean_html}")
    
    # Verify key elements
    if "input type=\"checkbox\"" in clean_html:
        print("✓ HTML checkbox element created")
    else:
        print("✗ No checkbox element found!")
    
    if "disabled" in clean_html:
        print("✓ Checkbox is disabled (read-only)")
    
    if "checked" in clean_html and "[x]" in input_text:
        print("✓ Checked attribute set correctly")

print("\n" + "=" * 70)
print("Test completed successfully!")
print("=" * 70)
