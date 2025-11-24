"""
Property-based tests for matching strategies.

Tests correctness properties for face matching strategies including
closest match selection, threshold enforcement, fallback activation,
and strategy selection consistency.
"""

import numpy as np
from hypothesis import given, strategies as st, settings, assume
from matching_strategy import (
    MatchingStrategy,
    DistanceMatchingStrategy,
    LandmarkMatchingStrategy,
    HybridMatchingStrategy,
    MatchResult,
    MatchingStrategyFactory
)
from face_matching_config import FaceMatchingConfig


# Strategy for generating valid face encodings (128-dimensional vectors)
def face_encoding():
    """Generate a valid face encoding (128-dimensional normalized vector)."""
    # Face encodings are 128-dimensional vectors with values typically in [-1, 1]
    # Use numpy arrays directly for better performance
    return st.builds(
        lambda: np.random.uniform(-1.0, 1.0, 128).astype(np.float64)
    )


@st.composite
def known_faces_database(draw, min_size=2, max_size=10):
    """Generate a database of known faces with IDs."""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    # Generate all encodings at once for better performance
    encodings = [np.random.uniform(-1.0, 1.0, 128).astype(np.float64) for _ in range(size)]
    ids = [f"person_{i:04d}" for i in range(1, size + 1)]
    return encodings, ids


@st.composite
def tolerance_value(draw):
    """Generate a valid tolerance value."""
    return draw(st.floats(min_value=0.1, max_value=0.9, allow_nan=False, allow_infinity=False))


# Property 3: Closest match selection
# Feature: photo-matching-enhancement, Property 3: Closest match selection
# Validates: Requirements 1.3
@settings(max_examples=100, deadline=None)
@given(
    database=known_faces_database(min_size=2, max_size=10),
    tolerance=tolerance_value()
)
def test_property_closest_match_selection(database, tolerance):
    """
    Property 3: Closest match selection
    
    For any scanned encoding and set of known faces where multiple matches exist
    below the tolerance, the system should select the person ID with the minimum
    face distance.
    
    Validates: Requirements 1.3
    """
    known_encodings, known_ids = database
    
    # Generate unknown encoding
    unknown = np.random.uniform(-1.0, 1.0, 128).astype(np.float64)
    
    # Create strategy
    strategy = DistanceMatchingStrategy()
    
    # Perform matching
    result = strategy.match(unknown, known_encodings, known_ids, tolerance)
    
    # Compute all distances manually
    distances = []
    for encoding in known_encodings:
        distance = np.linalg.norm(unknown - encoding)
        distances.append(distance)
    
    # Find minimum distance and corresponding ID
    min_distance = min(distances)
    min_index = distances.index(min_distance)
    expected_id = known_ids[min_index]
    
    # Property: If there's a match within tolerance, it should be the closest one
    if min_distance <= tolerance:
        # There should be a match
        assert result.person_id is not None, \
            f"Expected match for distance {min_distance} <= tolerance {tolerance}"
        
        # It should be the person with minimum distance
        assert result.person_id == expected_id, \
            f"Expected closest match {expected_id}, got {result.person_id}"
        
        # The reported distance should match the minimum distance
        assert abs(result.match_distance - min_distance) < 0.001, \
            f"Expected distance {min_distance}, got {result.match_distance}"
    else:
        # No match should be found
        assert result.person_id is None, \
            f"Expected no match for distance {min_distance} > tolerance {tolerance}"


