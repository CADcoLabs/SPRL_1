"""
Error handling and logging module for AutoCAD interface.
Provides comprehensive error handling, logging, and exception management.
"""

import time
from typing import Optional, Any, Dict, List
from abc import ABC, abstractmethod

from .logging_config import get_logger
from .exceptions import (
    AutoCADConnectionError, GenerationError, GeometryError,
    handle_exception_chain
)


class ErrorHandler(ABC):
    """Abstract base class for error handlers."""

    @abstractmethod
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Handle an error with given context."""
        pass

    @abstractmethod
    def log_operation_start(self, operation: str, details: Dict[str, Any]) -> None:
        """Log the start of an operation."""
        pass

    @abstractmethod
    def log_operation_end(self, operation: str, success: bool, details: Dict[str, Any]) -> None:
        """Log the end of an operation."""
        pass


class AutoCADErrorHandler(ErrorHandler):
    """
    Comprehensive error handler for AutoCAD operations with logging and recovery.
    """

    def __init__(self):
        """Initialize error handler."""
        self.logger = get_logger(__name__ + '.AutoCADErrorHandler')
        self.error_history = []
        self.operation_stack = []

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """
        Handle an error with comprehensive logging and context.

        Args:
            error: The exception that occurred
            context: Dictionary containing error context information
        """
        # Log the error with full context
        error_info = {
            "timestamp": time.time(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "stack_trace": self._get_stack_trace(error)
        }

        self.error_history.append(error_info)

        # Log based on error type
        if isinstance(error, AutoCADConnectionError):
            self.logger.error(f"AutoCAD Connection Error: {error}", exc_info=True)
            if hasattr(error, 'connection_attempt'):
                self.logger.error(f"Connection attempt {error.connection_attempt} failed")
        elif isinstance(error, GenerationError):
            self.logger.error(f"Generation Error: {error}", exc_info=True)
            if hasattr(error, 'geometry_type'):
                self.logger.error(f"Failed to generate {error.geometry_type} during {error.operation}")
        elif isinstance(error, GeometryError):
            self.logger.error(f"Geometry Error: {error}", exc_info=True)
            if hasattr(error, 'calculation'):
                self.logger.error(f"Failed calculation: {error.calculation}")
        else:
            self.logger.error(f"Unexpected Error: {error}", exc_info=True)

        # Log additional context information
        if context:
            self.logger.error(f"Error Context: {context}")

        # Check for patterns in recent errors
        self._analyze_error_patterns()

    def log_operation_start(self, operation: str, details: Dict[str, Any]) -> None:
        """
        Log the start of an operation.

        Args:
            operation: Name of the operation
            details: Dictionary containing operation details
        """
        operation_info = {
            "operation": operation,
            "start_time": time.time(),
            "details": details
        }

        self.operation_stack.append(operation_info)
        self.logger.info(f"Starting operation: {operation}")
        self.logger.debug(f"Operation details: {details}")

    def log_operation_end(self, operation: str, success: bool, details: Dict[str, Any]) -> None:
        """
        Log the end of an operation.

        Args:
            operation: Name of the operation
            success: Whether the operation was successful
            details: Dictionary containing result details
        """
        end_time = time.time()

        # Find the matching operation in the stack
        for i, op_info in enumerate(reversed(self.operation_stack)):
            if op_info["operation"] == operation:
                start_time = op_info["start_time"]
                duration = end_time - start_time

                if success:
                    self.logger.info(f"Operation '{operation}' completed successfully in {duration:.2f}s")
                    if details:
                        self.logger.debug(f"Result details: {details}")
                else:
                    self.logger.error(f"Operation '{operation}' failed after {duration:.2f}s")
                    if details:
                        self.logger.error(f"Failure details: {details}")

                # Remove from stack
                self.operation_stack.pop(len(self.operation_stack) - 1 - i)
                break
        else:
            self.logger.warning(f"Could not find matching start for operation: {operation}")

    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get a summary of recent errors.

        Returns:
            Dictionary containing error statistics and recent errors
        """
        total_errors = len(self.error_history)
        recent_errors = self.error_history[-10:]  # Last 10 errors

        error_types = {}
        for error in self.error_history:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            "total_errors": total_errors,
            "error_types": error_types,
            "recent_errors": recent_errors,
            "active_operations": len(self.operation_stack)
        }

    def clear_error_history(self) -> None:
        """Clear the error history."""
        self.error_history.clear()
        self.logger.info("Error history cleared")

    def _get_stack_trace(self, error: Exception) -> str:
        """Get formatted stack trace from exception."""
        import traceback
        return ''.join(traceback.format_exception(type(error), error, error.__traceback__))

    def _analyze_error_patterns(self) -> None:
        """Analyze recent errors for patterns."""
        if len(self.error_history) < 3:
            return

        recent_errors = self.error_history[-5:]  # Last 5 errors
        error_types = [error["error_type"] for error in recent_errors]

        # Check for repeated connection failures
        if error_types.count("AutoCADConnectionError") >= 3:
            self.logger.warning("Multiple consecutive AutoCAD connection errors detected")
            self.logger.warning("Consider checking AutoCAD installation and COM registration")

        # Check for repeated geometry errors
        if error_types.count("GeometryError") >= 3:
            self.logger.warning("Multiple consecutive geometry errors detected")
            self.logger.warning("Check input parameters and coordinate system")

        # Check for repeated generation errors
        if error_types.count("GenerationError") >= 3:
            self.logger.warning("Multiple consecutive generation errors detected")
            self.logger.warning("Check AutoCAD memory usage and system resources")


