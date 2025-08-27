# Spiral Staircase Generator - Knowledge Organization

## Overview

This document organizes key knowledge about the Spiral Staircase Generator system, providing a structured reference for understanding the system's components, interfaces, and architectural principles. This serves as a comprehensive knowledge base for developers working with the system.

## System Architecture

### Master Orchestrator Pattern

The system follows a Master Orchestrator Pattern with these key characteristics:

1. **Component Independence**: Each of the 6 modules operates completely independently
2. **Zero Cross-Module Dependencies**: Modules can fail without affecting others
3. **Self-Validation**: Each module validates its own parameters
4. **Self-Cleanup**: Each module handles its own cleanup
5. **Centralized Coordination**: Orchestrator coordinates execution but doesn't share data between modules

### Data Flow

```
User Interface → Configuration Manager → Orchestrator → Component Modules → AutoCAD Interface → AutoCAD
```

### Core Components

1. **BaseStairComponent**: Abstract base class for all modules
2. **MasterStairOrchestrator**: Coordinates all component generation
3. **ConfigManager**: Manages configuration with schema validation
4. **AutoCADInterface**: Dual implementation (Real/Mock) for AutoCAD operations

## Component Module Reference

### Module Interfaces

All modules inherit from `BaseStairComponent` and implement:

```python
class BaseStairComponent(ABC):
    def __init__(self, name: str)
    @abstractmethod
    def validate_parameters(self, config: Dict[str, Any]) -> bool
    @abstractmethod
    def generate_geometry(self, autocad_interface, config: Dict[str, Any]) -> bool
    @abstractmethod
    def get_required_parameters(self) -> List[str]
    def cleanup(self, autocad_interface) -> None
    def get_status(self) -> Dict[str, Any]
```

### Module Registry

The orchestrator registers components with:
- Name for display
- Component class to instantiate
- Dependencies (though currently unused due to zero-dependency rule)
- Configuration key to check if enabled
- Required status for successful generation

### Generation Order

Structurally logical generation order:
1. Center Pole (Foundation)
2. Treads (Structure)
3. Landings (Platforms)
4. Posts (Supports - only if horizontal pickets enabled)
5. Handrails (Safety)
6. Vertical Pickets (Finishing - vertical balusters)
7. Horizontal Pickets (Finishing - horizontal rails)

## AutoCAD Interface Reference

### Interface Abstraction

```python
class AutoCADInterface(ABC):
    @abstractmethod
    def connect(self) -> bool
    @abstractmethod
    def disconnect(self) -> None
    @abstractmethod
    def is_connected(self) -> bool
    @abstractmethod
    def create_circle(self, center: tuple, radius: float) -> Any
    @abstractmethod
    def create_line(self, start_point: tuple, end_point: tuple) -> Any
    @abstractmethod
    def create_polyline(self, points: list) -> Any
    @abstractmethod
    def create_arc(self, center: tuple, radius: float, start_angle: float, end_angle: float) -> Any
    @abstractmethod
    def create_region(self, objects: list) -> Any
    @abstractmethod
    def create_extruded_solid(self, profile: Any, height: float, taper_angle: float = 0) -> Any
    @abstractmethod
    def create_helix(self, center: tuple, base_radius: float, top_radius: float, height: float, turns: float, axis_vector: tuple = (0, 0, 1)) -> Any
    @abstractmethod
    def add_text(self, text: str, position: tuple, height: float = 0.125) -> Any
    @abstractmethod
    def add_dimension(self, point1: tuple, point2: tuple, dimension_line_point: tuple, text: str = None) -> Any
    @abstractmethod
    def create_layer(self, layer_name: str, color: int = 7) -> Any
    @abstractmethod
    def set_active_layer(self, layer_name: str) -> None
    @abstractmethod
    def select_entities_by_layer(self, layer_name: str) -> Any
    @abstractmethod
    def send_command(self, command: str) -> None
```

### Standard Layers

The system creates these standard layers with predefined colors:
- `CENTERPOLE`: Color 252
- `TREADS`: Color 254
- `LANDINGS`: Color 143
- `HANDRAILS`: Color 130
- `PICKETS`: Color 253
- `POSTS`: Color 6 (Magenta)

### Real vs Mock Implementation

#### Real AutoCAD Interface
- Communicates with AutoCAD 2025 via COM
- Uses `pywin32` for COM interface
- Implements proper parameter marshalling with VARIANT arrays
- Supports all AutoCAD geometric entities

#### Mock AutoCAD Interface
- Simulates AutoCAD operations for testing without AutoCAD installation
- Maintains entity tracking for validation
- Supports all geometric operations with simplified implementations
- Provides consistent interface for development and testing

## Configuration Reference

### Configuration Sections

