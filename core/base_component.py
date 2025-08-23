"""
Base component class for all stair components following the Master Orchestrator Pattern.
All stair component modules inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseStairComponent(ABC):
    """
    Abstract base class for all stair components.

    Provides common interface and error handling patterns for:
    - Center pole
    - Treads
    - Landings
    - Pickets (future)
    - Handrails (future)
    - Posts (future)
    """

    def __init__(self, name: str):
        """
        Initialize base component.

        Args:
            name: Component name for logging and error reporting
        """
        self.name = name
        self.is_generated = False
        self.last_error = None

    @abstractmethod
    def validate_parameters(self, config: Dict[str, Any]) -> bool:
        """
        Validate component-specific parameters.

        Args:
            config: Configuration dictionary containing all parameters

        Returns:
            bool: True if parameters are valid, False otherwise

        Raises:
            ValueError: If parameters are invalid with descriptive message
        """
        pass

    @abstractmethod
    def generate_geometry(self, autocad_interface, config: Dict[str, Any]) -> bool:
        """
        Generate AutoCAD geometry for this component.

        Args:
            autocad_interface: AutoCAD COM interface wrapper
            config: Validated configuration parameters

        Returns:
            bool: True if generation successful, False otherwise

        Raises:
            Exception: Component-specific generation errors
        """
        pass

    @abstractmethod
    def get_required_parameters(self) -> List[str]:
        """
        Get list of required configuration parameters for this component.

        Returns:
            List[str]: Required parameter names
        """
        pass

    def cleanup(self, autocad_interface) -> None:
        """
        Cleanup any partial geometry if generation fails.
        Base implementation - override if component needs specific cleanup.

        Args:
            autocad_interface: AutoCAD COM interface wrapper
        """
        # Base cleanup - components can override for specific cleanup
        if hasattr(self, "_created_entities"):
            # TODO: Implement entity cleanup through AutoCAD interface
            pass

    def get_status(self) -> Dict[str, Any]:
        """
        Get current component status for debugging and monitoring.

        Returns:
            Dict with component status information
        """
        return {
            "name": self.name,
            "is_generated": self.is_generated,
            "last_error": str(self.last_error) if self.last_error else None,
        }
