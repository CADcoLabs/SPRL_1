"""
Vertical Picket Module - Creates vertical balusters for spiral staircase.
Extracted from the original unified picket module to preserve flawless vertical functionality.
"""

import math
from typing import Dict, Any, List
from core.base_component import BaseStairComponent
from core.autocad_interface import AutoCADInterface


class VerticalPicketModule(BaseStairComponent):
    """
    Creates vertical balusters for spiral staircase.

    Vertical pickets are safety barrier elements that:
    - Provide fall protection for users
    - Comply with IBC 4" sphere rule (edge-to-edge spacing ≤ 4")
    - Are positioned along the outer edge of treads
    - Create identical patterns on all treads
    - Connect to handrail helix system
    - Support various materials (aluminum, steel, wood, composite)
    """

    def __init__(self):
        """Initialize vertical picket module."""
        super().__init__("Vertical Pickets")
        self.pickets_created = []
        self.picket_count = 0
        self.picket_spacing = 3.5  # Default spacing in inches
        self.picket_positions = []

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
        Validate parameters for vertical picket generation.

        Args:
            config: Configuration dictionary containing all parameters

        Returns:
            bool: True if parameters are valid

        Raises:
            ValueError: If parameters are invalid with descriptive message
        """
        # Get vertical picket configuration
        vertical_config = config.get("vertical_picket_configuration", {})
        
        # Check if vertical pickets are enabled
        if not vertical_config.get("enabled", False):
            return True  # Skip validation if not enabled
        
        # Validate vertical picket configuration parameters
        spacing = vertical_config.get("spacing_inches", 3.5)
        material = vertical_config.get("material", "aluminum")
        diameter = vertical_config.get("diameter", 0.75)
        quantity = vertical_config.get("quantity", 3)
        position = vertical_config.get("position", "outer")

        # Validate spacing (IBC 4" sphere rule - edge-to-edge measurement)
        if spacing <= 0 or spacing > 4.0:
            raise ValueError(
                f'Vertical picket edge-to-edge spacing must be between 0 and 4 inches '
                f'(IBC 4" sphere rule). Got: {spacing}'
            )

        # Validate material
        valid_materials = ["aluminum", "steel", "wood", "composite"]
        if material not in valid_materials:
            raise ValueError(
                f"Vertical picket material must be one of {valid_materials}. "
                f"Got: {material}"
            )
        
        # Validate diameter
        if diameter <= 0 or diameter > 2.0:
            raise ValueError(
                f"Vertical picket diameter must be between 0 and 2.0 inches. "
                f"Got: {diameter}"
            )
        
        # Validate quantity
        if quantity < 1 or quantity > 20:
            raise ValueError(
                f"Vertical picket quantity must be between 1 and 20 per tread section. "
                f"Got: {quantity}"
            )
        
        # Validate position
        valid_positions = ["outer", "inner", "middle"]
        if position not in valid_positions:
            raise ValueError(
                f"Vertical picket position must be one of {valid_positions}. "
                f"Got: {position}"
            )

        return True

    def generate_geometry(
        self,
        autocad_interface: AutoCADInterface,
        config: Dict[str, Any]
    ) -> bool:
        """
        Generate vertical picket geometries for spiral staircase.

        Args:
            autocad_interface: AutoCAD interface for geometry creation
            config: Configuration dictionary

        Returns:
            bool: True if generation successful
        """
        try:
            # Get vertical picket configuration
            vertical_config = config.get("vertical_picket_configuration", {})
            basic_params = config.get("basic_parameters", {})

            # Check if vertical pickets are enabled
            if not vertical_config.get("enabled", False):
                print("Vertical pickets disabled in configuration - "
                      "skipping vertical picket generation")
                self.is_generated = True
                return True

            # Extract parameters
            center_pole_dia = basic_params.get("center_pole_diameter")
            overall_height = basic_params.get("overall_height")
            outside_dia = basic_params.get("outside_diameter")
            total_rotation = basic_params.get("total_rotation")
            is_clockwise = basic_params.get("is_clockwise", True)

            # Vertical picket configuration parameters
            quantity_per_tread = vertical_config.get("quantity", 3)
            material = vertical_config.get("material", "aluminum")
            picket_diameter = vertical_config.get("diameter", 0.75)
            position = vertical_config.get("position", "outer")
            self.picket_spacing = vertical_config.get("spacing_inches", 3.5)

            # Calculate basic geometry
            center_pole_radius = center_pole_dia / 2
            outside_radius = outside_dia / 2

            print(f"Creating vertical pickets with {quantity_per_tread} "
                  f"per tread")
            print(f"Material: {material}, Diameter: {picket_diameter}\", "
                  f"Position: {position}")
            print(f"Target edge-to-edge spacing: {self.picket_spacing}\" (IBC compliant)")

            # Set the PICKETS layer as active (assuming it's already created by the orchestrator)
            print("Attempting to set active layer to PICKETS")
            autocad_interface.set_active_layer("PICKETS")
            print("Set active layer to PICKETS")

            # Generate vertical pickets using proven algorithm
            success = self._generate_vertical_pickets(
                autocad_interface,
                config,
                center_pole_radius,
                outside_radius,
                outside_dia,
                overall_height,
                total_rotation,
                is_clockwise,
                quantity_per_tread,
                picket_diameter,
                material,
            )

            if not success:
                return False

            self.is_generated = True
            self.picket_count = len(self.pickets_created)

            print(f"Successfully created {self.picket_count} vertical picket entities")
            return True

        except Exception as e:
            self.last_error = str(e)
            print(f"Error generating vertical pickets: {e}")
            self.cleanup(autocad_interface)
            return False

    def cleanup(self, autocad_interface: AutoCADInterface) -> None:
        """
        Cleanup any partial geometry if generation fails.

        Args:
            autocad_interface: AutoCAD COM interface wrapper
        """
        # Clean up any created entities
        self.pickets_created = []
        self.picket_count = 0
        self.picket_positions = []
        print("Vertical picket module cleanup completed")

    def _calculate_edge_to_edge_spacing(
        self, 
        center_to_center_distance: float, 
        picket_diameter: float
    ) -> float:
        """
        Calculate edge-to-edge spacing from center-to-center distance.
        
        This is the critical IBC compliance measurement - the actual gap
        between picket edges that a 4" sphere could pass through.
        
        Args:
            center_to_center_distance: Distance between picket centers
            picket_diameter: Diameter of pickets
            
        Returns:
            Edge-to-edge spacing (the actual gap between pickets)
        """
        # Edge-to-edge = center-to-center - (radius1 + radius2)
        # For identical pickets: edge-to-edge = center-to-center - diameter
        edge_spacing = center_to_center_distance - picket_diameter
        return edge_spacing

    def get_status(self) -> Dict[str, Any]:
        """
        Get current component status for debugging and monitoring.

        Returns:
            Dict with component status information
        """
        status = super().get_status()
        status.update({
            "pickets_created": self.picket_count,
            "picket_positions": len(self.picket_positions),
        })
        return status

    def _generate_vertical_pickets(
        self,
        autocad_interface: AutoCADInterface,
        config: Dict[str, Any],
        center_pole_radius: float,
        outside_radius: float,
        outside_dia: float,
        overall_height: float,
        total_rotation: float,
        is_clockwise: bool,
        quantity_per_tread: int,
        picket_diameter: float,
        material: str,
    ) -> bool:
        """
        Generate vertical pickets on ALL TREADS using the same pattern.
        
        This creates the exact same picket pattern on every tread throughout
        the spiral staircase, positioned at each tread's specific height.
        
        PRESERVED ALGORITHM - This is the proven, flawless implementation
        that maintains IBC compliance and proper handrail integration.
        
        Approach:
        1. Calculate tread geometry and heights for all treads
        2. Apply IBC-compliant picket spacing algorithm (same for all treads)
        3. Create identical picket patterns on each tread at correct Z heights
        4. Extend lines upward to show handrail connection
        
        Args:
            autocad_interface: AutoCAD interface
            config: Configuration dictionary
            center_pole_radius: Radius of center pole
            outside_radius: Outside radius of stair
            outside_dia: Outside diameter of stair
            overall_height: Total height of stair (for handrail calculation)
            total_rotation: Total rotation in degrees
            is_clockwise: Direction of rotation
            quantity_per_tread: Number of pickets per tread (reference)
            picket_diameter: Diameter of pickets in inches
            material: Material for pickets

        Returns:
            bool: True if generation successful
        """
        try:
            # Get handrail configuration
            handrail_config = config.get("handrail_configuration", {})
            handrail_diameter = handrail_config.get("diameter", 1.5)
            handrail_height_above_tread = handrail_config.get("height_above_tread", 36.0)
            
            print("ALL TREADS VERTICAL PICKET IMPLEMENTATION")
            print("Creating identical picket patterns on every tread")
            print(f"  Outside diameter: {outside_radius * 2:.1f}\" (radius: {outside_radius:.1f}\")")
            print(f"  Handrail diameter: {handrail_diameter}\"")
            print(f"  Picket diameter: {picket_diameter}\"")
            print("  IBC Requirement: Edge-to-edge spacing <= 4.0\"")
            
            # Calculate tread geometry for all treads
            import math
            num_treads = math.ceil(overall_height / 9.5)  # Same formula as tread module
            tread_angle_degrees = total_rotation / (num_treads - 1)  # Angle per tread
            riser_height = 9.0  # Standard riser height in inches
            
            print(f"\nTREAD GEOMETRY FOR ALL TREADS:")
            print(f"  Total treads: {num_treads}")
            print(f"  Tread angle: {tread_angle_degrees:.1f}°")
            print(f"  Riser height: {riser_height:.1f}\"")
            
            # Calculate picket placement radius to align with handrail position
            # Use same logic as handrail module: (outside_diameter - handrail_diameter) / 2
            picket_placement_radius = (outside_dia - handrail_diameter) / 2
            
            print(f"\nPICKET POSITIONING ALIGNMENT:")
            print(f"  Outside diameter: {outside_dia}\"")
            print(f"  Handrail diameter: {handrail_diameter}\"")
            print(f"  Handrail radius (from center): {picket_placement_radius:.2f}\"")
            print(f"  Pickets positioned directly under handrail center")
            
            # Find optimal picket division using IBC compliance (same for all treads)
            print(f"\nOPTIMIZING PICKET SPACING (SAME FOR ALL TREADS):")
            best_divisions = None
            best_edge_spacing = 0.0
            best_positions_template = []
            
            # Use relative positions (0° to tread_angle_degrees)
            arc_start_angle = 0.0
            arc_end_angle = tread_angle_degrees
            
            for num_divisions in range(2, 8):
                # Calculate positions for this division count
                positions = []
                if num_divisions == 1:
                    # Single picket at middle
                    angle_deg = (arc_start_angle + arc_end_angle) / 2
                    angle_rad = math.radians(angle_deg)
                    x = picket_placement_radius * math.cos(angle_rad)
                    y = picket_placement_radius * math.sin(angle_rad)
                    positions.append((x, y, angle_deg))
                else:
                    # Multiple pickets evenly spaced
                    angular_step = tread_angle_degrees / (num_divisions - 1)
                    for i in range(num_divisions):
                        angle_deg = arc_start_angle + (i * angular_step)
                        angle_rad = math.radians(angle_deg)
                        x = picket_placement_radius * math.cos(angle_rad)
                        y = picket_placement_radius * math.sin(angle_rad)
                        positions.append((x, y, angle_deg))
                
                # Calculate spacing between adjacent pickets
                if len(positions) < 2:
                    max_edge_spacing = 999  # Single picket, no spacing issue
                else:
                    center_spacings = []
                    for i in range(len(positions) - 1):
                        pos1, pos2 = positions[i], positions[i + 1]
                        dx, dy = pos2[0] - pos1[0], pos2[1] - pos1[1]
                        center_distance = math.sqrt(dx*dx + dy*dy)
                        center_spacings.append(center_distance)
                    
                    # Convert to edge-to-edge spacing
                    edge_spacings = [c - picket_diameter for c in center_spacings]
                    max_edge_spacing = max(edge_spacings) if edge_spacings else 0
                
                is_compliant = max_edge_spacing <= 4.0
                print(f"  {num_divisions} divisions: edge spacing = {max_edge_spacing:.2f}\" "
                      f"{'COMPLIANT' if is_compliant else 'TOO LARGE'}")
                
                # Choose largest compliant spacing for efficiency
                if is_compliant and max_edge_spacing > best_edge_spacing:
                    best_divisions = num_divisions
                    best_edge_spacing = max_edge_spacing
                    best_positions_template = positions
            
            if best_divisions is None:
                print("  ERROR: No compliant division found")
                return False
            
            print(f"\nOPTIMAL SOLUTION:")
            print(f"  Divisions: {best_divisions}")
            print(f"  Edge spacing: {best_edge_spacing:.2f}\" (max allowed: 4.0\")")
            print(f"  Picket count per tread: {len(best_positions_template)}")
            
            # Create the same picket pattern on every tread
            print(f"\nCREATING PICKETS ON ALL TREADS:")
            picket_size = picket_diameter  # Use diameter as square size
            total_created_pickets = []
            construction_arcs = []  # Track construction arcs separately
            
            # Loop through all treads except the last one (to avoid extra picket pattern at top landing)
            for tread_num in range(num_treads - 1):
                tread_height = riser_height * (tread_num + 1)  # Each tread is one riser higher
                tread_start_angle = tread_num * tread_angle_degrees  # Starting angle for this tread
                
                print(f"\n  TREAD {tread_num + 1}: Height Z={tread_height:.1f}\", Start Angle={tread_start_angle:.1f}°")
                
                # Create construction arcs for this tread
                arc_center = (0.0, 0.0, tread_height)
                arc_start_rad = math.radians(tread_start_angle)
                arc_end_rad = math.radians(tread_start_angle + tread_angle_degrees)
                
                # Outer tread edge arc
                outer_arc = autocad_interface.create_arc(
                    arc_center, outside_radius, arc_start_rad, arc_end_rad
                )
                if outer_arc:
                    self.pickets_created.append(outer_arc)
                    construction_arcs.append(outer_arc)  # Track for later deletion
                
                # Inner tread edge arc
                inner_arc = autocad_interface.create_arc(
                    arc_center, center_pole_radius, arc_start_rad, arc_end_rad
                )
                if inner_arc:
                    self.pickets_created.append(inner_arc)
                    construction_arcs.append(inner_arc)  # Track for later deletion
                
                # Apply the same pattern to this tread
                tread_created_pickets = []
                for i, (template_x, template_y, relative_angle) in enumerate(best_positions_template):
                    # Calculate actual angle for this tread
                    actual_angle_deg = tread_start_angle + relative_angle
                    
                    # Skip the shortest picket (at relative angle 0°)
                    if relative_angle == 0.0:
                        print(f"    Skipping shortest picket at relative angle {relative_angle:.1f}°")
                        continue
                    
                    # Calculate actual position for this tread
                    actual_angle_rad = math.radians(actual_angle_deg)
                    x = picket_placement_radius * math.cos(actual_angle_rad)
                    y = picket_placement_radius * math.sin(actual_angle_rad)
                    
                    # Create square picket at this tread level
                    half_size = picket_size / 2
                    
                    # Calculate rotation angle (perpendicular to radial direction)
                    cos_a = math.cos(actual_angle_rad)
                    sin_a = math.sin(actual_angle_rad)
                    
                    # Create rotated square corners (aligned with arc)
                    corner1 = (x - half_size * cos_a - half_size * (-sin_a), 
                              y - half_size * sin_a - half_size * cos_a, tread_height)
                    corner2 = (x + half_size * cos_a - half_size * (-sin_a), 
                              y + half_size * sin_a - half_size * cos_a, tread_height)
                    corner3 = (x + half_size * cos_a + half_size * (-sin_a), 
                              y + half_size * sin_a + half_size * cos_a, tread_height)
                    corner4 = (x - half_size * cos_a + half_size * (-sin_a), 
                              y - half_size * sin_a + half_size * cos_a, tread_height)
                    
                    # Create 4 lines to form square
                    line1 = autocad_interface.create_line(corner1, corner2)
                    line2 = autocad_interface.create_line(corner2, corner3)
                    line3 = autocad_interface.create_line(corner3, corner4)
                    line4 = autocad_interface.create_line(corner4, corner1)
                    
                    if line1 and line2 and line3 and line4:
                        self.pickets_created.extend([line1, line2, line3, line4])
                        tread_created_pickets.append((x, y, actual_angle_deg, relative_angle))
                        self.picket_positions.append((x, y, tread_height))
                        print(f"    Picket {i+1}: {picket_size:.2f}\" square at angle {actual_angle_deg:.1f}° (relative {relative_angle:.1f}°), Z={tread_height}\"")
                        
                        # Add micro-delay after each picket creation to prevent positioning errors
                        import time
                        time.sleep(0.02)  # 20ms delay after each picket
                    else:
                        print(f"    FAILED to create square picket {i+1}")
                
                total_created_pickets.extend(tread_created_pickets)
                
                # Add small delay after completing each tread to prevent COM timing issues
                import time
                time.sleep(0.05)  # 50ms delay after each tread
            
            # Create vertical lines to handrail helix intersection for all pickets
            print(f"\nCREATING VERTICAL LINES TO HANDRAIL HELIX:")
            
            # Get handrail helix parameters (matching handrail_module.py)
            handrail_radius = (outside_dia - handrail_diameter) / 2
            turns = total_rotation / 337.5
            helix_height = overall_height
            helix_start_z = handrail_height_above_tread  # Helix starts at height_above_tread
            
            print(f"  Handrail helix parameters:")
            print(f"    Radius: {handrail_radius:.2f}\"")
            print(f"    Turns: {turns:.3f}")
            print(f"    Height: {helix_height:.1f}\"")
            print(f"    Start Z: {helix_start_z:.1f}\"")
            print(f"    Helix end Z: {helix_start_z + helix_height:.1f}\"")
            
            # Calculate vertical lines for all created pickets
            shortest_picket_length = handrail_height_above_tread  # 36"
            
            for i, (x, y, actual_angle_deg, relative_angle) in enumerate(total_created_pickets):
                # Find which tread this picket belongs to
                tread_num = int(actual_angle_deg // tread_angle_degrees)
                
                # Calculate the picket length based on relative position within its tread
                progress_in_tread = relative_angle / tread_angle_degrees  # 0.0 to 1.0 across tread
                
                # Set start position - adjust tallest picket down one riser
                picket_start_z = riser_height * (tread_num + 1)
                if progress_in_tread == 1.0:  # Tallest picket - bring bottom down one riser
                    picket_start_z = picket_start_z - riser_height
                
                # Interpolate between shortest and tallest based on position
                picket_length = shortest_picket_length + (progress_in_tread * riser_height)
                
                # End point is start + length
                picket_end_z = picket_start_z + picket_length
                
                start_point = (x, y, picket_start_z)
                end_point = (x, y, picket_end_z)
                
                vertical_line = autocad_interface.create_line(start_point, end_point)
                if vertical_line:
                    self.pickets_created.append(vertical_line)
                    print(f"  Line {i+1}: length {picket_length:.1f}\" "
                          f"(Z={picket_start_z:.1f}\" to Z={picket_end_z:.1f}\") "
                          f"[tread {tread_num+1}, angle {actual_angle_deg:.1f}°, progress {progress_in_tread:.1%}]")
                    
                    # Add micro-delay after each vertical line to prevent completion failures
                    import time
                    time.sleep(0.015)  # 15ms delay after each vertical line
            
            print(f"\nALL TREADS VERTICAL PICKET CREATION COMPLETE:")
            print(f"  Total treads: {num_treads}")
            print(f"  Total entities: {len(self.pickets_created)}")
            print(f"  - {num_treads * 2} construction arcs (tread boundaries)")
            print(f"  - {len(total_created_pickets) * 4} lines forming {len(total_created_pickets)} square pickets ({picket_size:.2f}\" each)")
            print(f"  - {len(total_created_pickets)} vertical lines to handrail")
            print(f"  Identical pattern on every tread at correct heights")
            print(f"  IBC compliant edge spacing: {best_edge_spacing:.2f}\"")
            
            # Delete construction arcs as they're only needed for generation
            print(f"\nDELETING CONSTRUCTION ARCS:")
            deleted_count = 0
            for arc in construction_arcs:
                try:
                    # Try to delete the arc directly
                    if hasattr(arc, "Delete"):
                        arc.Delete()
                        self.pickets_created.remove(arc)  # Remove from tracking list
                        deleted_count += 1
                    # Fallback for mock environment
                    elif hasattr(autocad_interface, "entities") and arc in autocad_interface.entities:
                        autocad_interface.entities.remove(arc)
                        self.pickets_created.remove(arc)  # Remove from tracking list
                        deleted_count += 1
                    else:
                        print(f"  Warning: Could not delete construction arc - no deletion method available")
                except Exception as e:
                    print(f"  Warning: Failed to delete construction arc: {e}")
            
            print(f"  Deleted {deleted_count} construction arcs")
            
            # Perform batch JOIN operation on all entities on the PICKETS layer
            print(f"\nPERFORMING BATCH JOIN OPERATION:")
            try:
                # Select all entities on the PICKETS layer
                selection_set = autocad_interface.select_entities_by_layer("PICKETS")
                
                # Send the JOIN command to AutoCAD
                # Note: In AutoCAD, the JOIN command works on the current selection
                autocad_interface.send_command("JOIN")
                
                print(f"  Batch JOIN operation completed successfully")
            except Exception as e:
                print(f"  Warning: Batch JOIN operation failed: {e}")
                # This is not a critical failure, so we continue
            
            return True
            
        except Exception as e:
            print(f"Error generating vertical pickets: {str(e)}")
            return False

    def _calculate_num_treads(self, overall_height: float) -> int:
        """
        Calculate number of treads based on overall height.
        Uses same logic as other modules for consistency.

        Args:
            overall_height: Total stair height in inches

        Returns:
            Number of treads required
        """
        return math.ceil(overall_height / 7.5)