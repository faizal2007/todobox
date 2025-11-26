# API Reference

## Overview

TodoBox is a server-rendered Flask application that uses HTML forms and HTTP redirects for most operations. This document describes all available routes and endpoints.

## Authentication Routes

### Login

- **Route**: `GET/POST /login`
- **Authentication**: None
- **Description**: User login page and authentication
- **Parameters**:
  - `username` (required): User login username
  - `password` (required): User login password
  - `remember_me` (optional): Checkbox to remember login
- **Response**:
  - Success: Redirect to requested page or todo list
  - Failure: Flash message and redirect to login
- **Status Code**: 302 (redirect)

### Logout

- **Route**: `GET /logout`
- **Authentication**: Required
- **Description**: Logout current user and clear session
- **Response**: Redirect to index page
- **Status Code**: 302 (redirect)

## Todo Management Routes

### Index Page

- **Route**: `GET /` or `GET /index`
- **Authentication**: None
- **Description**: Redirect to today's todo list
- **Response**: Redirect to `/today/list`
- **Status Code**: 302 (redirect)

### Main Todo View

- **Route**: `GET /todo`
- **Authentication**: Required
- **Description**: Display today's todo items
- **Response**: Rendered HTML page with today's todos
- **Status Code**: 200

### List Todos by Date

- **Route**: `GET /<id>/list`
- **Authentication**: Required
- **Parameters**:
  - `id` (required): 'today' or 'tomorrow'
- **Description**: Display todo list for specific date
- **Response**: Rendered HTML with filtered todo items
- **Status Code**: 200 (valid id) or 404 (invalid id)

### View Todo Item

- **Route**: `GET /<path>/view`
- **Authentication**: Required
- **Parameters**:
  - `path` (required): 'pending' or 'done'
- **Description**: View all pending or completed tasks
- **Response**: Rendered HTML with filtered tasks
- **Status Code**: 200 (valid path) or 404 (invalid path)

### Get Todo Details (AJAX)

- **Route**: `POST /<id>/todo`
- **Authentication**: Required
- **Parameters**:
  - `id` (required): Todo item ID
  - `tbl_save` (optional): Save flag to determine button rendering
- **Description**: Fetch specific todo item details for editing
- **Response**: JSON with todo details

```json
{
  "status": "Success",
  "id": 1,
  "title": "Task title",
  "activities": "Task description",
  "modified": "2024-01-15 10:30:00",
  "button": "<button>Save</button>"
}
```

- **Status Code**: 200

### Add or Update Todo

- **Route**: `POST /add`
- **Authentication**: Required
- **Parameters**:
  - `title` (required): Todo item title
  - `activities` (required): Todo item description (supports Markdown)
  - `todo_id` (optional): Empty string for new, ID for update
  - `tomorrow` (optional): Flag to schedule for tomorrow
  - `byPass` (optional): Flag to bypass no-change detection
- **Description**: Create new todo or update existing one
- **Response**: JSON response with status
- **Status Code**: 200

#### Success Response

```json
{
  "status": "success"
}
```

#### Error Response

```json
{
  "status": "failed",
  "msg": "Title Required."
}
```

### Mark Todo as Done

- **Route**: `POST /<id>/<todo_id>/done`
- **Authentication**: Required
- **Parameters**:
  - `id` (required): 'today' or 'tomorrow'
  - `todo_id` (required): Todo item ID
- **Description**: Mark a todo item as completed
- **Response**: JSON with success status

```json
{
  "status": "Success",
  "todo_id": 1
}
```

- **Status Code**: 200

### Delete Todo

- **Route**: `POST /<todo_id>/delete`
- **Authentication**: Required
- **Parameters**:
  - `todo_id` (required): Todo item ID
- **Description**: Delete a todo item and its tracking records
- **Response**: Redirect to todo page
- **Status Code**: 302 (redirect)

## User Account Routes

### Account Settings

- **Route**: `GET/POST /account`
- **Authentication**: Required
- **Description**: View and update user account details
- **Parameters** (POST):
  - `username` (required): New username
  - `email` (required): New email address
- **Response**:
  - GET: Rendered HTML form
  - POST: Flash message and form reload
- **Status Code**: 200

### Security Settings

- **Route**: `GET/POST /security`
- **Authentication**: Required
- **Description**: Change user password
- **Parameters** (POST):
  - `oldPassword` (required): Current password for verification
  - `password` (required): New password
  - `confirm` (required): Password confirmation (must match)
- **Response**:
  - GET: Rendered HTML form
  - POST: Flash message and form reload
- **Status Code**: 200

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 302 | Found - Redirect |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Login required |
| 404 | Not Found - Invalid route or resource |
| 500 | Internal Server Error |

## Data Validation Rules

### Todo Item

- **Title**: Required, non-empty after strip
- **Activities**: Required, supports Markdown formatting
- **Date**: Future dates allowed (tomorrow parameter)

### User Account

- **Username**: Required, must be unique
- **Email**: Required, must be valid email format and unique
- **Password**: Minimum 8 characters recommended, must be confirmed on change

### Login Credentials

- **Username**: Must exist in database
- **Password**: Must match hashed password

## Error Handling

All endpoints handle errors gracefully:

- Missing required parameters: JSON error response with message
- Invalid data: Flash message to user interface
- Unauthorized access: Redirect to login page
- Not found: 404 page

## Session Management

- **Session Duration**: 120 minutes (2 hours)
- **Session Type**: Persistent (Flask default)
- **Remember Me**: Extends session beyond browser close
- **Session Timeout**: Requires re-login with notice

## CSRF Protection

All POST requests must include valid CSRF token:

```html
<form method="post">
  {{ csrf_token() }}
  <!-- form fields -->
</form>
```

Token is automatically included in all Flask-WTF forms.

## Rate Limiting

No rate limiting currently implemented. Consider adding for production use.

## API Usage Examples

### Create a New Todo (HTML Form)

```html
<form method="post" action="/add">
  {{ csrf_token() }}
  <input type="hidden" name="todo_id" value="">
  <input type="text" name="title" value="Buy groceries">
  <textarea name="activities">Milk, eggs, bread</textarea>
  <button type="submit">Save</button>
</form>
```

### Fetch Todo via AJAX

```javascript
fetch('/' + todoId + '/todo', {
  method: 'POST',
  body: new FormData(form),
  headers: {
    'X-CSRFToken': csrfToken
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### Mark Todo as Done via AJAX

```javascript
fetch('/today/' + todoId + '/done', {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrfToken
  }
})
.then(response => response.json())
.then(data => console.log(data));
```
