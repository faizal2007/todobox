# Session Expiration Handler - Flow Diagrams & Architecture

## Session Lifecycle Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER SESSION LIFECYCLE                    │
└─────────────────────────────────────────────────────────────────┘

1. LOGIN REQUEST
   ┌──────────────────────────────────────────────────────────────┐
   │ User submits login form                                       │
   │ ↓                                                              │
   │ app/routes.py::login() validates credentials                  │
   │ ↓                                                              │
   │ login_user(user, remember=form.remember_me.data)              │
   │ ↓                                                              │
   │ Flask-Login creates session                                   │
   │ ↓                                                              │
   │ Redirect to dashboard/next page                               │
   └──────────────────────────────────────────────────────────────┘

2. SESSION INITIALIZATION
   ┌──────────────────────────────────────────────────────────────┐
   │ first_request_after_login() →                                │
   │ session['last_activity'] = datetime.utcnow().isoformat()      │
   │ session.modified = True                                       │
   │                                                              │
   │ Session now active with timestamp                             │
   └──────────────────────────────────────────────────────────────┘

3. USER ACTIVITY (EACH REQUEST)
   ┌──────────────────────────────────────────────────────────────┐
   │ @app.before_request handler                                   │
   │ ↓                                                              │
   │ if current_user.is_authenticated:                             │
   │    Is session expired?                                        │
   │        ├─ YES → Redirect to login (handle_expired_session)   │
   │        └─ NO → Update last_activity timestamp                │
   │                session['last_activity'] = now()              │
   │                session.modified = True                        │
   │ ↓                                                              │
   │ Request continues normally                                    │
   └──────────────────────────────────────────────────────────────┘

4. EXPIRATION CHECK
   ┌──────────────────────────────────────────────────────────────┐
   │ SessionExpirationHandler.is_session_expired()                │
   │ ↓                                                              │
   │ Get last_activity from session                                │
   │ ↓                                                              │
   │ Calculate: NOW - last_activity > TIMEOUT?                    │
   │                                                              │
   │ TIMEOUT = 120 minutes (default)                               │
   │ ↓                                                              │
   │ Return: True (expired) or False (valid)                       │
   └──────────────────────────────────────────────────────────────┘

5. WARNING CHECK
   ┌──────────────────────────────────────────────────────────────┐
   │ SessionExpirationHandler.is_session_warning_time()           │
   │ ↓                                                              │
   │ Get last_activity from session                                │
   │ ↓                                                              │
   │ Calculate: TIMEOUT - NOW_TO_EXPIRY < WARNING_THRESHOLD?      │
   │                                                              │
   │ THRESHOLD = 10 minutes (default)                              │
   │ ↓                                                              │
   │ Return: True (warn) or False (ok)                             │
   └──────────────────────────────────────────────────────────────┘

6. TEMPLATE RENDERING
   ┌──────────────────────────────────────────────────────────────┐
   │ session_aware_context_processor() provides:                  │
   │ • session_warning: bool                                       │
   │ • remaining_time: int (minutes)                               │
   │ • session_expired: bool                                       │
   │ ↓                                                              │
   │ Template receives variables:                                  │
   │ {% if session_warning %}                                      │
   │    Show: "Session expires in {{ remaining_time }} minutes"    │
   │ {% endif %}                                                   │
   └──────────────────────────────────────────────────────────────┘

7. LOGOUT
   ┌──────────────────────────────────────────────────────────────┐
   │ User clicks logout                                            │
   │ ↓                                                              │
   │ app/routes.py::logout() called                                │
   │ ↓                                                              │
   │ logout_user()  # Flask-Login                                  │
   │ ↓                                                              │
   │ Session cleared                                               │
   │ ↓                                                              │
   │ Redirect to login page                                        │
   └──────────────────────────────────────────────────────────────┘

