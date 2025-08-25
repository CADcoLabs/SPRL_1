# Module Specifications
## Individual Component Modules for Spiral Stair Creator

### Overview

This document provides detailed specifications for each component module in the modular spiral stair creator system. Each module follows the `BaseStairComponent` pattern and operates independently with clear interfaces and error handling.

---

## Base Module Pattern and Interface Contracts

### Abstract Base Class: `BaseStairComponent`

**File**: `src/modules/base_module.py`

```python
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any, Optional, Protocol
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

class ComponentState(Enum):
    """Component lifecycle states"""
    INITIALIZED = "initialized"
    VALIDATED = "validated"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CLEANED_UP = "cleaned_up"

class EntityType(Enum):
    """Supported entity types in AutoCAD"""
    CYLINDER = "cylinder"
    REGION = "region"
    EXTRUSION = "extrusion"
    SPLINE = "spline"
    LINE = "line"
    ARC = "arc"
    CIRCLE = "circle"
    POLYLINE = "polyline"

@dataclass
class EntityInfo:
    handle: str
    entity_type: EntityType
    properties: Dict[str, Any]
    created_timestamp: datetime = field(default_factory=datetime.now)
    layer_name: Optional[str] = None
    color_index: Optional[int] = None
    line_type: Optional[str] = None

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

@dataclass
class GenerationResult:
    success: bool
    messages: List[str] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    created_entity_count: int = 0

class IGeometryProvider(Protocol):
    """Interface for modules that provide geometry data to other modules"""
    
    def get_geometry_data(self) -> Dict[str, Any]:
        """Return geometry data for use by dependent modules"""
        ...
        
    def get_reference_points(self) -> List[Tuple[float, float, float]]:
        """Return key reference points for positioning dependent components"""
        ...
        
    def get_bounding_geometry(self) -> Dict[str, float]:
        """Return bounding box and key dimensions"""
        ...

class IGeometryConsumer(Protocol):
    """Interface for modules that depend on geometry from other modules"""
    
    def set_dependency_data(self, provider_name: str, geometry_data: Dict[str, Any]) -> bool:
        """Receive geometry data from a provider module"""
        ...
        
    def get_dependencies(self) -> List[str]:
        """Return list of required provider module names"""
        ...
        
    def validate_dependencies(self) -> Tuple[bool, List[str]]:
        """Validate that all required dependencies are satisfied"""
        ...

class BaseStairComponent(ABC):
    """Enhanced abstract base class with comprehensive interface contracts"""
    
    def __init__(self, config: 'StairConfiguration', autocad_interface: 'AutoCADInterface'):
        self.config = config
        self.acad = autocad_interface
        self.logger = logging.getLogger(self.__class__.__name__)
        self.generated_entities: List[EntityInfo] = []
        self.state = ComponentState.INITIALIZED
        self.component_id = str(uuid.uuid4())
        self.dependencies_satisfied = False
        self.performance_metrics: Dict[str, float] = {}
        
    # Core Abstract Methods
    @abstractmethod
    def validate_parameters(self) -> ValidationResult:
        """
        Validate component-specific parameters
        
        Returns:
            ValidationResult with detailed validation information
            
        Raises:
            ValueError: If configuration is fundamentally invalid
        """
        pass
        
    @abstractmethod
    def generate_geometry(self) -> GenerationResult:
        """
        Generate component geometry in AutoCAD
        
        Returns:
            GenerationResult with success status, messages, and created entities
            
        Raises:
            AutoCADException: If AutoCAD operations fail
            GeometryException: If geometric calculations fail
        """
        pass
        
    @abstractmethod
    def get_required_parameters(self) -> List[str]:
        """
        Return list of required configuration parameters
        
        Returns:
            List of parameter paths (e.g., 'basic_parameters.center_pole_diameter')
        """
        pass
        
    # Enhanced Interface Methods
    def get_component_info(self) -> Dict[str, Any]:
        """Return comprehensive component information"""
        return {
            'component_id': self.component_id,
            'class_name': self.__class__.__name__,
            'state': self.state.value,
            'entity_count': len(self.generated_entities),
            'dependencies_satisfied': self.dependencies_satisfied,
            'performance_metrics': self.performance_metrics,
            'last_updated': datetime.now().isoformat()
        }
    
    def pre_generation_checks(self) -> ValidationResult:
        """Perform comprehensive pre-generation validation"""
        result = ValidationResult(is_valid=True)
        
        # Parameter validation
        param_validation = self.validate_parameters()
        result.errors.extend(param_validation.errors)
        result.warnings.extend(param_validation.warnings)
        
        # AutoCAD connection check
        if not self.acad.is_connected():
            result.errors.append("AutoCAD interface not connected")
            
        # Dependency check (if applicable)
        if hasattr(self, 'validate_dependencies'):
            dep_valid, dep_errors = self.validate_dependencies()
            if not dep_valid:
                result.errors.extend(dep_errors)
                
        result.is_valid = len(result.errors) == 0
        return result
    
    def post_generation_validation(self) -> ValidationResult:
        """Validate results after generation"""
        result = ValidationResult(is_valid=True)
        
        if len(self.generated_entities) == 0:
            result.errors.append("No entities were created during generation")
            
        # Validate entity integrity
        for entity in self.generated_entities:
            if not self.acad.entity_exists(entity.handle):
                result.errors.append(f"Entity {entity.handle} not found in AutoCAD")
                
        result.is_valid = len(result.errors) == 0
        return result
    
    def cleanup_on_failure(self):
        """Enhanced cleanup with comprehensive error handling"""
        cleanup_errors = []
        
        for entity_info in self.generated_entities:
            try:
                if self.acad.entity_exists(entity_info.handle):
                    success = self.acad.delete_entity(entity_info.handle)
                    if not success:
                        cleanup_errors.append(f"Failed to delete entity {entity_info.handle}")
                        
            except Exception as e:
                cleanup_errors.append(f"Error deleting entity {entity_info.handle}: {str(e)}")
                
        self.generated_entities.clear()
        self.state = ComponentState.CLEANED_UP
        
        if cleanup_errors:
            self.logger.warning(f"Cleanup errors in {self.__class__.__name__}: {cleanup_errors}")
        
        return len(cleanup_errors) == 0
        
    def get_entity_handles(self) -> List[str]:
        """Return list of created entity handles"""
        return [e.handle for e in self.generated_entities]
        
    def add_entity(self, handle: str, entity_type: EntityType, properties: Dict[str, Any],
                   layer_name: str = None, color_index: int = None, line_type: str = None):
        """
        Track a newly created entity with comprehensive metadata
        
        Args:
            handle: AutoCAD entity handle
            entity_type: Type of entity created
            properties: Entity-specific properties
            layer_name: AutoCAD layer name
            color_index: AutoCAD color index
            line_type: AutoCAD line type
        """
        entity_info = EntityInfo(
            handle=handle,
            entity_type=entity_type,
            properties=properties,
            layer_name=layer_name,
            color_index=color_index,
            line_type=line_type
        )
        self.generated_entities.append(entity_info)
        
        self.logger.debug(f"Added entity: {entity_type.value} with handle {handle}")
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Return detailed generation statistics"""
        entity_counts = {}
        for entity in self.generated_entities:
            entity_type = entity.entity_type.value
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            
        return {
            'total_entities': len(self.generated_entities),
            'entity_counts_by_type': entity_counts,
            'generation_time': self.performance_metrics.get('generation_time', 0),
            'memory_used': self.performance_metrics.get('memory_used', 0),
            'autocad_calls': self.performance_metrics.get('autocad_calls', 0)
        }
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export component configuration for documentation/debugging"""
        return {
            'component_class': self.__class__.__name__,
            'component_id': self.component_id,
            'required_parameters': self.get_required_parameters(),
            'current_configuration': self._extract_relevant_config(),
            'validation_result': self.validate_parameters().__dict__,
            'performance_metrics': self.performance_metrics
        }
    
    def _extract_relevant_config(self) -> Dict[str, Any]:
        """Extract only the configuration parameters relevant to this component"""
        relevant_config = {}
        for param_path in self.get_required_parameters():
            try:
                value = self._get_config_value(param_path)
                relevant_config[param_path] = value
            except KeyError:
                relevant_config[param_path] = None
        return relevant_config
    
    def _get_config_value(self, param_path: str) -> Any:
        """Get configuration value using dot notation path"""
        parts = param_path.split('.')
        value = self.config
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                raise KeyError(f"Configuration parameter not found: {param_path}")
        return value

# Enhanced Module Registry with Dependency Resolution
class ModuleRegistry:
    """Registry managing module dependencies and execution order"""
    
    def __init__(self):
        self.modules: Dict[str, type] = {}
        self.providers: Dict[str, IGeometryProvider] = {}
        self.consumers: Dict[str, IGeometryConsumer] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.execution_order: List[str] = []
        
    def register_module(self, name: str, module_class: type, 
                       dependencies: List[str] = None) -> bool:
        """
        Register a module with dependency tracking
        
        Args:
            name: Module identifier
            module_class: Module class (must inherit from BaseStairComponent)
            dependencies: List of modules this module depends on
            
        Returns:
            bool: Registration success
        """
        if not issubclass(module_class, BaseStairComponent):
            raise ValueError(f"Module {name} must inherit from BaseStairComponent")
            
        self.modules[name] = module_class
        self.dependency_graph[name] = dependencies or []
        
        # Update execution order
        self.execution_order = self.calculate_execution_order()
        
        return True
    
    def calculate_execution_order(self) -> List[str]:
        """Calculate topological sort of modules based on dependencies"""
        from collections import deque
        
        # Kahn's algorithm for topological sorting
        in_degree = {node: 0 for node in self.dependency_graph}
        
        # Calculate in-degrees
        for node in self.dependency_graph:
            for dep in self.dependency_graph[node]:
                if dep in in_degree:
                    in_degree[node] += 1
        
        # Initialize queue with nodes having no dependencies
        queue = deque([node for node in in_degree if in_degree[node] == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            # Reduce in-degree for dependent nodes
            for node in self.dependency_graph:
                if current in self.dependency_graph[node]:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)
        
        # Check for circular dependencies
        if len(result) != len(self.dependency_graph):
            remaining = set(self.dependency_graph.keys()) - set(result)
            raise ValueError(f"Circular dependency detected involving: {remaining}")
            
        return result
    
    def validate_dependency_graph(self) -> Tuple[bool, List[str]]:
        """Check for circular dependencies and missing providers"""
        errors = []
        
        try:
            self.calculate_execution_order()
        except ValueError as e:
            errors.append(str(e))
            
        # Check for missing dependencies
        for module_name, deps in self.dependency_graph.items():
            for dep in deps:
                if dep not in self.modules:
                    errors.append(f"Module {module_name} depends on unregistered module {dep}")
        
        return len(errors) == 0, errors
    
    def get_execution_plan(self) -> List[Dict[str, Any]]:
        """Get detailed execution plan with dependency information"""
        plan = []
        for module_name in self.execution_order:
            plan.append({
                'module_name': module_name,
                'module_class': self.modules[module_name].__name__,
                'dependencies': self.dependency_graph[module_name],
                'execution_index': len(plan)
            })
        return plan
```