class AutoCADLoggingManager:
    """
    Manages comprehensive logging for AutoCAD operations.
    """

    def __init__(self):
        """Initialize logging manager."""
        self.logger = get_logger(__name__ + '.LoggingManager')
        self.operation_log = []
        self.performance_metrics = {}

    def log_connection_attempt(self, attempt: int, max_attempts: int, error: Optional[Exception] = None) -> None:
        """
        Log a connection attempt.

        Args:
            attempt: Current attempt number
            max_attempts: Maximum number of attempts
            error: Exception if attempt failed
        """
        if error:
            self.logger.warning(f"AutoCAD connection attempt {attempt}/{max_attempts} failed: {str(error)}")
        else:
            self.logger.info(f"AutoCAD connection attempt {attempt}/{max_attempts} succeeded")

    def log_entity_creation(self, entity_type: str, parameters: Dict[str, Any], success: bool, error: Optional[Exception] = None) -> None:
        """
        Log entity creation attempt.

        Args:
            entity_type: Type of entity being created
            parameters: Parameters used for creation
            success: Whether creation was successful
            error: Exception if creation failed
        """
        if success:
            self.logger.info(f"Successfully created {entity_type} entity")
            self.logger.debug(f"Entity parameters: {parameters}")
        else:
            self.logger.error(f"Failed to create {entity_type} entity: {str(error) if error else 'Unknown error'}")
            self.logger.debug(f"Failed entity parameters: {parameters}")

    def log_performance_metric(self, operation: str, duration: float, success: bool) -> None:
        """
        Log performance metrics for operations.

        Args:
            operation: Name of the operation
            duration: Duration in seconds
            success: Whether the operation was successful
        """
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_duration": 0.0,
                "avg_duration": 0.0
            }

        metrics = self.performance_metrics[operation]
        metrics["total_calls"] += 1

        if success:
            metrics["successful_calls"] += 1
        else:
            metrics["failed_calls"] += 1

        metrics["total_duration"] += duration
        metrics["avg_duration"] = metrics["total_duration"] / metrics["total_calls"]

        self.logger.debug(f"Performance metric for {operation}: {duration:.3f}s (avg: {metrics['avg_duration']:.3f}s)")

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate a performance report.

        Returns:
            Dictionary containing performance metrics
        """
        report = {
            "operations": {},
            "summary": {
                "total_operations": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "total_duration": 0.0
            }
        }

        for operation, metrics in self.performance_metrics.items():
            report["operations"][operation] = metrics.copy()

            report["summary"]["total_operations"] += metrics["total_calls"]
            report["summary"]["successful_operations"] += metrics["successful_calls"]
            report["summary"]["failed_operations"] += metrics["failed_calls"]
            report["summary"]["total_duration"] += metrics["total_duration"]

        if report["summary"]["total_operations"] > 0:
            success_rate = (report["summary"]["successful_operations"] /
                          report["summary"]["total_operations"]) * 100
            report["summary"]["success_rate"] = success_rate
            self.logger.info(f"Performance report: {success_rate:.1f}% success rate across {report['summary']['total_operations']} operations")

        return report

    def log_system_info(self) -> None:
        """Log system and AutoCAD information."""
        import sys
        import platform

        self.logger.info("=== System Information ===")
        self.logger.info(f"Python version: {sys.version}")
        self.logger.info(f"Platform: {platform.platform()}")
        self.logger.info(f"Architecture: {platform.architecture()}")
        self.logger.info(f"Machine: {platform.machine()}")

        # Check for AutoCAD COM availability
        try:
            import win32com.client
            self.logger.info("win32com.client: Available")
        except ImportError:
            self.logger.warning("win32com.client: Not available")

        try:
            import pythoncom
            self.logger.info("pythoncom: Available")
        except ImportError:
            self.logger.warning("pythoncom: Not available")

    def log_configuration(self, config: Dict[str, Any]) -> None:
        """
        Log configuration settings.

        Args:
            config: Configuration dictionary to log
        """
        self.logger.info("=== Configuration Settings ===")
        for section, settings in config.items():
            self.logger.info(f"{section}:")
            if isinstance(settings, dict):
                for key, value in settings.items():
                    # Don't log sensitive information
                    if "password" not in key.lower() and "token" not in key.lower():
                        self.logger.info(f"  {key}: {value}")
            else:
                self.logger.info(f"  {settings}")


# Global instances for use across the application
error_handler = AutoCADErrorHandler()
logging_manager = AutoCADLoggingManager()