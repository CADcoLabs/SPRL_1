"""
Centralized Logging Configuration for Spiral Stair Creator System.

This module provides enterprise-grade logging configuration with:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Console and rotating file output
- Structured log formatting
- Thread-safe operation
- Customizable log levels per module
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import threading


class StructuredFormatter(logging.Formatter):
    """Custom formatter that provides structured log output with context."""
    
    def __init__(self):
        super().__init__()
        
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured information."""
        # Create timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Get thread info
        thread_name = threading.current_thread().name
        
        # Format the basic message
        message = record.getMessage()
        
        # Add exception info if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        # Structured log format
        log_parts = [
            f"{timestamp}",
            f"[{record.levelname:8}]",
            f"[{record.name:20}]",
            f"[{thread_name:10}]",
            f"{message}"
        ]
        
        # Add extra context if available
        if hasattr(record, 'component'):
            log_parts.insert(-1, f"[{record.component}]")
        if hasattr(record, 'operation'):
            log_parts.insert(-1, f"[{record.operation}]")
        
        return " ".join(log_parts)


class SpiralStairLogger:
    """
    Centralized logger configuration for the Spiral Stair Creator System.
    
    Features:
    - Console output with colored levels (if supported)
    - Rotating file logs with size limits
    - Separate debug and error log files
    - Thread-safe operation
    - Module-specific log levels
    """
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls) -> 'SpiralStairLogger':
        """Singleton pattern for logger configuration."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger configuration (only once)."""
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._setup_logging()
                    self._initialized = True
    
    def _setup_logging(self):
        """Configure logging system with dual local/network logging."""
        import tempfile
        import socket
        import getpass
        
        # Get current user and machine info
        self.username = getpass.getuser()
        self.machine_name = socket.gethostname()
        
        # Setup local logs directory (in user's temp folder)
        self.local_log_dir = Path(tempfile.gettempdir()) / "SpiralStair_Logs"
        self.local_log_dir.mkdir(exist_ok=True)
        
        # Setup network logs directory (where the application is installed)
        project_root = Path(__file__).parent.parent
        self.network_log_dir = project_root / "logs"
        self.network_log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatters
        self.structured_formatter = StructuredFormatter()
        self.console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)-8s] %(name)-20s: %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_local_file_handlers()
        self._setup_network_usage_handler()
        
        # Log system initialization
        logger = logging.getLogger(__name__)
        logger.info("Dual logging system initialized")
        logger.info(f"Local log directory: {self.local_log_dir}")
        logger.info(f"Network log directory: {self.network_log_dir}")
        logger.info(f"User: {self.username}@{self.machine_name}")
    
    def _setup_console_handler(self):
        """Setup console handler with appropriate formatting."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.console_formatter)
        
        # Add to root logger
        logging.getLogger().addHandler(console_handler)
    
    def _setup_local_file_handlers(self):
        """Setup local file handlers on client machine."""
        # Local main application log (INFO and above)
        today = datetime.now().strftime('%Y%m%d')
        local_main_log = self.local_log_dir / f"spiral_stair_{today}.log"
        local_handler = logging.handlers.RotatingFileHandler(
            local_main_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        local_handler.setLevel(logging.INFO)
        local_handler.setFormatter(self.structured_formatter)
        logging.getLogger().addHandler(local_handler)
        
        # Local debug log (DEBUG and above)
        local_debug_log = self.local_log_dir / f"spiral_stair_debug_{today}.log"
        local_debug_handler = logging.handlers.RotatingFileHandler(
            local_debug_log,
            maxBytes=50*1024*1024,  # 50MB
            backupCount=3,
            encoding='utf-8'
        )
        local_debug_handler.setLevel(logging.DEBUG)
        local_debug_handler.setFormatter(self.structured_formatter)
        logging.getLogger().addHandler(local_debug_handler)
    
    def _setup_network_usage_handler(self):
        """Setup network usage tracking handler."""
        try:
            # Network usage log (INFO and above, includes user/machine info)
            today = datetime.now().strftime('%Y%m%d')
            network_usage_log = self.network_log_dir / f"usage_tracking_{today}.log"
            
            # Create custom formatter for usage tracking
            usage_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | {user}@{machine} | %(name)-20s | %(message)s'.format(
                    user=self.username, machine=self.machine_name
                ),
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            network_handler = logging.handlers.RotatingFileHandler(
                network_usage_log,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=10,
                encoding='utf-8'
            )
            network_handler.setLevel(logging.INFO)
            network_handler.setFormatter(usage_formatter)
            logging.getLogger().addHandler(network_handler)
            
        except (OSError, PermissionError) as e:
            # If network logging fails, log locally only
            local_logger = logging.getLogger(__name__)
            local_logger.warning(f"Network usage logging unavailable: {e}")
            local_logger.info("Continuing with local logging only")
    
    def get_logger(self, name: str, level: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance for a specific module.
        
        Args:
            name: Logger name (typically __name__)
            level: Optional log level override for this logger
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        
        if level:
            numeric_level = getattr(logging, level.upper(), logging.INFO)
            logger.setLevel(numeric_level)
        
        return logger
    
    def log_with_context(self, logger: logging.Logger, level: str, message: str, 
                        component: Optional[str] = None, operation: Optional[str] = None,
                        extra_data: Optional[Dict[str, Any]] = None):
        """
        Log a message with additional context information.
        
        Args:
            logger: Logger instance
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            component: Component name for context
            operation: Operation name for context
            extra_data: Additional data to include in log
        """
        # Prepare extra context
        extra = {}
        if component:
            extra['component'] = component
        if operation:
            extra['operation'] = operation
        
        # Add extra data to message if provided
        if extra_data:
            formatted_extra = ", ".join(f"{k}={v}" for k, v in extra_data.items())
            message = f"{message} | {formatted_extra}"
        
        # Log with appropriate level
        log_method = getattr(logger, level.lower())
        log_method(message, extra=extra)
    
    def set_module_level(self, module_name: str, level: str):
        """
        Set log level for a specific module.
        
        Args:
            module_name: Name of the module
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        logger = logging.getLogger(module_name)
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(numeric_level)
        
        # Log the change
        main_logger = logging.getLogger(__name__)
        main_logger.info(f"Set log level for {module_name} to {level}")
    
    def enable_debug_mode(self):
        """Enable debug mode for all loggers."""
        logging.getLogger().setLevel(logging.DEBUG)
        
        # Set console handler to debug as well
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(logging.DEBUG)
                break
        
        logger = logging.getLogger(__name__)
        logger.info("Debug mode enabled")
    
    def disable_debug_mode(self):
        """Disable debug mode, return to INFO level."""
        logging.getLogger().setLevel(logging.INFO)
        
        # Set console handler back to info
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(logging.INFO)
                break
        
        logger = logging.getLogger(__name__)
        logger.info("Debug mode disabled")
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Clean up old log files from both local and network directories.
        
        Args:
            days_to_keep: Number of days of logs to keep
        """
        import time
        
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        total_cleaned = 0
        
        # Clean local logs
        local_cleaned = 0
        for log_file in self.local_log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    local_cleaned += 1
                except OSError as e:
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to delete local log file {log_file}: {e}")
        
        # Clean network logs (only if accessible)
        network_cleaned = 0
        try:
            for log_file in self.network_log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    try:
                        log_file.unlink()
                        network_cleaned += 1
                    except OSError as e:
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Failed to delete network log file {log_file}: {e}")
        except (OSError, PermissionError):
            # Network directory not accessible, skip cleanup
            pass
        
        total_cleaned = local_cleaned + network_cleaned
        if total_cleaned > 0:
            logger = logging.getLogger(__name__)
            logger.info(f"Cleaned up {total_cleaned} old log files ({local_cleaned} local, {network_cleaned} network)")


# Global logger instance
_logger_instance = None

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
        level: Optional log level override
        
    Returns:
        Configured logger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SpiralStairLogger()
    
    return _logger_instance.get_logger(name, level)

def log_with_context(logger: logging.Logger, level: str, message: str, 
                    component: Optional[str] = None, operation: Optional[str] = None,
                    **kwargs):
    """
    Convenience function for logging with context.
    
    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        component: Component name
        operation: Operation name
        **kwargs: Additional context data
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SpiralStairLogger()
    
    _logger_instance.log_with_context(logger, level, message, component, operation, kwargs)

def enable_debug_mode():
    """Enable debug mode for all loggers."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SpiralStairLogger()
    _logger_instance.enable_debug_mode()

def disable_debug_mode():
    """Disable debug mode."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SpiralStairLogger()
    _logger_instance.disable_debug_mode()

def set_module_level(module_name: str, level: str):
    """Set log level for a specific module."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SpiralStairLogger()
    _logger_instance.set_module_level(module_name, level)

def cleanup_old_logs(days_to_keep: int = 30):
    """Clean up old log files."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SpiralStairLogger()
    _logger_instance.cleanup_old_logs(days_to_keep)