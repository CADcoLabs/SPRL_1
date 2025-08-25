# User Story: Commercial Architect
## Designing Emergency Egress Stairs for a Manufacturing Facility

### User Profile
**Name**: Michael Rodriguez  
**Role**: Commercial Architect / Project Manager  
**Experience**: 15 years in commercial architecture, specialized in industrial facilities  
**Project**: 3-story manufacturing facility requiring multiple emergency egress spiral stairs  
**Firm**: Rodriguez & Associates Architects

---

## The Challenge

Michael is designing a new manufacturing facility with a complex layout requiring multiple emergency egress routes. The building has three levels with equipment platforms at various heights, and traditional straight stairs won't fit in the available spaces. He needs to design four different spiral stairs, each with specific requirements for capacity, materials, and code compliance.

**Project Requirements:**
- **Multiple stairs**: 4 spiral stairs with different specifications
- **Heavy-duty construction**: Steel construction for industrial use
- **High capacity**: Wide stairs for emergency egress
- **Strict compliance**: Multiple code requirements (IBC, OSHA, local amendments)
- **Fast delivery**: Tight project timeline
- **Cost optimization**: Need accurate material quantities for bidding

---

## Multi-Stair Design Challenge

### Stair Specifications Needed:
1. **Main Egress Stair**: 18-foot height, 10-foot diameter, steel
2. **Platform Access**: 12-foot height, 8-foot diameter, steel
3. **Mezzanine Stair**: 15-foot height, 9-foot diameter, steel with special coatings
4. **Equipment Access**: 24-foot height, 12-foot diameter, heavy-duty steel

---

## Using the Spiral Stair Creator

### Workflow Overview
Michael decides to create all four stairs systematically, saving configurations for reuse and documentation.

### Stair 1: Main Egress Stair

#### Step 1: Open New Project
Michael launches the Spiral Stair Creator and immediately appreciates the professional interface.

```
"Finally, a tool that looks like it belongs in a commercial workflow. 
The tabbed interface is much more sophisticated than the old VBA form."
```

#### Step 2: Configure Main Egress Stair
**Basic Parameters:**
- **Center Pole Diameter**: 8.0 inches (heavy-duty option)
- **Overall Height**: 216.0 inches (18 feet)
- **Outside Diameter**: 120.0 inches (10 feet)
- **Total Rotation**: 450 degrees (1.25 turns for optimal egress flow)
- **Direction**: Counterclockwise (standard for egress)

**Validation Results:**
```
✓ Walkline width: 12.8" (exceeds 6.75" minimum)
✓ Walk space: 38.2" (exceeds 26" minimum)
⚠ Height exceeds 151" - midlanding required per R311.7.3
```

The system automatically prompts for midlanding placement. Michael selects tread 12 for optimal positioning.

#### Step 3: Heavy-Duty Configuration
**Treads:**
- **Material**: Steel
- **Thickness**: 0.375 inches (heavier gauge)
- **Surface**: Diamond plate for slip resistance

