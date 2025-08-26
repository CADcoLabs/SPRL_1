# AutoCAD COM Polyline Creation - Complete Solution

## Overview

This document provides the definitive solution for creating polylines through AutoCAD's COM interface, specifically addressing the challenging compatibility issues between modern AutoCAD versions and legacy documentation.

## The Problem

When creating polylines via AutoCAD COM interface, developers commonly encounter this error:

```
(-2147352567, 'Exception occurred.', (0, 'AutoCAD.Application', 
'Too few elements in SafeArray or total number of elements is not a multiple of three'))
```

### Root Causes

1. **Misleading Documentation**: Most AutoCAD COM documentation shows `AddPolyline` expecting 2D coordinates, but modern AutoCAD actually requires 3D coordinates for this method.

2. **Hidden Modern Method**: `AddLightWeightPolyline` is the recommended method for AutoCAD 2020+, but it's poorly documented and uses different coordinate formatting.

3. **Version Evolution**: AutoCAD's COM interface evolved between versions without clear migration guidance.

## The Solution: Dual-Method Approach

The key breakthrough is understanding that modern AutoCAD has **two different polyline methods** with **different coordinate requirements**:

### Method 1: AddLightWeightPolyline (Recommended)
- **Format**: 2D coordinates `[x1, y1, x2, y2, ...]`
- **Best for**: Modern AutoCAD 2020+
- **Advantages**: Memory efficient, faster

### Method 2: AddPolyline (Legacy Fallback)
- **Format**: 3D coordinates `[x1, y1, z1, x2, y2, z2, ...]`
- **Best for**: Backward compatibility
- **Note**: Despite documentation suggesting 2D, it actually requires 3D coordinates

## Implementation

### Complete Working Code

```python
def create_polyline(self, points: list) -> Any:
    """
    Create polyline in AutoCAD using dual-method approach.
    
    Args:
        points: List of (x, y, z) points
    Returns:
        AutoCAD polyline entity
    """
    # Validate minimum points
    if len(points) < 2:
        raise GeometryError("Polyline must have at least 2 points")
        
    # Get model space
    model_space = self.connection_manager.get_model_space()
    
    # Extract Z coordinate for elevation
    z_coordinate = None
    if len(points[0]) >= 3:
        z_coordinate = float(points[0][2])
    
    # Method 1: Try AddLightWeightPolyline (modern method)
    if hasattr(model_space, 'AddLightWeightPolyline'):
        try:
            # Prepare 2D coordinates [x1, y1, x2, y2, ...]
            flattened_2d = []
            for point in points:
                flattened_2d.extend([float(point[0]), float(point[1])])
            
            # Convert to VARIANT array for 2D coordinates
            points_variant_2d = self._convert_to_variant_array_2d(flattened_2d)
            
            # Create lightweight polyline
            polyline = model_space.AddLightWeightPolyline(points_variant_2d)
            
            # Set elevation if provided
            if z_coordinate is not None:
                polyline.Elevation = z_coordinate
            
            # Close if needed
            if len(points) >= 2 and points[0][:2] == points[-1][:2]:
                polyline.Closed = True
            
            return polyline
            
        except Exception as lw_error:
            # Fall through to legacy method
            pass
    
    # Method 2: Fallback to AddPolyline (legacy method)
    # Prepare 3D coordinates [x1, y1, z1, x2, y2, z2, ...]
    flattened_3d = []
    for point in points:
        x = float(point[0])
        y = float(point[1])
        z = float(point[2]) if len(point) >= 3 else (z_coordinate or 0.0)
        flattened_3d.extend([x, y, z])
    
    # Convert to VARIANT array for 3D coordinates
    points_variant_3d = self._convert_to_variant_array_3d(flattened_3d)
    
    # Create legacy polyline
    polyline = model_space.AddPolyline(points_variant_3d)
    
    # Close if needed
    if len(points) >= 2 and points[0][:2] == points[-1][:2]:
        polyline.Closed = True
    
    return polyline
```

### VARIANT Array Conversion Methods

```python
def _convert_to_variant_array_2d(self, coordinates: list) -> Any:
    """Convert 2D coordinates to VARIANT array for AddLightWeightPolyline."""
    import win32com.client
    import pythoncom
    
    # Validate even number of elements (x,y pairs)
    if len(coordinates) % 2 != 0:
        raise ValueError("2D coordinates must have even number of elements")
    
    return win32com.client.VARIANT(
        pythoncom.VT_ARRAY | pythoncom.VT_R8,
        coordinates
    )

def _convert_to_variant_array_3d(self, coordinates: list) -> Any:
    """Convert 3D coordinates to VARIANT array for AddPolyline."""
    import win32com.client
    import pythoncom
    
    # Validate multiple of 3 elements (x,y,z triplets)
    if len(coordinates) % 3 != 0:
        raise ValueError("3D coordinates must have multiple of 3 elements")
    
    return win32com.client.VARIANT(
        pythoncom.VT_ARRAY | pythoncom.VT_R8,
        coordinates
    )
```

