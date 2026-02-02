"""
Test suite for on-the-fly mode switching and content conversion
Tests the behavior when users switch between simple and advanced modes
"""

import sys
import os

# Add the parent directory (project root) to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from app.models import Todo, User
from datetime import datetime
from contextlib import contextmanager


@contextmanager
def app_context():
    """Provide app context for tests"""
    with app.app_context():
        yield


def setup_test_user():
    """Create a test user"""
    timestamp = str(datetime.utcnow().timestamp()).replace('.', '')
    user = User(
        email=f'test_{timestamp}@example.com'
    )
    db.session.add(user)
    db.session.commit()
    return user


class TestModeSwitch:
    """Test on-the-fly content conversion between simple and advanced modes"""
    
    @staticmethod
    def test_simple_todo_content_preserved():
        """Test that simple todo content is preserved correctly"""
        with app_context():
            user = setup_test_user()
            
            # Create simple mode todo
            simple_todo = Todo(
                name='Simple Todo Test',
                details='- [ ] Item 1\n- [ ] Item 2\n- [x] Item 3',
                user_id=user.id,
                todo_type='simple',
            )
            db.session.add(simple_todo)
            db.session.commit()
            
            # Verify the todo was created
            retrieved_todo = Todo.query.filter_by(id=simple_todo.id).first()
            assert retrieved_todo is not None
            assert retrieved_todo.todo_type == 'simple'
            assert '- [ ] Item 1' in retrieved_todo.details
            assert '- [ ] Item 2' in retrieved_todo.details
            assert '- [x] Item 3' in retrieved_todo.details
    
    @staticmethod
    def test_advanced_todo_content_preserved():
        """Test that advanced todo content is preserved correctly"""
        with app_context():
            user = setup_test_user()
            
            # Create advanced mode todo
            advanced_todo = Todo(
                name='Advanced Todo Test',
                details='# Header\n\nSome content with **bold** and *italic* text',
                user_id=user.id,
                todo_type='advanced',
            )
            db.session.add(advanced_todo)
            db.session.commit()
            
            # Verify the todo was created
            retrieved_todo = Todo.query.filter_by(id=advanced_todo.id).first()
            assert retrieved_todo is not None
            assert retrieved_todo.todo_type == 'advanced'
            assert '# Header' in retrieved_todo.details
            assert '**bold**' in retrieved_todo.details
            assert '*italic*' in retrieved_todo.details
    
    @staticmethod
    def test_todo_type_detection_simple_mode():
        """Test that simple mode todos have correct type"""
        with app_context():
            user = setup_test_user()
            
            simple_todo = Todo(
                name='Simple Todo',
                details='- [ ] Item',
                user_id=user.id,
                todo_type='simple',
            )
            db.session.add(simple_todo)
            db.session.commit()
            
            # Load and verify
            todo = db.session.get(Todo, simple_todo.id)
            assert todo.todo_type == 'simple'
    
    @staticmethod
    def test_todo_type_detection_advanced_mode():
        """Test that advanced mode todos have correct type"""
        with app_context():
            user = setup_test_user()
            
            advanced_todo = Todo(
                name='Advanced Todo',
                details='# Header',
                user_id=user.id,
                todo_type='advanced',
            )
            db.session.add(advanced_todo)
            db.session.commit()
            
            # Load and verify
            todo = db.session.get(Todo, advanced_todo.id)
            assert todo.todo_type == 'advanced'
    
    @staticmethod
    def test_mixed_content_todo():
        """Test todo with mixed content (checklist + markdown)"""
        with app_context():
            user = setup_test_user()
            
            # Create mixed content todo
            todo = Todo(
                name='Mixed Content',
                details='# Instructions\n\n- [ ] Task 1\n- [ ] Task 2\n\nAdditional notes',
                user_id=user.id,
                todo_type='advanced',
            )
            db.session.add(todo)
            db.session.commit()
            
            # Verify all content is preserved
            retrieved = db.session.get(Todo, todo.id)
            assert '# Instructions' in retrieved.details
            assert '- [ ] Task 1' in retrieved.details
            assert '- [ ] Task 2' in retrieved.details
            assert 'Additional notes' in retrieved.details
    
    @staticmethod
    def test_empty_todo_handling():
        """Test handling of empty content"""
        with app_context():
            user = setup_test_user()
            
            # Create todo with empty details
            todo = Todo(
                name='Empty Todo',
                details='',
                user_id=user.id,
                todo_type='simple',
            )
            db.session.add(todo)
            db.session.commit()
            
            # Verify it was created
            retrieved = db.session.get(Todo, todo.id)
            assert retrieved is not None
            assert retrieved.details == ''
    
    @staticmethod
    def test_todo_update_preserves_type():
        """Test that updating a todo preserves its type"""
        with app_context():
            user = setup_test_user()
            
            simple_todo = Todo(
                name='Simple Todo',
                details='- [ ] Original',
                user_id=user.id,
                todo_type='simple',
            )
            db.session.add(simple_todo)
            db.session.commit()
            todo_id = simple_todo.id
            
            # Update the todo
            simple_todo.details = '- [ ] Updated Item 1\n- [ ] Updated Item 2'
            db.session.commit()
            
            # Verify type is preserved
            retrieved = db.session.get(Todo, todo_id)
            assert retrieved.todo_type == 'simple'
            assert '- [ ] Updated Item 1' in retrieved.details
    
    @staticmethod
    def test_mode_switch_preserves_id():
        """Test that switching modes doesn't affect todo ID"""
        with app_context():
            user = setup_test_user()
            
            simple_todo = Todo(
                name='Simple Todo',
                details='- [ ] Item',
                user_id=user.id,
                todo_type='simple',
            )
            db.session.add(simple_todo)
            db.session.commit()
            original_id = simple_todo.id
            
            # "Switch" mode by updating content
            simple_todo.details = '# Rich Content\n\nSome markdown'
            simple_todo.todo_type = 'advanced'
            db.session.commit()
            
            # Verify ID is unchanged
            retrieved = db.session.get(Todo, original_id)
            assert retrieved is not None
            assert retrieved.id == original_id
    
    @staticmethod
    def test_multiple_users_todos_isolated():
        """Test that todos from different users are isolated"""
        with app_context():
            # Create first user and todo
            timestamp = str(datetime.utcnow().timestamp()).replace('.', '')
            user1 = User(
                email=f'user1_{timestamp}@example.com'
            )
            db.session.add(user1)
            db.session.commit()
            
            todo1 = Todo(
                name='User1 Todo',
                details='- [ ] Item 1',
                user_id=user1.id,
                todo_type='simple',
            )
            db.session.add(todo1)
            db.session.commit()
            
            # Create second user and todo
            timestamp2 = str(datetime.utcnow().timestamp()).replace('.', '')
            user2 = User(
                email=f'user2_{timestamp2}@example.com'
            )
            db.session.add(user2)
            db.session.commit()
            
            todo2 = Todo(
                name='User2 Todo',
                details='# User2 Content',
                user_id=user2.id,
                todo_type='advanced',
            )
            db.session.add(todo2)
            db.session.commit()
            
            # Verify todos are isolated
            user1_todos = Todo.query.filter_by(user_id=user1.id).all()
            user2_todos = Todo.query.filter_by(user_id=user2.id).all()
            
            assert len(user1_todos) == 1
            assert len(user2_todos) == 1
            assert user1_todos[0].name == 'User1 Todo'
            assert user2_todos[0].name == 'User2 Todo'