**Pickets:**
- **Spacing**: 3.0 inches (stricter than 4" for safety)
- **Material**: Steel
- **Connection**: Welded construction
- **Horizontal Rails**: Enabled (2 rails for additional safety)

**Handrail:**
- **Height**: 42.0 inches (industrial standard, above residential 36")
- **Diameter**: 2.0 inches (larger grip for gloved hands)
- **Material**: Steel with powder coating

**Posts:**
- **Spacing**: Every 3 treads (closer spacing for heavy-duty)
- **Diameter**: 3.0 inches
- **Base Plates**: 8" x 8" x 0.75" thick

#### Step 4: Compliance Validation
**Advanced Settings:**
- **Regional Code**: IBC_2021 + OSHA 1910.25
- **Accessibility**: ADA compliant
- **Load Requirements**: Commercial heavy-duty

The system validates:
```
✓ IBC compliance verified
✓ OSHA industrial stair requirements met
✓ ADA accessibility standards satisfied
⚠ Custom inspection recommended for 450° rotation
```

#### Step 5: Generate and Save
Michael generates the first stair and saves the configuration as `MainEgress_18ft_Steel.json`.

**Generation Results:**
- **23 treads + midlanding + top landing**
- **Riser height**: 9.4 inches
- **Total steel**: 2,847 lbs
- **Generation time**: 38 seconds

---

### Stair 2: Platform Access (Batch Configuration)

#### Step 6: Load and Modify Template
Michael loads the main egress configuration and modifies it:

**Changes:**
- **Height**: 144 inches (12 feet)
- **Outside Diameter**: 96 inches (8 feet)
- **Rotation**: 360 degrees (full turn)
- **Post Spacing**: Every 4 treads (lighter duty)

The system recalculates automatically:
```
✓ No midlanding required (under 151")
✓ 16 treads total
✓ Riser height: 9.0"
✓ Estimated steel: 1,654 lbs
```

#### Step 7: Quick Generation
Michael generates the second stair and saves as `PlatformAccess_12ft_Steel.json`.

---

### Stair 3: Mezzanine Stair (Special Coatings)

#### Step 8: Environmental Requirements
For the mezzanine stair, Michael adds special requirements:

**Material Specifications:**
- **Base Material**: Steel
- **Coating**: Galvanized + powder coat
- **Environment**: Chemical resistant

**Enhanced Configuration:**
- **Picket Style**: Crossed pattern for aesthetics
- **Handrail Treatment**: Special grip texture
- **Drainage**: Perforated treads for washdown

Michael uses the **custom_requirements** section:
```json
"environmental_specs": {
  "coating_system": "galvanized_powder_coat",
  "chemical_resistance": "industrial_grade",
  "drainage_required": true
}
```

---

### Stair 4: Equipment Access (Maximum Size)

#### Step 9: Heavy-Duty Configuration
The largest stair requires maximum specifications:

**Basic Parameters:**
- **Center Pole**: 12.75 inches (largest available)
- **Height**: 288 inches (24 feet)
- **Diameter**: 144 inches (12 feet)
- **Rotation**: 540 degrees (1.5 turns)

**Advanced Features:**
- **Double midlandings**: Required due to height
- **Extra-wide treads**: Custom width specification
- **Reinforced posts**: Every 2 treads
- **Safety features**: Extra handrails at different heights

---

## Batch Operations and Optimization

### Step 10: Configuration Management
Michael organizes all configurations:

```
Project Configurations:
├── MainEgress_18ft_Steel.json
├── PlatformAccess_12ft_Steel.json  
├── Mezzanine_15ft_Coated.json
└── EquipmentAccess_24ft_HeavyDuty.json
```

### Step 11: Batch Material Calculation
Using the configuration files, Michael generates a consolidated material report:

```
TOTAL PROJECT MATERIALS:
- Steel (structural): 8,947 lbs
- Galvanizing: 1,234 sq ft
- Powder coating: 967 sq ft
- Base plates: 16 ea (various sizes)
- Fasteners: 1,247 pieces
- Estimated cost: $47,320
```

### Step 12: Drawing Organization
The system creates organized CAD layers:
```
SPIRAL_STAIR_01_CENTER_POLE
SPIRAL_STAIR_01_TREADS
SPIRAL_STAIR_01_PICKETS
SPIRAL_STAIR_01_HANDRAILS
SPIRAL_STAIR_01_POSTS
[Repeat for stairs 02, 03, 04]
```

---

## Design Iteration and Optimization

### Step 13: Client Feedback Integration
The client requests modifications:

> *"Can we reduce the rotation on Stair 2 to save space and add anti-slip coating to all treads?"*

**Quick Modifications:**
1. **Stair 2**: Load configuration, change rotation from 360° to 270°
2. **All stairs**: Add surface treatment specifications
3. **Regenerate**: Only affected components update

**Results:**
- **Space saved**: 18 inches on platform stair
- **Cost impact**: +$2,340 for anti-slip treatments
- **Code compliance**: Still maintained
- **Time to modify**: 8 minutes vs hours with manual recalculation

### Step 14: Value Engineering
Michael uses the **tread modification** feature to optimize:

**Stair 1 Optimization:**
- **Remove 1 tread**: Reduces material cost
- **Adjust riser height**: 9.8" (still under 9.5" limit with approval)
- **Material savings**: 127 lbs steel, $643 cost reduction

---

## Documentation and Deliverables

### Step 15: Professional Deliverables
The system generates:

**Technical Drawings:**
- **Plans**: Top view of each stair with dimensions
- **Elevations**: Side views showing height relationships
- **Details**: Connection details and specifications
- **3D Views**: Isometric views for clarity

**Specifications:**
- **Material lists**: Detailed quantities by component
- **Installation notes**: Assembly sequence and requirements
- **Code compliance**: Documentation for permit submission
- **Maintenance guide**: Long-term care instructions

### Step 16: Contractor Package
Michael exports complete packages for bidding:

```
Manufacturing_Facility_Spiral_Stairs/
├── Drawings/
│   ├── S-101_Stair_Plans.dwg
│   ├── S-102_Stair_Elevations.dwg
│   └── S-103_Details.dwg
├── Specifications/
│   ├── Material_List.xlsx
│   ├── Installation_Guide.pdf
│   └── Code_Compliance.pdf
├── Configurations/
│   ├── All 4 JSON configuration files
│   └── Master_Project_Config.json
└── Reports/
    ├── Cost_Estimate.pdf
    └── Compliance_Report.pdf
```

---

## Project Outcomes

### Efficiency Gains
- **Design Time**: 6 hours vs 20 hours traditional method
- **Accuracy**: Zero calculation errors, automatic code compliance
- **Iterations**: 3 rounds of client changes handled quickly
- **Documentation**: Professional package generated automatically

### Cost Optimization
- **Material accuracy**: ±2% vs ±15% manual estimation
- **Value engineering**: $2,847 saved through optimization
- **Bid confidence**: Contractors submit tighter bids due to accuracy

### Client Satisfaction
- **Visual communication**: 3D models help client understanding
- **Confidence**: Automated code compliance verification
- **Timeline**: Project delivered 2 weeks ahead of schedule

---

## Michael's Professional Assessment

> *"This tool has revolutionized our approach to spiral stair design. For commercial projects with multiple stairs, the configuration management and batch processing capabilities are invaluable. The ability to maintain code compliance while optimizing for cost and space is exactly what we needed."*

> *"The transition from that basic VBA script to this comprehensive system is like moving from a calculator to a full CAD system. Every missing component we used to draw manually is now generated automatically with proper connections and specifications."*

> *"Our clients are impressed with the speed and accuracy of iterations. Being able to show them exactly how changes affect cost and compliance in real-time has improved our design process significantly."*

---

## Configuration Example (Equipment Access Stair)

```json
{
  "metadata": {
    "project_name": "Manufacturing Facility - Equipment Access Stair",
    "created_by": "Michael Rodriguez, AIA",
    "client": "Industrial Manufacturing Corp",
    "drawing_number": "S-104"
  },
  "basic_parameters": {
    "center_pole_diameter": 12.75,
    "overall_height": 288.0,
    "outside_diameter": 144.0,
    "total_rotation": 540.0,
    "is_clockwise": false
  },
  "tread_configuration": {
    "thickness": 0.375,
    "material": "steel",
    "surface_finish": "diamond_plate"
  },
  "picket_configuration": {
    "spacing_inches": 3.0,
    "material": "steel",
    "horizontal_rails": {
      "enabled": true,
      "rail_count": 2
    }
  },
  "handrail_configuration": {
    "height_above_tread": 42.0,
    "diameter": 2.0,
    "material": "steel"
  },
  "post_configuration": {
    "spacing_treads": 2,
    "post_diameter": 3.0,
    "base_plate": {
      "size_inches": 10.0,
      "thickness": 0.75
    }
  },
  "compliance_settings": {
    "regional_code": "IBC_2021",
    "accessibility_compliance": "ADA",
    "custom_requirements": {
      "load_rating": "commercial_heavy_duty",
      "osha_compliance": true
    }
  }
}
```

This user story demonstrates the power of the modular system for complex commercial projects, showing how the enhanced capabilities handle real-world architectural challenges that the original VBA script couldn't address.