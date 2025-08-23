"""
Entity manipulation utilities module for AutoCAD interface.
Handles entity creation, modification, and utility operations.
"""

from typing import Optional, Any, List, Dict
import math

from .logging_config import get_logger
from .exceptions import AutoCADConnectionError, GenerationError
from .autocad_connection import AutoCADConnectionManager


class AutoCADEntityManipulator:
    """
    Handles manipulation of AutoCAD entities including creation, modification, and utility operations.
    """

    def __init__(self, connection_manager: AutoCADConnectionManager):
        """
        Initialize entity manipulator.

        Args:
            connection_manager: AutoCAD connection manager instance
        """
        self.logger = get_logger(__name__ + '.EntityManipulator')
        self.connection_manager = connection_manager

    def create_region(self, objects: list) -> Any:
        """Create a region from a list of objects."""
        if not self.connection_manager.is_connected():
            raise AutoCADConnectionError("Not connected to AutoCAD")
        try:
            # Convert objects list to VARIANT array for COM interface
            import win32com.client
            import pythoncom
            objects_variant = win32com.client.VARIANT(
                pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH,
                objects
            )
            model_space = self.connection_manager.get_model_space()
            region = model_space.AddRegion(objects_variant)
            self.logger.debug("AutoCAD region created successfully")
            return region
        except Exception as e:
            raise GenerationError(f"Failed to create region: {e}")

    def create_extruded_solid(self, profile: Any, height: float, taper_angle: float = 0) -> Any:
        """Create an extruded solid from a profile."""
        if not self.connection_manager.is_connected():
            raise AutoCADConnectionError("Not connected to AutoCAD")
        try:
            model_space = self.connection_manager.get_model_space()
            solid = model_space.AddExtrudedSolid(profile, height, taper_angle)
            self.logger.debug("AutoCAD extruded solid created successfully")
            return solid
        except Exception as e:
            raise GenerationError(f"Failed to create extruded solid: {e}")

    def create_spline(self, points: List[tuple]) -> Any:
        """
        Create spline in AutoCAD using proper parameter marshalling.

        Args:
            points: List of (x, y, z) control points

        Returns:
            AutoCAD spline entity

        Raises:
            AutoCADConnectionError: If not connected
            GenerationError: If creation fails
        """
        if not self.connection_manager.is_connected():
            error_msg = "Not connected to AutoCAD"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        try:
            self.logger.debug(f"Creating AutoCAD spline with {len(points)} points")

            # Validate input
            if len(points) < 2:
                raise GenerationError(
                    f"Spline requires at least 2 points, got {len(points)}",
                    geometry_type="spline",
                    operation="create"
                )

            # Get model space
            model_space = self.connection_manager.get_model_space()
            if not model_space:
                raise AutoCADConnectionError("Model space not available", is_mock_mode=False)

            # Try different approaches for spline creation
            # Approach 1: Individual VARIANT arrays for each point
            try:
                import win32com.client
                import pythoncom

                point_variants = []
                for point in points:
                    point_variant = self._convert_to_variant_array(point)
                    point_variants.append(point_variant)

                # Create spline with point array
                spline = model_space.AddSpline(point_variants, None, None)

            except Exception as variant_error:
                self.logger.debug(f"VARIANT array approach failed: {variant_error}")

                # Approach 2: Fallback to polyline
                try:
                    self.logger.debug("Falling back to polyline for spline creation")

                    # Convert all points to flattened array for polyline
                    flattened_coords = []
                    for point in points:
                        flattened_coords.extend([
                            float(point[0]),
                            float(point[1]),
                            float(point[2]) if len(point) > 2 else 0.0
                        ])

                    # Create polyline as spline substitute
                    points_variant = win32com.client.VARIANT(
                        pythoncom.VT_ARRAY | pythoncom.VT_R8,
                        flattened_coords
                    )

                    spline = model_space.AddPolyline(points_variant)

                except Exception as polyline_error:
                    raise Exception(f"Both spline and polyline creation failed: {variant_error}, {polyline_error}")

            self.logger.debug(f"AutoCAD spline created successfully")
            return spline

        except (AutoCADConnectionError, GenerationError):
            raise
        except Exception as e:
            error_msg = f"Failed to create spline in AutoCAD: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GenerationError(
                error_msg,
                geometry_type="spline",
                operation="create",
                details={"points": points}
            )

    def create_sphere(self, center: tuple, radius: float) -> Any:
        """
        Create sphere in AutoCAD using proper parameter marshalling.

        Args:
            center: (x, y, z) center point
            radius: Sphere radius

        Returns:
            AutoCAD sphere entity

        Raises:
            AutoCADConnectionError: If not connected
            GenerationError: If creation fails
        """
        if not self.connection_manager.is_connected():
            error_msg = "Not connected to AutoCAD"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        try:
            self.logger.debug(f"Creating AutoCAD sphere: center={center}, radius={radius}")

            # Validate inputs
            if radius <= 0:
                raise GenerationError(
                    f"Invalid sphere radius: {radius}",
                    geometry_type="sphere",
                    operation="create"
                )

            # Get model space
            model_space = self.connection_manager.get_model_space()
            if not model_space:
                raise AutoCADConnectionError("Model space not available", is_mock_mode=False)

            # Convert center to VARIANT array
            center_variant = self._convert_to_variant_array(center)

            # Try to create sphere using AddSphere if available
            if hasattr(model_space, 'AddSphere'):
                sphere = model_space.AddSphere(center_variant, radius)
                self.logger.debug(f"AutoCAD sphere created successfully")
                return sphere
            else:
                # Fallback to circle if sphere not available
                self.logger.warning("AddSphere not available, falling back to circle")
                circle = model_space.AddCircle(center_variant, radius)
                return circle

        except (AutoCADConnectionError, GenerationError):
            raise
        except Exception as e:
            error_msg = f"Failed to create sphere in AutoCAD: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GenerationError(
                error_msg,
                geometry_type="sphere",
                operation="create",
                details={"center": center, "radius": radius}
            )

    def create_box(self, center: tuple, length: float, width: float, height: float) -> Any:
        """
        Create box in AutoCAD using proper parameter marshalling.

        Args:
            center: (x, y, z) center point
            length: Box length
            width: Box width
            height: Box height

        Returns:
            AutoCAD box entity

        Raises:
            AutoCADConnectionError: If not connected
            GenerationError: If creation fails
        """
        if not self.connection_manager.is_connected():
            error_msg = "Not connected to AutoCAD"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        try:
            self.logger.debug(f"Creating AutoCAD box: center={center}, dimensions={length}x{width}x{height}")

            # Validate inputs
            if length <= 0 or width <= 0 or height <= 0:
                raise GenerationError(
                    f"Invalid box dimensions: {length}x{width}x{height}",
                    geometry_type="box",
                    operation="create"
                )

            # Get model space
            model_space = self.connection_manager.get_model_space()
            if not model_space:
                raise AutoCADConnectionError("Model space not available", is_mock_mode=False)

            # Convert center to VARIANT array
            center_variant = self._convert_to_variant_array(center)

            # Try to create box using Add3DBox if available
            if hasattr(model_space, 'Add3DBox'):
                # Calculate corner points for 3D box
                half_length = length / 2
                half_width = width / 2
                half_height = height / 2

                # Create corner coordinates
                x, y, z = center[0], center[1], center[2] if len(center) > 2 else 0.0
                corner1 = (x - half_length, y - half_width, z - half_height)
                corner2 = (x + half_length, y + half_width, z + half_height)

                import win32com.client
                import pythoncom
                corner1_variant = self._convert_to_variant_array(corner1)
                corner2_variant = self._convert_to_variant_array(corner2)

                box = model_space.Add3DBox(corner1_variant, corner2_variant)
                self.logger.debug(f"AutoCAD 3D box created successfully")
                return box
            else:
                # Fallback to rectangle if 3D box not available
                self.logger.warning("Add3DBox not available, falling back to rectangle")

                # Create rectangle from center
                x, y = center[0], center[1]
                half_length = length / 2
                half_width = width / 2

                corner1 = (x - half_length, y - half_width, 0.0)
                corner2 = (x + half_length, y + half_width, 0.0)

                corner1_variant = self._convert_to_variant_array(corner1)
                corner2_variant = self._convert_to_variant_array(corner2)

                # Create rectangle using polyline
                rect_points = [
                    x - half_length, y - half_width, 0.0,
                    x + half_length, y - half_width, 0.0,
                    x + half_length, y + half_width, 0.0,
                    x - half_length, y + half_width, 0.0
                ]

                points_variant = win32com.client.VARIANT(
                    pythoncom.VT_ARRAY | pythoncom.VT_R8,
                    rect_points
                )

                polyline = model_space.AddPolyline(points_variant)
                polyline.Closed = True
                return polyline

        except (AutoCADConnectionError, GenerationError):
            raise
        except Exception as e:
            error_msg = f"Failed to create box in AutoCAD: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GenerationError(
                error_msg,
                geometry_type="box",
                operation="create",
                details={
                    "center": center, "length": length,
                    "width": width, "height": height
                }
            )

    def add_text(self, text: str, position: tuple, height: float = 0.125) -> Any:
        """Add text annotation to the drawing."""
        try:
            self.logger.debug(f"Creating AutoCAD text: '{text}' at {position}, height={height}")

            # Convert position to AutoCAD variant array
            import win32com.client
            import pythoncom
            text_point = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, position)

            # Get model space
            model_space = self.connection_manager.get_model_space()
            if not model_space:
                raise AutoCADConnectionError("Model space not available", is_mock_mode=False)

            # Create text entity
            text_entity = model_space.AddText(text, text_point, height)

            self.logger.debug(f"Created AutoCAD text entity at {position}")
            return text_entity

        except Exception as e:
            error_msg = f"Failed to create AutoCAD text '{text}': {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GenerationError(
                error_msg,
                geometry_type="text",
                operation="create",
                details={"text": text, "position": position, "height": height}
            )

    def add_dimension(self, point1: tuple, point2: tuple, dimension_line_point: tuple, text: str = None) -> Any:
        """Add linear dimension between two points."""
        try:
            self.logger.debug(f"Creating AutoCAD dimension: {point1} to {point2}")

            # Calculate distance
            distance = math.sqrt(sum((p2 - p1)**2 for p1, p2 in zip(point1, point2)))
            dim_text = text or f"{distance:.2f}\""

            # Convert points to AutoCAD variant arrays
            import win32com.client
            import pythoncom
            pt1 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, point1)
            pt2 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, point2)
            dim_line_pt = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, dimension_line_point)

            # Get model space
            model_space = self.connection_manager.get_model_space()
            if not model_space:
                raise AutoCADConnectionError("Model space not available", is_mock_mode=False)

            # Create aligned dimension
            dim_entity = model_space.AddDimAligned(pt1, pt2, dim_line_pt)

            # Set custom text if provided
            if text:
                dim_entity.TextOverride = text

            self.logger.debug(f"Created AutoCAD dimension between {point1} and {point2}")
            return dim_entity

        except Exception as e:
            error_msg = f"Failed to create AutoCAD dimension: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GenerationError(
                error_msg,
                geometry_type="dimension",
                operation="create",
                details={"point1": point1, "point2": point2, "dimension_line_point": dimension_line_point}
            )

    def _convert_to_variant_array(self, coordinates: tuple) -> Any:
        """
        Convert Python coordinates to win32com VARIANT array format.

        Args:
            coordinates: Tuple of (x, y, z) coordinates

        Returns:
            win32com.client.VARIANT array compatible with AutoCAD

        Raises:
            GenerationError: If conversion fails
        """
        try:
            # Ensure we have 3D coordinates
            coords = [
                float(coordinates[0]),
                float(coordinates[1]),
                float(coordinates[2]) if len(coordinates) > 2 else 0.0
            ]

            # Create VARIANT array using the working format from diagnostics
            import win32com.client
            import pythoncom
            variant_array = win32com.client.VARIANT(
                pythoncom.VT_ARRAY | pythoncom.VT_R8,
                coords
            )

            self.logger.debug(f"Converted coordinates {coordinates} to VARIANT array")
            return variant_array

        except Exception as e:
            self.logger.error(f"Failed to convert coordinates to VARIANT: {e}")
            raise GenerationError(
                f"Coordinate conversion failed: {e}",
                geometry_type="coordinate_conversion",
                operation="convert"
            )