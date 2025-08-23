"""
Configuration management system with JSON schema validation.
Replaces the rigid 4-parameter VBA interface with flexible configuration.
"""

import json
import os
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError


class ConfigManager:
    """
    Manages spiral stair configuration with schema validation.
    Supports both basic 4-parameter mode and enhanced configuration.
    """

    def __init__(self):
        """Initialize configuration manager with default schema."""
        self.schema = self._get_base_schema()
        self.config = self.get_default_config()

    def _get_base_schema(self) -> Dict[str, Any]:
        """
        Define JSON schema for spiral stair configuration.

        Returns:
            JSON schema dictionary
        """
        return {
            "type": "object",
            "properties": {
                "basic_parameters": {
                    "type": "object",
                    "properties": {
                        "center_pole_diameter": {
                            "type": "number",
                            "minimum": 1.0,
                            "maximum": 24.0,
                            "description": "Center pole diameter in inches",
                        },
                        "overall_height": {
                            "type": "number",
                            "minimum": 60.0,
                            "maximum": 240.0,
                            "description": "Total height of spiral stair in inches",
                        },
                        "outside_diameter": {
                            "type": "number",
                            "minimum": 36.0,
                            "maximum": 120.0,
                            "description": "Outside diameter of spiral stair in inches",
                        },
                        "total_rotation": {
                            "type": "number",
                            "minimum": 90.0,
                            "maximum": 720.0,
                            "description": "Total rotation in degrees",
                        },
                        "is_clockwise": {
                            "type": "boolean",
                            "description": "Clockwise rotation direction",
                        },
                        "mid_landing_enabled": {
                            "type": "boolean",
                            "description": "Enable mid-landing for stairs > 151 inches",
                            "default": False,
                        },
                        "mid_landing_tread_index": {
                            "type": "integer",
                            "minimum": -1,
                            "maximum": 50,
                            "description": "Zero-based index of tread to become mid-landing (-1 = disabled)",
                            "default": -1,
                        },
                    },
                    "required": [
                        "center_pole_diameter",
                        "overall_height",
                        "outside_diameter",
                        "total_rotation",
                    ],
                    "additionalProperties": False,
                },
                "compliance_settings": {
                    "type": "object",
                    "properties": {
                        "ibc_compliance_enabled": {
                            "type": "boolean",
                            "description": "Enable IBC building code compliance validation",
                        },
                        "educational_mode": {
                            "type": "boolean",
                            "description": "Educational mode allows non-compliant configurations",
                        },
                        "regional_code": {
                            "type": "string",
                            "enum": ["IBC_2021", "IBC_2018", "IBC_2015", "Custom"],
                            "default": "IBC_2021",
                            "description": "Building code standard to use for compliance",
                        },
                    },
                    "additionalProperties": False,
                },
                "component_settings": {
                    "type": "object",
                    "properties": {
                        "center_pole_enabled": {"type": "boolean", "default": True},
                        "treads_enabled": {"type": "boolean", "default": True},
                        "landings_enabled": {"type": "boolean", "default": True},
                    },
                    "additionalProperties": False,
                },
                "post_configuration": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "default": False,
                            "description": "Enable structural posts connecting treads",
                        },
                        "spacing": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3,
                            "default": 1,
                            "description": "Post spacing: 1=every tread, 2=every other tread, 3=every third tread",
                        },
                        "diameter": {
                            "type": "number",
                            "minimum": 0.5,
                            "maximum": 6.0,
                            "default": 2.0,
                            "description": "Post diameter in inches",
                        },
                        "material": {
                            "type": "string",
                            "enum": ["steel", "aluminum", "wood", "composite"],
                            "default": "steel",
                            "description": "Post material type",
                        },
                        "position": {
                            "type": "string",
                            "enum": ["outer_edge", "mid_tread", "inner_edge"],
                            "default": "outer_edge",
                            "description": "Post position on tread",
                        },
                    },
                    "additionalProperties": False,
                },
                "handrail_configuration": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "default": True,
                            "description": "Enable handrail generation",
                        },
                        "height_above_tread": {
                            "type": "number",
                            "minimum": 30.0,
                            "maximum": 42.0,
                            "default": 36.0,
                            "description": "Handrail height above tread in inches",
                        },
                        "diameter": {
                            "type": "number",
                            "minimum": 1.25,
                            "maximum": 2.5,
                            "default": 1.75,
                            "description": "Handrail diameter in inches",
                        },
                        "material": {
                            "type": "string",
                            "enum": ["steel", "aluminum", "wood", "composite"],
                            "default": "steel",
                            "description": "Handrail material type",
                        },
                        "continuous": {
                            "type": "boolean",
                            "default": True,
                            "description": "Continuous handrail (vs. segmented)",
                        },
                        "end_treatment": {
                            "type": "string",
                            "enum": ["cap", "return", "extended"],
                            "default": "cap",
                            "description": "Handrail end treatment",
                        },
                        "brackets": {
                            "type": "object",
                            "properties": {
                                "enabled": {
                                    "type": "boolean",
                                    "default": True,
                                    "description": "Enable handrail brackets",
                                },
                                "spacing_inches": {
                                    "type": "number",
                                    "minimum": 12.0,
                                    "maximum": 48.0,
                                    "default": 24.0,
                                    "description": "Bracket spacing in inches",
                                },
                                "bracket_type": {
                                    "type": "string",
                                    "enum": ["post_mount", "wall_mount", "under_mount"],
                                    "default": "post_mount",
                                    "description": "Bracket mounting type",
                                },
                            },
                            "additionalProperties": False,
                        },
                        "custom_offset": {
                            "type": "number",
                            "minimum": -10.0,
                            "maximum": 10.0,
                            "default": 0.0,
                            "description": "Custom offset from standard handrail position in inches (0 = automatic)",
                        },
                    },
                    "additionalProperties": False,
                },
                "picket_configuration": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "default": False,
                            "description": "Enable picket/baluster generation",
                        },
                        "spacing_inches": {
                            "type": "number",
                            "minimum": 1.0,
                            "maximum": 4.0,
                            "default": 3.5,
                            "description": "Picket spacing in inches (IBC max 4\")",
                        },
                        "style": {
                            "type": "string",
                            "enum": ["vertical", "horizontal"],
                            "default": "vertical",
                            "description": "Picket orientation",
                        },
                        "material": {
                            "type": "string",
                            "enum": ["aluminum", "steel", "wood", "composite"],
                            "default": "aluminum",
                            "description": "Picket material type",
                        },
                        "diameter": {
                            "type": "number",
                            "minimum": 0.375,
                            "maximum": 2.0,
                            "default": 0.75,
                            "description": "Picket diameter/width in inches (square pickets default)",
                        },
                        "quantity": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 20,
                            "default": 3,
                            "description": "Number of pickets per tread section",
                        },
                        "position": {
                            "type": "string",
                            "enum": ["outer", "inner", "middle"],
                            "default": "outer",
                            "description": "Position of pickets relative to tread",
                        },
                    },
                    "additionalProperties": False,
                },
                "advanced_settings": {
                    "type": "object",
                    "properties": {
                        "mock_mode": {
                            "type": "boolean",
                            "default": True,
                            "description": "Use mock AutoCAD interface for testing",
                        },
                        "generation_timeout": {
                            "type": "integer",
                            "minimum": 30,
                            "maximum": 300,
                            "default": 120,
                            "description": "Timeout for stair generation in seconds",
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "required": ["basic_parameters"],
            "additionalProperties": False,
        }

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration matching original VBA system.

        Returns:
            Default configuration dictionary
        """
        return {
            "basic_parameters": {
                "center_pole_diameter": 5.563,
                "overall_height": 144.0,
                "outside_diameter": 72.0,
                "total_rotation": 450.0,
                "is_clockwise": True,
            },
            "compliance_settings": {
                "ibc_compliance_enabled": True,
                "educational_mode": False,
                "regional_code": "IBC_2021",
            },
            "component_settings": {
                "center_pole_enabled": True,
                "treads_enabled": True,
                "landings_enabled": True,
            },
            "post_configuration": {
                "enabled": False,
                "spacing": 1,
                "diameter": 2.0,
                "material": "steel",
                "position": "outer_edge",
            },
            "handrail_configuration": {
                "enabled": True,
                "height_above_tread": 36.0,
                "diameter": 1.75,
                "material": "steel",
                "continuous": True,
                "end_treatment": "cap",
                "custom_offset": 0.0,
                "brackets": {
                    "enabled": True,
                    "spacing_inches": 24.0,
                    "bracket_type": "post_mount"
                }
            },
            "picket_configuration": {
                "enabled": True,
                "spacing_inches": 3.5,
                "style": "vertical",
                "material": "aluminum",
                "diameter": 0.75,
                "quantity": 3,
                "position": "outer",
            },
            "advanced_settings": {
                "mock_mode": True,
                "generation_timeout": 120
            }
        }

    def load_config(self, file_path: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file.

        Args:
            file_path: Path to JSON configuration file

        Returns:
            Dict[str, Any]: Loaded configuration

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValidationError: If configuration doesn't match schema
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Configuration file not found: {file_path}")

            with open(file_path, "r") as f:
                loaded_config = json.load(f)

            # Validate against schema
            validate(instance=loaded_config, schema=self.schema)

            # Merge with defaults to ensure all fields present
            self.config = self._merge_with_defaults(loaded_config)
            return self.config

        except (json.JSONDecodeError, ValidationError) as e:
            raise ValidationError(f"Invalid configuration: {str(e)}")

    def save_config(self, config: Dict[str, Any], file_path: str) -> bool:
        """
        Save configuration to JSON file.

        Args:
            config: Configuration to save
            file_path: Path to save configuration file

        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w") as f:
                json.dump(config, f, indent=2)

            return True

        except Exception as e:
            print(f"Failed to save configuration: {str(e)}")
            return False

    def validate_config(self, config: Optional[Dict[str, Any]] = None) -> tuple[bool, Dict[str, str]]:
        """
        Validate configuration against schema.

        Args:
            config: Configuration to validate (uses current if None)

        Returns:
            tuple: (is_valid, errors) where is_valid is a boolean and errors is a dict of error messages
        """
        config_to_validate = config if config is not None else self.config
        errors = {}

        try:
            validate(instance=config_to_validate, schema=self.schema)
            return True, errors
        except ValidationError as e:
            # Collect validation errors
            errors[str(e.schema_path)] = str(e.message)
            return False, errors

    def get_parameter(self, section: str, key: str) -> Any:
        """
        Get specific configuration parameter.

        Args:
            section: Configuration section name
            key: Parameter key within section

        Returns:
            Parameter value or None if not found
        """
        return self.config.get(section, {}).get(key)

    def set_parameter(self, section: str, key: str, value: Any) -> bool:
        """
        Set specific configuration parameter.

        Args:
            section: Configuration section name
            key: Parameter key within section
            value: New parameter value

        Returns:
            bool: True if set successfully and valid, False otherwise
        """
        if section not in self.config:
            self.config[section] = {}

        self.config[section][key] = value

        try:
            self.validate_config()
            return True
        except ValidationError:
            # Revert change if invalid
            del self.config[section][key]
            return False

    def get_basic_parameters(self) -> Dict[str, Any]:
        """
        Get the 4 basic parameters for VBA compatibility.

        Returns:
            Dict with center_pole_diameter, overall_height, outside_diameter, total_rotation
        """
        return self.config.get("basic_parameters", {})

    def _merge_with_defaults(self, loaded_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge loaded configuration with defaults to ensure completeness.

        Args:
            loaded_config: Configuration loaded from file

        Returns:
            Complete configuration with defaults filled in
        """
        result = self.get_default_config().copy()

        for section, values in loaded_config.items():
            if section in result and isinstance(values, dict):
                result[section].update(values)
            else:
                result[section] = values

        return result
