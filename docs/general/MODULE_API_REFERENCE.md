# Module API Reference

## BaseStairComponent Interface

All modules inherit from `BaseStairComponent` with these required methods:

### Abstract Methods
```python
def validate_parameters(self, config: Dict[str, Any]) -> bool
def generate_geometry(self, autocad_interface, config: Dict[str, Any]) -> bool  
def get_required_parameters(self) -> List[str]
```

### Inherited Methods  
```python
def cleanup(self, autocad_interface) -> None
def get_status(self) -> Dict[str, Any]
```

---

## CenterPoleModule

**Purpose:** Creates central support pole for spiral staircase

### Required Parameters
- `basic_parameters.center_pole_diameter` (1.0-24.0 inches)
- `basic_parameters.overall_height` (60.0-240.0 inches)

### Usage
```python
from modules.center_pole_module import CenterPoleModule

pole = CenterPoleModule()
if pole.validate_parameters(config):
    success = pole.generate_geometry(autocad, config)
```

### Generated Geometry
- 3D solid cylinder at origin (0,0,0)
- Bottom at Z=0, top at Z=overall_height
- Color: 251 (VBA compatible)
- Positioned with center at Z=height/2

### Validation Rules
- Diameter must be > 0 and ≤ 24 inches
- Height must be > 0 and ≤ 240 inches

---

## TreadModule

**Purpose:** Creates individual stair treads/steps

### Required Parameters  
- `basic_parameters.center_pole_diameter`
- `basic_parameters.overall_height`
- `basic_parameters.outside_diameter` (36.0-120.0 inches)
- `basic_parameters.total_rotation` (90.0-720.0 degrees)
- `basic_parameters.is_clockwise` (boolean)

### Usage
```python
from modules.tread_module import TreadModule

treads = TreadModule()
if treads.validate_parameters(config):
    success = treads.generate_geometry(autocad, config)
```

### Generated Geometry
- Individual tread plates positioned at calculated angles
- Thickness: 1.5 inches (standard)
- Width: (outside_diameter - center_pole_diameter) / 2
- Automatic IBC compliance checking

### IBC Compliance
- Walkline width ≥ 6.75" at 12" from center pole edge
- Automatic parameter adjustment suggestions if non-compliant

---

## LandingModule

**Purpose:** Creates mid-landings and top landing platforms

### Required Parameters
- All basic_parameters (same as TreadModule)

### Usage
```python
from modules.landing_module import LandingModule

landings = LandingModule()
if landings.validate_parameters(config):
    success = landings.generate_geometry(autocad, config)
```

### Generated Geometry
- Mid-landing automatically created if height > 151" (IBC requirement)
- Top landing at full height
- Platform dimensions based on stair diameter
- Thickness: 1.5 inches (standard)

### Auto-Generation Rules
- Mid-landing: height > 151 inches
- Landing width: matches tread width
- Positioned at appropriate angles for access

---

## PostModule  

**Purpose:** Creates structural support posts connecting treads

### Required Parameters
- All basic_parameters
- `post_configuration.enabled` (boolean)
- `post_configuration.spacing` (1-3: every tread, every other, every third)
- `post_configuration.diameter` (0.5-6.0 inches)
- `post_configuration.material` ("steel", "aluminum", "wood", "composite")
- `post_configuration.position` ("outer_edge", "mid_tread", "inner_edge")

### Usage
```python
from modules.post_module import PostModule

posts = PostModule()
config["post_configuration"] = {
    "enabled": True,
    "spacing": 2,  # Every other tread
    "diameter": 2.5,
    "material": "steel", 
    "position": "outer_edge"
}
if posts.validate_parameters(config):
    success = posts.generate_geometry(autocad, config)
```

### Generated Geometry
- Cylindrical posts connecting consecutive treads
- Height varies based on tread positions
- Material affects color/properties
- Position determines connection point on tread

---

## HandrailModule