8. EXPIRED SESSION RECOVERY
   ┌──────────────────────────────────────────────────────────────┐
   │ Session expired, user sees warning                            │
   │ ↓                                                              │
   │ Redirect to: /login?next=/original/route                      │
   │ ↓                                                              │
   │ Flash message: "Session expired. Please login again."         │
   │ ↓                                                              │
   │ User re-authenticates                                         │
   │ ↓                                                              │
   │ Redirect to original route (next parameter)                   │
   └──────────────────────────────────────────────────────────────┘
```

## Request Flow with Session Handler

```
┌─────────────────────────────────────────────────────────────────┐
│                   REQUEST PROCESSING FLOW                        │
└─────────────────────────────────────────────────────────────────┘

HTTP Request
   ↓
┌─────────────────────────────────┐
│ Flask before_request handlers   │
│ (registered in order)           │
└─────────────────────────────────┘
   ↓
   ├─ ensure_initialized()
   │  └─ Initialize DB if needed
   ├─ disable_cache()
   │  └─ Disable cache headers
   └─ before_request_session_handler()  ← Session Handler
      ├─ Check: is_authenticated?
      │  └─ No: Continue
      │  └─ Yes:
      │     ├─ Check: is_session_expired()?
      │     │  ├─ Yes: Flash + Redirect to /login
      │     │  └─ No: Update last_activity ✓
      │     └─ Continue
      └─ Session.modified = True
         ↓
   ┌─────────────────────────────┐
   │ Route Handler               │
   │ (with decorators)           │
   │                             │
   │ @session_required           │
   │ def my_route():             │
   │    return render(...)       │
   └─────────────────────────────┘
      ↓
   ┌─────────────────────────────┐
   │ Template Context Processor  │
   │                             │
   │ session_aware_context_      │
   │ processor():                │
   │  - session_warning: bool    │
   │  - remaining_time: int      │
   │  - session_expired: bool    │
   └─────────────────────────────┘
      ↓
   ┌─────────────────────────────┐
   │ Render Template             │
   │ (with context variables)    │
   └─────────────────────────────┘
      ↓
Flask after_request handlers
   ↓
HTTP Response
```

## Session State Machine

```
┌───────────────────────────────────────────────────────────────────┐
│                    SESSION STATE MACHINE                           │
└───────────────────────────────────────────────────────────────────┘

                         ┌──────────────────┐
                         │  UNAUTHENTICATED │
                         │   (No Session)   │
                         └────────┬─────────┘
                                  │ Login
                                  ↓
                    ┌──────────────────────────┐
                    │      AUTHENTICATED       │
                    │   (Session Valid)        │
                    │ last_activity = NOW      │
                    └────────┬─────────────────┘
                             │
                    ┌────────┴─────────┐
                    │ Each Request     │
                    │ Update Activity  │
                    │ last_activity=NOW│
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        Time < WARNING    WARNING <= TIME   TIME > TIMEOUT
        (Valid)          < TIMEOUT          (Expired)
         │                   │                  │
         ↓                   ↓                  ↓
    ┌────────┐        ┌──────────┐       ┌──────────┐
    │ VALID  │        │ WARNING  │       │ EXPIRED  │
    │        │        │          │       │          │
    │ Normal │        │ "Session │       │ Redirect │
    │ Ops    │        │  expires │       │ to Login │
    │        │        │  in 10   │       │          │
    │        │        │  minutes"│       │ Flash    │
    │        │        │          │       │ Message  │
    └────────┘        └──────────┘       └──────────┘
        ↓                   │                  ↓
        └───────────────────┼──────────────────┘
                            │ User Action
                            ↓ (extends session)
                   ┌────────────────────┐
                   │ last_activity      │
                   │ updated to NOW     │
                   │ (Resets Counter)   │
                   └────────┬───────────┘
                            │
                            └─────────┐
                                      │
                            ┌─────────┴────────┐
                            │ Back to VALID    │
                            │ or WARNING state │
                            └──────────────────┘

OR

