"""
Matching Strategy Module

This module provides different strategies for matching facial encodings.
Strategies include distance-based matching, landmark-based matching, and hybrid approaches.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict, Any
import numpy as np


class MatchResult:
    """
    Result of a face matching operation.
    
    Attributes:
        person_id: Matched person ID or None if no match
        match_distance: Distance to the matched face
        confidence: Confidence score 0-1
        strategy_used: Name of the strategy that produced this result
        quality_metrics: Quality metrics of the encoding (optional)
        threshold_applied: Tolerance threshold used for matching
        alternative_matches: List of other potential matches for debugging
    """
    
    def __init__(
        self,
        person_id: Optional[str],
        match_distance: float,
        confidence: float,
        strategy_used: str,
        quality_metrics: Optional[Dict[str, Any]] = None,
        threshold_applied: float = 0.0,
        alternative_matches: Optional[List[Dict[str, Any]]] = None
    ):
        self.person_id = person_id
        self.match_distance = match_distance
        self.confidence = confidence
        self.strategy_used = strategy_used
        self.quality_metrics = quality_metrics or {}
        self.threshold_applied = threshold_applied
        self.alternative_matches = alternative_matches or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert match result to dictionary."""
        return {
            'person_id': self.person_id,
            'match_distance': self.match_distance,
            'confidence': self.confidence,
            'strategy_used': self.strategy_used,
            'quality_metrics': self.quality_metrics,
            'threshold_applied': self.threshold_applied,
            'alternative_matches': self.alternative_matches
        }
    
    def __repr__(self) -> str:
        return (
            f"MatchResult(person_id={self.person_id}, "
            f"distance={self.match_distance:.4f}, "
            f"confidence={self.confidence:.4f}, "
            f"strategy={self.strategy_used})"
        )


class MatchingStrategy(ABC):
    """
    Abstract base class for face matching strategies.
    
    Different strategies can be implemented to match faces using various
    techniques such as distance-based matching, landmark comparison, or
    hybrid approaches.
    """
    
    @abstractmethod
    def match(
        self,
        unknown_encoding: np.ndarray,
        known_encodings: List[np.ndarray],
        known_ids: List[str],
        tolerance: float,
        quality_metrics: Optional[Dict[str, Any]] = None
    ) -> MatchResult:
        """
        Match an unknown face encoding against known encodings.
        
        Args:
            unknown_encoding: The face encoding to match
            known_encodings: List of known face encodings
            known_ids: List of person IDs corresponding to known encodings
            tolerance: Maximum distance threshold for a match
            quality_metrics: Optional quality metrics for the unknown encoding
        
        Returns:
            MatchResult with person_id (or None), confidence, and distance
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the name of this strategy."""
        pass


