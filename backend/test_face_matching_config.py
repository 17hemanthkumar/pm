"""
Property-based tests for FaceMatchingConfig class.
Tests configuration loading, validation, and application.
"""

import os
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from face_matching_config import FaceMatchingConfig


# Feature: photo-matching-enhancement, Property 19: Configuration application
# For any valid configuration values (tolerances, preprocessing options),
# the system should apply those configured values in all relevant operations.
# Validates: Requirements 8.2, 8.3
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    learning_tolerance=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    recognition_tolerance=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    adaptive_enabled=st.booleans(),
    min_face_size=st.integers(min_value=1, max_value=1000),
    min_confidence=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    normalize_brightness=st.booleans(),
    target_width=st.integers(min_value=100, max_value=2000),
    target_height=st.integers(min_value=100, max_value=2000),
    primary_strategy=st.sampled_from(['distance', 'landmarks', 'hybrid']),
    enable_fallback=st.booleans(),
    log_level=st.sampled_from(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
    log_match_details=st.booleans()
)
def test_property_configuration_application(
    learning_tolerance, recognition_tolerance, adaptive_enabled,
    min_face_size, min_confidence, normalize_brightness,
    target_width, target_height, primary_strategy, enable_fallback,
    log_level, log_match_details
):
    """
    Property: For any valid configuration values, the system should apply
    those configured values correctly.
    """
    # Set environment variables with the generated values
    env_vars = {
        'FACE_LEARNING_TOLERANCE': str(learning_tolerance),
        'FACE_RECOGNITION_TOLERANCE': str(recognition_tolerance),
        'FACE_ADAPTIVE_TOLERANCE_ENABLED': str(adaptive_enabled),
        'FACE_MIN_SIZE': str(min_face_size),
        'FACE_MIN_CONFIDENCE': str(min_confidence),
        'FACE_NORMALIZE_BRIGHTNESS': str(normalize_brightness),
        'FACE_TARGET_IMAGE_SIZE': f"{target_width},{target_height}",
        'FACE_PRIMARY_STRATEGY': primary_strategy,
        'FACE_ENABLE_FALLBACK': str(enable_fallback),
        'FACE_LOG_LEVEL': log_level,
        'FACE_LOG_MATCH_DETAILS': str(log_match_details)
    }
    
    # Store original environment
    original_env = {}
    for key in env_vars:
        original_env[key] = os.environ.get(key)
    
    try:
        # Set environment variables
        for key, value in env_vars.items():
            os.environ[key] = value
        
        # Create configuration
        config = FaceMatchingConfig()
        
        # Verify all values are applied correctly
        assert config.learning_tolerance == learning_tolerance, \
            f"Expected learning_tolerance {learning_tolerance}, got {config.learning_tolerance}"
        
        assert config.recognition_tolerance == recognition_tolerance, \
            f"Expected recognition_tolerance {recognition_tolerance}, got {config.recognition_tolerance}"
        
        assert config.adaptive_tolerance_enabled == adaptive_enabled, \
            f"Expected adaptive_tolerance_enabled {adaptive_enabled}, got {config.adaptive_tolerance_enabled}"
        
        assert config.min_face_size == min_face_size, \
            f"Expected min_face_size {min_face_size}, got {config.min_face_size}"
        
        assert config.min_confidence == min_confidence, \
            f"Expected min_confidence {min_confidence}, got {config.min_confidence}"
        
        assert config.normalize_brightness == normalize_brightness, \
            f"Expected normalize_brightness {normalize_brightness}, got {config.normalize_brightness}"
        
        assert config.target_image_size == (target_width, target_height), \
            f"Expected target_image_size ({target_width}, {target_height}), got {config.target_image_size}"
        
        assert config.primary_strategy == primary_strategy, \
            f"Expected primary_strategy '{primary_strategy}', got '{config.primary_strategy}'"
        
        assert config.enable_fallback == enable_fallback, \
            f"Expected enable_fallback {enable_fallback}, got {config.enable_fallback}"
        
        assert config.log_level == log_level.upper(), \
            f"Expected log_level '{log_level.upper()}', got '{config.log_level}'"
        
        assert config.log_match_details == log_match_details, \
            f"Expected log_match_details {log_match_details}, got {config.log_match_details}"
    
    finally:
        # Restore original environment
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


