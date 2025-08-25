# Configuration Schema Documentation
## JSON Configuration System for Spiral Stair Creator

### Overview

The modular spiral stair creator uses a comprehensive JSON configuration system to define all parameters for stair generation. This document details the complete schema, validation rules, and usage examples.

---

## Complete Configuration Schema

### JSON Schema Definition

**File**: `src/schemas/stair_config.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Spiral Stair Configuration",
  "description": "Complete configuration schema for modular spiral stair creator",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "config_version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$",
          "description": "Configuration schema version"
        },
        "created_date": {
          "type": "string",
          "format": "date-time",
          "description": "Configuration creation timestamp"
        },
        "created_by": {
          "type": "string",
          "description": "Configuration creator"
        },
        "project_name": {
          "type": "string",
          "description": "Project or drawing name"
        },
        "description": {
          "type": "string",
          "description": "Configuration description"
        },
        "tags": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Searchable tags"
        }
      },
      "required": ["config_version"]
    },
    "basic_parameters": {
      "type": "object",
      "description": "Core stair dimensions and geometry",
      "properties": {
        "center_pole_diameter": {
          "type": "number",
          "minimum": 3.0,
          "maximum": 12.75,
          "enum": [3, 3.5, 4, 4.5, 5, 5.56, 6, 6.625, 8, 8.625, 10.75, 12.75],
          "description": "Center pole diameter in inches (available sizes)"
        },
        "overall_height": {
          "type": "number",
          "minimum": 24.0,
          "maximum": 240.0,
          "description": "Total height from finished floor to finished floor (inches)"
        },
        "outside_diameter": {
          "type": "number",
          "minimum": 36.0,
          "maximum": 120.0,
          "description": "Overall stair diameter (inches)"
        },
        "total_rotation": {
          "type": "number",
          "minimum": 180.0,
          "maximum": 720.0,
          "description": "Total rotation from bottom to top (degrees)"
        },
        "is_clockwise": {
          "type": "boolean",
          "description": "Rotation direction (true = clockwise, false = counterclockwise)"
        },
        "units": {
          "type": "string",
          "enum": ["inches", "feet", "millimeters", "centimeters"],
          "default": "inches",
          "description": "Units for all dimensions"
        }
      },
      "required": [
        "center_pole_diameter",
        "overall_height", 
        "outside_diameter",
        "total_rotation",
        "is_clockwise"
      ]
    },
    "tread_configuration": {
      "type": "object",
      "description": "Tread-specific parameters",
      "properties": {
        "thickness": {
          "type": "number",
          "minimum": 0.125,
          "maximum": 2.0,
          "default": 0.25,
          "description": "Tread thickness (inches)"
        },
        "riser_height_max": {
          "type": "number",
          "minimum": 6.0,
          "maximum": 12.0,
          "default": 9.5,
          "description": "Maximum riser height per IBC (inches)"
        },
        "nosing_projection": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 2.0,
          "default": 0.75,
          "description": "Tread nosing projection (inches)"
        },
        "material": {
          "type": "string",
          "enum": ["aluminum", "steel", "wood", "concrete", "composite"],
          "default": "aluminum",
          "description": "Tread material type"
        },
        "surface_finish": {
          "type": "string",
          "enum": ["smooth", "textured", "perforated", "diamond_plate"],
          "default": "textured",
          "description": "Tread surface finish for slip resistance"
        },
        "custom_treads": {
          "type": "array",
          "description": "Custom modifications to individual treads",
          "items": {
            "type": "object",
            "properties": {
              "index": {
                "type": "integer",
                "minimum": 0,
                "description": "Tread index (0-based)"
              },
              "custom_angle": {
                "type": "number",
                "description": "Override default angle for this tread"
              },
              "custom_height": {
                "type": "number",
                "description": "Override default height for this tread"
              },
              "custom_material": {
                "type": "string",
                "enum": ["aluminum", "steel", "wood", "concrete", "composite"]
              }
            },
            "required": ["index"]
          }
        }
      }
    },
    "picket_configuration": {
      "type": "object",
      "description": "Picket/baluster system configuration",
      "properties": {
        "enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable picket generation"
        },
        "spacing_inches": {
          "type": "number",
          "minimum": 2.0,
          "maximum": 4.0,
          "default": 3.5,
          "description": "Maximum picket spacing per IBC (inches)"
        },
        "height_ratio": {
          "type": "number",
          "minimum": 0.5,
          "maximum": 1.0,
          "default": 0.85,
          "description": "Picket height as ratio of tread-to-handrail distance"
        },
        "style": {
          "type": "string",
          "enum": ["vertical", "horizontal", "crossed", "decorative"],
          "default": "vertical",
          "description": "Picket arrangement style"
        },
        "material": {
          "type": "string",
          "enum": ["aluminum", "steel", "wood", "composite"],
          "default": "aluminum",
          "description": "Picket material"
        },
        "connection_type": {
          "type": "string",
          "enum": ["welded", "bolted", "mechanical", "glued"],
          "default": "welded",
          "description": "Connection method to treads and handrail"
        },
        "picket_diameter": {
          "type": "number",
          "minimum": 0.25,
          "maximum": 2.0,
          "default": 0.75,
          "description": "Individual picket diameter (inches)"
        },
        "decorative_pattern": {
          "type": "string",
          "enum": ["none", "diamond", "spiral", "wave", "custom"],
          "default": "none",
          "description": "Decorative pattern for artistic pickets"
        },
        "color_code": {
          "type": "integer",
          "minimum": 0,
          "maximum": 255,
          "default": 7,
          "description": "AutoCAD color code for pickets"
        },
        "horizontal_rails": {
          "type": "object",
          "properties": {
            "enabled": {
              "type": "boolean",
              "default": false,
              "description": "Add horizontal rails between pickets"
            },
            "rail_count": {
              "type": "integer",
              "minimum": 1,
              "maximum": 3,
              "default": 1,
              "description": "Number of horizontal rails"
            },
            "rail_diameter": {
              "type": "number",
              "minimum": 0.25,
              "maximum": 1.0,
              "default": 0.5,
              "description": "Horizontal rail diameter (inches)"
            }
          }
        }
      }
    },
    "handrail_configuration": {
      "type": "object",
      "description": "Handrail system configuration",
      "properties": {
        "enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable handrail generation"
        },
        "height_above_tread": {
          "type": "number",
          "minimum": 34.0,
          "maximum": 38.0,
          "default": 36.0,
          "description": "Handrail height above tread nosing per IBC (inches)"
        },
        "diameter": {
          "type": "number",
          "minimum": 1.25,
          "maximum": 2.625,
          "default": 1.5,
          "description": "Handrail diameter for proper grip (inches)"
        },
        "material": {
          "type": "string",
          "enum": ["aluminum", "steel", "wood", "composite"],
          "default": "aluminum",
          "description": "Handrail material"
        },
        "continuous": {
          "type": "boolean",
          "default": true,
          "description": "Continuous rail vs segmented sections"
        },
        "mounting_height": {
          "type": "number",
          "minimum": 1.0,
          "maximum": 6.0,
          "default": 2.0,
          "description": "Distance from stair edge to handrail centerline (inches)"
        },
        "end_treatment": {
          "type": "string",
          "enum": ["cap", "return", "extension", "volute"],
          "default": "cap",
          "description": "Handrail end treatment style"
        },
        "brackets": {
          "type": "object",
          "properties": {
            "enabled": {
              "type": "boolean",
              "default": true,
              "description": "Add handrail mounting brackets"
            },
            "spacing_inches": {
              "type": "number",
              "minimum": 12.0,
              "maximum": 48.0,
              "default": 24.0,
              "description": "Bracket spacing (inches)"
            },
            "bracket_type": {
              "type": "string",
              "enum": ["wall_mount", "post_mount", "underside"],
              "default": "post_mount"
            }
          }
        },
        "color_code": {
          "type": "integer",
          "minimum": 0,
          "maximum": 255,
          "default": 5,
          "description": "AutoCAD color code for handrail"
        }
      }
    },
    "post_configuration": {
      "type": "object",
      "description": "Structural post configuration",
      "properties": {
        "enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable post generation"
        },
        "spacing_treads": {
          "type": "integer",
          "minimum": 2,
          "maximum": 8,
          "default": 4,
          "description": "Post spacing in number of treads"
        },
        "post_diameter": {
          "type": "number",
          "minimum": 1.0,
          "maximum": 4.0,
          "default": 2.0,
          "description": "Post diameter (inches)"
        },
        "height_above_handrail": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 6.0,
          "default": 2.0,
          "description": "Post height above handrail (inches)"
        },
        "connection_type": {
          "type": "string",
          "enum": ["welded", "bolted", "socket", "threaded"],
          "default": "welded",
          "description": "Post connection method"
        },
        "base_plate": {
          "type": "object",
          "properties": {
            "enabled": {
              "type": "boolean",
              "default": true,
              "description": "Add base plates for posts"
            },
            "size_inches": {
              "type": "number",
              "minimum": 4.0,
              "maximum": 12.0,
              "default": 6.0,
              "description": "Square base plate size (inches)"
            },
            "thickness": {
              "type": "number",
              "minimum": 0.25,
              "maximum": 1.0,
              "default": 0.5,
              "description": "Base plate thickness (inches)"
            }
          }
        },
        "material": {
          "type": "string",
          "enum": ["aluminum", "steel", "stainless_steel"],
          "default": "steel",
          "description": "Post material"
        },
        "color_code": {
          "type": "integer",
          "minimum": 0,
          "maximum": 255,
          "default": 8,
          "description": "AutoCAD color code for posts"
        }
      }
    },
    "compliance_settings": {
      "type": "object",
      "description": "Building code compliance configuration",
      "properties": {
        "enforce_ibc": {
          "type": "boolean",
          "default": true,
          "description": "Enforce International Building Code requirements"
        },
        "allow_overrides": {
          "type": "boolean",
          "default": false,
          "description": "Allow user to override code violations with warnings"
        },
        "regional_code": {
          "type": "string",
          "enum": ["IBC_2021", "IBC_2018", "IRC_2021", "IRC_2018", "CUSTOM"],
          "default": "IBC_2021",
          "description": "Building code version to enforce"
        },
        "accessibility_compliance": {
          "type": "string",
          "enum": ["none", "ADA", "ANSI_A117.1"],
          "default": "none",
          "description": "Accessibility standard compliance"
        },
        "custom_requirements": {
          "type": "object",
          "description": "Custom compliance requirements",
          "properties": {
            "walkline_width_min": {
              "type": "number",
              "minimum": 6.0,
              "default": 6.75,
              "description": "Minimum walkline width (inches)"
            },
            "walk_space_min": {
              "type": "number", 
              "minimum": 24.0,
              "default": 26.0,
              "description": "Minimum clear walk space (inches)"
            },
            "picket_spacing_max": {
              "type": "number",
              "minimum": 3.0,
              "maximum": 6.0,
              "default": 4.0,
              "description": "Maximum picket spacing (inches)"
            },
            "handrail_height_min": {
              "type": "number",
              "default": 34.0
            },
            "handrail_height_max": {
              "type": "number",
              "default": 38.0
            },
            "riser_height_max": {
              "type": "number",
              "default": 9.5
            },
            "midlanding_threshold": {
              "type": "number",
              "default": 151.0,
              "description": "Height requiring midlanding (inches)"
            }
          }
        }
      }
    },
    "generation_options": {
      "type": "object",
      "description": "Generation and output options",
      "properties": {
        "create_center_pole": {
          "type": "boolean",
          "default": true
        },
        "create_treads": {
          "type": "boolean", 
          "default": true
        },
        "create_landings": {
          "type": "boolean",
          "default": true
        },
        "create_pickets": {
          "type": "boolean",
          "default": true
        },
        "create_handrails": {
          "type": "boolean",
          "default": true
        },
        "create_posts": {
          "type": "boolean",
          "default": true
        },
        "layer_organization": {
          "type": "object",
          "properties": {
            "use_layers": {
              "type": "boolean",
              "default": true,
              "description": "Organize components on separate layers"
            },
            "layer_prefix": {
              "type": "string",
              "default": "SPIRAL_STAIR",
              "description": "Prefix for layer names"
            },
            "layer_names": {
              "type": "object",
              "properties": {
                "center_pole": {"type": "string", "default": "CENTER_POLE"},
                "treads": {"type": "string", "default": "TREADS"},
                "landings": {"type": "string", "default": "LANDINGS"},
                "pickets": {"type": "string", "default": "PICKETS"},
                "handrails": {"type": "string", "default": "HANDRAILS"},
                "posts": {"type": "string", "default": "POSTS"}
              }
            }
          }
        },
        "summary_annotation": {
          "type": "object",
          "properties": {
            "enabled": {
              "type": "boolean",
              "default": true,
              "description": "Add summary text annotation to drawing"
            },
            "position": {
              "type": "array",
              "items": {"type": "number"},
              "minItems": 2,
              "maxItems": 3,
              "default": [100, 50, 0],
              "description": "Annotation position [x, y, z]"
            },
            "text_height": {
              "type": "number",
              "minimum": 1.0,
              "maximum": 10.0,
              "default": 2.0,
              "description": "Text height for annotations"
            }
          }
        }
      }
    },
    "performance_settings": {
      "type": "object",
      "description": "Performance and optimization settings",
      "properties": {
        "batch_operations": {
          "type": "boolean",
          "default": true,
          "description": "Batch AutoCAD operations for better performance"
        },
        "regen_frequency": {
          "type": "string",
          "enum": ["never", "per_module", "at_end"],
          "default": "at_end",
          "description": "When to regenerate the drawing"
        },
        "progress_reporting": {
          "type": "boolean",
          "default": true,
          "description": "Enable progress reporting during generation"
        },
        "max_entities_per_batch": {
          "type": "integer",
          "minimum": 10,
          "maximum": 1000,
          "default": 100,
          "description": "Maximum entities per batch operation"
        }
      }
    }
  },
  "required": [
    "metadata",
    "basic_parameters"
  ],
  "additionalProperties": false
}
```