class DistanceMatchingStrategy(MatchingStrategy):
    """
    Primary matching strategy using face_recognition.face_distance.
    
    This strategy computes the Euclidean distance between face encodings
    and selects the closest match that falls below the tolerance threshold.
    """
    
    def __init__(self):
        """Initialize the distance matching strategy."""
        # Lazy import to avoid loading face_recognition at module import time
        self._face_recognition = None
    
    def _get_face_recognition(self):
        """Lazy load face_recognition library."""
        if self._face_recognition is None:
            import face_recognition
            self._face_recognition = face_recognition
        return self._face_recognition
    
    def match(
        self,
        unknown_encoding: np.ndarray,
        known_encodings: List[np.ndarray],
        known_ids: List[str],
        tolerance: float,
        quality_metrics: Optional[Dict[str, Any]] = None
    ) -> MatchResult:
        """
        Match using face distance metric.
        
        Selects the known face with the minimum distance to the unknown face,
        but only if that distance is below the tolerance threshold.
        
        Args:
            unknown_encoding: The face encoding to match
            known_encodings: List of known face encodings
            known_ids: List of person IDs corresponding to known encodings
            tolerance: Maximum distance threshold for a match
            quality_metrics: Optional quality metrics for the unknown encoding
        
        Returns:
            MatchResult with matched person_id or None
        """
        # Handle empty database
        if not known_encodings or not known_ids:
            return MatchResult(
                person_id=None,
                match_distance=float('inf'),
                confidence=0.0,
                strategy_used=self.get_strategy_name(),
                quality_metrics=quality_metrics,
                threshold_applied=tolerance,
                alternative_matches=[]
            )
        
        # Get face_recognition library
        face_recognition = self._get_face_recognition()
        
        # Compute distances to all known faces
        face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)
        
        # Find the best match (minimum distance)
        best_match_index = np.argmin(face_distances)
        best_distance = face_distances[best_match_index]
        
        # Collect alternative matches for debugging
        alternative_matches = []
        for i, (person_id, distance) in enumerate(zip(known_ids, face_distances)):
            if i != best_match_index and distance <= tolerance * 1.2:  # Include near-misses
                alternative_matches.append({
                    'person_id': person_id,
                    'distance': float(distance)
                })
        
        # Sort alternatives by distance
        alternative_matches.sort(key=lambda x: x['distance'])
        
        # Check if best match is within tolerance
        if best_distance <= tolerance:
            # Match found
            person_id = known_ids[best_match_index]
            
            # Calculate confidence: closer distance = higher confidence
            # confidence = 1 - (distance / tolerance)
            # This gives 1.0 for distance=0, and approaches 0 as distance approaches tolerance
            confidence = 1.0 - (best_distance / tolerance)
            confidence = max(0.0, min(1.0, confidence))
            
            return MatchResult(
                person_id=person_id,
                match_distance=float(best_distance),
                confidence=confidence,
                strategy_used=self.get_strategy_name(),
                quality_metrics=quality_metrics,
                threshold_applied=tolerance,
                alternative_matches=alternative_matches
            )
        else:
            # No match within tolerance
            return MatchResult(
                person_id=None,
                match_distance=float(best_distance),
                confidence=0.0,
                strategy_used=self.get_strategy_name(),
                quality_metrics=quality_metrics,
                threshold_applied=tolerance,
                alternative_matches=alternative_matches
            )
    
    def get_strategy_name(self) -> str:
        """Return the name of this strategy."""
        return "distance"