# Feature: photo-matching-enhancement, Property 20: Configuration defaults
# For any invalid or missing configuration value, the system should use
# a sensible default value and log a warning.
# Validates: Requirements 8.5
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    invalid_learning_tolerance=st.one_of(
        st.just("invalid"),
        st.just("not_a_number"),
        st.floats(min_value=-10.0, max_value=-0.1),
        st.floats(min_value=1.1, max_value=10.0)
    ),
    invalid_min_face_size=st.one_of(
        st.just("invalid"),
        st.just("not_an_int"),
        st.integers(max_value=0)
    ),
    invalid_bool=st.sampled_from(["maybe", "unknown", "2", "-1", "yes_no"]),
    invalid_strategy=st.text(min_size=1, max_size=20).filter(
        lambda x: x not in ['distance', 'landmarks', 'hybrid'] and '\x00' not in x
    ),
    invalid_log_level=st.text(min_size=1, max_size=20).filter(
        lambda x: x.upper() not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] and '\x00' not in x
    ),
    invalid_tuple=st.sampled_from(["invalid", "100", "100,200,300", "abc,def"])
)
def test_property_configuration_defaults(
    invalid_learning_tolerance, invalid_min_face_size, invalid_bool,
    invalid_strategy, invalid_log_level, invalid_tuple
):
    """
    Property: For any invalid or missing configuration value, the system
    should use sensible defaults and handle errors gracefully.
    """
    # Store original environment
    env_keys = [
        'FACE_LEARNING_TOLERANCE',
        'FACE_MIN_SIZE',
        'FACE_ADAPTIVE_TOLERANCE_ENABLED',
        'FACE_PRIMARY_STRATEGY',
        'FACE_LOG_LEVEL',
        'FACE_TARGET_IMAGE_SIZE'
    ]
    original_env = {key: os.environ.get(key) for key in env_keys}
    
    try:
        # Set invalid environment variables
        os.environ['FACE_LEARNING_TOLERANCE'] = str(invalid_learning_tolerance)
        os.environ['FACE_MIN_SIZE'] = str(invalid_min_face_size)
        os.environ['FACE_ADAPTIVE_TOLERANCE_ENABLED'] = invalid_bool
        os.environ['FACE_PRIMARY_STRATEGY'] = invalid_strategy
        os.environ['FACE_LOG_LEVEL'] = invalid_log_level
        os.environ['FACE_TARGET_IMAGE_SIZE'] = invalid_tuple
        
        # Create configuration - should not raise exceptions
        config = FaceMatchingConfig()
        
        # Verify defaults are used for invalid values
        # learning_tolerance should be default 0.45 or clamped to valid range
        assert 0.0 <= config.learning_tolerance <= 1.0, \
            f"learning_tolerance {config.learning_tolerance} is out of valid range"
        
        # min_face_size should be at least 1
        assert config.min_face_size >= 1, \
            f"min_face_size {config.min_face_size} should be at least 1"
        
        # adaptive_tolerance_enabled should be a boolean (default True)
        assert isinstance(config.adaptive_tolerance_enabled, bool), \
            f"adaptive_tolerance_enabled should be bool, got {type(config.adaptive_tolerance_enabled)}"
        
        # primary_strategy should be one of the valid options (default 'distance')
        assert config.primary_strategy in ['distance', 'landmarks', 'hybrid'], \
            f"primary_strategy '{config.primary_strategy}' is not valid"
        
        # log_level should be one of the valid options (default 'INFO')
        assert config.log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], \
            f"log_level '{config.log_level}' is not valid"
        
        # target_image_size should be a valid tuple with positive dimensions
        assert isinstance(config.target_image_size, tuple), \
            f"target_image_size should be tuple, got {type(config.target_image_size)}"
        assert len(config.target_image_size) == 2, \
            f"target_image_size should have 2 elements, got {len(config.target_image_size)}"
        assert config.target_image_size[0] >= 1 and config.target_image_size[1] >= 1, \
            f"target_image_size {config.target_image_size} should have positive dimensions"
    
    finally:
        # Restore original environment
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


# Test that missing configuration values use defaults
def test_missing_configuration_uses_defaults():
    """
    Test that when no environment variables are set, sensible defaults are used.
    """
    # Store original environment
    env_keys = [
        'FACE_LEARNING_TOLERANCE',
        'FACE_RECOGNITION_TOLERANCE',
        'FACE_ADAPTIVE_TOLERANCE_ENABLED',
        'FACE_MIN_SIZE',
        'FACE_MIN_CONFIDENCE',
        'FACE_NORMALIZE_BRIGHTNESS',
        'FACE_TARGET_IMAGE_SIZE',
        'FACE_PRIMARY_STRATEGY',
        'FACE_ENABLE_FALLBACK',
        'FACE_LOG_LEVEL',
        'FACE_LOG_MATCH_DETAILS'
    ]
    original_env = {key: os.environ.get(key) for key in env_keys}
    
    try:
        # Clear all environment variables
        for key in env_keys:
            os.environ.pop(key, None)
        
        # Create configuration
        config = FaceMatchingConfig()
        
        # Verify all defaults are as expected
        assert config.learning_tolerance == 0.45
        assert config.recognition_tolerance == 0.54
        assert config.adaptive_tolerance_enabled == True
        assert config.min_face_size == 80
        assert config.min_confidence == 0.7
        assert config.normalize_brightness == True
        assert config.target_image_size == (800, 800)
        assert config.primary_strategy == 'distance'
        assert config.enable_fallback == True
        assert config.log_level == 'INFO'
        assert config.log_match_details == True
    
    finally:
        # Restore original environment
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