---

## Module 1: Center Pole Module

**File**: `src/modules/center_pole_module.py`

### Purpose
Creates the structural center pole cylinder based on user-specified diameter and overall height. Migrated from VBA `Module1.bas:278-290` with enhancements for validation, error handling, and geometry optimization.

### Configuration Parameters
```json
{
  "basic_parameters": {
    "center_pole_diameter": 5.0,    // inches, from available sizes
    "overall_height": 120.0         // inches, finished floor to finished floor
  }
}
```

### Interface Contract
- **Provides**: Center pole geometry and reference points for other modules
- **Dependencies**: None (base module)
- **AutoCAD Entities**: Creates single cylinder entity
- **Layer**: "SPIRAL_STAIR_POLE"

### Implementation
```python
import math
import time
import psutil
from typing import List, Dict, Any, Tuple
from ..base_module import BaseStairComponent, IGeometryProvider, ValidationResult, GenerationResult, EntityType

class CenterPoleModule(BaseStairComponent, IGeometryProvider):
    """
    Center pole module creating structural cylinder for spiral stair
    
    This module implements IGeometryProvider as it provides reference geometry
    for other modules like treads, pickets, and handrails.
    """
    
    # Available center pole diameters (inches)
    AVAILABLE_DIAMETERS = [3, 3.5, 4, 4.5, 5, 5.56, 6, 6.625, 8, 8.625, 10.75, 12.75]
    
    # Human-readable diameter labels
    DIAMETER_LABELS = [
        "3 (tube)", "3.5 (tube)", "4 (tube)", "4.5 (tube)", "5 (tube)", 
        "5.56 (5in. pipe)", "6 (tube)", "6.625 (6in. pipe)", "8 (tube)",
        "8.625 (8in. pipe)", "10.75 (10in. pipe)", "12.75 (12in. pipe)"
    ]
    
    # AutoCAD layer and display properties
    LAYER_NAME = "SPIRAL_STAIR_POLE"
    COLOR_INDEX = 1  # Red
    LINE_TYPE = "CONTINUOUS"
    
    # Performance and validation limits
    MIN_HEIGHT = 24.0    # Minimum practical height (2 feet)
    MAX_HEIGHT = 300.0   # Maximum practical height (25 feet)
    
    def __init__(self, config: 'StairConfiguration', autocad_interface: 'AutoCADInterface'):
        super().__init__(config, autocad_interface)
        
        # Component-specific properties
        self.pole_radius = 0.0
        self.pole_center = (0.0, 0.0, 0.0)  # Always at origin
        self.pole_handle = None
        
        # Performance tracking
        self.creation_start_time = 0.0
        self.memory_before = 0.0
        
    def validate_parameters(self) -> ValidationResult:
        """
        Validate center pole specific parameters
        
        Returns:
            ValidationResult with comprehensive validation information
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Get configuration values
            diameter = self._get_config_value('basic_parameters.center_pole_diameter')
            height = self._get_config_value('basic_parameters.overall_height')
            
        except KeyError as e:
            result.errors.append(f"Missing required parameter: {e}")
            result.is_valid = False
            return result
        
        # Validate diameter
        if diameter not in self.AVAILABLE_DIAMETERS:
            result.errors.append(
                f"Center pole diameter {diameter} is not available. "
                f"Available sizes: {self.AVAILABLE_DIAMETERS}"
            )
            
            # Suggest closest available diameter
            closest = min(self.AVAILABLE_DIAMETERS, key=lambda x: abs(x - diameter))
            result.suggestions.append(f"Consider using {closest} inches instead")
            
        # Validate height
        if height < self.MIN_HEIGHT:
            result.errors.append(
                f"Overall height {height} inches is below minimum {self.MIN_HEIGHT} inches"
            )
            
        elif height > self.MAX_HEIGHT:
            result.errors.append(
                f"Overall height {height} inches exceeds practical limit of {self.MAX_HEIGHT} inches"
            )
            
        # Warning for very tall poles
        if height > 180.0:  # 15 feet
            result.warnings.append(
                f"Height {height} inches may require structural analysis for wind loads"
            )
            
        # Warning for small diameter with tall height
        if diameter <= 4.0 and height > 120.0:
            result.warnings.append(
                f"Small diameter {diameter}\" with height {height}\" may have stability issues"
            )
            
        result.is_valid = len(result.errors) == 0
        return result
    
    def get_required_parameters(self) -> List[str]:
        """Return list of required configuration parameters"""
        return [
            'basic_parameters.center_pole_diameter',
            'basic_parameters.overall_height'
        ]
    
    def generate_geometry(self) -> GenerationResult:
        """
        Generate center pole cylinder in AutoCAD
        
        Returns:
            GenerationResult with creation status and performance metrics
        """
        self.state = ComponentState.GENERATING
        result = GenerationResult(success=False)
        
        # Performance tracking setup
        self.creation_start_time = time.time()
        process = psutil.Process()
        self.memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            # Get validated parameters
            validation = self.validate_parameters()
            if not validation.is_valid:
                result.messages.extend(validation.errors)
                self.state = ComponentState.FAILED
                return result
            
            diameter = self._get_config_value('basic_parameters.center_pole_diameter')
            height = self._get_config_value('basic_parameters.overall_height')
            
            self.pole_radius = diameter / 2.0
            
            # Create AutoCAD cylinder
            self.logger.info(f"Creating center pole: diameter={diameter}\", height={height}\"")
            
            # Ensure layer exists
            self._ensure_layer_exists()
            
            # Create cylinder at origin
            cylinder_handle = self.acad.create_cylinder(
                center=[0.0, 0.0, 0.0],
                radius=self.pole_radius,
                height=height
            )
            
            if not cylinder_handle:
                result.messages.append("Failed to create center pole cylinder in AutoCAD")
                self.state = ComponentState.FAILED
                return result
            
            # Set entity properties
            self._set_entity_properties(cylinder_handle)
            
            # Track the created entity
            self.add_entity(
                handle=cylinder_handle,
                entity_type=EntityType.CYLINDER,
                properties={
                    'center': [0.0, 0.0, 0.0],
                    'radius': self.pole_radius,
                    'height': height,
                    'diameter': diameter
                },
                layer_name=self.LAYER_NAME,
                color_index=self.COLOR_INDEX,
                line_type=self.LINE_TYPE
            )
            
            self.pole_handle = cylinder_handle
            
            # Calculate performance metrics
            self._calculate_performance_metrics()
            
            # Success result
            result.success = True
            result.messages.append(f"Center pole created successfully (handle: {cylinder_handle})")
            result.entities = {
                'pole_handle': cylinder_handle,
                'diameter': diameter,
                'height': height,
                'radius': self.pole_radius,
                'center': [0.0, 0.0, 0.0]
            }
            result.created_entity_count = 1
            result.performance_metrics = self.performance_metrics.copy()
            
            self.state = ComponentState.COMPLETED
            self.logger.info(f"Center pole generation completed in {self.performance_metrics.get('generation_time', 0):.3f}s")
            
        except Exception as e:
            result.messages.append(f"Exception during center pole creation: {str(e)}")
            self.logger.error(f"Center pole generation failed: {str(e)}", exc_info=True)
            self.state = ComponentState.FAILED
            
            # Cleanup on failure
            self.cleanup_on_failure()
        
        return result
    
    def _ensure_layer_exists(self):
        """Ensure the center pole layer exists in AutoCAD"""
        try:
            self.acad.create_layer(
                layer_name=self.LAYER_NAME,
                color_index=self.COLOR_INDEX,
                line_type=self.LINE_TYPE
            )
        except Exception as e:
            self.logger.warning(f"Could not create/verify layer {self.LAYER_NAME}: {e}")
    
    def _set_entity_properties(self, handle: str):
        """Set AutoCAD entity properties"""
        try:
            self.acad.set_entity_layer(handle, self.LAYER_NAME)
            self.acad.set_entity_color(handle, self.COLOR_INDEX)
            self.acad.set_entity_linetype(handle, self.LINE_TYPE)
        except Exception as e:
            self.logger.warning(f"Could not set entity properties for {handle}: {e}")
    
    def _calculate_performance_metrics(self):
        """Calculate and store performance metrics"""
        generation_time = time.time() - self.creation_start_time
        
        process = psutil.Process()
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - self.memory_before
        
        self.performance_metrics.update({
            'generation_time': generation_time,
            'memory_used': memory_used,
            'autocad_calls': 1,  # Single cylinder creation call
            'entities_created': 1
        })
    
    # IGeometryProvider Interface Implementation
    def get_geometry_data(self) -> Dict[str, Any]:
        """
        Return center pole geometry data for other modules
        
        Returns:
            Dict containing pole geometry information
        """
        if self.state != ComponentState.COMPLETED:
            raise RuntimeError("Center pole geometry not yet generated")
            
        return {
            'center_point': self.pole_center,
            'radius': self.pole_radius,
            'diameter': self.pole_radius * 2,
            'height': self._get_config_value('basic_parameters.overall_height'),
            'entity_handle': self.pole_handle,
            'bounding_cylinder': {
                'center': self.pole_center,
                'radius': self.pole_radius,
                'height': self._get_config_value('basic_parameters.overall_height')
            }
        }
    
    def get_reference_points(self) -> List[Tuple[float, float, float]]:
        """
        Return key reference points for positioning dependent components
        
        Returns:
            List of (x, y, z) reference points
        """
        if self.state != ComponentState.COMPLETED:
            return []
            
        height = self._get_config_value('basic_parameters.overall_height')
        
        return [
            (0.0, 0.0, 0.0),           # Base center
            (0.0, 0.0, height),        # Top center
            (self.pole_radius, 0.0, 0.0),     # Edge at 0°
            (0.0, self.pole_radius, 0.0),     # Edge at 90°
            (-self.pole_radius, 0.0, 0.0),    # Edge at 180°
            (0.0, -self.pole_radius, 0.0),    # Edge at 270°
        ]
    
    def get_bounding_geometry(self) -> Dict[str, float]:
        """
        Return bounding geometry information
        
        Returns:
            Dict with bounding box dimensions
        """
        if self.state != ComponentState.COMPLETED:
            return {}
            
        height = self._get_config_value('basic_parameters.overall_height')
        
        return {
            'min_x': -self.pole_radius,
            'max_x': self.pole_radius,
            'min_y': -self.pole_radius,
            'max_y': self.pole_radius,
            'min_z': 0.0,
            'max_z': height,
            'center_x': 0.0,
            'center_y': 0.0,
            'center_z': height / 2.0,
            'diameter': self.pole_radius * 2,
            'height': height
        }
    
    # Utility Methods
    def get_pole_radius(self) -> float:
        """
        Get center pole radius (convenience method)
        
        Returns:
            float: Pole radius in inches
        """
        if self.state == ComponentState.COMPLETED:
            return self.pole_radius
        else:
            diameter = self._get_config_value('basic_parameters.center_pole_diameter')
            return diameter / 2.0
    
    def get_diameter_label(self) -> str:
        """
        Get human-readable diameter label
        
        Returns:
            str: Diameter label (e.g., "5 (tube)")
        """
        diameter = self._get_config_value('basic_parameters.center_pole_diameter')
        
        try:
            index = self.AVAILABLE_DIAMETERS.index(diameter)
            return self.DIAMETER_LABELS[index]
        except ValueError:
            return f"{diameter} (custom)"
    
    def estimate_material_volume(self) -> float:
        """
        Estimate material volume for cost calculation
        
        Returns:
            float: Volume in cubic inches
        """
        diameter = self._get_config_value('basic_parameters.center_pole_diameter')
        height = self._get_config_value('basic_parameters.overall_height')
        
        radius = diameter / 2.0
        volume = math.pi * radius * radius * height
        
        return volume
    
    def get_structural_properties(self) -> Dict[str, float]:
        """
        Get structural properties for engineering calculations
        
        Returns:
            Dict with structural properties
        """
        diameter = self._get_config_value('basic_parameters.center_pole_diameter')
        radius = diameter / 2.0
        
        # Assuming hollow tube (typical for steel construction)
        # These are approximate values for standard steel tubing
        wall_thickness = 0.125  # 1/8 inch typical
        inner_radius = radius - wall_thickness
        
        # Moment of inertia for hollow circular section
        moment_of_inertia = (math.pi / 4) * (radius**4 - inner_radius**4)
        
        # Section modulus
        section_modulus = moment_of_inertia / radius
        
        # Cross-sectional area
        cross_sectional_area = math.pi * (radius**2 - inner_radius**2)
        
        return {
            'outer_diameter': diameter,
            'inner_diameter': inner_radius * 2,
            'wall_thickness': wall_thickness,
            'moment_of_inertia': moment_of_inertia,
            'section_modulus': section_modulus,
            'cross_sectional_area': cross_sectional_area,
            'radius_of_gyration': math.sqrt(moment_of_inertia / cross_sectional_area)
        }
```

