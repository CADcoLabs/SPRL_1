"""
Master Orchestrator for Spiral Stair Component Generation.

This module implements the MasterStairOrchestrator class that coordinates all stair
components with proper dependency resolution, progress tracking, and error handling.
Replaces the MockOrchestrator in the UI system with full functionality.
"""

import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future
import threading

from .base_component import BaseStairComponent
from .config_manager import ConfigManager
from .autocad_interface import AutoCADInterface, create_autocad_interface
from .logging_config import get_logger
from .exceptions import (
    SpiralStairException, 
    ComponentNotFoundError, 
    GenerationError, 
    ConfigurationError,
    AutoCADConnectionError,
    handle_exception_chain
)

# Import component modules
from modules.center_pole_module import CenterPoleModule
from modules.tread_module import TreadModule
from modules.landing_module import LandingModule
from modules.post_module import PostModule
from modules.picket_module import PicketModule
from modules.handrail_module import HandrailModule


class ComponentStatus(Enum):
    """Status enumeration for component generation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class GenerationPhase(Enum):
    """Generation phases for progress tracking."""
    INITIALIZATION = "initialization"
    VALIDATION = "validation"
    AUTOCAD_CONNECTION = "autocad_connection"
    COMPONENT_GENERATION = "component_generation"
    CLEANUP = "cleanup"
    COMPLETED = "completed"
    FAILED = "failed"


class ComponentInfo:
    """Information about a registered component."""
    
    def __init__(self, name: str, component_class: type, dependencies: List[str] = None,
                 config_key: str = None, required: bool = True):
        """
        Initialize component information.
        
        Args:
            name: Component name for display
            component_class: Component class to instantiate
            dependencies: List of component names this depends on
            config_key: Configuration key to check if component is enabled
            required: Whether component is required for successful generation
        """
        self.name = name
        self.component_class = component_class
        self.dependencies = dependencies or []
        self.config_key = config_key
        self.required = required
        self.status = ComponentStatus.PENDING
        self.instance: Optional[BaseStairComponent] = None
        self.error: Optional[Exception] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
    def is_enabled(self, config: Dict[str, Any]) -> bool:
        """Check if component is enabled in configuration."""
        if not self.config_key:
            return True
        
        # Navigate nested config keys
        keys = self.config_key.split('.')
        current = config
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return self.required  # Default to required status if config missing
            current = current[key]
        
        return bool(current)
    
    def get_duration(self) -> Optional[float]:
        """Get component generation duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class PostsComponentInfo(ComponentInfo):
    """Component info for Posts following zero-dependency principle."""
    
    def get_duration(self) -> Optional[float]:
        """Get component generation duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class MasterStairOrchestrator:
    """
    Master orchestrator that coordinates all stair component generation.
    
    Features:
    - Component dependency resolution
    - Sequential generation with proper order
    - Progress tracking and UI callbacks
    - Centralized error handling and recovery
    - Configuration validation across modules
    - Component status monitoring
    - Cleanup on failure
    - Mock mode support for testing
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the master orchestrator.
        
        Args:
            config_manager: Configuration manager instance (creates default if None)
        """
        self.logger = get_logger(__name__)
        self.config_manager = config_manager or ConfigManager()
        self.autocad_interface: Optional[AutoCADInterface] = None
        self.components: Dict[str, ComponentInfo] = {}
        self.generation_order: List[str] = []
        self.current_phase = GenerationPhase.INITIALIZATION
        self.is_generating = False
        self.generation_cancelled = False
        self.total_progress = 0.0
        self.generation_thread: Optional[threading.Thread] = None
        
        # Callbacks for UI integration
        self.progress_callback: Optional[Callable[[float], None]] = None
        self.status_callback: Optional[Callable[[str], None]] = None
        self.log_callback: Optional[Callable[[str], None]] = None
        
        # Statistics
        self.generation_stats = {
            'start_time': None,
            'end_time': None,
            'total_components': 0,
            'successful_components': 0,
            'failed_components': 0,
            'skipped_components': 0
        }
        
        self.logger.info("Master Stair Orchestrator initialized")
        self._register_components()
        
    def _register_components(self):
        """Register all stair components with their dependencies."""
        self.logger.debug("Registering stair components...")
        
        # Register components in dependency order
        component_definitions = [
            # Center Pole - no dependencies (OPTIONAL for modular architecture)
            ComponentInfo(
                name="Center Pole",
                component_class=CenterPoleModule,
                dependencies=[],
                config_key="component_settings.center_pole_enabled",
                required=False
            ),
            
            # Treads - independent generation (OPTIONAL for modular architecture)
            ComponentInfo(
                name="Treads",
                component_class=TreadModule,
                dependencies=[],  # Remove dependency to enable independent generation
                config_key="component_settings.treads_enabled",
                required=False
            ),
            
            # Landings - independent generation (OPTIONAL for modular architecture)
            ComponentInfo(
                name="Landings",
                component_class=LandingModule,
                dependencies=[],  # Remove dependency to enable independent generation
                config_key="component_settings.landings_enabled",
                required=False
            ),
            
            # Posts - independent generation (OPTIONAL for modular architecture)
            # Only enabled when horizontal pickets are selected
            PostsComponentInfo(
                name="Posts",
                component_class=PostModule,
                dependencies=[],  # Remove dependency to enable independent generation
                config_key="post_configuration.enabled",
                required=False
            ),
            
            # Pickets - independent generation (OPTIONAL for modular architecture)
            ComponentInfo(
                name="Pickets",
                component_class=PicketModule,
                dependencies=[],  # Remove dependency to enable independent generation
                config_key="picket_configuration.enabled",
                required=False
            ),
            
            # Handrails - independent generation (OPTIONAL for modular architecture)
            ComponentInfo(
                name="Handrails",
                component_class=HandrailModule,
                dependencies=[],  # Remove dependency to enable independent generation
                config_key="handrail_configuration.enabled",
                required=False
            )
        ]
        
        # Register components
        for comp_info in component_definitions:
            self.components[comp_info.name] = comp_info
            self.logger.debug(f"Registered component: {comp_info.name}")
        
        # Set structurally logical generation order (no dependencies needed due to modular architecture)
        self.generation_order = [
            "Center Pole",    # Foundation
            "Treads",         # Structure  
            "Landings",       # Platforms
            "Posts",          # Supports (only if horizontal pickets)
            "Handrails",      # Safety
            "Pickets"         # Finishing
        ]
        self.logger.info(f"Component generation order: {' -> '.join(self.generation_order)}")
        
    def _calculate_generation_order(self) -> List[str]:
        """Calculate the correct generation order based on dependencies."""
        ordered = []
        remaining = set(self.components.keys())
        
        while remaining:
            # Find components with no remaining dependencies
            ready = []
            for name in remaining:
                component = self.components[name]
                unmet_deps = [dep for dep in component.dependencies if dep in remaining]
                if not unmet_deps:
                    ready.append(name)
            
            if not ready:
                # Circular dependency detected
                raise ConfigurationError(
                    f"Circular dependency detected in components: {remaining}",
                    details={'remaining_components': list(remaining)}
                )
            
            # Add ready components to order and remove from remaining
            ready.sort()  # Ensure deterministic order
            ordered.extend(ready)
            remaining -= set(ready)
        
        return ordered
        
    def set_callbacks(self, progress_callback: Optional[Callable[[float], None]] = None,
                     status_callback: Optional[Callable[[str], None]] = None,
                     log_callback: Optional[Callable[[str], None]] = None):
        """
        Set UI callback functions for progress tracking.
        
        Args:
            progress_callback: Called with progress percentage (0-100)
            status_callback: Called with status message strings
            log_callback: Called with detailed log messages
        """
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.log_callback = log_callback
        self.logger.debug("UI callbacks configured")
        
    def _notify_progress(self, progress: float):
        """Notify progress callback if set."""
        if self.progress_callback:
            try:
                self.progress_callback(min(100.0, max(0.0, progress)))
            except Exception as e:
                self.logger.warning(f"Progress callback failed: {e}")
                
    def _notify_status(self, status: str):
        """Notify status callback if set."""
        if self.status_callback:
            try:
                self.status_callback(status)
            except Exception as e:
                self.logger.warning(f"Status callback failed: {e}")
                
    def _notify_log(self, message: str):
        """Notify log callback if set."""
        if self.log_callback:
            try:
                self.log_callback(message)
            except Exception as e:
                self.logger.warning(f"Log callback failed: {e}")
    
    def validate_configuration(self, config: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """
        Validate configuration across all enabled components.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        self.logger.debug("Validating configuration across all components...")
        errors = {}
        
        # Basic configuration validation
        try:
            is_valid, config_errors = self.config_manager.validate_config(config)
            if not is_valid:
                errors.update(config_errors)
        except Exception as e:
            errors['config_manager'] = str(e)
        
        # Component-specific validation
        for name, component_info in self.components.items():
            if not component_info.is_enabled(config):
                continue
                
            try:
                # Create temporary instance for validation
                temp_instance = component_info.component_class()
                temp_instance.validate_parameters(config)
                self.logger.debug(f"Component {name} validation passed")
            except Exception as e:
                errors[f'component_{name.lower().replace(" ", "_")}'] = str(e)
                self.logger.warning(f"Component {name} validation failed: {e}")
        
        is_valid = len(errors) == 0
        self.logger.info(f"Configuration validation {'passed' if is_valid else 'failed'}")
        return is_valid, errors
        
    def generate_stair(self, config: Dict[str, Any]) -> bool:
        """
        Generate complete spiral stair with all enabled components.
        
        Args:
            config: Validated configuration dictionary
            
        Returns:
            bool: True if generation successful, False otherwise
            
        Raises:
            GenerationError: If generation fails
        """
        if self.is_generating:
            raise GenerationError("Generation already in progress")
            
        self.logger.info("Starting spiral stair generation")
        self._notify_log("Starting spiral stair generation...")
        
        # Reset state
        self.is_generating = True
        self.generation_cancelled = False
        self.current_phase = GenerationPhase.INITIALIZATION
        self.total_progress = 0.0
        self.generation_stats = {
            'start_time': time.time(),
            'end_time': None,
            'total_components': 0,
            'successful_components': 0,
            'failed_components': 0,
            'skipped_components': 0
        }
        
        try:
            # Phase 1: Initialization and validation
            self._notify_status("Initializing generation...")
            self._notify_progress(5.0)
            self.current_phase = GenerationPhase.VALIDATION
            
            # Validate configuration
            is_valid, errors = self.validate_configuration(config)
            if not is_valid:
                error_msg = f"Configuration validation failed: {errors}"
                self.logger.error(error_msg)
                raise ConfigurationError(error_msg, validation_errors=errors)
            
            self._notify_log(f"Configuration validated: {len(config)} sections")
            self._notify_progress(10.0)
            
            # Phase 2: AutoCAD connection
            self.current_phase = GenerationPhase.AUTOCAD_CONNECTION
            self._notify_status("Connecting to AutoCAD...")
            
            success = self._initialize_autocad(config)
            if not success:
                return False
                
            self._notify_progress(15.0)
            
            # Phase 3: Component generation
            self.current_phase = GenerationPhase.COMPONENT_GENERATION
            return self._generate_components(config)
            
        except Exception as e:
            self.current_phase = GenerationPhase.FAILED
            self.logger.error(f"Stair generation failed: {e}", exc_info=True)
            self._notify_status(f"Generation failed: {str(e)}")
            self._notify_log(f"ERROR: {str(e)}")
            
            # Attempt cleanup
            self._cleanup_failed_generation()
            return False
            
        finally:
            self.is_generating = False
            self.generation_stats['end_time'] = time.time()
            
    def _initialize_autocad(self, config: Dict[str, Any]) -> bool:
        """Initialize AutoCAD interface based on configuration."""
        try:
            mock_mode = config.get('advanced_settings', {}).get('mock_mode', True)
            
            if mock_mode:
                self._notify_log("Initializing Mock AutoCAD interface...")
                self.logger.info("Using Mock AutoCAD interface for generation")
            else:
                self._notify_log("Connecting to AutoCAD...")
                self.logger.info("Connecting to real AutoCAD interface")
            
            # Create AutoCAD interface
            self.autocad_interface = create_autocad_interface()
            
            # Connect
            connected = self.autocad_interface.connect()
            if not connected:
                raise AutoCADConnectionError("Failed to connect to AutoCAD interface")
            
            self._notify_log("AutoCAD connection established")
            return True
            
        except Exception as e:
            self.logger.error(f"AutoCAD initialization failed: {e}")
            self._notify_log(f"AutoCAD connection failed: {str(e)}")
            raise
            
    def _generate_components(self, config: Dict[str, Any]) -> bool:
        """Generate all enabled components in dependency order."""
        enabled_components = [name for name in self.generation_order 
                            if self.components[name].is_enabled(config)]
        
        if not enabled_components:
            self._notify_log("No components enabled for generation")
            self.logger.warning("No components enabled")
            return True
        
        self.generation_stats['total_components'] = len(enabled_components)
        self._notify_log(f"Generating {len(enabled_components)} components...")
        
        # Calculate progress increment per component
        component_progress_size = 80.0 / len(enabled_components)  # 80% for components, 20% for setup/cleanup
        base_progress = 15.0  # Starting after setup
        
        for i, component_name in enumerate(enabled_components):
            if self.generation_cancelled:
                self.logger.info("Generation cancelled by user")
                return False
                
            component_info = self.components[component_name]
            
            try:
                # Check dependencies
                self._verify_dependencies(component_name, config)
                
                # Generate component
                success = self._generate_single_component(component_info, config)
                
                if success:
                    component_info.status = ComponentStatus.COMPLETED
                    self.generation_stats['successful_components'] += 1
                    self._notify_log(f"{component_name} generation completed successfully")
                else:
                    if component_info.required:
                        component_info.status = ComponentStatus.FAILED
                        self.generation_stats['failed_components'] += 1
                        raise GenerationError(f"Required component {component_name} failed")
                    else:
                        component_info.status = ComponentStatus.SKIPPED
                        self.generation_stats['skipped_components'] += 1
                        self._notify_log(f"Optional component {component_name} skipped due to error")
                
            except Exception as e:
                component_info.status = ComponentStatus.FAILED
                component_info.error = e
                self.generation_stats['failed_components'] += 1
                
                if component_info.required:
                    self.logger.error(f"Required component {component_name} failed: {e}")
                    raise
                else:
                    self.logger.warning(f"Optional component {component_name} failed: {e}")
                    self._notify_log(f"WARNING: {component_name} failed: {str(e)}")
            
            # Update progress
            progress = base_progress + (i + 1) * component_progress_size
            self._notify_progress(progress)
        
        # Phase 4: Cleanup and finalization
        self.current_phase = GenerationPhase.CLEANUP
        self._notify_status("Finalizing generation...")
        self._notify_progress(95.0)
        
        # Success!
        self.current_phase = GenerationPhase.COMPLETED
        self._notify_status("Stair generation completed successfully!")
        self._notify_log("All components generated successfully")
        self._notify_progress(100.0)
        
        # Log statistics
        total_time = self.generation_stats['end_time'] - self.generation_stats['start_time'] if self.generation_stats['end_time'] else 0
        self.logger.info(f"Generation completed in {total_time:.2f} seconds")
        self._notify_log(f"Generation completed in {total_time:.2f} seconds")
        
        # Collect actual measurements from generated components
        self.actual_specs = self._collect_actual_specifications(config)
        
        return True
        
    def _verify_dependencies(self, component_name: str, config: Dict[str, Any]):
        """Verify that all dependencies for a component have been successfully generated."""
        component_info = self.components[component_name]
        
        for dep_name in component_info.dependencies:
            dep_component = self.components.get(dep_name)
            if not dep_component:
                raise ComponentNotFoundError(dep_name, list(self.components.keys()))
            
            # Check if dependency was enabled and generated
            if dep_component.is_enabled(config):
                if dep_component.status != ComponentStatus.COMPLETED:
                    raise GenerationError(
                        f"Dependency {dep_name} not completed for {component_name}",
                        component_name=component_name,
                        details={'dependency': dep_name, 'status': dep_component.status.value}
                    )
        
    def _generate_single_component(self, component_info: ComponentInfo, config: Dict[str, Any]) -> bool:
        """Generate a single component."""
        self._notify_status(f"Generating {component_info.name}...")
        self.logger.info(f"Starting generation of {component_info.name}")
        
        component_info.start_time = time.time()
        component_info.status = ComponentStatus.IN_PROGRESS
        
        try:
            # Create component instance
            if not component_info.instance:
                component_info.instance = component_info.component_class()
            
            # Validate parameters
            component_info.instance.validate_parameters(config)
            
            # Generate geometry
            success = component_info.instance.generate_geometry(self.autocad_interface, config)
            
            component_info.end_time = time.time()
            duration = component_info.get_duration()
            
            if success:
                self.logger.info(f"{component_info.name} generated successfully in {duration:.2f}s")
                return True
            else:
                self.logger.warning(f"{component_info.name} generation returned False")
                return False
                
        except Exception as e:
            component_info.end_time = time.time()
            component_info.error = handle_exception_chain(e)
            self.logger.error(f"{component_info.name} generation failed: {e}", exc_info=True)
            
            # Attempt component cleanup
            if component_info.instance:
                try:
                    component_info.instance.cleanup(self.autocad_interface)
                except Exception as cleanup_error:
                    self.logger.warning(f"Cleanup failed for {component_info.name}: {cleanup_error}")
            
            raise
    
    def _cleanup_failed_generation(self):
        """Clean up partially generated components on failure."""
        self.logger.info("Cleaning up failed generation...")
        self._notify_status("Cleaning up...")
        
        for name, component_info in self.components.items():
            if component_info.instance and component_info.status == ComponentStatus.IN_PROGRESS:
                try:
                    component_info.instance.cleanup(self.autocad_interface)
                    self.logger.debug(f"Cleaned up {name}")
                except Exception as e:
                    self.logger.warning(f"Cleanup failed for {name}: {e}")
                    
        # Disconnect AutoCAD
        if self.autocad_interface:
            try:
                self.autocad_interface.disconnect()
            except Exception as e:
                self.logger.warning(f"AutoCAD disconnection failed: {e}")
                
    def cancel_generation(self):
        """Cancel ongoing generation."""
        if self.is_generating:
            self.logger.info("Generation cancellation requested")
            self.generation_cancelled = True
            self._notify_status("Cancelling generation...")
            self._notify_log("Generation cancelled by user")
            
    def get_component_status(self, component_name: str) -> Dict[str, Any]:
        """Get detailed status for a specific component."""
        if component_name not in self.components:
            raise ComponentNotFoundError(component_name, list(self.components.keys()))
            
        component_info = self.components[component_name]
        status = {
            'name': component_info.name,
            'status': component_info.status.value,
            'required': component_info.required,
            'dependencies': component_info.dependencies,
            'duration': component_info.get_duration(),
            'error': str(component_info.error) if component_info.error else None
        }
        
        if component_info.instance:
            status.update(component_info.instance.get_status())
            
        return status
        
    def get_generation_status(self) -> Dict[str, Any]:
        """Get overall generation status and statistics."""
        return {
            'is_generating': self.is_generating,
            'current_phase': self.current_phase.value,
            'progress': self.total_progress,
            'cancelled': self.generation_cancelled,
            'statistics': self.generation_stats.copy(),
            'components': {name: self.get_component_status(name) 
                         for name in self.components.keys()}
        }
        
    def get_available_components(self) -> List[str]:
        """Get list of all available component names."""
        return list(self.components.keys())
        
    def get_generation_order(self) -> List[str]:
        """Get the calculated generation order."""
        return self.generation_order.copy()
        
    def reset(self):
        """Reset orchestrator state for new generation."""
        self.logger.debug("Resetting orchestrator state")
        
        # Reset component states
        for component_info in self.components.values():
            component_info.status = ComponentStatus.PENDING
            component_info.instance = None
            component_info.error = None
            component_info.start_time = None
            component_info.end_time = None
            
        # Reset generation state
        self.current_phase = GenerationPhase.INITIALIZATION
        self.is_generating = False
        self.generation_cancelled = False
        self.total_progress = 0.0
        
        # Disconnect AutoCAD if connected
        if self.autocad_interface:
            try:
                self.autocad_interface.disconnect()
            except Exception as e:
                self.logger.warning(f"Error disconnecting AutoCAD during reset: {e}")
            finally:
                self.autocad_interface = None
                
    def _collect_actual_specifications(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect actual measurements from generated components.
        
        Args:
            config: Configuration used for generation
            
        Returns:
            Dict containing actual measurements from components
        """
        try:
            basic_params = config.get("basic_parameters", {})
            actual_specs = {
                # Basic parameters (from config)
                'center_pole_diameter': basic_params.get("center_pole_diameter", 5.563),
                'overall_height': basic_params.get("overall_height", 144.0),
                'outside_diameter': basic_params.get("outside_diameter", 72.0),
                'total_rotation': basic_params.get("total_rotation", 450.0),
            }
            
            # Collect actual measurements from component instances
            for component_name, component_info in self.components.items():
                if (component_info.status == ComponentStatus.COMPLETED and 
                    component_info.instance and 
                    hasattr(component_info.instance, 'get_geometry_info')):
                    
                    try:
                        geometry_info = component_info.instance.get_geometry_info()
                        
                        # Extract relevant measurements based on component type
                        if component_name == "Treads":
                            actual_specs.update({
                                'number_of_treads': geometry_info.get('tread_count', 16),
                                'riser_height': geometry_info.get('riser_height', 9.0),
                                'tread_angle': geometry_info.get('tread_angle', 30.0),
                            })
                            
                            # Calculate actual walkline width using TreadModule logic
                            import math
                            walkline_radius = (actual_specs['center_pole_diameter'] / 2) + 12.0
                            tread_angle_rad = math.radians(abs(geometry_info.get('tread_angle', 30.0)))
                            actual_specs['walkline_width'] = walkline_radius * tread_angle_rad
                            
                            # Calculate actual walk space (tread width minus handrail space)
                            # Formula: (outside_diameter - center_pole) / 2 - handrail_diameter
                            handrail_config = config.get('handrail_configuration', {})
                            handrail_diameter = handrail_config.get('diameter', 1.5)
                            actual_specs['walk_space'] = (actual_specs['outside_diameter'] - actual_specs['center_pole_diameter']) / 2 - handrail_diameter
                            
                        elif component_name == "Handrails":
                            # Add handrail-specific measurements if available
                            actual_specs.update({
                                'handrail_length': geometry_info.get('total_length', 0),
                                'handrail_height': geometry_info.get('height_above_tread', 36.0),
                            })
                            
                        elif component_name == "Pickets":
                            # Add picket-specific measurements if available
                            actual_specs.update({
                                'picket_count': geometry_info.get('total_pickets', 0),
                                'picket_spacing': geometry_info.get('actual_spacing', 0),
                            })
                            
                    except Exception as e:
                        self.logger.warning(f"Could not collect geometry info from {component_name}: {e}")
            
            self.logger.info(f"Collected actual specifications from {len(actual_specs)} measurements")
            return actual_specs
            
        except Exception as e:
            self.logger.error(f"Error collecting actual specifications: {e}")
            return {}
    
    def get_actual_specifications(self) -> Dict[str, Any]:
        """
        Get the collected actual specifications from the last generation.
        
        Returns:
            Dict containing actual measurements, or empty dict if none available
        """
        return getattr(self, 'actual_specs', {})