# Vertical Picket Placement Specification for Spiral Stairs

## Document Purpose
This document outlines the standard process and calculations for correctly placing vertical pickets on spiral stair treads to ensure proper spacing, IBC compliance, and structural integrity.

## Overview
Vertical pickets on spiral stairs require precise positioning along each tread to maintain safety standards and aesthetic consistency. This specification details the step-by-step process for determining correct picket placement, spacing, and height calculations.

## Required Parameters
- **Center Pole Diameter**: Default 5.56"
- **Overall Height**: Default 144"
- **Outside Diameter**: Default 72"
- **Total Rotation**: Default 450°
- **Handrail Diameter**: Default 1.5"
- **Picket Size**: Default 0.75" × 0.75" (square)

## Step-by-Step Placement Process

### 1. Arc Creation and Offset
1. Create an arc along the outside radius of the tread
2. Offset the arc inward by **half the handrail diameter**
   - Formula: `offset_distance = handrail_diameter ÷ 2`
   - Example: 1.5" ÷ 2 = 0.75"
3. This offset arc becomes the path where pickets will be positioned

### 2. Arc Rotation for Clearance
1. Rotate the offset arc so its ends are positioned away from the tread's radial edges
2. The rotation distance is calculated as: **half the picket size**
   - Formula: `clearance_distance = picket_size ÷ 2`
   - Example: 0.75" ÷ 2 = 0.375"
3. This ensures pickets are centered and won't interfere with the next tread above

### 3. Picket Shape Creation
1. Create a square picket shape with dimensions matching the picket size
   - Default: 0.75" × 0.75" square
2. Place the picket shape on one end of the offset arc
3. Align it properly along the arc's path using geometric center alignment

### 4. Array Creation and IBC Compliance
1. Create a path array along the arc using the picket shape
2. **Initial Array Setup**:
   - Start with 4 pickets (creating 3 spaces between them)
   - Measure the spacing at the narrowest points between pickets
3. **IBC Compliance Check**:
   - Maximum allowed spacing: 4" (sphere test)
   - If spacing > 4", add additional pickets until compliance is achieved
4. **Example Process**:
   - 4 pickets = 3 spaces = 5.3313" spacing (NON-COMPLIANT)
   - 5 pickets = 4 spaces = 3.8130" spacing (COMPLIANT)

### 5. Final Picket Count Determination
1. **Important Note**: Each tread uses 4 actual pickets, not 5
2. The 5th picket in the calculation represents the tallest picket that extends to meet the handrail
3. The spacing calculation uses 5 positions to determine proper distribution
4. Only 4 pickets are actually placed on each tread

### 6. Variable Height Calculations
Each picket has a different height due to the helical handrail:
- Heights are measured from the tread surface to where the picket intersects the handrail helix
- **Example Heights**:
  - Shortest picket: 38.0684"
  - Second picket: 40.3177"
  - Third picket: 42.5663"
  - Tallest picket: 44.8161"

### 7. Final Processing
1. Explode the array to work with individual picket shapes
2. Extrude the picket shapes upward to their calculated heights
3. Slice each picket at the correct angle where it meets the handrail helix
4. Ensure clean intersections with both the tread below and handrail above

## Key Algorithm Requirements

### Formulas
1. **Offset Distance**: `handrail_diameter ÷ 2`
2. **Clearance Distance**: `picket_size ÷ 2`
3. **Maximum Spacing**: 4" (IBC requirement)
4. **Picket Height**: Variable, based on intersection with handrail helix

### Positioning Rules
1. Pickets must be positioned along the offset arc, not the outer edge
2. Each picket must be centered on its position point
3. Angular distribution must be even along the arc
4. Heights must be calculated individually for each picket position

### Compliance Requirements
1. No space between pickets may exceed 4" (sphere test)
2. Pickets must extend from tread surface to handrail
3. Pickets must not interfere with adjacent treads
4. All pickets must be structurally sound and properly aligned

## Implementation Notes

### For Algorithm Development
- The algorithm must calculate the offset arc position based on handrail diameter
- Angular positioning must account for the rotated arc clearance
- Height calculations must consider the helical nature of the handrail
- IBC compliance must be verified programmatically

### For Testing
- Verify spacing at the narrowest points between pickets
- Ensure all pickets clear adjacent tread boundaries
- Confirm proper intersection with handrail helix
- Test with various handrail diameters and picket sizes

## Future Considerations
- This specification applies only to vertical pickets
- Horizontal pickets require a different approach
- Different picket shapes (round, rectangular) may need adjustments
- Local building codes may have additional requirements beyond IBC

## Revision History
- **Version 1.0** (2025-08-20): Initial specification based on manual AutoCAD placement process