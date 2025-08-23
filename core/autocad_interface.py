"""
AutoCAD COM interface wrapper with modular architecture.
Provides robust connection management and error handling for AutoCAD 2025.
Enhanced with comprehensive logging and specific exception handling.
"""

import os
import time
from typing import Optional, Any, Dict, List
from abc import ABC, abstractmethod

from .logging_config import get_logger
from .exceptions import (
    AutoCADConnectionError, GenerationError, GeometryError,
    handle_exception_chain
)
from .autocad_connection import AutoCADConnectionManager
from .geometry_creation import AutoCADGeometryCreator
from .entity_manipulation import AutoCADEntityManipulator
from .autocad_error_handling import error_handler, logging_manager

# Import COM modules for parameter marshalling
try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False
    win32com = None
    pythoncom = None


class AutoCADInterface(ABC):
    """Abstract base for AutoCAD interface implementations."""

    @abstractmethod
    def connect(self) -> bool:
        """Connect to AutoCAD."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from AutoCAD."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to AutoCAD."""
        pass

    @abstractmethod
    def create_circle(self, center: tuple, radius: float) -> Any:
        """Create a circle entity."""
        pass

    @abstractmethod
    def create_line(self, start_point: tuple, end_point: tuple) -> Any:
        """Create a line entity."""
        pass

    @abstractmethod
    def create_arc(
        self, center: tuple, radius: float, start_angle: float, end_angle: float
    ) -> Any:
        """Create an arc entity."""
        pass

    @abstractmethod
    def create_region(self, objects: list) -> Any:
        """Create a region from a list of objects."""
        pass

    @abstractmethod
    def create_extruded_solid(self, profile: Any, height: float, taper_angle: float = 0) -> Any:
        """Create an extruded solid from a profile."""
        pass

    @abstractmethod
    def create_helix(
        self,
        center: tuple,
        base_radius: float,
        top_radius: float,
        height: float,
        turns: float,
        axis_vector: tuple = (0, 0, 1)
    ) -> Any:
        """Create a helix entity."""
        pass

    @abstractmethod
    def add_text(self, text: str, position: tuple, height: float = 0.125) -> Any:
        """Add text annotation to the drawing."""
        pass

    @abstractmethod
    def add_dimension(self, point1: tuple, point2: tuple, dimension_line_point: tuple, text: str = None) -> Any:
        """Add linear dimension between two points."""
        pass