---

## Default Configuration Template

### Complete Default Configuration

**File**: `config/default_config.json`

```json
{
  "metadata": {
    "config_version": "1.0.0",
    "created_date": "2024-01-01T00:00:00Z",
    "created_by": "System",
    "project_name": "Default Spiral Stair",
    "description": "Standard aluminum spiral staircase with IBC compliance",
    "tags": ["default", "aluminum", "residential"]
  },
  "basic_parameters": {
    "center_pole_diameter": 5.0,
    "overall_height": 120.0,
    "outside_diameter": 72.0,
    "total_rotation": 360.0,
    "is_clockwise": true,
    "units": "inches"
  },
  "tread_configuration": {
    "thickness": 0.25,
    "riser_height_max": 9.5,
    "nosing_projection": 0.75,
    "material": "aluminum",
    "surface_finish": "textured",
    "custom_treads": []
  },
  "picket_configuration": {
    "enabled": true,
    "spacing_inches": 3.5,
    "height_ratio": 0.85,
    "style": "vertical",
    "material": "aluminum",
    "connection_type": "welded",
    "picket_diameter": 0.75,
    "decorative_pattern": "none",
    "color_code": 7,
    "horizontal_rails": {
      "enabled": false,
      "rail_count": 1,
      "rail_diameter": 0.5
    }
  },
  "handrail_configuration": {
    "enabled": true,
    "height_above_tread": 36.0,
    "diameter": 1.5,
    "material": "aluminum",
    "continuous": true,
    "mounting_height": 2.0,
    "end_treatment": "cap",
    "brackets": {
      "enabled": true,
      "spacing_inches": 24.0,
      "bracket_type": "post_mount"
    },
    "color_code": 5
  },
  "post_configuration": {
    "enabled": true,
    "spacing_treads": 4,
    "post_diameter": 2.0,
    "height_above_handrail": 2.0,
    "connection_type": "welded",
    "base_plate": {
      "enabled": true,
      "size_inches": 6.0,
      "thickness": 0.5
    },
    "material": "steel",
    "color_code": 8
  },
  "compliance_settings": {
    "enforce_ibc": true,
    "allow_overrides": false,
    "regional_code": "IBC_2021",
    "accessibility_compliance": "none",
    "custom_requirements": {
      "walkline_width_min": 6.75,
      "walk_space_min": 26.0,
      "picket_spacing_max": 4.0,
      "handrail_height_min": 34.0,
      "handrail_height_max": 38.0,
      "riser_height_max": 9.5,
      "midlanding_threshold": 151.0
    }
  },
  "generation_options": {
    "create_center_pole": true,
    "create_treads": true,
    "create_landings": true,
    "create_pickets": true,
    "create_handrails": true,
    "create_posts": true,
    "layer_organization": {
      "use_layers": true,
      "layer_prefix": "SPIRAL_STAIR",
      "layer_names": {
        "center_pole": "CENTER_POLE",
        "treads": "TREADS",
        "landings": "LANDINGS",
        "pickets": "PICKETS",
        "handrails": "HANDRAILS",
        "posts": "POSTS"
      }
    },
    "summary_annotation": {
      "enabled": true,
      "position": [100, 50, 0],
      "text_height": 2.0
    }
  },
  "performance_settings": {
    "batch_operations": true,
    "regen_frequency": "at_end",
    "progress_reporting": true,
    "max_entities_per_batch": 100
  }
}
```