class TestChecklistCompatibility:
    """Test checklist format detection and compatibility"""
    
    @staticmethod
    def test_dash_checklist_format():
        """Test detection of dash checklist format"""
        content = '- [ ] item 1\n- [x] item 2'
        import re
        pattern = r'^[-*+]\s*\[[^\]]*\]'
        assert re.search(pattern, content, re.MULTILINE)
    
    @staticmethod
    def test_asterisk_checklist_format():
        """Test detection of asterisk checklist format"""
        content = '* [ ] item 1\n* [x] item 2'
        import re
        pattern = r'^[-*+]\s*\[[^\]]*\]'
        assert re.search(pattern, content, re.MULTILINE)
    
    @staticmethod
    def test_plus_checklist_format():
        """Test detection of plus checklist format"""
        content = '+ [ ] item 1\n+ [x] item 2'
        import re
        pattern = r'^[-*+]\s*\[[^\]]*\]'
        assert re.search(pattern, content, re.MULTILINE)
    
    @staticmethod
    def test_mixed_checklist_format():
        """Test detection of mixed checklist formats"""
        content = '- [ ] dash\n* [ ] asterisk\n+ [x] plus'
        import re
        pattern = r'^[-*+]\s*\[[^\]]*\]'
        assert re.search(pattern, content, re.MULTILINE)
    
    @staticmethod
    def test_non_checklist_content():
        """Test that non-checklist content is not detected as checklist"""
        content = '# Header\n- This is a dash list\n- Not a checklist'
        import re
        pattern = r'^[-*+]\s*\[[^\]]*\]'
        assert not re.search(pattern, content, re.MULTILINE)
    
    @staticmethod
    def test_checked_unchecked_variants():
        """Test both checked and unchecked variants"""
        content = '- [ ] unchecked\n- [x] checked\n- [X] uppercase'
        import re
        pattern = r'^[-*+]\s*\[[^\]]*\]'
        assert re.search(pattern, content, re.MULTILINE)
    
    @staticmethod
    def test_checklist_with_spaces():
        """Test checklist format with various spacing"""
        content = '-  [ ]  item\n*   [x]   item\n+    [ ]    item'
        import re
        pattern = r'^[-*+]\s*\[[^\]]*\]'
        assert re.search(pattern, content, re.MULTILINE)


