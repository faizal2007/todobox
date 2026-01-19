"""
Enhanced test coverage for mark_done and mark_kiv routes.
These tests explicitly cover error paths that were missed before.

KEY INSIGHT: The original syntax error `}, 404)` was in the ERROR HANDLER,
not the success path. Tests that only exercise the success path will never
catch such errors. These tests verify error paths explicitly.
"""
import pytest
from app.models import Todo, User


class TestMarkDoneErrorPaths:
    """Test error paths for mark_done and mark_kiv routes - these catch hidden errors!"""
        
    def test_mark_done_error_path_not_found(self, auth_client):
        """Test mark_done with non-existent todo returns proper error.
        
        KEY: This test DOES trigger the error handler (line 2048).
        If there's a syntax error in the error handler, this will catch it!
        
        The original syntax error `}, 404)` would cause HTTP 500 or TypeError
        when this code path executes.
        """
        # Use a todo ID that definitely doesn't exist
        response = auth_client.post('/99999/done', follow_redirects=False)
        
        # Should return 404 (or redirect depending on implementation)
        # The key is that it shouldn't be a 500 error or exception
        assert response.status_code in [302, 404], \
            f"Got unexpected status {response.status_code}: {response.get_json() if response.is_json else response.data}"
    
    def test_mark_kiv_error_path_not_found(self, auth_client):
        """Test mark_kiv error handler with non-existent todo.
        
        KEY: This TRIGGERS the error handler. Any syntax error here gets caught!
        """
        response = auth_client.post('/99999/kiv', follow_redirects=False)
        
        # Should handle gracefully (redirect or return error), NOT return 500
        assert response.status_code in [302, 404], \
            f"Got unexpected status {response.status_code}"


class TestResponseValidation:
    """Test that responses have proper structure and types."""
    
    def test_mark_done_error_response_has_status_field(self, auth_client):
        """Verify error responses include 'status' field.
        
        This catches cases where error handlers return malformed responses.
        """
        response = auth_client.post('/99999/done', follow_redirects=False)
        
        if response.is_json:
            data = response.get_json()
            assert 'status' in data, "JSON response missing 'status' field"
            
    def test_mark_kiv_error_response_has_status_field(self, auth_client):
        """Verify kiv error responses include 'status' field."""
        response = auth_client.post('/99999/kiv', follow_redirects=False)
        
        if response.is_json:
            data = response.get_json()
            assert 'status' in data, "JSON response missing 'status' field"