---

## Module 2: Enhanced Tread Module

**File**: `src/modules/tread_module.py`

### Purpose
Creates spiral stair treads with enhanced functionality including individual tread addition/removal, custom modifications, and midlanding support. Migrated from VBA with significant enhancements for modularity and user control.

### Configuration Parameters
```json
{
  "basic_parameters": {
    "center_pole_diameter": 5.0,
    "overall_height": 120.0,
    "outside_diameter": 72.0,
    "total_rotation": 360.0,
    "is_clockwise": true
  },
  "tread_configuration": {
    "thickness": 0.25,
    "riser_height_max": 9.5,
    "material": "aluminum",
    "surface_finish": "diamond_plate",
    "custom_treads": {}
  }
}
```

### Interface Contract
- **Provides**: Tread geometry, positions, and reference points for pickets and handrails
- **Dependencies**: Center Pole Module (for radius and positioning)
- **AutoCAD Entities**: Creates multiple region and extrusion entities
- **Layer**: "SPIRAL_STAIR_TREADS"

### Implementation
```python
import math
import time
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from ..base_module import BaseStairComponent, IGeometryProvider, IGeometryConsumer
from ..base_module import ValidationResult, GenerationResult, EntityType

@dataclass
class TreadGeometry:
    """Individual tread geometry data"""
    index: int
    angle_start: float  # radians
    angle_end: float    # radians
    z_position: float   # height
    inner_radius: float
    outer_radius: float
    thickness: float
    is_midlanding: bool = False
    custom_properties: Dict[str, Any] = None
    
    def get_center_angle(self) -> float:
        """Get center angle of tread"""
        return (self.angle_start + self.angle_end) / 2.0
        
    def get_angular_width(self) -> float:
        """Get angular width in radians"""
        return abs(self.angle_end - self.angle_start)

class TreadModule(BaseStairComponent, IGeometryProvider, IGeometryConsumer):
    """
    Enhanced tread module with individual tread management
    
    Implements both IGeometryProvider (provides tread positions to other modules)
    and IGeometryConsumer (consumes center pole geometry for positioning)
    """
    
    # AutoCAD layer and display properties
    LAYER_NAME = "SPIRAL_STAIR_TREADS"
    COLOR_INDEX = 3  # Green
    LINE_TYPE = "CONTINUOUS"
    
    # IBC and practical limits
    MIN_TREAD_COUNT = 2
    MAX_TREAD_COUNT = 100
    MAX_RISER_HEIGHT = 9.5  # inches
    MIDLANDING_HEIGHT_THRESHOLD = 151.0  # inches
    MIDLANDING_ANGLE = math.pi / 2  # 90 degrees
    
    def __init__(self, config: 'StairConfiguration', autocad_interface: 'AutoCADInterface'):
        super().__init__(config, autocad_interface)
        
        # Tread-specific properties
        self.tread_geometries: List[TreadGeometry] = []
        self.midlanding_index: int = -1
        self.num_treads: int = 0
        self.tread_handles: List[str] = []
        
        # Geometry provider dependencies
        self.center_pole_data: Optional[Dict[str, Any]] = None
        self.dependencies_satisfied = False
        
    def get_dependencies(self) -> List[str]:
        """Return list of required provider module names"""
        return ['center_pole']
        
    def set_dependency_data(self, provider_name: str, geometry_data: Dict[str, Any]) -> bool:
        """Receive geometry data from provider modules"""
        if provider_name == 'center_pole':
            self.center_pole_data = geometry_data
            self.dependencies_satisfied = True
            return True
        return False
        
    def validate_dependencies(self) -> Tuple[bool, List[str]]:
        """Validate that all required dependencies are satisfied"""
        errors = []
        
        if not self.dependencies_satisfied or self.center_pole_data is None:
            errors.append("Center pole geometry data not provided")
            
        return len(errors) == 0, errors
    
    def validate_parameters(self) -> ValidationResult:
        """Validate tread-specific parameters"""
        result = ValidationResult(is_valid=True)
        
        try:
            # Get configuration values
            height = self._get_config_value('basic_parameters.overall_height')
            outside_dia = self._get_config_value('basic_parameters.outside_diameter')
            rotation = self._get_config_value('basic_parameters.total_rotation')
            thickness = self._get_config_value('tread_configuration.thickness')
            max_riser = self._get_config_value('tread_configuration.riser_height_max')
            
            # Get center pole data
            if self.center_pole_data:
                center_dia = self.center_pole_data['diameter']
            else:
                center_dia = self._get_config_value('basic_parameters.center_pole_diameter')
                
        except KeyError as e:
            result.errors.append(f"Missing required parameter: {e}")
            result.is_valid = False
            return result
            
        # Validate basic geometry relationships
        if outside_dia <= center_dia + 12:  # Minimum 6" on each side
            result.errors.append(
                f"Outside diameter ({outside_dia}\") must be at least "
                f"{center_dia + 12}\" for adequate tread width"
            )
            
        # Validate rotation range
        if rotation < 180.0 or rotation > 720.0:
            result.errors.append(
                f"Total rotation ({rotation}°) must be between 180° and 720°"
            )
            
        # Validate tread thickness
        if thickness < 0.125 or thickness > 2.0:
            result.errors.append(
                f"Tread thickness ({thickness}\") must be between 0.125\" and 2.0\""
            )
            
        # Calculate and validate tread count
        num_treads = self._calculate_num_treads(height, max_riser)
        if num_treads < self.MIN_TREAD_COUNT:
            result.errors.append(
                f"Calculated tread count ({num_treads}) is below minimum {self.MIN_TREAD_COUNT}"
            )
        elif num_treads > self.MAX_TREAD_COUNT:
            result.errors.append(
                f"Calculated tread count ({num_treads}) exceeds maximum {self.MAX_TREAD_COUNT}"
            )
            
        # Validate walkline width (IBC requirement)
        walkline_width = self._calculate_walkline_width(center_dia, outside_dia, rotation, num_treads)
        if walkline_width < 6.75:
            result.errors.append(
                f"Walkline width ({walkline_width:.2f}\") is below 6.75\" IBC minimum"
            )
            
        # Check midlanding requirement
        if height > self.MIDLANDING_HEIGHT_THRESHOLD:
            result.warnings.append(
                f"Height ({height}\") exceeds {self.MIDLANDING_HEIGHT_THRESHOLD}\" - midlanding will be added"
            )
            
        result.is_valid = len(result.errors) == 0
        return result
    
    def get_required_parameters(self) -> List[str]:
        """Return list of required configuration parameters"""
        return [
            'basic_parameters.overall_height',
            'basic_parameters.outside_diameter', 
            'basic_parameters.total_rotation',
            'basic_parameters.is_clockwise',
            'tread_configuration.thickness',
            'tread_configuration.riser_height_max'
        ]
    
    def generate_geometry(self) -> GenerationResult:
        """Generate all tread geometries in AutoCAD"""
        self.state = ComponentState.GENERATING
        result = GenerationResult(success=False)
        
        start_time = time.time()
        
        try:
            # Validate dependencies and parameters
            dep_valid, dep_errors = self.validate_dependencies()
            if not dep_valid:
                result.messages.extend(dep_errors)
                self.state = ComponentState.FAILED
                return result
                
            param_validation = self.validate_parameters()
            if not param_validation.is_valid:
                result.messages.extend(param_validation.errors)
                self.state = ComponentState.FAILED
                return result
            
            # Calculate tread geometries
            self.tread_geometries = self._calculate_tread_geometries()
            self.num_treads = len(self.tread_geometries)
            
            self.logger.info(f"Generating {self.num_treads} treads...")
            
            # Create layer
            self._ensure_layer_exists()
            
            # Generate each tread
            successful_treads = 0
            total_volume = 0.0
            
            for tread_geom in self.tread_geometries:
                success, volume = self._create_single_tread(tread_geom)
                if success:
                    successful_treads += 1
                    total_volume += volume
                else:
                    result.messages.append(f"Failed to create tread {tread_geom.index}")
            
            # Calculate performance metrics
            generation_time = time.time() - start_time
            self.performance_metrics.update({
                'generation_time': generation_time,
                'entities_created': successful_treads,
                'autocad_calls': successful_treads * 3,  # Region, extrude, properties
                'total_volume': total_volume
            })
            
            if successful_treads == self.num_treads:
                result.success = True
                result.messages.append(f"Successfully created {successful_treads} treads")
                result.entities = {
                    'num_treads': successful_treads,
                    'midlanding_index': self.midlanding_index,
                    'total_volume': total_volume,
                    'tread_handles': self.tread_handles.copy()
                }
                self.state = ComponentState.COMPLETED
            else:
                result.messages.append(f"Created {successful_treads} of {self.num_treads} treads")
                self.state = ComponentState.FAILED
            
        except Exception as e:
            result.messages.append(f"Exception during tread generation: {str(e)}")
            self.logger.error(f"Tread generation failed: {str(e)}", exc_info=True)
            self.state = ComponentState.FAILED
            self.cleanup_on_failure()
        
        return result
    
    def _calculate_tread_geometries(self) -> List[TreadGeometry]:
        """Calculate geometry for all treads including midlanding"""
        height = self._get_config_value('basic_parameters.overall_height')
        outside_dia = self._get_config_value('basic_parameters.outside_diameter')
        rotation = self._get_config_value('basic_parameters.total_rotation')
        is_clockwise = self._get_config_value('basic_parameters.is_clockwise')
        thickness = self._get_config_value('tread_configuration.thickness')
        max_riser = self._get_config_value('tread_configuration.riser_height_max')
        
        center_radius = self.center_pole_data['radius']
        outer_radius = outside_dia / 2.0
        
        # Calculate number of treads
        num_treads = self._calculate_num_treads(height, max_riser)
        
        # Check for midlanding requirement
        needs_midlanding = height > self.MIDLANDING_HEIGHT_THRESHOLD
        if needs_midlanding:
            self.midlanding_index = num_treads // 2
        
        # Convert rotation to radians
        total_rotation_rad = math.radians(rotation)
        direction = -1 if is_clockwise else 1
        
        geometries = []
        
        for i in range(num_treads):
            # Calculate Z position
            if needs_midlanding and i >= self.midlanding_index:
                # Account for midlanding height
                z_pos = (i / (num_treads - 1)) * height
            else:
                z_pos = (i / (num_treads - 1)) * height
            
            # Calculate angular position
            if needs_midlanding and i == self.midlanding_index:
                # Midlanding gets 90 degrees
                angle_width = self.MIDLANDING_ANGLE
                angle_start = (i / num_treads) * total_rotation_rad
                angle_end = angle_start + angle_width * direction
                is_midlanding = True
            else:
                # Regular tread
                angle_per_tread = total_rotation_rad / num_treads
                angle_start = (i / num_treads) * total_rotation_rad
                angle_end = ((i + 1) / num_treads) * total_rotation_rad
                is_midlanding = False
            
            # Apply clockwise direction
            if is_clockwise:
                angle_start = -angle_start
                angle_end = -angle_end
            
            # Create tread geometry
            tread_geom = TreadGeometry(
                index=i,
                angle_start=angle_start,
                angle_end=angle_end,
                z_position=z_pos,
                inner_radius=center_radius + 0.5,  # Small gap from pole
                outer_radius=outer_radius,
                thickness=thickness,
                is_midlanding=is_midlanding
            )
            
            geometries.append(tread_geom)
        
        return geometries
    
    def _create_single_tread(self, geometry: TreadGeometry) -> Tuple[bool, float]:
        """Create a single tread in AutoCAD"""
        try:
            # Create tread profile (sector)
            angle_start = geometry.angle_start
            angle_end = geometry.angle_end
            inner_r = geometry.inner_radius
            outer_r = geometry.outer_radius
            
            # Calculate points for sector
            points = self._calculate_sector_points(
                angle_start, angle_end, inner_r, outer_r
            )
            
            # Create region from points
            region_handle = self.acad.create_region_from_points(points)
            if not region_handle:
                return False, 0.0
            
            # Extrude to create tread thickness
            tread_handle = self.acad.extrude_region(
                region_handle, geometry.thickness
            )
            if not tread_handle:
                self.acad.delete_entity(region_handle)
                return False, 0.0
            
            # Move to correct Z position
            self.acad.move_entity(
                tread_handle, [0, 0, geometry.z_position]
            )
            
            # Set properties
            self._set_entity_properties(tread_handle)
            
            # Track entity
            self.add_entity(
                handle=tread_handle,
                entity_type=EntityType.EXTRUSION,
                properties={
                    'tread_index': geometry.index,
                    'angle_start': geometry.angle_start,
                    'angle_end': geometry.angle_end,
                    'z_position': geometry.z_position,
                    'is_midlanding': geometry.is_midlanding
                },
                layer_name=self.LAYER_NAME,
                color_index=self.COLOR_INDEX,
                line_type=self.LINE_TYPE
            )
            
            self.tread_handles.append(tread_handle)
            
            # Calculate volume
            angular_width = abs(geometry.angle_end - geometry.angle_start)
            area = 0.5 * angular_width * (outer_r**2 - inner_r**2)
            volume = area * geometry.thickness
            
            # Clean up temporary region
            self.acad.delete_entity(region_handle)
            
            return True, volume
            
        except Exception as e:
            self.logger.error(f"Failed to create tread {geometry.index}: {e}")
            return False, 0.0
    
    def _calculate_sector_points(self, angle_start: float, angle_end: float, 
                               inner_r: float, outer_r: float) -> List[Tuple[float, float]]:
        """Calculate points for tread sector geometry"""
        points = []
        
        # Number of segments for arc approximation
        num_segments = max(8, int(abs(angle_end - angle_start) * 180 / math.pi / 5))
        
        # Outer arc points
        for i in range(num_segments + 1):
            t = i / num_segments
            angle = angle_start + t * (angle_end - angle_start)
            x = outer_r * math.cos(angle)
            y = outer_r * math.sin(angle)
            points.append((x, y))
        
        # Inner arc points (reverse order)
        for i in range(num_segments, -1, -1):
            t = i / num_segments
            angle = angle_start + t * (angle_end - angle_start)
            x = inner_r * math.cos(angle)
            y = inner_r * math.sin(angle)
            points.append((x, y))
        
        return points
    
    def _calculate_num_treads(self, height: float, max_riser: float) -> int:
        """Calculate number of treads based on height and max riser"""
        return math.ceil(height / max_riser)
    
    def _calculate_walkline_width(self, center_dia: float, outside_dia: float, 
                                rotation: float, num_treads: int) -> float:
        """Calculate walkline width for IBC compliance"""
        walkline_radius = center_dia / 2 + 12  # 12" from center pole edge
        angle_per_tread = math.radians(rotation / num_treads)
        return walkline_radius * angle_per_tread
    
    # Enhanced functionality methods
    def add_tread_at_index(self, index: int) -> bool:
        """Add a new tread at specified index"""
        if self.state != ComponentState.COMPLETED:
            self.logger.error("Cannot add tread - geometry not generated")
            return False
            
        if index < 0 or index > len(self.tread_geometries):
            self.logger.error(f"Invalid tread index: {index}")
            return False
        
        try:
            # Recalculate all geometries with new tread count
            height = self._get_config_value('basic_parameters.overall_height')
            max_riser = self._get_config_value('tread_configuration.riser_height_max')
            
            new_tread_count = len(self.tread_geometries) + 1
            
            # Validate new count
            if new_tread_count > self.MAX_TREAD_COUNT:
                self.logger.error(f"Cannot exceed maximum tread count of {self.MAX_TREAD_COUNT}")
                return False
            
            # Recalculate geometries
            self.tread_geometries = self._calculate_tread_geometries()
            
            # Regenerate all treads (for now - could be optimized)
            self._regenerate_all_treads()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add tread at index {index}: {e}")
            return False
    
    def remove_tread_at_index(self, index: int) -> bool:
        """Remove tread at specified index"""
        if self.state != ComponentState.COMPLETED:
            self.logger.error("Cannot remove tread - geometry not generated")
            return False
            
        if len(self.tread_geometries) <= self.MIN_TREAD_COUNT:
            self.logger.error(f"Cannot go below minimum tread count of {self.MIN_TREAD_COUNT}")
            return False
            
        if index < 0 or index >= len(self.tread_geometries):
            self.logger.error(f"Invalid tread index: {index}")
            return False
        
        try:
            # Remove the tread entity from AutoCAD
            if index < len(self.tread_handles):
                self.acad.delete_entity(self.tread_handles[index])
                self.tread_handles.pop(index)
            
            # Remove from geometries list
            self.tread_geometries.pop(index)
            
            # Recalculate remaining tread positions
            self._regenerate_all_treads()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove tread at index {index}: {e}")
            return False
    
    def _regenerate_all_treads(self):
        """Regenerate all treads after modification"""
        # Clean up existing entities
        for handle in self.tread_handles:
            try:
                self.acad.delete_entity(handle)
            except:
                pass
        
        self.tread_handles.clear()
        self.generated_entities.clear()
        
        # Regenerate
        result = self.generate_geometry()
        return result.success
    
    # IGeometryProvider Interface Implementation
    def get_geometry_data(self) -> Dict[str, Any]:
        """Return tread geometry data for other modules"""
        if self.state != ComponentState.COMPLETED:
            raise RuntimeError("Tread geometry not yet generated")
        
        tread_positions = []
        for geom in self.tread_geometries:
            center_angle = geom.get_center_angle()
            center_radius = (geom.inner_radius + geom.outer_radius) / 2
            
            tread_positions.append({
                'index': geom.index,
                'center_angle': center_angle,
                'angle_start': geom.angle_start,
                'angle_end': geom.angle_end,
                'z_position': geom.z_position,
                'inner_radius': geom.inner_radius,
                'outer_radius': geom.outer_radius,
                'center_radius': center_radius,
                'center_x': center_radius * math.cos(center_angle),
                'center_y': center_radius * math.sin(center_angle),
                'is_midlanding': geom.is_midlanding,
                'thickness': geom.thickness
            })
        
        return {
            'tread_count': len(self.tread_geometries),
            'tread_positions': tread_positions,
            'midlanding_index': self.midlanding_index,
            'total_height': self._get_config_value('basic_parameters.overall_height'),
            'bounding_radius': self._get_config_value('basic_parameters.outside_diameter') / 2.0
        }
    
    def get_reference_points(self) -> List[Tuple[float, float, float]]:
        """Return tread reference points for other modules"""
        if self.state != ComponentState.COMPLETED:
            return []
        
        points = []
        for geom in self.tread_geometries:
            center_angle = geom.get_center_angle()
            center_radius = (geom.inner_radius + geom.outer_radius) / 2
            
            # Center point of tread
            center_x = center_radius * math.cos(center_angle)
            center_y = center_radius * math.sin(center_angle)
            points.append((center_x, center_y, geom.z_position + geom.thickness))
            
            # Edge points
            inner_x = geom.inner_radius * math.cos(center_angle)
            inner_y = geom.inner_radius * math.sin(center_angle)
            outer_x = geom.outer_radius * math.cos(center_angle)
            outer_y = geom.outer_radius * math.sin(center_angle)
            
            points.extend([
                (inner_x, inner_y, geom.z_position + geom.thickness),
                (outer_x, outer_y, geom.z_position + geom.thickness)
            ])
        
        return points
    
    def get_bounding_geometry(self) -> Dict[str, float]:
        """Return bounding geometry for treads"""
        if self.state != ComponentState.COMPLETED:
            return {}
        
        outside_radius = self._get_config_value('basic_parameters.outside_diameter') / 2.0
        height = self._get_config_value('basic_parameters.overall_height')
        
        return {
            'min_x': -outside_radius,
            'max_x': outside_radius,
            'min_y': -outside_radius,
            'max_y': outside_radius,
            'min_z': 0.0,
            'max_z': height,
            'outer_radius': outside_radius,
            'total_height': height
        }
```

