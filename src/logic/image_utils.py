"""
Image utility functions for base64 encoding/decoding and validation.

This module provides utilities for converting images to/from base64 format,
validating image files, and sanitizing images by removing EXIF data.
Used for storing profile pictures in SQLite as TEXT fields.
"""

import base64
import io
from typing import Tuple
from PIL import Image


def encode_image(file_bytes: bytes) -> str:
    """
    Convert image bytes to base64 string for database storage.

    Args:
        file_bytes: Raw image file bytes

    Returns:
        Base64-encoded string (without data URI prefix)

    Example:
        >>> with open('photo.jpg', 'rb') as f:
        ...     encoded = encode_image(f.read())
        >>> encoded[:20]
        '/9j/4AAQSkZJRgABAQAA...'
    """
    return base64.b64encode(file_bytes).decode("utf-8")


def decode_image(base64_string: str) -> bytes:
    """
    Convert base64 string back to image bytes.

    Args:
        base64_string: Base64-encoded image data (without data URI prefix)

    Returns:
        Raw image bytes

    Raises:
        ValueError: If base64_string is invalid or cannot be decoded

    Example:
        >>> encoded = '/9j/4AAQSkZJRgABAQAA...'
        >>> image_bytes = decode_image(encoded)
        >>> len(image_bytes)
        45678
    """
    try:
        return base64.b64decode(base64_string)
    except Exception as e:
        raise ValueError(f"Invalid base64 string: {str(e)}")


def validate_image(file_bytes: bytes) -> Tuple[bool, str]:
    """
    Validate image file using Pillow and return validation result.

    Checks:
    - File is a valid image format (JPEG, PNG, GIF)
    - File size is under 5MB limit
    - Image can be opened by Pillow (magic number validation)
    - Image is not malicious or corrupted

    Args:
        file_bytes: Raw image file bytes to validate

    Returns:
        Tuple of (is_valid, mime_type_or_error_message)
        - If valid: (True, "image/jpeg") or (True, "image/png") or (True, "image/gif")
        - If invalid: (False, "Error: File size exceeds 5MB limit") or similar

    Example:
        >>> with open('photo.jpg', 'rb') as f:
        ...     valid, mime = validate_image(f.read())
        >>> valid
        True
        >>> mime
        'image/jpeg'
    """
    # Check file size (5MB limit)
    MAX_SIZE = 5 * 1024 * 1024  # 5MB in bytes
    if len(file_bytes) > MAX_SIZE:
        return (False, f"File size ({len(file_bytes)} bytes) exceeds 5MB limit")

    try:
        # Open image with Pillow (validates magic number)
        image = Image.open(io.BytesIO(file_bytes))

        # Check format is allowed
        allowed_formats = ["JPEG", "PNG", "GIF"]
        if image.format not in allowed_formats:
            return (False, f"Invalid format: {image.format}. Allowed: JPEG, PNG, GIF")

        # Verify image can be loaded (detect corruption)
        image.verify()

        # Return success with MIME type
        mime_type = f"image/{image.format.lower()}"
        return (True, mime_type)

    except Exception as e:
        return (False, f"Invalid image file: {str(e)}")


def sanitize_image(file_bytes: bytes) -> bytes:
    """
    Strip EXIF metadata and optionally resize image for security.

    Removes potentially sensitive metadata (location, camera info, etc.)
    from images before storing. Optionally resizes large images to
    reduce storage size.

    Args:
        file_bytes: Raw image file bytes

    Returns:
        Sanitized image bytes (EXIF removed, optionally resized)

    Raises:
        ValueError: If image cannot be processed

    Example:
        >>> with open('photo_with_exif.jpg', 'rb') as f:
        ...     sanitized = sanitize_image(f.read())
        >>> # EXIF data now removed from sanitized bytes
    """
    try:
        # Open image
        image = Image.open(io.BytesIO(file_bytes))

        # Get format for saving
        format = image.format
        if format not in ["JPEG", "PNG", "GIF"]:
            raise ValueError(f"Unsupported format: {format}")

        # Remove EXIF data by creating new image with same data
        # (copying pixel data without metadata)
        data = image.getdata()
        sanitized_img = Image.new(image.mode, image.size)
        sanitized_img.putdata(data)

        # Optional: resize if very large (> 2000px on either dimension)
        MAX_DIMENSION = 2000
        if image.width > MAX_DIMENSION or image.height > MAX_DIMENSION:
            # Calculate new size maintaining aspect ratio
            ratio = min(MAX_DIMENSION / image.width, MAX_DIMENSION / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            sanitized_img = sanitized_img.resize(new_size, Image.Resampling.LANCZOS)

        # Save to bytes
        output = io.BytesIO()

        # Save with format-specific options
        if format == "JPEG":
            sanitized_img.save(output, format="JPEG", quality=85, optimize=True)
        elif format == "PNG":
            sanitized_img.save(output, format="PNG", optimize=True)
        else:  # GIF
            sanitized_img.save(output, format="GIF")

        return output.getvalue()

    except Exception as e:
        raise ValueError(f"Failed to sanitize image: {str(e)}")
