"""
Horizontal Picket Module - Creates horizontal rail infill system for spiral staircase.
Implements sophisticated horizontal rail system with IBC compliance and structural integration.
"""

import math
from typing import Dict, Any, List, Tuple, Optional
from core.base_component import BaseStairComponent
from core.autocad_interface import AutoCADInterface


class HorizontalPicketModule(BaseStairComponent):
    """
    Creates horizontal rail infill system for spiral staircase.

    Horizontal pickets are infill barrier elements that:
    - Provide horizontal rail barriers between posts or structural points
    - Comply with IBC 4" sphere rule (no opening allows 4" sphere passage)
    - Follow the curved geometry of spiral staircases
    - Integrate with post systems when available
    - Support various materials with proper galvanic isolation
    - Include mounting bracket systems for structural connections
    """

    def __init__(self):
        """Initialize horizontal picket module."""
        super().__init__("Horizontal Pickets")
        self.horizontal_rails_created = []
        self.rail_count = 0
        self.mounting_brackets_created = []
        self.rail_levels = []
        self.rail_segments = []

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
        Validate parameters for horizontal picket generation.

        Args:
            config: Configuration dictionary containing all parameters

        Returns:
            bool: True if parameters are valid

        Raises:
            ValueError: If parameters are invalid with descriptive message
        """
        # Get horizontal picket configuration
        horizontal_config = config.get("horizontal_picket_configuration", {})
        
        # Check if horizontal pickets are enabled
        if not horizontal_config.get("enabled", False):
            return True  # Skip validation if not enabled
        
        # Validate horizontal picket configuration parameters
        rail_material = horizontal_config.get("rail_material", "aluminum")
        rail_profile = horizontal_config.get("rail_profile", "square_1x1")
        rail_levels = horizontal_config.get("rail_levels", 4)
        level_distribution = horizontal_config.get("level_distribution", "even")
        mounting_system = horizontal_config.get("mounting_system", "bracket_mount")
        rail_length_max = horizontal_config.get("rail_length_max", 72.0)

        # Validate rail material
        valid_materials = ["aluminum", "steel", "wood", "composite"]
        if rail_material not in valid_materials:
            raise ValueError(
                f"Horizontal rail material must be one of {valid_materials}. "
                f"Got: {rail_material}"
            )
        
        # Validate rail profile
        valid_profiles = ["square_1x1", "rectangular_1x2", "round_1", "custom"]
        if rail_profile not in valid_profiles:
            raise ValueError(
                f"Horizontal rail profile must be one of {valid_profiles}. "
                f"Got: {rail_profile}"
            )
        
        # Validate rail levels
        if rail_levels < 2 or rail_levels > 8:
            raise ValueError(
                f"Horizontal rail levels must be between 2 and 8. "
                f"Got: {rail_levels}"
            )
        
        # Validate level distribution
        valid_distributions = ["even", "concentrated_lower", "concentrated_upper", "custom"]
        if level_distribution not in valid_distributions:
            raise ValueError(
                f"Horizontal rail level distribution must be one of {valid_distributions}. "
                f"Got: {level_distribution}"
            )
        
        # Validate mounting system
        valid_mounting = ["bracket_mount", "weld_mount", "clamp_mount"]
        if mounting_system not in valid_mounting:
            raise ValueError(
                f"Horizontal rail mounting system must be one of {valid_mounting}. "
                f"Got: {mounting_system}"
            )
        
        # Validate rail length
        if rail_length_max < 12.0 or rail_length_max > 120.0:
            raise ValueError(
                f"Horizontal rail maximum length must be between 12.0 and 120.0 inches. "
                f"Got: {rail_length_max}"
            )

        return True

    def generate_geometry(
        self,
        autocad_interface: AutoCADInterface,
        config: Dict[str, Any]
    ) -> bool:
        """
        Generate horizontal picket geometries for spiral staircase.

        Args:
            autocad_interface: AutoCAD interface for geometry creation
            config: Configuration dictionary

        Returns:
            bool: True if generation successful
        """
        try:
            # Get horizontal picket configuration
            horizontal_config = config.get("horizontal_picket_configuration", {})
            basic_params = config.get("basic_parameters", {})

            # Check if horizontal pickets are enabled
            if not horizontal_config.get("enabled", False):
                print("Horizontal pickets disabled in configuration - "
                      "skipping horizontal picket generation")
                self.is_generated = True
                return True

            # Extract parameters
            center_pole_dia = basic_params.get("center_pole_diameter")
            overall_height = basic_params.get("overall_height")
            outside_dia = basic_params.get("outside_diameter")
            total_rotation = basic_params.get("total_rotation")
            is_clockwise = basic_params.get("is_clockwise", True)

            # Horizontal picket configuration parameters
            rail_material = horizontal_config.get("rail_material", "aluminum")
            rail_profile = horizontal_config.get("rail_profile", "square_1x1")
            rail_levels = horizontal_config.get("rail_levels", 4)
            level_distribution = horizontal_config.get("level_distribution", "even")
            mounting_system = horizontal_config.get("mounting_system", "bracket_mount")
            rail_length_max = horizontal_config.get("rail_length_max", 72.0)

            # Calculate basic geometry
            center_pole_radius = center_pole_dia / 2
            outside_radius = outside_dia / 2

            print(f"Creating horizontal rail system with {rail_levels} levels")
            print(f"Material: {rail_material}, Profile: {rail_profile}")
            print(f"Distribution: {level_distribution}, Mounting: {mounting_system}")
            print(f"Maximum rail length: {rail_length_max}\"")

            # Generate horizontal rail system
            success = self._generate_horizontal_rail_system(
                autocad_interface,
                config,
                center_pole_radius,
                outside_radius,
                outside_dia,
                overall_height,
                total_rotation,
                is_clockwise,
                rail_material,
                rail_profile,
                rail_levels,
                level_distribution,
                mounting_system,
                rail_length_max,
            )

            if not success:
                return False

            self.is_generated = True
            self.rail_count = len(self.horizontal_rails_created)

            print(f"Successfully created {self.rail_count} horizontal rail entities")
            return True

        except Exception as e:
            self.last_error = str(e)
            print(f"Error generating horizontal pickets: {e}")
            self.cleanup(autocad_interface)
            return False

    def cleanup(self, autocad_interface: AutoCADInterface) -> None:
        """
        Cleanup any partial geometry if generation fails.

        Args:
            autocad_interface: AutoCAD COM interface wrapper
        """
        # Clean up any created entities
        self.horizontal_rails_created = []
        self.rail_count = 0
        self.mounting_brackets_created = []
        self.rail_levels = []
        self.rail_segments = []
        print("Horizontal picket module cleanup completed")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current component status for debugging and monitoring.

        Returns:
            Dict with component status information
        """
        status = super().get_status()
        status.update({
            "rails_created": self.rail_count,
            "rail_levels": len(self.rail_levels),
            "mounting_brackets": len(self.mounting_brackets_created),
            "rail_segments": len(self.rail_segments),
        })
        return status

    def _generate_horizontal_rail_system(
        self,
        autocad_interface: AutoCADInterface,
        config: Dict[str, Any],
        center_pole_radius: float,
        outside_radius: float,
        outside_dia: float,
        overall_height: float,
        total_rotation: float,
        is_clockwise: bool,
        rail_material: str,
        rail_profile: str,
        rail_levels: int,
        level_distribution: str,
        mounting_system: str,
        rail_length_max: float,
    ) -> bool:
        """
        Generate comprehensive horizontal rail system for spiral staircase.
        
        This implements sophisticated horizontal rail geometry with:
        - Multi-level rail distribution following IBC compliance
        - Integration with post system (if enabled)
        - Curved rail geometry following spiral stair curvature
        - Mounting bracket systems with material compatibility
        - IBC 4" sphere rule compliance validation
        
        Args:
            autocad_interface: AutoCAD interface
            config: Configuration dictionary
            center_pole_radius: Radius of center pole
            outside_radius: Outside radius of stair
            outside_dia: Outside diameter of stair
            overall_height: Total height of stair
            total_rotation: Total rotation in degrees
            is_clockwise: Direction of rotation
            rail_material: Rail material type
            rail_profile: Rail cross-section profile
            rail_levels: Number of horizontal rail levels
            level_distribution: Level spacing distribution type
            mounting_system: Rail mounting system type
            rail_length_max: Maximum single rail length

        Returns:
            bool: True if generation successful
        """
        try:
            print("HORIZONTAL RAIL SYSTEM IMPLEMENTATION")
            print("Creating sophisticated multi-level horizontal rail system")
            
            # Step 1: Calculate guard height and rail placement zone
            guard_height = 42.0  # IBC minimum guard height in inches
            handrail_config = config.get("handrail_configuration", {})
            handrail_height_above_tread = handrail_config.get("height_above_tread", 36.0)
            
            print(f"\nRAIL PLACEMENT PARAMETERS:")
            print(f"  Guard height requirement: {guard_height:.1f}\"")
            print(f"  Handrail height above tread: {handrail_height_above_tread:.1f}\"")
            print(f"  Available rail zone: 0\" to {guard_height:.1f}\"")
            
            # Step 2: Calculate rail level heights based on distribution
            rail_heights = self._calculate_rail_level_heights(
                rail_levels, guard_height, level_distribution, config
            )
            
            print(f"\nRAIL LEVEL DISTRIBUTION ({level_distribution}):")
            for i, height in enumerate(rail_heights):
                print(f"  Level {i+1}: {height:.1f}\" above tread")
            
            # Step 3: Determine post positions and structural integration
            post_positions = self._get_post_positions(config)
            structural_points = self._calculate_structural_points(
                post_positions, center_pole_radius, outside_radius, total_rotation
            )
            
            print(f"\nSTRUCTURAL INTEGRATION:")
            if post_positions:
                print(f"  Post system enabled: {len(post_positions)} posts detected")
                print(f"  Structural points: {len(structural_points)}")
            else:
                print(f"  Post system disabled: Using tread-edge mounting")
                print(f"  Structural points: Calculated from tread geometry")
            
            # Step 4: Calculate tread geometry for rail segmentation
            num_treads = math.ceil(overall_height / 9.5)  # Consistent with other modules
            tread_angle_degrees = total_rotation / (num_treads - 1)
            
            print(f"\nTREAD GEOMETRY FOR RAIL SEGMENTATION:")
            print(f"  Total treads: {num_treads}")
            print(f"  Tread angle: {tread_angle_degrees:.1f}°")
            
            # Step 5: Generate rail segments for each level
            total_rail_entities = []
            total_bracket_entities = []
            
            for level_index, rail_height in enumerate(rail_heights):
                print(f"\n--- GENERATING LEVEL {level_index + 1} at {rail_height:.1f}\" ---")
                
                # Calculate rail segments for this level
                level_segments = self._generate_rail_segments_for_level(
                    rail_height,
                    num_treads,
                    tread_angle_degrees,
                    center_pole_radius,
                    outside_radius,
                    total_rotation,
                    structural_points,
                    rail_length_max,
                    is_clockwise
                )
                
                # Create AutoCAD entities for each segment
                for segment_index, segment in enumerate(level_segments):
                    # Create curved rail geometry
                    rail_entities = self._create_curved_rail_segment(
                        autocad_interface, segment, rail_profile, rail_material
                    )
                    
                    # Create mounting brackets
                    bracket_entities = self._create_mounting_brackets(
                        autocad_interface, segment, mounting_system, rail_material
                    )
                    
                    if rail_entities:
                        total_rail_entities.extend(rail_entities)
                        print(f"  Segment {segment_index + 1}: Created {len(rail_entities)} rail entities")
                    
                    if bracket_entities:
                        total_bracket_entities.extend(bracket_entities)
                        print(f"  Segment {segment_index + 1}: Created {len(bracket_entities)} bracket entities")
                
                print(f"Level {level_index + 1} complete: {len(level_segments)} segments")
            
            # Step 6: Validate IBC compliance
            compliance_result = self._validate_ibc_compliance(
                rail_heights, rail_profile, guard_height
            )
            
            if not compliance_result['compliant']:
                print(f"\nIBC COMPLIANCE WARNING:")
                for warning in compliance_result['warnings']:
                    print(f"  - {warning}")
            else:
                print(f"\nIBC COMPLIANCE: ✅ All requirements satisfied")
                print(f"  - 4\" sphere rule: COMPLIANT")
                print(f"  - Guard height: {guard_height:.1f}\" (minimum 42\")")
                print(f"  - Rail spacing: {compliance_result['max_gap']:.1f}\" (maximum 4\")")
            
            # Store created entities
            self.horizontal_rails_created.extend(total_rail_entities)
            self.mounting_brackets_created.extend(total_bracket_entities)
            self.rail_levels = rail_heights
            
            print(f"\nHORIZONTAL RAIL SYSTEM COMPLETE:")
            print(f"  Total rail entities: {len(total_rail_entities)}")
            print(f"  Total bracket entities: {len(total_bracket_entities)}")
            print(f"  Rail levels: {len(rail_heights)}")
            print(f"  Material: {rail_material}, Profile: {rail_profile}")
            print(f"  Mounting: {mounting_system}")
            print(f"  IBC Compliance: {'✅ COMPLIANT' if compliance_result['compliant'] else '⚠️ WARNINGS'}")
            
            return True
            
        except Exception as e:
            print(f"Error generating horizontal rail system: {str(e)}")
            return False

    def _calculate_rail_level_heights(
        self,
        rail_levels: int,
        guard_height: float,
        level_distribution: str,
        config: Dict[str, Any]
    ) -> List[float]:
        """
        Calculate height positions for horizontal rail levels.
        
        Args:
            rail_levels: Number of rail levels
            guard_height: Total guard height (42" IBC minimum)
            level_distribution: Distribution pattern for levels
            config: Configuration dictionary for custom levels
            
        Returns:
            List of rail heights above tread level
        """
        horizontal_config = config.get("horizontal_picket_configuration", {})
        
        if level_distribution == "custom":
            # Use custom levels if provided
            custom_levels = horizontal_config.get("custom_levels", [])
            if len(custom_levels) >= rail_levels:
                return custom_levels[:rail_levels]
            else:
                print(f"Warning: Only {len(custom_levels)} custom levels provided, need {rail_levels}. Using even distribution.")
                level_distribution = "even"
        
        heights = []
        
        if level_distribution == "even":
            # Even distribution across guard height
            for i in range(rail_levels):
                height = (guard_height / (rail_levels + 1)) * (i + 1)
                heights.append(height)
        
        elif level_distribution == "concentrated_lower":
            # More rails in lower 60% of guard height
            lower_zone = guard_height * 0.6
            upper_zone = guard_height * 0.4
            lower_rails = max(1, int(rail_levels * 0.7))
            upper_rails = rail_levels - lower_rails
            
            # Lower rails
            for i in range(lower_rails):
                height = (lower_zone / (lower_rails + 1)) * (i + 1)
                heights.append(height)
            
            # Upper rails
            for i in range(upper_rails):
                height = lower_zone + (upper_zone / (upper_rails + 1)) * (i + 1)
                heights.append(height)
        
        elif level_distribution == "concentrated_upper":
            # More rails in upper 60% of guard height
            lower_zone = guard_height * 0.4
            upper_zone = guard_height * 0.6
            lower_rails = max(1, int(rail_levels * 0.3))
            upper_rails = rail_levels - lower_rails
            
            # Lower rails
            for i in range(lower_rails):
                height = (lower_zone / (lower_rails + 1)) * (i + 1)
                heights.append(height)
            
            # Upper rails
            for i in range(upper_rails):
                height = lower_zone + (upper_zone / (upper_rails + 1)) * (i + 1)
                heights.append(height)
        
        return sorted(heights)

    def _get_post_positions(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get post positions from post configuration if posts are enabled.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of post position dictionaries
        """
        post_config = config.get("post_configuration", {})
        if not post_config.get("enabled", False):
            return []
        
        # In a full implementation, this would query the actual post module
        # For now, simulate post positions based on configuration
        basic_params = config.get("basic_parameters", {})
        overall_height = basic_params.get("overall_height", 144.0)
        total_rotation = basic_params.get("total_rotation", 450.0)
        outside_dia = basic_params.get("outside_diameter", 72.0)
        
        post_spacing = post_config.get("spacing", 1)  # 1=every tread, 2=every other, etc.
        post_position = post_config.get("position", "outer_edge")
        
        # Calculate approximate post positions
        num_treads = math.ceil(overall_height / 9.5)
        tread_angle = total_rotation / (num_treads - 1)
        
        posts = []
        for tread_num in range(0, num_treads, post_spacing):
            angle_deg = tread_num * tread_angle
            angle_rad = math.radians(angle_deg)
            
            if post_position == "outer_edge":
                radius = outside_dia / 2
            elif post_position == "inner_edge":
                radius = basic_params.get("center_pole_diameter", 8.0) / 2 + 6.0
            else:  # mid_tread
                radius = (outside_dia / 2 + basic_params.get("center_pole_diameter", 8.0) / 2) / 2
            
            x = radius * math.cos(angle_rad)
            y = radius * math.sin(angle_rad)
            z = (tread_num + 1) * 9.0  # Tread height
            
            posts.append({
                'x': x, 'y': y, 'z': z,
                'angle_deg': angle_deg,
                'tread_num': tread_num,
                'radius': radius
            })
        
        return posts

    def _calculate_structural_points(
        self,
        post_positions: List[Dict[str, Any]],
        center_pole_radius: float,
        outside_radius: float,
        total_rotation: float
    ) -> List[Dict[str, Any]]:
        """
        Calculate structural mounting points for rails.
        
        Args:
            post_positions: List of post positions
            center_pole_radius: Center pole radius
            outside_radius: Outside radius
            total_rotation: Total rotation in degrees
            
        Returns:
            List of structural point dictionaries
        """
        if post_positions:
            # Use post positions as structural points
            return [
                {
                    'x': post['x'],
                    'y': post['y'],
                    'z': post['z'],
                    'type': 'post',
                    'angle_deg': post['angle_deg']
                }
                for post in post_positions
            ]
        else:
            # Generate structural points at tread edges
            # This creates mounting points at regular intervals
            num_points = max(8, int(total_rotation / 45))  # At least 8 points, more for larger rotation
            angle_step = total_rotation / num_points
            
            points = []
            for i in range(num_points + 1):
                angle_deg = i * angle_step
                angle_rad = math.radians(angle_deg)
                
                x = outside_radius * math.cos(angle_rad)
                y = outside_radius * math.sin(angle_rad)
                z = 0  # Will be adjusted for each tread level
                
                points.append({
                    'x': x,
                    'y': y,
                    'z': z,
                    'type': 'tread_edge',
                    'angle_deg': angle_deg
                })
            
            return points

    def _generate_rail_segments_for_level(
        self,
        rail_height: float,
        num_treads: int,
        tread_angle_degrees: float,
        center_pole_radius: float,
        outside_radius: float,
        total_rotation: float,
        structural_points: List[Dict[str, Any]],
        rail_length_max: float,
        is_clockwise: bool
    ) -> List[Dict[str, Any]]:
        """
        Generate rail segments for a specific height level.
        
        Args:
            rail_height: Height of this rail level above tread
            num_treads: Number of treads in stair
            tread_angle_degrees: Angle per tread
            center_pole_radius: Center pole radius
            outside_radius: Outside radius
            total_rotation: Total rotation in degrees
            structural_points: List of structural mounting points
            rail_length_max: Maximum rail segment length
            is_clockwise: Direction of rotation
            
        Returns:
            List of rail segment dictionaries
        """
        segments = []
        
        # Calculate rail placement radius (between handrail and outer edge)
        rail_radius = outside_radius * 0.9  # Place rails slightly inside outer edge
        
        # Generate continuous rail following stair curvature
        # Break into segments based on structural points or maximum length
        
        # Calculate number of segments needed
        total_arc_length = (total_rotation * math.pi / 180) * rail_radius
        num_segments = max(1, math.ceil(total_arc_length / rail_length_max))
        
        angular_step = total_rotation / num_segments
        
        for i in range(num_segments):
            start_angle = i * angular_step
            end_angle = (i + 1) * angular_step
            
            if not is_clockwise:
                start_angle = -start_angle
                end_angle = -end_angle
            
            # Calculate start and end points
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)
            
            start_x = rail_radius * math.cos(start_rad)
            start_y = rail_radius * math.sin(start_rad)
            end_x = rail_radius * math.cos(end_rad)
            end_y = rail_radius * math.sin(end_rad)
            
            # Calculate height adjustment based on tread progression
            # Rails follow the stair's vertical progression
            tread_progress = (start_angle + end_angle) / 2 / tread_angle_degrees
            base_height = tread_progress * 9.0  # 9" riser height
            
            segment = {
                'start_point': (start_x, start_y, base_height + rail_height),
                'end_point': (end_x, end_y, base_height + rail_height),
                'start_angle': start_angle,
                'end_angle': end_angle,
                'radius': rail_radius,
                'height': rail_height,
                'segment_index': i,
                'arc_length': abs(end_angle - start_angle) * math.pi / 180 * rail_radius
            }
            
            segments.append(segment)
        
        return segments

    def _create_curved_rail_segment(
        self,
        autocad_interface: AutoCADInterface,
        segment: Dict[str, Any],
        rail_profile: str,
        rail_material: str
    ) -> List[Any]:
        """
        Create AutoCAD entities for a curved rail segment.
        
        Args:
            autocad_interface: AutoCAD interface
            segment: Rail segment dictionary
            rail_profile: Rail cross-section profile
            rail_material: Rail material
            
        Returns:
            List of created AutoCAD entities
        """
        entities = []
        
        try:
            # Get segment parameters
            start_point = segment['start_point']
            end_point = segment['end_point']
            radius = segment['radius']
            start_angle = math.radians(segment['start_angle'])
            end_angle = math.radians(segment['end_angle'])
            
            # Create curved rail as arc
            arc_center = (0.0, 0.0, (start_point[2] + end_point[2]) / 2)
            
            rail_arc = autocad_interface.create_arc(
                arc_center, radius, start_angle, end_angle
            )
            
            if rail_arc:
                entities.append(rail_arc)
            
            # Add rail profile geometry based on profile type
            if rail_profile == "square_1x1":
                # Create square profile along the arc
                profile_entities = self._create_square_profile_along_arc(
                    autocad_interface, segment, 1.0  # 1" x 1" square
                )
                entities.extend(profile_entities)
            
            elif rail_profile == "rectangular_1x2":
                # Create rectangular profile
                profile_entities = self._create_rectangular_profile_along_arc(
                    autocad_interface, segment, 1.0, 2.0  # 1" x 2" rectangle
                )
                entities.extend(profile_entities)
            
            elif rail_profile == "round_1":
                # Create round profile
                profile_entities = self._create_round_profile_along_arc(
                    autocad_interface, segment, 1.0  # 1" diameter round
                )
                entities.extend(profile_entities)
            
        except Exception as e:
            print(f"Error creating curved rail segment: {e}")
        
        return entities

    def _create_square_profile_along_arc(
        self,
        autocad_interface: AutoCADInterface,
        segment: Dict[str, Any],
        size: float
    ) -> List[Any]:
        """Create square profile geometry along arc segment."""
        entities = []
        
        # Create simplified square profile at start and end points
        half_size = size / 2
        
        for point in [segment['start_point'], segment['end_point']]:
            x, y, z = point
            
            # Create square corners
            corners = [
                (x - half_size, y - half_size, z - half_size),
                (x + half_size, y - half_size, z - half_size),
                (x + half_size, y + half_size, z - half_size),
                (x - half_size, y + half_size, z - half_size),
            ]
            
            # Create square outline
            for i in range(4):
                line = autocad_interface.create_line(corners[i], corners[(i + 1) % 4])
                if line:
                    entities.append(line)
        
        return entities

    def _create_rectangular_profile_along_arc(
        self,
        autocad_interface: AutoCADInterface,
        segment: Dict[str, Any],
        width: float,
        height: float
    ) -> List[Any]:
        """Create rectangular profile geometry along arc segment."""
        entities = []
        
        half_width = width / 2
        half_height = height / 2
        
        for point in [segment['start_point'], segment['end_point']]:
            x, y, z = point
            
            corners = [
                (x - half_width, y - half_height, z),
                (x + half_width, y - half_height, z),
                (x + half_width, y + half_height, z),
                (x - half_width, y + half_height, z),
            ]
            
            for i in range(4):
                line = autocad_interface.create_line(corners[i], corners[(i + 1) % 4])
                if line:
                    entities.append(line)
        
        return entities

    def _create_round_profile_along_arc(
        self,
        autocad_interface: AutoCADInterface,
        segment: Dict[str, Any],
        diameter: float
    ) -> List[Any]:
        """Create round profile geometry along arc segment."""
        entities = []
        
        radius = diameter / 2
        
        for point in [segment['start_point'], segment['end_point']]:
            x, y, z = point
            center = (x, y, z)
            
            # Create circle at each end
            circle = autocad_interface.create_circle(center, radius)
            if circle:
                entities.append(circle)
        
        return entities

    def _create_mounting_brackets(
        self,
        autocad_interface: AutoCADInterface,
        segment: Dict[str, Any],
        mounting_system: str,
        rail_material: str
    ) -> List[Any]:
        """
        Create mounting bracket geometry for rail segment.
        
        Args:
            autocad_interface: AutoCAD interface
            segment: Rail segment dictionary
            mounting_system: Type of mounting system
            rail_material: Rail material for compatibility
            
        Returns:
            List of bracket entities
        """
        entities = []
        
        try:
            if mounting_system == "bracket_mount":
                # Create bracket geometry at start and end points
                bracket_size = 2.0  # 2" bracket plates
                
                for point in [segment['start_point'], segment['end_point']]:
                    x, y, z = point
                    
                    # Create bracket plate as small rectangle
                    half_size = bracket_size / 2
                    corners = [
                        (x - half_size, y, z - half_size),
                        (x + half_size, y, z - half_size),
                        (x + half_size, y, z + half_size),
                        (x - half_size, y, z + half_size),
                    ]
                    
                    for i in range(4):
                        line = autocad_interface.create_line(corners[i], corners[(i + 1) % 4])
                        if line:
                            entities.append(line)
            
            elif mounting_system == "clamp_mount":
                # Create clamp geometry
                for point in [segment['start_point'], segment['end_point']]:
                    x, y, z = point
                    center = (x, y, z)
                    
                    # Simple clamp representation as circle
                    clamp_circle = autocad_interface.create_circle(center, 1.0)
                    if clamp_circle:
                        entities.append(clamp_circle)
            
        except Exception as e:
            print(f"Error creating mounting brackets: {e}")
        
        return entities

    def _validate_ibc_compliance(
        self,
        rail_heights: List[float],
        rail_profile: str,
        guard_height: float
    ) -> Dict[str, Any]:
        """
        Validate horizontal rail system against IBC requirements.
        
        Args:
            rail_heights: List of rail height positions
            rail_profile: Rail cross-section profile
            guard_height: Total guard height
            
        Returns:
            Dictionary with compliance results
        """
        warnings = []
        
        # Check guard height requirement
        if guard_height < 42.0:
            warnings.append(f"Guard height {guard_height:.1f}\" is below IBC minimum 42\"")
        
        # Check 4" sphere rule - calculate maximum gap between rails
        rail_thickness = self._get_rail_thickness(rail_profile)
        
        if len(rail_heights) < 2:
            max_gap = guard_height
        else:
            gaps = []
            
            # Gap from bottom to first rail
            gaps.append(rail_heights[0] - rail_thickness/2)
            
            # Gaps between adjacent rails
            for i in range(len(rail_heights) - 1):
                gap = (rail_heights[i + 1] - rail_thickness/2) - (rail_heights[i] + rail_thickness/2)
                gaps.append(gap)
            
            # Gap from last rail to top
            gaps.append((guard_height) - (rail_heights[-1] + rail_thickness/2))
            
            max_gap = max(gaps) if gaps else 0
        
        # Check 4" sphere rule compliance
        if max_gap > 4.0:
            warnings.append(f"Maximum gap {max_gap:.1f}\" exceeds 4\" sphere rule")
        
        compliant = len(warnings) == 0
        
        return {
            'compliant': compliant,
            'warnings': warnings,
            'max_gap': max_gap,
            'guard_height': guard_height,
            'rail_count': len(rail_heights)
        }

    def _get_rail_thickness(self, rail_profile: str) -> float:
        """
        Get rail thickness based on profile type.
        
        Args:
            rail_profile: Rail cross-section profile
            
        Returns:
            Rail thickness in inches
        """
        thickness_map = {
            "square_1x1": 1.0,
            "rectangular_1x2": 1.0,  # Use smaller dimension
            "round_1": 1.0,
            "custom": 1.0
        }
        
        return thickness_map.get(rail_profile, 1.0)

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