This completes the comprehensive Module Specifications with detailed interface contracts and implementation details for both the Center Pole and Enhanced Tread modules. Each module includes:
        basic = self.config.basic_parameters
        
        diameter = basic.get("center_pole_diameter", 0)
        height = basic.get("overall_height", 0)
        
        if diameter <= 0:
            errors.append("Center pole diameter must be greater than 0")
        elif diameter not in self.AVAILABLE_DIAMETERS:
            closest = min(self.AVAILABLE_DIAMETERS, key=lambda x: abs(x - diameter))
            errors.append(f"Center pole diameter {diameter} not available. Closest: {closest}")
            
        if height <= 0:
            errors.append("Overall height must be greater than 0")
        elif height > 240:  # Practical limit
            errors.append("Overall height exceeds practical limit of 240 inches")
            
        return len(errors) == 0, errors
        
    def generate_geometry(self) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Generate center pole cylinder"""
        try:
            basic = self.config.basic_parameters
            diameter = basic["center_pole_diameter"]
            height = basic["overall_height"]
            radius = diameter / 2
            
            # Create cylinder at origin
            center_point = [0.0, 0.0, 0.0]
            pole_handle = self.acad.create_cylinder(center_point, radius, height)
            
            if not pole_handle:
                return False, ["Failed to create center pole cylinder"], {}
                
            # Move cylinder to proper position (center at height/2)
            pole_entity = self.acad.get_entity_by_handle(pole_handle)
            if pole_entity:
                # Create transformation matrix to move cylinder
                transform_matrix = [
                    [1, 0, 0, 0],
                    [0, 1, 0, 0], 
                    [0, 0, 1, height/2],
                    [0, 0, 0, 1]
                ]
                pole_entity.TransformBy(transform_matrix)
                
                # Set color (light gray)
                pole_entity.Color = 251
                
            # Track the created entity
            self.add_entity(pole_handle, "cylinder", {
                "diameter": diameter,
                "height": height,
                "radius": radius,
                "center": [0, 0, height/2]
            })
            
            self.is_generated = True
            
            return True, [f"Center pole created: {diameter}\" diameter, {height}\" height"], {
                "pole_handle": pole_handle,
                "diameter": diameter,
                "height": height,
                "volume": 3.14159 * radius * radius * height
            }
            
        except Exception as e:
            self.logger.error(f"Center pole generation failed: {str(e)}")
            self.cleanup_on_failure()
            return False, [f"Center pole generation failed: {str(e)}"], {}
            
    def get_required_parameters(self) -> List[str]:
        return ["basic_parameters.center_pole_diameter", "basic_parameters.overall_height"]
        
    def get_pole_radius(self) -> float:
        """Get the pole radius for other modules to use"""
        return self.config.basic_parameters["center_pole_diameter"] / 2
```

---

## Module 2: Tread Module (Enhanced)

**File**: `src/modules/tread_module.py`

### Purpose
Creates sector-shaped treads with enhanced functionality for adding, removing, and modifying individual treads. Migrated from VBA `Module1.bas:292-340` with significant enhancements.

### New Capabilities
- **Add tread at specific index**: Insert new tread and recalculate angles
- **Remove tread at index**: Delete tread and adjust remaining treads
- **Modify existing tread**: Change parameters without full regeneration
- **Batch operations**: Multiple tread modifications in single operation

### Configuration Parameters
```json
{
  "basic_parameters": {
    "center_pole_diameter": 5.0,
    "overall_height": 120.0,
    "outside_diameter": 72.0,
    "total_rotation": 360.0,
    "is_clockwise": true
  },
  "tread_configuration": {
    "thickness": 0.25,              // inches
    "riser_height_max": 9.5,        // inches per IBC
    "custom_treads": []             // Array of custom tread modifications
  }
}
```

### Implementation
```python
from typing import NamedTuple
import math

class TreadGeometry(NamedTuple):
    index: int
    start_angle: float
    end_angle: float
    height: float
    inner_radius: float
    outer_radius: float

class TreadModule(BaseStairComponent):
    def __init__(self, config: StairConfiguration, autocad_interface: AutoCADInterface):
        super().__init__(config, autocad_interface)
        self.tread_geometries: List[TreadGeometry] = []
        self.midlanding_index = -1
        
    def validate_parameters(self) -> Tuple[bool, List[str]]:
        """Validate tread parameters"""
        errors = []
        basic = self.config.basic_parameters
        
        height = basic.get("overall_height", 0)
        outside_dia = basic.get("outside_diameter", 0)
        center_dia = basic.get("center_pole_diameter", 0)
        rotation = basic.get("total_rotation", 0)
        
        if outside_dia <= center_dia:
            errors.append("Outside diameter must be greater than center pole diameter")
            
        if rotation <= 0 or rotation > 720:
            errors.append("Total rotation must be between 0 and 720 degrees")
            
        # Calculate basic tread geometry for validation
        num_treads = self._calculate_num_treads(height)
        if num_treads < 2:
            errors.append("Insufficient height for minimum 2 treads")
        elif num_treads > 50:  # Practical limit
            errors.append("Too many treads - consider reducing height or increasing riser height")
            
        return len(errors) == 0, errors
        
    def _calculate_num_treads(self, height: float) -> int:
        """Calculate number of treads based on height and max riser"""
        max_riser = self.config.tread_configuration.get("riser_height_max", 9.5)
        return math.ceil(height / max_riser)
        
    def _calculate_tread_geometries(self) -> List[TreadGeometry]:
        """Calculate geometry for all treads"""
        basic = self.config.basic_parameters
        height = basic["overall_height"]
        center_dia = basic["center_pole_diameter"]
        outside_dia = basic["outside_diameter"]
        rotation_deg = basic["total_rotation"]
        is_clockwise = basic["is_clockwise"]
        
        num_treads = self._calculate_num_treads(height)
        riser_height = height / num_treads
        inner_radius = center_dia / 2
        outer_radius = outside_dia / 2
        
        # Check for midlanding requirement
        self.midlanding_index = -1
        if height > 151:  # IBC requirement
            self.midlanding_index = round(num_treads / 2) - 1
            
        # Calculate angles
        if self.midlanding_index >= 0:
            # Reserve 90 degrees for midlanding
            tread_angle_deg = (rotation_deg - 90) / (num_treads - 2)
        else:
            tread_angle_deg = rotation_deg / (num_treads - 1)
            
        direction = 1 if is_clockwise else -1
        tread_angle_rad = math.radians(tread_angle_deg * direction)
        
        geometries = []
        current_angle = 0
        
        for i in range(num_treads):
            tread_height = riser_height * (i + 1) - 0.25  # Account for thickness
            
            if i == self.midlanding_index:
                # Midlanding gets 90 degrees
                end_angle = current_angle + direction * math.radians(90)
            else:
                end_angle = current_angle + tread_angle_rad
                
            geometry = TreadGeometry(
                index=i,
                start_angle=current_angle,
                end_angle=end_angle,
                height=tread_height,
                inner_radius=inner_radius,
                outer_radius=outer_radius
            )
            geometries.append(geometry)
            current_angle = end_angle
            
        return geometries
        
    def generate_geometry(self) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Generate all treads"""
        try:
            self.tread_geometries = self._calculate_tread_geometries()
            messages = []
            total_volume = 0
            
            for geometry in self.tread_geometries:
                success, volume = self._create_single_tread(geometry)
                if success:
                    total_volume += volume
                    if geometry.index == self.midlanding_index:
                        messages.append(f"Midlanding created at tread {geometry.index + 1}")
                else:
                    messages.append(f"Failed to create tread {geometry.index + 1}")
                    
            self.is_generated = True
            
            return True, messages, {
                "num_treads": len(self.tread_geometries),
                "total_volume": total_volume,
                "midlanding_index": self.midlanding_index,
                "tread_handles": self.get_entity_handles()
            }
            
        except Exception as e:
            self.logger.error(f"Tread generation failed: {str(e)}")
            self.cleanup_on_failure()
            return False, [f"Tread generation failed: {str(e)}"], {}
            
    def _create_single_tread(self, geometry: TreadGeometry) -> Tuple[bool, float]:
        """Create a single tread based on geometry"""
        try:
            thickness = self.config.tread_configuration.get("thickness", 0.25)
            
            # Create tread outline entities
            entities = []
            
            # Inner radial line
            start_point = [0, 0, geometry.height]
            end_point = [
                geometry.outer_radius * math.cos(geometry.start_angle),
                geometry.outer_radius * math.sin(geometry.start_angle),
                geometry.height
            ]
            line1_handle = self.acad.create_line(start_point, end_point)
            if line1_handle:
                entities.append(line1_handle)
                
            # Outer arc
            center = [0, 0, geometry.height]
            is_clockwise = self.config.basic_parameters["is_clockwise"]
            if is_clockwise:
                arc_handle = self.acad.create_arc(center, geometry.outer_radius, 
                                                geometry.start_angle, geometry.end_angle)
            else:
                arc_handle = self.acad.create_arc(center, geometry.outer_radius,
                                                geometry.end_angle, geometry.start_angle)
            if arc_handle:
                entities.append(arc_handle)
                
            # Outer radial line
            start_point = [
                geometry.outer_radius * math.cos(geometry.end_angle),
                geometry.outer_radius * math.sin(geometry.end_angle), 
                geometry.height
            ]
            end_point = [0, 0, geometry.height]
            line2_handle = self.acad.create_line(start_point, end_point)
            if line2_handle:
                entities.append(line2_handle)
                
            # Create region from entities
            region_handle = self.acad.create_region_from_entities(entities)
            if not region_handle:
                return False, 0
                
            # Extrude region to create solid
            solid_handle = self.acad.extrude_region(region_handle, thickness)
            if not solid_handle:
                return False, 0
                
            # Set color
            solid_entity = self.acad.get_entity_by_handle(solid_handle)
            if solid_entity:
                if geometry.index == self.midlanding_index:
                    solid_entity.Color = 1  # Red for midlanding
                else:
                    solid_entity.Color = 251  # Light gray for treads
                    
            # Calculate volume
            angle_span = abs(geometry.end_angle - geometry.start_angle)
            sector_area = 0.5 * geometry.outer_radius * geometry.outer_radius * angle_span
            volume = sector_area * thickness
            
            # Track entity
            self.add_entity(solid_handle, "tread", {
                "index": geometry.index,
                "height": geometry.height,
                "volume": volume,
                "is_midlanding": geometry.index == self.midlanding_index
            })
            
            # Clean up construction entities
            for entity_handle in entities + [region_handle]:
                self.acad.delete_entity(entity_handle)
                
            return True, volume
            
        except Exception as e:
            self.logger.error(f"Failed to create tread {geometry.index}: {str(e)}")
            return False, 0
            
    def add_tread_at_index(self, index: int) -> bool:
        """Add a new tread at specified index and recalculate"""
        try:
            if not self.is_generated:
                return False
                
            # Remove existing treads
            self._clear_existing_treads()
            
            # Recalculate with additional tread
            basic = self.config.basic_parameters.copy()
            num_treads = len(self.tread_geometries) + 1
            basic["overall_height"] = basic["overall_height"] * num_treads / (num_treads - 1)
            
            # Update configuration temporarily
            original_config = self.config.basic_parameters
            self.config.basic_parameters = basic
            
            # Regenerate all treads
            success, messages, info = self.generate_geometry()
            
            # Restore original configuration
            self.config.basic_parameters = original_config
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to add tread at index {index}: {str(e)}")
            return False
            
    def remove_tread_at_index(self, index: int) -> bool:
        """Remove tread at specified index and recalculate"""
        try:
            if not self.is_generated or index >= len(self.tread_geometries):
                return False
                
            # Remove existing treads
            self._clear_existing_treads()
            
            # Recalculate with fewer treads
            basic = self.config.basic_parameters.copy()
            num_treads = len(self.tread_geometries) - 1
            if num_treads < 2:
                return False
                
            basic["overall_height"] = basic["overall_height"] * num_treads / (num_treads + 1)
            
            # Update configuration temporarily
            original_config = self.config.basic_parameters
            self.config.basic_parameters = basic
            
            # Regenerate all treads
            success, messages, info = self.generate_geometry()
            
            # Restore original configuration
            self.config.basic_parameters = original_config
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to remove tread at index {index}: {str(e)}")
            return False
            
    def _clear_existing_treads(self):
        """Remove all existing tread entities"""
        for entity_info in self.generated_entities:
            self.acad.delete_entity(entity_info.handle)
        self.generated_entities.clear()
        self.is_generated = False
        
    def get_required_parameters(self) -> List[str]:
        return [
            "basic_parameters.center_pole_diameter",
            "basic_parameters.overall_height", 
            "basic_parameters.outside_diameter",
            "basic_parameters.total_rotation",
            "basic_parameters.is_clockwise"
        ]
