# User Story: Residential Designer
## Creating a Custom Spiral Stair for a Loft Conversion

### User Profile
**Name**: Sarah Chen  
**Role**: Residential Interior Designer  
**Experience**: 8 years in residential design, familiar with AutoCAD but new to spiral stair design  
**Project**: Converting a garage into a loft apartment with space constraints

---

## The Challenge

Sarah is working on a loft conversion project where the client wants to add a second floor to their converted garage. The space is tight - only 7 feet by 8 feet available for the stairway, and they need to reach a height of 10 feet. The client wants an aluminum spiral stair that looks modern but meets all building codes.

**Key Requirements:**
- **Space constraint**: Must fit in 7' x 8' area
- **Height**: 10 feet (120 inches) floor to floor
- **Style**: Modern aluminum with clean lines
- **Code compliance**: Must meet local IBC requirements
- **Budget conscious**: Needs accurate material estimates

---

## Using the Spiral Stair Creator

### Step 1: Initial Setup
Sarah opens AutoCAD 2025 and launches the Spiral Stair Creator. The tkinter interface opens with a clean, tabbed design.

```
"This is so much better than trying to calculate everything manually or 
using the old VBA script that only gave me basic geometry."
```

### Step 2: Basic Parameters Configuration
On the **Basic Parameters** tab, Sarah enters:
- **Center Pole Diameter**: 5.0 inches (from dropdown of available sizes)
- **Overall Height**: 120.0 inches
- **Outside Diameter**: 66.0 inches (to fit in the 7x8 space with clearance)
- **Total Rotation**: 270 degrees (3/4 turn to optimize space)
- **Direction**: Clockwise ✓

As she enters values, the interface shows real-time validation:
```
✓ Walkline width: 7.2" (exceeds 6.75" minimum)
✓ Walk space: 28.5" (exceeds 26" minimum)  
✓ Configuration meets IBC requirements
```

### Step 3: Picket Configuration
Moving to the **Pickets** tab, Sarah configures:
- **Enable Pickets**: ✓ Yes
- **Spacing**: 3.5 inches (safely under 4" IBC requirement)
- **Style**: Vertical
- **Material**: Aluminum
- **Height Ratio**: 0.85 (85% of tread-to-handrail distance)

The interface shows: `✓ Picket spacing complies with 4-inch sphere rule`

### Step 4: Handrail Configuration
On the **Handrail** tab:
- **Enable Handrail**: ✓ Yes
- **Height Above Tread**: 36.0 inches
- **Diameter**: 1.5 inches
- **Material**: Aluminum
- **Continuous**: ✓ Yes
- **End Treatment**: Cap

### Step 5: Posts Configuration
**Posts** tab settings:
- **Enable Posts**: ✓ Yes
- **Spacing**: Every 4 treads
- **Post Diameter**: 2.0 inches
- **Material**: Aluminum
- **Base Plates**: ✓ Enabled, 6" square

### Step 6: Advanced Options
In **Advanced** tab, Sarah:
- Confirms **IBC Enforcement**: ✓ Enabled
- Sets **Regional Code**: IBC_2021
- Enables **Layer Organization** for clean CAD file structure

---

## Generation Process

### Step 7: Preview and Validate
Sarah clicks **Preview** and sees a summary:
```
Spiral Stair Summary:
- 13 treads + top landing
- Riser height: 9.23" (under 9.5" maximum)
- Walkline width: 7.2"
- Total rotation: 270°
- Estimated materials: 145 lbs aluminum
```

All validation checks pass with green checkmarks.

### Step 8: Generation
Sarah clicks **Generate Stair**. The progress bar shows:
```
Progress: ████████░░ 80% - Generating handrail...
Status: Creating continuous spiral handrail...
```

### Step 9: Results
In 25 seconds, the complete spiral stair appears in AutoCAD:
- **Center pole**: Clean aluminum cylinder
- **13 textured treads**: Properly spaced with nosing
- **Pickets**: Evenly spaced vertical balusters
- **Handrail**: Continuous spiral following the geometry
- **4 posts**: At strategic locations with base plates
- **Summary table**: Added to drawing with specifications

---

## Post-Generation Workflow

### Step 10: Client Presentation
Sarah uses AutoCAD's visual styles to create a realistic rendering for the client presentation. The organized layer structure makes it easy to control visibility of different components.

### Step 11: Design Iteration
The client asks: *"Could we add one more tread to make the steps a bit shorter?"*

Sarah uses the enhanced **Tread Module**:
1. Selects the tread module in the interface
2. Clicks **Add Tread** and specifies position
3. The system recalculates all geometry automatically
4. New configuration: 14 treads, 8.57" riser height

```
"This is amazing! In the old system, I would have had to regenerate 
everything from scratch. This just updated the affected components."
```

### Step 12: Configuration Management
Sarah saves the final configuration as `LoftProject_SpiralStair_v2.json` for:
- **Future reference**: Easy to recreate if needed
- **Documentation**: Attached to project files
- **Variations**: Base for similar projects

---

## Value Delivered

### Design Efficiency
- **Time saved**: 3 hours vs manual calculation and drawing
- **Accuracy**: Perfect IBC compliance automatically verified
- **Iterations**: Quick design changes without starting over
- **Professional output**: Clean, organized CAD geometry

### Client Benefits
- **Code compliance**: Automatic IBC verification provides confidence
- **Visualization**: Complete 3D model for better understanding
- **Accurate costing**: Precise material takeoffs for budgeting
- **Documentation**: Professional drawings for permit submission

### Business Impact
- **Faster turnaround**: More projects per week
- **Reduced errors**: Automated compliance checking
- **Professional quality**: Consistent, high-quality deliverables
- **Client satisfaction**: Quick iterations based on feedback

---

## Sarah's Feedback

> *"This tool has completely transformed how I approach spiral stair projects. Before, I would avoid them because of the complexity and time required. Now I can confidently propose spiral stairs knowing I can deliver accurate, code-compliant designs quickly."*

> *"The ability to add or remove treads after generation is a game-changer. Clients always want to see options, and this makes iteration so easy."*

> *"Having all the missing components - pickets, handrails, posts - generated automatically saves me hours of manual drafting. The old VBA script was good, but this is in a completely different league."*

---

## Configuration File (Saved)

```json
{
  "metadata": {
    "project_name": "Loft Conversion Spiral Stair",
    "created_by": "Sarah Chen",
    "description": "Aluminum spiral stair for garage loft conversion"
  },
  "basic_parameters": {
    "center_pole_diameter": 5.0,
    "overall_height": 120.0,
    "outside_diameter": 66.0,
    "total_rotation": 270.0,
    "is_clockwise": true
  },
  "picket_configuration": {
    "enabled": true,
    "spacing_inches": 3.5,
    "style": "vertical",
    "material": "aluminum"
  },
  "handrail_configuration": {
    "enabled": true,
    "height_above_tread": 36.0,
    "diameter": 1.5,
    "material": "aluminum",
    "end_treatment": "cap"
  },
  "post_configuration": {
    "enabled": true,
    "spacing_treads": 4,
    "post_diameter": 2.0,
    "material": "aluminum"
  }
}
```

This user story demonstrates the complete workflow from initial design challenge through final delivery, showing how the modular system addresses real-world design needs while providing the missing functionality from the original VBA script.