---

## Configuration Examples

### Example 1: Compact Residential Stair

**File**: `examples/compact_residential.json`

```json
{
  "metadata": {
    "config_version": "1.0.0",
    "project_name": "Compact Residential Stair",
    "description": "Small spiral stair for residential use",
    "tags": ["residential", "compact", "wood"]
  },
  "basic_parameters": {
    "center_pole_diameter": 4.0,
    "overall_height": 96.0,
    "outside_diameter": 60.0,
    "total_rotation": 270.0,
    "is_clockwise": true
  },
  "picket_configuration": {
    "enabled": true,
    "spacing_inches": 3.0,
    "style": "vertical",
    "material": "wood"
  },
  "handrail_configuration": {
    "enabled": true,
    "material": "wood",
    "end_treatment": "volute"
  }
}
```

### Example 2: Commercial Heavy-Duty Stair

**File**: `examples/commercial_heavy_duty.json`

```json
{
  "metadata": {
    "config_version": "1.0.0",
    "project_name": "Commercial Heavy-Duty Stair",
    "description": "Steel spiral stair for commercial use",
    "tags": ["commercial", "steel", "heavy-duty"]
  },
  "basic_parameters": {
    "center_pole_diameter": 8.0,
    "overall_height": 144.0,
    "outside_diameter": 96.0,
    "total_rotation": 450.0,
    "is_clockwise": false
  },
  "tread_configuration": {
    "material": "steel",
    "surface_finish": "diamond_plate",
    "thickness": 0.375
  },
  "picket_configuration": {
    "material": "steel",
    "connection_type": "welded",
    "horizontal_rails": {
      "enabled": true,
      "rail_count": 2
    }
  },
  "post_configuration": {
    "post_diameter": 3.0,
    "spacing_treads": 3,
    "base_plate": {
      "size_inches": 8.0,
      "thickness": 0.75
    }
  },
  "compliance_settings": {
    "accessibility_compliance": "ADA"
  }
}
```