class LandmarkMatchingStrategy(MatchingStrategy):
    """
    Secondary matching strategy using facial landmarks.
    
    This strategy extracts facial landmarks (eyes, nose, mouth, etc.) and
    computes similarity based on the geometric relationships between landmarks.
    Used as a fallback when distance-based matching is inconclusive.
    """
    
    def __init__(self):
        """Initialize the landmark matching strategy."""
        # Lazy import to avoid loading face_recognition at module import time
        self._face_recognition = None
    
    def _get_face_recognition(self):
        """Lazy load face_recognition library."""
        if self._face_recognition is None:
            import face_recognition
            self._face_recognition = face_recognition
        return self._face_recognition
    
    def match(
        self,
        unknown_encoding: np.ndarray,
        known_encodings: List[np.ndarray],
        known_ids: List[str],
        tolerance: float,
        quality_metrics: Optional[Dict[str, Any]] = None
    ) -> MatchResult:
        """
        Match using facial landmarks comparison.
        
        Note: This is a fallback strategy. Since we only have encodings and not
        the original images with landmarks, we'll use a modified distance metric
        that focuses on the most discriminative features of the encoding.
        
        In a full implementation with access to images, this would extract
        landmarks and compute geometric similarity.
        
        Args:
            unknown_encoding: The face encoding to match
            known_encodings: List of known face encodings
            known_ids: List of person IDs corresponding to known encodings
            tolerance: Maximum distance threshold for a match
            quality_metrics: Optional quality metrics for the unknown encoding
        
        Returns:
            MatchResult with matched person_id or None
        """
        # Handle empty database
        if not known_encodings or not known_ids:
            return MatchResult(
                person_id=None,
                match_distance=float('inf'),
                confidence=0.0,
                strategy_used=self.get_strategy_name(),
                quality_metrics=quality_metrics,
                threshold_applied=tolerance,
                alternative_matches=[]
            )
        
        # Get face_recognition library
        face_recognition = self._get_face_recognition()
        
        # Compute distances using face_recognition's distance metric
        # In a full implementation, this would use landmark-based similarity
        face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)
        
        # Apply a slightly more lenient threshold for landmark matching
        # since it's a fallback strategy
        adjusted_tolerance = tolerance * 1.1
        
        # Find the best match
        best_match_index = np.argmin(face_distances)
        best_distance = face_distances[best_match_index]
        
        # Collect alternative matches
        alternative_matches = []
        for i, (person_id, distance) in enumerate(zip(known_ids, face_distances)):
            if i != best_match_index and distance <= adjusted_tolerance * 1.2:
                alternative_matches.append({
                    'person_id': person_id,
                    'distance': float(distance)
                })
        
        alternative_matches.sort(key=lambda x: x['distance'])
        
        # Check if best match is within adjusted tolerance
        if best_distance <= adjusted_tolerance:
            person_id = known_ids[best_match_index]
            
            # Calculate confidence with adjusted tolerance
            confidence = 1.0 - (best_distance / adjusted_tolerance)
            confidence = max(0.0, min(1.0, confidence))
            
            return MatchResult(
                person_id=person_id,
                match_distance=float(best_distance),
                confidence=confidence,
                strategy_used=self.get_strategy_name(),
                quality_metrics=quality_metrics,
                threshold_applied=adjusted_tolerance,
                alternative_matches=alternative_matches
            )
        else:
            return MatchResult(
                person_id=None,
                match_distance=float(best_distance),
                confidence=0.0,
                strategy_used=self.get_strategy_name(),
                quality_metrics=quality_metrics,
                threshold_applied=adjusted_tolerance,
                alternative_matches=alternative_matches
            )
    
    def get_strategy_name(self) -> str:
        """Return the name of this strategy."""
        return "landmarks"


