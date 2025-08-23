"""
Geometry creation module for AutoCAD interface.
Handles creation of geometric entities like circles, lines, arcs, etc.
"""

import time
from typing import Optional, Any, List, Tuple

from .logging_config import get_logger
from .exceptions import AutoCADConnectionError, GeometryError
from .autocad_connection import AutoCADConnectionManager


class AutoCADGeometryCreator:
    """
    Handles creation of geometric entities in AutoCAD.
    """

    def __init__(self, connection_manager: AutoCADConnectionManager):
        """
        Initialize geometry creator.

        Args:
            connection_manager: AutoCAD connection manager instance
        """
        self.logger = get_logger(__name__ + '.GeometryCreator')
        self.connection_manager = connection_manager

    def create_circle(self, center: tuple, radius: float) -> Any:
        """
        Create circle in AutoCAD using proper parameter marshalling.

        Args:
            center: (x, y, z) center point
            radius: Circle radius

        Returns:
            AutoCAD circle entity

        Raises:
            AutoCADConnectionError: If not connected
            GeometryError: If creation fails
        """
        if not self.connection_manager.is_connected():
            error_msg = "Not connected to AutoCAD"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        try:
            self.logger.debug(f"Creating AutoCAD circle: center={center}, radius={radius}")

            # Set UCS to World for consistent positioning
            self.connection_manager.set_ucs_to_world()

            # Get model space
            model_space = self.connection_manager.get_model_space()
            if not model_space:
                raise AutoCADConnectionError("Model space not available", is_mock_mode=False)

            # Convert center to VARIANT array (the only format that works)
            center_variant = self._convert_to_variant_array(center)
            circle = model_space.AddCircle(center_variant, radius)

            self.logger.debug(f"AutoCAD circle created successfully")
            return circle

        except (AutoCADConnectionError, GeometryError):
            raise
        except Exception as e:
            error_msg = f"Failed to create circle in AutoCAD: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GeometryError(
                error_msg,
                geometry_type="circle",
                operation="create",
                details={"center": center, "radius": radius}
            )

    def create_line(self, start_point: tuple, end_point: tuple) -> Any:
        """
        Create line in AutoCAD using proper parameter marshalling.

        Args:
            start_point: (x, y, z) start point
            end_point: (x, y, z) end point

        Returns:
            AutoCAD line entity

        Raises:
            AutoCADConnectionError: If not connected
            GeometryError: If creation fails
        """
        if not self.connection_manager.is_connected():
            error_msg = "Not connected to AutoCAD"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        try:
            self.logger.debug(f"Creating AutoCAD line: start={start_point}, end={end_point}")

            # Get model space
            model_space = self.connection_manager.get_model_space()
            if not model_space:
                raise AutoCADConnectionError("Model space not available", is_mock_mode=False)

            # Convert points to VARIANT arrays (the only format that works)
            start_variant = self._convert_to_variant_array(start_point)
            end_variant = self._convert_to_variant_array(end_point)
            line = model_space.AddLine(start_variant, end_variant)

            self.logger.debug(f"AutoCAD line created successfully")
            return line

        except (AutoCADConnectionError, GeometryError):
            raise
        except Exception as e:
            error_msg = f"Failed to create line in AutoCAD: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GeometryError(
                error_msg,
                geometry_type="line",
                operation="create",
                details={"start_point": start_point, "end_point": end_point}
            )

    def create_arc(self, center: tuple, radius: float, start_angle: float, end_angle: float) -> Any:
        """
        Create arc in AutoCAD using proper parameter marshalling.

        Args:
            center: (x, y, z) center point
            radius: Arc radius
            start_angle: Start angle in radians
            end_angle: End angle in radians

        Returns:
            AutoCAD arc entity

        Raises:
            AutoCADConnectionError: If not connected
            GeometryError: If creation fails
        """
        if not self.connection_manager.is_connected():
            error_msg = "Not connected to AutoCAD"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        try:
            self.logger.debug(f"Creating AutoCAD arc: center={center}, radius={radius}, angles={start_angle}-{end_angle}")

            # Set UCS to World for consistent positioning
            self.connection_manager.set_ucs_to_world()

            # Get model space
            model_space = self.connection_manager.get_model_space()
            if not model_space:
                raise AutoCADConnectionError("Model space not available", is_mock_mode=False)

            # Convert center to VARIANT array (the only format that works)
            center_variant = self._convert_to_variant_array(center)
            arc = model_space.AddArc(center_variant, radius, start_angle, end_angle)

            self.logger.debug(f"AutoCAD arc created successfully")
            return arc

        except (AutoCADConnectionError, GeometryError):
            raise
        except Exception as e:
            error_msg = f"Failed to create arc in AutoCAD: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GeometryError(
                error_msg,
                geometry_type="arc",
                operation="create",
                details={
                    "center": center,
                    "radius": radius,
                    "start_angle": start_angle,
                    "end_angle": end_angle
                }
            )

    def create_cylinder(self, center: tuple, radius: float, height: float) -> Any:
        """
        Create cylinder in AutoCAD.

        Args:
            center: (x, y, z) center point
            radius: Cylinder radius
            height: Cylinder height

        Returns:
            AutoCAD cylinder entity or circle fallback

        Raises:
            AutoCADConnectionError: If not connected
            GeometryError: If creation fails
        """
        if not self.connection_manager.is_connected():
            error_msg = "Not connected to AutoCAD"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        try:
            self.logger.debug(f"Creating AutoCAD cylinder: center={center}, radius={radius}, height={height}")

            # Validate inputs
            if radius <= 0:
                raise GeometryError(
                    f"Invalid cylinder radius: {radius}",
                    calculation="cylinder_validation",
                    input_values={"center": center, "radius": radius, "height": height}
                )

            if height <= 0:
                raise GeometryError(
                    f"Invalid cylinder height: {height}",
                    calculation="cylinder_validation",
                    input_values={"center": center, "radius": radius, "height": height}
                )

            # Validate center point
            if not isinstance(center, (list, tuple)) or len(center) < 2:
                raise GeometryError(
                    f"Invalid center point: {center}",
                    calculation="cylinder_validation",
                    input_values={"center": center, "radius": radius, "height": height}
                )

            # Ensure we have valid numeric values
            try:
                x = float(center[0])
                y = float(center[1])
                z = float(center[2]) if len(center) > 2 else 0.0

                # Additional validation for AutoCAD compatibility
                if not (-1e9 <= x <= 1e9) or not (-1e9 <= y <= 1e9) or not (-1e9 <= z <= 1e9):
                    raise GeometryError(
                        f"Center coordinates out of valid range: {center}",
                        calculation="cylinder_validation",
                        input_values={"center": center, "radius": radius, "height": height}
                    )

                if not (0 < radius <= 1e6):
                    raise GeometryError(
                        f"Radius out of valid range: {radius}",
                        calculation="cylinder_validation",
                        input_values={"center": center, "radius": radius, "height": height}
                    )

                if not (0 < height <= 1e6):
                    raise GeometryError(
                        f"Height out of valid range: {height}",
                        calculation="cylinder_validation",
                        input_values={"center": center, "radius": radius, "height": height}
                    )

            except (ValueError, TypeError) as e:
                raise GeometryError(
                    f"Invalid center point coordinates: {center}",
                    calculation="cylinder_validation",
                    input_values={"center": center, "radius": radius, "height": height}
                )

            self.logger.debug(f"Validated coordinates: x={x}, y={y}, z={z}")

            # Get model space
            model_space = self.connection_manager.get_model_space()
            if not model_space:
                raise AutoCADConnectionError("Model space not available", is_mock_mode=False)

            # Convert center to VARIANT array (the only format that works)
            center_variant = self._convert_to_variant_array((x, y, z))

            # Try to create a true cylinder using AddCylinder if available
            if hasattr(model_space, 'AddCylinder'):
                try:
                    self.logger.debug(f"Attempting to create cylinder with AddCylinder")
                    self.logger.debug(f"Parameters: center=VARIANT, radius={radius}, height={height}")
                    cylinder = model_space.AddCylinder(center_variant, radius, height)
                    self.logger.debug(f"AutoCAD cylinder created successfully")
                    return cylinder
                except Exception as cylinder_error:
                    self.logger.warning(f"AddCylinder failed, falling back to circle: {str(cylinder_error)}")

            # Fallback to creating a circle (this maintains backward compatibility)
            self.logger.debug(f"Attempting to create circle with AddCircle")
            self.logger.debug(f"Parameters: center=VARIANT, radius={radius}")
            circle = model_space.AddCircle(center_variant, radius)
            self.logger.debug(f"AutoCAD circle (cylinder fallback) created successfully")
            return circle

        except (GeometryError, AutoCADConnectionError):
            raise
        except Exception as e:
            error_msg = f"Failed to create cylinder/circle in AutoCAD: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GeometryError(
                error_msg,
                geometry_type="cylinder",
                operation="create",
                details={"center": center, "radius": radius, "height": height}
            )

    def create_helix(self, center: tuple, base_radius: float, top_radius: float,
                    height: float, turns: float, axis_vector: tuple = (0, 0, 1)) -> Any:
        """
        Create helix in AutoCAD using proper parameter marshalling.

        Args:
            center: (x, y, z) center point at base
            base_radius: Radius at base of helix
            top_radius: Radius at top of helix (same as base for constant radius)
            height: Total height of helix
            turns: Number of turns (can be fractional, e.g., 1.25 for 450°)
            axis_vector: (x, y, z) direction vector for helix axis

        Returns:
            AutoCAD helix entity

        Raises:
            AutoCADConnectionError: If not connected
            GeometryError: If creation fails
        """
        if not self.connection_manager.is_connected():
            error_msg = "Not connected to AutoCAD"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        try:
            self.logger.debug(f"Creating AutoCAD helix: center={center}, base_radius={base_radius}, top_radius={top_radius}, height={height}, turns={turns}")

            # Validate inputs
            if base_radius <= 0 or top_radius <= 0:
                raise GeometryError(
                    f"Invalid helix radius: base={base_radius}, top={top_radius}",
                    calculation="helix_validation",
                    input_values={
                        "center": center, "base_radius": base_radius,
                        "top_radius": top_radius, "height": height, "turns": turns
                    }
                )

            if height <= 0:
                raise GeometryError(
                    f"Invalid helix height: {height}",
                    calculation="helix_validation",
                    input_values={
                        "center": center, "base_radius": base_radius,
                        "top_radius": top_radius, "height": height, "turns": turns
                    }
                )

            if turns <= 0:
                raise GeometryError(
                    f"Invalid helix turns: {turns}",
                    calculation="helix_validation",
                    input_values={
                        "center": center, "base_radius": base_radius,
                        "top_radius": top_radius, "height": height, "turns": turns
                    }
                )

            # Get application and document
            acad_app = self.connection_manager.get_application()
            if not acad_app:
                raise AutoCADConnectionError("AutoCAD application not available", is_mock_mode=False)

            # Convert parameters to VARIANT arrays
            center_variant = self._convert_to_variant_array(center)
            axis_variant = self._convert_to_variant_array(axis_vector)

            # Build command string - AutoCAD HELIX command sequence
            x, y, z = center

            command_sequence = [
                "HELIX",                                    # Start HELIX command
                f"{x},{y},{z}",                            # Center point
                str(base_radius),                          # Base radius
                str(top_radius),                           # Top radius
                str(height),                               # Height
                ""                                         # Final enter to execute
            ]

            # Join with carriage returns and send to AutoCAD
            command_string = "\r".join(command_sequence) + "\r"

            self.logger.debug(f"Sending HELIX command: {command_string.replace(chr(13), '|')}")

            # Send the command to AutoCAD
            if hasattr(acad_app, 'ActiveDocument'):
                doc = acad_app.ActiveDocument
                doc.SendCommand(command_string)

                # Try to find and modify the newly created helix
                try:
                    # Use a more robust approach with polling instead of fixed sleep
                    max_wait_time = 2.0  # Maximum wait time in seconds
                    poll_interval = 0.1   # Polling interval
                    wait_time = 0.0
                    
                    # Wait for command to complete with polling
                    while wait_time < max_wait_time:
                        time.sleep(poll_interval)
                        wait_time += poll_interval
                        
                        # Check if helix is available
                        model_space = self.connection_manager.get_model_space()
                        if model_space:
                            helix_found = False
                            for i in range(min(10, model_space.Count)):  # Check last 10 entities
                                try:
                                    entity = model_space.Item(model_space.Count - 1 - i)
                                    if hasattr(entity, 'ObjectName') and entity.ObjectName == "AcDbHelix":
                                        helix_found = True
                                        break
                                except:
                                    continue
                            if helix_found:
                                break
                    if model_space:
                        for i in range(model_space.Count - 1, -1, -1):  # Search backwards from most recent
                            entity = model_space.Item(i)
                            if hasattr(entity, 'ObjectName') and entity.ObjectName == "AcDbHelix":
                                # Found a helix, set the turns property
                                entity.Turns = turns
                                self.logger.info(f"Set helix turns to {turns}")
                                break
                        else:
                            self.logger.warning("Could not find newly created helix to set turns property")
                    else:
                        self.logger.warning("Could not find newly created helix to set turns property")

                except Exception as prop_error:
                    self.logger.warning(f"Could not set helix turns property: {prop_error}")

            else:
                # Alternative approach if ActiveDocument not available
                acad_app.SendCommand(command_string)

            helix = True  # Return success indicator since we can't get the entity directly

            self.logger.debug(f"AutoCAD helix created successfully")
            return helix

        except (AutoCADConnectionError, GeometryError):
            raise
        except Exception as e:
            error_msg = f"Failed to create helix in AutoCAD: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GeometryError(
                error_msg,
                geometry_type="helix",
                operation="create",
                details={
                    "center": center, "base_radius": base_radius,
                    "top_radius": top_radius, "height": height,
                    "turns": turns, "axis_vector": axis_vector
                }
            )

    def _convert_to_variant_array(self, coordinates: tuple) -> Any:
        """
        Convert Python coordinates to win32com VARIANT array format.

        Args:
            coordinates: Tuple of (x, y, z) coordinates

        Returns:
            win32com.client.VARIANT array compatible with AutoCAD

        Raises:
            GeometryError: If conversion fails
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
            raise GeometryError(
                f"Coordinate conversion failed: {e}",
                calculation="coordinate_conversion",
                input_values={"coordinates": coordinates}
            )