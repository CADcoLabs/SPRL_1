"""
Main UI application for Spiral Stair Generator.
Mock-first iterative development approach with complete Tkinter interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
import sys
from typing import Dict, Any, Optional

# Add parent directory to path so we can import core modules
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(parent_dir)
from core.config_manager import ConfigManager
from core.orchestrator import MasterStairOrchestrator


class MockOrchestrator:
    """Mock orchestrator for testing UI without AutoCAD dependencies."""
    
    def __init__(self):
        self.components = [
            "Center Pole",
            "Treads", 
            "Landings",
            "Posts",
            "Vertical Pickets", 
            "Horizontal Pickets",
            "Handrails"
        ]
        
    def generate_stair(self, config: Dict[str, Any], progress_callback=None, status_callback=None, log_callback=None):
        """
        Mock stair generation with realistic timing and progress updates.
        
        Args:
            config: Configuration dictionary
            progress_callback: Callback for progress updates (0-100)
            status_callback: Callback for status messages
            log_callback: Callback for detailed logging
        """
        if log_callback:
            log_callback("Starting spiral stair generation...")
            log_callback(f"Configuration: {len(config)} sections loaded")
            
        total_components = len(self.components)
        
        for i, component in enumerate(self.components):
            if status_callback:
                status_callback(f"Generating {component}...")
            if log_callback:
                log_callback(f"Initializing {component} module...")
                
            # Simulate component generation time (3-6 seconds total)
            component_time = 1.0  # 1 second per component
            steps = 10  # More frequent updates
            
            for step in range(steps):
                time.sleep(component_time / steps)  # 0.1 seconds per step
                
                # Calculate overall progress
                component_progress = (step + 1) / steps
                overall_progress = ((i + component_progress) / total_components) * 100
                
                if progress_callback:
                    progress_callback(overall_progress)
                    
                # Log detailed steps occasionally
                if log_callback and step % 5 == 0:
                    log_callback(f"{component}: {int(component_progress*100)}% complete")
            
            if log_callback:
                log_callback(f"{component} generation completed successfully")
                
            # Simulate occasional warnings for testing
            if component == "Vertical Pickets":
                vertical_pickets = config.get("vertical_picket_configuration", {})
                if vertical_pickets.get("enabled", False):
                    quantity = vertical_pickets.get("quantity", 3)
                    if log_callback:
                        log_callback(f"Generated {quantity} vertical pickets with IBC compliance checking")
            elif component == "Horizontal Pickets":
                horizontal_pickets = config.get("horizontal_picket_configuration", {})
                if horizontal_pickets.get("enabled", False):
                    levels = horizontal_pickets.get("rail_levels", 4)
                    if log_callback:
                        log_callback(f"Generated {levels}-level horizontal rail system")
        
        if status_callback:
            status_callback("Stair generation completed successfully!")
        if log_callback:
            log_callback("All components generated successfully")
            log_callback("Build process completed")
        if progress_callback:
            progress_callback(100)


class SpiralStairUI:
    """Main UI application for Spiral Stair Generator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Mullet's Aluminum Products - Spiral Stair Creator v4.0.1.b")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Try to set custom icon (if available)
        try:
            # You can replace this with a custom icon file path
            # self.root.iconbitmap('path/to/your/icon.ico')  
            pass
        except:
            pass  # Use default if no custom icon available
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.orchestrator = MasterStairOrchestrator(self.config_manager)
        self.current_config = self.config_manager.get_default_config()
        
        # UI State
        self.is_generating = False
        
        # Status variable for UI updates
        self.status_var = tk.StringVar(value="Ready")
        
        # Set up UI
        self.setup_ui()
        self.load_default_values()
        self.setup_keyboard_shortcuts()
        
        # Finalize UI setup (Posts tab visibility, etc.)
        self.complete_ui_setup()
        
    def setup_ui(self):
        """Create the main UI layout."""
        # Create main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Menu bar
        self.setup_menu()
        
        # Title
        title_label = ttk.Label(main_frame, text="Mullet's Aluminum Products - Spiral Stair Creator v4.0.1.b", 
                               font=("TkDefaultFont", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Tab notebook with wider tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # Configure notebook for wider tabs
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[20, 8])
        
        # Create tabs
        self.setup_basic_tab()
        self.setup_pickets_tab()
        self.setup_handrail_tab()
        # Posts are now inline in pickets tab
        self.setup_advanced_tab()
        self.setup_generate_tab()
        
        # Bottom section - no longer needed as Generate tab handles this
        # self.setup_bottom_section(main_frame)
        
        # Note: Progress bars are now integrated directly into tab content instead of being added dynamically
        
    def setup_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Configuration", command=self.new_config)
        file_menu.add_command(label="Load Configuration...", command=self.load_config)
        file_menu.add_command(label="Save Configuration...", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def setup_basic_tab(self):
        """Create Basic Parameters tab."""
        basic_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(basic_frame, text="  Basic Parameters  ")
        basic_frame.columnconfigure(0, weight=1)
        basic_frame.columnconfigure(1, weight=1)
        
        # Basic parameters group (left side)
        basic_group = ttk.LabelFrame(basic_frame, text="Basic Parameters", padding="15")
        basic_group.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10), pady=(0, 15))
        basic_group.columnconfigure(1, weight=1)
        
        # Center pole diameter
        ttk.Label(basic_group, text="Center Pole Diameter (inches):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.center_pole_var = tk.DoubleVar(value=5.56)
        center_pole_entry = ttk.Entry(basic_group, textvariable=self.center_pole_var, width=10, justify='center')
        center_pole_entry.grid(row=0, column=1, sticky=tk.W)
        center_pole_entry.bind('<KeyRelease>', self.validate_basic_parameters)
        
        # Overall height
        ttk.Label(basic_group, text="Overall Height (inches):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.height_var = tk.DoubleVar(value=144.0)
        height_entry = ttk.Entry(basic_group, textvariable=self.height_var, width=10, justify='center')
        height_entry.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        height_entry.bind('<KeyRelease>', self.on_height_change)
        
        # Outside diameter
        ttk.Label(basic_group, text="Outside Diameter (inches):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.outside_diameter_var = tk.DoubleVar(value=72.0)
        outside_diameter_entry = ttk.Entry(basic_group, textvariable=self.outside_diameter_var, width=10, justify='center')
        outside_diameter_entry.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        outside_diameter_entry.bind('<KeyRelease>', self.validate_basic_parameters)
        
        # Total rotation
        ttk.Label(basic_group, text="Total Rotation (degrees):").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.rotation_var = tk.DoubleVar(value=450.0)
        rotation_entry = ttk.Entry(basic_group, textvariable=self.rotation_var, width=10, justify='center')
        rotation_entry.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
        rotation_entry.bind('<KeyRelease>', self.validate_basic_parameters)
        
        # Direction
        ttk.Label(basic_group, text="Direction:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.direction_var = tk.BooleanVar(value=True)
        direction_frame = ttk.Frame(basic_group)
        direction_frame.grid(row=4, column=1, sticky=tk.W, pady=(5, 0))
        ttk.Radiobutton(direction_frame, text="Clockwise", variable=self.direction_var, value=True).pack(side=tk.LEFT)
        ttk.Radiobutton(direction_frame, text="Counter-clockwise", variable=self.direction_var, value=False).pack(side=tk.LEFT, padx=(10, 0))
        
        # Mid-landing controls
        ttk.Label(basic_group, text="Mid-Landing:").grid(row=5, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.mid_landing_enabled_var = tk.BooleanVar(value=False)
        mid_landing_frame = ttk.Frame(basic_group)
        mid_landing_frame.grid(row=5, column=1, sticky=tk.W, pady=(5, 0))
        
        self.mid_landing_checkbox = ttk.Checkbutton(mid_landing_frame, text="Enable", 
                                                   variable=self.mid_landing_enabled_var,
                                                   command=self.on_mid_landing_toggle)
        self.mid_landing_checkbox.pack(side=tk.LEFT)
        
        # Mid-landing position
        ttk.Label(basic_group, text="Mid-Landing Position:").grid(row=6, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.mid_landing_position_var = tk.IntVar(value=8)
        
        position_frame = ttk.Frame(basic_group)
        position_frame.grid(row=6, column=1, sticky=tk.W, pady=(5, 0))
        
        ttk.Label(position_frame, text="Tread #:").pack(side=tk.LEFT)
        self.mid_landing_position_entry = ttk.Entry(position_frame, textvariable=self.mid_landing_position_var, 
                                                   width=5, justify='center', state='disabled')
        self.mid_landing_position_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        self.mid_landing_info_label = ttk.Label(position_frame, text="(Required for heights > 151\")", 
                                               foreground='gray')
        self.mid_landing_info_label.pack(side=tk.LEFT)
        
        # Combined Parameter Validation and IBC Compliance Status
        validation_frame = ttk.Frame(basic_group)
        validation_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        validation_frame.columnconfigure(0, weight=1)
        
        # Status display (combines parameter validation and IBC compliance)
        self.basic_combined_status_var = tk.StringVar(value="Checking parameters...")
        self.basic_combined_status_label = ttk.Label(validation_frame, textvariable=self.basic_combined_status_var, 
                                                    foreground="blue", wraplength=400, justify=tk.LEFT)
        self.basic_combined_status_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # IBC ignore option moved to Advanced tab only
        self.basic_ibc_ignore = tk.BooleanVar(value=False)  # Keep variable for compatibility
        
        # Component selection (right side)
        components_group = ttk.LabelFrame(basic_frame, text="Components to Generate", padding="15")
        components_group.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), padx=(10, 0), pady=(0, 15))
        
        self.center_pole_enabled = tk.BooleanVar(value=True)
        self.treads_enabled = tk.BooleanVar(value=True)
        self.landings_enabled = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(components_group, text="Center Pole", variable=self.center_pole_enabled).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Checkbutton(components_group, text="Treads", variable=self.treads_enabled).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Checkbutton(components_group, text="Landings", variable=self.landings_enabled).grid(row=2, column=0, sticky=tk.W)
        
    def setup_pickets_tab(self):
        """Create Pickets configuration tab with inline Posts configuration."""
        pickets_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(pickets_frame, text="  Pickets  ")
        pickets_frame.columnconfigure(0, weight=1)
        pickets_frame.columnconfigure(1, weight=1)
        
        # Pickets group (left side)
        pickets_group = ttk.LabelFrame(pickets_frame, text="Picket Configuration", padding="15")
        pickets_group.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 15), padx=(0, 10))
        pickets_group.columnconfigure(1, weight=1)
        
        # Posts group (right side - initially hidden)
        self.posts_inline_group = ttk.LabelFrame(pickets_frame, text="Structural Posts Configuration", padding="15")
        self.posts_inline_group.columnconfigure(1, weight=1)
        
        # Enable pickets
        self.pickets_enabled = tk.BooleanVar(value=True)  # Default to True
        ttk.Checkbutton(pickets_group, text="Enable Pickets", variable=self.pickets_enabled,
                       command=self.toggle_pickets).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # Picket quantity control with auto-calculation
        quantity_label_frame = ttk.Frame(pickets_group)
        quantity_label_frame.grid(row=1, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))
        ttk.Label(quantity_label_frame, text="Quantity per Tread:").pack(side=tk.LEFT)
        ttk.Button(quantity_label_frame, text="Auto", command=self.auto_calculate_pickets, width=6, state='disabled').pack(side=tk.LEFT, padx=(5, 0))
        
        quantity_frame = ttk.Frame(pickets_group)
        quantity_frame.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        self.picket_quantity_var = tk.IntVar(value=12)
        self.picket_adjustment_var = tk.IntVar(value=0)  # -1, 0, or +1 adjustment
        self.picket_base_quantity_var = tk.IntVar(value=12)
        
        # Base quantity display
        ttk.Label(quantity_frame, text="Base:").pack(side=tk.LEFT)
        base_label = ttk.Label(quantity_frame, textvariable=self.picket_base_quantity_var, width=3, anchor='center')
        base_label.pack(side=tk.LEFT, padx=(5, 10))
        
        # Adjustment controls
        ttk.Label(quantity_frame, text="Adj:").pack(side=tk.LEFT)
        adjustment_frame = ttk.Frame(quantity_frame)
        adjustment_frame.pack(side=tk.LEFT, padx=(5, 10))
        
        self.adj_minus1 = ttk.Radiobutton(adjustment_frame, text="-1", variable=self.picket_adjustment_var, value=-1, 
                                          command=self.update_picket_quantity, state='disabled')
        self.adj_minus1.pack(side=tk.LEFT)
        self.adj_zero = ttk.Radiobutton(adjustment_frame, text="0", variable=self.picket_adjustment_var, value=0,
                                        command=self.update_picket_quantity, state='disabled')
        self.adj_zero.pack(side=tk.LEFT, padx=(5, 5))
        self.adj_plus1 = ttk.Radiobutton(adjustment_frame, text="+1", variable=self.picket_adjustment_var, value=1,
                                         command=self.update_picket_quantity, state='disabled')
        self.adj_plus1.pack(side=tk.LEFT)
        
        # No total display needed - we count per tread, typically 3-4 pickets
        
        # Store auto-calc button reference
        self.picket_auto_btn = quantity_label_frame.winfo_children()[1]
        
        # Style
        ttk.Label(pickets_group, text="Style:").grid(row=2, column=0, sticky=tk.W, padx=(0, 15), pady=(10, 0))
        self.picket_style_var = tk.StringVar(value="vertical")  # Default to vertical pickets
        style_combo = ttk.Combobox(pickets_group, textvariable=self.picket_style_var, 
                                  values=["vertical", "horizontal"], width=15, state='disabled')
        style_combo.grid(row=2, column=1, sticky=tk.W, pady=(10, 0))
        style_combo.bind('<<ComboboxSelected>>', self.on_picket_style_change)
        self.picket_style_combo = style_combo
        
        # Position (for vertical pickets)
        self.picket_position_label = ttk.Label(pickets_group, text="Position:")
        self.picket_position_label.grid(row=3, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))
        self.picket_position_var = tk.StringVar(value="under_handrail")
        position_combo = ttk.Combobox(pickets_group, textvariable=self.picket_position_var,
                                     values=["outside_diameter", "under_handrail", "custom_dimension"], width=15, state='disabled')
        position_combo.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
        self.picket_position_combo = position_combo
        
        # Custom dimension (when position is custom)
        ttk.Label(pickets_group, text="Custom Dimension:").grid(row=4, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))
        self.picket_custom_dim_var = tk.DoubleVar(value=0.0)
        self.picket_custom_entry = ttk.Entry(pickets_group, textvariable=self.picket_custom_dim_var, width=15, state='disabled', justify='center')
        self.picket_custom_entry.grid(row=4, column=1, sticky=tk.W, pady=(5, 0))
        
        # Material
        ttk.Label(pickets_group, text="Material:").grid(row=5, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))
        self.picket_material_var = tk.StringVar(value="aluminum")
        material_combo = ttk.Combobox(pickets_group, textvariable=self.picket_material_var,
                                     values=["aluminum", "steel", "wood", "composite"], width=15, state='disabled')
        material_combo.grid(row=5, column=1, sticky=tk.W, pady=(5, 0))
        self.picket_material_combo = material_combo
        
        # Shape selection
        shape_frame = ttk.Frame(pickets_group)
        shape_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        ttk.Label(shape_frame, text="Cross-Section:").grid(row=0, column=0, sticky=tk.W, padx=(0, 15))
        
        # Round diameter
        self.picket_shape_var = tk.StringVar(value="square")
        self.picket_round_radio = ttk.Radiobutton(shape_frame, text="Round - Diameter:", variable=self.picket_shape_var, value="round", 
                                                 command=self.toggle_picket_shape, state='disabled')
        self.picket_round_radio.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.picket_diameter_var = tk.DoubleVar(value=0.75)
        self.picket_diameter_entry = ttk.Entry(shape_frame, textvariable=self.picket_diameter_var, width=8, state='disabled', justify='center')
        self.picket_diameter_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        ttk.Label(shape_frame, text="inches").grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        # Square dimension
        self.picket_square_radio = ttk.Radiobutton(shape_frame, text="Square - Side:", variable=self.picket_shape_var, value="square",
                                                  command=self.toggle_picket_shape, state='disabled')
        self.picket_square_radio.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.picket_square_var = tk.DoubleVar(value=0.75)
        self.picket_square_entry = ttk.Entry(shape_frame, textvariable=self.picket_square_var, width=8, state='disabled', justify='center')
        self.picket_square_entry.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        ttk.Label(shape_frame, text="inches").grid(row=2, column=2, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        # Other (custom) dimension
        self.picket_other_radio = ttk.Radiobutton(shape_frame, text="Other (Custom):", variable=self.picket_shape_var, value="other",
                                                 command=self.toggle_picket_shape, state='disabled')
        self.picket_other_radio.grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.picket_other_var = tk.StringVar(value="Custom specification")
        self.picket_other_entry = ttk.Entry(shape_frame, textvariable=self.picket_other_var, width=15, state='disabled')
        self.picket_other_entry.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Store references for enable/disable (will be properly set after creation)
        self.picket_shape_radios = []
        
        # IBC compliance note
        ibc_note = ttk.Label(pickets_group, text="Note: IBC requires picket gap spacing ≤ 4.0 inches (sphere rule)", 
                           font=("TkDefaultFont", 9), foreground="blue", wraplength=500)
        ibc_note.grid(row=7, column=0, columnspan=2, pady=(15, 0))
        
        # IBC Compliance section for Pickets
        picket_ibc_group = ttk.LabelFrame(pickets_frame, text="IBC Compliance - Picket Spacing", padding="15")
        picket_ibc_group.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        picket_ibc_group.columnconfigure(0, weight=1)
        
        # IBC status display
        self.picket_ibc_status_var = tk.StringVar(value="Analyzing picket spacing...")
        self.picket_ibc_status_label = ttk.Label(picket_ibc_group, textvariable=self.picket_ibc_status_var, 
                                                foreground="blue", wraplength=600)
        self.picket_ibc_status_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # IBC ignore option moved to Advanced tab only
        self.picket_ibc_ignore = tk.BooleanVar(value=False)  # Keep variable for compatibility
        
        # Setup inline Posts configuration (right side)
        self.setup_posts_inline()
        
    def setup_posts_inline(self):
        """Create inline Posts configuration in Pickets tab."""
        # Enable posts
        self.posts_enabled = tk.BooleanVar(value=True)  # Default enabled for horizontal pickets
        ttk.Checkbutton(self.posts_inline_group, text="Enable Posts", variable=self.posts_enabled,
                       command=self.toggle_posts_inline).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Spacing
        ttk.Label(self.posts_inline_group, text="Spacing:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.post_spacing_var = tk.IntVar(value=1)
        spacing_frame = ttk.Frame(self.posts_inline_group)
        spacing_frame.grid(row=1, column=1, sticky=tk.W)
        self.post_spacing_radio1 = ttk.Radiobutton(spacing_frame, text="Every tread", variable=self.post_spacing_var, value=1)
        self.post_spacing_radio2 = ttk.Radiobutton(spacing_frame, text="Every 2nd", variable=self.post_spacing_var, value=2)
        self.post_spacing_radio3 = ttk.Radiobutton(spacing_frame, text="Every 3rd", variable=self.post_spacing_var, value=3)
        self.post_spacing_radio1.pack(side=tk.LEFT)
        self.post_spacing_radio2.pack(side=tk.LEFT, padx=(10, 0))
        self.post_spacing_radio3.pack(side=tk.LEFT, padx=(10, 0))
        
        # Diameter
        ttk.Label(self.posts_inline_group, text="Diameter (inches):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.post_diameter_var = tk.DoubleVar(value=2.0)
        self.post_diameter_entry = ttk.Entry(self.posts_inline_group, textvariable=self.post_diameter_var, width=10, justify='center')
        self.post_diameter_entry.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        # Material
        ttk.Label(self.posts_inline_group, text="Material:").grid(row=3, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))
        self.post_material_var = tk.StringVar(value="aluminum")
        self.post_material_combo = ttk.Combobox(self.posts_inline_group, textvariable=self.post_material_var,
                                               values=["aluminum", "steel", "wood", "composite"], width=15)
        self.post_material_combo.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
        
        # Position
        ttk.Label(self.posts_inline_group, text="Position:").grid(row=4, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))
        self.post_position_var = tk.StringVar(value="outer_edge")
        self.post_position_combo = ttk.Combobox(self.posts_inline_group, textvariable=self.post_position_var,
                                               values=["inner_edge", "outer_edge", "center"], width=15)
        self.post_position_combo.grid(row=4, column=1, sticky=tk.W, pady=(5, 0))
        
        # Position note
        position_note = ttk.Label(self.posts_inline_group, text="Position determines where posts are placed on each tread", 
                                font=("TkDefaultFont", 9), foreground="gray")
        position_note.grid(row=5, column=0, columnspan=2, pady=(5, 0))
        
    def setup_handrail_tab(self):
        """Create Handrail configuration tab."""
        handrail_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(handrail_frame, text="  Handrail System  ")
        handrail_frame.columnconfigure(0, weight=1)
        
        # Handrail group
        handrail_group = ttk.LabelFrame(handrail_frame, text="Handrail Configuration", padding="15")
        handrail_group.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        handrail_group.columnconfigure(1, weight=1)
        
        # Enable handrail
        self.handrail_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(handrail_group, text="Enable Handrail", variable=self.handrail_enabled,
                       command=self.toggle_handrail).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Height above tread
        ttk.Label(handrail_group, text="Height Above Tread (inches):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.handrail_height_var = tk.DoubleVar(value=36.0)
        self.handrail_height_entry = ttk.Entry(handrail_group, textvariable=self.handrail_height_var, width=10, justify='center')
        self.handrail_height_entry.grid(row=1, column=1, sticky=tk.W)
        
        # Diameter
        ttk.Label(handrail_group, text="Diameter (inches):").grid(row=2, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))
        self.handrail_diameter_var = tk.DoubleVar(value=1.5)  # Changed default to 1.5"
        self.handrail_diameter_entry = ttk.Entry(handrail_group, textvariable=self.handrail_diameter_var, width=15, justify='center')
        self.handrail_diameter_entry.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        # Custom offset from outside diameter
        ttk.Label(handrail_group, text="Custom Offset (inches):").grid(row=3, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))
        self.handrail_offset_var = tk.DoubleVar(value=0.0)  # Default 0.0 means use standard calculation
        self.handrail_offset_entry = ttk.Entry(handrail_group, textvariable=self.handrail_offset_var, width=15, justify='center')
        self.handrail_offset_entry.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
        
        # Material
        ttk.Label(handrail_group, text="Material:").grid(row=4, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))
        self.handrail_material_var = tk.StringVar(value="aluminum")  # Changed default to aluminum
        handrail_material_combo = ttk.Combobox(handrail_group, textvariable=self.handrail_material_var,
                                              values=["aluminum", "steel", "wood", "composite"], width=15)
        handrail_material_combo.grid(row=4, column=1, sticky=tk.W, pady=(5, 0))
        self.handrail_material_combo = handrail_material_combo
        
        # Continuous
        self.handrail_continuous = tk.BooleanVar(value=True)
        ttk.Checkbutton(handrail_group, text="Continuous Handrail", 
                       variable=self.handrail_continuous).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # End treatment
        ttk.Label(handrail_group, text="End Treatment:").grid(row=6, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.handrail_end_var = tk.StringVar(value="cap")
        end_combo = ttk.Combobox(handrail_group, textvariable=self.handrail_end_var,
                               values=["cap", "return", "extended"], width=12)
        end_combo.grid(row=6, column=1, sticky=tk.W, pady=(5, 0))
        self.handrail_end_combo = end_combo
        
        # IBC compliance note
        ibc_note = ttk.Label(handrail_group, text="Note: IBC requires handrail height 34-38 inches above tread nosing", 
                           font=("TkDefaultFont", 9), foreground="blue", wraplength=500)
        ibc_note.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        # IBC Compliance section for Handrail
        handrail_ibc_group = ttk.LabelFrame(handrail_frame, text="IBC Compliance - Handrail Height", padding="15")
        handrail_ibc_group.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        handrail_ibc_group.columnconfigure(0, weight=1)
        
        # IBC status display
        self.handrail_ibc_status_var = tk.StringVar(value="Checking handrail height compliance...")
        self.handrail_ibc_status_label = ttk.Label(handrail_ibc_group, textvariable=self.handrail_ibc_status_var, 
                                                  foreground="blue", wraplength=600)
        self.handrail_ibc_status_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # IBC ignore option moved to Advanced tab only
        self.handrail_ibc_ignore = tk.BooleanVar(value=False)  # Keep variable for compatibility
        
    def setup_posts_tab(self):
        """Create Posts configuration tab (initially hidden)."""
        self.posts_frame = ttk.Frame(self.notebook, padding="15")
        # Don't add to notebook initially - will be added when horizontal pickets selected
        self.posts_frame.columnconfigure(0, weight=1)
        self.posts_tab_added = False  # Track if tab is currently visible
        
        # Posts group
        posts_group = ttk.LabelFrame(self.posts_frame, text="Post Configuration", padding="15")
        posts_group.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        posts_group.columnconfigure(1, weight=1)
        
        # Enable posts
        self.posts_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(posts_group, text="Enable Posts", variable=self.posts_enabled,
                       command=self.toggle_posts).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Spacing
        ttk.Label(posts_group, text="Spacing:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.post_spacing_var = tk.IntVar(value=1)
        spacing_frame = ttk.Frame(posts_group)
        spacing_frame.grid(row=1, column=1, sticky=tk.W)
        self.post_spacing_radio1 = ttk.Radiobutton(spacing_frame, text="Every tread", variable=self.post_spacing_var, value=1, state='disabled')
        self.post_spacing_radio2 = ttk.Radiobutton(spacing_frame, text="Every 2nd", variable=self.post_spacing_var, value=2, state='disabled')
        self.post_spacing_radio3 = ttk.Radiobutton(spacing_frame, text="Every 3rd", variable=self.post_spacing_var, value=3, state='disabled')
        self.post_spacing_radio1.pack(side=tk.LEFT)
        self.post_spacing_radio2.pack(side=tk.LEFT, padx=(10, 0))
        self.post_spacing_radio3.pack(side=tk.LEFT, padx=(10, 0))
        
        # Diameter
        ttk.Label(posts_group, text="Diameter (inches):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.post_diameter_var = tk.DoubleVar(value=2.0)
        self.post_diameter_entry = ttk.Entry(posts_group, textvariable=self.post_diameter_var, width=10, state='disabled', justify='center')
        self.post_diameter_entry.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        # Material
        ttk.Label(posts_group, text="Material:").grid(row=3, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))
        self.post_material_var = tk.StringVar(value="aluminum")  # Changed default to aluminum
        self.post_material_combo = ttk.Combobox(posts_group, textvariable=self.post_material_var,
                                               values=["aluminum", "steel", "wood", "composite"], width=15, state='disabled')
        self.post_material_combo.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
        
        # Position
        ttk.Label(posts_group, text="Position on Tread:").grid(row=4, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))
        self.post_position_var = tk.StringVar(value="outer_edge")
        self.post_position_combo = ttk.Combobox(posts_group, textvariable=self.post_position_var,
                                               values=["Outer Edge (near handrail)", "Mid Tread (center)", "Inner Edge (near pole)"], width=25, state='disabled')
        self.post_position_combo.grid(row=4, column=1, sticky=tk.W, pady=(5, 0))
        
        # Position explanation
        position_note = ttk.Label(posts_group, text="Position determines where posts are placed on each tread", 
                                font=("TkDefaultFont", 9), foreground="gray")
        position_note.grid(row=5, column=0, columnspan=2, pady=(5, 0))
        
    def setup_advanced_tab(self):
        """Create Advanced settings tab."""
        advanced_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(advanced_frame, text="  Advanced Settings  ")
        advanced_frame.columnconfigure(0, weight=1)
        
        # IBC Compliance group (compact)
        ibc_group = ttk.LabelFrame(advanced_frame, text="IBC Compliance", padding="8")
        ibc_group.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        self.ibc_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(ibc_group, text="Enable IBC Compliance Checking", 
                       variable=self.ibc_enabled).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 3))
        
        self.educational_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(ibc_group, text="Educational Mode (Allow non-compliant configurations)", 
                       variable=self.educational_mode, command=self.on_educational_mode_change).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 3))
        
        # Regional code and reset on same row
        ttk.Label(ibc_group, text="Regional Code:").grid(row=2, column=0, sticky=tk.W, pady=(3, 0))
        self.regional_code_var = tk.StringVar(value="IBC_2021")
        regional_combo = ttk.Combobox(ibc_group, textvariable=self.regional_code_var,
                                     values=["IBC_2021", "IBC_2018", "IBC_2015", "Custom"], width=12)
        regional_combo.grid(row=2, column=1, sticky=tk.W, pady=(3, 0), padx=(5, 10))
        
        reset_button = ttk.Button(ibc_group, text="Reset All Defaults", 
                                 command=self.reset_ibc_defaults, width=15)
        reset_button.grid(row=2, column=2, sticky=tk.W, pady=(3, 0))
        
        # Add tooltip for clarity
        def show_reset_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = tk.Label(tooltip, text="Reset ALL settings in ALL tabs to defaults", 
                           background="lightyellow", relief="solid", borderwidth=1,
                           font=("TkDefaultFont", "9", "normal"))
            label.pack()
            tooltip.after(2000, tooltip.destroy)  # Auto-hide after 2 seconds
        
        def hide_reset_tooltip(event):
            pass  # Tooltip auto-hides
        
        reset_button.bind("<Enter>", show_reset_tooltip)
        reset_button.bind("<Leave>", hide_reset_tooltip)
        
        # System Settings group (compact)
        system_group = ttk.LabelFrame(advanced_frame, text="System Settings", padding="8")
        system_group.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        system_group.columnconfigure(2, weight=1)
        
        # Initialize mock mode based on environment variable
        current_mock_mode = os.environ.get('AUTOCAD_MOCK_MODE', 'false').lower() == 'true'
        self.mock_mode = tk.BooleanVar(value=current_mock_mode)
        ttk.Checkbutton(system_group, text="Mock Mode (Testing without AutoCAD)", 
                       variable=self.mock_mode, command=self.toggle_mock_mode).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Connection testing on one row
        ttk.Label(system_group, text="Test:").grid(row=1, column=0, sticky=tk.W, pady=(3, 0))
        self.test_mock_button = ttk.Button(system_group, text="Mock Mode", 
                                          command=self.test_mock_connection, width=12)
        self.test_mock_button.grid(row=1, column=1, sticky=tk.W, padx=(5, 5), pady=(3, 0))
        
        self.test_autocad_button = ttk.Button(system_group, text="AutoCAD", 
                                             command=self.test_autocad_connection, width=12, state='disabled')
        self.test_autocad_button.grid(row=1, column=2, sticky=tk.W, pady=(3, 0))
        
        # Connection status (using Entry for copyable text)
        self.connection_status_var = tk.StringVar(value="No connection test performed")
        self.connection_status_entry = ttk.Entry(system_group, textvariable=self.connection_status_var, 
                                                font=("TkDefaultFont", 9), state="readonly", width=50)
        self.connection_status_entry.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=(3, 0))
        
        # Timeout setting on same row as label
        ttk.Label(system_group, text="Timeout:").grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.timeout_var = tk.IntVar(value=120)
        timeout_entry = ttk.Entry(system_group, textvariable=self.timeout_var, width=8, justify='center')
        timeout_entry.grid(row=3, column=1, sticky=tk.W, pady=(5, 0), padx=(5, 5))
        ttk.Label(system_group, text="seconds").grid(row=3, column=2, sticky=tk.W, pady=(5, 0))
        
        # Initialize button states based on current mock mode (after all UI elements are created)
        self.toggle_mock_mode()
        
        # Generation Details group (expanded)
        details_group = ttk.LabelFrame(advanced_frame, text="Generation Details", padding="10")
        details_group.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        details_group.columnconfigure(0, weight=1)
        details_group.rowconfigure(1, weight=1)
        
        # Details header with controls
        details_header = ttk.Frame(details_group)
        details_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        details_header.columnconfigure(0, weight=1)
        
        ttk.Label(details_header, text="Interface Logging:", font=("TkDefaultFont", 10, "bold")).pack(side=tk.LEFT)
        
        # Show/Hide and Clear buttons
        self.advanced_details_visible = tk.BooleanVar(value=True)
        self.advanced_show_hide_btn = ttk.Button(details_header, text="Hide", command=self.toggle_advanced_details, width=8)
        self.advanced_show_hide_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(details_header, text="Clear", command=self.clear_advanced_details, width=8).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Details text area with scrollbar (expanded)
        text_frame = ttk.Frame(details_group)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.advanced_details_text = tk.Text(text_frame, height=12, width=80, wrap=tk.WORD,
                                           font=("Consolas", 10), background="#f8f8f8")
        self.advanced_details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for text area
        details_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.advanced_details_text.yview)
        details_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.advanced_details_text.config(yscrollcommand=details_scrollbar.set)
        
        # Initial content
        self.advanced_details_text.insert(tk.END, "Generation details will appear here when spiral stair generation begins...\n")
        
        # Make advanced frame expandable
        advanced_frame.rowconfigure(2, weight=1)
        
    def setup_generate_tab(self):
        """Create Generate tab with specification review and progress bar - optimized layout."""
        generate_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(generate_frame, text="  Generate  ")
        
        # Configure grid for two-column layout
        generate_frame.columnconfigure(0, weight=1)  # Left column (specs)
        generate_frame.columnconfigure(1, weight=1)  # Right column (progress/details)
        generate_frame.rowconfigure(0, weight=1)     # Main content row
        
        # Left Column: Specification Review
        left_frame = ttk.Frame(generate_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        review_group = ttk.LabelFrame(left_frame, text="Specification Review", padding="10")
        review_group.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        review_group.columnconfigure(0, weight=1)
        review_group.rowconfigure(0, weight=1)
        
        # Specification text (no scrolling needed with compact layout)
        review_text_frame = ttk.Frame(review_group)
        review_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        review_text_frame.columnconfigure(0, weight=1)
        review_text_frame.rowconfigure(0, weight=1)
        
        self.review_text = tk.Text(review_text_frame, height=16, width=50, wrap=tk.WORD,
                                  font=("TkDefaultFont", 8), state=tk.DISABLED)
        self.review_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        review_scrollbar = ttk.Scrollbar(review_text_frame, orient="vertical", command=self.review_text.yview)
        self.review_text.configure(yscrollcommand=review_scrollbar.set)
        review_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Refresh button
        refresh_button = ttk.Button(review_group, text="Refresh Specifications", 
                                   command=self.update_specification_review)
        refresh_button.grid(row=1, column=0, pady=(5, 0))
        
        # Right Column: Progress and Build Details
        right_frame = ttk.Frame(generate_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)  # Build details section expands
        
        # Progress Section (top of right column)
        progress_group = ttk.LabelFrame(right_frame, text="Generation Progress", padding="10")
        progress_group.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_group.columnconfigure(1, weight=1)
        
        # Configure colorful progress bar style
        self.setup_progress_bar_style()
        
        # Progress bar
        self.generate_progress_bar = ttk.Progressbar(progress_group, length=400, mode='determinate',
                                                    style="Sophisticated.Horizontal.TProgressbar")
        self.generate_progress_bar.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # Progress labels
        self.generate_progress_label = ttk.Label(progress_group, text="Ready to generate...", 
                                               font=("TkDefaultFont", 9), foreground="gray")
        self.generate_progress_label.grid(row=1, column=0, sticky=tk.W)
        
        self.generate_progress_percent = ttk.Label(progress_group, text="0%", 
                                                 font=("TkDefaultFont", 9, "bold"))
        self.generate_progress_percent.grid(row=1, column=2, sticky=tk.E)
        
        # Generate button
        self.generate_button = ttk.Button(progress_group, text="Generate Stair", 
                                         command=self.generate_stair, 
                                         style="Accent.TButton", width=18)
        self.generate_button.grid(row=2, column=1, pady=(10, 0))
        
        # Build Details Section (bottom of right column - expandable)
        details_group = ttk.LabelFrame(right_frame, text="Build Logging", padding="10")
        details_group.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        details_group.columnconfigure(0, weight=1)
        details_group.rowconfigure(0, weight=1)
        
        # Build details text area - larger since it has more space
        details_text_frame = ttk.Frame(details_group)
        details_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        details_text_frame.columnconfigure(0, weight=1)
        details_text_frame.rowconfigure(0, weight=1)
        
        self.generate_tab_details_text = tk.Text(details_text_frame, height=15, width=50, wrap=tk.WORD,
                                         font=("Courier", 8), state=tk.DISABLED)
        self.generate_tab_details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        details_scrollbar = ttk.Scrollbar(details_text_frame, orient="vertical", command=self.generate_tab_details_text.yview)
        self.generate_tab_details_text.configure(yscrollcommand=details_scrollbar.set)
        details_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Initialize with current specifications
        self.update_specification_review()
        
        # Initialize control states for default enabled components
        self.toggle_pickets()  # Ensure picket controls reflect default enabled state
        
        # Add test progress animation after 3 seconds to show colorful progress bar
        self.root.after(3000, self._test_progress_bar)
    
    def update_specification_review(self, actual_specs=None):
        """Update the specification review text with current settings.
        
        Args:
            actual_specs: Dict of actual measurements from generated components (optional)
        """
        self.review_text.config(state=tk.NORMAL)
        self.review_text.delete(1.0, tk.END)
        
        # Clear existing tags
        self.review_text.tag_delete("preliminary", "actual", "header")
        
        is_actual = actual_specs is not None
        
        # Configure text tags for color coding
        self.review_text.tag_configure("preliminary", foreground="#cc0000")  # Red for preliminary
        self.review_text.tag_configure("actual", foreground="#000000")       # Black for actual
        self.review_text.tag_configure("header", foreground="#0066cc", font=("TkDefaultFont", 10, "bold"))
        self.review_text.tag_configure("warning", foreground="#ff6600", font=("TkDefaultFont", 9, "italic"))
        
        # Header
        header_text = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        if is_actual:
            header_text += "ACTUAL SPECIFICATIONS - POST GENERATION\n"
        else:
            header_text += "PRELIMINARY SPECIFICATIONS - PRE GENERATION\n"
        header_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        self.review_text.insert(tk.END, header_text, "header")
        
        # Add status warning for preliminary specs
        if not is_actual:
            warning_text = "⚠ These are PRELIMINARY estimates based on configuration\n"
            warning_text += "⚠ Actual measurements will be displayed after generation\n\n"
            self.review_text.insert(tk.END, warning_text, "warning")
        
        # Get measurements (actual if available, otherwise calculate preliminary)
        if is_actual and actual_specs:
            # Use actual measurements from generated components
            rotation_degrees = actual_specs.get('total_rotation', self.rotation_var.get())
            overall_height = actual_specs.get('overall_height', self.height_var.get())
            outside_diameter = actual_specs.get('outside_diameter', self.outside_diameter_var.get())
            center_pole_diameter = actual_specs.get('center_pole_diameter', self.center_pole_var.get())
            number_of_treads = actual_specs.get('number_of_treads', 16)
            riser_height = actual_specs.get('riser_height', 9.0)
            tread_angle = actual_specs.get('tread_angle', 30.0)
            walkline_width = actual_specs.get('walkline_width', 7.7388)
            walk_space = actual_specs.get('walk_space', 32.47)  # Actual measured walk space
        else:
            # Calculate preliminary values using TreadModule logic
            rotation_degrees = self.rotation_var.get()
            overall_height = self.height_var.get()
            outside_diameter = self.outside_diameter_var.get()
            center_pole_diameter = self.center_pole_var.get()
            
            # Calculate number of treads using TreadModule formula
            import math
            number_of_treads = math.ceil(overall_height / 9.5)
            riser_height = overall_height / number_of_treads
            
            # Check for mid-landing (like in tread module)
            mid_landing_index = -1
            if overall_height > 151:
                mid_landing_index = round(number_of_treads / 2) - 1
            
            # Calculate tread angle based on mid-landing presence
            if mid_landing_index >= 0:
                # With mid-landing: subtract 90° for landing, distribute remaining rotation
                tread_angle = (rotation_degrees - 90) / (number_of_treads - 2)
            else:
                # No mid-landing: distribute full rotation among treads
                tread_angle = rotation_degrees / (number_of_treads - 1)
            
            # Calculate walkline width using TreadModule formula
            # Walkline radius is 12" from center pole edge
            walkline_radius = (center_pole_diameter / 2) + 12.0
            walkline_width = walkline_radius * abs(math.radians(tread_angle))
            
            # Preliminary walk space calculation - tread width minus handrail space
            # Formula: (outside_diameter - center_pole) / 2 - handrail_diameter
            handrail_diameter = self.handrail_diameter_var.get()
            walk_space = (outside_diameter - center_pole_diameter) / 2 - handrail_diameter
        
        # Main Specifications (in requested order) - using color-coded text
        self.review_text.insert(tk.END, "MAIN SPECIFICATIONS:\n", "header")
        self.review_text.insert(tk.END, "────────────────────────────────────────────────\n")
        
        # Determine tag for measurement values
        value_tag = "actual" if is_actual else "preliminary"
        
        measurements = [
            f"Center Pole Diameter: {center_pole_diameter:.3f}\"\n",
            f"Overall Height: {overall_height:.3f}\"\n", 
            f"Outside Diameter: {outside_diameter:.3f}\"\n",
            f"Total Rotation: {rotation_degrees:.1f}°\n",
            f"Number of Treads: {number_of_treads}\n",
            f"Riser Height: {riser_height:.3f}\"\n",
            f"Tread Angle: {tread_angle:.3f}°\n",
            f"Walkline Width: {walkline_width:.3f}\"\n",
            f"Walk Space: {walk_space:.2f}\"\n",
        ]
        
        for measurement in measurements:
            self.review_text.insert(tk.END, measurement, value_tag)
        
        # Configuration items (always black)
        direction_text = "Right Hand - Up" if self.direction_var.get() else "Left Hand - Up"
        config_items = [
            f"Mid-Landing: {'Yes' if self.landings_enabled.get() else 'No'}\n",
            f"Rotation Direction: {direction_text}\n\n"
        ]
        
        for item in config_items:
            self.review_text.insert(tk.END, item, "actual")
        
        # Components Status (always black - configuration info)
        enabled_components = []
        if self.center_pole_enabled.get(): enabled_components.append("Center Pole")
        if self.treads_enabled.get(): enabled_components.append("Treads")
        if self.landings_enabled.get(): enabled_components.append("Landings")
        if self.pickets_enabled.get():
            if self.picket_style_var.get() == "vertical":
                enabled_components.append("Vertical Pickets")
            elif self.picket_style_var.get() == "horizontal":
                enabled_components.append("Horizontal Pickets")
            else:
                enabled_components.append("Vertical Pickets")  # Default to vertical
        if self.handrail_enabled.get(): enabled_components.append("Handrail")
        if self.posts_enabled.get(): enabled_components.append("Posts")
        
        self.review_text.insert(tk.END, "ENABLED COMPONENTS:\n", "header")
        self.review_text.insert(tk.END, "────────────────────────────────────────────────\n")
        self.review_text.insert(tk.END, f"{', '.join(enabled_components) if enabled_components else 'None Selected'}\n\n", "actual")
        
        # Pickets Configuration (compact)
        if self.pickets_enabled.get():
            self.review_text.insert(tk.END, "PICKETS:\n", "header")
            self.review_text.insert(tk.END, "────────────────────────────────────────────────\n")
            self.review_text.insert(tk.END, f"Qty: {self.picket_quantity_var.get()} | Style: {self.picket_style_var.get()}\n", "actual")
            self.review_text.insert(tk.END, f"Position: {self.picket_position_var.get().title()}\n", "actual")
            self.review_text.insert(tk.END, f"Material: {self.picket_material_var.get()}\n", "actual")
            
            # Cross-section (compact)
            if self.picket_shape_var.get() == "round":
                self.review_text.insert(tk.END, f"Round: ⌀{self.picket_diameter_var.get():.2f}\"\n", "actual")
            elif self.picket_shape_var.get() == "square":
                self.review_text.insert(tk.END, f"Square: {self.picket_square_var.get():.2f}\" × {self.picket_square_var.get():.2f}\"\n", "actual")
            else:
                self.review_text.insert(tk.END, f"Other: {self.picket_other_var.get()}\n", "actual")
            self.review_text.insert(tk.END, "\n")
            
            # Posts (if horizontal pickets)
            if self.picket_position_var.get() == "horizontal" and hasattr(self, 'posts_enabled') and self.posts_enabled.get():
                self.review_text.insert(tk.END, "POSTS (for horizontal pickets):\n", "header")
                self.review_text.insert(tk.END, f"Spacing: {self.post_spacing_var.get()} | ⌀{self.post_diameter_var.get():.2f}\"\n", "actual")
                self.review_text.insert(tk.END, f"Material: {self.post_material_var.get()}\n\n", "actual")
        
        # Handrail Configuration (compact)
        if self.handrail_enabled.get():
            self.review_text.insert(tk.END, "HANDRAIL SYSTEM:\n", "header")
            self.review_text.insert(tk.END, "────────────────────────────────────────────────\n")
            self.review_text.insert(tk.END, f"Height: {self.handrail_height_var.get():.2f}\" | ⌀{self.handrail_diameter_var.get():.2f}\"\n", "actual")
            self.review_text.insert(tk.END, f"Material: {self.handrail_material_var.get()}\n", "actual")
            self.review_text.insert(tk.END, f"Continuous: {'Yes' if self.handrail_continuous.get() else 'No'}\n", "actual")
            self.review_text.insert(tk.END, f"End: {self.handrail_end_var.get()}\n\n", "actual")
        
        # Advanced Settings (compact)
        self.review_text.insert(tk.END, "ADVANCED:\n", "header")
        self.review_text.insert(tk.END, "────────────────────────────────────────────────\n")
        self.review_text.insert(tk.END, f"IBC: {'ON' if self.ibc_enabled.get() else 'OFF'}\n", "actual")
        if self.ibc_enabled.get():
            self.review_text.insert(tk.END, f"Educational: {'ON' if self.educational_mode.get() else 'OFF'}\n", "actual")
            self.review_text.insert(tk.END, f"Region: {self.regional_code_var.get()}\n", "actual")
        self.review_text.insert(tk.END, f"Mock: {'ON' if self.mock_mode.get() else 'OFF'}\n", "actual")
        self.review_text.insert(tk.END, f"Timeout: {self.timeout_var.get()}s\n\n", "actual")
        
        # Status indicator
        footer_text = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        if is_actual:
            footer_text += "✓ GENERATION COMPLETE - ACTUAL MEASUREMENTS\n"
        else:
            footer_text += "✓ READY TO GENERATE - PRELIMINARY ESTIMATES\n"
        footer_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        self.review_text.insert(tk.END, footer_text, "header")
        self.review_text.config(state=tk.DISABLED)
        
    def _test_progress_bar(self):
        """Test the progress bar with animation to show it's working and colorful."""
        if not hasattr(self, 'generate_progress_bar'):
            return
            
        def animate_progress(current=0):
            if current <= 100:
                self._update_generate_tab_progress(current, f"Testing progress bar... ({current}%)")
                self.root.after(50, lambda: animate_progress(current + 2))
            else:
                # Reset after test
                self.root.after(1000, lambda: self._update_generate_tab_progress(0, "Ready to generate..."))
        
        animate_progress()
        
    def setup_tab_progress_bars(self):
        """Add sophisticated progress bars to each tab above generate button area."""
        # Configure custom style for sophisticated progress bar
        self.setup_progress_bar_style()
        
        # Get all tab frames
        tab_frames = [
            getattr(self.notebook.nametowidget(self.notebook.tabs()[i]), 'master', None) 
            for i in range(len(self.notebook.tabs()))
        ]
        
        # Create progress components for each tab
        self.tab_progress_bars = {}
        self.tab_progress_labels = {}
        self.tab_progress_frames = {}
        
        for i, tab_id in enumerate(self.notebook.tabs()):
            tab_frame = self.notebook.nametowidget(tab_id)
            tab_name = self.notebook.tab(tab_id, 'text').strip()
            
            # Create progress frame
            progress_frame = ttk.Frame(tab_frame, padding="10")
            progress_frame.columnconfigure(1, weight=1)
            
            # Progress label
            progress_label = ttk.Label(progress_frame, text="Generating Spiral Stair...", 
                                     font=("TkDefaultFont", 10, "bold"))
            progress_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            
            # Progress percentage
            progress_percent = ttk.Label(progress_frame, text="0%", 
                                       font=("TkDefaultFont", 9))
            progress_percent.grid(row=0, column=2, sticky=tk.E)
            
            # Sophisticated progress bar
            progress_bar = ttk.Progressbar(progress_frame, 
                                         style="Sophisticated.Horizontal.TProgressbar",
                                         length=400, mode='determinate')
            progress_bar.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 10))
            
            # Status text
            status_label = ttk.Label(progress_frame, text="Ready to generate...", 
                                   font=("TkDefaultFont", 9), foreground="gray")
            status_label.grid(row=2, column=0, columnspan=3, sticky=tk.W)
            
            # Generate button for this tab
            generate_button = ttk.Button(progress_frame, text="Generate Stair", 
                                       command=self.generate_stair, 
                                       style="Accent.TButton", width=20)
            generate_button.grid(row=3, column=1, pady=(10, 0))
            
            # Store references
            self.tab_progress_frames[tab_name] = progress_frame
            self.tab_progress_bars[tab_name] = progress_bar
            self.tab_progress_labels[tab_name] = {
                'main': progress_label,
                'percent': progress_percent, 
                'status': status_label
            }
            
            # Position progress frame at bottom of each tab
            # Use a row number that puts progress bars right after existing content
            # Most tabs use rows 0-2, so use row 3 to be safe but visible
            progress_row = 3  
            
            # Configure the tab frame to show this row
            try:
                # Allow the tab frame to expand vertically to show the progress bar
                tab_frame.rowconfigure(progress_row, weight=0)  # Don't expand the progress bar row itself
                tab_frame.columnconfigure(0, weight=1)  # Allow horizontal expansion
                
                # Make sure lower-numbered rows don't consume all space
                for i in range(progress_row):
                    tab_frame.rowconfigure(i, weight=0)
                    
            except Exception as e:
                print(f"Grid configuration error for {tab_name}: {e}")
            
            progress_frame.grid(row=progress_row, column=0, columnspan=10, sticky=(tk.W, tk.E), 
                               pady=(20, 10), padx=10)
            
    def setup_progress_bar_style(self):
        """Configure sophisticated progress bar styling."""
        style = ttk.Style()
        
        # Create sophisticated progress bar style
        style.theme_use('clam')  # Use clam theme as base
        
        # Configure sophisticated progress bar
        style.configure("Sophisticated.Horizontal.TProgressbar",
                       background='#0078d4',  # Microsoft Blue
                       troughcolor='#e1e1e1',  # Light gray trough
                       borderwidth=1,
                       lightcolor='#0078d4',
                       darkcolor='#005a9e',
                       thickness=20)  # Control height through thickness
        
        # Add animation-ready gradient colors
        style.map("Sophisticated.Horizontal.TProgressbar",
                 background=[('active', '#106ebe'),  # Darker blue on hover
                            ('pressed', '#005a9e')])  # Even darker when pressed
                            
    def show_tab_progress_bars(self):
        """Show sophisticated progress bars on all tabs."""
        # Progress bars are now always visible, just make sure they show activity
        for tab_name, frame in self.tab_progress_frames.items():
            # Make sure the frame is visible (it should already be gridded)
            frame.grid()
            
    def hide_tab_progress_bars(self):
        """Hide sophisticated progress bars on all tabs."""
        # Reset progress bars to show "Ready" state instead of hiding completely
        for tab_name, frame in self.tab_progress_frames.items():
            # Keep visible but reset to ready state
            pass  # Progress bars stay visible
        
        # Reset all progress bars to 0 and ready state
        self.update_tab_progress_bars(0, "Ready to generate...")
            
    def update_tab_progress_bars(self, progress, status="Processing..."):
        """Update all tab progress bars with current progress."""
        for tab_name, bar in self.tab_progress_bars.items():
            bar['value'] = progress
            # Update percentage label
            self.tab_progress_labels[tab_name]['percent'].config(text=f"{int(progress)}%")
            # Update status
            self.tab_progress_labels[tab_name]['status'].config(text=status)
            
    def animate_progress_bar(self, target_progress, current_progress=0, step=2):
        """Animate progress bar with smooth transitions."""
        if current_progress < target_progress:
            self.update_tab_progress_bars(current_progress)
            self.root.after(50, lambda: self.animate_progress_bar(target_progress, current_progress + step, step))
        else:
            self.update_tab_progress_bars(target_progress)
        
    def setup_bottom_section(self, parent):
        """Create bottom section with progress bar, build details, and generate button."""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        bottom_frame.columnconfigure(0, weight=1)
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(bottom_frame, variable=self.progress_var, 
                                          maximum=100, length=600)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(bottom_frame, textvariable=self.status_var)
        
        # Build details section (initially hidden)
        details_frame = ttk.Frame(bottom_frame)
        details_frame.columnconfigure(0, weight=1)
        
        # Details header with buttons
        details_header = ttk.Frame(details_frame)
        details_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        details_header.columnconfigure(0, weight=1)
        
        ttk.Label(details_header, text="Build Logging:", font=("TkDefaultFont", 10, "bold")).pack(side=tk.LEFT)
        
        self.hide_details_button = ttk.Button(details_header, text="Hide Details", 
                                             command=self.hide_build_details, width=12)
        self.hide_details_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.clear_details_button = ttk.Button(details_header, text="Clear Details", 
                                              command=self.clear_build_details, width=12)
        self.clear_details_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Build details text widget
        details_text_frame = ttk.Frame(details_frame)
        details_text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        details_text_frame.columnconfigure(0, weight=1)
        details_text_frame.rowconfigure(0, weight=1)
        
        self.build_details_text = tk.Text(details_text_frame, height=8, wrap=tk.WORD, 
                                         font=("Consolas", 10), background="#f8f8f8")
        details_scrollbar = ttk.Scrollbar(details_text_frame, orient=tk.VERTICAL, 
                                         command=self.build_details_text.yview)
        self.build_details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.build_details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        details_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Store details frame reference
        self.details_frame = details_frame
        
        # Button frame
        button_frame = ttk.Frame(bottom_frame)
        button_frame.grid(row=3, column=0, pady=(15, 0))
        
        # Generate button
        self.generate_button = ttk.Button(button_frame, text="Generate Stair", 
                                         command=self.generate_stair, style="Accent.TButton", width=15)
        self.generate_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Note: Preview is now handled by Shift+Tab shortcut
        
    def load_default_values(self):
        """Load default values into UI components."""
        # Basic parameters already set in setup_basic_tab
        # Additional defaults are set during widget creation
        self.update_config_from_ui()
        
    def _sanitize_numeric_input(self, value, field_name):
        """
        Sanitize and validate numeric input to prevent injection attacks.

        Args:
            value: Raw input value
            field_name: Name of the field for error reporting

        Returns:
            float: Sanitized numeric value

        Raises:
            ValueError: If input is invalid or potentially malicious
        """
        if not value:
            raise ValueError(f"{field_name} cannot be empty")

        # Convert to string and strip whitespace
        value_str = str(value).strip()

        # Check for potentially malicious patterns
        dangerous_patterns = [
            ';', '--', '/*', '*/', 'xp_', 'sp_', 'exec', 'union',
            'select', 'insert', 'update', 'delete', 'drop', 'create',
            'script', 'javascript', 'vbscript', 'onload', 'onerror',
            '<', '>', '"', "'", '\\', '\n', '\r', '\t'
        ]

        value_lower = value_str.lower()
        for pattern in dangerous_patterns:
            if pattern in value_lower:
                raise ValueError(f"{field_name} contains potentially malicious content")

        # Check for extremely large numbers that could cause overflow
        if len(value_str) > 10:  # Reasonable limit for numeric inputs
            raise ValueError(f"{field_name} value is too long")

        try:
            # Convert to float
            numeric_value = float(value_str)

            # Check for special float values that could cause issues
            if not (numeric_value == numeric_value):  # NaN check
                raise ValueError(f"{field_name} cannot be NaN")
            if numeric_value in (float('inf'), float('-inf')):  # Infinity check
                raise ValueError(f"{field_name} cannot be infinite")

            # Check for extremely small or large values
            if abs(numeric_value) > 1e10:  # Maximum reasonable value
                raise ValueError(f"{field_name} value is too large")

            return numeric_value

        except (ValueError, OverflowError):
            raise ValueError(f"{field_name} must be a valid number")

    def _validate_security_constraints(self, center_pole, height, outside_diameter, rotation):
        """
        Validate security constraints to prevent resource exhaustion or other attacks.

        Args:
            center_pole, height, outside_diameter, rotation: Validated numeric inputs

        Returns:
            list: List of security-related error messages
        """
        errors = []

        # Check for zero or negative values that could cause division by zero
        if center_pole <= 0:
            errors.append("Center pole diameter must be positive")
        if height <= 0:
            errors.append("Height must be positive")
        if outside_diameter <= 0:
            errors.append("Outside diameter must be positive")
        if rotation <= 0:
            errors.append("Rotation must be positive")

        # Check for extremely small values that could cause precision issues
        if center_pole < 0.1:
            errors.append("Center pole diameter is too small (minimum 0.1 inches)")
        if height < 10:
            errors.append("Height is too small (minimum 10 inches)")
        if outside_diameter < 10:
            errors.append("Outside diameter is too small (minimum 10 inches)")
        if rotation < 10:
            errors.append("Rotation is too small (minimum 10 degrees)")

        # Check for relationships that could cause computational issues
        if center_pole >= outside_diameter:
            errors.append("Center pole diameter must be smaller than outside diameter")

        # Check for values that could cause memory or performance issues
        if height > 1000:  # Unreasonably tall structure
            errors.append("Height exceeds maximum safe limit (1000 inches)")
        if rotation > 3600:  # More than 10 full rotations
            errors.append("Rotation exceeds maximum safe limit (3600 degrees)")

        return errors

    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Bind Shift+Tab to preview configuration (network compatible)
        try:
            self.root.bind('<Shift-ISO_Left_Tab>', lambda e: self.preview_config())
        except:
            pass  # Skip if ISO_Left_Tab not supported
        self.root.bind('<Shift-Tab>', lambda e: self.preview_config())
        # Focus on root to enable keyboard shortcuts
        self.root.focus_set()
        
    def on_height_change(self, event=None):
        """Handle height changes to automatically manage mid-landing requirements."""
        try:
            height = self.height_var.get()
            
            # Auto-suggest mid-landing for heights > 151"
            if height > 151:
                self.mid_landing_info_label.config(text="(REQUIRED for heights > 151\")", foreground='red')
                
                # Auto-enable mid-landing if not already enabled
                if not self.mid_landing_enabled_var.get():
                    self.mid_landing_enabled_var.set(True)
                    self.on_mid_landing_toggle()
                    
                # Calculate suggested position (middle of stair)
                import math
                num_treads = math.ceil(height / 9.5)
                suggested_position = round(num_treads / 2)
                self.mid_landing_position_var.set(suggested_position)
                
            else:
                self.mid_landing_info_label.config(text="(Required for heights > 151\")", foreground='gray')
                
        except (ValueError, tk.TclError):
            # Handle invalid height values gracefully
            pass
            
        # Always validate parameters after height change
        self.validate_basic_parameters(event)
    
    def on_mid_landing_toggle(self):
        """Handle mid-landing enable/disable toggle."""
        enabled = self.mid_landing_enabled_var.get()
        
        # Enable/disable the position entry
        if enabled:
            self.mid_landing_position_entry.config(state='normal')
            
            # Set default position if not already set
            if self.mid_landing_position_var.get() <= 0:
                try:
                    height = self.height_var.get()
                    import math
                    num_treads = math.ceil(height / 9.5)
                    default_position = round(num_treads / 2)
                    self.mid_landing_position_var.set(default_position)
                except (ValueError, tk.TclError):
                    self.mid_landing_position_var.set(8)  # Safe default
        else:
            self.mid_landing_position_entry.config(state='disabled')
        
        # Trigger validation update
        self.validate_basic_parameters()

    def validate_basic_parameters(self, event=None):
        """Validate basic parameters and update status."""
        try:
            # Get current values with input sanitization and validation
            center_pole_raw = self.center_pole_var.get()
            height_raw = self.height_var.get()
            outside_diameter_raw = self.outside_diameter_var.get()
            rotation_raw = self.rotation_var.get()

            # Sanitize and validate inputs
            try:
                center_pole = self._sanitize_numeric_input(center_pole_raw, "Center pole diameter")
            except ValueError as e:
                raise ValueError(f"Center pole: {e}")

            try:
                height = self._sanitize_numeric_input(height_raw, "Height")
            except ValueError as e:
                raise ValueError(f"Height: {e}")

            try:
                outside_diameter = self._sanitize_numeric_input(outside_diameter_raw, "Outside diameter")
            except ValueError as e:
                raise ValueError(f"Outside diameter: {e}")

            try:
                rotation = self._sanitize_numeric_input(rotation_raw, "Rotation")
            except ValueError as e:
                raise ValueError(f"Rotation: {e}")

            # Basic range validation with security bounds
            errors = []
            if center_pole < 1.0 or center_pole > 24.0:
                errors.append("Center pole diameter must be 1.0-24.0 inches")
            if height < 60.0 or height > 240.0:
                errors.append("Height must be 60-240 inches")
            if outside_diameter < 36.0 or outside_diameter > 120.0:
                errors.append("Outside diameter must be 36-120 inches")
            if rotation < 90.0 or rotation > 720.0:
                errors.append("Rotation must be 90-720 degrees")

            # Security validation: Check for potentially malicious values
            security_errors = self._validate_security_constraints(center_pole, height, outside_diameter, rotation)
            errors.extend(security_errors)

            # Combine parameter validation and IBC compliance
            self.update_combined_basic_status(center_pole, height, outside_diameter, rotation, errors)

        except ValueError as e:
            self.basic_combined_status_var.set(f"Input validation error: {str(e)}")
            self.basic_combined_status_label.config(foreground="red")
        except tk.TclError:
            self.basic_combined_status_var.set("Invalid numeric values entered - please check your input")
            self.basic_combined_status_label.config(foreground="red")
    
    def toggle_pickets(self):
        """Toggle pickets configuration controls."""
        state = 'normal' if self.pickets_enabled.get() else 'disabled'
        
        # Update all picket controls
        if hasattr(self, 'picket_style_combo'):
            self.picket_style_combo.config(state=state)
        if hasattr(self, 'picket_material_combo'):
            self.picket_material_combo.config(state=state)
        if hasattr(self, 'picket_position_combo'):
            self.picket_position_combo.config(state=state)
        if hasattr(self, 'picket_custom_entry'):
            self.picket_custom_entry.config(state=state)
                
        # Update quantity controls
        if hasattr(self, 'picket_auto_btn'):
            self.picket_auto_btn.config(state=state)
        if hasattr(self, 'adj_minus1'):
            self.adj_minus1.config(state=state)
            self.adj_zero.config(state=state)
            self.adj_plus1.config(state=state)
            
        # Update shape radio buttons
        if hasattr(self, 'picket_round_radio'):
            self.picket_round_radio.config(state=state)
            self.picket_square_radio.config(state=state)
            self.picket_other_radio.config(state=state)
            
        # Handle shape-specific entry controls - ensure proper state is set
        self.toggle_picket_shape()
            
        # Update spacing calculation
        self.validate_picket_spacing()
        
    def toggle_handrail(self):
        """Toggle handrail configuration controls."""
        state = 'normal' if self.handrail_enabled.get() else 'disabled'
        self.handrail_height_entry.config(state=state)
        self.handrail_diameter_entry.config(state=state)
        self.handrail_offset_entry.config(state=state)
        self.handrail_material_combo.config(state=state)
        self.handrail_end_combo.config(state=state)
        
    def toggle_posts(self):
        """Toggle posts configuration controls."""
        state = 'normal' if self.posts_enabled.get() else 'disabled'
        self.post_spacing_radio1.config(state=state)
        self.post_spacing_radio2.config(state=state)
        self.post_spacing_radio3.config(state=state)
        self.post_diameter_entry.config(state=state)
        self.post_material_combo.config(state=state)
        self.post_position_combo.config(state=state)
        
    def update_config_from_ui(self):
        """Update configuration dictionary from UI values with input validation."""
        try:
            # Validate and sanitize all numeric inputs
            center_pole = self._sanitize_numeric_input(self.center_pole_var.get(), "Center pole diameter")
            height = self._sanitize_numeric_input(self.height_var.get(), "Height")
            outside_diameter = self._sanitize_numeric_input(self.outside_diameter_var.get(), "Outside diameter")
            rotation = self._sanitize_numeric_input(self.rotation_var.get(), "Rotation")

            # Additional security validation
            security_errors = self._validate_security_constraints(center_pole, height, outside_diameter, rotation)
            if security_errors:
                raise ValueError("Security validation failed: " + "; ".join(security_errors))

            self.current_config = {
                "basic_parameters": {
                    "center_pole_diameter": center_pole,
                    "overall_height": height,
                    "outside_diameter": outside_diameter,
                    "total_rotation": rotation,
                    "is_clockwise": self.direction_var.get(),
                    "mid_landing_enabled": self.mid_landing_enabled_var.get(),
                    "mid_landing_tread_index": self.mid_landing_position_var.get() - 1 if self.mid_landing_enabled_var.get() else -1
                },
                "compliance_settings": {
                    "ibc_compliance_enabled": self.ibc_enabled.get(),
                    "educational_mode": self.educational_mode.get(),
                    "regional_code": self.regional_code_var.get()
                },
                "component_settings": {
                    "center_pole_enabled": self.center_pole_enabled.get(),
                    "treads_enabled": self.treads_enabled.get(),
                    "landings_enabled": self.landings_enabled.get()
                },
                "post_configuration": {
                    "enabled": self.posts_enabled.get(),
                    "spacing": self.post_spacing_var.get(),
                    "diameter": self.post_diameter_var.get(),
                    "material": self.post_material_var.get(),
                    "position": self.post_position_var.get()
                },
                "handrail_configuration": {
                    "enabled": self.handrail_enabled.get(),
                    "height_above_tread": self.handrail_height_var.get(),
                    "diameter": self.handrail_diameter_var.get(),
                    "material": self.handrail_material_var.get(),
                    "continuous": self.handrail_continuous.get(),
                    "end_treatment": self.handrail_end_var.get(),
                    "custom_offset": self.handrail_offset_var.get(),
                    "brackets": {
                        "enabled": True,
                        "spacing_inches": 24.0,
                        "bracket_type": "post_mount"
                    }
                },
                "vertical_picket_configuration": {
                    "enabled": self.pickets_enabled.get() and self.picket_style_var.get() == "vertical",
                    "spacing_inches": 3.5,  # Use default for now
                    "material": self.picket_material_var.get(),
                    "diameter": self.picket_diameter_var.get(),
                    "quantity": 3,
                    "position": "outer"
                },
                "horizontal_picket_configuration": {
                    "enabled": self.pickets_enabled.get() and self.picket_style_var.get() == "horizontal",
                    "rail_material": self.picket_material_var.get(),
                    "rail_profile": "square_1x1",
                    "rail_levels": 4,
                    "level_distribution": "even",
                    "mounting_system": "bracket_mount",
                    "bracket_material": self.picket_material_var.get(),
                    "connection_type": "post_mount",
                    "galvanic_isolation": True,
                    "rail_length_max": 72.0,
                    "deflection_limit": 0.25,
                    "custom_levels": []
                },
                "advanced_settings": {
                    "mock_mode": self.mock_mode.get(),
                    "generation_timeout": self.timeout_var.get()
                }
            }
        except tk.TclError as e:
            messagebox.showerror("Configuration Error", f"Invalid values in configuration: {e}")
            
    def preview_config(self):
        """Show configuration preview dialog."""
        self.update_config_from_ui()
        
        # Validate configuration
        is_valid, errors = self.config_manager.validate_config(self.current_config)
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Configuration Preview")
        preview_window.geometry("500x400")
        preview_window.resizable(True, True)
        
        # Text widget for configuration display
        text_widget = tk.Text(preview_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(preview_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        preview_window.columnconfigure(0, weight=1)
        preview_window.rowconfigure(0, weight=1)
        
        # Display configuration
        import json
        config_text = json.dumps(self.current_config, indent=2)
        text_widget.insert(tk.END, "CONFIGURATION PREVIEW\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        
        if not is_valid:
            text_widget.insert(tk.END, "❌ VALIDATION ERRORS:\n")
            for field, error in errors.items():
                text_widget.insert(tk.END, f"  {field}: {error}\n")
            text_widget.insert(tk.END, "\n")
        else:
            text_widget.insert(tk.END, "✅ Configuration is valid\n\n")
            
        text_widget.insert(tk.END, config_text)
        text_widget.config(state=tk.DISABLED)
        
    def generate_stair(self):
        """Generate stair with progress tracking."""
        if self.is_generating:
            messagebox.showwarning("Generation In Progress", "Stair generation is already in progress.")
            return
            
        # Update configuration from UI
        self.update_config_from_ui()
        
        # Validate configuration
        is_valid, errors = self.config_manager.validate_config(self.current_config)
        if not is_valid:
            error_text = "\n".join([f"{field}: {error}" for field, error in errors.items()])
            messagebox.showerror("Configuration Error", f"Configuration validation failed:\n\n{error_text}")
            return
            
        # Start generation in thread
        self.is_generating = True
        self.generate_button.config(state='disabled', text="Generating...")
        
        # Progress is now shown on the Generate tab
        
        # Progress bars are now integrated into individual tabs
        
        # Start generation thread
        generation_thread = threading.Thread(target=self._generate_stair_thread)
        generation_thread.daemon = True
        generation_thread.start()
        
    def _generate_stair_thread(self):
        """Thread function for stair generation."""
        try:
            # Set up callbacks for progress, status, and logging
            self.orchestrator.set_callbacks(
                progress_callback=self._update_progress,
                status_callback=self._update_status,
                log_callback=self._log_build_message
            )
            
            success = self.orchestrator.generate_stair(self.current_config)
            
            if not success:
                raise Exception("Orchestrator returned False")
            
            # Generation completed
            self.root.after(0, self._generation_complete, True, "Stair generation completed successfully!")
            
        except Exception as e:
            self.root.after(0, self._generation_complete, False, f"Generation failed: {str(e)}")
            
    def _log_build_message(self, message):
        """Thread-safe logging to build details."""
        self.root.after(0, lambda: self.log_build_message(message))
            
    def _update_progress(self, progress):
        """Update progress bar from thread."""
        # Update the generate tab progress bar
        component_num = max(1, min(6, int(progress/16.67) + 1))  # 6 components, ~16.67% each
        status_text = f"Generating component {component_num} of 6... ({int(progress)}%)"
        
        # Store current progress for status updates
        self.current_progress = progress
        
        if hasattr(self, 'generate_progress_bar'):
            self.root.after(0, lambda: self._update_generate_tab_progress(progress, status_text))
    
    def _update_status(self, status):
        """Update status text from thread."""
        # Update the generate tab progress bar with status
        if hasattr(self, 'generate_progress_bar'):
            # Get current progress or use 0
            current_progress = getattr(self, 'current_progress', 0)
            self.root.after(0, lambda: self._update_generate_tab_progress(current_progress, status))
            
    def _update_generate_tab_progress(self, progress, status_text):
        """Update the generate tab progress bar."""
        if hasattr(self, 'generate_progress_bar'):
            self.generate_progress_bar['value'] = progress
            self.generate_progress_label.config(text=status_text)
            self.generate_progress_percent.config(text=f"{int(progress)}%")
        
    def _update_status(self, status):
        """Update status label from thread."""
        self.root.after(0, lambda: self.status_var.set(status))
        # The progress callback handles tab progress bar updates
        
    def _generation_complete(self, success, message):
        """Handle generation completion."""
        self.is_generating = False
        self.generate_button.config(state='normal', text="Generate Stair")
        
        # Progress bar is on Generate tab - no need to hide
        
        # Update generate tab progress bar
        if success:
            if hasattr(self, 'generate_progress_bar'):
                self._update_generate_tab_progress(100, "Generation completed!")
                
            # Update specification review with actual measurements
            actual_specs = self.orchestrator.get_actual_specifications()
            if actual_specs:
                self.update_specification_review(actual_specs=actual_specs)
        else:
            if hasattr(self, 'generate_progress_bar'):
                self._update_generate_tab_progress(0, "Generation failed!")
        
        # Show result
        if success:
            messagebox.showinfo("Generation Complete", message)
        else:
            messagebox.showerror("Generation Failed", message)
            
        # Reset status (with safety checks)
        if hasattr(self, 'status_var'):
            self.status_var.set("Ready")
        if hasattr(self, 'progress_var'):
            self.progress_var.set(0)
        
    def new_config(self):
        """Create new configuration."""
        if messagebox.askyesno("New Configuration", "Reset all settings to defaults?"):
            self.current_config = self.config_manager.get_default_config()
            self.load_config_to_ui()
            
    def load_config(self):
        """Load configuration from file."""
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.current_config = self.config_manager.load_config(filename)
                self.load_config_to_ui()
                messagebox.showinfo("Success", "Configuration loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration:\n{str(e)}")
                
    def save_config(self):
        """Save configuration to file."""
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.update_config_from_ui()
                success = self.config_manager.save_config(self.current_config, filename)
                if success:
                    messagebox.showinfo("Success", "Configuration saved successfully!")
                else:
                    messagebox.showerror("Error", "Failed to save configuration")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")
                
    def load_config_to_ui(self):
        """Load configuration dictionary into UI controls."""
        config = self.current_config
        
        # Basic parameters
        basic = config.get("basic_parameters", {})
        self.center_pole_var.set(basic.get("center_pole_diameter", 5.56))
        self.height_var.set(basic.get("overall_height", 144.0))
        self.outside_diameter_var.set(basic.get("outside_diameter", 72.0))
        self.rotation_var.set(basic.get("total_rotation", 450.0))
        self.direction_var.set(basic.get("is_clockwise", True))
        
        # Mid-landing parameters
        self.mid_landing_enabled_var.set(basic.get("mid_landing_enabled", False))
        mid_landing_index = basic.get("mid_landing_tread_index", -1)
        self.mid_landing_position_var.set(mid_landing_index + 1 if mid_landing_index >= 0 else 8)
        self.on_mid_landing_toggle()  # Update UI state
        
        # Component settings
        components = config.get("component_settings", {})
        self.center_pole_enabled.set(components.get("center_pole_enabled", True))
        self.treads_enabled.set(components.get("treads_enabled", True))
        self.landings_enabled.set(components.get("landings_enabled", True))
        
        # Compliance settings
        compliance = config.get("compliance_settings", {})
        self.ibc_enabled.set(compliance.get("ibc_compliance_enabled", True))
        self.educational_mode.set(compliance.get("educational_mode", False))
        self.regional_code_var.set(compliance.get("regional_code", "IBC_2021"))
        
        # Posts
        posts = config.get("post_configuration", {})
        self.posts_enabled.set(posts.get("enabled", False))
        self.post_spacing_var.set(posts.get("spacing", 1))
        self.post_diameter_var.set(posts.get("diameter", 2.0))
        self.post_material_var.set(posts.get("material", "steel"))
        self.post_position_var.set(posts.get("position", "outer_edge"))
        
        # Handrail
        handrail = config.get("handrail_configuration", {})
        self.handrail_enabled.set(handrail.get("enabled", True))
        self.handrail_height_var.set(handrail.get("height_above_tread", 36.0))
        self.handrail_diameter_var.set(handrail.get("diameter", 1.75))
        self.handrail_material_var.set(handrail.get("material", "steel"))
        self.handrail_continuous.set(handrail.get("continuous", True))
        self.handrail_end_var.set(handrail.get("end_treatment", "cap"))
        self.handrail_offset_var.set(handrail.get("custom_offset", 0.0))
        
        # Pickets - Handle both new dual format and legacy format
        vertical_pickets = config.get("vertical_picket_configuration", {})
        horizontal_pickets = config.get("horizontal_picket_configuration", {})
        
        # Legacy fallback for old configurations
        legacy_pickets = config.get("picket_configuration", {})
        
        # Determine if any picket type is enabled
        vertical_enabled = vertical_pickets.get("enabled", False)
        horizontal_enabled = horizontal_pickets.get("enabled", False)
        legacy_enabled = legacy_pickets.get("enabled", False)
        
        self.pickets_enabled.set(vertical_enabled or horizontal_enabled or legacy_enabled)
        
        # Set style based on what's enabled
        if vertical_enabled:
            self.picket_style_var.set("vertical")
            self.picket_material_var.set(vertical_pickets.get("material", "aluminum"))
            self.picket_quantity_var.set(vertical_pickets.get("quantity", 3))
        elif horizontal_enabled:
            self.picket_style_var.set("horizontal")
            self.picket_material_var.set(horizontal_pickets.get("rail_material", "aluminum"))
            self.picket_quantity_var.set(horizontal_pickets.get("rail_levels", 4))
        else:
            # Legacy or default values
            self.picket_style_var.set(legacy_pickets.get("style", "vertical"))
            self.picket_material_var.set(legacy_pickets.get("material", "aluminum"))
            self.picket_quantity_var.set(legacy_pickets.get("quantity", 12))
            
        self.picket_base_quantity_var.set(legacy_pickets.get("base_quantity", 12))
        self.picket_adjustment_var.set(legacy_pickets.get("adjustment", 0))
        self.picket_shape_var.set(legacy_pickets.get("shape", "square"))
        
        # Use appropriate diameter based on configuration type
        if vertical_enabled:
            self.picket_diameter_var.set(vertical_pickets.get("diameter", 0.75))
        elif horizontal_enabled:
            self.picket_diameter_var.set(1.0)  # Default for horizontal rails
        else:
            self.picket_diameter_var.set(legacy_pickets.get("diameter", 0.75))
            
        self.picket_square_var.set(legacy_pickets.get("square_side", 0.75))
        self.picket_other_var.set(legacy_pickets.get("other_spec", "Custom specification"))
        self.picket_position_var.set(legacy_pickets.get("position", "under_handrail"))
        self.picket_custom_dim_var.set(legacy_pickets.get("custom_dimension", 0.0))
        
        # Posts tab visibility will be updated in setup_ui_complete()
        
        # Advanced
        advanced = config.get("advanced_settings", {})
        self.mock_mode.set(advanced.get("mock_mode", True))
        self.timeout_var.set(advanced.get("generation_timeout", 120))
        
        # Update control states
        self.toggle_posts()
        self.toggle_handrail()
        self.toggle_pickets()
        self.validate_basic_parameters()
        
    def show_about(self):
        """Show about dialog."""
        about_text = """
Spiral Stair Generator
Version 1.0 (Mock UI)

A modular Python system for generating complete 
spiral staircases in AutoCAD with IBC compliance.

Features:
• Complete component generation
• IBC building code compliance
• Configuration management
• Mock mode for development

Architecture: Master Orchestrator Pattern
Components: 6 independent modules

by Barry Adams 2025
        """
        
        messagebox.showinfo("About", about_text.strip())
        
    # New methods for enhanced functionality
    def add_picket(self):
        """Add a picket to the current quantity."""
        current = self.picket_quantity_var.get()
        self.picket_quantity_var.set(current + 1)
        self.validate_picket_spacing()
        
    def remove_picket(self):
        """Remove a picket from the current quantity."""
        current = self.picket_quantity_var.get()
        if current > 0:
            self.picket_quantity_var.set(current - 1)
            self.validate_picket_spacing()
            
    def toggle_picket_shape(self):
        """Toggle between round, square, and other picket shapes."""
        state = 'normal' if self.pickets_enabled.get() else 'disabled'
        
        # Disable all shape entries first
        self.picket_diameter_entry.config(state='disabled')
        self.picket_square_entry.config(state='disabled')
        self.picket_other_entry.config(state='disabled')
        
        # Enable appropriate entry field
        shape = self.picket_shape_var.get()
        if shape == "round":
            self.picket_diameter_entry.config(state=state)
        elif shape == "square":
            self.picket_square_entry.config(state=state)
        elif shape == "other":
            self.picket_other_entry.config(state=state)
            
    def validate_picket_spacing(self):
        """Calculate and validate picket spacing based on quantity and style."""
        if not self.pickets_enabled.get():
            return
            
        try:
            quantity = self.picket_quantity_var.get()
            rotation = self.rotation_var.get()
            outside_radius = self.outside_diameter_var.get() / 2
            height = self.height_var.get()
            style = self.picket_style_var.get()
            
            # Calculate spacing between pickets based on style
            if quantity > 0:
                if style == "vertical":
                    # For vertical pickets: calculate per tread, not per entire stair
                    # Estimate treads based on height (typical 7-8" rise per tread)
                    estimated_treads = max(1, int(height / 7.5))  # Assume 7.5" rise per tread
                    pickets_per_tread = quantity / estimated_treads
                    
                    # Calculate spacing on tread circumference (not full rotation)
                    tread_angle = 360 / estimated_treads  # Degrees per tread
                    angle_per_picket = tread_angle / pickets_per_tread if pickets_per_tread > 0 else tread_angle
                    arc_length = (angle_per_picket * 3.14159 / 180) * outside_radius
                    gap_spacing = arc_length - (0.75 if self.picket_shape_var.get() == "round" else 0.75)
                    
                    if gap_spacing <= 4.0:
                        self.picket_ibc_status_var.set(f"+ Vertical picket spacing: {gap_spacing:.2f}\" per tread ({pickets_per_tread:.1f} pickets/tread) - IBC compliant")
                        self.picket_ibc_status_label.config(foreground="green")
                    else:
                        additional_per_tread = int((gap_spacing / 4.0) * pickets_per_tread) - int(pickets_per_tread) + 1
                        total_additional = additional_per_tread * estimated_treads
                        self.picket_ibc_status_var.set(f"- Vertical picket spacing: {gap_spacing:.2f}\" exceeds 4\" IBC limit. Need {additional_per_tread} more per tread ({total_additional} total)")
                        self.picket_ibc_status_label.config(foreground="red")
                        
                else:  # horizontal pickets
                    # For horizontal pickets: calculate across entire stair rotation
                    angle_per_picket = rotation / quantity
                    arc_length = (angle_per_picket * 3.14159 / 180) * outside_radius
                    gap_spacing = arc_length - (0.75 if self.picket_shape_var.get() == "round" else 0.75)
                    
                    if gap_spacing <= 4.0:
                        self.picket_ibc_status_var.set(f"+ Horizontal picket spacing: {gap_spacing:.2f}\" (IBC compliant)")
                        self.picket_ibc_status_label.config(foreground="green")
                    else:
                        additional_needed = int((gap_spacing/4.0)*quantity) - quantity + 1
                        self.picket_ibc_status_var.set(f"- Horizontal picket spacing: {gap_spacing:.2f}\" exceeds 4\" IBC limit. Need {additional_needed} more pickets")
                        self.picket_ibc_status_label.config(foreground="red")
            else:
                self.picket_ibc_status_var.set("No pickets specified")
                self.picket_ibc_status_label.config(foreground="gray")
                
        except (tk.TclError, ZeroDivisionError):
            self.picket_ibc_status_var.set("Invalid parameters for spacing calculation")
            self.picket_ibc_status_label.config(foreground="red")
            
    def auto_calculate_pickets(self):
        """Calculate optimal picket quantity based on 4-inch maximum spacing rule."""
        try:
            # Get the outside diameter and rotation from basic parameters
            outside_diameter = self.outside_diameter_var.get()
            rotation_degrees = self.rotation_var.get()
            
            # Calculate the arc length per tread
            radius = outside_diameter / 2
            angle_per_tread = rotation_degrees / 16  # Assuming 16 treads typical
            angle_rad = angle_per_tread * (3.14159 / 180)
            arc_length = radius * angle_rad
            
            # Calculate maximum pickets that can fit with 4" spacing
            # Allow for picket width (approximate 0.75" for typical picket)
            picket_width = 0.75
            available_space = arc_length - picket_width  # Space minus one picket width
            max_gaps = available_space / 4.0  # Maximum 4" gaps
            optimal_quantity = max(1, int(max_gaps))  # At least 1 picket
            
            # Update the base quantity
            self.picket_base_quantity_var.set(optimal_quantity)
            
            # Reset adjustment to 0 and update total
            self.picket_adjustment_var.set(0)
            self.update_picket_quantity()
            
        except (tk.TclError, ZeroDivisionError, ValueError):
            # If calculation fails, set a reasonable default
            self.picket_base_quantity_var.set(3)
            self.picket_adjustment_var.set(0)
            self.update_picket_quantity()
            
    def update_picket_quantity(self):
        """Update the total picket quantity based on base + adjustment."""
        base = self.picket_base_quantity_var.get()
        adjustment = self.picket_adjustment_var.get()
        total = max(1, base + adjustment)  # Ensure at least 1 picket
        self.picket_quantity_var.set(total)
        
        # Trigger spacing validation
        self.validate_picket_spacing()
            
    def on_picket_style_change(self, event=None):
        """Handle picket style changes to show/hide Posts inline group and update UI."""
        style = self.picket_style_var.get()
        if style == "horizontal":
            self.show_posts_inline()
            if hasattr(self, 'picket_position_label'):
                self.picket_position_label.config(text="Position (Horizontal):")
            # Enable posts automatically for horizontal pickets since they're structurally required
            if hasattr(self, 'posts_enabled'):
                self.posts_enabled.set(True)
                if hasattr(self, 'toggle_posts_inline'):
                    self.toggle_posts_inline()
        else:  # vertical
            self.hide_posts_inline()
            if hasattr(self, 'picket_position_label'):
                self.picket_position_label.config(text="Position (Vertical):")
            # Disable posts for vertical pickets (not structurally needed)
            if hasattr(self, 'posts_enabled'):
                self.posts_enabled.set(False)
                if hasattr(self, 'toggle_posts_inline'):
                    self.toggle_posts_inline()
            
    def show_posts_inline(self):
        """Show the inline Posts group in the Pickets tab."""
        self.posts_inline_group.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), pady=(0, 15), padx=(10, 0))
        
    def hide_posts_inline(self):
        """Hide the inline Posts group in the Pickets tab."""
        self.posts_inline_group.grid_remove()
        
    def toggle_posts_inline(self):
        """Toggle inline posts configuration controls."""
        state = 'normal' if self.posts_enabled.get() else 'disabled'
        
        # Update all post controls
        if hasattr(self, 'post_diameter_entry'):
            self.post_diameter_entry.config(state=state)
        if hasattr(self, 'post_material_combo'):
            self.post_material_combo.config(state=state)
        if hasattr(self, 'post_position_combo'):
            self.post_position_combo.config(state=state)
        if hasattr(self, 'post_spacing_radio1'):
            self.post_spacing_radio1.config(state=state)
            self.post_spacing_radio2.config(state=state)
            self.post_spacing_radio3.config(state=state)
            
    def show_posts_tab(self):
        """Add the Posts tab to the notebook."""
        if not self.posts_tab_added:
            # Insert Posts tab before Advanced tab (which is always last)
            self.notebook.insert(self.notebook.index("end") - 1, self.posts_frame, text="  Structural Posts  ")
            self.posts_tab_added = True
            
    def hide_posts_tab(self):
        """Remove the Posts tab from the notebook."""
        if self.posts_tab_added:
            # Find and remove the Posts tab
            for i in range(self.notebook.index("end")):
                if self.notebook.tab(i, "text").strip() == "Structural Posts":
                    self.notebook.forget(i)
                    self.posts_tab_added = False
                    break
            
    def toggle_advanced_details(self):
        """Toggle visibility of advanced details textbox."""
        if self.advanced_details_visible.get():
            # Hide the textbox
            self.advanced_details_text.grid_remove()
            self.advanced_show_hide_btn.config(text="Show")
            self.advanced_details_visible.set(False)
        else:
            # Show the textbox
            self.advanced_details_text.grid()
            self.advanced_show_hide_btn.config(text="Hide")
            self.advanced_details_visible.set(True)
            
    def clear_advanced_details(self):
        """Clear contents of advanced details textbox."""
        self.advanced_details_text.delete(1.0, tk.END)
        self.advanced_details_text.insert(tk.END, "Generation details cleared...\n")
            
    def complete_ui_setup(self):
        """Complete UI setup after all components are initialized."""
        # Update Posts tab visibility based on current picket style
        self.on_picket_style_change()
        
        # Update combined status displays
        if hasattr(self, 'update_combined_basic_status'):
            try:
                self.update_combined_basic_status(
                    self.center_pole_var.get(),
                    self.height_var.get(), 
                    self.outside_diameter_var.get(),
                    self.rotation_var.get(),
                    []
                )
            except:
                pass  # Skip if values not ready yet
                
        # Initialize specification review with preliminary values
        if hasattr(self, 'update_specification_review'):
            try:
                self.update_specification_review()
            except:
                pass  # Skip if review components not ready yet
            
    def on_educational_mode_change(self):
        """Handle educational mode toggle - update basic params validation display."""
        # Trigger a refresh of the basic parameters validation display
        if hasattr(self, 'validate_basic_parameters'):
            self.validate_basic_parameters()
            
    def toggle_mock_mode(self):
        """Toggle mock mode and update connection test buttons."""
        import os
        if self.mock_mode.get():
            # Enable mock mode
            os.environ['AUTOCAD_MOCK_MODE'] = 'true'
            self.test_mock_button.config(state='normal')
            self.test_autocad_button.config(state='disabled')
            self.connection_status_var.set("Mock mode enabled")
        else:
            # Enable real AutoCAD mode
            os.environ['AUTOCAD_MOCK_MODE'] = 'false'
            self.test_mock_button.config(state='disabled')
            self.test_autocad_button.config(state='normal')
            self.connection_status_var.set("Real AutoCAD mode enabled")
            
    def test_mock_connection(self):
        """Test mock mode connection."""
        self.connection_status_var.set("Testing mock connection...")
        self.root.update()
        
        # Simulate connection test
        import time
        time.sleep(1)
        
        self.connection_status_var.set("+ Mock connection successful - Ready for testing")
        
    def test_autocad_connection(self):
        """Test AutoCAD connection."""
        self.connection_status_var.set("Testing AutoCAD connection...")
        self.root.update()
        
        try:
            # Try to create the appropriate AutoCAD interface
            import os
            if os.environ.get('AUTOCAD_MOCK_MODE', 'false').lower() == 'true':
                from core.autocad_interface import MockAutoCADInterface
                autocad = MockAutoCADInterface()
                success = autocad.connect()
                if success:
                    self.connection_status_var.set("+ Mock AutoCAD connection successful")
                else:
                    self.connection_status_var.set("- Mock AutoCAD connection failed")
            else:
                from core.autocad_interface import RealAutoCADInterface
                autocad = RealAutoCADInterface()
                success = autocad.connect()
                version = autocad.acad_app.Version if hasattr(autocad, 'acad_app') and autocad.acad_app else "Unknown"
                if success:
                    self.connection_status_var.set(f"+ AutoCAD connection successful - Version: {version}")
                else:
                    self.connection_status_var.set("- AutoCAD connection failed")
        except Exception as e:
            self.connection_status_var.set(f"- AutoCAD connection failed: {str(e)}")
            
    def configure_custom_standards(self):
        """Configure custom company standards."""
        messagebox.showinfo("Custom Standards", "Custom company standards configuration will be implemented in a future version.")
        
    def reset_ibc_defaults(self):
        """Reset ALL settings across all tabs to defaults."""
        if messagebox.askyesno("Reset All Settings", "Reset ALL settings in ALL tabs to defaults?\n\nThis will reset:\n• Basic Parameters\n• Pickets\n• Posts\n• Handrails\n• Advanced Settings\n• IBC Compliance"):
            # Basic Parameters Tab
            self.center_pole_var.set(5.56)
            self.height_var.set(144.0)
            self.outside_diameter_var.set(72.0)
            self.rotation_var.set(450.0)
            self.direction_var.set(True)  # Clockwise
            self.basic_ibc_ignore.set(False)
            
            # Mid-landing controls
            self.mid_landing_enabled_var.set(False)
            self.mid_landing_position_var.set(8)
            self.on_mid_landing_toggle()  # Update UI state
            
            # Component Enables
            self.center_pole_enabled.set(True)
            self.treads_enabled.set(True)
            self.landings_enabled.set(True)
            
            # Pickets Tab
            self.pickets_enabled.set(True)
            self.picket_quantity_var.set(12)
            self.picket_adjustment_var.set(0)
            self.picket_base_quantity_var.set(12)
            self.picket_style_var.set("vertical")
            self.picket_position_var.set("under_handrail")
            self.picket_custom_dim_var.set(0.0)
            self.picket_material_var.set("aluminum")
            self.picket_shape_var.set("square")
            self.picket_diameter_var.set(0.75)
            self.picket_square_var.set(0.75)
            self.picket_other_var.set("Custom specification")
            self.picket_ibc_ignore.set(False)
            
            # Posts Tab
            self.posts_enabled.set(True)
            self.post_spacing_var.set(1)
            self.post_diameter_var.set(2.0)
            self.post_material_var.set("aluminum")
            self.post_position_var.set("outer_edge")
            
            # Handrails Tab
            self.handrail_enabled.set(True)
            self.handrail_height_var.set(36.0)
            self.handrail_diameter_var.set(1.5)
            self.handrail_material_var.set("aluminum")
            self.handrail_continuous.set(True)
            self.handrail_end_var.set("cap")
            self.handrail_offset_var.set(0.0)
            self.handrail_ibc_ignore.set(False)
            
            # Advanced/IBC Settings
            self.ibc_enabled.set(True)
            self.educational_mode.set(False)
            self.regional_code_var.set("IBC_2021")
            self.timeout_var.set(120)
            
            # Reset status variables
            self.basic_combined_status_var.set("Checking parameters...")
            self.picket_ibc_status_var.set("Analyzing picket spacing...")
            self.handrail_ibc_status_var.set("Checking handrail height compliance...")
            self.connection_status_var.set("No connection test performed")
            
            # Trigger validation refreshes
            if hasattr(self, 'validate_basic_parameters'):
                self.validate_basic_parameters()
            if hasattr(self, 'update_picket_calculations'):
                self.update_picket_calculations()
            if hasattr(self, 'validate_handrail_parameters'):
                self.validate_handrail_parameters()
            
            # Reset Generate tab displays
            if hasattr(self, 'update_specification_review'):
                self.update_specification_review()  # Reset to preliminary (red) display
            if hasattr(self, 'clear_advanced_details'):
                self.clear_advanced_details()  # Clear Interface Logging
                
            messagebox.showinfo("Reset Complete", "All settings have been reset to defaults across all tabs.")
            
    def hide_build_details(self):
        """Hide the build details section."""
        self.details_frame.grid_remove()
        
    def show_build_details(self):
        """Show the build details section."""
        self.details_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
    def clear_build_details(self):
        """Clear the build details text."""
        self.build_details_text.delete(1.0, tk.END)
        
    def log_build_message(self, message):
        """Add a message to the build details log."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Log to bottom section build details (if it exists)
        if hasattr(self, 'build_details_text'):
            self.build_details_text.insert(tk.END, formatted_message)
            self.build_details_text.see(tk.END)
            self.show_build_details()  # Show details when logging
        
        # Log to Generate tab build details
        if hasattr(self, 'generate_tab_details_text'):
            self.generate_tab_details_text.config(state=tk.NORMAL)
            self.generate_tab_details_text.insert(tk.END, formatted_message)
            self.generate_tab_details_text.see(tk.END)
            self.generate_tab_details_text.config(state=tk.DISABLED)
        
        # Also log to advanced tab details textbox
        if hasattr(self, 'advanced_details_text'):
            self.advanced_details_text.insert(tk.END, formatted_message)
            self.advanced_details_text.see(tk.END)
        
    def update_combined_basic_status(self, center_pole, height, outside_diameter, rotation, param_errors):
        """Update combined parameter validation and IBC compliance status."""
        status_messages = []
        overall_status = "green"  # Start optimistic
        
        # Parameter validation section
        if param_errors:
            status_messages.append("PARAMETER VALIDATION:")
            for error in param_errors:
                status_messages.append(f"  - {error}")
            overall_status = "red"
        else:
            status_messages.append("PARAMETER VALIDATION:")
            status_messages.append("  + All parameters are within valid ranges")
        
        status_messages.append("")  # Add spacing
        
        # IBC Compliance section
        if hasattr(self, 'educational_mode') and self.educational_mode.get():
            status_messages.append("IBC COMPLIANCE:")
            status_messages.append("  ~ IBC compliance checks ignored (Educational Mode)")
            if overall_status != "red":
                overall_status = "gray"
        else:
            try:
                # Calculate walkline width (IBC requirement: >= 6.75")
                center_radius = center_pole / 2
                walkline_radius = center_radius + 12  # 12" from center pole edge
                
                # Estimate number of treads
                riser_height = 7.5  # Typical riser height
                num_treads = height / riser_height
                
                # Calculate angle per tread
                angle_per_tread = rotation / num_treads
                angle_rad = (angle_per_tread * 3.14159) / 180
                
                # Calculate walkline width
                walkline_width = walkline_radius * angle_rad
                
                status_messages.append("IBC COMPLIANCE:")
                ibc_compliant = True
                
                # Check walkline width
                if walkline_width >= 6.75:
                    status_messages.append(f"  + Walkline width: {walkline_width:.2f}\" (≥ 6.75\" required)")
                else:
                    status_messages.append(f"  - Walkline width: {walkline_width:.2f}\" < 6.75\" IBC minimum")
                    status_messages.append(f"    → Increase center pole to {((6.75/angle_rad - 12) * 2):.1f}\" diameter")
                    ibc_compliant = False
                    
                # Check walk space (clear width at handrail level)
                walk_space = (outside_diameter/2 - center_radius - 12) * 2  # Approximate
                if walk_space >= 26:
                    status_messages.append(f"  + Walk space: {walk_space:.1f}\" (≥ 26\" required)")
                else:
                    status_messages.append(f"  - Walk space: {walk_space:.1f}\" < 26\" IBC minimum")
                    status_messages.append(f"    → Increase outside diameter to {outside_diameter + (26 - walk_space):.1f}\"")
                    ibc_compliant = False
                    
                # Check if mid-landing required
                if height > 151:
                    status_messages.append(f"  + Mid-landing required for height {height:.1f}\" > 151\"")
                else:
                    status_messages.append(f"  + No mid-landing required for height {height:.1f}\" ≤ 151\"")
                
                if not ibc_compliant and overall_status != "red":
                    overall_status = "red"
                    
            except (ZeroDivisionError, ValueError):
                status_messages.append("IBC COMPLIANCE:")
                status_messages.append("  - Cannot calculate compliance - invalid parameters")
                overall_status = "red"
        
        status_text = "\n".join(status_messages)
        self.basic_combined_status_var.set(status_text)
        
        # Set color based on overall status
        if overall_status == "green":
            self.basic_combined_status_label.config(foreground="green")
        elif overall_status == "gray":
            self.basic_combined_status_label.config(foreground="gray")
        else:
            self.basic_combined_status_label.config(foreground="red")


def main():
    """Main application entry point."""
    # Only set mock mode if not already set (allow override)
    # Default to false to use real AutoCAD for production use
    # Set to true for development/testing without AutoCAD installation
    if 'AUTOCAD_MOCK_MODE' not in os.environ:
        os.environ['AUTOCAD_MOCK_MODE'] = 'false'
    
    # Create main window
    root = tk.Tk()
    
    # Apply modern styling
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
    
    # Create application
    app = SpiralStairUI(root)
    
    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()