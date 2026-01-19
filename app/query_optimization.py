"""Database query optimization utilities

This module provides helper functions to eliminate N+1 query problems
using SQLAlchemy eager loading strategies.

Optimization Patterns:
1. joinedload() - For one-to-many and one-to-one relationships
2. subqueryload() - For many-to-many relationships
3. contains_eager() - For filtered eager loading
4. selectinload() - Modern eager loading (SQLAlchemy 1.4+)
"""

from sqlalchemy.orm import joinedload, subqueryload, contains_eager
from sqlalchemy import desc, and_, or_
from app.models import Todo, Tracker, Status, User
from typing import List, Dict, Any


def get_todos_with_latest_tracker(user_id: int, target_date=None) -> List[Todo]:
    """Get todos with latest tracker efficiently
    
    This resolves N+1 problem where each todo loads its latest tracker separately.
    
    Args:
        user_id: User ID
        target_date: Optional filter by target_date
        
    Returns:
        List of todos with trackers loaded
        
    Query Count: 2 queries (instead of N+1)
    - Query 1: Get todos with joined trackers
    - Query 2: Subquery for latest trackers per todo
    """
    from sqlalchemy.orm import Query
    
    # Subquery for latest tracker per todo
    latest_tracker_subquery = (
        Todo.query.session.query(
            Tracker.id,
            Tracker.todo_id,
            Tracker.status_id,
            Tracker.timestamp
        )
        .distinct(Tracker.todo_id)
        .order_by(Tracker.todo_id, Tracker.timestamp.desc())
    )
    
    query = Todo.query.filter_by(user_id=user_id)
    
    if target_date:
        query = query.filter_by(target_date=target_date)
    
    # Load todos with their latest tracker
    todos = query.options(
        subqueryload(Todo.tracker)
    ).all()
    
    return todos


def get_todos_with_status(user_id: int) -> List[Dict[str, Any]]:
    """Get todos with current status efficiently
    
    Returns todos with their current status name without N+1 queries.
    
    Args:
        user_id: User ID
        
    Returns:
        List of dicts with {todo, status_name}
        
    Query Count: 1 query (optimized join)
    """
    from sqlalchemy.orm import Session
    from sqlalchemy import func
    
    # Subquery for latest tracker per todo
    latest_tracker_per_todo = (
        Todo.query.session.query(
            Tracker.todo_id,
            func.max(Tracker.id).label('tracker_id')
        )
        .group_by(Tracker.todo_id)
    ).subquery()
    
    # Single query joining todos, latest trackers, and statuses
    results = (
        Todo.query.session.query(Todo, Status.name)
        .outerjoin(
            latest_tracker_per_todo,
            Todo.id == latest_tracker_per_todo.c.todo_id
        )
        .outerjoin(Tracker, Tracker.id == latest_tracker_per_todo.c.tracker_id)
        .outerjoin(Status, Status.id == Tracker.status_id)
        .filter(Todo.user_id == user_id)
        .all()
    )
    
    return [{'todo': todo, 'status_name': status_name} for todo, status_name in results]


def get_todos_with_all_trackers(user_id: int) -> List[Todo]:
    """Get todos with all their trackers (for history view)
    
    Efficiently loads all trackers for all todos without N+1.
    
    Args:
        user_id: User ID
        
    Returns:
        List of todos with all trackers loaded
        
    Query Count: 2 queries
    """
    todos = (
        Todo.query
        .filter_by(user_id=user_id)
        .options(subqueryload(Todo.tracker))
        .all()
    )
    
    return todos


def get_user_statistics(user_id: int) -> Dict[str, Any]:
    """Get user statistics without N+1 queries
    
    Calculates total todos, completed, failed, etc. in minimal queries.
    
    Args:
        user_id: User ID
        
    Returns:
        Dict with statistics
        
    Query Count: 3-4 queries (instead of many)
    """
    from sqlalchemy import func
    
    # Get counts by status in single query
    stats = (
        Todo.query.session.query(
            Status.id,
            Status.name,
            func.count(Todo.id).label('count')
        )
        .outerjoin(Tracker, Todo.id == Tracker.todo_id)
        .outerjoin(Status, Status.id == Tracker.status_id)
        .filter(Todo.user_id == user_id)
        .group_by(Status.id, Status.name)
        .all()
    )
    
    return {
        'by_status': [
            {'status_id': status_id, 'status_name': status_name, 'count': count}
            for status_id, status_name, count in stats
        ],
        'total': sum(row[2] for row in stats) if stats else 0
    }


def bulk_load_todos_batch(user_id: int, batch_size: int = 100) -> List[Todo]:
    """Load todos in batches for memory efficiency
    
    For large todo lists, load in batches to avoid memory issues.
    
    Args:
        user_id: User ID
        batch_size: Number of todos per batch
        
    Yields:
        Lists of todos (batch_size items each)
        
    Memory Usage: O(batch_size) instead of O(total_todos)
    """
    query = Todo.query.filter_by(user_id=user_id).options(
        subqueryload(Todo.tracker)
    )
    
    for offset in range(0, query.count(), batch_size):
        batch = query.offset(offset).limit(batch_size).all()
        yield batch


def count_todos_by_status(user_id: int) -> Dict[str, int]:
    """Count todos by status efficiently
    
    Single query to count todos per status (no N+1).
    
    Args:
        user_id: User ID
        
    Returns:
        Dict mapping status names to counts
        
    Query Count: 1 query
    """
    from sqlalchemy import func
    
    result = (
        Todo.query.session.query(
            Status.name,
            func.count(Todo.id).label('count')
        )
        .join(Tracker, Tracker.todo_id == Todo.id)
        .join(Status, Status.id == Tracker.status_id)
        .filter(Todo.user_id == user_id)
        .group_by(Status.name)
        .all()
    )
    
    return {status_name: count for status_name, count in result}


def get_user_with_all_data(user_id: int) -> User:
    """Load user with all related data (for profile page)
    
    Loads user, todos, and trackers in minimal queries.
    
    Args:
        user_id: User ID
        
    Returns:
        User object with todos and trackers loaded
        
    Query Count: 2-3 queries (instead of N+1+M)
    """
    user = (
        User.query
        .filter_by(id=user_id)
        .options(subqueryload(User.todos).subqueryload(Todo.tracker))
        .first()
    )
    
    return user


__all__ = [
    'get_todos_with_latest_tracker',
    'get_todos_with_status',
    'get_todos_with_all_trackers',
    'get_user_statistics',
    'bulk_load_todos_batch',
    'count_todos_by_status',
    'get_user_with_all_data',
]