class MockAutoCADInterface(AutoCADInterface):
    """
    Mock AutoCAD interface for development without AutoCAD dependency.
    Simulates AutoCAD operations for testing and development.
    """

    def __init__(self):
        """Initialize mock interface."""
        self.logger = get_logger(__name__ + '.MockAutoCAD')
        self.connected = False
        self.entities = []
        self.last_operation = None
        self.current_layer = "0"  # Default layer
        self.current_color = 7    # Default color (white/black)
        
        self.logger.info("Mock AutoCAD interface initialized")
        self.logger.debug("Mock mode active - no real AutoCAD required")

    def connect(self) -> bool:
        """Simulate connection to AutoCAD."""
        try:
            self.logger.info("Mock AutoCAD: Simulating connection...")
            time.sleep(0.1)  # Simulate connection delay
            self.connected = True
            self.logger.info("Mock AutoCAD connection established successfully")
            return True
        except Exception as e:
            self.logger.error(f"Mock AutoCAD connection failed: {str(e)}", exc_info=True)
            raise AutoCADConnectionError(
                f"Mock connection failed: {str(e)}",
                is_mock_mode=True
            )

    def disconnect(self) -> None:
        """Simulate disconnection from AutoCAD."""
        try:
            self.logger.info("Mock AutoCAD: Simulating disconnection...")
            self.connected = False
            self.logger.info("Mock AutoCAD disconnected successfully")
        except Exception as e:
            self.logger.warning(f"Mock AutoCAD disconnection warning: {str(e)}")
            # Don't raise exception for disconnection issues in mock mode

    def is_connected(self) -> bool:
        """Check mock connection status."""
        return self.connected

    def create_circle(self, center: tuple, radius: float) -> Dict[str, Any]:
        """Simulate circle creation."""
        try:
            self.logger.debug(f"Creating mock circle: center={center}, radius={radius}")
            
            # Validate inputs
            if radius <= 0:
                raise GeometryError(
                    f"Invalid circle radius: {radius}",
                    calculation="circle_validation",
                    input_values={"center": center, "radius": radius}
                )
            
            entity = {
                "type": "circle",
                "center": center,
                "radius": radius,
                "id": len(self.entities),
            }
            self.entities.append(entity)
            self.last_operation = f"Created circle at {center} with radius {radius}"
            
            self.logger.debug(f"Mock circle created successfully: ID {entity['id']}")
            return entity
            
        except GeometryError:
            raise
        except Exception as e:
            self.logger.error(f"Mock circle creation failed: {str(e)}", exc_info=True)
            raise GenerationError(
                f"Failed to create mock circle: {str(e)}",
                geometry_type="circle",
                operation="create"
            )

    def create_line(self, start_point: tuple, end_point: tuple) -> Dict[str, Any]:
        """Simulate line creation."""
        try:
            self.logger.debug(f"Creating mock line: start={start_point}, end={end_point}")
            
            # Validate inputs
            if start_point == end_point:
                raise GeometryError(
                    "Line start and end points cannot be identical",
                    calculation="line_validation",
                    input_values={"start_point": start_point, "end_point": end_point}
                )
            
            entity = {
                "type": "line",
                "start_point": start_point,
                "end_point": end_point,
                "id": len(self.entities),
            }
            self.entities.append(entity)
            self.last_operation = f"Created line from {start_point} to {end_point}"
            
            self.logger.debug(f"Mock line created successfully: ID {entity['id']}")
            return entity
            
        except GeometryError:
            raise
        except Exception as e:
            self.logger.error(f"Mock line creation failed: {str(e)}", exc_info=True)
            raise GenerationError(
                f"Failed to create mock line: {str(e)}",
                geometry_type="line",
                operation="create"
            )

    def create_arc(
        self, center: tuple, radius: float, start_angle: float, end_angle: float
    ) -> Dict[str, Any]:
        """Simulate arc creation."""
        try:
            self.logger.debug(f"Creating mock arc: center={center}, radius={radius}, angles={start_angle}-{end_angle}")
            
            # Validate inputs
            if radius <= 0:
                raise GeometryError(
                    f"Invalid arc radius: {radius}",
                    calculation="arc_validation",
                    input_values={
                        "center": center, "radius": radius, 
                        "start_angle": start_angle, "end_angle": end_angle
                    }
                )
            
            entity = {
                "type": "arc",
                "center": center,
                "radius": radius,
                "start_angle": start_angle,
                "end_angle": end_angle,
                "id": len(self.entities),
            }
            self.entities.append(entity)
            self.last_operation = f"Created arc at {center} with radius {radius}"
            
            self.logger.debug(f"Mock arc created successfully: ID {entity['id']}")
            return entity
            
        except GeometryError:
            raise
        except Exception as e:
            self.logger.error(f"Mock arc creation failed: {str(e)}", exc_info=True)
            raise GenerationError(
                f"Failed to create mock arc: {str(e)}",
                geometry_type="arc",
                operation="create"
            )

    def create_cylinder(
        self, center: tuple, radius: float, height: float
    ) -> Dict[str, Any]:
        """Simulate cylinder creation."""
        try:
            self.logger.debug(f"Creating mock cylinder: center={center}, radius={radius}, height={height}")
            
            # Validate inputs
            if radius <= 0 or height <= 0:
                raise GeometryError(
                    f"Invalid cylinder dimensions: radius={radius}, height={height}",
                    calculation="cylinder_validation",
                    input_values={"center": center, "radius": radius, "height": height}
                )
            
            entity = {
                "type": "cylinder",
                "center": center,
                "radius": radius,
                "height": height,
                "id": len(self.entities),
            }
            self.entities.append(entity)
            self.last_operation = (
                f"Created cylinder at {center} with radius {radius} and height {height}"
            )
            
            self.logger.debug(f"Mock cylinder created successfully: ID {entity['id']}")
            return entity
            
        except GeometryError:
            raise
        except Exception as e:
            self.logger.error(f"Mock cylinder creation failed: {str(e)}", exc_info=True)
            raise GenerationError(
                f"Failed to create mock cylinder: {str(e)}",
                geometry_type="cylinder",
                operation="create"
            )

    def create_spline(self, points: List[tuple]) -> Dict[str, Any]:
        """Simulate spline creation."""
        try:
            self.logger.debug(f"Creating mock spline with {len(points)} points")
            
            # Validate inputs
            if len(points) < 2:
                raise GeometryError(
                    f"Spline requires at least 2 points, got {len(points)}",
                    calculation="spline_validation",
                    input_values={"points": points}
                )
            
            entity = {"type": "spline", "points": points, "id": len(self.entities)}
            self.entities.append(entity)
            self.last_operation = f"Created spline with {len(points)} points"
            
            self.logger.debug(f"Mock spline created successfully: ID {entity['id']}")
            return entity
            
        except GeometryError:
            raise
        except Exception as e:
            self.logger.error(f"Mock spline creation failed: {str(e)}", exc_info=True)
            raise GenerationError(
                f"Failed to create mock spline: {str(e)}",
                geometry_type="spline",
                operation="create"
            )

    def create_sphere(self, center: tuple, radius: float) -> Dict[str, Any]:
        """Simulate sphere creation."""
        try:
            self.logger.debug(f"Creating mock sphere: center={center}, radius={radius}")
            
            # Validate inputs
            if radius <= 0:
                raise GeometryError(
                    f"Invalid sphere radius: {radius}",
                    calculation="sphere_validation",
                    input_values={"center": center, "radius": radius}
                )
            
            entity = {
                "type": "sphere",
                "center": center,
                "radius": radius,
                "id": len(self.entities),
            }
            self.entities.append(entity)
            self.last_operation = f"Created sphere at {center} with radius {radius}"
            
            self.logger.debug(f"Mock sphere created successfully: ID {entity['id']}")
            return entity
            
        except GeometryError:
            raise
        except Exception as e:
            self.logger.error(f"Mock sphere creation failed: {str(e)}", exc_info=True)
            raise GenerationError(
                f"Failed to create mock sphere: {str(e)}",
                geometry_type="sphere",
                operation="create"
            )

    def create_box(
        self, center: tuple, length: float, width: float, height: float
    ) -> Dict[str, Any]:
        """Simulate box creation."""
        try:
            self.logger.debug(f"Creating mock box: center={center}, dimensions={length}x{width}x{height}")
            
            # Validate inputs
            if length <= 0 or width <= 0 or height <= 0:
                raise GeometryError(
                    f"Invalid box dimensions: {length}x{width}x{height}",
                    calculation="box_validation",
                    input_values={
                        "center": center, "length": length, 
                        "width": width, "height": height
                    }
                )
            
            entity = {
                "type": "box",
                "center": center,
                "length": length,
                "width": width,
                "height": height,
                "id": len(self.entities),
            }
            self.entities.append(entity)
            self.last_operation = (
                f"Created box at {center} with dimensions {length}x{width}x{height}"
            )
            
            self.logger.debug(f"Mock box created successfully: ID {entity['id']}")
            return entity
            
        except GeometryError:
            raise
        except Exception as e:
            self.logger.error(f"Mock box creation failed: {str(e)}", exc_info=True)
            raise GenerationError(
                f"Failed to create mock box: {str(e)}",
                geometry_type="box",
                operation="create"
            )

    def create_region(self, objects: list) -> list:
        """Simulate region creation."""
        region = {"type": "region", "objects": objects, "id": len(self.entities)}
        self.entities.append(region)
        return [region]

    def create_extruded_solid(self, profile: Any, height: float, taper_angle: float = 0) -> Dict[str, Any]:
        """Simulate extruded solid creation."""
        solid = {
            "type": "solid",
            "profile": profile,
            "height": height,
            "taper_angle": taper_angle,
            "id": len(self.entities),
        }
        self.entities.append(solid)
        return solid

    def create_helix(
        self, 
        center: tuple, 
        base_radius: float, 
        top_radius: float, 
        height: float, 
        turns: float, 
        axis_vector: tuple = (0, 0, 1)
    ) -> Dict[str, Any]:
        """Simulate helix creation."""
        try:
            self.logger.debug(f"Creating mock helix: center={center}, base_radius={base_radius}, top_radius={top_radius}, height={height}, turns={turns}")
            
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
            
            entity = {
                "type": "helix",
                "center": center,
                "base_radius": base_radius,
                "top_radius": top_radius,
                "height": height,
                "turns": turns,
                "axis_vector": axis_vector,
                "id": len(self.entities),
            }
            self.entities.append(entity)
            self.last_operation = f"Created helix at {center} with {turns} turns and height {height}"
            
            self.logger.debug(f"Mock helix created successfully: ID {entity['id']}")
            return entity
            
        except GeometryError:
            raise
        except Exception as e:
            self.logger.error(f"Mock helix creation failed: {str(e)}", exc_info=True)
            raise GenerationError(
                f"Failed to create mock helix: {str(e)}",
                geometry_type="helix",
                operation="create"
            )

    def add_text(self, text: str, position: tuple, height: float = 0.125) -> Dict[str, Any]:
        """Add text annotation to the drawing."""
        try:
            self.logger.debug(f"Creating mock text: '{text}' at {position}, height={height}")
            
            entity = {
                "type": "text",
                "text": text,
                "position": position,
                "height": height,
                "layer": self.current_layer or "0",
                "color": self.current_color or 7,
                "id": f"text_{len(self.entities) + 1}"
            }
            
            self.entities.append(entity)
            self.logger.debug(f"Created mock text entity: {entity['id']}")
            return entity
            
        except Exception as e:
            self.logger.error(f"Mock text creation failed: {str(e)}", exc_info=True)
            raise GenerationError(
                f"Failed to create mock text: {str(e)}",
                geometry_type="text",
                operation="create"
            )

    def add_dimension(self, point1: tuple, point2: tuple, dimension_line_point: tuple, text: str = None) -> Dict[str, Any]:
        """Add linear dimension between two points."""
        try:
            import math
            
            # Calculate distance
            distance = math.sqrt(sum((p2 - p1)**2 for p1, p2 in zip(point1, point2)))
            dim_text = text or f"{distance:.2f}\""
            
            self.logger.debug(f"Creating mock dimension: {point1} to {point2}, text='{dim_text}'")
            
            entity = {
                "type": "dimension",
                "point1": point1,
                "point2": point2,
                "dimension_line_point": dimension_line_point,
                "text": dim_text,
                "distance": distance,
                "layer": self.current_layer or "0",
                "color": self.current_color or 7,
                "id": f"dim_{len(self.entities) + 1}"
            }
            
            self.entities.append(entity)
            self.logger.debug(f"Created mock dimension entity: {entity['id']}")
            return entity
            
        except Exception as e:
            self.logger.error(f"Mock dimension creation failed: {str(e)}", exc_info=True)
            raise GenerationError(
                f"Failed to create mock dimension: {str(e)}",
                geometry_type="dimension",
                operation="create"
            )

    def get_entities(self) -> List[Dict[str, Any]]:
        """Get all created entities for testing."""
        return self.entities.copy()