### Example 3: Decorative Artistic Stair

**File**: `examples/decorative_artistic.json`

```json
{
  "metadata": {
    "config_version": "1.0.0",
    "project_name": "Decorative Artistic Stair",
    "description": "Ornamental spiral stair with decorative elements",
    "tags": ["decorative", "artistic", "custom"]
  },
  "basic_parameters": {
    "center_pole_diameter": 6.0,
    "overall_height": 108.0,
    "outside_diameter": 84.0,
    "total_rotation": 540.0,
    "is_clockwise": true
  },
  "picket_configuration": {
    "style": "crossed",
    "decorative_pattern": "spiral",
    "material": "steel"
  },
  "handrail_configuration": {
    "diameter": 2.0,
    "end_treatment": "volute"
  },
  "compliance_settings": {
    "allow_overrides": true
  }
}
```

---

## Validation Rules and Constraints

### Advanced Cross-Parameter Validation

#### Extensible Validation Framework
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
from jsonschema import Draft7Validator
import jsonschema

class ValidationRule(ABC):
    """Abstract base class for custom validation rules"""
    
    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> List[str]:
        """Return list of validation errors"""
        pass
    
    @abstractmethod
    def get_rule_name(self) -> str:
        """Return unique rule identifier"""
        pass
    
    @abstractmethod
    def get_severity(self) -> str:
        """Return severity: 'error', 'warning', 'info'"""
        pass

