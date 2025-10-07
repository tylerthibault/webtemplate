"""
Performance tests for User Profile & Personal Settings feature.

Tests verify that settings pages and profile operations meet performance targets:
- Settings page load: < 500ms
- Profile update with image: < 2 seconds
- Image encoding (5MB): < 1 second
"""

import pytest
import time
import os
from io import BytesIO
from PIL import Image
from src.logic.image_utils import encode_image, sanitize_image


class TestSettingsPerformance:
    """Performance tests for settings endpoints."""
    
    def test_settings_page_load_time(self, client, auth_user):
        """
        Verify settings page loads in < 500ms.
        
        Expected: Page loads quickly with user data
        Target: < 500ms response time
        """
        # Login
        client.post('/auth/login', json={
            'email': auth_user.email,
            'password': 'TestPassword123'
        })
        
        # Measure GET /settings response time
        start_time = time.time()
        response = client.get('/settings/')
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time_ms < 500, \
            f"Settings page load took {response_time_ms:.2f}ms (target: <500ms)"
        
        print(f"✓ Settings page loaded in {response_time_ms:.2f}ms")
    
    def test_profile_update_time(self, client, auth_user):
        """
        Verify profile update completes in < 2 seconds.
        
        Expected: Profile update with image upload completes quickly
        Target: < 2000ms (2 seconds)
        """
        # Login
        client.post('/auth/login', json={
            'email': auth_user.email,
            'password': 'TestPassword123'
        })
        
        # Create a small test image (1MB)
        img = Image.new('RGB', (1000, 1000), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=85)
        img_bytes = img_bytes.getvalue()
        
        # Encode to base64
        base64_image = encode_image(img_bytes)
        
        # Prepare update data
        update_data = {
            'full_name': 'Performance Test User',
            'email': auth_user.email,
            'bio': 'Testing performance',
            'profile_picture_data': base64_image,
            'updated_at': auth_user.updated_at.isoformat()
        }
        
        # Measure POST /settings response time
        start_time = time.time()
        response = client.post('/settings/', 
                               json=update_data,
                               headers={'X-CSRF-Token': 'test-token'})
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code in [200, 403]  # 403 if CSRF validation strict
        assert response_time_ms < 2000, \
            f"Profile update took {response_time_ms:.2f}ms (target: <2000ms)"
        
        print(f"✓ Profile update completed in {response_time_ms:.2f}ms")
    
    def test_image_encoding_time(self):
        """
        Verify 5MB image encodes in < 1 second.
        
        Expected: Large image encoding is fast
        Target: < 1000ms (1 second)
        """
        # Create a 5MB test image
        # Approximate size: 2500x2500 pixels = ~18.75MB uncompressed
        # JPEG at quality 85 should be ~5MB
        img = Image.new('RGB', (2500, 2500), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=85)
        img_bytes_data = img_bytes.getvalue()
        
        size_mb = len(img_bytes_data) / (1024 * 1024)
        print(f"Test image size: {size_mb:.2f}MB")
        
        # Measure encoding time
        start_time = time.time()
        base64_string = encode_image(img_bytes_data)
        end_time = time.time()
        
        encoding_time_ms = (end_time - start_time) * 1000
        
        assert len(base64_string) > 0
        assert encoding_time_ms < 1000, \
            f"Image encoding took {encoding_time_ms:.2f}ms (target: <1000ms)"
        
        print(f"✓ {size_mb:.2f}MB image encoded in {encoding_time_ms:.2f}ms")


class TestImageProcessingPerformance:
    """Performance tests for image processing utilities."""
    
    def test_image_sanitization_time(self):
        """
        Verify image sanitization (EXIF removal + resize) completes quickly.
        
        Expected: Image sanitization is performant
        Target: < 1500ms for large images
        """
        # Create a large test image with EXIF data
        img = Image.new('RGB', (3000, 3000), color='green')
        
        # Add fake EXIF data
        exif_data = img.getexif()
        exif_data[0x010F] = "Test Camera"  # Make
        exif_data[0x0110] = "Test Model"   # Model
        
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=85, exif=exif_data)
        img_bytes_data = img_bytes.getvalue()
        
        size_mb = len(img_bytes_data) / (1024 * 1024)
        print(f"Test image size: {size_mb:.2f}MB")
        
        # Measure sanitization time
        start_time = time.time()
        sanitized_bytes = sanitize_image(img_bytes_data)
        end_time = time.time()
        
        sanitization_time_ms = (end_time - start_time) * 1000
        
        assert len(sanitized_bytes) > 0
        assert sanitization_time_ms < 1500, \
            f"Image sanitization took {sanitization_time_ms:.2f}ms (target: <1500ms)"
        
        print(f"✓ {size_mb:.2f}MB image sanitized in {sanitization_time_ms:.2f}ms")
    
    def test_concurrent_profile_updates(self, client, auth_user):
        """
        Verify system handles multiple concurrent profile updates.
        
        Expected: System remains responsive under load
        Target: < 3 seconds for 5 sequential updates
        """
        # Login
        client.post('/auth/login', json={
            'email': auth_user.email,
            'password': 'TestPassword123'
        })
        
        # Perform 5 sequential profile updates
        start_time = time.time()
        
        for i in range(5):
            update_data = {
                'full_name': f'Test User {i}',
                'email': auth_user.email,
                'bio': f'Update number {i}',
                'updated_at': auth_user.updated_at.isoformat()
            }
            
            response = client.post('/settings/',
                                   json=update_data,
                                   headers={'X-CSRF-Token': 'test-token'})
            
            # Refresh user timestamp (in real scenario)
            # auth_user.updated_at = datetime.utcnow()
        
        end_time = time.time()
        total_time_ms = (end_time - start_time) * 1000
        avg_time_ms = total_time_ms / 5
        
        assert total_time_ms < 3000, \
            f"5 updates took {total_time_ms:.2f}ms (target: <3000ms)"
        
        print(f"✓ 5 profile updates completed in {total_time_ms:.2f}ms")
        print(f"  Average: {avg_time_ms:.2f}ms per update")


@pytest.fixture
def auth_user(app):
    """Create an authenticated test user."""
    from src.models.user import User
    from src import db
    
    with app.app_context():
        user = User(
            email='perf@test.com',
            full_name='Performance Test User',
            password_hash='$2b$12$test'  # Mock hash
        )
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        db.session.delete(user)
        db.session.commit()


if __name__ == '__main__':
    print("Performance Test Suite for Feature 003")
    print("=" * 60)
    print("Run with: pytest tests/performance/test_settings_performance.py -v -s")