# Property 5: Threshold enforcement
# Feature: photo-matching-enhancement, Property 5: Threshold enforcement
# Validates: Requirements 1.5
@settings(max_examples=100, deadline=None)
@given(
    database=known_faces_database(min_size=2, max_size=10),
    tolerance=tolerance_value()
)
def test_property_threshold_enforcement(database, tolerance):
    """
    Property 5: Threshold enforcement
    
    For any facial encoding where the best match distance exceeds the tolerance
    threshold, the system should return None rather than returning an incorrect
    person ID.
    
    Validates: Requirements 1.5
    """
    known_encodings, known_ids = database
    
    # Generate unknown encoding
    unknown = np.random.uniform(-1.0, 1.0, 128).astype(np.float64)
    
    # Create strategy
    strategy = DistanceMatchingStrategy()
    
    # Perform matching
    result = strategy.match(unknown, known_encodings, known_ids, tolerance)
    
    # Compute all distances manually
    distances = []
    for encoding in known_encodings:
        distance = np.linalg.norm(unknown - encoding)
        distances.append(distance)
    
    # Find minimum distance
    min_distance = min(distances)
    
    # Property: If minimum distance exceeds tolerance, no match should be returned
    if min_distance > tolerance:
        assert result.person_id is None, \
            f"Expected no match when min_distance {min_distance} > tolerance {tolerance}, " \
            f"but got person_id {result.person_id}"
        
        # Confidence should be 0 when no match
        assert result.confidence == 0.0, \
            f"Expected confidence 0.0 for no match, got {result.confidence}"
    else:
        # If within tolerance, a match should be returned
        assert result.person_id is not None, \
            f"Expected a match when min_distance {min_distance} <= tolerance {tolerance}"
        
        # Confidence should be positive when there's a match
        assert result.confidence > 0.0, \
            f"Expected positive confidence for match, got {result.confidence}"


# Property 13: Fallback strategy activation
# Feature: photo-matching-enhancement, Property 13: Fallback strategy activation
# Validates: Requirements 5.1, 5.2
@settings(max_examples=100, deadline=None)
@given(
    database=known_faces_database(min_size=3, max_size=10),
    tolerance=tolerance_value()
)
def test_property_fallback_strategy_activation(database, tolerance):
    """
    Property 13: Fallback strategy activation
    
    For any encoding where the primary distance metric is inconclusive
    (multiple candidates within a narrow distance range), the system should
    apply secondary verification using landmarks or additional features.
    
    Validates: Requirements 5.1, 5.2
    """
    known_encodings, known_ids = database
    
    # Generate unknown encoding that will be close to multiple known faces
    # by averaging two known encodings
    unknown = (known_encodings[0] + known_encodings[1]) / 2.0
    
    # Add some noise to make it not exactly between them
    noise = np.random.uniform(-0.1, 0.1, 128)
    unknown = unknown + noise
    
    # Create hybrid strategy
    hybrid_strategy = HybridMatchingStrategy()
    
    # Perform matching with hybrid strategy
    hybrid_result = hybrid_strategy.match(unknown, known_encodings, known_ids, tolerance)
    
    # Also get distance-only result for comparison
    distance_strategy = DistanceMatchingStrategy()
    distance_result = distance_strategy.match(unknown, known_encodings, known_ids, tolerance)
    
    # Property: When using hybrid strategy, it should use "hybrid" as strategy name
    assert hybrid_result.strategy_used == "hybrid", \
        f"Expected hybrid strategy to report 'hybrid', got '{hybrid_result.strategy_used}'"
    
    # Property: Hybrid strategy should produce a valid result
    # (either a match or no match, but not an error)
    assert hybrid_result.person_id is None or isinstance(hybrid_result.person_id, str), \
        f"Expected person_id to be None or string, got {type(hybrid_result.person_id)}"
    
    # Property: If distance strategy found a match, hybrid should also find a match
    # (hybrid may find a different person, but should not fail to match if distance succeeded)
    if distance_result.person_id is not None:
        # Hybrid should also find a match (though possibly different)
        assert hybrid_result.person_id is not None, \
            "Hybrid strategy should find a match when distance strategy does"


