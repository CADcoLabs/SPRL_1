# Spiral Stair Component Integration Guide

## Overview

This package contains 6 production-ready spiral stair component modules that can be integrated into any Python AutoCAD application. Each module maintains full functionality exactly as designed in the original 1NewSpiral system.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Basic Integration
```python
from core.config_manager import ConfigManager
from modules.center_pole_module import CenterPoleModule
from core.autocad_interface import AutoCADInterface

# Initialize configuration
config_manager = ConfigManager()
config = config_manager.get_default_config()

# Initialize AutoCAD interface
autocad = AutoCADInterface()

# Create and use a component
center_pole = CenterPoleModule()
if center_pole.validate_parameters(config):
    success = center_pole.generate_geometry(autocad, config)
```

## Component Modules

### Available Components
1. **CenterPoleModule** - Central support pole
2. **TreadModule** - Stair treads/steps 
3. **LandingModule** - Mid and top landings
4. **PostModule** - Structural support posts
5. **HandrailModule** - Continuous spiral handrails
6. **PicketModule** - Vertical/horizontal balusters

### Component Independence
Each module is completely independent and can be used separately. No dependencies between component modules - mix and match as needed.

## Required Configuration

All modules require a configuration dictionary with at minimum:

```python
config = {
    "basic_parameters": {
        "center_pole_diameter": 5.563,
        "overall_height": 144.0,
        "outside_diameter": 72.0,
        "total_rotation": 450.0,
        "is_clockwise": True
    }
}
```

Additional components may require their specific configuration sections (see MODULE_API_REFERENCE.md).

## Architecture Pattern

All modules follow the **BaseStairComponent** pattern:

```python
class YourModule(BaseStairComponent):
    def validate_parameters(self, config) -> bool
    def generate_geometry(self, autocad_interface, config) -> bool
    def get_required_parameters(self) -> List[str]
    def cleanup(self, autocad_interface) -> None
```

## AutoCAD Integration

### Real AutoCAD
```python
from core.autocad_interface import AutoCADInterface
autocad = AutoCADInterface()  # Connects to running AutoCAD
```

### Mock Mode (Testing)
```python
import os
os.environ['AUTOCAD_MOCK_MODE'] = 'true'
from core.autocad_interface import AutoCADInterface
autocad = AutoCADInterface()  # Uses mock interface
```

## Error Handling

Each module includes robust error handling:

```python
try:
    if module.validate_parameters(config):
        success = module.generate_geometry(autocad, config)
        if not success:
            print(f"Generation failed: {module.last_error}")
except Exception as e:
    module.cleanup(autocad)  # Automatic cleanup
    print(f"Error: {e}")
```

## IBC Compliance

Components automatically enforce IBC building code requirements:
- Walkline width ≥ 6.75" (12" from center pole edge)
- Walk space ≥ 26" (clear space at/below handrail) 
- Picket spacing ≤ 4" (sphere rule)
- Handrail height 34"-38" above tread nosing
- Mid-landing required for heights > 151"

## Integration Examples

See `/examples/` directory for complete working examples:
- `simple_stair.py` - Basic 4-component stair
- `full_featured_stair.py` - All components with configuration
- `custom_ui_example.py` - Integration with your UI framework

## Troubleshooting

### Import Errors
Ensure all core files are in your Python path:
```python
import sys
sys.path.append('/path/to/New_UI')
```

### AutoCAD Connection Issues
- Verify AutoCAD 2025 is running
- Install pywin32: `pip install pywin32`
- Use mock mode for development: `AUTOCAD_MOCK_MODE=true`

### Configuration Validation Errors
Use ConfigManager for automatic validation:
```python
config_manager = ConfigManager()
is_valid, errors = config_manager.validate_config(config)
if not is_valid:
    print("Configuration errors:", errors)
```

## File Structure Required

Your integration must maintain this structure:
```
your_project/
├── modules/          # Component modules  
├── core/            # Base infrastructure
├── utils/           # Utility functions (optional)
├── requirements.txt # Dependencies
└── your_ui.py       # Your custom UI
```

## Support

Each component is fully self-contained with comprehensive error messages and debugging information. Check `module.get_status()` and `module.last_error` for detailed diagnostics.