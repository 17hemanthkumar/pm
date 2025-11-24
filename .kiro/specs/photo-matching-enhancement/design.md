# Design Document

## Overview

This design document outlines the enhancement of the photo matching and facial recognition system in the PicMe application. The current implementation uses the face_recognition library with a fixed tolerance threshold of 0.54 for both learning (grouping photos during upload) and recognition (matching user scans). This design introduces adaptive thresholds, improved preprocessing, quality-based matching, fallback strategies, and comprehensive logging to significantly improve matching accuracy and reliability.

The enhancement maintains full backward compatibility with existing person IDs and photo assignments while providing configurable parameters for fine-tuning the system's behavior.

## Architecture

### Current Architecture

The existing system consists of:
- **FaceRecognitionModel** (`face_model.py`): Manages face learning and recognition with fixed 0.5 learning threshold and 0.54 recognition threshold
- **process_images()** function (`app.py`): Background task that processes uploaded photos, extracts faces, and organizes them by person ID
- **recognize_face()** endpoint (`app.py`): API endpoint that handles user face scans and retrieves their photos
- **known_faces.dat**: Pickle file storing facial encodings and person IDs

### Enhanced Architecture

The enhanced system will:
1. **Extend FaceRecognitionModel** with adaptive threshold logic, quality assessment, and multi-strategy matching
2. **Add FaceMatchingConfig** class to manage configurable parameters
3. **Enhance process_images()** with improved preprocessing and error handling
4. **Add FaceQualityAssessor** component to evaluate encoding quality
5. **Implement MatchingStrategy** interface with multiple concrete strategies
6. **Add comprehensive logging throughout the matching pipeline

### Component Interaction Flow

```
User Scan → recognize_face() → FaceRecognitionModel.recognize_face()
                                      ↓
                                FaceQualityAssessor.assess()
                                      ↓
                                MatchingStrategy.match()
                                      ↓
                                Return person_id or None

Photo Upload → process_images() → FaceRecognitionModel.learn_face()
                                      ↓
                                FaceQualityAssessor.assess()
                                      ↓
                                MatchingStrategy.match()
                                      ↓
                                Assign person_id
```

## Components and Interfaces

### 1. FaceMatchingConfig

A configuration management class that loads and validates matching parameters.

```python
class FaceMatchingConfig:
    def __init__(self, config_file=None):
        # Tolerance thresholds
        self.learning_tolerance: float = 0.45  # Stricter for grouping
        self.recognition_tolerance: float = 0.54  # More lenient for user scans
        self.adaptive_tolerance_enabled: bool = True
        
        # Quality thresholds
        self.min_face_size: int = 80  # pixels
        self.min_confidence: float = 0.7
        
        # Preprocessing options
        self.normalize_brightness: bool = True
        self.target_image_size: tuple = (800, 800)
        
        # Matching strategies
        self.primary_strategy: str = "distance"  # distance, landmarks, hybrid
        self.enable_fallback: bool = True
        
        # Logging
        self.log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
        self.log_match_details: bool = True
```

### 2. FaceQualityAssessor

Evaluates the quality of facial encodings and detection results.

```python
class FaceQualityAssessor:
    def assess_encoding_quality(self, image, face_location) -> dict:
        """
        Returns quality metrics:
        - face_size: pixel dimensions of detected face
        - brightness_score: 0-1, optimal around 0.5
        - blur_score: 0-1, higher is sharper
        - confidence: overall quality 0-1
        """
        
    def should_use_adaptive_threshold(self, quality_metrics) -> bool:
        """Determine if adaptive threshold should be applied"""
        
    def compute_adaptive_tolerance(self, base_tolerance, quality_metrics) -> float:
        """Adjust tolerance based on quality"""
```

### 3. MatchingStrategy Interface

Abstract interface for different matching approaches.

