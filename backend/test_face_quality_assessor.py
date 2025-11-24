"""
Unit tests for FaceQualityAssessor class.
Tests quality metrics calculation with various conditions.
"""

import pytest
import numpy as np
from face_quality_assessor import FaceQualityAssessor
from face_matching_config import FaceMatchingConfig


class TestFaceQualityAssessor:
    """Unit tests for face quality assessment"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = FaceMatchingConfig()
        self.assessor = FaceQualityAssessor(self.config)
    
    def test_face_size_calculation_small_face(self):
        """Test face size calculation with a small face"""
        # Create a small test image (100x100)
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Small face location: 50x50 pixels
        face_location = (25, 75, 75, 25)  # (top, right, bottom, left)
        
        metrics = self.assessor.assess_encoding_quality(image, face_location)
        
        assert metrics['face_size'] == (50, 50)
        assert metrics['face_area'] == 2500
        assert not metrics['is_acceptable'], "Small face should not be acceptable"
    
    def test_face_size_calculation_large_face(self):
        """Test face size calculation with a large face"""
        # Create a larger test image (400x400)
        image = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)
        
        # Large face location: 200x200 pixels
        face_location = (100, 300, 300, 100)
        
        metrics = self.assessor.assess_encoding_quality(image, face_location)
        
        assert metrics['face_size'] == (200, 200)
        assert metrics['face_area'] == 40000
    
    def test_face_size_calculation_various_locations(self):
        """Test face size calculation with various face locations"""
        image = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)
        
        test_cases = [
            ((0, 100, 100, 0), (100, 100)),      # Top-left corner
            ((400, 500, 500, 400), (100, 100)),  # Bottom-right corner
            ((150, 350, 350, 150), (200, 200)),  # Center
            ((50, 200, 150, 50), (150, 100)),    # Rectangular face
        ]
        
        for face_location, expected_size in test_cases:
            metrics = self.assessor.assess_encoding_quality(image, face_location)
            assert metrics['face_size'] == expected_size
    
    def test_brightness_scoring_dark_image(self):
        """Test brightness scoring with a dark image"""
        # Create a dark image (low brightness)
        image = np.full((200, 200, 3), 30, dtype=np.uint8)  # Very dark
        face_location = (50, 150, 150, 50)
        
        metrics = self.assessor.assess_encoding_quality(image, face_location)
        
        # Dark image should have lower brightness score
        assert 0.0 <= metrics['brightness_score'] <= 0.5, \
            f"Dark image brightness score {metrics['brightness_score']} should be low"
    
    def test_brightness_scoring_bright_image(self):
        """Test brightness scoring with a bright image"""
        # Create a bright image (high brightness)
        image = np.full((200, 200, 3), 220, dtype=np.uint8)  # Very bright
        face_location = (50, 150, 150, 50)
        
        metrics = self.assessor.assess_encoding_quality(image, face_location)
        
        # Very bright image should have lower brightness score
        assert 0.0 <= metrics['brightness_score'] <= 0.5, \
            f"Bright image brightness score {metrics['brightness_score']} should be low"
    
    def test_brightness_scoring_optimal_lighting(self):
        """Test brightness scoring with optimal lighting"""
        # Create an image with optimal brightness (mid-range ~127)
        image = np.full((200, 200, 3), 127, dtype=np.uint8)
        face_location = (50, 150, 150, 50)
        
        metrics = self.assessor.assess_encoding_quality(image, face_location)
        
        # Optimal lighting should have high brightness score
        assert metrics['brightness_score'] >= 0.8, \
            f"Optimal lighting brightness score {metrics['brightness_score']} should be high"
    
    def test_blur_detection_sharp_image(self):
        """Test blur detection with a sharp image"""
        # Create a sharp image with high-frequency patterns
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        # Add checkerboard pattern (sharp edges)
        for i in range(0, 200, 10):
            for j in range(0, 200, 10):
                if (i // 10 + j // 10) % 2 == 0:
                    image[i:i+10, j:j+10] = 255
        
        face_location = (50, 150, 150, 50)
        
        metrics = self.assessor.assess_encoding_quality(image, face_location)
        
        # Sharp image should have higher blur score
        assert metrics['blur_score'] > 0.3, \
            f"Sharp image blur score {metrics['blur_score']} should be higher"
    
    def test_blur_detection_blurry_image(self):
        """Test blur detection with a blurry image"""
        # Create a blurry image (uniform color, no edges)
        image = np.full((200, 200, 3), 127, dtype=np.uint8)
        face_location = (50, 150, 150, 50)
        
        metrics = self.assessor.assess_encoding_quality(image, face_location)
        
        # Blurry image should have lower blur score
        assert metrics['blur_score'] < 0.5, \
            f"Blurry image blur score {metrics['blur_score']} should be lower"
    
    def test_confidence_score_computation_high_quality(self):
        """Test confidence score with high quality inputs"""
        # Create a high-quality image: large, sharp, well-lit
        image = np.zeros((400, 400, 3), dtype=np.uint8)
        # Add sharp pattern
        for i in range(0, 400, 20):
            for j in range(0, 400, 20):
                if (i // 20 + j // 20) % 2 == 0:
                    image[i:i+20, j:j+20] = 127  # Mid-brightness
        
        # Large face
        face_location = (100, 300, 300, 100)
        
        metrics = self.assessor.assess_encoding_quality(image, face_location)
        
        # High quality should result in high confidence
        assert metrics['confidence'] >= 0.5, \
            f"High quality confidence {metrics['confidence']} should be high"
        assert metrics['is_acceptable'], "High quality should be acceptable"
    
    def test_confidence_score_computation_low_quality(self):
        """Test confidence score with low quality inputs"""
        # Create a low-quality image: small, blurry, poor lighting
        image = np.full((100, 100, 3), 30, dtype=np.uint8)  # Dark and uniform
        
        # Small face
        face_location = (25, 75, 75, 25)
        
        metrics = self.assessor.assess_encoding_quality(image, face_location)
        
        # Low quality should result in low confidence
        assert metrics['confidence'] < 0.7, \
            f"Low quality confidence {metrics['confidence']} should be low"
    
    def test_confidence_score_range(self):
        """Test that confidence score is always in valid range"""
        # Test with various random images
        for _ in range(10):
            image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
            face_location = (50, 250, 250, 50)
            
            metrics = self.assessor.assess_encoding_quality(image, face_location)
            
            assert 0.0 <= metrics['confidence'] <= 1.0, \
                f"Confidence {metrics['confidence']} should be in range [0, 1]"
    
    def test_quality_threshold_checking(self):
        """Test that quality threshold checking works correctly"""
        # Test with face below minimum size
        image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        small_face = (50, 120, 120, 50)  # 70x70 pixels (below default 80)
        
        metrics = self.assessor.assess_encoding_quality(image, small_face)
        assert not metrics['is_acceptable'], "Face below min size should not be acceptable"
        
        # Test with face above minimum size
        large_face = (50, 150, 150, 50)  # 100x100 pixels (above default 80)
        metrics = self.assessor.assess_encoding_quality(image, large_face)
        # Acceptability depends on confidence, but size check should pass
        assert metrics['face_size'][0] >= self.config.min_face_size
    
    def test_adaptive_tolerance_high_quality(self):
        """Test adaptive tolerance with high quality encoding"""
        # High quality metrics
        quality_metrics = {
            'face_size': (200, 200),
            'face_area': 40000,
            'brightness_score': 0.9,
            'blur_score': 0.9,
            'confidence': 0.9,
            'is_acceptable': True
        }
        
        base_tolerance = 0.54
        adjusted = self.assessor.compute_adaptive_tolerance(base_tolerance, quality_metrics)
        
        # High quality should result in tolerance close to or slightly higher than base
        assert adjusted >= base_tolerance * 0.9, \
            f"High quality adjusted tolerance {adjusted} should be close to base {base_tolerance}"
        assert adjusted <= 1.0, "Tolerance should not exceed 1.0"
    
    def test_adaptive_tolerance_low_quality(self):
        """Test adaptive tolerance with low quality encoding"""
        # Low quality metrics
        quality_metrics = {
            'face_size': (80, 80),
            'face_area': 6400,
            'brightness_score': 0.3,
            'blur_score': 0.3,
            'confidence': 0.4,
            'is_acceptable': False
        }
        
        base_tolerance = 0.54
        adjusted = self.assessor.compute_adaptive_tolerance(base_tolerance, quality_metrics)
        
        # Low quality should result in stricter (lower) tolerance
        assert adjusted < base_tolerance, \
            f"Low quality adjusted tolerance {adjusted} should be stricter than base {base_tolerance}"
        assert adjusted >= 0.0, "Tolerance should not be negative"
    
    def test_adaptive_tolerance_bounds_checking(self):
        """Test that adaptive tolerance stays within valid range"""
        test_cases = [
            {'confidence': 0.0},  # Minimum confidence
            {'confidence': 1.0},  # Maximum confidence
            {'confidence': 0.5},  # Mid confidence
            {'confidence': 0.7},  # Typical confidence
        ]
        
        base_tolerance = 0.54
        
        for quality_metrics in test_cases:
            adjusted = self.assessor.compute_adaptive_tolerance(base_tolerance, quality_metrics)
            
            assert 0.0 <= adjusted <= 1.0, \
                f"Adjusted tolerance {adjusted} should be in range [0, 1]"
    
    def test_adaptive_tolerance_stricter_for_lower_quality(self):
        """Test that tolerance becomes stricter as quality decreases"""
        base_tolerance = 0.54
        
        # Test with decreasing quality levels
        confidences = [0.9, 0.7, 0.5, 0.3]
        previous_tolerance = 1.0
        
        for confidence in confidences:
            quality_metrics = {'confidence': confidence}
            adjusted = self.assessor.compute_adaptive_tolerance(base_tolerance, quality_metrics)
            
            # Each lower confidence should result in stricter (lower) tolerance
            assert adjusted <= previous_tolerance, \
                f"Tolerance should decrease as quality decreases: {adjusted} > {previous_tolerance}"
            previous_tolerance = adjusted
    
    def test_should_use_adaptive_threshold_high_quality(self):
        """Test adaptive threshold decision with high quality"""
        quality_metrics = {
            'confidence': 0.9,
            'is_acceptable': True
        }
        
        should_adapt = self.assessor.should_use_adaptive_threshold(quality_metrics)
        
        # High quality (>= 0.8) should not require adaptive threshold
        assert not should_adapt, "High quality should not require adaptive threshold"
    
    def test_should_use_adaptive_threshold_low_quality(self):
        """Test adaptive threshold decision with low quality"""
        quality_metrics = {
            'confidence': 0.6,
            'is_acceptable': False
        }
        
        should_adapt = self.assessor.should_use_adaptive_threshold(quality_metrics)
        
        # Low quality (< 0.8) should require adaptive threshold
        assert should_adapt, "Low quality should require adaptive threshold"
    
    def test_should_use_adaptive_threshold_boundary(self):
        """Test adaptive threshold decision at boundary"""
        # Test at exactly 0.8 confidence
        quality_metrics = {'confidence': 0.8}
        should_adapt = self.assessor.should_use_adaptive_threshold(quality_metrics)
        assert not should_adapt, "Confidence of 0.8 should not require adaptation"
        
        # Test just below 0.8
        quality_metrics = {'confidence': 0.79}
        should_adapt = self.assessor.should_use_adaptive_threshold(quality_metrics)
        assert should_adapt, "Confidence below 0.8 should require adaptation"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])



# Property-Based Tests using Hypothesis

from hypothesis import given, strategies as st, settings, HealthCheck


# Feature: photo-matching-enhancement, Property 2: Adaptive tolerance based on quality
# For any facial encoding with quality metrics, the system should apply a tolerance
# threshold that becomes stricter (lower) as quality decreases, and the quality
# metrics should influence the matching decision.
# Validates: Requirements 1.2, 3.4, 3.5
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    base_tolerance=st.floats(min_value=0.1, max_value=0.9, allow_nan=False, allow_infinity=False),
    confidence=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    brightness_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    blur_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    face_area=st.integers(min_value=100, max_value=100000)
)
def test_property_adaptive_tolerance_based_on_quality(
    base_tolerance, confidence, brightness_score, blur_score, face_area
):
    """
    Property: For any facial encoding with quality metrics, the system should
    apply a tolerance threshold that becomes stricter as quality decreases.
    """
    config = FaceMatchingConfig()
    assessor = FaceQualityAssessor(config)
    
    # Create quality metrics
    quality_metrics = {
        'face_size': (int(np.sqrt(face_area)), int(np.sqrt(face_area))),
        'face_area': face_area,
        'brightness_score': brightness_score,
        'blur_score': blur_score,
        'confidence': confidence,
        'is_acceptable': confidence >= config.min_confidence
    }
    
    # Compute adaptive tolerance
    adjusted_tolerance = assessor.compute_adaptive_tolerance(base_tolerance, quality_metrics)
    
    # Property 1: Adjusted tolerance should always be in valid range [0, 1]
    assert 0.0 <= adjusted_tolerance <= 1.0, \
        f"Adjusted tolerance {adjusted_tolerance} must be in range [0, 1]"
    
    # Property 2: Lower confidence should result in stricter (lower or equal) tolerance
    # Test with a slightly higher confidence
    if confidence < 1.0:
        higher_confidence_metrics = quality_metrics.copy()
        higher_confidence_metrics['confidence'] = min(1.0, confidence + 0.1)
        
        higher_adjusted = assessor.compute_adaptive_tolerance(base_tolerance, higher_confidence_metrics)
        
        assert adjusted_tolerance <= higher_adjusted, \
            f"Lower confidence ({confidence}) should result in stricter tolerance " \
            f"({adjusted_tolerance}) than higher confidence ({higher_confidence_metrics['confidence']}) " \
            f"tolerance ({higher_adjusted})"
    
    # Property 3: The adjustment should be based on confidence
    # confidence = 1.0 should give adjustment_factor = 1.0 (no change or slight increase)
    # confidence = 0.0 should give adjustment_factor = 0.5 (50% stricter)
    expected_factor = 0.5 + 0.5 * confidence
    expected_tolerance = base_tolerance * expected_factor
    expected_tolerance = max(0.0, min(1.0, expected_tolerance))
    
    # Allow small floating point differences
    assert abs(adjusted_tolerance - expected_tolerance) < 1e-6, \
        f"Adjusted tolerance {adjusted_tolerance} should match expected {expected_tolerance}"
    
    # Property 4: should_use_adaptive_threshold should be consistent with confidence
    should_adapt = assessor.should_use_adaptive_threshold(quality_metrics)
    
    if confidence >= 0.8:
        assert not should_adapt, \
            f"High confidence ({confidence}) should not require adaptive threshold"
    else:
        assert should_adapt, \
            f"Low confidence ({confidence}) should require adaptive threshold"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])



# Feature: photo-matching-enhancement, Property 4: Low quality rejection
# For any facial encoding with quality metrics below acceptable thresholds,
# the system should return an error requesting a rescan rather than attempting to match.
# Validates: Requirements 1.4
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    # Generate face sizes that might be below threshold
    face_width=st.integers(min_value=10, max_value=200),
    face_height=st.integers(min_value=10, max_value=200),
    brightness_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    blur_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
def test_property_low_quality_rejection(face_width, face_height, brightness_score, blur_score):
    """
    Property: For any facial encoding with quality metrics below acceptable thresholds,
    the system should mark it as not acceptable (is_acceptable = False).
    """
    config = FaceMatchingConfig()
    assessor = FaceQualityAssessor(config)
    
    # Create a test image large enough to contain the face
    image_size = max(face_width + 100, face_height + 100, 300)
    image = np.random.randint(0, 255, (image_size, image_size, 3), dtype=np.uint8)
    
    # Create face location
    top = 50
    left = 50
    bottom = top + face_height
    right = left + face_width
    face_location = (top, right, bottom, left)
    
    # Assess quality
    metrics = assessor.assess_encoding_quality(image, face_location)
    
    # Property 1: is_acceptable should be False if face is too small
    min_dimension = min(face_width, face_height)
    if min_dimension < config.min_face_size:
        assert not metrics['is_acceptable'], \
            f"Face with min dimension {min_dimension} < {config.min_face_size} should not be acceptable"
    
    # Property 2: is_acceptable should be False if confidence is too low
    if metrics['confidence'] < config.min_confidence:
        assert not metrics['is_acceptable'], \
            f"Face with confidence {metrics['confidence']} < {config.min_confidence} should not be acceptable"
    
    # Property 3: is_acceptable should be True only if both conditions are met
    if metrics['is_acceptable']:
        assert min_dimension >= config.min_face_size, \
            f"Acceptable face should have min dimension >= {config.min_face_size}, got {min_dimension}"
        assert metrics['confidence'] >= config.min_confidence, \
            f"Acceptable face should have confidence >= {config.min_confidence}, got {metrics['confidence']}"
    
    # Property 4: All quality scores should be in valid range [0, 1]
    assert 0.0 <= metrics['brightness_score'] <= 1.0, \
        f"Brightness score {metrics['brightness_score']} should be in [0, 1]"
    assert 0.0 <= metrics['blur_score'] <= 1.0, \
        f"Blur score {metrics['blur_score']} should be in [0, 1]"
    assert 0.0 <= metrics['confidence'] <= 1.0, \
        f"Confidence {metrics['confidence']} should be in [0, 1]"
    
    # Property 5: Face size should match the location dimensions
    assert metrics['face_size'] == (face_width, face_height), \
        f"Face size {metrics['face_size']} should match dimensions ({face_width}, {face_height})"
    assert metrics['face_area'] == face_width * face_height, \
        f"Face area {metrics['face_area']} should equal {face_width * face_height}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