```

---

## Module 3: Landing Module

**File**: `src/modules/landing_module.py`

### Purpose
Creates rectangular top landing and optional mid-landings. Migrated from VBA `Module1.bas:342-402` with enhancements for different landing shapes.

### Implementation
```python
class LandingModule(BaseStairComponent):
    def validate_parameters(self) -> Tuple[bool, List[str]]:
        """Validate landing parameters"""
        errors = []
        basic = self.config.basic_parameters
        
        outside_dia = basic.get("outside_diameter", 0)
        if outside_dia <= 0:
            errors.append("Outside diameter required for landing generation")
            
        return len(errors) == 0, errors
        
    def generate_geometry(self) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Generate top landing (final tread is always the landing)"""
        try:
            basic = self.config.basic_parameters
            outside_dia = basic["outside_diameter"] 
            height = basic["overall_height"]
            rotation = basic["total_rotation"]
            is_clockwise = basic["is_clockwise"]
            
            # Calculate landing position
            num_treads = math.ceil(height / 9.5)
            riser_height = height / num_treads
            landing_height = height - 0.25  # Account for thickness
            
            # Landing dimensions
            landing_length = outside_dia / 2
            landing_width = 50  # Standard width
            
            # Calculate final angle
            final_angle = math.radians(rotation)
            direction = 1 if is_clockwise else -1
            
            success = self._create_rectangular_landing(
                landing_length, landing_width, final_angle, direction, landing_height
            )
            
            if success:
                return True, ["Top landing created"], {
                    "landing_handle": self.get_entity_handles()[-1],
                    "height": landing_height,
                    "dimensions": [landing_length, landing_width]
                }
            else:
                return False, ["Failed to create top landing"], {}
                
        except Exception as e:
            self.logger.error(f"Landing generation failed: {str(e)}")
            self.cleanup_on_failure()
            return False, [f"Landing generation failed: {str(e)}"], {}
            
    def _create_rectangular_landing(self, length: float, width: float, 
                                  angle: float, direction: int, height: float) -> bool:
        """Create rectangular landing at specified position"""
        try:
            # Create landing outline
            entities = []
            
            # Calculate corner points
            corners = [
                [0, 0, height],
                [length * math.cos(angle), length * math.sin(angle), height],
                [length * math.cos(angle) + width * math.cos(angle + math.pi/2 * direction),
                 length * math.sin(angle) + width * math.sin(angle + math.pi/2 * direction), height],
                [width * math.cos(angle + math.pi/2 * direction),
                 width * math.sin(angle + math.pi/2 * direction), height]
            ]
            
            # Create lines
            for i in range(4):
                start = corners[i]
                end = corners[(i + 1) % 4]
                line_handle = self.acad.create_line(start, end)
                if line_handle:
                    entities.append(line_handle)
                    
            # Create region
            region_handle = self.acad.create_region_from_entities(entities)
            if not region_handle:
                return False
                
            # Extrude to create solid
            solid_handle = self.acad.extrude_region(region_handle, 0.25)
            if not solid_handle:
                return False
                
            # Set color (green for landing)
            solid_entity = self.acad.get_entity_by_handle(solid_handle)
            if solid_entity:
                solid_entity.Color = 3
                
            # Track entity
            self.add_entity(solid_handle, "landing", {
                "length": length,
                "width": width,
                "height": height,
                "angle": angle
            })
            
            # Clean up construction entities
            for entity_handle in entities + [region_handle]:
                self.acad.delete_entity(entity_handle)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create landing: {str(e)}")
            return False
            
    def get_required_parameters(self) -> List[str]:
        return ["basic_parameters.outside_diameter", "basic_parameters.overall_height"]
```

---

## Module 4: Picket Module (NEW)

**File**: `src/modules/picket_module.py`

### Purpose
Creates vertical and/or horizontal pickets (balusters) between treads with IBC-compliant spacing. This is a completely new component not present in the original VBA system.

### Configuration Parameters
```json
{
  "picket_configuration": {
    "enabled": true,
    "spacing_inches": 3.5,          // Maximum spacing per IBC (≤ 4")
    "height_ratio": 0.85,           // Height as ratio of tread-to-handrail distance
    "style": "vertical",            // "vertical", "horizontal", "crossed"
    "material": "aluminum",         // "aluminum", "steel", "wood"
    "connection_type": "welded",    // "welded", "bolted", "mechanical"
    "picket_diameter": 0.75,        // inches
    "decorative_pattern": "none"    // "none", "diamond", "spiral", "custom"
  }
}
```

### Implementation
```python
class PicketModule(BaseStairComponent):
    def validate_parameters(self) -> Tuple[bool, List[str]]:
        """Validate picket parameters including IBC compliance"""
        errors = []
        
        if not self.config.picket_configuration.get("enabled", False):
            return True, []  # Skip validation if disabled
            
        picket_config = self.config.picket_configuration
        spacing = picket_config.get("spacing_inches", 6.0)
        
        # IBC 4-inch sphere rule
        if spacing > 4.0:
            errors.append(f"Picket spacing {spacing}\" exceeds 4\" maximum per IBC R311.7.8")
            
        diameter = picket_config.get("picket_diameter", 0.75)
        if diameter <= 0 or diameter > 2.0:
            errors.append("Picket diameter must be between 0 and 2 inches")
            
        height_ratio = picket_config.get("height_ratio", 0.85)
        if height_ratio <= 0 or height_ratio > 1.0:
            errors.append("Height ratio must be between 0 and 1.0")
            
        return len(errors) == 0, errors
        
    def generate_geometry(self) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Generate picket system"""
        try:
            if not self.config.picket_configuration.get("enabled", False):
                return True, ["Pickets disabled"], {}
                
            # Get tread information from orchestrator or calculate
            tread_positions = self._calculate_tread_positions()
            picket_positions = self._calculate_picket_positions(tread_positions)
            
            messages = []
            total_pickets = 0
            
            style = self.config.picket_configuration.get("style", "vertical")
            
            if style == "vertical":
                success, count = self._generate_vertical_pickets(picket_positions)
                total_pickets += count
                messages.append(f"Generated {count} vertical pickets")
                
            elif style == "horizontal":
                success, count = self._generate_horizontal_rails(tread_positions)
                total_pickets += count
                messages.append(f"Generated {count} horizontal rail segments")
                
            elif style == "crossed":
                v_success, v_count = self._generate_vertical_pickets(picket_positions)
                h_success, h_count = self._generate_horizontal_rails(tread_positions)
                total_pickets = v_count + h_count
                messages.append(f"Generated {v_count} vertical pickets, {h_count} horizontal rails")
                success = v_success and h_success
                
            self.is_generated = True
            
            return success, messages, {
                "total_pickets": total_pickets,
                "style": style,
                "picket_handles": self.get_entity_handles()
            }
            
        except Exception as e:
            self.logger.error(f"Picket generation failed: {str(e)}")
            self.cleanup_on_failure()
            return False, [f"Picket generation failed: {str(e)}"], {}
            
    def _calculate_tread_positions(self) -> List[Dict[str, float]]:
        """Calculate positions and angles of all treads"""
        basic = self.config.basic_parameters
        height = basic["overall_height"]
        rotation_deg = basic["total_rotation"]
        is_clockwise = basic["is_clockwise"]
        
        num_treads = math.ceil(height / 9.5)
        riser_height = height / num_treads
        tread_angle_deg = rotation_deg / (num_treads - 1)
        
        direction = 1 if is_clockwise else -1
        positions = []
        
        for i in range(num_treads - 1):  # Exclude top landing
            angle_rad = math.radians(tread_angle_deg * i * direction)
            tread_height = riser_height * (i + 1)
            
            positions.append({
                "index": i,
                "angle": angle_rad,
                "height": tread_height,
                "next_height": riser_height * (i + 2) if i < num_treads - 2 else height
            })
            
        return positions
        
    def _calculate_picket_positions(self, tread_positions: List[Dict]) -> List[Dict[str, float]]:
        """Calculate individual picket positions based on spacing"""
        picket_config = self.config.picket_configuration
        spacing = picket_config.get("spacing_inches", 3.5)
        basic = self.config.basic_parameters
        center_radius = basic["center_pole_diameter"] / 2
        outer_radius = basic["outside_diameter"] / 2
        
        positions = []
        
        for tread in tread_positions:
            # Calculate arc length at walkline (12" from center pole edge)
            walkline_radius = center_radius + 12
            tread_angle_deg = math.degrees(abs(tread["angle"] - tread_positions[min(tread["index"] + 1, len(tread_positions) - 1)]["angle"]))
            arc_length = walkline_radius * math.radians(tread_angle_deg)
            
            # Calculate number of pickets needed
            num_pickets = math.floor(arc_length / spacing) + 1
            
            for i in range(num_pickets):
                picket_angle = tread["angle"] + (tread_angle_deg / num_pickets * i)
                
                positions.append({
                    "tread_index": tread["index"],
                    "angle": picket_angle,
                    "inner_radius": center_radius,
                    "outer_radius": outer_radius,
                    "bottom_height": tread["height"],
                    "top_height": tread["next_height"]
                })
                
        return positions
        
    def _generate_vertical_pickets(self, positions: List[Dict]) -> Tuple[bool, int]:
        """Generate vertical pickets at calculated positions"""
        try:
            picket_config = self.config.picket_configuration
            diameter = picket_config.get("picket_diameter", 0.75)
            radius = diameter / 2
            height_ratio = picket_config.get("height_ratio", 0.85)
            
            count = 0
            
            for pos in positions:
                # Calculate picket position on tread edge
                picket_radius = pos["outer_radius"] - 2  # Inset from edge
                x = picket_radius * math.cos(pos["angle"])
                y = picket_radius * math.sin(pos["angle"])
                
                # Calculate picket height
                picket_height = (pos["top_height"] - pos["bottom_height"]) * height_ratio
                center_point = [x, y, pos["bottom_height"] + picket_height/2]
                
                # Create picket cylinder
                picket_handle = self.acad.create_cylinder(center_point, radius, picket_height)
                
                if picket_handle:
                    # Set color based on material
                    picket_entity = self.acad.get_entity_by_handle(picket_handle)
                    if picket_entity:
                        material = picket_config.get("material", "aluminum")
                        color = {"aluminum": 7, "steel": 8, "wood": 30}.get(material, 7)
                        picket_entity.Color = color
                        
                    self.add_entity(picket_handle, "picket", {
                        "position": [x, y, pos["bottom_height"]],
                        "height": picket_height,
                        "diameter": diameter,
                        "tread_index": pos["tread_index"]
                    })
                    
                    count += 1
                    
            return True, count
            
        except Exception as e:
            self.logger.error(f"Failed to generate vertical pickets: {str(e)}")
            return False, 0
            
    def _generate_horizontal_rails(self, tread_positions: List[Dict]) -> Tuple[bool, int]:
        """Generate horizontal rails between treads"""
        try:
            # Implementation for horizontal rails between pickets
            # This would create connecting rails at mid-height between treads
            return True, 0  # Placeholder
            
        except Exception as e:
            self.logger.error(f"Failed to generate horizontal rails: {str(e)}")
            return False, 0
            
    def get_required_parameters(self) -> List[str]:
        return [
            "basic_parameters.center_pole_diameter",
            "basic_parameters.outside_diameter",
            "picket_configuration.enabled"
        ]