class GeometricConstraintsRule(ValidationRule):
    """Validates geometric relationships between parameters"""
    
    def validate(self, config: Dict[str, Any]) -> List[str]:
        errors = []
        basic = config.get("basic_parameters", {})
        
        center_dia = basic.get("center_pole_diameter", 0)
        outside_dia = basic.get("outside_diameter", 0)
        
        # Outside diameter must be significantly larger than center pole
        if outside_dia <= center_dia + 24:  # Minimum 12" on each side
            errors.append(
                f"Outside diameter ({outside_dia}) must be at least "
                f"{center_dia + 24} inches for proper walkway"
            )
        
        # Check walkline width compliance
        height = basic.get("overall_height", 0)
        rotation = basic.get("total_rotation", 0)
        
        if height > 0 and rotation > 0:
            num_treads = math.ceil(height / 9.5)
            tread_angle_rad = math.radians(rotation / num_treads)
            walkline_radius = center_dia / 2 + 12
            walkline_width = walkline_radius * tread_angle_rad
            
            if walkline_width < 6.75:
                errors.append(
                    f"Configuration results in walkline width of {walkline_width:.2f} "
                    f"inches, which is less than 6.75 inches required"
                )
        
        return errors
    
    def get_rule_name(self) -> str:
        return "geometric_constraints"
    
    def get_severity(self) -> str:
        return "error"

