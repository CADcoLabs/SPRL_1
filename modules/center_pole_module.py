"""
Center Pole Module - Migrated from VBA Module1.bas CreateCenterPole function.
Creates the central support pole for the spiral staircase.
"""

import math
from typing import Dict, Any, List
from core.base_component import BaseStairComponent


class CenterPoleModule(BaseStairComponent):
    """
    Center pole component that creates the central support cylinder.

    Migrated from VBA CreateCenterPole function with identical geometry:
    - Creates cylinder at origin (0,0,0)
    - Diameter from configuration
    - Height matches overall stair height
    - Color 251 (same as VBA)
    - Positioned with center at Z = height/2
    """

    def __init__(self):
        """Initialize center pole module."""
        super().__init__("CenterPole")

    def validate_parameters(self, config: Dict[str, Any]) -> bool:
        """
        Validate center pole parameters.

        Args:
            config: Configuration dictionary

        Returns:
            bool: True if parameters are valid

        Raises:
            ValueError: If parameters are invalid
        """
        basic_params = config.get("basic_parameters", {})

        # Get required parameters
        center_pole_diameter = basic_params.get("center_pole_diameter")
        overall_height = basic_params.get("overall_height")

        # Validate center pole diameter
        if center_pole_diameter is None:
            raise ValueError("center_pole_diameter is required")
        if not isinstance(center_pole_diameter, (int, float)):
            raise ValueError("center_pole_diameter must be a number")
        if center_pole_diameter <= 0:
            raise ValueError("center_pole_diameter must be > 0")
        if center_pole_diameter > 24.0:
            raise ValueError("center_pole_diameter must be <= 24 inches")

        # Validate overall height
        if overall_height is None:
            raise ValueError("overall_height is required")
        if not isinstance(overall_height, (int, float)):
            raise ValueError("overall_height must be a number")
        if overall_height <= 0:
            raise ValueError("overall_height must be > 0")
        if overall_height > 240.0:
            raise ValueError("overall_height must be <= 240 inches")

        return True

    def generate_geometry(self, autocad_interface, config: Dict[str, Any]) -> bool:
        """
        Generate center pole geometry in AutoCAD.

        Recreates the exact VBA logic:
        1. Create cylinder at origin with specified diameter and height
        2. Set color to 251 (matching VBA)
        3. Transform to position center at Z = height/2

        Args:
            autocad_interface: AutoCAD interface (real or mock)
            config: Validated configuration parameters

        Returns:
            bool: True if generation successful

        Raises:
            Exception: If AutoCAD operations fail
        """
        try:
            basic_params = config.get("basic_parameters", {})
            center_pole_diameter = basic_params["center_pole_diameter"]
            overall_height = basic_params["overall_height"]

            # Calculate radius (VBA uses diameter/2)
            radius = center_pole_diameter / 2.0

            # Calculate correct height and position
            # Center pole should be full overall height
            pole_height = overall_height
            
            # Position cylinder so bottom is at Z=0 and top is at Z=pole_height
            # Center point needs to be at Z = pole_height / 2
            center_point = (0.0, 0.0, pole_height / 2.0)

            # Create center pole as a 3D solid (like treads do)
            if hasattr(autocad_interface, "entities"):  # Mock interface
                # For mock, create simplified representation
                pole = autocad_interface.create_cylinder(
                    center_point, radius, pole_height
                )
            else:
                # Real AutoCAD: Create circle at Z=0 and extrude to create 3D solid
                # Circle at the base (Z=0)
                circle_center = (0.0, 0.0, 0.0)
                circle = autocad_interface.create_circle(circle_center, radius)
                
                # Create region from the circle
                regions = autocad_interface.create_region([circle])
                
                if regions and len(regions) > 0:
                    region_obj = regions[0]
                    
                    # Extrude the region to create 3D solid cylinder
                    pole = autocad_interface.create_extruded_solid(region_obj, pole_height, 0)
                    
                    print(f"AutoCAD: Created 3D solid center pole cylinder at Z=0, height={pole_height}")
                else:
                    print("Failed to create region for center pole")
                    return False

            # Store created entity for cleanup if needed
            self._created_entities = [pole]

            # Set color to 251 (matching VBA)
            if hasattr(pole, "color"):
                pole.color = 251

            # Store geometry parameters for get_geometry_info()
            self.diameter = center_pole_diameter
            self.height = pole_height
            self.radius = radius
            self.center_z = pole_height / 2.0
            self.bottom_z = 0.0
            self.top_z = pole_height
            
            self.is_generated = True
            print(
                f'Center pole created: diameter={center_pole_diameter}", height={pole_height}", radius={radius}"'
            )
            print(f'Center pole positioned: bottom Z={self.bottom_z}", center Z={self.center_z}", top Z={self.top_z}"')

            return True

        except Exception as e:
            self.last_error = e
            print(f"Failed to create center pole: {str(e)}")
            return False

    def get_required_parameters(self) -> List[str]:
        """
        Get list of required configuration parameters.

        Returns:
            List of required parameter paths
        """
        return [
            "basic_parameters.center_pole_diameter",
            "basic_parameters.overall_height",
        ]

    def cleanup(self, autocad_interface) -> None:
        """
        Clean up center pole geometry if generation fails.

        Args:
            autocad_interface: AutoCAD interface
        """
        if hasattr(self, "_created_entities"):
            for entity in self._created_entities:
                try:
                    if hasattr(entity, "Delete"):
                        entity.Delete()
                    elif hasattr(autocad_interface, "delete_entity"):
                        autocad_interface.delete_entity(entity)
                except:
                    pass  # Ignore cleanup errors
            self._created_entities = []

        self.is_generated = False
        print("Center pole geometry cleaned up")

    def get_geometry_info(self) -> Dict[str, Any]:
        """
        Get information about generated geometry for debugging.

        Returns:
            Dict with geometry details
        """
        if not self.is_generated:
            return {"status": "not_generated"}

        return {
            "status": "generated",
            "type": "cylinder",
            "diameter": getattr(self, 'diameter', 0.0),
            "height": getattr(self, 'height', 0.0),
            "radius": getattr(self, 'radius', 0.0),
            "center_z": getattr(self, 'center_z', 0.0),
            "bottom_z": getattr(self, 'bottom_z', 0.0),
            "top_z": getattr(self, 'top_z', 0.0),
            "color": 251,
            "position": "bottom_at_z_zero",
            "note": "Center pole positioned with bottom at Z=0, height = overall_height",
        }
