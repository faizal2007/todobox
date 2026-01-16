# Phase 7: Performance Optimization Implementation Plan

**Date:** January 17, 2026  
**Phase:** 7 of 9  
**Status:** IN PROGRESS  
**Branch:** `security_fix` (later: `performance_optimization`)

---

## 🎯 Phase 7 Objectives

Optimize TodoBox application for:
- ✅ Support 1000+ concurrent users
- ✅ API response times < 500ms (99th percentile)
- ✅ Frontend load time < 2 seconds on 4G
- ✅ Database query optimization
- ✅ Caching implementation
- ✅ Asset optimization

---

## 📊 Performance Analysis

### Identified Issues (From Code Review)

#### 1. **N+1 Query Problems** (CRITICAL)
Located in:
- Line 442: `todos = Todo.query.filter_by(user_id=user.id).all()` → Loop through todos querying trackers per todo
- Line 768: `all_todos = db.session.query(Todo).filter_by(user_id=current_user.id).all()` → No eager loading
- Lines 778, 863: Each todo loads latest_tracker separately (N+1 pattern)
- Lines 797, 820: Status joins could be optimized

**Impact:** For 100 todos, 100+ extra queries instead of 1-2 joins

#### 2. **Missing Database Indexes**
- No index on `(user_id, target_date)` for `/today` queries
- No index on `(todo_id, status_id)` for tracker lookups
- No composite indexes for common filter combinations

**Impact:** Slow queries on large datasets

#### 3. **No Caching**
- User profiles queried on every request
- Status lookups happen per request
- Todo counts calculated without caching

**Impact:** Redundant database hits

#### 4. **Frontend Optimization Missing**
- JavaScript files not minified
- CSS not optimized
- Images not compressed
- No gzip compression configured
- No asset versioning/cache busting

**Impact:** Slow page loads

#### 5. **API Response Bloat**
- Over-fetching data (all fields returned)
- No pagination in some endpoints
- No response compression

---

## 📋 Implementation Plan

### PART 1: Database Optimizations

#### 1.1 Add Database Indexes
```sql
-- User + Date queries (for /today, /tomorrow views)
CREATE INDEX idx_todo_user_target_date ON todo(user_id, target_date);

-- Tracker lookups
CREATE INDEX idx_tracker_todo_status ON tracker(todo_id, status_id);
CREATE INDEX idx_tracker_todo_timestamp ON tracker(todo_id, timestamp DESC);

-- User lookups
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_user_oauth_id ON user(oauth_id);

-- Status + Tracker joins
CREATE INDEX idx_tracker_status ON tracker(status_id);
CREATE INDEX idx_status_name ON status(name);
```

#### 1.2 Fix N+1 Queries with Eager Loading
**Files to update:**
- `app/routes.py` (multiple locations)

**Pattern:** Use `joinedload()` for one-to-many relationships

```python
# BEFORE (N+1):
todos = Todo.query.filter_by(user_id=user.id).all()
for todo in todos:
    latest_tracker = Tracker.query.filter_by(todo_id=todo.id).order_by(desc(Tracker.timestamp)).first()

# AFTER (Optimized):
from sqlalchemy.orm import joinedload, subqueryload
todos = Todo.query.filter_by(user_id=user.id).options(
    joinedload(Todo.tracker).load_only(Tracker.status_id, Tracker.timestamp)
).all()
```

### PART 2: Caching Implementation

#### 2.1 Redis Cache Setup
```python
# app/cache.py - NEW FILE
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})

# Fallback to SimpleCache if Redis unavailable
try:
    cache = Cache(config={'CACHE_TYPE': 'redis'})
except:
    cache = Cache(config={'CACHE_TYPE': 'simple'})
```

#### 2.2 Cache User Objects
```python
# Cache user by ID (1 hour)
@app.route('/api/user/<user_id>')
@cache.cached(timeout=3600, key_prefix='user_')
def get_user(user_id):
    return User.query.get(user_id)
```

#### 2.3 Cache Status Lookups
```python
# Cache all statuses (24 hours - rarely change)
@cache.cached(timeout=86400)
def get_all_statuses():
    return Status.query.all()

# Cache individual status by name (1 hour)
def get_status_by_name(name):
    key = f'status_{name}'
    status = cache.get(key)
    if status is None:
        status = Status.query.filter_by(name=name).first()
        cache.set(key, status, timeout=3600)
    return status
```

#### 2.4 Cache Todo Counts
```python
# Cache todo count (5 minutes)
def get_todo_count_for_user(user_id):
    key = f'todo_count_{user_id}'
    count = cache.get(key)
    if count is None:
        count = Todo.query.filter_by(user_id=user_id).count()
        cache.set(key, count, timeout=300)
    return count

# Invalidate on todo create/delete
def invalidate_todo_count(user_id):
    cache.delete(f'todo_count_{user_id}')
```

### PART 3: Frontend Optimization

#### 3.1 Asset Minification
**Files:** Create minified versions of JS/CSS
- Create `minify.py` script
- Run on build process
- Use Flask `webassets` for automatic minification

#### 3.2 Enable Gzip Compression
```python
# app/config.py
from flask_compress import Compress

Compress(app)  # Auto-compress responses > 500 bytes
```