```python
class MatchingStrategy(ABC):
    @abstractmethod
    def match(self, unknown_encoding, known_encodings, known_ids, tolerance) -> tuple:
        """
        Returns: (person_id or None, confidence_score, match_distance)
        """

class DistanceMatchingStrategy(MatchingStrategy):
    """Primary strategy using face_distance"""
    
class LandmarkMatchingStrategy(MatchingStrategy):
    """Secondary strategy using facial landmarks"""
    
class HybridMatchingStrategy(MatchingStrategy):
    """Combines distance and landmarks for higher confidence"""
```

### 4. Enhanced FaceRecognitionModel

Extended version of the existing model with new capabilities.

```python
class FaceRecognitionModel:
    def __init__(self, data_file='known_faces.dat', config=None):
        self.data_file = data_file
        self.config = config or FaceMatchingConfig()
        self.quality_assessor = FaceQualityAssessor()
        self.strategy = self._create_strategy()
        self.known_encodings = []
        self.known_ids = []
        self.load_model()
    
    def learn_face(self, new_encoding, image=None, face_location=None):
        """Enhanced learning with quality assessment and adaptive threshold"""
        
    def recognize_face(self, scanned_encoding, image=None, face_location=None):
        """Enhanced recognition with quality assessment and fallback strategies"""
        
    def _match_with_quality_awareness(self, encoding, quality_metrics, is_learning=False):
        """Internal method that applies quality-based matching logic"""
```

## Data Models

### Quality Metrics Structure

```python
{
    "face_size": (width, height),  # pixels
    "face_area": int,  # width * height
    "brightness_score": float,  # 0-1
    "blur_score": float,  # 0-1
    "confidence": float,  # 0-1, overall quality
    "is_acceptable": bool  # meets minimum thresholds
}
```

### Match Result Structure

```python
{
    "person_id": str or None,
    "match_distance": float,
    "confidence": float,  # 0-1
    "strategy_used": str,  # "distance", "landmarks", "hybrid"
    "quality_metrics": dict,
    "threshold_applied": float,
    "alternative_matches": [  # for debugging
        {"person_id": str, "distance": float}
    ]
}
```

### Configuration File Format (YAML)

