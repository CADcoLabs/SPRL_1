# Project Context Guide for AI Assistants

This file provides essential context for AI assistants to quickly understand and work with this codebase.

## Project Overview
- **Name**: Modular Spiral Stair Creator System
- **Purpose**: Generate complete spiral staircases in AutoCAD with IBC compliance
- **Status**: PRODUCTION READY (main branch)
- **Technology**: Python 3, AutoCAD 2025 COM API, Tkinter UI

## Key Facts to Remember
1. This replaces a legacy VBA system with modern modular Python architecture
2. All 6 modules operate independently with zero cross-module dependencies
3. Zero-cross-module dependencies is a HARD REQUIREMENT - no exceptions
4. Performance requirement: <30 seconds (currently achieves 0.15 seconds)
5. IBC building code compliance is enforced throughout
6. Two modes: Real AutoCAD (COM) and Mock Mode (for testing)

## Critical Architecture
```
User Interface → Configuration Manager → Orchestrator → Component Modules → AutoCAD Interface → AutoCAD 2025
```

- **6 Independent Modules**: center_pole, tread, landing, picket, handrail, post
- **Master Orchestrator Pattern**: Modules execute in dependency-free order
- **Configuration-Driven**: JSON schema validation with defaults
- **Mock Support**: Set AUTOCAD_MOCK_MODE=true for testing without AutoCAD

## Essential File Locations
- `core/base_component.py` - Base class for all modules
- `core/autocad_interface.py` - AutoCAD COM wrapper (Real/Mock)
- `core/orchestrator.py` - Master coordinator
- `core/config_manager.py` - Configuration system
- `modules/*.py` - Individual component modules
- `ui/main_ui.py` - Main user interface
- `ui/launch_spiral_stair_ui.bat` - Production launcher (uses Git Bash)

## Recent Critical Solutions
1. **Handrail Helix**: Fixed COM error by implementing proper AddHelix() method
2. **Picket IBC Compliance**: Fixed spacing calculation (edge-to-edge, not center-to-center)
3. **AutoCAD COM Access**: Resolved by using Git Bash environment (Windows CMD fails)

## Development Rules
- NEVER place Python files in root directory
- NEVER delete files - move to DELETED/ folder instead
- All modules must inherit from BaseStairComponent
- All modules must validate parameters and handle cleanup
- Mock mode must work without AutoCAD installation
- ALL CHANGES MUST BE THOROUGHLY TESTED - lying is regression, truth and honesty keep us moving forward

## Common Commands
```bash
# Production launch (recommended)
ui/launch_spiral_stair_ui.bat

# Development with AutoCAD (requires Git Bash)
cd ui && python launch_ui_real_autocad.py

# Mock mode development (any shell)
AUTOCAD_MOCK_MODE=true cd ui && python launch_ui_real_autocad.py
```

## Component Status
- ✅ CenterPoleModule - Ready
- ✅ TreadModule - Ready, IBC compliant
- ✅ LandingModule - Ready
- ✅ PostModule - Ready
- ✅ PicketModule - Ready, IBC spacing validation
- ✅ HandrailModule - Ready (check import paths)

## Zero Dependency Rule
This is the most critical architectural requirement:
1. Each module operates completely independently
2. No inter-module communication or data sharing
3. Modules can fail without affecting others
4. Each module validates its own parameters
5. Each module handles its own cleanup
6. Orchestrator coordinates but doesn't share data between modules

When adding new functionality, always maintain this independence.

## Critical Architectural Principle Enforcement

The AI assistant must reject any test that undermines the core architectural principle of modular independence. Passing a test by compromising the design's intended structure is not an acceptable outcome. The codebase's integrity and its adherence to a modular design are to be prioritized over passing tests that are fundamentally incompatible with this approach.

In different words, tests that are designed to defeat the architectural principles of this project, specifically the emphasis on truly independent and modular construction, are deemed inappropriate. The AI assistant is instructed to prioritize the preservation of the intended design over passing tests that would necessitate its deconstruction. Modifying the codebase to pass such a test is counter-productive and will not be considered a valid measure of success, as it would require rebuilding the original, intended design which would subsequently fail the same test.