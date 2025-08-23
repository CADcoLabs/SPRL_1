# Spiral Staircase Generator - Qwen Code Context

## Project Overview

This is a Python application for generating complete spiral staircases in AutoCAD with IBC (International Building Code) compliance. It features a modular architecture with six independent component modules and a master orchestrator pattern.

**Key Technologies:**
- Python 3
- AutoCAD 2025 COM API (pywin32)
- Tkinter for UI
- JSON for configuration

**Core Architecture:**
```
User Interface → Configuration Manager → Orchestrator → Component Modules → AutoCAD Interface → AutoCAD 2025
```

## Zero-Dependency Modular Design

The most critical architectural principle is **zero cross-module dependencies**:
- Each of the 6 modules operates completely independently
- Modules can fail without affecting others
- Each module validates its own parameters and handles its own cleanup
- The Orchestrator coordinates but doesn't share data between modules
- This design is a HARD REQUIREMENT and must never be compromised

## Component Modules

1. **CenterPoleModule** - Creates central support cylinder
2. **TreadModule** - Generates spiral stair treads with sector geometry
3. **LandingModule** - Creates top/mid landings
4. **PostModule** - Generates structural posts (for horizontal pickets)
5. **PicketModule** - Creates vertical/horizontal pickets with IBC spacing validation
6. **HandrailModule** - Generates spiral handrails using helix geometry

## Development Rules

1. **Never place Python files in root directory**
2. **Never delete files - move to DELETED/ folder instead**
3. **All modules must inherit from BaseStairComponent**
4. **All modules must validate parameters and handle cleanup**
5. **Mock mode must work without AutoCAD installation**
6. **ALL CHANGES MUST BE THOROUGHLY TESTED**

## Building and Running

### Production Launch (Recommended)
```bash
ui/launch_spiral_stair_ui.bat
```

### Development with AutoCAD (Requires Git Bash)
```bash
cd ui && python launch_ui_real_autocad.py
```

### Mock Mode Development (Any Shell)
```bash
AUTOCAD_MOCK_MODE=true cd ui && python launch_ui_real_autocad.py
```

## File Structure

- `core/` - Core system components (orchestrator, base classes, AutoCAD interface)
- `modules/` - Individual component modules
- `ui/` - Tkinter user interface
- `config/` - Configuration files and schemas
- `requirements.txt` - Runtime dependencies (pywin32, jsonschema)

## AutoCAD Interface

The system provides two AutoCAD interface implementations:
1. **RealAutoCADInterface** - Communicates with AutoCAD 2025 via COM
2. **MockAutoCADInterface** - Simulates AutoCAD operations for testing

Switch between modes using the `AUTOCAD_MOCK_MODE` environment variable.

## Configuration System

Uses JSON configuration with schema validation. Key configuration areas:
- Basic parameters (dimensions, rotation, direction)
- Component enable/disable settings
- Material and style specifications
- IBC compliance settings
- Advanced settings (mock mode, timeouts)

## IBC Compliance

Built-in validation for key building code requirements:
- Riser height (≤ 9.5")
- Tread depth at walkline (≥ 6.75")
- Picket spacing (≤ 4" sphere rule)
- Mid-landing requirement for stairs > 151" height
- Handrail height (34-38" above tread)

## Critical Solutions

1. **Handrail Helix**: Fixed COM error by implementing proper AddHelix() method
2. **Picket IBC Compliance**: Fixed spacing calculation (edge-to-edge, not center-to-center)
3. **AutoCAD COM Access**: Resolved by using Git Bash environment (Windows CMD fails)

## Component Status

- ✅ CenterPoleModule - Ready
- ✅ TreadModule - Ready, IBC compliant
- ✅ LandingModule - Ready
- ✅ PostModule - Ready
- ✅ PicketModule - Ready, IBC spacing validation
- ✅ HandrailModule - Ready (check import paths)