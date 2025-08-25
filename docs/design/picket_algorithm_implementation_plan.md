# Picket Algorithm Implementation Plan

## Overview
This document outlines the step-by-step plan for implementing the correct picket algorithm based on the detailed specification in `picket_placement_specification.md`. The algorithm will properly place vertical pickets on spiral stair treads with correct spacing, IBC compliance, and variable heights.

## Implementation Plan

### Phase 1: Analysis and Preparation
1. **Review Current Implementation**
   - Analyze existing `modules/picket_module.py`
   - Identify what needs to be changed vs. what can be reused
   - Review how the module integrates with the orchestrator

2. **Understand Dependencies**
   - Review `core/orchestrator.py` to understand how pickets are called
   - Check `modules/tread_module.py` for tread geometry data availability
   - Examine `modules/handrail_module.py` for handrail helix calculations

### Phase 2: Core Algorithm Implementation
3. **Implement Arc Calculation Functions**
   - Create function to calculate offset arc radius: `outside_radius - (handrail_diameter / 2)`
   - Create function to calculate arc rotation for clearance: `picket_size / 2`
   - Create function to calculate start and end angles for each tread's arc

4. **Implement IBC Compliance Logic**
   - Create function to determine optimal number of pickets for IBC compliance
   - Implement spacing calculation: `arc_length / (number_of_pickets - 1)`
   - Add validation to ensure spacing ≤ 4" (sphere test)
   - Logic to use 5 pickets for calculation but place only 4 actual pickets

5. **Implement Variable Height Calculations**
   - Create function to calculate handrail helix height at any given angle
   - Create function to determine each picket's height based on its position
   - Implement intersection calculation between picket and handrail helix

### Phase 3: Integration and Testing
6. **Update Picket Module**
   - Replace existing `generate_geometry` method with new algorithm
   - Update configuration parameter handling
   - Add proper error handling and logging
   - Ensure compatibility with existing UI configuration

7. **Create Comprehensive Tests**
   - Write tests for arc calculations
   - Write tests for IBC compliance logic
   - Write tests for variable height calculations
   - Write integration tests for the complete algorithm

8. **UI Integration Verification**
   - Verify UI configuration parameters work with new algorithm
   - Check that IBC validation in UI still works correctly
   - Ensure picket quantity controls function properly

### Phase 4: Validation and Refinement
9. **Manual Testing Preparation**
   - Create test cases with default parameters (5.56, 144, 72, 450)
   - Prepare for comparison with manual CAD results
   - Document expected vs. actual results

10. **Performance Optimization**
    - Optimize calculations for efficiency
    - Minimize redundant computations
    - Ensure clean, maintainable code

## Implementation Details

### Key Functions to Implement:

1. **`_calculate_offset_arc_radius(config)`**
   - Input: Configuration dictionary
   - Output: Radius for offset arc
   - Formula: `outside_radius - (handrail_diameter / 2)`

2. **`_calculate_arc_clearance_angle(config)`**
   - Input: Configuration dictionary
   - Output: Angle in radians for arc rotation
   - Formula: `picket_size / 2` converted to angle based on radius

3. **`_calculate_picket_spacing(arc_length, num_pickets)`**
   - Input: Arc length and number of pickets
   - Output: Spacing between pickets
   - Formula: `arc_length / (num_pickets - 1)`

4. **`_ensure_ibc_compliance(spacing)`**
   - Input: Calculated spacing
   - Output: Boolean indicating compliance
   - Check: `spacing <= 4.0`

5. **`_calculate_picket_height(angle, tread_height, config)`**
   - Input: Picket angle, tread height, configuration
   - Output: Picket height
   - Calculate intersection with handrail helix

6. **`_generate_picket_positions(tread_data, config)`**
   - Input: Tread geometry data and configuration
   - Output: List of picket positions and heights
   - Main coordination function

### Configuration Parameters Needed:
- `center_pole_diameter`
- `overall_height`
- `outside_diameter`
- `total_rotation`
- `handrail_diameter`
- `picket_size` (diameter or width)
- `picket_style` (vertical/horizontal)
- `quantity_per_tread`

### Expected Results:
For default parameters (5.56, 144, 72, 450):
- 4 pickets per tread
- Spacing: ~3.8130" (compliant with 4" rule)
- Variable heights: ~38.07", 40.32", 42.57", 44.82"

## Success Criteria:
1. ✅ Pickets placed along offset arc (not outer edge)
2. ✅ Correct number of pickets per tread (4)
3. ✅ IBC compliant spacing (≤ 4")
4. ✅ Variable heights based on handrail intersection
5. ✅ Proper clearance from tread edges
6. ✅ All tests pass
7. ✅ Integration with existing UI works
8. ✅ Manual testing confirms correct placement

## Timeline Estimate:
- Phase 1: 1-2 hours
- Phase 2: 3-4 hours
- Phase 3: 2-3 hours
- Phase 4: 1-2 hours
- **Total: 7-11 hours**

## Risk Mitigation:
- Use restore point if implementation goes wrong
- Test each phase independently
- Maintain compatibility with existing code structure
- Document any deviations from specification