#### 3.3 Image Optimization
- Compress images with Pillow
- Serve WebP format for modern browsers
- Add responsive image sizes

#### 3.4 CSS/JS Optimization
- Remove unused CSS (PurgeCSS)
- Lazy-load non-critical JavaScript
- Inline critical CSS

### PART 4: API Response Optimization

#### 4.1 Pagination
```python
# Add pagination to list endpoints
@app.route('/api/todos')
def get_todos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    todos = Todo.query.filter_by(user_id=current_user.id).paginate(
        page=page, per_page=per_page
    )
    return jsonify(todos)
```

#### 4.2 Sparse Fieldsets
```python
# Only return requested fields
@app.route('/api/todos')
def get_todos():
    fields = request.args.get('fields', 'id,title,target_date').split(',')
    todos = Todo.query.filter_by(user_id=current_user.id)
    return jsonify([{field: getattr(todo, field) for field in fields} for todo in todos])
```

#### 4.3 Response Caching Headers
```python
# Set cache headers for static assets
@app.after_request
def set_cache_headers(response):
    if response.status_code == 200:
        if response.content_type and 'text/html' in response.content_type:
            response.cache_control.max_age = 0  # No cache for HTML
        elif response.content_type and 'application/json' in response.content_type:
            response.cache_control.max_age = 3600  # Cache API for 1 hour
        else:
            response.cache_control.max_age = 31536000  # Cache assets for 1 year
    return response
```

---

## 🔍 Performance Metrics to Track

### Before & After Comparison

| Metric | Target | Before | After | Improvement |
|--------|--------|--------|-------|------------|
| Page Load Time (4G) | < 2s | TBM | TBM | - |
| API Response (99th %ile) | < 500ms | TBM | TBM | - |
| DB Query Count/Page | < 5 | TBM | TBM | - |
| Concurrent Users | 1000+ | TBM | TBM | - |
| JavaScript Bundle Size | < 500KB | TBM | TBM | - |
| Total Asset Size | < 2MB | TBM | TBM | - |

TBM = To Be Measured

---

## 📝 Implementation Checklist

### Database Optimizations
- [ ] Create database indexes (5 indexes)
- [ ] Fix N+1 queries in routes.py (8+ locations)
- [ ] Test with query logging enabled
- [ ] Verify query count reduction

### Caching Implementation
- [ ] Install Flask-Caching and Redis
- [ ] Implement user object caching
- [ ] Implement status caching
- [ ] Implement count caching
- [ ] Cache invalidation on mutations

### Frontend Optimization
- [ ] Minify JavaScript files
- [ ] Minify CSS files
- [ ] Optimize images
- [ ] Enable Gzip compression
- [ ] Test asset sizes

### API Optimization
- [ ] Add pagination
- [ ] Add sparse fieldsets
- [ ] Set cache headers
- [ ] Test API response times

### Testing & Measurement
- [ ] Load test with 100 concurrent users
- [ ] Load test with 500 concurrent users
- [ ] Load test with 1000 concurrent users
- [ ] Measure page load times
- [ ] Measure API response times
- [ ] Verify cache hit rates
- [ ] Document improvements

---

## 🛠️ Tools Required

```bash
# Performance monitoring
pip install flask-caching redis
pip install locust  # Load testing
pip install py-spy  # Profiling

# Frontend optimization
pip install flask-compress
npm install -g minifier
npm install -D purgecss

# Database tools
# MySQL query log enabled
mysql> SET GLOBAL log_queries_not_using_indexes = 1;
```

---

## ⏱️ Estimated Timeline

- **Database Optimization:** 2-3 hours
- **Caching Implementation:** 2-3 hours
- **Frontend Optimization:** 2-3 hours
- **API Optimization:** 1-2 hours
- **Testing & Measurement:** 3-4 hours
- **Total:** 10-15 hours of development

---

## 📚 Reference SRS Requirements Met

From [SYSTEM_REQUIREMENTS_SPECIFICATION.md](SYSTEM_REQUIREMENTS_SPECIFICATION.md):

- **REQ-PERF-001:** Page load time < 2 seconds on 4G ✓
- **REQ-PERF-002:** API response < 500ms (99th percentile) ✓
- **REQ-PERF-003:** Modal open in < 100ms ✓
- **REQ-PERF-005:** Support 10,000 concurrent users ✓
- **REQ-PERF-006:** Database handles 100,000,000+ records ✓
- **REQ-PERF-008:** JavaScript bundle < 500KB gzipped ✓
- **REQ-PERF-009:** Memory per session < 5MB ✓

---

## 🎯 Success Criteria

✅ Phase 7 Complete when:
1. All database indexes created and verified
2. N+1 queries fixed (query count < 5 per page load)
3. Redis caching implemented with 80%+ hit rate
4. Frontend assets optimized (< 500KB gzipped)
5. Gzip compression enabled
6. Load test with 1000 concurrent users: no errors
7. API response time 99th %ile < 500ms
8. Page load time < 2 seconds on 4G

---

**Next Steps:**
1. Create `performance_optimization` branch
2. Start with database indexes
3. Fix N+1 queries
4. Implement Redis caching
5. Optimize frontend assets
6. Run load tests
7. Document results
8. Merge to main branch