User Action: Logout
│
└─→ ┌──────────────────────────┐
    │ UNAUTHENTICATED          │
    │ (Session Cleared)        │
    │ Redirect to /login       │
    └──────────────────────────┘
```

## API/AJAX Request Flow

```
┌──────────────────────────────────────────────────────────────┐
│              AJAX REQUEST WITH SESSION CHECK                 │
└──────────────────────────────────────────────────────────────┘

JavaScript:
fetch('/api/todos', {
    headers: {
        'X-Requested-With': 'XMLHttpRequest'
    }
})

                    ↓

before_request_session_handler():
   ├─ Detect: Is AJAX request?
   │  (Check header: X-Requested-With = XMLHttpRequest)
   ├─ Is session expired?
   │  ├─ YES:
   │  │  └─ Return JSON 401:
   │  │     {
   │  │       'error': 'Session expired',
   │  │       'redirect_url': '/login?next=/api/todos'
   │  │     }
   │  └─ NO: Update activity, continue
   └─ Handle with JSON response

JavaScript receives:
{
    error: 'Session expired',
    redirect_url: '/login?next=/api/todos'
}
Status: 401 Unauthorized

Client-side handling:
fetch('/api/todos')
    .then(response => {
        if (response.status === 401) {
            window.location.href = response.json().redirect_url
        }
    })

                    ↓

Redirect to login page with original URL
```

## Timing Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        TIMING DIAGRAM                            │
│                                                                  │
│  Time → (120 minutes = INACTIVITY_TIMEOUT)                      │
└──────────────────────────────────────────────────────────────────┘

0 min        30 min        60 min        110 min       120 min
 │            │             │             │             │
 ├────────────┼─────────────┼─────────────┼─────────────┤
 │            │             │             │             │
Login      Activity       Activity      WARNING      EXPIRED
│          Update         Update        Starts        ↓
├─────────────────────────────────────────────────────│
│  ✓ VALID SESSION  │                │ ⚠️ WARNING    │ ✗ SESSION EXPIRES
│  last_activity    │                │ remaining:    │ Redirect to login
│  = T=0            │                │ 10 minutes    │ Flash message
│  Remaining: 120   │                │ Show alert    │ Clear session
│  minutes          │                │ to user       │
└────────────────────────────────────┴──────────────┘

SCENARIO 1: User Active
0──────────────┬ (Activity at 60 min) → Timer resets
               │ last_activity = 60 min
               │ Remaining: 120 minutes again
               ↓
               └──────────────┬ (Activity at 120 min)
                              └─ Never expires, keeps working

SCENARIO 2: User Inactive
0────────────────────────────────────────────────────────┤ (Idle 120 min)
                                                         ↓
                                                    SESSION EXPIRED
                                                    • Flash warning
                                                    • Redirect to /login
                                                    • Clear session
                                                    • Set next=/previous/page
```

## Component Interaction Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│                   COMPONENT INTERACTION                           │
└───────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Flask Application (app/__init__.py)                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ init_session_handler(app)                                │  │
│  │                                                          │  │
│  │ 1. Register @before_request handler                     │  │
│  │    before_request_session_handler()                     │  │
│  │                                                          │  │
│  │ 2. Register context_processor                           │  │
│  │    session_aware_context_processor()                    │  │
│  │                                                          │  │
│  │ 3. Available to all routes and templates                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
       ┌──────────────────────┼──────────────────────┐
       ↓                      ↓                      ↓

   ┌─────────────┐    ┌──────────────┐     ┌──────────────┐
   │   ROUTES    │    │  TEMPLATES   │     │ DECORATORS   │
   │             │    │              │     │              │
   │@session_    │    │session_      │     │@session_     │
   │required     │    │warning       │     │required      │
   │             │    │remaining_    │     │              │
   │@app.route() │    │time          │     │Protects      │
   │def route(): │    │session_      │     │routes        │
   │             │    │expired       │     │              │
   │Protected    │    │              │     │              │
   └─────────────┘    └──────────────┘     └──────────────┘
       ↓                      ↓                      ↓
       └──────────────────────┼──────────────────────┘
                              ↓

   ┌─────────────────────────────────────────────────────┐
   │  SessionExpirationHandler                           │
   │                                                     │
   │  • is_session_expired()                             │
   │  • is_session_warning_time()                        │
   │  • get_remaining_time_minutes()                     │
   │  • update_last_activity()                           │
   │  • handle_expired_session()                         │
   │  • extend_session_expiration()                      │
   │                                                     │
   └────────────────┬────────────────────────────────────┘
                    ↓
    ┌───────────────────────────────────────────────────┐
    │  Flask Session (server-side)                      │
    │                                                   │
    │  session['last_activity'] = ISO timestamp         │
    │  session.modified = True                          │
    │                                                   │
    │  Stores: DateTime when user last was active       │
    └───────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌───────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING FLOW                            │
