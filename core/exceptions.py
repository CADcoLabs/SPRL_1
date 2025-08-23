"""
Custom Exception Hierarchy for Spiral Stair Creator System.

This module defines specific exception types for different error categories,
enabling precise error handling and better user experience.
"""

from typing import Optional, Dict, Any, List


class SpiralStairException(Exception):
    """
    Base exception for all Spiral Stair Creator errors.
    
    Provides common functionality for error tracking and context.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 user_message: Optional[str] = None, recovery_suggestions: Optional[List[str]] = None):
        """
        Initialize base exception.
        
        Args:
            message: Technical error message for logging
            details: Additional error context/data
            user_message: User-friendly error message
            recovery_suggestions: List of suggested recovery actions
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.user_message = user_message or message
        self.recovery_suggestions = recovery_suggestions or []
        
    def get_context(self) -> Dict[str, Any]:
        """Get complete error context for logging."""
        return {
            'exception_type': self.__class__.__name__,
            'message': self.message,
            'user_message': self.user_message,
            'details': self.details,
            'recovery_suggestions': self.recovery_suggestions
        }


class ConfigurationError(SpiralStairException):
    """
    Exception raised for configuration-related errors.
    
    Includes validation failures, file I/O issues, and schema violations.
    """
    
    def __init__(self, message: str, config_path: Optional[str] = None, 
                 validation_errors: Optional[Dict[str, str]] = None, **kwargs):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_path: Path to configuration file (if applicable)
            validation_errors: Dictionary of validation errors
            **kwargs: Additional base exception arguments
        """
        details = kwargs.get('details', {})
        if config_path:
            details['config_path'] = config_path
        if validation_errors:
            details['validation_errors'] = validation_errors
        
        # Generate user-friendly message
        if validation_errors:
            user_msg = f"Configuration validation failed: {'; '.join(validation_errors.values())}"
        else:
            user_msg = f"Configuration error: {message}"
        
        # Recovery suggestions
        recovery = [
            "Check configuration file syntax and values",
            "Verify all required parameters are present",
            "Try loading default configuration"
        ]
        
        super().__init__(message, details=details, user_message=user_msg, recovery_suggestions=recovery)


class ValidationError(SpiralStairException):
    """
    Exception raised for parameter validation failures.
    
    Used when user input doesn't meet requirements or constraints.
    """
    
    def __init__(self, message: str, parameter_name: Optional[str] = None, 
                 parameter_value: Optional[Any] = None, valid_range: Optional[str] = None, **kwargs):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            parameter_name: Name of invalid parameter
            parameter_value: Invalid value
            valid_range: Description of valid value range
            **kwargs: Additional base exception arguments
        """
        details = kwargs.get('details', {})
        if parameter_name:
            details['parameter_name'] = parameter_name
        if parameter_value is not None:
            details['parameter_value'] = parameter_value
        if valid_range:
            details['valid_range'] = valid_range
        
        # Generate user-friendly message
        if parameter_name and valid_range:
            user_msg = f"Invalid value for {parameter_name}: {parameter_value}. Expected: {valid_range}"
        else:
            user_msg = f"Validation error: {message}"
        
        # Recovery suggestions
        recovery = [
            "Check parameter values against requirements",
            "Verify IBC compliance constraints",
            "Review parameter documentation"
        ]
        
        super().__init__(message, details=details, user_message=user_msg, recovery_suggestions=recovery)


class AutoCADConnectionError(SpiralStairException):
    """
    Exception raised for AutoCAD connection and communication errors.
    
    Includes COM interface issues, connection timeouts, and AutoCAD crashes.
    """
    
    def __init__(self, message: str, connection_attempt: Optional[int] = None, 
                 autocad_version: Optional[str] = None, is_mock_mode: bool = False, **kwargs):
        """
        Initialize AutoCAD connection error.
        
        Args:
            message: Error message
            connection_attempt: Which connection attempt failed
            autocad_version: AutoCAD version if detected
            is_mock_mode: Whether mock mode was being used
            **kwargs: Additional base exception arguments
        """
        details = kwargs.get('details', {})
        if connection_attempt:
            details['connection_attempt'] = connection_attempt
        if autocad_version:
            details['autocad_version'] = autocad_version
        details['is_mock_mode'] = is_mock_mode
        
        # Generate user-friendly message
        if is_mock_mode:
            user_msg = f"Mock AutoCAD error: {message}"
        else:
            user_msg = f"AutoCAD connection failed: {message}"
        
        # Recovery suggestions
        recovery = [
            "Ensure AutoCAD 2025 is installed and running",
            "Check AutoCAD COM interface is enabled",
            "Try restarting AutoCAD",
            "Consider using mock mode for testing"
        ]
        
        super().__init__(message, details=details, user_message=user_msg, recovery_suggestions=recovery)