class TestContentConversion:
    """Test the conversion functions for mode switching"""
    
    @staticmethod
    def test_normalize_simple_markdown_format():
        """Test that simple markdown is normalized correctly"""
        from app.routes import normalize_checkboxes
        
        content = '- [ ] Item 1\n- [x] Item 2\n* [ ] Item 3\n+ [x] Item 4'
        result = normalize_checkboxes(content)
        
        # Should convert all to dash format
        assert '- [ ] Item 1' in result
        assert '- [x] Item 2' in result or '- [ x ] Item 2' in result.replace(' ', '')
    
    @staticmethod
    def test_preserve_whitespace_in_conversion():
        """Test that whitespace is preserved during conversion"""
        from app.routes import normalize_checkboxes
        
        content = '- [ ] First\n- [ ] Second\n- [ ] Third'
        result = normalize_checkboxes(content)
        
        # Should preserve line breaks
        lines = result.strip().split('\n')
        assert len(lines) >= 2


class TestDataPersistence:
    """Test that data persists correctly across mode switches"""
    
    @staticmethod
    def test_simple_content_persists_after_update():
        """Test that simple mode content persists after update"""
        with app_context():
            timestamp = str(datetime.utcnow().timestamp()).replace('.', '')
            user = User(
                email=f'persist_{timestamp}@example.com'
            )
            db.session.add(user)
            db.session.commit()
            
            # Create simple todo
            todo = Todo(
                name='Persist Test',
                details='- [ ] Original Item',
                user_id=user.id,
                todo_type='simple',
            )
            db.session.add(todo)
            db.session.commit()
            todo_id = todo.id
            
            # Update it
            todo.details = '- [ ] Updated Item'
            db.session.commit()
            
            # Retrieve and verify
            retrieved = db.session.get(Todo, todo_id)
            assert retrieved.details == '- [ ] Updated Item'
            assert retrieved.todo_type == 'simple'
    
    @staticmethod
    def test_advanced_content_persists_after_update():
        """Test that advanced mode content persists after update"""
        with app_context():
            timestamp = str(datetime.utcnow().timestamp()).replace('.', '')
            user = User(
                email=f'persist2_{timestamp}@example.com'
            )
            db.session.add(user)
            db.session.commit()
            
            # Create advanced todo
            todo = Todo(
                name='Persist Test',
                details='# Original Header',
                user_id=user.id,
                todo_type='advanced',
            )
            db.session.add(todo)
            db.session.commit()
            todo_id = todo.id
            
            # Update it
            todo.details = '# Updated Header\n\nNew content'
            db.session.commit()
            
            # Retrieve and verify
            retrieved = db.session.get(Todo, todo_id)
            assert retrieved.details == '# Updated Header\n\nNew content'
            assert retrieved.todo_type == 'advanced'


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