class IBCComplianceRule(ValidationRule):
    """Validates IBC building code compliance"""
    
    def __init__(self, code_version: str = "IBC_2021"):
        self.code_version = code_version
        self.load_code_requirements()
    
    def load_code_requirements(self):
        """Load requirements based on code version"""
        self.requirements = {
            "walkline_width_min": 6.75,
            "walk_space_min": 26.0,
            "handrail_height_min": 34.0,
            "handrail_height_max": 38.0,
            "picket_spacing_max": 4.0,
            "riser_height_max": 9.5,
            "midlanding_threshold": 151.0
        }
    
    def validate(self, config: Dict[str, Any]) -> List[str]:
        errors = []
        compliance = config.get("compliance_settings", {})
        
        if not compliance.get("enforce_ibc", True):
            return []
        
        # Validate handrail height
        handrail_config = config.get("handrail_configuration", {})
        if handrail_config.get("enabled", True):
            height = handrail_config.get("height_above_tread", 36.0)
            if height < self.requirements["handrail_height_min"] or height > self.requirements["handrail_height_max"]:
                errors.append(
                    f"Handrail height {height}\" must be between "
                    f"{self.requirements['handrail_height_min']}\" and "
                    f"{self.requirements['handrail_height_max']}\" per IBC R311.7.8.1"
                )
        
        # Validate picket spacing
        picket_config = config.get("picket_configuration", {})
        if picket_config.get("enabled", True):
            spacing = picket_config.get("spacing_inches", 4.0)
            if spacing > self.requirements["picket_spacing_max"]:
                errors.append(
                    f"Picket spacing {spacing}\" exceeds {self.requirements['picket_spacing_max']}\" "
                    f"maximum per IBC R311.7.8 (4-inch sphere rule)"
                )
        
        # Validate midlanding requirement
        basic = config.get("basic_parameters", {})
        height = basic.get("overall_height", 0)
        if height > self.requirements["midlanding_threshold"]:
            errors.append(
                f"Overall height {height}\" exceeds {self.requirements['midlanding_threshold']}\" "
                f"limit without midlanding per IBC R311.7.3"
            )
        
        return errors
    
    def get_rule_name(self) -> str:
        return f"ibc_compliance_{self.code_version.lower()}"
    
    def get_severity(self) -> str:
        return "error"

class MaterialCompatibilityRule(ValidationRule):
    """Validates material compatibility across components"""
    
    GALVANIC_INCOMPATIBLE = {
        ("aluminum", "steel"): "Aluminum and steel may cause galvanic corrosion",
        ("aluminum", "copper"): "Aluminum and copper are galvanically incompatible",
    }
    
    def validate(self, config: Dict[str, Any]) -> List[str]:
        warnings = []
        
        tread_material = config.get("tread_configuration", {}).get("material", "aluminum")
        picket_material = config.get("picket_configuration", {}).get("material", "aluminum")
        handrail_material = config.get("handrail_configuration", {}).get("material", "aluminum")
        post_material = config.get("post_configuration", {}).get("material", "steel")
        
        # Check all material combinations
        materials = [tread_material, picket_material, handrail_material, post_material]
        for i, mat1 in enumerate(materials):
            for mat2 in materials[i+1:]:
                pair = tuple(sorted([mat1, mat2]))
                if pair in self.GALVANIC_INCOMPATIBLE:
                    warnings.append(
                        f"Warning: {self.GALVANIC_INCOMPATIBLE[pair]}. "
                        f"Consider using isolation or protective coatings."
                    )
        
        return warnings
    
    def get_rule_name(self) -> str:
        return "material_compatibility"
    
    def get_severity(self) -> str:
        return "warning"

