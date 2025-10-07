"""
Unit tests for image utility functions.

Tests the base64 encoding/decoding, validation, and sanitization
functions in src/logic/image_utils.py.
"""

import pytest
import os
import base64
from PIL import Image
import io
from src.logic.image_utils import (
    encode_image,
    decode_image,
    validate_image,
    sanitize_image
)


# Path to test fixtures
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'fixtures')


# === Test encode_image() ===

def test_encode_image_valid_jpeg():
    """
    Test encoding JPEG image bytes to base64 string.
    
    Expected: FAIL (encode_image not implemented)
    """
    jpeg_path = os.path.join(FIXTURES_DIR, 'test_image.jpg')
    with open(jpeg_path, 'rb') as f:
        image_bytes = f.read()
    
    encoded = encode_image(image_bytes)
    
    # Should return a string
    assert isinstance(encoded, str), "encode_image should return string"
    
    # Should be valid base64 (can decode it back)
    try:
        decoded = base64.b64decode(encoded)
        assert len(decoded) > 0
    except Exception as e:
        pytest.fail(f"encode_image did not produce valid base64: {e}")


def test_encode_image_valid_png():
    """
    Test encoding PNG image bytes to base64 string.
    
    Expected: FAIL (encode_image not implemented)
    """
    png_path = os.path.join(FIXTURES_DIR, 'test_image.png')
    with open(png_path, 'rb') as f:
        image_bytes = f.read()
    
    encoded = encode_image(image_bytes)
    
    assert isinstance(encoded, str)
    assert len(encoded) > 0
    
    # Should be valid base64
    decoded = base64.b64decode(encoded)
    assert len(decoded) == len(image_bytes)


def test_encode_image_roundtrip():
    """
    Test that encode then decode returns original bytes.
    
    Expected: FAIL (functions not implemented)
    """
    jpeg_path = os.path.join(FIXTURES_DIR, 'test_image.jpg')
    with open(jpeg_path, 'rb') as f:
        original_bytes = f.read()
    
    # Encode to base64
    encoded = encode_image(original_bytes)
    
    # Decode back to bytes
    decoded_bytes = decode_image(encoded)
    
    # Should match original
    assert decoded_bytes == original_bytes, \
        "Roundtrip encode→decode should return original bytes"


# === Test decode_image() ===

def test_decode_image_valid_base64():
    """
    Test decoding valid base64 string to bytes.
    
    Expected: FAIL (decode_image not implemented)
    """
    # Create base64 string from known bytes
    original_bytes = b"Test image data"
    base64_string = base64.b64encode(original_bytes).decode('utf-8')
    
    decoded = decode_image(base64_string)
    
    assert isinstance(decoded, bytes), "decode_image should return bytes"
    assert decoded == original_bytes


def test_decode_image_invalid_base64_raises():
    """
    Test that invalid base64 string raises ValueError.
    
    Expected: FAIL (decode_image not implemented)
    """
    invalid_base64 = "This is not valid base64!@#$%"
    
    with pytest.raises(ValueError):
        decode_image(invalid_base64)


# === Test validate_image() ===

def test_validate_image_valid_jpeg():
    """
    Test validation returns (True, 'image/jpeg') for valid JPEG.
    
    Expected: FAIL (validate_image not implemented)
    """
    jpeg_path = os.path.join(FIXTURES_DIR, 'test_image.jpg')
    with open(jpeg_path, 'rb') as f:
        image_bytes = f.read()
    
    is_valid, mime_type = validate_image(image_bytes)
    
    assert is_valid is True, "Valid JPEG should be accepted"
    assert mime_type == 'image/jpeg', \
        f"Expected 'image/jpeg', got '{mime_type}'"


def test_validate_image_valid_png():
    """
    Test validation returns (True, 'image/png') for valid PNG.
    
    Expected: FAIL (validate_image not implemented)
    """
    png_path = os.path.join(FIXTURES_DIR, 'test_image.png')
    with open(png_path, 'rb') as f:
        image_bytes = f.read()
    
    is_valid, mime_type = validate_image(image_bytes)
    
    assert is_valid is True, "Valid PNG should be accepted"
    assert mime_type == 'image/png', \
        f"Expected 'image/png', got '{mime_type}'"


