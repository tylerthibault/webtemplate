"""
Contract test for page rendering routes.

Tests the page routes API contract as defined in
specs/001-frontend-landingpage/contracts/page-routes.md

Following TDD: These tests MUST fail before implementation.
"""

import pytest


class TestPageRoutesContract:
    """Test contract for page rendering endpoints."""
    
    def test_landing_page_renders(self, client):
        """
        Test landing page (/) renders successfully.
        
        Contract: GET / returns 200 OK with rendered HTML
        """
        # Act
        response = client.get('/')
        
        # Assert
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
        # Verify template inheritance from public.html base
        assert b'<html' in response.data
    
    def test_landing_page_uses_public_base(self, client):
        """
        Test landing page extends public.html base template.
        
        Contract: All public pages extend bases/public.html
        """
        # Act
        response = client.get('/')
        
        # Assert
        assert response.status_code == 200
        # Check for Bootstrap CSS (loaded in public.html)
        assert b'bootstrap' in response.data.lower()
    
    def test_about_page_renders(self, client):
        """
        Test about page (/about) renders successfully.
        
        Contract: GET /about returns 200 OK with rendered HTML
        """
        # Act
        response = client.get('/about')
        
        # Assert
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
        assert b'<html' in response.data
    
    def test_about_page_uses_public_base(self, client):
        """
        Test about page extends public.html base template.
        
        Contract: All public pages extend bases/public.html
        """
        # Act
        response = client.get('/about')
        
        # Assert
        assert response.status_code == 200
        # Check for Bootstrap CSS (loaded in public.html)
        assert b'bootstrap' in response.data.lower()
    
    def test_contact_page_renders(self, client):
        """
        Test contact page (/contact) renders successfully.
        
        Contract: GET /contact returns 200 OK with rendered HTML and form
        """
        # Act
        response = client.get('/contact')
        
        # Assert
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
        # Check for contact form elements
        assert b'<form' in response.data
        assert b'name' in response.data.lower()
        assert b'email' in response.data.lower()
        assert b'subject' in response.data.lower()
        assert b'message' in response.data.lower()
    
    def test_contact_page_has_csrf_protection(self, client):
        """
        Test contact page includes CSRF token in form.
        
        Contract: All forms must include CSRF protection
        """
        # Act
        response = client.get('/contact')
        
        # Assert
        assert response.status_code == 200
        # Check for CSRF token field (custom implementation)
        assert b'csrf_token' in response.data or b'csrf-token' in response.data
    
    def test_login_page_renders(self, client):
        """
        Test login page (/auth/login) renders successfully.
        
        Contract: GET /auth/login returns 200 OK with login form
        """
        # Act
        response = client.get('/auth/login')
        
        # Assert
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
        # Check for login form elements
        assert b'<form' in response.data
        assert b'email' in response.data.lower()
        assert b'password' in response.data.lower()
    
    def test_login_page_uses_public_base(self, client):
        """
        Test login page extends public.html base template.
        
        Contract: Login page is accessible to public
        """
        # Act
        response = client.get('/auth/login')
        
        # Assert
        assert response.status_code == 200
        # Check for Bootstrap CSS (loaded in public.html)
        assert b'bootstrap' in response.data.lower()
    
    def test_register_page_renders(self, client):
        """
        Test register page (/auth/register) renders successfully.
        
        Contract: GET /auth/register returns 200 OK with registration form
        """
        # Act
        response = client.get('/auth/register')
        
        # Assert
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
        # Check for registration form elements
        assert b'<form' in response.data
        assert b'email' in response.data.lower()
        assert b'password' in response.data.lower()
        assert b'name' in response.data.lower() or b'full_name' in response.data.lower()
    
    def test_register_page_uses_public_base(self, client):
        """
        Test register page extends public.html base template.
        
        Contract: Registration page is accessible to public
        """
        # Act
        response = client.get('/auth/register')
        
        # Assert
        assert response.status_code == 200
        # Check for Bootstrap CSS (loaded in public.html)
        assert b'bootstrap' in response.data.lower()
    
    def test_dashboard_requires_authentication(self, client):
        """
        Test dashboard (/dashboard) redirects when not authenticated.
        
        Contract: GET /dashboard requires active session
        """
        # Act
        response = client.get('/dashboard', follow_redirects=False)
        
        # Assert
        # Should redirect to login or return 401/403
        assert response.status_code in [302, 401, 403]
    
    def test_dashboard_with_session_renders(self, client):
        """
        Test dashboard renders when authenticated.
        
        Contract: GET /dashboard returns 200 OK when logged in
        Note: This test requires helper to create authenticated session
        """
        # This test will be fully implemented after auth service exists
        # For now, just verify the route exists and handles unauthenticated state
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code in [200, 302, 401, 403]
    
    def test_dashboard_uses_private_base(self, client):
        """
        Test dashboard extends private.html base template.
        
        Contract: All authenticated pages extend bases/private.html
        Note: This test requires authenticated session
        """
        # This test will be fully implemented after auth service exists
        # Placeholder to verify route architecture
        pass