class AdvancedConfigurationValidator:
    """Enhanced configuration validator with extensible rules"""
    
    def __init__(self, schema_path: str):
        self.schema = self._load_schema(schema_path)
        self.rules: List[ValidationRule] = []
        self.setup_default_rules()
    
    def setup_default_rules(self):
        """Setup default validation rules"""
        self.add_rule(GeometricConstraintsRule())
        self.add_rule(IBCComplianceRule())
        self.add_rule(MaterialCompatibilityRule())
    
    def add_rule(self, rule: ValidationRule):
        """Add custom validation rule"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str):
        """Remove validation rule by name"""
        self.rules = [r for r in self.rules if r.get_rule_name() != rule_name]
    
    def validate_configuration(self, config: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
        """Comprehensive configuration validation"""
        validation_results = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # JSON Schema validation first
        try:
            jsonschema.validate(instance=config, schema=self.schema)
        except jsonschema.ValidationError as e:
            validation_results["errors"].append(f"Schema validation: {e.message}")
        
        # Custom rule validation
        for rule in self.rules:
            try:
                rule_errors = rule.validate(config)
                severity = rule.get_severity()
                validation_results[severity + "s"].extend(rule_errors)
            except Exception as e:
                validation_results["errors"].append(
                    f"Validation rule '{rule.get_rule_name()}' failed: {str(e)}"
                )
        
        is_valid = len(validation_results["errors"]) == 0
        return is_valid, validation_results
```

#### Enhanced JSON Schema with Dependencies

**Complete Schema with Advanced Validations:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Spiral Stair Configuration",
  "description": "Complete configuration schema with advanced validation",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "config_version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$",
          "description": "Configuration schema version (semantic versioning)"
        },
        "created_date": {
          "type": "string",
          "format": "date-time"
        },
        "created_by": {
          "type": "string",
          "maxLength": 100
        },
        "project_name": {
          "type": "string",
          "maxLength": 200
        },
        "description": {
          "type": "string",
          "maxLength": 1000
        },
        "tags": {
          "type": "array",
          "items": {"type": "string", "maxLength": 50},
          "maxItems": 20
        },
        "custom_fields": {
          "type": "object",
          "description": "User-defined extensible fields",
          "additionalProperties": {
            "oneOf": [
              {"type": "string"},
              {"type": "number"},
              {"type": "boolean"},
              {"type": "array"},
              {"type": "object"}
            ]
          }
        }
      },
      "required": ["config_version"],
      "additionalProperties": false
    },
    "basic_parameters": {
      "type": "object",
      "properties": {
        "center_pole_diameter": {
          "type": "number",
          "minimum": 3.0,
          "maximum": 12.75,
          "enum": [3, 3.5, 4, 4.5, 5, 5.56, 6, 6.625, 8, 8.625, 10.75, 12.75]
        },
        "overall_height": {
          "type": "number",
          "minimum": 24.0,
          "maximum": 240.0
        },
        "outside_diameter": {
          "type": "number",
          "minimum": 36.0,
          "maximum": 120.0
        },
        "total_rotation": {
          "type": "number",
          "minimum": 180.0,
          "maximum": 720.0
        },
        "is_clockwise": {
          "type": "boolean"
        },
        "units": {
          "type": "string",
          "enum": ["inches", "feet", "millimeters", "centimeters", "meters"],
          "default": "inches"
        }
      },
      "required": [
        "center_pole_diameter", "overall_height", 
        "outside_diameter", "total_rotation", "is_clockwise"
      ],
      "additionalProperties": false,
      "dependencies": {
        "outside_diameter": {
          "allOf": [
            {
              "if": {
                "properties": {
                  "center_pole_diameter": {"type": "number"},
                  "outside_diameter": {"type": "number"}
                }
              },
              "then": {
                "properties": {
                  "outside_diameter": {
                    "minimum": {"$data": "1/center_pole_diameter + 24"}
                  }
                }
              }
            }
          ]
        }
      }
    }
  },
  "definitions": {
    "unit_conversion": {
      "type": "object",
      "properties": {
        "from_unit": {"type": "string"},
        "to_unit": {"type": "string"},
        "conversion_factor": {"type": "number"}
      }
    },
    "validation_override": {
      "type": "object",
      "properties": {
        "rule_name": {"type": "string"},
        "override_reason": {"type": "string"},
        "approved_by": {"type": "string"},
        "approval_date": {"type": "string", "format": "date-time"}
      }
    }
  },
  "required": ["metadata", "basic_parameters"],
  "additionalProperties": false
}
```
```

#### Material Compatibility
```python
def validate_material_compatibility(config):
    """Validate material choices are compatible"""
    errors = []
    
    tread_material = config.get("tread_configuration", {}).get("material", "aluminum")
    picket_material = config.get("picket_configuration", {}).get("material", "aluminum")
    handrail_material = config.get("handrail_configuration", {}).get("material", "aluminum")
    post_material = config.get("post_configuration", {}).get("material", "steel")
    
    # Check for galvanic corrosion potential
    if tread_material == "aluminum" and post_material == "steel":
        errors.append(
            "Warning: Aluminum treads with steel posts may cause galvanic corrosion. "
            "Consider using aluminum posts or adding isolation."
        )
    
    return errors
```

### IBC Compliance Validation

```python
def validate_ibc_compliance(config):
    """Comprehensive IBC compliance checking"""
    errors = []
    compliance = config.get("compliance_settings", {})
    
    if not compliance.get("enforce_ibc", True):
        return []  # Skip if IBC not enforced
    
    # Handrail height validation
    handrail_config = config.get("handrail_configuration", {})
    if handrail_config.get("enabled", True):
        height = handrail_config.get("height_above_tread", 36.0)
        if height < 34.0 or height > 38.0:
            errors.append(
                f"Handrail height {height} inches violates IBC requirement "
                f"of 34-38 inches (R311.7.8.1)"
            )
    
    # Picket spacing validation
    picket_config = config.get("picket_configuration", {})
    if picket_config.get("enabled", True):
        spacing = picket_config.get("spacing_inches", 4.0)
        if spacing > 4.0:
            errors.append(
                f"Picket spacing {spacing} inches exceeds 4-inch sphere rule "
                f"(R311.7.8)"
            )
    
    # Midlanding requirement
    basic = config.get("basic_parameters", {})
    height = basic.get("overall_height", 0)
    if height > 151:
        errors.append(
            f"Overall height {height} inches exceeds 151-inch limit "
            f"without midlanding (R311.7.3)"
        )
    
    return errors
```

---

## Configuration Management

### Loading and Saving

```python
class ConfigurationManager:
    def __init__(self, schema_path: str):
        self.schema = self._load_schema(schema_path)
        
    def load_configuration(self, config_path: str) -> Dict[str, Any]:
        """Load and validate configuration from file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Validate against schema
            is_valid, errors = self.validate_configuration(config)
            if not is_valid:
                raise ValueError(f"Configuration validation failed: {errors}")
                
            # Apply defaults for missing values
            config = self._apply_defaults(config)
            
            return config
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
            
    def save_configuration(self, config: Dict[str, Any], config_path: str):
        """Save configuration to file with validation"""
        # Update metadata
        if "metadata" not in config:
            config["metadata"] = {}
            
        config["metadata"]["created_date"] = datetime.now().isoformat()
        config["metadata"]["config_version"] = "1.0.0"
        
        # Validate before saving
        is_valid, errors = self.validate_configuration(config)
        if not is_valid:
            raise ValueError(f"Cannot save invalid configuration: {errors}")
            
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2, sort_keys=True)
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
            
    def validate_configuration(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Comprehensive configuration validation"""
        errors = []
        
        # JSON schema validation
        try:
            jsonschema.validate(instance=config, schema=self.schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation: {e.message}")
            
        # Custom validation rules
        errors.extend(validate_geometric_constraints(config))
        errors.extend(validate_material_compatibility(config))
        errors.extend(validate_ibc_compliance(config))
        
        return len(errors) == 0, errors
```

### Configuration Migration

```python
def migrate_configuration(config: Dict[str, Any], target_version: str) -> Dict[str, Any]:
    """Migrate configuration to newer schema version"""
    current_version = config.get("metadata", {}).get("config_version", "1.0.0")
    
    if current_version == target_version:
        return config
        
    # Migration logic for different versions
    if current_version == "1.0.0" and target_version == "1.1.0":
        # Example migration: add new fields with defaults
        if "performance_settings" not in config:
            config["performance_settings"] = {
                "batch_operations": True,
                "regen_frequency": "at_end",
                "progress_reporting": True
            }
            
        config["metadata"]["config_version"] = target_version
        
    return config
```

This comprehensive configuration schema provides complete control over all aspects of spiral stair generation while maintaining strict validation and IBC compliance.