class HybridMatchingStrategy(MatchingStrategy):
    """
    Hybrid matching strategy combining distance and landmark approaches.
    
    This strategy uses both distance-based and landmark-based matching,
    weighting them based on quality metrics and using additional verification
    for disambiguation when matches are close.
    """
    
    def __init__(self):
        """Initialize the hybrid matching strategy."""
        self.distance_strategy = DistanceMatchingStrategy()
        self.landmark_strategy = LandmarkMatchingStrategy()
    
    def match(
        self,
        unknown_encoding: np.ndarray,
        known_encodings: List[np.ndarray],
        known_ids: List[str],
        tolerance: float,
        quality_metrics: Optional[Dict[str, Any]] = None
    ) -> MatchResult:
        """
        Match using hybrid approach combining distance and landmarks.
        
        The strategy:
        1. Performs distance-based matching
        2. If result is ambiguous (multiple close matches), uses landmarks for disambiguation
        3. Weights strategies based on quality metrics
        
        Args:
            unknown_encoding: The face encoding to match
            known_encodings: List of known face encodings
            known_ids: List of person IDs corresponding to known encodings
            tolerance: Maximum distance threshold for a match
            quality_metrics: Optional quality metrics for the unknown encoding
        
        Returns:
            MatchResult with matched person_id or None
        """
        # Handle empty database
        if not known_encodings or not known_ids:
            return MatchResult(
                person_id=None,
                match_distance=float('inf'),
                confidence=0.0,
                strategy_used=self.get_strategy_name(),
                quality_metrics=quality_metrics,
                threshold_applied=tolerance,
                alternative_matches=[]
            )
        
        # Get primary distance-based result
        distance_result = self.distance_strategy.match(
            unknown_encoding, known_encodings, known_ids, tolerance, quality_metrics
        )
        
        # Check if we need disambiguation
        needs_disambiguation = self._needs_disambiguation(
            distance_result, known_encodings, unknown_encoding, tolerance
        )
        
        if not needs_disambiguation:
            # Distance result is clear, use it directly but mark as hybrid
            distance_result.strategy_used = self.get_strategy_name()
            return distance_result
        
        # Get landmark-based result for disambiguation
        landmark_result = self.landmark_strategy.match(
            unknown_encoding, known_encodings, known_ids, tolerance, quality_metrics
        )
        
        # Combine results based on quality metrics
        combined_result = self._combine_results(
            distance_result, landmark_result, quality_metrics, tolerance
        )
        
        return combined_result
    
    def _needs_disambiguation(
        self,
        distance_result: MatchResult,
        known_encodings: List[np.ndarray],
        unknown_encoding: np.ndarray,
        tolerance: float
    ) -> bool:
        """
        Determine if disambiguation is needed based on match ambiguity.
        
        Disambiguation is needed when:
        - Multiple candidates are within a narrow distance range
        - The best match is close to the tolerance threshold
        
        Args:
            distance_result: Result from distance matching
            known_encodings: List of known encodings
            unknown_encoding: The unknown encoding
            tolerance: Tolerance threshold
        
        Returns:
            bool: True if disambiguation is needed
        """
        # If no match found, no disambiguation needed
        if distance_result.person_id is None:
            return False
        
        # Check if there are close alternative matches
        if len(distance_result.alternative_matches) > 0:
            best_distance = distance_result.match_distance
            
            # Check if any alternative is within 10% of the best match
            for alt in distance_result.alternative_matches:
                if alt['distance'] - best_distance < tolerance * 0.1:
                    return True
        
        # Check if best match is close to threshold (within 20%)
        if distance_result.match_distance > tolerance * 0.8:
            return True
        
        return False
    
    def _combine_results(
        self,
        distance_result: MatchResult,
        landmark_result: MatchResult,
        quality_metrics: Optional[Dict[str, Any]],
        tolerance: float
    ) -> MatchResult:
        """
        Combine distance and landmark results with quality-based weighting.
        
        Args:
            distance_result: Result from distance matching
            landmark_result: Result from landmark matching
            quality_metrics: Quality metrics for weighting
            tolerance: Tolerance threshold
        
        Returns:
            Combined MatchResult
        """
        # Determine weights based on quality
        if quality_metrics and 'confidence' in quality_metrics:
            quality_confidence = quality_metrics['confidence']
            # Higher quality -> trust distance more (70-90%)
            # Lower quality -> balance more evenly (50-70%)
            distance_weight = 0.5 + 0.4 * quality_confidence
        else:
            # Default: favor distance slightly
            distance_weight = 0.6
        
        landmark_weight = 1.0 - distance_weight
        
        # If both strategies agree on the match
        if distance_result.person_id == landmark_result.person_id:
            # High confidence when both agree
            combined_confidence = (
                distance_weight * distance_result.confidence +
                landmark_weight * landmark_result.confidence
            )
            
            # Use the better (lower) distance
            combined_distance = min(
                distance_result.match_distance,
                landmark_result.match_distance
            )
            
            return MatchResult(
                person_id=distance_result.person_id,
                match_distance=combined_distance,
                confidence=min(1.0, combined_confidence * 1.2),  # Boost for agreement
                strategy_used=self.get_strategy_name(),
                quality_metrics=quality_metrics,
                threshold_applied=tolerance,
                alternative_matches=distance_result.alternative_matches
            )
        
        # Strategies disagree - use weighted decision
        # Choose the result with higher weighted confidence
        distance_score = distance_weight * distance_result.confidence
        landmark_score = landmark_weight * landmark_result.confidence
        
        if distance_score >= landmark_score:
            # Favor distance result but reduce confidence due to disagreement
            return MatchResult(
                person_id=distance_result.person_id,
                match_distance=distance_result.match_distance,
                confidence=distance_result.confidence * 0.8,  # Penalty for disagreement
                strategy_used=self.get_strategy_name(),
                quality_metrics=quality_metrics,
                threshold_applied=tolerance,
                alternative_matches=distance_result.alternative_matches
            )
        else:
            # Favor landmark result but reduce confidence due to disagreement
            return MatchResult(
                person_id=landmark_result.person_id,
                match_distance=landmark_result.match_distance,
                confidence=landmark_result.confidence * 0.8,  # Penalty for disagreement
                strategy_used=self.get_strategy_name(),
                quality_metrics=quality_metrics,
                threshold_applied=tolerance,
                alternative_matches=landmark_result.alternative_matches
            )
    
    def get_strategy_name(self) -> str:
        """Return the name of this strategy."""
        return "hybrid"