```yaml
matching:
  learning_tolerance: 0.45
  recognition_tolerance: 0.54
  adaptive_tolerance_enabled: true

quality:
  min_face_size: 80
  min_confidence: 0.7

preprocessing:
  normalize_brightness: true
  target_image_size: [800, 800]

strategy:
  primary: "distance"
  enable_fallback: true

logging:
  level: "INFO"
  log_match_details: true
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Preprocessing consistency
*For any* image, running it through the preprocessing pipeline multiple times should produce identical or nearly identical facial encodings (within floating-point precision).
**Validates: Requirements 1.1**

### Property 2: Adaptive tolerance based on quality
*For any* facial encoding with quality metrics, the system should apply a tolerance threshold that becomes stricter (lower) as quality decreases, and the quality metrics should influence the matching decision.
**Validates: Requirements 1.2, 3.4, 3.5**

### Property 3: Closest match selection
*For any* scanned encoding and set of known faces where multiple matches exist below the tolerance, the system should select the person ID with the minimum face distance.
**Validates: Requirements 1.3**

### Property 4: Low quality rejection
*For any* facial encoding with quality metrics below acceptable thresholds, the system should return an error requesting a rescan rather than attempting to match.
**Validates: Requirements 1.4**

### Property 5: Threshold enforcement
*For any* facial encoding where the best match distance exceeds the tolerance threshold, the system should return None rather than returning an incorrect person ID.
**Validates: Requirements 1.5**

### Property 6: Complete face extraction
*For any* image with N detectable faces, the processing function should extract exactly N facial encodings.
**Validates: Requirements 2.1**

### Property 7: Learning tolerance stricter than recognition
*For any* system configuration, the learning tolerance should be less than or equal to the recognition tolerance, and the correct tolerance should be applied in each context.
**Validates: Requirements 2.2**

### Property 8: Correct person ID assignment
*For any* new face encoding, if it matches an existing person ID within the learning tolerance, it should be assigned that ID; otherwise, a new unique person ID should be created.
**Validates: Requirements 2.3, 2.4**

### Property 9: Group photo assignment
*For any* photo containing M faces that match M distinct person IDs, that photo should appear in all M person folders as a group photo.
**Validates: Requirements 2.5**

### Property 10: Brightness normalization
*For any* image, if brightness normalization is enabled, the preprocessed image should have brightness values normalized to a target range regardless of the original brightness.
**Validates: Requirements 3.1**

### Property 11: Consistent image resizing
*For any* image with arbitrary dimensions, the preprocessing should resize it to the configured target dimensions before face detection.
**Validates: Requirements 3.2**

### Property 12: Processing resilience
*For any* batch of images including some that fail face detection, the processing should continue for all remaining images and log each failure.
**Validates: Requirements 3.3**

### Property 13: Fallback strategy activation
*For any* encoding where the primary distance metric is inconclusive (multiple candidates within a narrow distance range), the system should apply secondary verification using landmarks or additional features.
**Validates: Requirements 5.1, 5.2**

### Property 14: Strategy selection consistency
*For any* configured matching strategy, the system should apply that strategy consistently across all matching operations.
**Validates: Requirements 5.4**

### Property 15: Quality-based strategy selection
*For any* encoding with quality metrics, the system should select the matching strategy appropriate for that quality level (e.g., hybrid for low quality, distance for high quality).
**Validates: Requirements 5.5**

### Property 16: Data format round-trip
*For any* valid known faces data structure, saving and then loading should produce an equivalent data structure with the same person IDs and encodings.
**Validates: Requirements 7.1, 7.2**

### Property 17: Person ID preservation
*For any* existing person ID in the system, processing new photos should never modify or reassign that person ID to a different face.
**Validates: Requirements 7.3**

### Property 18: Legacy compatibility
*For any* person ID created by the legacy system, the enhanced recognition algorithm should successfully match faces against that person ID.
**Validates: Requirements 7.4**

### Property 19: Configuration application
*For any* valid configuration values (tolerances, preprocessing options), the system should apply those configured values in all relevant operations.
**Validates: Requirements 8.2, 8.3**

### Property 20: Configuration defaults
*For any* invalid or missing configuration value, the system should use a sensible default value and log a warning.
**Validates: Requirements 8.5**

## Error Handling

### Error Categories

1. **Input Validation Errors**
   - No face detected in image
   - Multiple faces in single-person scan
   - Image file corrupted or unreadable
   - Invalid image format

2. **Quality Errors**
   - Face too small (below min_face_size)
   - Image too blurry (below blur threshold)
   - Poor lighting (brightness score too low/high)
   - Low overall confidence score

3. **Matching Errors**
   - No confident match found (all distances exceed threshold)
   - Ambiguous match (multiple candidates with similar distances)
   - Corrupted encoding data in known faces

4. **System Errors**
   - Database file read/write failures
   - Configuration file parsing errors
   - Out of memory during processing
   - Face recognition library errors

### Error Handling Strategies

1. **Graceful Degradation**: When quality is low but acceptable, use more conservative thresholds rather than rejecting outright
2. **Clear User Feedback**: Return specific error messages that guide users on how to resolve the issue
3. **Logging**: Log all errors with context for debugging, including quality metrics and match distances
4. **Fallback**: When primary strategy fails, attempt fallback strategies before giving up
5. **Partial Success**: In batch processing, continue with remaining items even if some fail

### Error Response Format

```python
{
    "success": False,
    "error_code": "LOW_QUALITY_SCAN",
    "error_message": "Face scan quality too low. Please try again with better lighting.",
    "details": {
        "quality_metrics": {...},
        "suggestions": ["Ensure face is well-lit", "Move closer to camera"]
    }
}
```

## Testing Strategy

### Unit Testing

Unit tests will verify specific behaviors and edge cases:

1. **Configuration Loading**: Test that config files are parsed correctly and defaults are applied
2. **Quality Assessment**: Test quality metric calculations with known good/bad images
3. **Threshold Calculation**: Test adaptive threshold computation with various quality levels
4. **Strategy Selection**: Test that correct strategy is selected based on configuration and quality
5. **Error Handling**: Test that appropriate errors are returned for invalid inputs
6. **Edge Cases**: Test empty database, single face, corrupted data scenarios

### Property-Based Testing

Property-based tests will verify universal properties across many random inputs using the **Hypothesis** library for Python:

- **Library**: Hypothesis (https://hypothesis.readthedocs.io/)
- **Iterations**: Minimum 100 iterations per property test
- **Tagging**: Each property test must include a comment with format: `# Feature: photo-matching-enhancement, Property N: [property text]`
- **Coverage**: Each correctness property must be implemented by a single property-based test

