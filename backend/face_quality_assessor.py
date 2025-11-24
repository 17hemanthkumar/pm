"""
Face Quality Assessment Module

This module provides quality assessment for facial encodings and detections.
It evaluates face size, brightness, blur, and overall confidence to help
make better matching decisions.
"""

import numpy as np


class FaceQualityAssessor:
    """
    Assesses the quality of facial encodings and detection results.
    
    Quality metrics include:
    - Face size (pixel dimensions)
    - Brightness score (lighting quality)
    - Blur score (image sharpness)
    - Overall confidence (combined quality metric)
    """
    
    def __init__(self, config=None):
        """
        Initialize the quality assessor with configuration.
        
        Args:
            config: FaceMatchingConfig instance with quality thresholds
        """
        self.config = config
        
        # Default thresholds if no config provided
        self.min_face_size = config.min_face_size if config else 80
        self.min_confidence = config.min_confidence if config else 0.7
    
    def assess_encoding_quality(self, image, face_location):
        """
        Assess the quality of a facial encoding.
        
        Args:
            image: numpy array of the image (RGB format)
            face_location: tuple of (top, right, bottom, left) coordinates
        
        Returns:
            dict with quality metrics:
            - face_size: (width, height) in pixels
            - face_area: width * height
            - brightness_score: 0-1, optimal around 0.5
            - blur_score: 0-1, higher is sharper
            - confidence: overall quality 0-1
            - is_acceptable: bool, meets minimum thresholds
        """
        top, right, bottom, left = face_location
        
        # Calculate face size
        face_width = right - left
        face_height = bottom - top
        face_area = face_width * face_height
        
        # Extract face region
        face_region = image[top:bottom, left:right]
        
        # Calculate brightness score
        brightness_score = self._calculate_brightness_score(face_region)
        
        # Calculate blur score
        blur_score = self._calculate_blur_score(face_region)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(
            face_area, brightness_score, blur_score
        )
        
        # Check if quality is acceptable
        is_acceptable = (
            min(face_width, face_height) >= self.min_face_size and
            confidence >= self.min_confidence
        )
        
        return {
            'face_size': (face_width, face_height),
            'face_area': face_area,
            'brightness_score': brightness_score,
            'blur_score': blur_score,
            'confidence': confidence,
            'is_acceptable': is_acceptable
        }
    
    def _calculate_brightness_score(self, face_region):
        """
        Calculate brightness score for a face region.
        
        Optimal brightness is around 0.5 (mid-range).
        Too dark or too bright reduces the score.
        
        Args:
            face_region: numpy array of face pixels (RGB)
        
        Returns:
            float: brightness score 0-1
        """
        # Convert to grayscale for brightness calculation
        if len(face_region.shape) == 3:
            # RGB to grayscale: 0.299*R + 0.587*G + 0.114*B
            gray = np.dot(face_region[..., :3], [0.299, 0.587, 0.114])
        else:
            gray = face_region
        
        # Calculate mean brightness (0-255 range)
        mean_brightness = np.mean(gray)
        
        # Normalize to 0-1 range
        normalized_brightness = mean_brightness / 255.0
        
        # Score is best at 0.5, decreases as it moves away
        # Using a quadratic function: 1 - 4*(x - 0.5)^2
        # This gives score of 1.0 at x=0.5, and 0.0 at x=0 or x=1
        brightness_score = 1.0 - 4.0 * (normalized_brightness - 0.5) ** 2
        
        # Clamp to 0-1 range
        brightness_score = max(0.0, min(1.0, brightness_score))
        
        return brightness_score
    
    def _calculate_blur_score(self, face_region):
        """
        Calculate blur score using Laplacian variance.
        
        Higher variance indicates sharper image (less blur).
        
        Args:
            face_region: numpy array of face pixels (RGB)
        
        Returns:
            float: blur score 0-1, higher is sharper
        """
        # Convert to grayscale if needed
        if len(face_region.shape) == 3:
            gray = np.dot(face_region[..., :3], [0.299, 0.587, 0.114])
        else:
            gray = face_region
        
        # Ensure we have a valid region
        if gray.size == 0:
            return 0.0
        
        # Calculate Laplacian
        # Using a simple discrete Laplacian kernel
        laplacian = self._apply_laplacian(gray)
        
        # Calculate variance of Laplacian
        variance = np.var(laplacian)
        
        # Normalize variance to 0-1 range
        # Typical variance for sharp images: 100-1000
        # Typical variance for blurry images: 0-100
        # Using a sigmoid-like function for smooth mapping
        blur_score = min(1.0, variance / 500.0)
        
        return blur_score
    
    def _apply_laplacian(self, gray_image):
        """
        Apply Laplacian operator to detect edges (blur detection).
        
        Args:
            gray_image: 2D numpy array (grayscale)
        
        Returns:
            numpy array: Laplacian of the image
        """
        # Simple Laplacian kernel:
        # [ 0  1  0]
        # [ 1 -4  1]
        # [ 0  1  0]
        
        # Pad the image to handle borders
        padded = np.pad(gray_image, pad_width=1, mode='edge')
        
        # Apply Laplacian
        laplacian = (
            padded[1:-1, 2:] +      # right
            padded[1:-1, :-2] +     # left
            padded[2:, 1:-1] +      # bottom
            padded[:-2, 1:-1] -     # top
            4 * padded[1:-1, 1:-1]  # center
        )
        
        return laplacian
    
    def _calculate_confidence(self, face_area, brightness_score, blur_score):
        """
        Calculate overall confidence score from individual metrics.
        
        Args:
            face_area: area of face in pixels
            brightness_score: 0-1
            blur_score: 0-1
        
        Returns:
            float: overall confidence 0-1
        """
        # Size score: normalize face area
        # Typical good face size: 80x80 = 6400 pixels minimum
        # Excellent face size: 200x200 = 40000 pixels
        size_score = min(1.0, face_area / 40000.0)
        
        # Weighted combination of metrics
        # Blur is most important (40%), brightness next (35%), size (25%)
        confidence = (
            0.40 * blur_score +
            0.35 * brightness_score +
            0.25 * size_score
        )
        
        return confidence
    
    def should_use_adaptive_threshold(self, quality_metrics):
        """
        Determine if adaptive threshold should be applied based on quality.
        
        Args:
            quality_metrics: dict from assess_encoding_quality()
        
        Returns:
            bool: True if adaptive threshold should be used
        """
        # Use adaptive threshold when quality is not optimal
        # If confidence is below 0.8, we should adapt the threshold
        return quality_metrics['confidence'] < 0.8
    
    def compute_adaptive_tolerance(self, base_tolerance, quality_metrics):
        """
        Adjust tolerance based on quality metrics.
        
        Lower quality -> stricter (lower) tolerance
        Higher quality -> more lenient (higher) tolerance
        
        Args:
            base_tolerance: the baseline tolerance value
            quality_metrics: dict from assess_encoding_quality()
        
        Returns:
            float: adjusted tolerance value
        """
        confidence = quality_metrics['confidence']
        
        # Adjustment factor based on confidence
        # confidence = 1.0 -> factor = 1.0 (no change)
        # confidence = 0.7 -> factor = 0.85 (15% stricter)
        # confidence = 0.5 -> factor = 0.7 (30% stricter)
        # confidence = 0.3 -> factor = 0.55 (45% stricter)
        
        # Linear interpolation: factor = 0.5 + 0.5 * confidence
        # This makes tolerance stricter as quality decreases
        adjustment_factor = 0.5 + 0.5 * confidence
        
        # Apply adjustment
        adjusted_tolerance = base_tolerance * adjustment_factor
        
        # Ensure tolerance stays in valid range [0.0, 1.0]
        adjusted_tolerance = max(0.0, min(1.0, adjusted_tolerance))
        
        return adjusted_tolerance
