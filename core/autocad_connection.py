"""
AutoCAD connection management module for Spiral Stair Generator.
Handles connection establishment, maintenance, and disconnection from AutoCAD.
"""

import os
import time
from typing import Optional, Any

from .logging_config import get_logger
from .exceptions import AutoCADConnectionError


# Import COM modules for parameter marshalling
try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False
    win32com = None
    pythoncom = None


class AutoCADConnectionManager:
    """
    Manages AutoCAD connection lifecycle with retry logic and error handling.
    """

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize connection manager.

        Args:
            max_retries: Maximum connection retry attempts
            retry_delay: Delay between retry attempts in seconds
        """
        self.logger = get_logger(__name__ + '.ConnectionManager')
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.acad_app = None
        self.acad_doc = None
        self.model_space = None

        # Verify COM availability
        if not COM_AVAILABLE:
            error_msg = "win32com.client and pythoncom are required for AutoCAD connection"
            self.logger.error(error_msg)
            raise AutoCADConnectionError(error_msg, is_mock_mode=False)

        # Initialize COM threading if needed
        try:
            pythoncom.CoInitialize()
            self.logger.debug("COM threading initialized")
        except Exception as e:
            self.logger.debug(f"COM threading initialization not needed or failed: {e}")

        self.logger.info(f"AutoCAD connection manager initialized (max_retries={max_retries}, retry_delay={retry_delay}s)")

    def connect(self) -> bool:
        """
        Connect to AutoCAD with retry logic.

        Returns:
            bool: True if connected successfully, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                # Initialize COM in this thread if needed
                try:
                    pythoncom.CoInitialize()
                    self.logger.debug("COM threading initialized in connect method")
                except Exception as e:
                    self.logger.debug(f"COM threading initialization not needed or failed: {e}")

                # Try to get running AutoCAD instance first
                try:
                    self.acad_app = win32com.client.GetActiveObject("AutoCAD.Application")
                    self.logger.info("Connected to existing AutoCAD instance")
                except Exception as get_active_error:
                    # Start new AutoCAD instance
                    self.logger.debug(f"No active AutoCAD instance found: {str(get_active_error)}")
                    self.logger.info("Starting new AutoCAD instance...")
                    self.acad_app = win32com.client.Dispatch("AutoCAD.Application")
                    self.logger.info("Started new AutoCAD instance")

                # Make AutoCAD visible
                self.acad_app.Visible = True
                self.logger.debug("AutoCAD visibility set to True")

                # Get active document
                self.acad_doc = self.acad_app.ActiveDocument
                self.logger.debug("Active document retrieved")
                
                # Get ModelSpace with error handling
                try:
                    self.model_space = self.acad_doc.ModelSpace
                    self.logger.debug("ModelSpace retrieved successfully")
                except Exception as ms_error:
                    self.logger.warning(f"Direct ModelSpace access failed: {ms_error}")
                    # Try alternative approach
                    try:
                        # Alternative method 1: Get through database
                        self.model_space = self.acad_doc.Database.ModelSpace
                        self.logger.debug("ModelSpace retrieved via Database")
                    except Exception as db_error:
                        self.logger.warning(f"Database ModelSpace access failed: {db_error}")
                        try:
                            # Alternative method 2: Get through layouts
                            model_layout = self.acad_doc.Layouts.Item("Model")
                            self.model_space = model_layout.Block
                            self.logger.debug("ModelSpace retrieved via Layouts")
                        except Exception as layout_error:
                            self.logger.error(f"All ModelSpace access methods failed: {layout_error}")
                            raise Exception(f"Cannot access ModelSpace: {ms_error}")

                # Test the connection by accessing a property
                version = self.acad_app.Version
                self.logger.info(f"Connected to AutoCAD version: {version}")
                self.logger.info(f"AutoCAD connection successful on attempt {attempt + 1}")
                return True

            except Exception as e:
                error_msg = f"AutoCAD connection attempt {attempt + 1} failed: {str(e)}"
                self.logger.warning(error_msg)

                if attempt < self.max_retries - 1:
                    self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"All {self.max_retries} connection attempts failed")

        error_msg = f"Failed to connect to AutoCAD after {self.max_retries} attempts"
        self.logger.error(error_msg)
        raise AutoCADConnectionError(
            error_msg,
            connection_attempt=self.max_retries,
            is_mock_mode=False
        )

    def disconnect(self) -> None:
        """Disconnect from AutoCAD."""
        try:
            if self.acad_app:
                self.logger.info("Disconnecting from AutoCAD...")
                self.model_space = None
                self.acad_doc = None
                self.acad_app = None
                self.logger.info("AutoCAD disconnection completed")
        except Exception as e:
            self.logger.warning(f"Error during AutoCAD disconnection: {str(e)}")
        finally:
            # Uninitialize COM threading if needed
            try:
                pythoncom.CoUninitialize()
                self.logger.debug("COM threading uninitialized")
            except Exception as e:
                self.logger.debug(f"COM threading uninitialization not needed or failed: {e}")
            # Don't raise exception for disconnection issues

    def is_connected(self) -> bool:
        """
        Check if connected to AutoCAD.

        Returns:
            bool: True if connected and AutoCAD is responsive
        """
        try:
            if self.acad_app and self.model_space:
                # Test connection by accessing AutoCAD property
                _ = self.acad_app.Name
                self.logger.debug("AutoCAD connection test passed")
                return True
        except Exception as e:
            self.logger.debug(f"AutoCAD connection test failed: {str(e)}")

        self.logger.debug("AutoCAD is not connected")
        return False

    def get_application(self) -> Optional[Any]:
        """Get the AutoCAD application object."""
        return self.acad_app

    def get_document(self) -> Optional[Any]:
        """Get the active AutoCAD document."""
        return self.acad_doc

    def get_model_space(self) -> Optional[Any]:
        """Get the model space for entity creation."""
        return self.model_space

    def set_ucs_to_world(self) -> None:
        """Set the User Coordinate System to World for consistent positioning."""
        if self.is_connected() and hasattr(self.acad_app, 'ActiveDocument'):
            try:
                doc = self.acad_app.ActiveDocument
                doc.SendCommand("UCS\rW\r")  # Set UCS to World
                self.logger.debug("UCS set to World coordinate system")
            except Exception as e:
                self.logger.warning(f"Failed to set UCS to World: {e}")

    def get_autocad_version(self) -> Optional[str]:
        """Get the AutoCAD version if connected."""
        if self.is_connected():
            try:
                return self.acad_app.Version
            except Exception as e:
                self.logger.warning(f"Failed to get AutoCAD version: {e}")
        return None

    def test_connection(self) -> dict:
        """
        Test the AutoCAD connection and return detailed status.

        Returns:
            dict: Connection test results with status and details
        """
        result = {
            "connected": False,
            "version": None,
            "error": None,
            "details": {}
        }

        try:
            if self.is_connected():
                result["connected"] = True
                result["version"] = self.get_autocad_version()
                result["details"]["application"] = "AutoCAD"
                result["details"]["model_space_available"] = self.model_space is not None
            else:
                result["error"] = "Not connected to AutoCAD"

        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"Connection test failed: {e}")

        return result