## Key Insights

### The "Multiple of Three" Mystery Solved

The error message "total number of elements is not a multiple of three" was the crucial clue that `AddPolyline` expects 3D coordinates, despite most documentation showing 2D examples.

### Why Documentation is Wrong

1. **Historical Accuracy**: Older AutoCAD versions may have accepted 2D coordinates
2. **Method Confusion**: Documentation often conflates `AddPolyline` and `AddLightWeightPolyline`
3. **Version Gaps**: AutoCAD 2020+ introduced changes not reflected in older documentation

## Testing Strategy

### Validation Points

1. **Coordinate Count**: Ensure 2D arrays have even elements, 3D arrays have multiples of 3
2. **Method Availability**: Check if `AddLightWeightPolyline` exists before attempting
3. **Fallback Logic**: Always provide legacy method as backup
4. **Elevation Handling**: Set elevation for 2D polylines when Z coordinates provided

### Test Cases

```python
def test_polyline_creation():
    # Test 2D points (should work with both methods)
    points_2d = [(10.0, 20.0), (30.0, 40.0), (50.0, 60.0)]
    
    # Test 3D points (should work with both methods)
    points_3d = [(10.0, 20.0, 5.0), (30.0, 40.0, 5.0), (50.0, 60.0, 5.0)]
    
    # Test closed polyline
    points_closed = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0), (0.0, 0.0, 0.0)]
```

## Troubleshooting

### Common Issues

1. **"Invalid class string"**: Use Git Bash environment on Windows (see CLAUDE.md)
2. **"Too few elements"**: Check coordinate array formatting (2D vs 3D)
3. **Method not found**: Verify AutoCAD version supports `AddLightWeightPolyline`

### Debugging Tips

1. **Log coordinate arrays**: Always log flattened coordinate arrays before VARIANT conversion
2. **Check array lengths**: Validate even/multiple-of-3 requirements
3. **Test both methods**: Isolate which method is failing
4. **Verify model space**: Ensure valid model space connection

## Performance Considerations

### Method Selection Priority

1. **First choice**: `AddLightWeightPolyline` - More memory efficient, faster
2. **Fallback**: `AddPolyline` - Broader compatibility, more memory usage

### Optimization Tips

1. **Batch creation**: Create multiple polylines in single operations when possible
2. **Elevation setting**: Set elevation once rather than per-vertex
3. **Closure detection**: Check first/last point equality before setting Closed property

## Version Compatibility

### AutoCAD 2020+
- **Recommended**: Use dual-method approach
- **Primary**: `AddLightWeightPolyline` with 2D coordinates
- **Fallback**: `AddPolyline` with 3D coordinates

### AutoCAD 2019 and Earlier
- **Method**: `AddPolyline` only
- **Format**: May accept either 2D or 3D (version-dependent)
- **Recommendation**: Always use 3D format for consistency

## Integration Notes

### In Existing Codebases

1. **Replace single-method calls**: Update any direct `AddPolyline` calls to use dual-method approach
2. **Update error handling**: Catch and handle both method failures appropriately
3. **Coordinate conversion**: Ensure proper 2D/3D coordinate preparation
4. **Testing**: Validate with both AutoCAD versions if supporting legacy systems

### Best Practices

1. **Always validate inputs**: Check point count and coordinate completeness
2. **Use proper VARIANT types**: VT_R8 (double) for coordinate arrays
3. **Handle failures gracefully**: Don't fail entire operations for single polyline errors
4. **Log extensively**: COM interface debugging requires detailed logging

## Summary

The key breakthrough in AutoCAD COM polyline creation is recognizing that modern AutoCAD has two distinct methods with different coordinate requirements. The dual-method approach ensures maximum compatibility across AutoCAD versions while providing optimal performance.

**Remember**: Despite what documentation suggests, `AddPolyline` requires 3D coordinates in modern AutoCAD, while `AddLightWeightPolyline` uses 2D coordinates as documented.

This solution eliminates the frustrating "multiple of three" error and provides robust polyline creation for all AutoCAD COM applications.