```

---

## Module 5: Handrail Module (NEW)

**File**: `src/modules/handrail_module.py`

### Purpose
Creates continuous spiral handrail following the stair geometry with proper height compliance. This is a completely new component.

### Configuration Parameters
```json
{
  "handrail_configuration": {
    "enabled": true,
    "height_above_tread": 36.0,     // inches (34"-38" per IBC)
    "diameter": 1.5,                // inches
    "material": "aluminum",         // "aluminum", "steel", "wood"
    "continuous": true,             // Continuous vs segmented
    "end_treatment": "cap",         // "cap", "return", "extension"
    "mounting_height": 2.0          // inches above outer edge
  }
}
```

### Implementation
```python
class HandrailModule(BaseStairComponent):
    def validate_parameters(self) -> Tuple[bool, List[str]]:
        """Validate handrail parameters for IBC compliance"""
        errors = []
        
        if not self.config.handrail_configuration.get("enabled", False):
            return True, []
            
        handrail_config = self.config.handrail_configuration
        height = handrail_config.get("height_above_tread", 36.0)
        
        # IBC handrail height requirement
        if height < 34.0 or height > 38.0:
            errors.append(f"Handrail height {height}\" must be between 34\" and 38\" per IBC R311.7.8.1")
            
        diameter = handrail_config.get("diameter", 1.5)
        if diameter < 1.25 or diameter > 2.0:
            errors.append("Handrail diameter should be between 1.25\" and 2\" for proper grip")
            
        return len(errors) == 0, errors
        
    def generate_geometry(self) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Generate continuous spiral handrail"""
        try:
            if not self.config.handrail_configuration.get("enabled", False):
                return True, ["Handrail disabled"], {}
                
            handrail_path = self._calculate_handrail_path()
            
            if self.config.handrail_configuration.get("continuous", True):
                success = self._generate_continuous_rail(handrail_path)
            else:
                success = self._generate_segmented_rail(handrail_path)
                
            if success:
                return True, ["Handrail generated"], {
                    "handrail_handle": self.get_entity_handles()[-1],
                    "path_length": len(handrail_path),
                    "type": "continuous" if self.config.handrail_configuration.get("continuous", True) else "segmented"
                }
            else:
                return False, ["Failed to generate handrail"], {}
                
        except Exception as e:
            self.logger.error(f"Handrail generation failed: {str(e)}")
            self.cleanup_on_failure()
            return False, [f"Handrail generation failed: {str(e)}"], {}
            
    def _calculate_handrail_path(self) -> List[Tuple[float, float, float]]:
        """Calculate 3D path for handrail following stair geometry"""
        basic = self.config.basic_parameters
        handrail_config = self.config.handrail_configuration
        
        height = basic["overall_height"]
        rotation_deg = basic["total_rotation"]
        is_clockwise = basic["is_clockwise"]
        handrail_height = handrail_config.get("height_above_tread", 36.0)
        mounting_height = handrail_config.get("mounting_height", 2.0)
        
        # Calculate handrail radius (typically at outer edge)
        handrail_radius = basic["outside_diameter"] / 2 - mounting_height
        
        num_treads = math.ceil(height / 9.5)
        riser_height = height / num_treads
        
        path_points = []
        direction = 1 if is_clockwise else -1
        
        # Generate points along the spiral path
        num_segments = num_treads * 4  # 4 points per tread for smooth curve
        
        for i in range(num_segments):
            t = i / (num_segments - 1)  # Parameter from 0 to 1
            
            # Calculate position along spiral
            angle = math.radians(rotation_deg * t * direction)
            spiral_height = height * t + handrail_height
            
            x = handrail_radius * math.cos(angle)
            y = handrail_radius * math.sin(angle)
            z = spiral_height
            
            path_points.append((x, y, z))
            
        return path_points
        
    def _generate_continuous_rail(self, path: List[Tuple[float, float, float]]) -> bool:
        """Generate continuous handrail using spline or swept geometry"""
        try:
            handrail_config = self.config.handrail_configuration
            diameter = handrail_config.get("diameter", 1.5)
            radius = diameter / 2
            
            # Create spline through path points
            # Note: This is a simplified approach - actual implementation would use
            # AutoCAD's spline or sweep functionality
            
            segments = []
            for i in range(len(path) - 1):
                start_point = path[i]
                end_point = path[i + 1]
                
                # Create line segment (simplified - would use spline in practice)
                line_handle = self.acad.create_line(list(start_point), list(end_point))
                if line_handle:
                    segments.append(line_handle)
                    
            # In a full implementation, this would:
            # 1. Create a spline through all points
            # 2. Create a circular profile at the start
            # 3. Sweep the profile along the spline path
            # 4. Apply material properties and color
            
            # For now, track the segments
            for segment in segments:
                self.add_entity(segment, "handrail_segment", {
                    "diameter": diameter,
                    "type": "continuous"
                })
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate continuous handrail: {str(e)}")
            return False
            
    def get_required_parameters(self) -> List[str]:
        return [
            "basic_parameters.outside_diameter",
            "basic_parameters.overall_height",
            "handrail_configuration.enabled"
        ]
```

---

## Module 6: Post Module (NEW)

**File**: `src/modules/post_module.py`

### Purpose
Creates structural posts at landings and intermediate points for handrail support. This is a completely new component.

### Configuration Parameters
```json
{
  "post_configuration": {
    "enabled": true,
    "spacing_treads": 4,            // Post every N treads
    "connection_type": "welded",    // "welded", "bolted", "mechanical"
    "height_above_handrail": 2.0,   // inches above handrail
    "post_diameter": 2.0,           // inches
    "base_plate_size": 6.0          // inches square
  }
}
```

### Implementation
```python
class PostModule(BaseStairComponent):
    def validate_parameters(self) -> Tuple[bool, List[str]]:
        """Validate post parameters"""
        errors = []
        
        if not self.config.post_configuration.get("enabled", False):
            return True, []
            
        post_config = self.config.post_configuration
        spacing = post_config.get("spacing_treads", 4)
        
        if spacing < 2 or spacing > 8:
            errors.append("Post spacing should be between 2 and 8 treads")
            
        diameter = post_config.get("post_diameter", 2.0)
        if diameter < 1.0 or diameter > 4.0:
            errors.append("Post diameter should be between 1.0 and 4.0 inches")
            
        return len(errors) == 0, errors
        
    def generate_geometry(self) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Generate structural posts"""
        try:
            if not self.config.post_configuration.get("enabled", False):
                return True, ["Posts disabled"], {}
                
            post_positions = self._calculate_post_positions()
            messages = []
            
            # Generate landing posts
            landing_posts = self._generate_landing_posts()
            messages.append(f"Generated {landing_posts} landing posts")
            
            # Generate intermediate posts
            intermediate_posts = self._generate_intermediate_posts(post_positions)
            messages.append(f"Generated {intermediate_posts} intermediate posts")
            
            total_posts = landing_posts + intermediate_posts
            
            return True, messages, {
                "total_posts": total_posts,
                "post_handles": self.get_entity_handles()
            }
            
        except Exception as e:
            self.logger.error(f"Post generation failed: {str(e)}")
            self.cleanup_on_failure()
            return False, [f"Post generation failed: {str(e)}"], {}
            
    def _calculate_post_positions(self) -> List[Dict[str, float]]:
        """Calculate positions for intermediate posts"""
        basic = self.config.basic_parameters
        post_config = self.config.post_configuration
        
        spacing = post_config.get("spacing_treads", 4)
        num_treads = math.ceil(basic["overall_height"] / 9.5)
        
        positions = []
        for i in range(0, num_treads, spacing):
            if i > 0 and i < num_treads - 1:  # Skip start and end
                positions.append({"tread_index": i})
                
        return positions
        
    def _generate_landing_posts(self) -> int:
        """Generate posts at landing positions"""
        # Implementation for landing posts
        return 1  # Placeholder
        
    def _generate_intermediate_posts(self, positions: List[Dict]) -> int:
        """Generate intermediate posts based on spacing"""
        # Implementation for intermediate posts
        return len(positions)  # Placeholder
        
    def get_required_parameters(self) -> List[str]:
        return ["post_configuration.enabled"]
```

---

## Module Integration Notes

### Execution Order
1. **Center Pole** - Provides foundation and reference geometry
2. **Treads** - Defines step geometry and walking surface
3. **Landings** - Creates platforms and final landing
4. **Posts** - Provides structural support points
5. **Pickets** - Fills safety gaps between structural elements
6. **Handrails** - Completes safety system with gripping surface

### Inter-Module Dependencies
- **Pickets** require tread positions and heights
- **Handrails** require tread geometry and post locations
- **Posts** require landing positions and span calculations
- All modules require basic parameters (pole diameter, height, etc.)

### Error Handling Strategy
- Each module validates its own parameters independently
- Module failures are isolated - other modules continue execution
- Comprehensive logging for debugging and troubleshooting
- Automatic cleanup of partially created geometry on failure

### Performance Considerations
- Batch AutoCAD operations where possible
- Minimize COM interface calls
- Use entity handles for efficient reference management
- Implement progressive generation with user feedback

This modular specification provides a complete framework for generating all components of a code-compliant spiral staircase while maintaining the flexibility to add, remove, or modify individual components without affecting the entire system.