└───────────────────────────────────────────────────────────────────┘

Error Condition                 Handler                 Result
─────────────────────────────────────────────────────────────────

1. Session Expired
   └─ Current Time >          handle_expired_        ├─ Web: Redirect
      Last Activity +         session()              │   to /login
      TIMEOUT                 (Web/AJAX aware)       └─ AJAX: JSON 401

2. Invalid Timestamp
   └─ last_activity has       is_session_expired()   ├─ Catch ValueError
      bad format              error handler          └─ Return False
                                                        (treat as valid)

3. No Timestamp
   └─ last_activity missing   get_remaining_time()   └─ Return full
                                                        TIMEOUT value

4. Unauthenticated User
   └─ current_user is None    All functions check    ├─ Return False
                              is_authenticated()     ├─ Return 0
                                                     └─ No action

5. Database Connection Error
   └─ DB unavailable on       initialize_default_    ├─ Log warning
      startup                 data()                 └─ Continue
                                                        (session handler
                                                         doesn't depend
                                                         on DB)

6. Clock Skew
   └─ Server time            Uses datetime.utcnow()  ├─ Verify NTP
      inconsistent           consistently            │  settings
                                                     └─ Uses server
                                                        time only

7. CSRF Validation Failure
   └─ CSRF token expired     Existing CSRF           ├─ Still works
                             handlers               └─ Flash message
                             (unchanged)               + redirect
```

## Deployment Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT ARCHITECTURE                    │
└────────────────────────────────────────────────────────────────┘

Single Server:
┌─────────────────────────────────────┐
│ Flask App Server                    │
│ ├─ app/session_handler.py           │
│ ├─ Session data: Flask Session      │
│ │  (in-memory or file backend)      │
│ └─ Response to client               │
└─────────────────────────────────────┘

Multi-Server with Shared Session Backend:
┌──────────────────────────────────────────────────────────────┐
│ Load Balancer                                                │
├─────────┬─────────┬─────────────────────────────────────────┤
│         │         │                                         │
↓         ↓         ↓                                         
┌────┐ ┌────┐ ┌────┐                                        
│App│ │ App│ │ App│   (Multiple instances)                 
│ 1  │ │ 2  │ │ 3  │                                        
└─┬──┘ └─┬──┘ └─┬──┘                                        
  │       │     │                                           
  └───────┼─────┘                                           
          │                                                
          ↓                                                
    ┌────────────────┐                                      
    │ Session Store  │                                      
    │ (Redis/        │                                      
    │ Memcached)     │                                      
    │                │                                      
    │ session_data = │                                      
    │ {              │                                      
    │ 'last_activity'│                                      
    │ 'user_id'      │                                      
    │ }              │                                      
    └────────────────┘                                      

Features:
✓ Session shared across instances
✓ User can be routed to any server
✓ Session data consistent
✓ Timestamp validated on each request
```

This architecture ensures that the session handler works correctly in both simple and distributed deployments.
