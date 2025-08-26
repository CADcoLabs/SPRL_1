# Implementation Plan: Widened Tread Geometry with Original Reference Option

## Project Overview

This plan outlines the implementation of widened tread geometry functionality for the spiral staircase tread module, with an optional feature to retain original tread geometry for reference purposes.

## Understanding Summary

### Requirements
1. **UI Enhancement**: Add a checkbox in the Basic Parameters tab: "Keep original tread geometry for reference"
2. **Geometry Modification**: Create widened treads by:
   - Offsetting both radial edge lines outward by 0.375"
   - Extending inner and outer arcs to meet the offset lines
3. **Conditional Retention**: When checkbox is enabled, keep original tread geometry alongside the new widened geometry
4. **Focus on Bottom Tread**: Initial implementation and testing on the bottom-most tread only
5. **No Rotation Changes**: Strictly geometric widening, no angular modifications
6. **Universal Application**: Must work with all valid user inputs

### Key Technical Insights from Documentation Review

From the **AI Problem-Solving Methodology**, the implementation will focus on:
- Physical construction requirements vs. mathematical complexity
- Thinking like a fabricator - how will this actually be built and used
- Avoiding over-engineering when simple solutions work

From the **AutoCAD Polyline COM Solution**, the implementation will leverage:
- The dual-method approach for polyline creation (AddLightWeightPolyline vs AddPolyline)
- Proper VARIANT parameter marshalling for COM interface
- The importance of 2D vs 3D coordinate formatting

## Current Tread Module Analysis

The existing tread module creates sector treads using:
- Three entities: two radial lines + one arc
- Region creation from these entities
- Extrusion to create 3D solid
- Proper layer management (TREADS layer)

## Implementation Plan

### Phase 1: UI Enhancement
1. **Update Configuration Schema** (`core/config_manager.py`)
   - Add `keep_original_tread_geometry` boolean parameter to basic_parameters section
   - Update validation logic to include new parameter

2. **Update Default Configuration** (`config/default_config.json`)
   - Add `"keep_original_tread_geometry": false` to basic_parameters

### Phase 2: Tread Module Enhancement  
3. **Modify Tread Module** (`modules/tread_module.py`)
   - Update `_create_sector_tread` method to support widened geometry creation
   - Implement offset calculation logic (0.375" outward offset for both radial lines)
   - Add arc extension logic to meet offset radial lines
   - Implement conditional geometry retention based on user setting
   - Focus initial implementation on bottom tread (index 0) for testing

### Phase 3: Geometry Creation Logic
4. **Implement Widening Algorithm**:
   - Calculate offset radial lines (leading and trailing edges offset outward by 0.375")
   - Determine new arc endpoints where extended arcs meet offset radial lines
   - Create widened sector using AutoCAD polyline/region approach
   - Apply proper layer management for both original and widened geometry

### Phase 4: AutoCAD Integration
5. **Leverage Existing COM Interface**:
   - Use established `create_line`, `create_arc`, `create_region`, `create_extruded_solid` methods
   - Apply dual-method polyline approach from documentation
   - Ensure proper VARIANT parameter marshalling for reliability

### Phase 5: Testing & Validation
6. **Test Implementation**:
   - Validate with mock AutoCAD interface first
   - Test with real AutoCAD using Git Bash environment
   - Verify geometry creation with various stair configurations
   - Confirm original geometry retention when option enabled

## Technical Approach

### Core Principles
- **No Rotation Changes**: Maintain existing angular positioning logic
- **Physical Construction Focus**: Simple offset calculation rather than complex mathematical modeling  
- **Fabricator Perspective**: Create geometry that serves practical construction needs
- **Universal Compatibility**: Work with all valid user input combinations

### Geometry Calculation Details
1. **Original Tread Geometry**:
   - Inner arc: radius = center_pole_diameter / 2
   - Outer arc: radius = outside_diameter / 2
   - Leading radial line: from inner arc to outer arc at start_angle
   - Trailing radial line: from inner arc to outer arc at end_angle

2. **Widened Tread Geometry**:
   - Same inner and outer radii
   - Leading radial line offset outward by 0.375" (parallel to original)
   - Trailing radial line offset outward by 0.375" (parallel to original)
   - Arcs extended to meet new radial line endpoints

3. **Offset Calculation**:
   - Calculate perpendicular offset vectors for radial lines
   - Apply 0.375" offset distance in outward direction
   - Compute intersection points with extended arcs

## Success Criteria

- Bottom tread successfully widened by 0.375" on both radial edges
- Original tread geometry conditionally retained based on user setting
- No impact on existing tread functionality
- Clean, maintainable code following established patterns
- Robust error handling and validation
- Compatibility with both mock and real AutoCAD interfaces

## Implementation Notes

### File Structure
- Primary changes in `modules/tread_module.py`
- Configuration updates in `core/config_manager.py` and `config/default_config.json`
- Testing files to be created as needed

### Testing Strategy
- Start with mock AutoCAD interface for rapid iteration
- Progress to real AutoCAD testing in Git Bash environment
- Test with various stair configurations and parameter combinations
- Validate both original and widened geometry creation

### Future Extensions
- Apply logic to all treads after successful bottom tread implementation
- Consider additional offset distance options
- Potential integration with other stair components (posts, pickets, etc.)