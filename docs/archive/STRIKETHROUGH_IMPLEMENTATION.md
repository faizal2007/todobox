# Strikethrough Feature Implementation Guide

## Overview
Strikethrough formatting has been added to SimpleMDE markdown editors throughout the TodoBox application. The button appears in the editor toolbar and can be triggered with keyboard shortcuts.

## Feature Details
- **Button Label:** S̶ (Unicode strikethrough S)
- **Markdown Syntax:** `~~selected text~~`
- **Keyboard Shortcuts:**
  - Windows/Linux: `Ctrl+Shift+S`
  - Mac: `Cmd+Shift+S`

## Files Containing SimpleMDE Configuration

### 1. **app/templates/list.html** (Lines 108-141)
**Purpose:** New todo creation modal & existing todo editing (from "Today/Tomorrow/Undone" list views)

**Editor Element ID:** `details-textarea`

**SimpleMDE Toolbar Configuration:**
```javascript
toolbar: [
    "bold", 
    "italic",
    {
        name: "strikethrough",
        action: function(editor) {
             var cm = editor.codemirror;
             var selectedText = cm.getSelection();
             cm.replaceSelection(selectedText ? "~~" + selectedText + "~~" : "~~text~~");
             cm.focus();
        },
        className: "fa fa-strikethrough",
        title: "Strikethrough (Ctrl-Shift-S)",
        default: true
    },
    "unordered-list", 
    "ordered-list", "|", 
    "quote",
    "link",
    "preview"
],
```

**Keyboard Shortcut Setup:**
```javascript
simplemde.codemirror.setOption("extraKeys", {
     "Ctrl-Shift-S": function(cm) {
          var selectedText = cm.getSelection();
          cm.replaceSelection(selectedText ? "~~" + selectedText + "~~" : "~~text~~");
          cm.focus();
     },
     "Cmd-Shift-S": function(cm) {
          var selectedText = cm.getSelection();
          cm.replaceSelection(selectedText ? "~~" + selectedText + "~~" : "~~text~~");
          cm.focus();
     }
});
```

---

### 2. **app/templates/todo.html** (Lines 108-145)
**Purpose:** View/edit todo details page

**Editor Element ID:** `activitiesFormControlTextArea1`

**SimpleMDE Toolbar Configuration:** Same pattern as list.html (see above)

**Keyboard Shortcut Setup:** Same pattern as list.html (see above)

---

### 3. **app/templates/undone.html** (Lines 174-211)
**Purpose:** Undone/KIV todos view with editing capability

**Editor Element ID:** `details-textarea`

**SimpleMDE Toolbar Configuration:** Same pattern as list.html (see above)

**Keyboard Shortcut Setup:** Same pattern as list.html (see above)

---

## How to Add/Modify Toolbar Buttons

### Adding a New Button
1. **Find the SimpleMDE initialization** in your target file (search for `new SimpleMDE`)
2. **Add button object to toolbar array:**
```javascript
{
    name: "button-name",
    action: function(editor) {
        var cm = editor.codemirror;
        var selectedText = cm.getSelection();
        // Your formatting logic here
        cm.replaceSelection(formattedText);
        cm.focus();
    },
    className: "fa fa-icon-name",  // Font Awesome icon class
    title: "Tooltip Text (Keyboard Shortcut)",
    default: true
}
```

3. **Add keyboard shortcut** in `setOption("extraKeys", {...})` section:
```javascript
"Ctrl-Key": function(cm) {
    // Same logic as button action
}
```

---

## Key Points to Remember

✅ **All three files must be updated together** - to ensure consistent experience across all pages where todos can be edited

✅ **Editor Element IDs differ by page:**
- `details-textarea` → list.html, undone.html
- `activitiesFormControlTextArea1` → todo.html

✅ **Toolbar button structure:**
- Pre-built buttons like `"bold"` and `"italic"` are strings
- Custom buttons are objects with `name`, `action`, `className`, `title`, `default` properties

✅ **Font Awesome icons** - uses `fa fa-*` class naming convention

✅ **CodeMirror shortcuts** - keyboard mappings go in `extraKeys` option

---

## Testing the Feature

1. **Hard refresh browser:** `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
2. **Create or edit a todo** from any page
3. **Verify button appears** in editor toolbar
4. **Test button click:** Select text and click strikethrough button → should wrap with `~~`
5. **Test keyboard shortcut:** Select text and press `Ctrl+Shift+S` (or `Cmd+Shift+S` on Mac) → should wrap with `~~`

---

## Future Enhancements

If you need to add more formatting options:
1. Update all three files: `list.html`, `todo.html`, `undone.html`
2. Use the strikethrough implementation as a template
3. Update CHANGELOG.md with the new feature
4. Commit changes with descriptive message

---

**Last Updated:** December 15, 2025  
**Feature Status:** ✅ Active & Tested
