"""
Configuration management for face matching system.
Provides configurable parameters for tolerance thresholds, quality assessment,
preprocessing, matching strategies, and logging.
"""

import os
import logging
from typing import Optional, Tuple


class FaceMatchingConfig:
    """
    Configuration class for face matching parameters.
    Loads configuration from environment variables with fallback to sensible defaults.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration with defaults and load from environment variables.
        
        Args:
            config_file: Optional path to YAML configuration file (not yet implemented)
        """
        # Tolerance thresholds
        self.learning_tolerance: float = self._load_float_env(
            'FACE_LEARNING_TOLERANCE', 0.45
        )
        self.recognition_tolerance: float = self._load_float_env(
            'FACE_RECOGNITION_TOLERANCE', 0.54
        )
        self.adaptive_tolerance_enabled: bool = self._load_bool_env(
            'FACE_ADAPTIVE_TOLERANCE_ENABLED', True
        )
        
        # Quality thresholds
        self.min_face_size: int = self._load_int_env(
            'FACE_MIN_SIZE', 80
        )
        self.min_confidence: float = self._load_float_env(
            'FACE_MIN_CONFIDENCE', 0.7
        )
        
        # Preprocessing options
        self.normalize_brightness: bool = self._load_bool_env(
            'FACE_NORMALIZE_BRIGHTNESS', True
        )
        self.target_image_size: Tuple[int, int] = self._load_tuple_env(
            'FACE_TARGET_IMAGE_SIZE', (800, 800)
        )
        
        # Matching strategies
        self.primary_strategy: str = self._load_str_env(
            'FACE_PRIMARY_STRATEGY', 'distance'
        )
        self.enable_fallback: bool = self._load_bool_env(
            'FACE_ENABLE_FALLBACK', True
        )
        
        # Logging
        self.log_level: str = self._load_str_env(
            'FACE_LOG_LEVEL', 'INFO'
        )
        self.log_match_details: bool = self._load_bool_env(
            'FACE_LOG_MATCH_DETAILS', True
        )
        
        # Validate configuration after loading
        self._validate()
        
        # Log configuration if YAML file was requested but not implemented
        if config_file is not None:
            logging.warning(
                f"YAML configuration file '{config_file}' was specified but "
                "YAML loading is not yet implemented. Using environment variables "
                "and defaults."
            )
    
    def _load_float_env(self, key: str, default: float) -> float:
        """Load a float value from environment variable with validation."""
        value_str = os.environ.get(key)
        if value_str is None:
            return default
        
        try:
            value = float(value_str)
            return value
        except ValueError:
            logging.warning(
                f"Invalid float value for {key}: '{value_str}'. "
                f"Using default: {default}"
            )
            return default
    
    def _load_int_env(self, key: str, default: int) -> int:
        """Load an integer value from environment variable with validation."""
        value_str = os.environ.get(key)
        if value_str is None:
            return default
        
        try:
            value = int(value_str)
            return value
        except ValueError:
            logging.warning(
                f"Invalid integer value for {key}: '{value_str}'. "
                f"Using default: {default}"
            )
            return default
    
    def _load_bool_env(self, key: str, default: bool) -> bool:
        """Load a boolean value from environment variable with validation."""
        value_str = os.environ.get(key)
        if value_str is None:
            return default
        
        value_lower = value_str.lower()
        if value_lower in ('true', '1', 'yes', 'on'):
            return True
        elif value_lower in ('false', '0', 'no', 'off'):
            return False
        else:
            logging.warning(
                f"Invalid boolean value for {key}: '{value_str}'. "
                f"Using default: {default}"
            )
            return default
    
    def _load_str_env(self, key: str, default: str) -> str:
        """Load a string value from environment variable."""
        value = os.environ.get(key)
        if value is None:
            return default
        return value
    
    def _load_tuple_env(self, key: str, default: Tuple[int, int]) -> Tuple[int, int]:
        """Load a tuple value from environment variable with validation."""
        value_str = os.environ.get(key)
        if value_str is None:
            return default
        
        try:
            # Expected format: "800,800" or "800x800"
            parts = value_str.replace('x', ',').split(',')
            if len(parts) != 2:
                raise ValueError("Expected 2 values")
            
            width = int(parts[0].strip())
            height = int(parts[1].strip())
            return (width, height)
        except (ValueError, AttributeError) as e:
            logging.warning(
                f"Invalid tuple value for {key}: '{value_str}'. "
                f"Using default: {default}. Error: {e}"
            )
            return default
    
    def _validate(self):
        """Validate configuration values and log warnings for invalid values."""
        warnings = []
        
        # Validate tolerance thresholds
        if not (0.0 <= self.learning_tolerance <= 1.0):
            warnings.append(
                f"learning_tolerance ({self.learning_tolerance}) should be "
                "between 0.0 and 1.0"
            )
            self.learning_tolerance = max(0.0, min(1.0, self.learning_tolerance))
        
        if not (0.0 <= self.recognition_tolerance <= 1.0):
            warnings.append(
                f"recognition_tolerance ({self.recognition_tolerance}) should be "
                "between 0.0 and 1.0"
            )
            self.recognition_tolerance = max(0.0, min(1.0, self.recognition_tolerance))
        
        # Validate quality thresholds
        if self.min_face_size < 1:
            warnings.append(
                f"min_face_size ({self.min_face_size}) should be at least 1"
            )
            self.min_face_size = max(1, self.min_face_size)
        
        if not (0.0 <= self.min_confidence <= 1.0):
            warnings.append(
                f"min_confidence ({self.min_confidence}) should be between 0.0 and 1.0"
            )
            self.min_confidence = max(0.0, min(1.0, self.min_confidence))
        
        # Validate image size
        if self.target_image_size[0] < 1 or self.target_image_size[1] < 1:
            warnings.append(
                f"target_image_size {self.target_image_size} should have "
                "positive dimensions"
            )
            self.target_image_size = (
                max(1, self.target_image_size[0]),
                max(1, self.target_image_size[1])
            )
        
        # Validate strategy
        valid_strategies = ['distance', 'landmarks', 'hybrid']
        if self.primary_strategy not in valid_strategies:
            warnings.append(
                f"primary_strategy '{self.primary_strategy}' is not valid. "
                f"Valid options: {valid_strategies}"
            )
            self.primary_strategy = 'distance'
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            warnings.append(
                f"log_level '{self.log_level}' is not valid. "
                f"Valid options: {valid_log_levels}"
            )
            self.log_level = 'INFO'
        else:
            self.log_level = self.log_level.upper()
        
        # Log all warnings
        for warning in warnings:
            logging.warning(f"Configuration validation: {warning}")
    
    def __repr__(self) -> str:
        """Return string representation of configuration."""
        return (
            f"FaceMatchingConfig("
            f"learning_tolerance={self.learning_tolerance}, "
            f"recognition_tolerance={self.recognition_tolerance}, "
            f"adaptive_tolerance_enabled={self.adaptive_tolerance_enabled}, "
            f"min_face_size={self.min_face_size}, "
            f"min_confidence={self.min_confidence}, "
            f"normalize_brightness={self.normalize_brightness}, "
            f"target_image_size={self.target_image_size}, "
            f"primary_strategy='{self.primary_strategy}', "
            f"enable_fallback={self.enable_fallback}, "
            f"log_level='{self.log_level}', "
            f"log_match_details={self.log_match_details}"
            f")"
        )