1. **basic_parameters**: Core dimensions and settings
2. **compliance_settings**: IBC compliance options
3. **component_settings**: Enable/disable individual components
4. **post_configuration**: Structural post settings
5. **handrail_configuration**: Handrail specifications
6. **vertical_picket_configuration**: Vertical baluster settings
7. **horizontal_picket_configuration**: Horizontal rail settings
8. **advanced_settings**: Development and testing options

### Key Configuration Parameters

#### Basic Parameters
- `center_pole_diameter`: Center pole diameter in inches
- `overall_height`: Total height of spiral stair in inches
- `outside_diameter`: Outside diameter of spiral stair in inches
- `total_rotation`: Total rotation in degrees
- `is_clockwise`: Clockwise rotation direction
- `mid_landing_enabled`: Enable mid-landing for stairs > 151 inches
- `mid_landing_tread_index`: Zero-based index of tread to become mid-landing
- `keep_original_tread_geometry`: Keep original tread geometry for reference

#### Compliance Settings
- `ibc_compliance_enabled`: Enable IBC building code compliance validation
- `educational_mode`: Educational mode allows non-compliant configurations
- `regional_code`: Building code standard to use for compliance

#### Component Settings
- `center_pole_enabled`: Enable center pole generation
- `treads_enabled`: Enable tread generation
- `landings_enabled`: Enable landing generation

### Parameter Validation Rules

#### Numerical Ranges
- Center pole diameter: 1.0-24.0 inches
- Overall height: 60.0-240.0 inches
- Outside diameter: 36.0-120.0 inches
- Total rotation: 90.0-720.0 degrees
- Handrail height: 30.0-42.0 inches
- Picket spacing: 1.0-4.0 inches (IBC max 4")
- Post diameter: 0.5-6.0 inches
- Bracket spacing: 12.0-48.0 inches

#### Enumerated Values
- Materials: steel, aluminum, wood, composite
- Picket positions: outer, inner, middle
- Post positions: outer_edge, mid_tread, inner_edge
- Rail profiles: square_1x1, rectangular_1x2, round_1, custom
- Level distributions: even, concentrated_lower, concentrated_upper, custom
- Mounting systems: bracket_mount, weld_mount, clamp_mount
- End treatments: cap, return, extended
- Regional codes: IBC_2021, IBC_2018, IBC_2015, Custom

## IBC Compliance Reference

### Key Requirements Implemented

1. **Riser Height**: ≤ 9.5 inches
   - Implementation: Ceiling(height / 9.5) calculation
   - Validation: Error if > 9.5", warning if > 9.0"

2. **Tread Depth at Walkline**: ≥ 6.75 inches
   - Implementation: Walkline radius = (center_pole_dia / 2) + 12
   - Calculation: Walkline width = walkline_radius * tread_angle_radians
   - Validation: Error if < 6.75", warning if < 7.5"

3. **Picket Spacing**: 4" sphere rule (edge-to-edge spacing ≤ 4")
   - Implementation: Edge-to-edge = center-to-center - diameter
   - Validation: Error if spacing > 4"

4. **Mid-Landing Requirement**: For stairs > 151 inches height
   - Implementation: If height > 151, mid_landing_index = round(num_treads / 2) - 1
   - Validation: Error if height > 151 and no mid-landing

5. **Handrail Height**: 34"-38" above tread
   - Implementation: Configurable height_above_tread parameter
   - Validation: Error if < 34" or > 38"

6. **Guard Height**: Minimum 42" for horizontal pickets
   - Implementation: Fixed guard_height = 42.0
   - Validation: Ensure rail system meets this requirement

### Compliance Validation Process

Each module can validate its own compliance requirements:
- TreadModule: Riser height, tread depth, mid-landing
- VerticalPicketModule: 4" sphere rule spacing
- HandrailModule: Height requirements
- HorizontalPicketModule: 4" sphere rule, guard height
- LandingModule: Mid-landing implementation

## Geometric Calculations Reference

### Tread Calculations

1. **Number of Treads**: `ceil(overall_height / 9.5)`
2. **Riser Height**: `overall_height / num_treads`
3. **Tread Angle**: 
   - With mid-landing: `(total_rotation - 90) / (num_treads - 2)`
   - Without mid-landing: `total_rotation / (num_treads - 1)`
4. **Walkline Width**: `walkline_radius * abs(tread_angle_radians)`
   - Walkline radius = `(center_pole_dia / 2) + 12`

### Handrail Calculations

1. **Handrail Radius**: `(outside_dia - handrail_diameter) / 2`
2. **Helix Turns**: `total_rotation / 337.5`
3. **Helix Height**: `overall_height`
4. **Total Handrail Length**: `sqrt((2π * radius * turns)² + height²)`

### Picket Spacing Calculations

1. **Edge-to-Edge Spacing**: `center_to_center_distance - picket_diameter`
2. **Optimal Division**: Find number of divisions that keeps spacing ≤ 4"
3. **Positioning**: Place pickets at calculated angular positions

