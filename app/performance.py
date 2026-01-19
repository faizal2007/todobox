"""Performance testing and metrics collection

This module provides tools for:
1. Load testing with concurrent users (using Locust)
2. Query performance profiling
3. Memory usage tracking
4. API response time measurement
5. Cache hit rate monitoring
"""

import time
import logging
from functools import wraps
from typing import Callable, Dict, List, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Collect and report performance metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.query_counts: Dict[str, int] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
    def record_metric(self, name: str, value: float) -> None:
        """Record a performance metric (e.g., response time)"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)
    
    def record_query_count(self, route: str, count: int) -> None:
        """Record number of queries for a route"""
        self.query_counts[route] = count
    
    def record_cache_hit(self) -> None:
        """Increment cache hit counter"""
        self.cache_hits += 1
    
    def record_cache_miss(self) -> None:
        """Increment cache miss counter"""
        self.cache_misses += 1
    
    def get_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        if metric_name not in self.metrics:
            return {}
        
        values = self.metrics[metric_name]
        if not values:
            return {}
        
        values_sorted = sorted(values)
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'p50': values_sorted[len(values) // 2],
            'p95': values_sorted[int(len(values) * 0.95)],
            'p99': values_sorted[int(len(values) * 0.99)],
        }
    
    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate (0-1)"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total
    
    def report(self) -> str:
        """Generate performance report"""
        report = "PERFORMANCE METRICS REPORT\n"
        report += "=" * 50 + "\n\n"
        
        # Response time metrics
        for metric_name in sorted(self.metrics.keys()):
            stats = self.get_stats(metric_name)
            report += f"{metric_name}:\n"
            report += f"  Count: {stats.get('count', 0)}\n"
            report += f"  Min: {stats.get('min', 0):.3f}ms\n"
            report += f"  Max: {stats.get('max', 0):.3f}ms\n"
            report += f"  Avg: {stats.get('avg', 0):.3f}ms\n"
            report += f"  P50: {stats.get('p50', 0):.3f}ms\n"
            report += f"  P95: {stats.get('p95', 0):.3f}ms\n"
            report += f"  P99: {stats.get('p99', 0):.3f}ms\n\n"
        
        # Query counts
        report += "QUERY COUNTS BY ROUTE:\n"
        for route, count in sorted(self.query_counts.items()):
            report += f"  {route}: {count} queries\n"
        
        report += f"\nCACHE METRICS:\n"
        report += f"  Hits: {self.cache_hits}\n"
        report += f"  Misses: {self.cache_misses}\n"
        report += f"  Hit Rate: {self.get_cache_hit_rate():.2%}\n"
        
        return report


# Global metrics instance
metrics = PerformanceMetrics()


def profile_request(f: Callable) -> Callable:
    """Decorator to profile request duration and query count
    
    Usage:
        @app.route('/api/todos')
        @profile_request
        def get_todos():
            return jsonify(todos)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        from sqlalchemy import event
        from sqlalchemy.engine import Engine
        
        # Track query count
        query_count = 0
        
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            nonlocal query_count
            query_count += 1
        
        event.listen(Engine, "after_cursor_execute", receive_after_cursor_execute)
        
        # Measure request duration
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
        finally:
            event.remove(Engine, "after_cursor_execute", receive_after_cursor_execute)
            duration = (time.time() - start_time) * 1000  # Convert to ms
            
            # Record metrics
            route = request.endpoint or request.path
            metrics.record_metric(f'{route}_duration', duration)
            metrics.record_query_count(route, query_count)
            
            # Log if slow
            if duration > 500:
                logger.warning(f"SLOW REQUEST: {route} took {duration:.1f}ms ({query_count} queries)")
            elif query_count > 10:
                logger.warning(f"HIGH QUERY COUNT: {route} executed {query_count} queries")
        
        return result
    
    return decorated_function


def profile_function(f: Callable) -> Callable:
    """Decorator to profile function execution time
    
    Usage:
        @profile_function
        def expensive_calculation():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
        finally:
            duration = (time.time() - start_time) * 1000
            metrics.record_metric(f'{f.__name__}_duration', duration)
            
            if duration > 100:
                logger.warning(f"SLOW FUNCTION: {f.__name__} took {duration:.1f}ms")
        
        return result
    
    return decorated_function


class LoadTestScenario:
    """Define load test scenarios for Locust"""
    
    LIGHT = {
        'users': 100,
        'spawn_rate': 10,
        'duration': 300,  # 5 minutes
    }
    
    MEDIUM = {
        'users': 500,
        'spawn_rate': 50,
        'duration': 600,  # 10 minutes
    }
    
    HEAVY = {
        'users': 1000,
        'spawn_rate': 100,
        'duration': 900,  # 15 minutes
    }
    
    STRESS = {
        'users': 5000,
        'spawn_rate': 500,
        'duration': 1200,  # 20 minutes
    }


def generate_load_test_report(scenario: str = 'LIGHT') -> str:
    """Generate load test configuration file for Locust
    
    Usage:
        report = generate_load_test_report('HEAVY')
        with open('locustfile.py', 'w') as f:
            f.write(report)
    """
    scenario_config = getattr(LoadTestScenario, scenario)
    
    return f'''"""Locust load test configuration for TodoBox

Run with:
    locust -f locustfile.py --host=http://localhost:5000
"""

from locust import HttpUser, task, between
import random


class TodoBoxUser(HttpUser):
    """Simulated TodoBox user for load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    @task(3)
    def view_today(self):
        """View todos for today"""
        self.client.get('/today')
    
    @task(2)
    def view_tomorrow(self):
        """View todos for tomorrow"""
        self.client.get('/tomorrow')
    
    @task(2)
    def view_later(self):
        """View todos for later"""
        self.client.get('/later')
    
    @task(1)
    def create_todo(self):
        """Create a new todo"""
        self.client.post('/api/todo/create', json={{
            'title': 'Test todo {{}}'.format(random.randint(1, 10000)),
            'target_date': '2026-01-20',
            'description': 'Load test todo'
        }})
    
    @task(1)
    def get_achievements(self):
        """View achievements"""
        self.client.get('/achievements')


# Load test configuration
# Users: {scenario_config['users']}
# Spawn Rate: {scenario_config['spawn_rate']} users/sec
# Duration: {scenario_config['duration']} seconds

SCENARIO = "{scenario}"
USERS = {scenario_config['users']}
SPAWN_RATE = {scenario_config['spawn_rate']}
DURATION = {scenario_config['duration']}
'''


__all__ = [
    'PerformanceMetrics',
    'metrics',
    'profile_request',
    'profile_function',
    'LoadTestScenario',
    'generate_load_test_report',
]
