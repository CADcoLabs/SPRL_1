"""
Tread Module - Creates individual spiral stair treads with proper geometry and spacing.
Migrated from VBA CreateSectorTread function with enhanced Python implementation.
"""

import math
import time
from typing import Dict, Any, List, Tuple, Optional
from core.base_component import BaseStairComponent
from core.autocad_interface import AutoCADInterface

# Import COM modules for parameter marshalling
try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False
    win32com = None
    pythoncom = None


class TreadModule(BaseStairComponent):
    """
    Creates individual spiral stair treads with sector geometry.

    Each tread is created as an extruded solid with:
    - Sector shape (pie slice) from center pole to outside diameter
    - 0.25" thickness (standard tread depth)
    - Proper height positioning based on riser height
    - Color handled by layer (TREADS layer)
    """

    def __init__(self):
        """Initialize tread module."""
        super().__init__("Treads")
        self.treads_created = []
        self.tread_count = 0
        self.riser_height = 0.0
        self.tread_angle = 0.0
        self.mid_landing_index = -1

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
            # Mid-landing parameters are optional but validated if present
        ]

    def validate_parameters(self, config: Dict[str, Any]) -> bool:
        """
        Validate parameters for tread generation.

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

        # Calculate derived parameters for validation
        num_treads = self._calculate_num_treads(overall_height)
        if num_treads < 1:
            raise ValueError("Invalid number of treads calculated")

        return True

    def generate_geometry(
        self, autocad_interface: AutoCADInterface, config: Dict[str, Any]
    ) -> bool:
        """
        Generate all tread geometries for the spiral staircase.

        Args:
            autocad_interface: AutoCAD interface for geometry creation
            config: Configuration dictionary

        Returns:
            bool: True if generation successful
        """
        try:
            # Set active layer to TREADS before creating any tread entities
            autocad_interface.set_active_layer("TREADS")
            
            basic_params = config.get("basic_parameters", {})

            # Extract parameters
            center_pole_dia = basic_params.get("center_pole_diameter")
            overall_height = basic_params.get("overall_height")
            outside_dia = basic_params.get("outside_diameter")
            total_rotation = basic_params.get("total_rotation")
            is_clockwise = basic_params.get("is_clockwise", True)

            # Calculate tread geometry
            num_treads = self._calculate_num_treads(overall_height)
            self.riser_height = overall_height / num_treads

            # Mid-landing handling - now uses basic parameters (UI-controlled)
            self.mid_landing_index = -1
            mid_landing_enabled = basic_params.get("mid_landing_enabled", False)
            mid_landing_tread_index = basic_params.get("mid_landing_tread_index", -1)
            
            if mid_landing_enabled and mid_landing_tread_index >= 0:
                # Validate mid-landing index is within bounds
                if 0 <= mid_landing_tread_index < num_treads:
                    self.mid_landing_index = mid_landing_tread_index
                    print(f"Mid-landing enabled at tread #{self.mid_landing_index + 1} (user-specified)")
                else:
                    print(f"WARNING: Mid-landing index {mid_landing_tread_index} out of range (0-{num_treads-1})")
                    print("Proceeding without mid-landing")
            elif overall_height > 151 and not mid_landing_enabled:
                # Height > 151" but user hasn't enabled mid-landing - warn about code compliance
                print(f"NOTICE: Overall height ({overall_height:.1f}\") exceeds 151 inches.")
                print("A mid-landing is required per IRC R311.7.3 for code compliance.")
                print("Enable mid-landing in basic parameters for compliant design.")

            # Calculate tread angle based on mid-landing presence
            if self.mid_landing_index >= 0:
                # With mid-landing: subtract 90° for landing, distribute remaining rotation
                self.tread_angle = (total_rotation - 90) / (num_treads - 2)
            else:
                # No mid-landing: distribute full rotation among treads
                self.tread_angle = total_rotation / (num_treads - 1)

            # Apply direction (clockwise = positive, counterclockwise = negative)
            direction = 1 if is_clockwise else -1
            signed_tread_angle = direction * self.tread_angle

            # Calculate radii for tread sector
            inner_radius = center_pole_dia / 2
            outer_radius = outside_dia / 2

            current_angle = 0.0  # Start at 0 degrees
            self.treads_created = []

            print(
                f'Creating {num_treads} treads with {self.riser_height:.2f}" riser height'
            )
            print(
                f"Tread angle: {self.tread_angle:.2f}°, Direction: {'CW' if is_clockwise else 'CCW'}"
            )
            if self.mid_landing_index >= 0:
                print(f"Mid-landing at tread #{self.mid_landing_index + 1}")

            # Create each tread
            for i in range(num_treads):
                # Calculate tread height (subtract 0.25" for tread thickness)
                tread_height = self.riser_height * (i + 1) - 0.25
                if tread_height + 0.25 > overall_height:
                    tread_height = overall_height - 0.25

                # Skip the last tread - it becomes the top landing (handled by landing module)
                if i == num_treads - 1:
                    print(f"Skipping tread {i + 1} - will be top landing")
                    break

                # Calculate end angle for this tread
                if i == self.mid_landing_index:
                    # Mid-landing tread: 90-degree sector
                    end_angle = current_angle + direction * math.radians(90)
                    print(
                        f'Creating mid-landing tread {i + 1} at height {tread_height:.2f}"'
                    )
                else:
                    # Normal tread: calculated angle
                    end_angle = current_angle + math.radians(signed_tread_angle)
                    print(f'Creating tread {i + 1} at height {tread_height:.2f}"')

                # Create the tread geometry (color handled by layer)
                success = self._create_sector_tread(
                    autocad_interface,
                    current_angle,
                    end_angle,
                    inner_radius,
                    outer_radius,
                    tread_height,
                    is_clockwise,
                    config,
                    i,
                )

                if success:
                    self.treads_created.append(
                        {
                            "index": i,
                            "start_angle": math.degrees(current_angle),
                            "end_angle": math.degrees(end_angle),
                            "height": tread_height,
                            "is_mid_landing": i == self.mid_landing_index,
                        }
                    )
                    
                    # Add widened tread 2D geometry for the first tread (index 0)
                    if i == 0:
                        basic_params = config.get("basic_parameters", {})
                        keep_original = basic_params.get("keep_original_tread_geometry", False)
                        print(f"Creating widened 2D geometry for first tread (keep_original={keep_original})")
                        
                        widened_success = self._create_widened_2d_geometry(
                            autocad_interface, current_angle, end_angle, inner_radius, outer_radius, tread_height
                        )
                        if widened_success:
                            print("Widened 2D geometry created successfully")
                        else:
                            print("Failed to create widened 2D geometry")
                    current_angle = end_angle
                else:
                    print(f"Failed to create tread {i + 1}")
                    return False

            self.tread_count = len(self.treads_created)
            self.is_generated = True

            print(f"Successfully created {self.tread_count} treads")
            return True

        except Exception as e:
            self.last_error = str(e)
            print(f"Error generating treads: {str(e)}")
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

    def _create_sector_tread(
        self,
        autocad_interface: AutoCADInterface,
        start_angle: float,
        end_angle: float,
        inner_radius: float,
        outer_radius: float,
        tread_height: float,
        is_clockwise: bool = True,
        config: Dict[str, Any] = None,
        tread_index: int = 0,
    ) -> bool:
        """
        Create a single sector tread using AutoCAD interface with 3D solid geometry.
        Based on VBA CreateSectorTread function (Module1.bas:292-340).
        Supports optional widened tread geometry with configurable offset.

        Args:
            autocad_interface: AutoCAD interface
            start_angle: Start angle in radians
            end_angle: End angle in radians
            inner_radius: Inner radius (center pole edge)
            outer_radius: Outer radius (outside diameter)
            tread_height: Z-height for tread placement
            is_clockwise: Direction of rotation
            config: Configuration dictionary with widened tread settings
            tread_index: Index of the tread being created (0 = bottom)

        Returns:
            bool: True if creation successful
        """
        try:
            # Check if this is the mock interface
            is_mock = not hasattr(autocad_interface, 'model_space')
            
            if is_mock:
                # Mock interface implementation
                center = (0.0, 0.0, tread_height)
                arc = autocad_interface.create_arc(
                    center, outer_radius, start_angle, end_angle
                )
                arc["inner_radius"] = inner_radius
                arc["tread_height"] = tread_height
                arc["thickness"] = 0.25

                # Add lines to show sector boundaries
                start_pt = (
                    outer_radius * math.cos(start_angle),
                    outer_radius * math.sin(start_angle),
                    tread_height,
                )
                end_pt = (0.0, 0.0, tread_height)
                autocad_interface.create_line(start_pt, end_pt)

                end_start_pt = (
                    outer_radius * math.cos(end_angle),
                    outer_radius * math.sin(end_angle),
                    tread_height,
                )
                autocad_interface.create_line(end_start_pt, end_pt)

                print(
                    f"Mock AutoCAD: Created sector tread from {math.degrees(start_angle):.1f}° to {math.degrees(end_angle):.1f}° at Z={tread_height:.2f}"
                )
                
                return True
            else:
                # Real AutoCAD implementation - Create 3D solid tread using regions and extrusion
                # Based on VBA CreateSectorTread function logic
                
                try:
                    return self._create_original_tread_real(
                        autocad_interface, start_angle, end_angle, inner_radius, outer_radius, tread_height, is_clockwise
                    )
                    
                except Exception as e:
                    print(f"Error creating sector tread in AutoCAD: {str(e)}")
                    return False

        except Exception as e:
            print(f"Error creating sector tread: {str(e)}")
            return False

    def _add_tread_measurements(self, autocad_interface: AutoCADInterface, start_angle: float, end_angle: float, 
                               inner_radius: float, outer_radius: float, tread_height: float) -> None:
        """Add measurement annotations to the first tread only (to avoid clutter)."""
        try:
            import math
            
            # Check if the interface has text methods
            if not hasattr(autocad_interface, 'add_text') or not hasattr(autocad_interface, 'add_dimension'):
                return
                
            # Calculate tread dimensions
            tread_width = outer_radius - inner_radius
            tread_angle = abs(end_angle - start_angle)
            arc_length = outer_radius * tread_angle
            
            # Position for text annotations - slightly above the tread
            text_z = tread_height + 0.5
            
            # Calculate center point of the tread for text placement
            mid_angle = (start_angle + end_angle) / 2
            text_radius = (inner_radius + outer_radius) / 2
            text_position = (
                text_radius * math.cos(mid_angle),
                text_radius * math.sin(mid_angle),
                text_z
            )
            
            # Add width dimension (radial direction)
            inner_pt = (
                inner_radius * math.cos(mid_angle),
                inner_radius * math.sin(mid_angle),
                tread_height + 0.125
            )
            outer_pt = (
                outer_radius * math.cos(mid_angle),
                outer_radius * math.sin(mid_angle),
                tread_height + 0.125
            )
            dim_line_pt = (
                (text_radius + 2) * math.cos(mid_angle),
                (text_radius + 2) * math.sin(mid_angle),
                tread_height + 0.125
            )
            
            # Add dimension line for tread width
            autocad_interface.add_dimension(inner_pt, outer_pt, dim_line_pt, f"{tread_width:.2f}\"")
            
            # Add text annotation with key measurements
            measurement_text = f"W: {tread_width:.2f}\"\nR: {self.riser_height:.2f}\""
            autocad_interface.add_text(measurement_text, text_position, 0.1)
            
            print(f"Added measurements to FIRST TREAD ONLY: Width={tread_width:.2f}\", Rise={self.riser_height:.2f}\"")
            
        except Exception as e:
            # Don't fail the tread creation if measurement annotation fails
            print(f"Warning: Could not add tread measurements: {str(e)}")

    def _create_widened_2d_geometry(
        self,
        autocad_interface: AutoCADInterface,
        start_angle: float,
        end_angle: float,
        inner_radius: float,
        outer_radius: float,
        tread_height: float
    ) -> bool:
        """
        Create widened 2D geometry for the tread exactly as specified:
        - Offset both radial edge lines outward by 0.375"
        - Extend inner and outer arcs to meet the offset lines
        - Create as simple 2D lines and arcs
        """
        try:
            extend_distance = 0.375  # inches - LINEAR distance
            
            # Calculate separate angular extensions for each arc to get exactly 0.375" LINEAR extension
            inner_angular_extension = extend_distance / inner_radius
            outer_angular_extension = extend_distance / outer_radius
            
            # Inner arc extended angles
            inner_extended_start = start_angle - inner_angular_extension
            inner_extended_end = end_angle + inner_angular_extension
            
            # Outer arc extended angles  
            outer_extended_start = start_angle - outer_angular_extension
            outer_extended_end = end_angle + outer_angular_extension
            
            # Use tread_height + 1.25 to put geometry at correct height
            geometry_height = tread_height + 1.25
            
            print(f"Creating extended arcs at height {geometry_height:.2f}")
            print(f"Original: {math.degrees(start_angle):.1f}° to {math.degrees(end_angle):.1f}°")
            print(f"Inner arc extended: {math.degrees(inner_extended_start):.1f}° to {math.degrees(inner_extended_end):.1f}°")
            print(f"Outer arc extended: {math.degrees(outer_extended_start):.1f}° to {math.degrees(outer_extended_end):.1f}°")
            
            # Create and switch to "Geometry" layer (yellow)
            autocad_interface.create_layer("Geometry", color=2)  # Yellow is color 2 in AutoCAD
            autocad_interface.set_active_layer("Geometry")
            
            # 1. Outer arc (extended by 0.375" LINEAR at each end)
            outer_arc = autocad_interface.create_arc(
                (0.0, 0.0, geometry_height), outer_radius, outer_extended_start, outer_extended_end
            )
            
            # 2. Inner arc (extended by 0.375" LINEAR at each end)  
            inner_arc = autocad_interface.create_arc(
                (0.0, 0.0, geometry_height), inner_radius, inner_extended_start, inner_extended_end
            )
            
            # Add lines connecting the endpoints of the two arcs on the first tread only
            # First line: connecting at the extended start angle
            line1_start_point = (
                outer_radius * math.cos(outer_extended_start),
                outer_radius * math.sin(outer_extended_start),
                geometry_height
            )
            
            line1_end_point = (
                inner_radius * math.cos(inner_extended_start),
                inner_radius * math.sin(inner_extended_start),
                geometry_height
            )
            
            # Create the first connecting line on the Geometry layer
            autocad_interface.create_line(line1_start_point, line1_end_point)
            
            # Second line: connecting at the extended end angle
            line2_start_point = (
                outer_radius * math.cos(outer_extended_end),
                outer_radius * math.sin(outer_extended_end),
                geometry_height
            )
            
            line2_end_point = (
                inner_radius * math.cos(inner_extended_end),
                inner_radius * math.sin(inner_extended_end),
                geometry_height
            )
            
            # Create the second connecting line on the Geometry layer
            autocad_interface.create_line(line2_start_point, line2_end_point)
            
            # Switch back to TREADS layer
            autocad_interface.set_active_layer("TREADS")
            
            print("Created extended arcs: 2 arcs extended by 0.375\" at each end on Geometry layer (yellow)")
            print("Added two connecting lines between endpoints of outer and inner arcs at both extended angles")
            return True
            
        except Exception as e:
            print(f"Error creating widened 2D geometry: {str(e)}")
            return False

    def _create_widened_tread_mock(
        self, 
        autocad_interface: AutoCADInterface,
        start_angle: float,
        end_angle: float,
        inner_radius: float,
        outer_radius: float,
        tread_height: float
    ) -> bool:
        """Create widened tread geometry for mock AutoCAD interface."""
        try:
            # Calculate the widened tread geometry
            # 0.375" offset for both radial lines, outward direction
            offset_distance = 0.375
            
            # Calculate offset angles (perpendicular offset in angular direction)
            # For a radial line at angle theta, the offset angle is +/- offset_distance / radius
            angular_offset = offset_distance / outer_radius
            
            # Widen the tread by extending both the start and end angles outward
            widened_start_angle = start_angle - angular_offset
            widened_end_angle = end_angle + angular_offset
            
            # Create widened tread arc
            center = (0.0, 0.0, tread_height + 1.0)  # 1" higher than original for visibility
            widened_arc = autocad_interface.create_arc(
                center, outer_radius, widened_start_angle, widened_end_angle
            )
            widened_arc["inner_radius"] = inner_radius
            widened_arc["tread_height"] = tread_height + 1.0
            widened_arc["thickness"] = 0.25
            widened_arc["type"] = "widened_tread"

            # Add widened sector boundary lines
            widened_start_pt = (
                outer_radius * math.cos(widened_start_angle),
                outer_radius * math.sin(widened_start_angle),
                tread_height + 1.0,
            )
            end_pt = (0.0, 0.0, tread_height + 1.0)
            autocad_interface.create_line(widened_start_pt, end_pt)

            widened_end_pt = (
                outer_radius * math.cos(widened_end_angle),
                outer_radius * math.sin(widened_end_angle),
                tread_height + 1.0,
            )
            autocad_interface.create_line(widened_end_pt, end_pt)

            print(
                f"Mock AutoCAD: Created widened tread from {math.degrees(widened_start_angle):.1f}° to {math.degrees(widened_end_angle):.1f}° (offset: {offset_distance}\")"
            )
            
            return True
            
        except Exception as e:
            print(f"Error creating widened tread geometry: {str(e)}")
            return False

    def _create_original_tread_real(
        self,
        autocad_interface: AutoCADInterface,
        start_angle: float,
        end_angle: float,
        inner_radius: float,
        outer_radius: float,
        tread_height: float,
        is_clockwise: bool
    ) -> bool:
        """Create original tread geometry for real AutoCAD interface."""
        try:
            # Create the three entities that form the sector boundary
            # Entity 1: Line from center to outer edge at start angle
            start_point = (0.0, 0.0, tread_height)
            end_point = (
                outer_radius * math.cos(start_angle),
                outer_radius * math.sin(start_angle),
                tread_height
            )
            
            # Use interface method for line creation
            line1 = autocad_interface.create_line(start_point, end_point)
            
            # Entity 2: Arc from start angle to end angle
            arc_center = (0.0, 0.0, tread_height)
            
            # Handle direction for arc creation (like VBA logic)
            # VBA: If direction = 1 Then arc(center, radius, start, end) Else arc(center, radius, end, start)
            if is_clockwise:
                arc = autocad_interface.create_arc(arc_center, outer_radius, start_angle, end_angle)
            else:
                arc = autocad_interface.create_arc(arc_center, outer_radius, end_angle, start_angle)
            
            # Entity 3: Line from outer edge at end angle back to center
            start_point2 = (
                outer_radius * math.cos(end_angle),
                outer_radius * math.sin(end_angle),
                tread_height
            )
            end_point2 = (0.0, 0.0, tread_height)
            
            # Use interface method for line creation
            line2 = autocad_interface.create_line(start_point2, end_point2)
            
            # Create region from the three entities
            entities = [line1, arc, line2]
            regions = autocad_interface.create_region(entities)
            
            # Check if region was created successfully
            if regions and len(regions) > 0:
                region_obj = regions[0]
                
                # Extrude the region to create 3D solid (0.25" thick)
                tread_solid = autocad_interface.create_extruded_solid(region_obj, 0.25, 0)
                
                # Store for cleanup
                if not hasattr(self, '_created_entities'):
                    self._created_entities = []
                self._created_entities.append(tread_solid)
                
                print(
                    f"AutoCAD: Created original 3D solid sector tread from {math.degrees(start_angle):.1f}° to {math.degrees(end_angle):.1f}° at Z={tread_height:.2f}"
                )
                
                return True
            else:
                print(f"Failed to create region for original tread at Z={tread_height}")
                return False
                
        except Exception as e:
            print(f"Error creating original tread in AutoCAD: {str(e)}")
            return False

    def _create_widened_tread_real(
        self,
        autocad_interface: AutoCADInterface,
        start_angle: float,
        end_angle: float,
        inner_radius: float,
        outer_radius: float,
        tread_height: float,
        is_clockwise: bool
    ) -> bool:
        """Create widened tread geometry for real AutoCAD interface."""
        try:
            # Calculate the widened tread geometry
            # 0.375" offset for both radial lines, outward direction
            offset_distance = 0.375
            
            # Calculate offset angles (perpendicular offset in angular direction)
            # For a radial line at angle theta, the offset angle is +/- offset_distance / radius
            angular_offset = offset_distance / outer_radius
            
            # Widen the tread by extending both the start and end angles outward
            widened_start_angle = start_angle - angular_offset
            widened_end_angle = end_angle + angular_offset
            
            # Create the three entities that form the widened sector boundary
            # Entity 1: Line from center to outer edge at widened start angle
            start_point = (0.0, 0.0, tread_height + 1.0)  # 1" higher than original for visibility
            end_point = (
                outer_radius * math.cos(widened_start_angle),
                outer_radius * math.sin(widened_start_angle),
                tread_height + 1.0
            )
            
            line1 = autocad_interface.create_line(start_point, end_point)
            
            # Entity 2: Arc from widened start angle to widened end angle
            arc_center = (0.0, 0.0, tread_height + 1.0)
            
            if is_clockwise:
                arc = autocad_interface.create_arc(arc_center, outer_radius, widened_start_angle, widened_end_angle)
            else:
                arc = autocad_interface.create_arc(arc_center, outer_radius, widened_end_angle, widened_start_angle)
            
            # Entity 3: Line from outer edge at widened end angle back to center
            start_point2 = (
                outer_radius * math.cos(widened_end_angle),
                outer_radius * math.sin(widened_end_angle),
                tread_height + 1.0
            )
            end_point2 = (0.0, 0.0, tread_height + 1.0)
            
            line2 = autocad_interface.create_line(start_point2, end_point2)
            
            # Create region from the three entities
            entities = [line1, arc, line2]
            regions = autocad_interface.create_region(entities)
            
            # Check if region was created successfully
            if regions and len(regions) > 0:
                region_obj = regions[0]
                
                # Extrude the region to create 3D solid (0.25" thick)
                widened_solid = autocad_interface.create_extruded_solid(region_obj, 0.25, 0)
                
                # Store for cleanup
                if not hasattr(self, '_created_entities'):
                    self._created_entities = []
                self._created_entities.append(widened_solid)
                
                print(
                    f"AutoCAD: Created widened 3D solid tread from {math.degrees(widened_start_angle):.1f}° to {math.degrees(widened_end_angle):.1f}° (offset: {offset_distance}\")"
                )
                
                return True
            else:
                print(f"Failed to create region for widened tread at Z={tread_height + 1.0}")
                return False
                
        except Exception as e:
            print(f"Error creating widened tread in AutoCAD: {str(e)}")
            return False

    def add_tread_at_index(self, index: int, autocad_interface: AutoCADInterface, config: Dict[str, Any]) -> bool:
        """
        Add a new tread at the specified index.
        
        Args:
            index: Index where to insert the new tread
            autocad_interface: AutoCAD interface for geometry creation
            config: Configuration dictionary
            
        Returns:
            bool: True if addition successful
        """
        try:
            if not self.is_generated:
                print("Error: Treads must be generated first before adding individual treads")
                return False
                
            if index < 0 or index > len(self.treads_created):
                print(f"Error: Index {index} is out of range (0-{len(self.treads_created)})")
                return False
            
            basic_params = config.get("basic_parameters", {})
            is_clockwise = basic_params.get("is_clockwise", True)
            direction = 1 if is_clockwise else -1
            
            # Recalculate angles for all treads after insertion point
            if self.mid_landing_index >= 0 and index <= self.mid_landing_index:
                self.mid_landing_index += 1
                
            # Calculate new tread angle distribution
            num_treads = len(self.treads_created) + 1
            if self.mid_landing_index >= 0:
                new_tread_angle = (basic_params.get("total_rotation", 360) - 90) / (num_treads - 2)
            else:
                new_tread_angle = basic_params.get("total_rotation", 360) / (num_treads - 1)
                
            signed_tread_angle = direction * new_tread_angle
            
            # Get radii
            inner_radius = basic_params.get("center_pole_diameter", 5.0) / 2
            outer_radius = basic_params.get("outside_diameter", 72.0) / 2
            
            # Calculate angles for the new tread
            if index == 0:
                # First tread
                start_angle = 0.0
                end_angle = signed_tread_angle if self.mid_landing_index != 0 else direction * math.radians(90)
            elif index == len(self.treads_created):
                # Last tread
                prev_tread = self.treads_created[-1]
                start_angle = math.radians(prev_tread["end_angle"])
                end_angle = start_angle + (signed_tread_angle if self.mid_landing_index != index else direction * math.radians(90))
            else:
                # Middle tread
                prev_tread = self.treads_created[index - 1]
                start_angle = math.radians(prev_tread["end_angle"])
                end_angle = start_angle + (signed_tread_angle if self.mid_landing_index != index else direction * math.radians(90))
            
            # Calculate tread height
            tread_height = self.riser_height * (index + 1) - 0.25
            if tread_height + 0.25 > basic_params.get("overall_height", 120.0):
                tread_height = basic_params.get("overall_height", 120.0) - 0.25
                
            # Create the tread (color handled by layer)
            success = self._create_sector_tread(
                autocad_interface,
                start_angle,
                end_angle,
                inner_radius,
                outer_radius,
                tread_height,
                is_clockwise,
                config,
                index,
            )
            
            if success:
                # Insert the new tread in the list
                new_tread = {
                    "index": index,
                    "start_angle": math.degrees(start_angle),
                    "end_angle": math.degrees(end_angle),
                    "height": tread_height,
                    "is_mid_landing": index == self.mid_landing_index,
                }
                self.treads_created.insert(index, new_tread)
                
                # Update indices for subsequent treads
                for i in range(index + 1, len(self.treads_created)):
                    self.treads_created[i]["index"] = i
                    
                # Recalculate remaining tread angles
                self._recalculate_tread_angles(autocad_interface, config, index + 1)
                
                self.tread_count = len(self.treads_created)
                print(f"Successfully added tread at index {index}")
                return True
            else:
                print(f"Failed to create tread at index {index}")
                return False
                
        except Exception as e:
            print(f"Error adding tread at index {index}: {str(e)}")
            return False
    
    def remove_tread_at_index(self, index: int, autocad_interface: AutoCADInterface) -> bool:
        """
        Remove a tread at the specified index.
        
        Args:
            index: Index of tread to remove
            autocad_interface: AutoCAD interface for geometry removal
            
        Returns:
            bool: True if removal successful
        """
        try:
            if not self.is_generated:
                print("Error: No treads generated to remove")
                return False
                
            if index < 0 or index >= len(self.treads_created):
                print(f"Error: Index {index} is out of range (0-{len(self.treads_created)-1})")
                return False
                
            if len(self.treads_created) <= 2:
                print("Error: Cannot remove treads - minimum tread count is 2")
                return False
            
            # Remove the tread entity from AutoCAD
            if hasattr(autocad_interface, 'model_space') and hasattr(self, '_created_entities'):
                try:
                    if index < len(self._created_entities):
                        entity_to_remove = self._created_entities[index]
                        entity_to_remove.Delete()
                        self._created_entities.pop(index)
                except Exception as e:
                    print(f"Warning: Could not remove AutoCAD entity: {str(e)}")
            
            # Remove from tread list
            removed_tread = self.treads_created.pop(index)
            
            # Update mid-landing index if needed
            if self.mid_landing_index > index:
                self.mid_landing_index -= 1
            elif self.mid_landing_index == index:
                self.mid_landing_index = -1  # Remove mid-landing
                
            # Update indices for remaining treads
            for i in range(index, len(self.treads_created)):
                self.treads_created[i]["index"] = i
                
            self.tread_count = len(self.treads_created)
            print(f"Successfully removed tread at index {index}")
            return True
            
        except Exception as e:
            print(f"Error removing tread at index {index}: {str(e)}")
            return False
    
    def modify_tread(self, index: int, params: Dict[str, Any], autocad_interface: AutoCADInterface, config: Dict[str, Any]) -> bool:
        """
        Modify an existing tread at the specified index.
        
        Args:
            index: Index of tread to modify
            params: Dictionary of parameters to modify (angle, height, etc.)
            autocad_interface: AutoCAD interface for geometry modification
            config: Configuration dictionary
            
        Returns:
            bool: True if modification successful
        """
        try:
            if not self.is_generated:
                print("Error: No treads generated to modify")
                return False
                
            if index < 0 or index >= len(self.treads_created):
                print(f"Error: Index {index} is out of range (0-{len(self.treads_created)-1})")
                return False
            
            # Remove the existing tread
            if not self.remove_tread_at_index(index, autocad_interface):
                print(f"Error: Could not remove existing tread at index {index}")
                return False
            
            # Get basic parameters
            basic_params = config.get("basic_parameters", {})
            is_clockwise = basic_params.get("is_clockwise", True)
            direction = 1 if is_clockwise else -1
            
            # Calculate new parameters
            new_start_angle = params.get("start_angle", None)
            new_end_angle = params.get("end_angle", None)
            new_height = params.get("height", None)
            
            # Use existing values if not provided
            if index == 0:
                start_angle = 0.0 if new_start_angle is None else math.radians(new_start_angle)
            else:
                prev_tread = self.treads_created[index - 1]
                start_angle = math.radians(prev_tread["end_angle"]) if new_start_angle is None else math.radians(new_start_angle)
            
            if new_end_angle is not None:
                end_angle = math.radians(new_end_angle)
            else:
                # Calculate based on tread angle
                if self.mid_landing_index >= 0:
                    tread_angle = (basic_params.get("total_rotation", 360) - 90) / (len(self.treads_created) - 1)
                else:
                    tread_angle = basic_params.get("total_rotation", 360) / len(self.treads_created)
                end_angle = start_angle + (tread_angle * direction if index != self.mid_landing_index else direction * math.radians(90))
            
            # Get radii
            inner_radius = basic_params.get("center_pole_diameter", 5.0) / 2
            outer_radius = basic_params.get("outside_diameter", 72.0) / 2
            
            # Calculate height
            if new_height is not None:
                tread_height = new_height
            else:
                tread_height = self.riser_height * (index + 1) - 0.25
                if tread_height + 0.25 > basic_params.get("overall_height", 120.0):
                    tread_height = basic_params.get("overall_height", 120.0) - 0.25
            
            # Create the modified tread (color handled by layer)
            success = self._create_sector_tread(
                autocad_interface,
                start_angle,
                end_angle,
                inner_radius,
                outer_radius,
                tread_height,
                is_clockwise,
                config,
                index,
            )
            
            if success:
                # Insert the modified tread
                modified_tread = {
                    "index": index,
                    "start_angle": math.degrees(start_angle),
                    "end_angle": math.degrees(end_angle),
                    "height": tread_height,
                    "is_mid_landing": index == self.mid_landing_index,
                }
                self.treads_created.insert(index, modified_tread)
                
                # Update indices for subsequent treads
                for i in range(index + 1, len(self.treads_created)):
                    self.treads_created[i]["index"] = i
                
                self.tread_count = len(self.treads_created)
                print(f"Successfully modified tread at index {index}")
                return True
            else:
                print(f"Failed to create modified tread at index {index}")
                return False
                
        except Exception as e:
            print(f"Error modifying tread at index {index}: {str(e)}")
            return False
    
    def _recalculate_tread_angles(self, autocad_interface: AutoCADInterface, config: Dict[str, Any], start_index: int) -> None:
        """
        Recalculate angles for treads starting from the specified index.
        
        Args:
            autocad_interface: AutoCAD interface
            config: Configuration dictionary
            start_index: Index from which to start recalculating
        """
        try:
            basic_params = config.get("basic_parameters", {})
            is_clockwise = basic_params.get("is_clockwise", True)
            direction = 1 if is_clockwise else -1
            
            # Calculate new tread angle distribution
            num_treads = len(self.treads_created)
            if self.mid_landing_index >= 0:
                new_tread_angle = (basic_params.get("total_rotation", 360) - 90) / (num_treads - 2)
            else:
                new_tread_angle = basic_params.get("total_rotation", 360) / (num_treads - 1)
                
            signed_tread_angle = direction * new_tread_angle
            
            # Get radii
            inner_radius = basic_params.get("center_pole_diameter", 5.0) / 2
            outer_radius = basic_params.get("outside_diameter", 72.0) / 2
            
            # Recalculate from start_index onwards
            for i in range(start_index, num_treads):
                if i == 0:
                    start_angle = 0.0
                else:
                    prev_tread = self.treads_created[i - 1]
                    start_angle = math.radians(prev_tread["end_angle"])
                
                end_angle = start_angle + (signed_tread_angle if i != self.mid_landing_index else direction * math.radians(90))
                
                # Calculate tread height
                tread_height = self.riser_height * (i + 1) - 0.25
                if tread_height + 0.25 > basic_params.get("overall_height", 120.0):
                    tread_height = basic_params.get("overall_height", 120.0) - 0.25
                
                # Remove old tread entity
                if hasattr(autocad_interface, 'model_space') and hasattr(self, '_created_entities'):
                    try:
                        if i < len(self._created_entities):
                            old_entity = self._created_entities[i]
                            old_entity.Delete()
                            self._created_entities.pop(i)
                    except Exception as e:
                        print(f"Warning: Could not remove old tread entity: {str(e)}")
                
                # Create new tread (color handled by layer)
                success = self._create_sector_tread(
                    autocad_interface,
                    start_angle,
                    end_angle,
                    inner_radius,
                    outer_radius,
                    tread_height,
                    is_clockwise,
                    config,
                    i,
                )
                
                if success:
                    # Update tread data
                    self.treads_created[i] = {
                        "index": i,
                        "start_angle": math.degrees(start_angle),
                        "end_angle": math.degrees(end_angle),
                        "height": tread_height,
                        "is_mid_landing": i == self.mid_landing_index,
                    }
                else:
                    print(f"Failed to recalculate tread at index {i}")
                    
        except Exception as e:
            print(f"Error recalculating tread angles: {str(e)}")

    def cleanup(self, autocad_interface: AutoCADInterface) -> None:
        """
        Clean up tread geometries on failure.

        Args:
            autocad_interface: AutoCAD interface
        """
        try:
            if hasattr(autocad_interface, "entities"):  # Mock interface
                print("Mock AutoCAD: Cleaning up tread geometries")
            else:
                print("Real AutoCAD: Cleaning up tread geometries")
                
                # Clean up created entities if they exist
                if hasattr(self, '_created_entities'):
                    for entity in self._created_entities:
                        try:
                            entity.Delete()
                        except Exception as e:
                            print(f"Warning: Could not delete entity: {str(e)}")
                    self._created_entities.clear()

            self.treads_created.clear()
            self.tread_count = 0

        except Exception as e:
            print(f"Error during tread cleanup: {str(e)}")


    def get_geometry_info(self) -> Dict[str, Any]:
        """
        Get detailed information about generated tread geometry.

        Returns:
            Dict with tread geometry details
        """
        if not self.is_generated:
            return {"status": "not_generated"}

        return {
            "status": "generated",
            "tread_count": self.tread_count,
            "riser_height": round(self.riser_height, 3),
            "tread_angle": round(self.tread_angle, 2),
            "mid_landing_index": self.mid_landing_index,
            "treads_created": self.treads_created,
            "note": "Matches VBA CreateSectorTread function with enhanced error handling",
        }

    def validate_ibc_compliance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate IBC compliance requirements for tread geometry.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict with compliance validation results
        """
        try:
            basic_params = config.get("basic_parameters", {})
            
            # Extract parameters
            center_pole_dia = basic_params.get("center_pole_diameter", 5.0)
            overall_height = basic_params.get("overall_height", 120.0)
            outside_dia = basic_params.get("outside_diameter", 72.0)
            total_rotation = basic_params.get("total_rotation", 360.0)
            
            # Calculate derived parameters
            num_treads = self._calculate_num_treads(overall_height)
            riser_height = overall_height / num_treads
            
            # Check for mid-landing requirement
            mid_landing_index = -1
            if overall_height > 151:
                mid_landing_index = round(num_treads / 2) - 1
            
            # Calculate tread angle
            if mid_landing_index >= 0:
                tread_angle = (total_rotation - 90) / (num_treads - 2)
            else:
                tread_angle = total_rotation / (num_treads - 1)
            
            # Calculate walkline radius (12" from center pole edge)
            walkline_radius = (center_pole_dia / 2) + 12
            walkline_width = walkline_radius * abs(math.radians(tread_angle))
            
            # Initialize compliance results
            compliance_results = {
                "is_compliant": True,
                "violations": [],
                "warnings": [],
                "measurements": {
                    "riser_height": riser_height,
                    "walkline_width": walkline_width,
                    "num_treads": num_treads,
                    "tread_angle": tread_angle,
                    "overall_height": overall_height,
                    "has_mid_landing": mid_landing_index >= 0
                }
            }
            
            # IBC 1011.5.2: Riser height shall not exceed 9.5 inches (241 mm)
            if riser_height > 9.5:
                compliance_results["is_compliant"] = False
                compliance_results["violations"].append({
                    "code": "IBC 1011.5.2",
                    "requirement": "Riser height shall not exceed 9.5 inches",
                    "measured": riser_height,
                    "limit": 9.5,
                    "severity": "critical"
                })
            elif riser_height > 9.0:
                compliance_results["warnings"].append({
                    "code": "IBC 1011.5.2",
                    "requirement": "Riser height should not exceed 9.0 inches for optimal safety",
                    "measured": riser_height,
                    "limit": 9.0,
                    "severity": "warning"
                })
            
            # IBC 1011.6: Tread depth at walkline shall be not less than 6.75 inches (171 mm)
            if walkline_width < 6.75:
                compliance_results["is_compliant"] = False
                compliance_results["violations"].append({
                    "code": "IBC 1011.6",
                    "requirement": "Tread depth at walkline shall be not less than 6.75 inches",
                    "measured": walkline_width,
                    "limit": 6.75,
                    "severity": "critical"
                })
            elif walkline_width < 7.5:
                compliance_results["warnings"].append({
                    "code": "IBC 1011.6",
                    "requirement": "Tread depth at walkline should be at least 7.5 inches for comfort",
                    "measured": walkline_width,
                    "limit": 7.5,
                    "severity": "warning"
                })
            
            # IBC 1011.8: Mid-landing requirement for stairs exceeding 151 inches in height
            if overall_height > 151 and mid_landing_index < 0:
                compliance_results["is_compliant"] = False
                compliance_results["violations"].append({
                    "code": "IBC 1011.8",
                    "requirement": "Mid-landing required for stairs exceeding 151 inches in height",
                    "measured": overall_height,
                    "limit": 151,
                    "severity": "critical"
                })
            
            # Additional safety checks
            if num_treads < 2:
                compliance_results["is_compliant"] = False
                compliance_results["violations"].append({
                    "code": "SAFETY",
                    "requirement": "Minimum of 2 treads required",
                    "measured": num_treads,
                    "limit": 2,
                    "severity": "critical"
                })
            
            # Check for excessive tread angles (safety concern)
            if abs(tread_angle) > 45:
                compliance_results["warnings"].append({
                    "code": "SAFETY",
                    "requirement": "Tread angle should not exceed 45 degrees for safety",
                    "measured": abs(tread_angle),
                    "limit": 45,
                    "severity": "warning"
                })
            
            # Check for adequate clearance
            if outside_dia < 48:
                compliance_results["warnings"].append({
                    "code": "SAFETY",
                    "requirement": "Outside diameter should be at least 48 inches for adequate clearance",
                    "measured": outside_dia,
                    "limit": 48,
                    "severity": "warning"
                })
            
            # Generate recommendations
            recommendations = []
            
            if not compliance_results["is_compliant"]:
                recommendations.append("Design does not meet IBC requirements. Modifications required.")
                
                # Specific recommendations based on violations
                for violation in compliance_results["violations"]:
                    if violation["code"] == "IBC 1011.5.2":
                        recommendations.append(f"Reduce riser height from {violation['measured']:.2f}\" to ≤{violation['limit']}\" by increasing number of treads.")
                    elif violation["code"] == "IBC 1011.6":
                        recommendations.append(f"Increase tread depth at walkline from {violation['measured']:.2f}\" to ≥{violation['limit']}\" by increasing outside diameter or reducing tread angle.")
                    elif violation["code"] == "IBC 1011.8":
                        recommendations.append("Add mid-landing for stairs exceeding 151 inches in height.")
            else:
                recommendations.append("Design meets IBC requirements.")
                
                if compliance_results["warnings"]:
                    recommendations.append("Consider addressing warnings for improved safety and comfort.")
            
            compliance_results["recommendations"] = recommendations
            
            return compliance_results
            
        except Exception as e:
            return {
                "is_compliant": False,
                "violations": [{
                    "code": "ERROR",
                    "requirement": "IBC compliance validation failed",
                    "measured": "N/A",
                    "limit": "N/A",
                    "severity": "critical",
                    "error": str(e)
                }],
                "warnings": [],
                "recommendations": ["Error occurred during validation. Check configuration and try again."],
                "measurements": {}
            }