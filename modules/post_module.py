"""
Post Module - Creates structural posts connecting treads in spiral staircase.
Posts provide structural support and connect treads together, replacing pickets where present.
"""

import math
from typing import Dict, Any, List, Tuple, Optional
from core.base_component import BaseStairComponent
from core.autocad_interface import AutoCADInterface


class PostModule(BaseStairComponent):
    """
    Creates structural posts for spiral staircase.

    Posts are vertical structural elements that:
    - Connect treads together for structural integrity
    - Replace pickets where present (posts take precedence)
    - Can be spaced every tread, every other tread, or every third tread
    - Extend from tread surface to underside of tread above
    - Are positioned at the outer edge of treads for maximum structural benefit
    """

    def __init__(self):
        """Initialize post module."""
        super().__init__("Posts")
        self.posts_created = []
        self.post_count = 0
        self.post_spacing = 1  # Default: one post per tread
        self.post_positions = []

    def get_required_parameters(self) -> List[str]:
        """
        Get list of required configuration parameters.

        Returns:
            List of required parameter keys
        """
        return [
            "center_pole_diameter",
            "overall_height",
            "outside_diameter",
            "total_rotation",
            "is_clockwise",
        ]

    def validate_parameters(self, config: Dict[str, Any]) -> bool:
        """
        Validate parameters for post generation.

        Args:
            config: Configuration dictionary

        Returns:
            bool: True if parameters are valid

        Raises:
            ValueError: If parameters are invalid
        """
        basic_params = config.get("basic_parameters", {})
        post_config = config.get("post_configuration", {})

        # Check basic parameters (inherited validation)
        center_pole_dia = basic_params.get("center_pole_diameter", 0)
        overall_height = basic_params.get("overall_height", 0)
        outside_dia = basic_params.get("outside_diameter", 0)

        if center_pole_dia <= 0:
            raise ValueError("Center pole diameter must be > 0")
        if overall_height <= 0:
            raise ValueError("Overall height must be > 0")
        if outside_dia <= center_pole_dia:
            raise ValueError("Outside diameter must be > center pole diameter")

        # Validate post-specific parameters
        if post_config.get("enabled", False):
            post_spacing = post_config.get("spacing", 1)
            post_diameter = post_config.get("diameter", 2.0)

            if post_spacing not in [1, 2, 3]:
                raise ValueError("Post spacing must be 1, 2, or 3 (treads per post)")
            if post_diameter <= 0 or post_diameter > 6.0:
                raise ValueError("Post diameter must be between 0 and 6 inches")

        return True

    def generate_geometry(
        self, autocad_interface: AutoCADInterface, config: Dict[str, Any]
    ) -> bool:
        """
        Generate post geometries for the spiral staircase.

        Args:
            autocad_interface: AutoCAD interface for geometry creation
            config: Configuration dictionary

        Returns:
            bool: True if generation successful
        """
        try:
            # Set active layer to POSTS before creating any post entities
            autocad_interface.set_active_layer("POSTS")
            
            post_config = config.get("post_configuration", {})

            # Check if posts are enabled
            if not post_config.get("enabled", False):
                print("Posts disabled in configuration - skipping post generation")
                self.is_generated = True
                return True

            basic_params = config.get("basic_parameters", {})

            # Extract parameters
            center_pole_dia = basic_params.get("center_pole_diameter")
            overall_height = basic_params.get("overall_height")
            outside_dia = basic_params.get("outside_diameter")
            total_rotation = basic_params.get("total_rotation")
            is_clockwise = basic_params.get("is_clockwise", True)

            # Post configuration parameters
            self.post_spacing = post_config.get(
                "spacing", 1
            )  # 1, 2, or 3 treads per post
            post_diameter = post_config.get("diameter", 2.0)
            post_material = post_config.get("material", "steel")
            post_position = post_config.get(
                "position", "outer_edge"
            )  # outer_edge, mid_tread, inner_edge

            # Calculate tread information (matching tread module logic)
            num_treads = self._calculate_num_treads(overall_height)
            riser_height = overall_height / num_treads

            # Check for mid-landing requirement (matching tread module)
            mid_landing_index = -1
            if overall_height > 151:
                mid_landing_index = round(num_treads / 2) - 1

            # Calculate tread angle (matching tread module)
            if mid_landing_index >= 0:
                tread_angle = (total_rotation - 90) / (num_treads - 2)
            else:
                tread_angle = total_rotation / (num_treads - 1)

            # Apply direction
            direction = 1 if is_clockwise else -1
            signed_tread_angle = direction * tread_angle

            # Calculate post position radius based on configuration
            inner_radius = center_pole_dia / 2
            outer_radius = outside_dia / 2

            if post_position == "outer_edge":
                post_radius = (
                    outer_radius - (post_diameter / 2) - 0.5
                )  # 0.5" inset from edge
            elif post_position == "mid_tread":
                post_radius = (inner_radius + outer_radius) / 2
            else:  # inner_edge
                post_radius = (
                    inner_radius + (post_diameter / 2) + 0.5
                )  # 0.5" inset from pole

            current_angle = 0.0
            self.posts_created = []

            print(f"Creating posts with spacing: every {self.post_spacing} tread(s)")
            print(f'Post diameter: {post_diameter}", Material: {post_material}')
            print(f'Post position: {post_position} at radius {post_radius:.2f}"')

            # Create posts based on spacing
            for i in range(num_treads - 1):  # Exclude last tread (becomes top landing)
                # Skip if not a post location based on spacing
                if i % self.post_spacing != 0:
                    # Still need to advance angle for proper positioning
                    if i == mid_landing_index:
                        current_angle += direction * math.radians(90)
                    else:
                        current_angle += math.radians(signed_tread_angle)
                    continue

                # Calculate tread heights
                current_tread_height = (
                    riser_height * (i + 1) - 0.25
                )  # Current tread top
                next_tread_height = riser_height * (i + 2) - 0.25  # Next tread top

                # Post extends from current tread surface to next tread bottom
                post_bottom = current_tread_height + 0.25  # Top of current tread
                post_top = next_tread_height  # Bottom of next tread
                post_height = post_top - post_bottom

                # Calculate end angle for this tread to position post
                if i == mid_landing_index:
                    end_angle = current_angle + direction * math.radians(90)
                    post_angle = current_angle + direction * math.radians(
                        45
                    )  # Center of landing
                    print(
                        f"Creating post {len(self.posts_created) + 1} at mid-landing (tread {i + 1})"
                    )
                else:
                    end_angle = current_angle + math.radians(signed_tread_angle)
                    post_angle = current_angle + math.radians(
                        signed_tread_angle / 2
                    )  # Center of tread
                    print(
                        f"Creating post {len(self.posts_created) + 1} at tread {i + 1}"
                    )

                # Calculate post position
                post_x = post_radius * math.cos(post_angle)
                post_y = post_radius * math.sin(post_angle)

                # Create the post geometry
                success = self._create_post(
                    autocad_interface,
                    post_x,
                    post_y,
                    post_bottom,
                    post_height,
                    post_diameter,
                    post_material,
                )

                if success:
                    self.posts_created.append(
                        {
                            "index": len(self.posts_created),
                            "tread_index": i,
                            "x_position": round(post_x, 3),
                            "y_position": round(post_y, 3),
                            "bottom_height": round(post_bottom, 3),
                            "top_height": round(post_top, 3),
                            "height": round(post_height, 3),
                            "diameter": post_diameter,
                            "angle_degrees": round(math.degrees(post_angle), 2),
                            "material": post_material,
                            "is_at_mid_landing": i == mid_landing_index,
                        }
                    )
                else:
                    print(f"Failed to create post at tread {i + 1}")
                    return False

                current_angle = end_angle

            self.post_count = len(self.posts_created)
            self.is_generated = True

            print(f"Successfully created {self.post_count} posts")
            return True

        except Exception as e:
            self.last_error = str(e)
            print(f"Error generating posts: {str(e)}")
            return False

    def _calculate_num_treads(self, overall_height: float) -> int:
        """
        Calculate number of treads based on overall height.
        Uses same logic as tread module for consistency.

        Args:
            overall_height: Total stair height in inches

        Returns:
            Number of treads required
        """
        return math.ceil(overall_height / 9.5)

    def _create_post(
        self,
        autocad_interface: AutoCADInterface,
        x_pos: float,
        y_pos: float,
        bottom_height: float,
        post_height: float,
        diameter: float,
        material: str,
    ) -> bool:
        """
        Create a single post using AutoCAD interface.

        Args:
            autocad_interface: AutoCAD interface
            x_pos: X position of post center
            y_pos: Y position of post center
            bottom_height: Z-height of post bottom
            post_height: Height of post
            diameter: Post diameter
            material: Post material type

        Returns:
            bool: True if creation successful
        """
        try:
            # For mock mode, create simplified representation
            if hasattr(autocad_interface, "entities"):  # Mock interface
                # Create cylinder to represent the post
                bottom_center = (x_pos, y_pos, bottom_height)
                top_center = (x_pos, y_pos, bottom_height + post_height)

                cylinder = autocad_interface.create_cylinder(
                    bottom_center, diameter / 2, post_height
                )
                cylinder["material"] = material
                cylinder["diameter"] = diameter
                cylinder["post_type"] = "structural"

                # Add lines to show post outline
                autocad_interface.create_line(bottom_center, top_center)

                print(
                    f"Mock AutoCAD: Created post at ({x_pos:.2f}, {y_pos:.2f}) "
                    f'height {post_height:.2f}" diameter {diameter}"'
                )
                return True
            else:
                # Real AutoCAD implementation
                try:
                    # Create a cylinder for the post
                    center_point = (x_pos, y_pos, bottom_height + post_height / 2)
                    
                    # Convert to VARIANT array for AutoCAD
                    if hasattr(autocad_interface, '_convert_to_variant_array'):
                        # Use the helper method if available
                        center_variant = autocad_interface._convert_to_variant_array(center_point)
                    else:
                        # Manual conversion
                        import win32com.client
                        import pythoncom
                        center_variant = win32com.client.VARIANT(
                            pythoncom.VT_ARRAY | pythoncom.VT_R8,
                            [float(center_point[0]), float(center_point[1]), float(center_point[2])]
                        )
                    
                    # Create the cylinder
                    cylinder = autocad_interface.model_space.AddCylinder(
                        center_variant, diameter / 2, post_height
                    )
                    
                    # Store for cleanup
                    if not hasattr(self, '_created_entities'):
                        self._created_entities = []
                    self._created_entities.append(cylinder)
                    
                    print(
                        f"Real AutoCAD: Created post at ({x_pos:.2f}, {y_pos:.2f}) "
                        f'height {post_height:.2f}" diameter {diameter}"'
                    )
                    return True
                    
                except Exception as e:
                    print(f"Error creating post in AutoCAD: {str(e)}")
                    return False

        except Exception as e:
            print(f"Error creating post: {str(e)}")
            return False

    def cleanup(self, autocad_interface: AutoCADInterface) -> None:
        """
        Clean up post geometries on failure.

        Args:
            autocad_interface: AutoCAD interface
        """
        try:
            if hasattr(autocad_interface, "entities"):  # Mock interface
                print("Mock AutoCAD: Cleaning up post geometries")
            else:
                print("Real AutoCAD: Cleaning up post geometries")

            self.posts_created.clear()
            self.post_count = 0

        except Exception as e:
            print(f"Error during post cleanup: {str(e)}")

    def get_geometry_info(self) -> Dict[str, Any]:
        """
        Get detailed information about generated post geometry.

        Returns:
            Dict with post geometry details
        """
        if not self.is_generated:
            return {"status": "not_generated"}

        return {
            "status": "generated",
            "post_count": self.post_count,
            "post_spacing": self.post_spacing,
            "posts_created": self.posts_created,
            "note": "Posts provide structural connection between treads",
        }

    def get_post_positions(self) -> List[Dict[str, Any]]:
        """
        Get list of post positions for use by other modules (like picket module).
        This allows picket module to avoid creating pickets where posts exist.

        Returns:
            List of post position dictionaries with tread_index and coordinates
        """
        return [
            {
                "tread_index": post["tread_index"],
                "x_position": post["x_position"],
                "y_position": post["y_position"],
                "diameter": post["diameter"],
            }
            for post in self.posts_created
        ]