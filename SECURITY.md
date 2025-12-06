# Security Configuration for TodoBox

## Overview
This document outlines the security measures implemented in TodoBox to protect against common web application vulnerabilities.

## Security Measures Implemented

### 1. Input Validation and Sanitization
- **HTML Escaping**: All user inputs are escaped using `html.escape()` to prevent XSS attacks
- **Length Validation**: Input fields have maximum length constraints (title: 255 chars, activities: 10,000 chars)
- **Markdown Sanitization**: Uses `bleach` library to sanitize markdown content with allowed tags/attributes

### 2. Security Headers
- **X-Content-Type-Options**: Set to `nosniff` to prevent MIME type sniffing
- **X-Frame-Options**: Set to `DENY` to prevent clickjacking attacks
- **X-XSS-Protection**: Enables browser XSS filtering
- **Referrer-Policy**: Set to `strict-origin-when-cross-origin`
- **Content-Security-Policy**: Restricts resource loading to trusted sources

### 3. Session Security
- **Secure Cookies**: `SESSION_COOKIE_SECURE=true` for HTTPS environments
- **HttpOnly Cookies**: `SESSION_COOKIE_HTTPONLY=true` to prevent XSS cookie theft
- **SameSite Cookies**: Set to `Lax` to prevent CSRF attacks
- **Session Timeout**: 120-minute session lifetime

### 4. CSRF Protection
- Flask-WTF CSRF protection enabled on all forms
- CSRF tokens required for state-changing operations

### 5. Authentication & Authorization
- Flask-Login for session management
- OAuth2 integration with Google for secure authentication
- Admin role-based access control
- User isolation (users can only access their own data)

### 6. Database Security
- **SQL Injection Prevention**: Uses SQLAlchemy ORM with parameterized queries
- **Optional Encryption**: Todo content can be encrypted at rest
- **Database URL Security**: Database credentials managed via environment variables

### 7. Environment Configuration
- **Secret Key Security**: Auto-generates secure random key if not provided
- **Environment Variables**: Sensitive configuration via environment variables
- **Debug Mode**: Disabled in production with additional security checks

### 8. Email Security
- **Template Injection Prevention**: Email templates use escaped variables
- **SMTP Authentication**: Secure SMTP with TLS encryption

## Security Best Practices

### For Deployment:
1. Set strong `SECRET_KEY` in environment variables
2. Use HTTPS in production (set `PREFERRED_URL_SCHEME=https`)
3. Configure secure database credentials
4. Enable todo encryption for sensitive data (`TODO_ENCRYPTION_ENABLED=true`)
5. Review and adjust Content-Security-Policy for your domain
6. Use secure SMTP configuration for email features

### For Development:
1. Never commit credentials or secrets to version control
2. Use `.env` file for local environment variables
3. Regularly update dependencies for security patches
4. Test with security headers enabled

## Security Dependencies
- `bleach`: HTML sanitization
- `cryptography`: Encryption support
- `email-validator`: Email validation
- `Flask-WTF`: CSRF protection
- `MarkupSafe`: Safe string handling

## Vulnerability Mitigations
- **XSS**: Input escaping, CSP headers, secure template rendering
- **CSRF**: CSRF tokens, SameSite cookies
- **Clickjacking**: X-Frame-Options header
- **SQL Injection**: ORM usage, parameterized queries
- **Session Hijacking**: Secure cookies, session timeout
- **Information Disclosure**: Security headers, error handling
- **Template Injection**: Safe template rendering with escaped variables

## Reporting Security Issues
Security vulnerabilities should be reported privately to the maintainers.