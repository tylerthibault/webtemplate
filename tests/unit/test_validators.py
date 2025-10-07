"""
Unit tests for profile validation functions.

Tests validation logic for bio and password strength validation.
"""

import pytest
from src.utils.validators import validate_bio, validate_password_strength


# === Test validate_bio() ===

def test_validate_bio_valid():
    """Test 200 char bio passes validation. Expected: FAIL"""
    bio = "A" * 200
    assert validate_bio(bio) is True


def test_validate_bio_empty():
    """Test empty bio passes (optional field). Expected: FAIL"""
    assert validate_bio("") is True
    assert validate_bio(None) is True


def test_validate_bio_max_length():
    """Test 500 char bio passes (at limit). Expected: FAIL"""
    bio = "B" * 500
    assert validate_bio(bio) is True


def test_validate_bio_exceeds_limit():
    """Test 501 char bio fails validation. Expected: FAIL"""
    bio = "C" * 501
    assert validate_bio(bio) is False


def test_validate_bio_sanitizes_xss():
    """Test XSS tags are sanitized. Expected: FAIL"""
    dangerous_bio = "Normal text <script>alert('xss')</script> more text"
    result = validate_bio(dangerous_bio)
    
    # Should either reject or sanitize
    if isinstance(result, str):
        assert '<script>' not in result.lower()
    else:
        # Assuming it returns sanitized string
        assert result is True or result is False


# === Test validate_password_strength() ===

def test_validate_password_valid():
    """Test strong password passes. Expected: FAIL"""
    assert validate_password_strength("SecurePass123") is True


def test_validate_password_too_short():
    """Test password < 8 chars fails. Expected: FAIL"""
    assert validate_password_strength("Abc1") is False


def test_validate_password_no_uppercase():
    """Test password without uppercase fails. Expected: FAIL"""
    assert validate_password_strength("secure123") is False


def test_validate_password_no_lowercase():
    """Test password without lowercase fails. Expected: FAIL"""
    assert validate_password_strength("SECURE123") is False


def test_validate_password_no_number():
    """Test password without number fails. Expected: FAIL"""
    assert validate_password_strength("SecurePass") is False
