# Dependency Guide

## Critical Dependencies Analysis

Based on comprehensive analysis of all component modules, here are the exact dependencies required for successful integration.

## Python Dependencies

### Required Packages (requirements.txt)
```txt
pywin32>=227        # For real AutoCAD COM interface
jsonschema>=4.0.0   # For configuration validation
```

### Installation
```bash
pip install -r requirements.txt
```

## File Dependencies

### Essential Core Files (Required by ALL modules)
```
core/
├── base_component.py      # Abstract base class for all modules
├── autocad_interface.py   # AutoCAD COM wrapper with mock support
├── exceptions.py          # Custom exception classes
├── logging_config.py      # Logging configuration 
└── config_manager.py      # Configuration management with JSON schema
```

### Component Modules (Use as needed)
```
modules/
├── center_pole_module.py  # Most independent - only needs base_component.py
├── tread_module.py        # Standard dependencies
├── landing_module.py      # Standard dependencies  
├── post_module.py         # Standard dependencies
├── picket_module.py       # Standard dependencies
└── handrail_module.py     # Standard dependencies + import path bug
```

### Utility Functions (Optional)
```
utils/
├── corrected_handrail_functions.py  # Required for handrail module
├── helix_calculation_corrected.py   # Optional geometry utilities
└── helix_corrected_implementation.py # Optional geometry utilities
```

## Dependency Matrix

| Module | base_component | autocad_interface | exceptions | logging_config | config_manager | utils |
|--------|---------------|-------------------|------------|----------------|----------------|-------|
| CenterPoleModule | ✅ Required | ✅ Required | ✅ Required | ✅ Required | - | - |
| TreadModule | ✅ Required | ✅ Required | ✅ Required | ✅ Required | - | - |
| LandingModule | ✅ Required | ✅ Required | ✅ Required | ✅ Required | - | - |
| PostModule | ✅ Required | ✅ Required | ✅ Required | ✅ Required | - | - |
| PicketModule | ✅ Required | ✅ Required | ✅ Required | ✅ Required | - | - |
| HandrailModule | ✅ Required | ✅ Required | ✅ Required | ✅ Required | - | ⚠️ Import Bug |

## Import Path Structure

### Correct Import Pattern
All modules use relative imports assuming this structure:
```python
from core.base_component import BaseStairComponent
from core.autocad_interface import AutoCADInterface  
```

### Your Integration Structure Must Be:
```
your_project/
├── core/           # Core infrastructure files
├── modules/        # Component modules
├── utils/          # Optional utilities
└── your_app.py     # Your application
```

## Critical Import Bug in HandrailModule

**Issue:** `handrail_module.py` uses incorrect import paths:
```python
# INCORRECT (current):
from src.core.base_component import BaseStairComponent

# CORRECT (should be):
from core.base_component import BaseStairComponent
```

**Solution:** Either fix the imports or ensure `src/` is in your Python path.

## External Dependencies

### For Real AutoCAD Integration
- **AutoCAD 2025** running with COM enabled
- **pywin32** package installed
- **Windows COM support** active

### For Mock/Testing Mode
- Set `AUTOCAD_MOCK_MODE=true` environment variable
- No AutoCAD required

## Configuration Dependencies

### Required Configuration Structure
```python
config = {
    "basic_parameters": {
        "center_pole_diameter": float,
        "overall_height": float,
        "outside_diameter": float, 
        "total_rotation": float,
        "is_clockwise": bool
    }
}
```

### Optional Component Configurations
- `post_configuration` - for PostModule
- `handrail_configuration` - for HandrailModule  
- `picket_configuration` - for PicketModule

Use `ConfigManager` class for automatic validation and defaults.

## Runtime Dependencies

### Memory Requirements
- **Base usage:** ~50MB RAM per component
- **Full stair:** ~300MB RAM total
- **Peak usage:** ~500MB during generation

### Performance Dependencies  
- **Windows COM performance** affects real AutoCAD speed
- **Mock mode:** ~0.1 seconds per component
- **Real AutoCAD:** ~5-15 seconds per component

## Integration Checklist

### ✅ Minimum Integration Requirements
- [ ] Copy all 5 core files to `core/` directory
- [ ] Copy desired module files to `modules/` directory  
- [ ] Install pywin32 and jsonschema packages
- [ ] Fix handrail import paths OR add `src/` to Python path
- [ ] Ensure project structure matches expected import paths

### ✅ Recommended Integration
- [ ] Copy example configurations from `config/` directory
- [ ] Copy utility functions for enhanced functionality
- [ ] Implement error handling patterns from examples
- [ ] Use ConfigManager for configuration validation
- [ ] Test with mock mode before real AutoCAD integration

### ✅ Production Integration
- [ ] Verify AutoCAD 2025 compatibility
- [ ] Implement proper cleanup on errors
- [ ] Add logging for debugging
- [ ] Test IBC compliance validation
- [ ] Performance test with complex stairs

## Troubleshooting Common Issues

### Import Errors
```python
# Add your project root to Python path
import sys
sys.path.append('/path/to/your/project')
```

### AutoCAD Connection Issues
```python
# Test with mock mode first
import os
os.environ['AUTOCAD_MOCK_MODE'] = 'true'
```

### Configuration Validation Errors
```python
from core.config_manager import ConfigManager
config_manager = ConfigManager()
is_valid, errors = config_manager.validate_config(your_config)
```

## Minimal Working Example

```python
# minimal_integration.py
import sys
import os

# Ensure imports work
sys.path.append(os.path.dirname(__file__))

# Mock mode for testing
os.environ['AUTOCAD_MOCK_MODE'] = 'true'

from core.config_manager import ConfigManager
from core.autocad_interface import AutoCADInterface
from modules.center_pole_module import CenterPoleModule

# Basic configuration
config_manager = ConfigManager()
config = config_manager.get_default_config()

# Create AutoCAD interface and component
autocad = AutoCADInterface()
center_pole = CenterPoleModule()

# Generate geometry
if center_pole.validate_parameters(config):
    success = center_pole.generate_geometry(autocad, config)
    print(f"Center pole generation: {'success' if success else 'failed'}")
```

This represents the absolute minimum integration for a single component.