## Error Handling Patterns

### Exception Hierarchy

The system uses a custom exception hierarchy:
- `SpiralStairException`: Base exception for all system errors
- `ComponentNotFoundError`: When a required component is missing
- `GenerationError`: When geometry generation fails
- `ConfigurationError`: When configuration validation fails
- `AutoCADConnectionError`: When AutoCAD connection fails
- `GeometryError`: When geometric calculations fail

### Error Handling Strategies

1. **Validation First**: Validate parameters before processing
2. **Graceful Degradation**: Continue with partial functionality when possible
3. **Detailed Error Messages**: Provide context and suggested fixes
4. **Cleanup on Failure**: Ensure partial geometry is cleaned up
5. **Logging**: Comprehensive logging for debugging

## Development Guidelines

### Zero Dependency Rule

The most critical architectural principle:
1. Each module operates completely independently
2. No inter-module communication or data sharing
3. Modules can fail without affecting others
4. Each module validates its own parameters
5. Each module handles its own cleanup
6. Orchestrator coordinates but doesn't share data between modules

### Code Organization Rules

1. **Never place Python files in root directory**
2. **Never delete files - move to DELETED/ folder instead**
3. **All modules must inherit from BaseStairComponent**
4. **All modules must validate parameters and handle cleanup**
5. **Mock mode must work without AutoCAD installation**
6. **ALL CHANGES MUST BE THOROUGHLY TESTED**

### Testing Requirements

1. **Mock Mode Compatibility**: All functionality must work in mock mode
2. **Parameter Validation**: All modules must validate their parameters
3. **IBC Compliance**: Verify compliance requirements are met
4. **Error Handling**: Test error conditions and recovery
5. **Edge Cases**: Test boundary values and unusual configurations

## Build and Execution

### Production Launch
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

## Performance Considerations

### Timing Constraints
- Target: <30 seconds for complete generation
- Current performance: ~0.15 seconds
- COM timing issues addressed with small delays between operations

### Optimization Strategies
1. **Minimize COM Calls**: Batch operations when possible
2. **Efficient Algorithms**: Use optimized geometric calculations
3. **Delay Management**: Small delays prevent COM timing issues
4. **Memory Management**: Clean up entities properly
5. **Layer Management**: Use standard layers for consistent coloring

## Future Enhancement Areas

### Potential Improvements
1. **Dimensioning Module**: Add automated dimensioning features
2. **Advanced Materials**: Support for more material properties
3. **Custom Profiles**: More complex geometric profiles
4. **Structural Analysis**: Integration with structural calculation engines
5. **Export Formats**: Support for additional CAD formats
6. **3D Printing**: Optimization for 3D printing applications

### Architectural Extensions
1. **Plugin System**: Allow third-party module integration
2. **Template System**: Predefined configuration templates
3. **Advanced Validation**: More sophisticated compliance checking
4. **Reporting Module**: Generation reports and documentation
5. **Collaboration Features**: Multi-user design capabilities

## Troubleshooting Guide

### Common Issues

1. **AutoCAD Connection Failures**
   - Solution: Use Git Bash environment (not Windows CMD)
   - Solution: Verify AutoCAD 2025 installation
   - Solution: Check COM security settings

2. **COM Timing Issues**
   - Solution: Add small delays between operations (0.01-0.25 seconds)
   - Solution: Verify AutoCAD is responsive

3. **Geometry Creation Failures**
   - Solution: Validate input parameters
   - Solution: Check coordinate system consistency
   - Solution: Verify layer management

4. **Configuration Validation Errors**
   - Solution: Check parameter ranges and types
   - Solution: Verify required parameters are present
   - Solution: Check for invalid enum values

### Debugging Techniques

1. **Enable Detailed Logging**: Set appropriate log levels
2. **Use Mock Mode**: Test without AutoCAD dependencies
3. **Parameter Isolation**: Test with minimal configurations
4. **Step-by-Step Execution**: Use orchestrator progress tracking
5. **Entity Inspection**: Examine created AutoCAD entities

## Documentation Standards

### Code Documentation
- Module-level docstrings explaining purpose and functionality
- Function-level docstrings with parameter and return value descriptions
- Inline comments for complex logic or calculations
- Type hints for all function parameters and return values

### Configuration Documentation
- Clear parameter descriptions in schema
- Range and constraint specifications
- Default value documentation
- Example values where appropriate

### User Documentation
- Installation and setup instructions
- Configuration guide with examples
- Component-specific usage information
- Troubleshooting and FAQ sections

## Conclusion

This knowledge organization provides a comprehensive reference for understanding and working with the Spiral Staircase Generator system. The modular architecture, combined with the configuration-driven approach and IBC compliance features, creates a robust platform for spiral staircase design. The zero-dependency principle ensures system stability and maintainability, while the dual AutoCAD interface supports both development and production environments.