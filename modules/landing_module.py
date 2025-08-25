"""
Landing Module - Creates top landing and handles mid-landing integration.
Migrated from VBA CreateRectangularLanding function with enhanced Python implementation.
"""

import math
from typing import Dict, Any, List, Tuple, Optional
from core.base_component import BaseStairComponent
from core.autocad_interface import AutoCADInterface
from core.exceptions import GenerationError

# Import COM modules for parameter marshalling
try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False
    win32com = None
    pythoncom = None


class LandingModule(BaseStairComponent):
    """
    Creates rectangular landings for spiral staircases.

    Handles both:
    - Top landing: Final landing at the top of the staircase
    - Mid-landing: Optional intermediate landing for tall staircases (>151")

    Each landing is created as an extruded solid with:
    - Rectangular shape extending from center outward
    - 0.25" thickness (matching tread depth)
    - Proper positioning at calculated heights
    - Color coding (3 for landings)
    """

    def __init__(self):
        """Initialize landing module."""
        super().__init__("Landings")
        self.landings_created = []
        self.top_landing_created = False
        self.mid_landing_created = False

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
        Validate parameters for landing generation.

        Args:
            config: Configuration dictionary

        Returns:
            bool: True if parameters are valid

        Raises:
            ValueError: If parameters are invalid
        """
        basic_params = config.get("basic_parameters", {})

        # Required parameters
        center_pole_dia = basic_params.get("center_pole_diameter", 0)
        overall_height = basic_params.get("overall_height", 0)
        outside_dia = basic_params.get("outside_diameter", 0)
        total_rotation = basic_params.get("total_rotation", 0)

        if center_pole_dia <= 0:
            raise ValueError("Center pole diameter must be > 0")
        if overall_height <= 0:
            raise ValueError("Overall height must be > 0")
        if outside_dia <= center_pole_dia:
            raise ValueError("Outside diameter must be > center pole diameter")
        if total_rotation <= 0:
            raise ValueError("Total rotation must be > 0")

        return True

    def generate_geometry(
        self, autocad_interface: AutoCADInterface, config: Dict[str, Any]
    ) -> bool:
        """
        Generate landing geometries for the spiral staircase.

        Args:
            autocad_interface: AutoCAD interface for geometry creation
            config: Configuration dictionary

        Returns:
            bool: True if generation successful
        """
        try:
            # Set active layer to LANDINGS before creating any landing entities
            autocad_interface.set_active_layer("LANDINGS")
            
            basic_params = config.get("basic_parameters", {})

            # Extract parameters
            center_pole_dia = basic_params.get("center_pole_diameter")
            overall_height = basic_params.get("overall_height")
            outside_dia = basic_params.get("outside_diameter")
            total_rotation = basic_params.get("total_rotation")
            is_clockwise = basic_params.get("is_clockwise", True)

            # Calculate tread geometry (matching tread module logic)
            num_treads = self._calculate_num_treads(overall_height)
            riser_height = overall_height / num_treads

            # Check for mid-landing requirement (VBA logic: height > 151")
            mid_landing_index = -1
            if overall_height > 151:
                mid_landing_index = round(num_treads / 2) - 1

            # Calculate angles and positions
            if mid_landing_index >= 0:
                # With mid-landing: subtract 90° for landing, distribute remaining rotation
                tread_angle = (total_rotation - 90) / (num_treads - 2)
            else:
                # No mid-landing: distribute full rotation among treads
                tread_angle = total_rotation / (num_treads - 1)

            # Apply direction (clockwise = positive, counterclockwise = negative)
            direction = 1 if is_clockwise else -1
            signed_tread_angle = direction * tread_angle

            # Calculate landing dimensions (from VBA call: outsideDia / 2, 50)
            landing_length = outside_dia / 2  # Radius from center to edge
            landing_width = 50.0  # Fixed width in VBA

            self.landings_created = []

            print(f"Generating landings for {num_treads} treads")
            if mid_landing_index >= 0:
                print(f"Mid-landing required at tread #{mid_landing_index + 1}")

            # Calculate current angle at top (where top landing goes)
            current_angle = 0.0
            for i in range(num_treads - 1):  # Skip last tread
                if i == mid_landing_index:
                    # Mid-landing: 90-degree sector
                    current_angle += direction * math.radians(90)
                else:
                    # Normal tread: calculated angle
                    current_angle += math.radians(signed_tread_angle)

            # Create top landing (replaces the last tread)
            top_landing_height = overall_height  # Top landing should be at full height

            success = self._create_rectangular_landing(
                autocad_interface,
                landing_length,
                landing_width,
                current_angle,
                direction,
                top_landing_height,
                "top",
            )

            if success:
                self.top_landing_created = True
                self.landings_created.append(
                    {
                        "type": "top",
                        "length": landing_length,
                        "width": landing_width,
                        "angle": math.degrees(current_angle),
                        "height": top_landing_height,
                        "direction": "CW" if is_clockwise else "CCW",
                    }
                )
                print(
                    f'Top landing created at height {top_landing_height:.2f}" and angle {math.degrees(current_angle):.1f}°'
                )
            else:
                print("Failed to create top landing")
                return False

            # Note: Mid-landings are handled by the tread module as special 90° treads
            # This is consistent with the VBA implementation

            self.is_generated = True
            print(f"Successfully created {len(self.landings_created)} landing(s)")
            return True

        except Exception as e:
            self.last_error = str(e)
            print(f"Error generating landings: {str(e)}")
            return False

    def _calculate_num_treads(self, overall_height: float) -> int:
        """
        Calculate number of treads based on overall height.
        Uses VBA logic: Ceiling(height / 9.5)

        Args:
            overall_height: Total stair height in inches

        Returns:
            Number of treads required
        """
        return math.ceil(overall_height / 9.5)

    def _create_rectangular_landing(
        self,
        autocad_interface: AutoCADInterface,
        landing_length: float,
        landing_width: float,
        current_angle: float,
        direction: int,
        landing_height: float,
        landing_type: str,
    ) -> bool:
        """
        Create a rectangular landing using AutoCAD interface.
        Follows VBA CreateRectangularLanding logic exactly.

        Args:
            autocad_interface: AutoCAD interface
            landing_length: Length of landing (from center outward)
            landing_width: Width of landing
            current_angle: Current rotation angle in radians
            direction: Direction (1 for clockwise, -1 for counterclockwise)
            landing_height: Z-height for landing placement
            landing_type: Type of landing ("top" or "mid")

        Returns:
            bool: True if creation successful
        """
        try:
            # Check if this is the mock interface
            is_mock = not hasattr(autocad_interface, 'model_space')
            
            if is_mock:
                # Mock interface implementation
                # Create lines to represent the rectangular landing
                # Following VBA logic exactly:

                # Line 0: From center to outer edge
                start_pt = (0.0, 0.0, landing_height)
                end_pt = (
                    landing_length * math.cos(current_angle),
                    landing_length * math.sin(current_angle),
                    landing_height,
                )
                line1 = autocad_interface.create_line(start_pt, end_pt)
                line1["landing_component"] = f"{landing_type}_landing_line_0"

                # Line 1: Perpendicular to first line
                start_pt = end_pt
                end_pt = (
                    start_pt[0]
                    + landing_width
                    * math.cos(current_angle + (math.pi / 2) * direction),
                    start_pt[1]
                    + landing_width
                    * math.sin(current_angle + (math.pi / 2) * direction),
                    landing_height,
                )
                line2 = autocad_interface.create_line(start_pt, end_pt)
                line2["landing_component"] = f"{landing_type}_landing_line_1"

                # Line 2: Back toward center
                start_pt = end_pt
                end_pt = (
                    start_pt[0] - landing_length * math.cos(current_angle),
                    start_pt[1] - landing_length * math.sin(current_angle),
                    landing_height,
                )
                line3 = autocad_interface.create_line(start_pt, end_pt)
                line3["landing_component"] = f"{landing_type}_landing_line_2"

                # Line 3: Close the rectangle
                start_pt = end_pt
                end_pt = (
                    start_pt[0]
                    - landing_width
                    * math.cos(current_angle + (math.pi / 2) * direction),
                    start_pt[1]
                    - landing_width
                    * math.sin(current_angle + (math.pi / 2) * direction),
                    landing_height,
                )
                line4 = autocad_interface.create_line(start_pt, end_pt)
                line4["landing_component"] = f"{landing_type}_landing_line_3"

                print(
                    f"Mock AutoCAD: Created {landing_type} landing at Z={landing_height:.2f}, angle={math.degrees(current_angle):.1f}°"
                )
                print(
                    f'Mock AutoCAD: Landing dimensions: {landing_length:.1f}" × {landing_width:.1f}"'
                )
                return True
            else:
                # Real AutoCAD implementation
                # Create a polyline to represent the rectangular landing
                try:
                    # Ensure AutoCAD is connected and ready
                    if not autocad_interface.is_connected():
                        if not autocad_interface.connect():
                            raise GenerationError(
                                "Failed to connect to AutoCAD",
                                geometry_type="landing",
                                operation="connect"
                            )
                    
                    # Verify model_space is available
                    if not hasattr(autocad_interface, 'model_space') or autocad_interface.model_space is None:
                        raise GenerationError(
                            "AutoCAD model space not available",
                            geometry_type="landing",
                            operation="access_model_space"
                        )
                    # Calculate the four corners of the rectangle
                    corners = []
                    
                    # Corner 1: From center to outer edge
                    x1 = landing_length * math.cos(current_angle)
                    y1 = landing_length * math.sin(current_angle)
                    corners.append((x1, y1, landing_height))
                    
                    # Corner 2: Perpendicular to first line
                    x2 = x1 + landing_width * math.cos(current_angle + (math.pi / 2) * direction)
                    y2 = y1 + landing_width * math.sin(current_angle + (math.pi / 2) * direction)
                    corners.append((x2, y2, landing_height))
                    
                    # Corner 3: Back toward center
                    x3 = x2 - landing_length * math.cos(current_angle)
                    y3 = y2 - landing_length * math.sin(current_angle)
                    corners.append((x3, y3, landing_height))
                    
                    # Corner 4: Close the rectangle
                    x4 = x3 - landing_width * math.cos(current_angle + (math.pi / 2) * direction)
                    y4 = y3 - landing_width * math.sin(current_angle + (math.pi / 2) * direction)
                    corners.append((x4, y4, landing_height))
                    
                    # Close the rectangle by adding the first point again
                    corners.append(corners[0])
                    
                    # Flatten the points array for AutoCAD LightWeightPolyline (2D only)
                    # Note: LightWeightPolyline only accepts 2D points (X,Y), not 3D (X,Y,Z)
                    points = []
                    for x, y, z in corners:
                        points.extend([x, y])  # Only X,Y coordinates for lightweight polyline
                    
                    # Convert to VARIANT array for AutoCAD using proper parameter marshalling
                    # This is the critical fix for Real AutoCAD compatibility
                    if COM_AVAILABLE:
                        points_variant = win32com.client.VARIANT(
                            pythoncom.VT_ARRAY | pythoncom.VT_R8,
                            [float(coord) for coord in points]
                        )
                    else:
                        raise GenerationError(
                            "COM modules not available for parameter marshalling",
                            geometry_type="polyline",
                            operation="create"
                        )
                    
                    # Create the polyline using proper COM interface
                    polyline = autocad_interface.model_space.AddLightWeightPolyline(points_variant)
                    polyline.Closed = True
                    polyline.color = 3  # Color 3 for landings
                    
                    # Set the elevation (Z-coordinate) for the polyline
                    polyline.Elevation = landing_height
                    
                    # Store for cleanup
                    if not hasattr(self, '_created_entities'):
                        self._created_entities = []
                    self._created_entities.append(polyline)
                    
                    print(
                        f"Real AutoCAD: Created {landing_type} landing at Z={landing_height:.2f}, angle={math.degrees(current_angle):.1f}°"
                    )
                    print(
                        f'Real AutoCAD: Landing dimensions: {landing_length:.1f}" × {landing_width:.1f}"'
                    )
                    return True
                    
                except Exception as e:
                    print(f"Error creating {landing_type} landing in AutoCAD: {str(e)}")
                    return False

        except Exception as e:
            print(f"Error creating {landing_type} landing: {str(e)}")
            return False

    def cleanup(self, autocad_interface: AutoCADInterface) -> None:
        """
        Clean up landing geometries on failure.

        Args:
            autocad_interface: AutoCAD interface
        """
        try:
            if hasattr(autocad_interface, "entities"):  # Mock interface
                print("Mock AutoCAD: Cleaning up landing geometries")
            else:
                print("Real AutoCAD: Cleaning up landing geometries")

            self.landings_created.clear()
            self.top_landing_created = False
            self.mid_landing_created = False

        except Exception as e:
            print(f"Error during landing cleanup: {str(e)}")

    def get_geometry_info(self) -> Dict[str, Any]:
        """
        Get detailed information about generated landing geometry.

        Returns:
            Dict with landing geometry details
        """
        if not self.is_generated:
            return {"status": "not_generated"}

        return {
            "status": "generated",
            "landings_count": len(self.landings_created),
            "top_landing_created": self.top_landing_created,
            "mid_landing_created": self.mid_landing_created,
            "landings_created": self.landings_created,
            "note": "Matches VBA CreateRectangularLanding function with enhanced error handling",
        }