class RealAutoCADInterface(AutoCADInterface):
    """
    Real AutoCAD COM interface with modular architecture.
    Requires AutoCAD 2025 and pywin32.
    Uses proper parameter marshalling to avoid -2147352567 errors.
    """

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize real AutoCAD interface.

        Args:
            max_retries: Maximum connection retry attempts
            retry_delay: Delay between retry attempts in seconds
        """
        self.logger = get_logger(__name__ + '.RealAutoCAD')

        # Initialize modular components
        self.connection_manager = AutoCADConnectionManager(max_retries, retry_delay)
        self.geometry_creator = AutoCADGeometryCreator(self.connection_manager)
        self.entity_manipulator = AutoCADEntityManipulator(self.connection_manager)

        self.logger.info(f"Real AutoCAD interface initialized (max_retries={max_retries}, retry_delay={retry_delay}s)")
        self.logger.debug("Real AutoCAD mode - requires AutoCAD 2025 and pywin32")
    
    @property
    def model_space(self):
        """Provide access to model space for backward compatibility."""
        return self.connection_manager.get_model_space()
    
    @property
    def acad_app(self):
        """Provide access to AutoCAD application for backward compatibility."""
        return self.connection_manager.get_application()
    
    @property
    def acad_doc(self):
        """Provide access to AutoCAD document for backward compatibility."""
        return self.connection_manager.get_document()

    def create_circle(self, center: tuple, radius: float) -> Any:
        """Create circle in AutoCAD using geometry creator."""
        return self.geometry_creator.create_circle(center, radius)

    def create_line(self, start_point: tuple, end_point: tuple) -> Any:
        """Create line in AutoCAD using geometry creator."""
        return self.geometry_creator.create_line(start_point, end_point)

    def create_arc(self, center: tuple, radius: float, start_angle: float, end_angle: float) -> Any:
        """Create arc in AutoCAD using geometry creator."""
        return self.geometry_creator.create_arc(center, radius, start_angle, end_angle)

    def create_region(self, objects: list) -> Any:
        """Create region using entity manipulator."""
        return self.entity_manipulator.create_region(objects)

    def create_extruded_solid(self, profile: Any, height: float, taper_angle: float = 0) -> Any:
        """Create extruded solid using entity manipulator."""
        return self.entity_manipulator.create_extruded_solid(profile, height, taper_angle)

    def create_helix(self, center: tuple, base_radius: float, top_radius: float,
                    height: float, turns: float, axis_vector: tuple = (0, 0, 1)) -> Any:
        """Create helix using geometry creator."""
        return self.geometry_creator.create_helix(center, base_radius, top_radius, height, turns, axis_vector)

    def add_text(self, text: str, position: tuple, height: float = 0.125) -> Any:
        """Add text using entity manipulator."""
        return self.entity_manipulator.add_text(text, position, height)

    def add_dimension(self, point1: tuple, point2: tuple, dimension_line_point: tuple, text: str = None) -> Any:
        """Add dimension using entity manipulator."""
        return self.entity_manipulator.add_dimension(point1, point2, dimension_line_point, text)

    def connect(self) -> bool:
        """
        Connect to AutoCAD with retry logic.

        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            return self.connection_manager.connect()
        except AutoCADConnectionError:
            raise

    def disconnect(self) -> None:
        """Disconnect from AutoCAD."""
        self.connection_manager.disconnect()

    def is_connected(self) -> bool:
        """
        Check if connected to AutoCAD.

        Returns:
            bool: True if connected and AutoCAD is responsive
        """
        return self.connection_manager.is_connected()

    def _convert_to_variant_array(self, coordinates: tuple) -> Any:
        """
        Convert Python coordinates to win32com VARIANT array format.
        This is the only format that works reliably for AutoCAD COM interface.
        
        Args:
            coordinates: Tuple of (x, y, z) coordinates
            
        Returns:
            win32com.client.VARIANT array compatible with AutoCAD
        """
        try:
            # Ensure we have 3D coordinates
            coords = [
                float(coordinates[0]),
                float(coordinates[1]),
                float(coordinates[2]) if len(coordinates) > 2 else 0.0
            ]
            
            # Create VARIANT array using the working format from diagnostics
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
    

    

    def create_arc(
        self, center: tuple, radius: float, start_angle: float, end_angle: float
    ) -> Any:
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
            GenerationError: If creation fails
        """
        if not self.is_connected():
            error_msg = "Not connected to AutoCAD"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        try:
            self.logger.debug(f"Creating AutoCAD arc: center={center}, radius={radius}, angles={start_angle}-{end_angle}")
            
            # Ensure we're using World Coordinate System for consistent positioning
            if hasattr(self.acad_app, 'ActiveDocument'):
                doc = self.acad_app.ActiveDocument
                doc.SendCommand("UCS\rW\r")  # Set UCS to World
            
            # Convert center to VARIANT array (the only format that works)
            center_variant = self._convert_to_variant_array(center)
            arc = self.model_space.AddArc(center_variant, radius, start_angle, end_angle)
            
            self.logger.debug(f"AutoCAD arc created successfully")
            return arc
            
        except (AutoCADConnectionError, GeometryError):
            raise
        except Exception as e:
            error_msg = f"Failed to create arc in AutoCAD: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GenerationError(
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
    
    def create_cylinder(
        self, center: tuple, radius: float, height: float
    ) -> Any:
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
            GenerationError: If creation fails
        """
        if not self.is_connected():
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
            
            # Convert center to AutoCAD point array with explicit validation
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
            
            # Convert center to VARIANT array (the only format that works)
            center_variant = self._convert_to_variant_array((x, y, z))
            
            # Try to create a true cylinder using AddCylinder if available
            if hasattr(self.model_space, 'AddCylinder'):
                try:
                    self.logger.debug(f"Attempting to create cylinder with AddCylinder")
                    self.logger.debug(f"Parameters: center=VARIANT, radius={radius}, height={height}")
                    cylinder = self.model_space.AddCylinder(center_variant, radius, height)
                    self.logger.debug(f"AutoCAD cylinder created successfully")
                    return cylinder
                except Exception as cylinder_error:
                    self.logger.warning(f"AddCylinder failed, falling back to circle: {str(cylinder_error)}")
            
            # Fallback to creating a circle (this maintains backward compatibility)
            self.logger.debug(f"Attempting to create circle with AddCircle")
            self.logger.debug(f"Parameters: center=VARIANT, radius={radius}")
            circle = self.model_space.AddCircle(center_variant, radius)
            self.logger.debug(f"AutoCAD circle (cylinder fallback) created successfully")
            return circle
            
        except (GeometryError, AutoCADConnectionError):
            raise
        except Exception as e:
            error_msg = f"Failed to create cylinder/circle in AutoCAD: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GenerationError(
                error_msg,
                geometry_type="cylinder",
                operation="create",
                details={"center": center, "radius": radius, "height": height}
            )

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
        if not self.is_connected():
            error_msg = "Not connected to AutoCAD"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        try:
            self.logger.debug(f"Creating AutoCAD spline with {len(points)} points")
            
            # Validate input
            if len(points) < 2:
                raise GeometryError(
                    f"Spline requires at least 2 points, got {len(points)}",
                    calculation="spline_validation",
                    input_values={"points": points}
                )
            
            # Try different approaches for spline creation
            # Approach 1: Individual VARIANT arrays for each point
            try:
                point_variants = []
                for point in points:
                    point_variant = self._convert_to_variant_array(point)
                    point_variants.append(point_variant)
                
                # Create spline with point array
                spline = self.model_space.AddSpline(point_variants, None, None)
                
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
                    
                    spline = self.model_space.AddPolyline(points_variant)
                    
                except Exception as polyline_error:
                    raise Exception(f"Both spline and polyline creation failed: {variant_error}, {polyline_error}")
            
            self.logger.debug(f"AutoCAD spline created successfully")
            return spline
            
        except (AutoCADConnectionError, GeometryError):
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
        if not self.is_connected():
            error_msg = "Not connected to AutoCAD"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        try:
            self.logger.debug(f"Creating AutoCAD sphere: center={center}, radius={radius}")
            
            # Validate inputs
            if radius <= 0:
                raise GeometryError(
                    f"Invalid sphere radius: {radius}",
                    calculation="sphere_validation",
                    input_values={"center": center, "radius": radius}
                )
            
            # Convert center to VARIANT array
            center_variant = self._convert_to_variant_array(center)
            
            # Try to create sphere using AddSphere if available
            if hasattr(self.model_space, 'AddSphere'):
                sphere = self.model_space.AddSphere(center_variant, radius)
                self.logger.debug(f"AutoCAD sphere created successfully")
                return sphere
            else:
                # Fallback to circle if sphere not available
                self.logger.warning("AddSphere not available, falling back to circle")
                circle = self.model_space.AddCircle(center_variant, radius)
                return circle
            
        except (AutoCADConnectionError, GeometryError):
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
        if not self.is_connected():
            error_msg = "Not connected to AutoCAD"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        try:
            self.logger.debug(f"Creating AutoCAD box: center={center}, dimensions={length}x{width}x{height}")
            
            # Validate inputs
            if length <= 0 or width <= 0 or height <= 0:
                raise GeometryError(
                    f"Invalid box dimensions: {length}x{width}x{height}",
                    calculation="box_validation",
                    input_values={
                        "center": center, "length": length, 
                        "width": width, "height": height
                    }
                )
            
            # Convert center to VARIANT array
            center_variant = self._convert_to_variant_array(center)
            
            # Try to create box using Add3DBox if available
            if hasattr(self.model_space, 'Add3DBox'):
                # Calculate corner points for 3D box
                half_length = length / 2
                half_width = width / 2
                half_height = height / 2
                
                # Create corner coordinates
                x, y, z = center[0], center[1], center[2] if len(center) > 2 else 0.0
                corner1 = (x - half_length, y - half_width, z - half_height)
                corner2 = (x + half_length, y + half_width, z + half_height)
                
                corner1_variant = self._convert_to_variant_array(corner1)
                corner2_variant = self._convert_to_variant_array(corner2)
                
                box = self.model_space.Add3DBox(corner1_variant, corner2_variant)
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
                
                polyline = self.model_space.AddPolyline(points_variant)
                polyline.Closed = True
                return polyline
            
        except (AutoCADConnectionError, GeometryError):
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

    def create_region(self, objects: list) -> Any:
        """Create a region from a list of objects."""
        if not self.is_connected():
            raise AutoCADConnectionError("Not connected to AutoCAD")
        try:
            # Convert objects list to VARIANT array for COM interface
            objects_variant = win32com.client.VARIANT(
                pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, 
                objects
            )
            region = self.model_space.AddRegion(objects_variant)
            self.logger.debug("AutoCAD region created successfully")
            return region
        except Exception as e:
            raise GenerationError(f"Failed to create region: {e}")

    def create_extruded_solid(self, profile: Any, height: float, taper_angle: float = 0) -> Any:
        """Create an extruded solid from a profile."""
        if not self.is_connected():
            raise AutoCADConnectionError("Not connected to AutoCAD")
        try:
            solid = self.model_space.AddExtrudedSolid(profile, height, taper_angle)
            self.logger.debug("AutoCAD extruded solid created successfully")
            return solid
        except Exception as e:
            raise GenerationError(f"Failed to create extruded solid: {e}")

    def create_helix(
        self, 
        center: tuple, 
        base_radius: float, 
        top_radius: float, 
        height: float, 
        turns: float, 
        axis_vector: tuple = (0, 0, 1)
    ) -> Any:
        """
        Create helix in AutoCAD using proper parameter marshalling.
        This is the correct method for spiral handrails.
        
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
            GenerationError: If creation fails
        """
        if not self.is_connected():
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
            
            # Convert parameters to VARIANT arrays
            center_variant = self._convert_to_variant_array(center)
            axis_variant = self._convert_to_variant_array(axis_vector)
            
            # Create helix using SendCommand method since AddHelix doesn't exist in COM interface
            # Command sequence: HELIX -> center point -> base radius -> top radius -> height -> turns
            x, y, z = center
            
            # Build command string - AutoCAD HELIX command sequence
            # Note: HELIX command defaults to 3 turns, turns must be set via properties after creation
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
            if hasattr(self.acad_app, 'ActiveDocument'):
                doc = self.acad_app.ActiveDocument
                doc.SendCommand(command_string)
                
                # Try to find and modify the newly created helix
                # Note: This is a best-effort approach since we can't get direct reference
                try:
                    # Use a more robust approach with polling instead of fixed sleep
                    max_wait_time = 2.0  # Maximum wait time in seconds
                    poll_interval = 0.1   # Polling interval
                    wait_time = 0.0
                    
                    # Wait for command to complete with polling
                    helix_found = False
                    while wait_time < max_wait_time and not helix_found:
                        time.sleep(poll_interval)
                        wait_time += poll_interval
                        
                        # Find the most recently created helix in model space
                        for i in range(min(10, self.model_space.Count)):  # Check last 10 entities
                            try:
                                entity = self.model_space.Item(self.model_space.Count - 1 - i)
                                if hasattr(entity, 'ObjectName') and entity.ObjectName == "AcDbHelix":
                                    # Found a helix, set the turns property
                                    entity.Turns = turns
                                    self.logger.info(f"Set helix turns to {turns}")
                                    helix_found = True
                                    break
                            except:
                                continue
                                
                    if not helix_found:
                        self.logger.warning("Could not find newly created helix to set turns property")
                        
                except Exception as prop_error:
                    self.logger.warning(f"Could not set helix turns property: {prop_error}")
                    
            else:
                # Alternative approach if ActiveDocument not available
                self.acad_app.SendCommand(command_string)
            
            helix = True  # Return success indicator since we can't get the entity directly
            
            self.logger.debug(f"AutoCAD helix created successfully")
            return helix
            
        except (AutoCADConnectionError, GeometryError):
            raise
        except Exception as e:
            error_msg = f"Failed to create helix in AutoCAD: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise GenerationError(
                error_msg,
                geometry_type="helix",
                operation="create",
                details={
                    "center": center, "base_radius": base_radius,
                    "top_radius": top_radius, "height": height, 
                    "turns": turns, "axis_vector": axis_vector
                }
            )

    def add_text(self, text: str, position: tuple, height: float = 0.125) -> Any:
        """Add text annotation to the drawing."""
        try:
            self.logger.debug(f"Creating AutoCAD text: '{text}' at {position}, height={height}")
            
            # Convert position to AutoCAD variant array
            text_point = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, position)
            
            # Create text entity
            text_entity = self.model_space.AddText(text, text_point, height)
            
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
            
            # Convert points to AutoCAD variant arrays
            pt1 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, point1)
            pt2 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, point2)
            dim_line_pt = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, dimension_line_point)
            
            # Create aligned dimension
            dim_entity = self.model_space.AddDimAligned(pt1, pt2, dim_line_pt)
            
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


def create_autocad_interface() -> AutoCADInterface:
    """
    Factory function to create appropriate AutoCAD interface based on environment.

    Returns:
        AutoCADInterface: Mock or Real interface based on AUTOCAD_MOCK_MODE
    """
    logger = get_logger(__name__)
    mock_mode = os.getenv("AUTOCAD_MOCK_MODE", "false").lower() == "true"

    if mock_mode:
        logger.info("Creating Mock AutoCAD Interface for development")
        return MockAutoCADInterface()
    else:
        logger.info("Creating Real AutoCAD Interface")
        return RealAutoCADInterface()