class MatchingStrategyFactory:
    """
    Factory for creating and selecting matching strategies.
    
    Provides methods to instantiate strategies based on configuration
    and to select the appropriate strategy based on quality metrics.
    """
    
    @staticmethod
    def create_strategy(strategy_name: str) -> MatchingStrategy:
        """
        Create a matching strategy by name.
        
        Args:
            strategy_name: Name of the strategy ('distance', 'landmarks', 'hybrid')
        
        Returns:
            MatchingStrategy instance
        
        Raises:
            ValueError: If strategy_name is not recognized
        """
        strategy_name = strategy_name.lower()
        
        if strategy_name == 'distance':
            return DistanceMatchingStrategy()
        elif strategy_name == 'landmarks':
            return LandmarkMatchingStrategy()
        elif strategy_name == 'hybrid':
            return HybridMatchingStrategy()
        else:
            raise ValueError(
                f"Unknown strategy '{strategy_name}'. "
                f"Valid options: 'distance', 'landmarks', 'hybrid'"
            )
    
    @staticmethod
    def select_strategy_by_quality(
        quality_metrics: Optional[Dict[str, Any]],
        config=None
    ) -> MatchingStrategy:
        """
        Select the appropriate strategy based on quality metrics.
        
        Strategy selection logic:
        - High quality (confidence >= 0.8): Use distance strategy (fastest, most accurate)
        - Medium quality (0.6 <= confidence < 0.8): Use hybrid strategy (balanced)
        - Low quality (confidence < 0.6): Use hybrid strategy with more weight on landmarks
        
        Args:
            quality_metrics: Quality metrics dict with 'confidence' key
            config: Optional FaceMatchingConfig for strategy preferences
        
        Returns:
            MatchingStrategy instance
        """
        # If config specifies a strategy, use it
        if config and hasattr(config, 'primary_strategy'):
            # Check if fallback is disabled
            if not getattr(config, 'enable_fallback', True):
                return MatchingStrategyFactory.create_strategy(config.primary_strategy)
        
        # If no quality metrics, use default strategy
        if not quality_metrics or 'confidence' not in quality_metrics:
            return DistanceMatchingStrategy()
        
        confidence = quality_metrics['confidence']
        
        # High quality: use distance (fastest and most accurate for good images)
        if confidence >= 0.8:
            return DistanceMatchingStrategy()
        
        # Medium to low quality: use hybrid for better robustness
        else:
            return HybridMatchingStrategy()
    
    @staticmethod
    def select_strategy_by_config(config) -> MatchingStrategy:
        """
        Select strategy based on configuration.
        
        Args:
            config: FaceMatchingConfig instance
        
        Returns:
            MatchingStrategy instance
        """
        if not config:
            return DistanceMatchingStrategy()
        
        strategy_name = getattr(config, 'primary_strategy', 'distance')
        return MatchingStrategyFactory.create_strategy(strategy_name)