Property tests will:
1. Generate random images with varying qualities, sizes, and lighting
2. Generate random facial encodings and quality metrics
3. Generate random configurations with valid parameter ranges
4. Verify properties hold across all generated inputs
5. Use shrinking to find minimal failing examples when properties are violated

### Integration Testing

Integration tests will verify end-to-end workflows:

1. **Upload and Process**: Upload photos, verify they are processed and organized correctly
2. **Scan and Retrieve**: Scan a face, verify correct photos are retrieved
3. **Multi-Event**: Verify person IDs work correctly across multiple events
4. **Backward Compatibility**: Load legacy data, verify it works with enhanced system

### Test Data

Test data will include:
- **Synthetic faces**: Generated faces with controlled variations
- **Real photos**: Sample event photos with various conditions
- **Edge cases**: Blurry images, poor lighting, extreme angles
- **Legacy data**: Existing known_faces.dat files for compatibility testing

## Implementation Notes

### Performance Considerations

1. **Lazy Loading**: Keep lazy loading of face_recognition library to maintain fast startup
2. **Caching**: Cache quality assessments to avoid recomputing for the same image
3. **Batch Processing**: Process multiple faces in parallel when possible
4. **Incremental Saves**: Save model incrementally during batch processing to prevent data loss

### Backward Compatibility

1. **Data Format**: Maintain pickle format for known_faces.dat
2. **Person ID Format**: Keep existing "person_NNNN" format
3. **API Compatibility**: Maintain existing function signatures, add new parameters as optional
4. **Gradual Migration**: Allow system to work with mix of old and new data

### Configuration Management

1. **Default Config**: Embed sensible defaults in code
2. **File Override**: Allow config file to override defaults
3. **Environment Override**: Allow environment variables to override config file
4. **Validation**: Validate all config values and log warnings for invalid values

### Logging Strategy

1. **Structured Logging**: Use structured log format for easy parsing
2. **Log Levels**: DEBUG for detailed matching info, INFO for operations, WARNING for quality issues, ERROR for failures
3. **Performance Logging**: Log processing time for performance monitoring
4. **Match Logging**: Log all match attempts with distances and decisions for debugging

## Dependencies

- **face_recognition**: Core face detection and encoding (existing)
- **opencv-python (cv2)**: Image preprocessing (existing)
- **numpy**: Numerical operations (existing)
- **pickle**: Data serialization (existing, Python standard library)
- **PyYAML**: Configuration file parsing (new, optional)
- **hypothesis**: Property-based testing (new, dev dependency)

## Deployment Considerations

1. **No Reprocessing Required**: Existing events and person IDs continue to work
2. **Configuration File**: Optionally deploy config file for custom tuning
3. **Monitoring**: Monitor match success rates and quality metrics
4. **Gradual Rollout**: Can deploy with conservative settings initially, then tune based on metrics