class GenerationError(SpiralStairException):
    """
    Exception raised during stair component generation.
    
    Includes geometry creation failures, constraint violations, and component-specific errors.
    """
    
    def __init__(self, message: str, component_name: Optional[str] = None, 
                 operation: Optional[str] = None, geometry_type: Optional[str] = None, **kwargs):
        """
        Initialize generation error.
        
        Args:
            message: Error message
            component_name: Name of component that failed
            operation: Specific operation that failed
            geometry_type: Type of geometry being created
            **kwargs: Additional base exception arguments
        """
        details = kwargs.get('details', {})
        if component_name:
            details['component_name'] = component_name
        if operation:
            details['operation'] = operation
        if geometry_type:
            details['geometry_type'] = geometry_type
        
        # Generate user-friendly message
        if component_name:
            user_msg = f"Failed to generate {component_name}: {message}"
        else:
            user_msg = f"Generation error: {message}"
        
        # Recovery suggestions
        recovery = [
            "Check parameter values for conflicts",
            "Verify AutoCAD is responsive",
            "Try generating components individually",
            "Review configuration for this component"
        ]
        
        super().__init__(message, details=details, user_message=user_msg, recovery_suggestions=recovery)


class UIError(SpiralStairException):
    """
    Exception raised for user interface specific issues.
    
    Includes widget creation failures, event handling errors, and UI state issues.
    """
    
    def __init__(self, message: str, widget_type: Optional[str] = None, 
                 operation: Optional[str] = None, ui_component: Optional[str] = None, **kwargs):
        """
        Initialize UI error.
        
        Args:
            message: Error message
            widget_type: Type of UI widget involved
            operation: UI operation that failed
            ui_component: Specific UI component (view, controller, model)
            **kwargs: Additional base exception arguments
        """
        details = kwargs.get('details', {})
        if widget_type:
            details['widget_type'] = widget_type
        if operation:
            details['operation'] = operation
        if ui_component:
            details['ui_component'] = ui_component
        
        # Generate user-friendly message
        user_msg = f"User interface error: {message}"
        
        # Recovery suggestions
        recovery = [
            "Try restarting the application",
            "Check if all UI dependencies are available",
            "Reset UI to default state"
        ]
        
        super().__init__(message, details=details, user_message=user_msg, recovery_suggestions=recovery)


class IBCComplianceError(ValidationError):
    """
    Exception raised for IBC building code compliance violations.
    
    Specialized validation error for building code requirements.
    """
    
    def __init__(self, message: str, code_section: Optional[str] = None, 
                 measured_value: Optional[float] = None, required_value: Optional[float] = None, **kwargs):
        """
        Initialize IBC compliance error.
        
        Args:
            message: Error message
            code_section: IBC code section violated
            measured_value: Actual measured value
            required_value: Required value per code
            **kwargs: Additional validation error arguments
        """
        details = kwargs.get('details', {})
        if code_section:
            details['ibc_code_section'] = code_section
        if measured_value is not None:
            details['measured_value'] = measured_value
        if required_value is not None:
            details['required_value'] = required_value
        
        # Generate user-friendly message
        if measured_value is not None and required_value is not None:
            user_msg = f"IBC code violation: {message}. Measured: {measured_value}, Required: {required_value}"
        else:
            user_msg = f"IBC code violation: {message}"
        
        # Recovery suggestions
        recovery = [
            "Adjust stair dimensions to meet IBC requirements",
            "Check walkline width (minimum 6.75 inches)",
            "Verify walk space clearance (minimum 26 inches)",
            "Consider different stair configuration"
        ]
        
        super().__init__(message, details=details, user_message=user_msg, 
                        recovery_suggestions=recovery, **kwargs)