def test_validate_image_non_image_returns_false():
    """
    Test that text file returns (False, error message).
    
    Expected: FAIL (validate_image not implemented)
    """
    txt_path = os.path.join(FIXTURES_DIR, 'test.txt')
    with open(txt_path, 'rb') as f:
        text_bytes = f.read()
    
    is_valid, error_msg = validate_image(text_bytes)
    
    assert is_valid is False, "Text file should not be valid image"
    assert isinstance(error_msg, str), "Error message should be string"
    assert len(error_msg) > 0, "Error message should not be empty"


def test_validate_image_oversized_returns_false():
    """
    Test that image > 5MB returns (False, error).
    
    Expected: FAIL (validate_image not implemented)
    """
    # Create large image (> 5MB)
    large_img = Image.new('RGB', (5000, 5000), color='blue')
    buf = io.BytesIO()
    large_img.save(buf, format='PNG')
    large_bytes = buf.getvalue()
    
    # Should be > 5MB
    assert len(large_bytes) > 5 * 1024 * 1024, "Test image should be > 5MB"
    
    is_valid, error_msg = validate_image(large_bytes)
    
    assert is_valid is False, "Oversized image should be rejected"
    assert 'size' in error_msg.lower() or '5mb' in error_msg.lower(), \
        "Error should mention size limit"


def test_validate_image_malformed_returns_false():
    """
    Test that corrupted image returns (False, error).
    
    Expected: FAIL (validate_image not implemented)
    """
    corrupted_path = os.path.join(FIXTURES_DIR, 'corrupted.jpg')
    with open(corrupted_path, 'rb') as f:
        corrupted_bytes = f.read()
    
    is_valid, error_msg = validate_image(corrupted_bytes)
    
    assert is_valid is False, "Corrupted image should be rejected"
    assert isinstance(error_msg, str)


# === Test sanitize_image() ===

def test_sanitize_image_strips_exif():
    """
    Test that EXIF metadata is removed from image.
    
    Expected: FAIL (sanitize_image not implemented)
    """
    # Create image with EXIF data
    img = Image.new('RGB', (100, 100), color='green')
    
    # Add EXIF data
    exif_data = img.getexif()
    exif_data[0x010F] = "Test Camera"  # Manufacturer
    exif_data[0x0132] = "2025:10:06 12:00:00"  # DateTime
    
    # Save with EXIF
    buf = io.BytesIO()
    img.save(buf, format='JPEG', exif=exif_data)
    original_bytes = buf.getvalue()
    
    # Sanitize
    sanitized_bytes = sanitize_image(original_bytes)
    
    # Check EXIF removed
    sanitized_img = Image.open(io.BytesIO(sanitized_bytes))
    sanitized_exif = sanitized_img.getexif()
    
    assert len(sanitized_exif) == 0 or 0x010F not in sanitized_exif, \
        "EXIF data should be removed"


def test_sanitize_image_preserves_content():
    """
    Test that image content is preserved after sanitization.
    
    Expected: FAIL (sanitize_image not implemented)
    """
    jpeg_path = os.path.join(FIXTURES_DIR, 'test_image.jpg')
    with open(jpeg_path, 'rb') as f:
        original_bytes = f.read()
    
    # Get original image dimensions
    original_img = Image.open(io.BytesIO(original_bytes))
    original_size = original_img.size
    
    # Sanitize
    sanitized_bytes = sanitize_image(original_bytes)
    
    # Check dimensions preserved (within reason, may be resized)
    sanitized_img = Image.open(io.BytesIO(sanitized_bytes))
    sanitized_size = sanitized_img.size
    
    # Sizes should match or be proportionally resized
    assert sanitized_size[0] > 0 and sanitized_size[1] > 0, \
        "Sanitized image should have valid dimensions"
    
    # If not resized, should match exactly
    # If resized, should be proportional
    if sanitized_size != original_size:
        # Allow for reasonable resizing
        aspect_ratio_original = original_size[0] / original_size[1]
        aspect_ratio_sanitized = sanitized_size[0] / sanitized_size[1]
        
        assert abs(aspect_ratio_original - aspect_ratio_sanitized) < 0.1, \
            "Sanitization should preserve aspect ratio"
