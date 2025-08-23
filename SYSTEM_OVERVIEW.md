# Spiral Staircase Generator System Overview

The Spiral Staircase Generator is a modular Python system that generates complete spiral staircases in AutoCAD while enforcing IBC building code compliance. It replaces a legacy VBA system with a modern, extensible architecture.

## Key Features

1. **Modular Architecture**: Six independent modules (Center Pole, Treads, Landings, Pickets, Handrails, Posts) with zero cross-module dependencies
2. **IBC Compliance**: Automatic building code validation throughout
3. **AutoCAD Integration**: Works with both real AutoCAD (COM interface) and mock mode for testing
4. **Configuration-Driven**: JSON-based configuration with schema validation
5. **Performance**: Generates complete staircases in under 0.3 seconds

## Core Components

- **Core Infrastructure** (`core/`):
  - `base_component.py`: Abstract base class defining component interface
  - `config_manager.py`: JSON configuration with schema validation
  - `autocad_interface.py`: AutoCAD COM wrapper with mock mode support
  - `orchestrator.py`: Master coordinator for component generation

- **Component Modules** (`modules/`):
  - `center_pole_module.py`
  - `tread_module.py`
  - `landing_module.py`
  - `picket_module.py`
  - `handrail_module.py`
  - `post_module.py`

- **User Interface** (`ui/`):
  - `main_ui.py`: Main Tkinter-based UI application
  - `launch_spiral_stair_ui.bat`: Production launcher

## How to Run the Application

### Production Mode (Recommended)
Double-click the batch file:
```
ui/launch_spiral_stair_ui.bat
```

This launcher:
1. Automatically detects Git Bash installation
2. Sets up the proper shell environment for AutoCAD COM access
3. Launches the UI with full AutoCAD integration

### Development Mode with Mock AutoCAD
For development without AutoCAD:
```bash
set AUTOCAD_MOCK_MODE=true
cd ui
python launch_ui_real_autocad.py
```

### Development Mode with Real AutoCAD
For development with real AutoCAD (requires Git Bash):
```bash
cd ui
python launch_ui_real_autocad.py
```

## Recent Breakthroughs

1. **Handrail Helix Implementation**: Successfully resolved COM error -2147352567 by implementing proper AutoCAD `AddHelix()` method
2. **Picket IBC Compliance**: Fixed spacing calculation to use edge-to-edge measurement instead of center-to-center, properly complying with the 4" sphere rule
3. **AutoCAD COM Access**: Resolved connection issues by using Git Bash environment instead of Windows CMD

## Testing

Run tests with mock mode:
```bash
set AUTOCAD_MOCK_MODE=true
cd tests
python -m pytest
```

The system includes comprehensive tests for:
- IBC edge spacing compliance
- Handrail helix geometry
- Module independence
- Performance benchmarks
- UI integration

All 37 tests are currently passing, and the system is production-ready.