"""
Unit tests for profile validation functions.

Tests validation logic for bio and password strength validation.
"""

import pytest
from src.utils.validators import validate_bio, validate_password_strength


# === Test validate_bio() ===

def test_validate_bio_valid():
    """Test 200 char bio passes validation."""
    bio = "A" * 200
    is_valid, result = validate_bio(bio)
    assert is_valid is True
    assert result == bio


def test_validate_bio_empty():
    """Test empty bio passes (optional field)."""
    is_valid, result = validate_bio("")
    assert is_valid is True
    assert result == ""


def test_validate_bio_max_length():
    """Test 500 char bio passes (at limit)."""
    bio = "B" * 500
    is_valid, result = validate_bio(bio)
    assert is_valid is True
    assert result == bio


def test_validate_bio_exceeds_limit():
    """Test 501 char bio fails validation."""
    bio = "C" * 501
    is_valid, error_msg = validate_bio(bio)
    assert is_valid is False
    assert "500 characters" in error_msg


def test_validate_bio_sanitizes_xss():
    """Test XSS tags are sanitized."""
    dangerous_bio = "Normal text <script>alert('xss')</script> more text"
    is_valid, sanitized = validate_bio(dangerous_bio)
    
    assert is_valid is True
    assert '<script>' not in sanitized.lower()
    assert 'normal text' in sanitized.lower()
    assert 'more text' in sanitized.lower()


# === Test validate_password_strength() ===

def test_validate_password_valid():
    """Test strong password passes."""
    is_valid, msg = validate_password_strength("SecurePass123")
    assert is_valid is True
    assert msg == ""


def test_validate_password_too_short():
    """Test password < 8 chars fails."""
    is_valid, error_msg = validate_password_strength("Abc1")
    assert is_valid is False
    assert "8 characters" in error_msg


def test_validate_password_no_uppercase():
    """Test password without uppercase fails."""
    is_valid, error_msg = validate_password_strength("secure123")
    assert is_valid is False
    assert "uppercase" in error_msg.lower()


def test_validate_password_no_lowercase():
    """Test password without lowercase fails."""
    is_valid, error_msg = validate_password_strength("SECURE123")
    assert is_valid is False
    assert "lowercase" in error_msg.lower()


def test_validate_password_no_number():
    """Test password without number fails."""
    is_valid, error_msg = validate_password_strength("SecurePass")
    assert is_valid is False
    assert "digit" in error_msg.lower() or "number" in error_msg.lower()