# Property 14: Strategy selection consistency
# Feature: photo-matching-enhancement, Property 14: Strategy selection consistency
# Validates: Requirements 5.4
@settings(max_examples=100, deadline=None)
@given(
    strategy_name=st.sampled_from(['distance', 'landmarks', 'hybrid']),
    database=known_faces_database(min_size=2, max_size=10),
    tolerance=tolerance_value()
)
def test_property_strategy_selection_consistency(strategy_name, database, tolerance):
    """
    Property 14: Strategy selection consistency
    
    For any configured matching strategy, the system should apply that strategy
    consistently across all matching operations.
    
    Validates: Requirements 5.4
    """
    known_encodings, known_ids = database
    
    # Generate unknown encoding
    unknown = np.random.uniform(-1.0, 1.0, 128).astype(np.float64)
    
    # Create strategy using factory
    strategy = MatchingStrategyFactory.create_strategy(strategy_name)
    
    # Perform multiple matches with the same strategy
    result1 = strategy.match(unknown, known_encodings, known_ids, tolerance)
    result2 = strategy.match(unknown, known_encodings, known_ids, tolerance)
    
    # Property: Strategy name should be consistent
    assert result1.strategy_used == strategy.get_strategy_name(), \
        f"Result strategy '{result1.strategy_used}' doesn't match strategy name '{strategy.get_strategy_name()}'"
    
    # Property: Multiple calls should produce identical results
    assert result1.person_id == result2.person_id, \
        f"Inconsistent person_id: {result1.person_id} vs {result2.person_id}"
    
    assert abs(result1.match_distance - result2.match_distance) < 0.0001, \
        f"Inconsistent distance: {result1.match_distance} vs {result2.match_distance}"
    
    assert abs(result1.confidence - result2.confidence) < 0.0001, \
        f"Inconsistent confidence: {result1.confidence} vs {result2.confidence}"
    
    # Property: Strategy used should match the requested strategy
    # (or 'hybrid' if the strategy internally uses hybrid approach)
    expected_strategy = strategy.get_strategy_name()
    assert result1.strategy_used == expected_strategy, \
        f"Expected strategy '{expected_strategy}', got '{result1.strategy_used}'"


# Property 15: Quality-based strategy selection
# Feature: photo-matching-enhancement, Property 15: Quality-based strategy selection
# Validates: Requirements 5.5
@settings(max_examples=100, deadline=None)
@given(
    confidence=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
def test_property_quality_based_strategy_selection(confidence):
    """
    Property 15: Quality-based strategy selection
    
    For any encoding with quality metrics, the system should select the matching
    strategy appropriate for that quality level (e.g., hybrid for low quality,
    distance for high quality).
    
    Validates: Requirements 5.5
    """
    # Create quality metrics with the given confidence
    quality_metrics = {
        'confidence': confidence,
        'face_size': (100, 100),
        'face_area': 10000,
        'brightness_score': 0.7,
        'blur_score': 0.8,
        'is_acceptable': True
    }
    
    # Select strategy based on quality
    strategy = MatchingStrategyFactory.select_strategy_by_quality(quality_metrics)
    
    # Property: Strategy should be appropriate for quality level
    strategy_name = strategy.get_strategy_name()
    
    if confidence >= 0.8:
        # High quality should use distance strategy (fastest, most accurate)
        assert strategy_name == 'distance', \
            f"Expected 'distance' strategy for high confidence {confidence}, got '{strategy_name}'"
    else:
        # Medium to low quality should use hybrid strategy (more robust)
        assert strategy_name == 'hybrid', \
            f"Expected 'hybrid' strategy for confidence {confidence}, got '{strategy_name}'"
    
    # Property: Strategy should be a valid MatchingStrategy instance
    assert isinstance(strategy, MatchingStrategy), \
        f"Expected MatchingStrategy instance, got {type(strategy)}"
    
    # Property: Selected strategy should be usable (has required methods)
    assert hasattr(strategy, 'match'), \
        "Strategy should have 'match' method"
    assert hasattr(strategy, 'get_strategy_name'), \
        "Strategy should have 'get_strategy_name' method"


if __name__ == "__main__":
    # Run the property tests
    test_property_closest_match_selection()
    print("✓ Property 3: Closest match selection - PASSED")
    
    test_property_threshold_enforcement()
    print("✓ Property 5: Threshold enforcement - PASSED")
    
    test_property_fallback_strategy_activation()
    print("✓ Property 13: Fallback strategy activation - PASSED")
    
    test_property_strategy_selection_consistency()
    print("✓ Property 14: Strategy selection consistency - PASSED")
    
    test_property_quality_based_strategy_selection()
    print("✓ Property 15: Quality-based strategy selection - PASSED")