**Purpose:** Creates continuous spiral handrails with IBC compliance

### Required Parameters
- All basic_parameters
- `handrail_configuration.enabled` (boolean)
- `handrail_configuration.height_above_tread` (30.0-42.0 inches, IBC: 34-38)
- `handrail_configuration.diameter` (1.25-2.5 inches)
- `handrail_configuration.material` ("steel", "aluminum", "wood", "composite")
- `handrail_configuration.continuous` (boolean)
- `handrail_configuration.end_treatment` ("cap", "return", "extended")
- `handrail_configuration.brackets.enabled` (boolean)
- `handrail_configuration.brackets.spacing_inches` (12.0-48.0)
- `handrail_configuration.brackets.bracket_type` ("post_mount", "wall_mount", "under_mount")

### Usage
```python
from modules.handrail_module import HandrailModule

handrail = HandrailModule()
config["handrail_configuration"] = {
    "enabled": True,
    "height_above_tread": 36.0,
    "diameter": 1.75,
    "material": "steel",
    "continuous": True,
    "end_treatment": "cap",
    "brackets": {
        "enabled": True,
        "spacing_inches": 24.0,
        "bracket_type": "post_mount"
    }
}
if handrail.validate_parameters(config):
    success = handrail.generate_geometry(autocad, config)
```

### Generated Geometry  
- Continuous 3D spiral following tread path
- Constant height above each tread nosing
- Mounting brackets at specified intervals
- End treatments (caps, returns, extensions)

### IBC Compliance
- Height: 34"-38" above tread nosing (validated)
- Continuous gripping surface
- Proper end treatments for safety

**Note:** Current version has import path issues that may need correction for your integration.

---

## PicketModule

**Purpose:** Creates vertical/horizontal balusters between treads and handrail

### Required Parameters
- All basic_parameters  
- `picket_configuration.enabled` (boolean)
- `picket_configuration.spacing_inches` (1.0-4.0, IBC max: 4.0)
- `picket_configuration.style` ("vertical", "horizontal")
- `picket_configuration.material` ("aluminum", "steel", "wood", "composite")
- `picket_configuration.diameter` (0.375-2.0 inches)

### Usage
```python
from modules.picket_module import PicketModule

pickets = PicketModule()
config["picket_configuration"] = {
    "enabled": True,
    "spacing_inches": 3.5,
    "style": "vertical", 
    "material": "aluminum",
    "diameter": 0.75
}
if pickets.validate_parameters(config):
    success = pickets.generate_geometry(autocad, config)
```

### Generated Geometry
- Individual picket elements between tread and handrail
- Spacing follows IBC 4" sphere rule
- Orientation based on style (vertical/horizontal)
- Material affects visual properties

### IBC Compliance
- Maximum 4" spacing (sphere rule)
- Proper connection to tread and handrail structures

---

## Error Handling Pattern

All modules follow consistent error handling:

```python
module = AnyModule()
try:
    # Always validate first
    if module.validate_parameters(config):
        success = module.generate_geometry(autocad, config)
        
        if not success:
            print(f"Generation failed: {module.last_error}")
            
    # Check status anytime
    status = module.get_status()
    print(f"Module: {status['name']}, Generated: {status['is_generated']}")
    
except Exception as e:
    # Automatic cleanup on errors
    module.cleanup(autocad)
    print(f"Critical error: {e}")
```

## Configuration Validation

Use ConfigManager for comprehensive validation:

```python
from core.config_manager import ConfigManager

config_manager = ConfigManager() 
is_valid, errors = config_manager.validate_config(config)

if not is_valid:
    for field, error in errors.items():
        print(f"Config error in {field}: {error}")
```

## Geometry Information

Get detailed geometry info for debugging:

```python
# After successful generation
geometry_info = module.get_geometry_info()  
print(f"Generated: {geometry_info['type']}")
print(f"Parameters: {geometry_info}")
```

This method is available on all modules and provides component-specific geometry details.