class GeometryError(GenerationError):
    """
    Exception raised for geometric calculation errors.
    
    Specialized generation error for mathematical and geometric issues.
    """
    
    def __init__(self, message: str, calculation: Optional[str] = None, 
                 input_values: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize geometry error.
        
        Args:
            message: Error message
            calculation: Type of calculation that failed
            input_values: Input values that caused the error
            **kwargs: Additional generation error arguments
        """
        details = kwargs.get('details', {})
        if calculation:
            details['calculation'] = calculation
        if input_values:
            details['input_values'] = input_values
        
        # Generate user-friendly message
        user_msg = f"Geometry calculation error: {message}"
        
        # Recovery suggestions
        recovery = [
            "Check input parameters for mathematical validity",
            "Verify angles are within valid ranges",
            "Ensure dimensions are positive and reasonable",
            "Try different parameter combinations"
        ]
        
        super().__init__(message, details=details, user_message=user_msg, 
                        recovery_suggestions=recovery, **kwargs)


class FileOperationError(SpiralStairException):
    """
    Exception raised for file I/O operations.
    
    Includes read/write failures, permission issues, and file format errors.
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 operation: Optional[str] = None, permissions_issue: bool = False, **kwargs):
        """
        Initialize file operation error.
        
        Args:
            message: Error message
            file_path: Path to file that caused error
            operation: Type of file operation (read, write, create, delete)
            permissions_issue: Whether this is a permissions problem
            **kwargs: Additional base exception arguments
        """
        details = kwargs.get('details', {})
        if file_path:
            details['file_path'] = file_path
        if operation:
            details['operation'] = operation
        details['permissions_issue'] = permissions_issue
        
        # Store permissions_issue as an instance attribute
        self.permissions_issue = permissions_issue
        
        # Generate user-friendly message
        if permissions_issue:
            user_msg = f"Permission denied for file operation: {message}"
        else:
            user_msg = f"File operation failed: {message}"
        
        # Recovery suggestions
        recovery = [
            "Check file path exists and is accessible",
            "Verify write permissions for the directory",
            "Ensure file is not locked by another application",
            "Try a different file location"
        ]
        
        super().__init__(message, details=details, user_message=user_msg, recovery_suggestions=recovery)


class ComponentNotFoundError(SpiralStairException):
    """
    Exception raised when a required component is not found or registered.
    """
    
    def __init__(self, component_name: str, available_components: Optional[List[str]] = None, **kwargs):
        """
        Initialize component not found error.
        
        Args:
            component_name: Name of component that was not found
            available_components: List of available components
            **kwargs: Additional base exception arguments
        """
        message = f"Component '{component_name}' not found"
        details = {'component_name': component_name}
        if available_components:
            details['available_components'] = available_components
        
        user_msg = f"Required component '{component_name}' is not available"
        
        recovery = [
            "Check component is properly registered",
            "Verify component module is loaded",
            "Review component configuration"
        ]
        
        super().__init__(message, details=details, user_message=user_msg, recovery_suggestions=recovery)


# Exception mapping for automatic conversion from generic exceptions
EXCEPTION_MAPPING = {
    'FileNotFoundError': FileOperationError,
    'PermissionError': FileOperationError,
    'IOError': FileOperationError,
    'OSError': FileOperationError,
    'ValueError': ValidationError,
    'TypeError': ValidationError,
    'KeyError': ConfigurationError,
    'AttributeError': ConfigurationError
}


def convert_exception(exc: Exception, context: Optional[Dict[str, Any]] = None) -> SpiralStairException:
    """
    Convert a generic exception to a specific SpiralStairException.
    
    Args:
        exc: Original exception
        context: Additional context information
        
    Returns:
        Appropriate SpiralStairException subclass
    """
    exc_type = type(exc).__name__
    context = context or {}
    
    # Get appropriate exception class
    exception_class = EXCEPTION_MAPPING.get(exc_type, SpiralStairException)
    
    # Special handling for specific exception types
    if exc_type == 'FileNotFoundError':
        return FileOperationError(
            str(exc), 
            file_path=context.get('file_path'),
            operation='read',
            details=context
        )
    elif exc_type == 'PermissionError':
        return FileOperationError(
            str(exc),
            file_path=context.get('file_path'),
            permissions_issue=True,
            details=context
        )
    elif exc_type in ['ValueError', 'TypeError']:
        return ValidationError(
            str(exc),
            parameter_name=context.get('parameter_name'),
            parameter_value=context.get('parameter_value'),
            details=context
        )
    else:
        # Generic conversion
        return exception_class(str(exc), details=context)


def handle_exception_chain(exc: Exception) -> SpiralStairException:
    """
    Handle exception chaining to preserve original exception context.
    
    Args:
        exc: Exception to handle
        
    Returns:
        SpiralStairException with preserved chain
    """
    if isinstance(exc, SpiralStairException):
        return exc
    
    # Convert with chaining
    converted = convert_exception(exc)
    converted.__cause__ = exc
    return converted