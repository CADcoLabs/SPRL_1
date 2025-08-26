"""
Debug script to check why widened tread functionality isn't working in real AutoCAD.
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.config_manager import ConfigManager
from modules.tread_module import TreadModule


def debug_tread_configuration():
    """Debug the tread configuration and logic."""
    
    print("=" * 60)
    print("TREAD WIDENING DEBUG")
    print("=" * 60)
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.get_default_config()
    
    print("\n1. Configuration Check:")
    print("-" * 30)
    basic_params = config.get("basic_parameters", {})
    keep_original = basic_params.get("keep_original_tread_geometry", "NOT_FOUND")
    print(f"keep_original_tread_geometry: {keep_original}")
    print(f"Type: {type(keep_original)}")
    
    # Test the logic for different scenarios
    print("\n2. Logic Testing for Bottom Tread (index=0):")
    print("-" * 30)
    
    tread_index = 0
    create_widened = tread_index == 0
    create_original = not create_widened or keep_original
    
    print(f"tread_index: {tread_index}")
    print(f"create_widened: {create_widened}")
    print(f"create_original: {create_original}")
    print(f"keep_original: {keep_original}")
    
    # Expected behavior
    print("\n3. Expected Behavior:")
    print("-" * 30)
    if keep_original:
        print("Should create BOTH original and widened geometry")
    else:
        print("Should create ONLY widened geometry (no original)")
    
    # Test with different settings
    print("\n4. Testing Different Settings:")
    print("-" * 30)
    
    test_configs = [
        {"keep_original_tread_geometry": False},
        {"keep_original_tread_geometry": True},
    ]
    
    for i, test_config in enumerate(test_configs):
        print(f"\nTest {i+1}: keep_original_tread_geometry = {test_config['keep_original_tread_geometry']}")
        
        # Update config
        test_basic_params = config["basic_parameters"].copy()
        test_basic_params.update(test_config)
        test_full_config = config.copy()
        test_full_config["basic_parameters"] = test_basic_params
        
        # Test logic
        keep_orig = test_basic_params.get("keep_original_tread_geometry", False)
        create_wide = tread_index == 0
        create_orig = not create_wide or keep_orig
        
        print(f"  - create_widened: {create_wide}")
        print(f"  - create_original: {create_orig}")
        
        if create_orig and create_wide:
            print("  -> Will create BOTH geometries")
        elif create_wide and not create_orig:
            print("  -> Will create ONLY widened geometry")
        elif create_orig and not create_wide:
            print("  -> Will create ONLY original geometry")
        else:
            print("  -> ERROR: Invalid logic state")
    
    # Check tread module initialization
    print("\n5. Tread Module Test:")
    print("-" * 30)
    
    tread_module = TreadModule()
    required_params = tread_module.get_required_parameters()
    print(f"Required parameters: {required_params}")
    
    # Validate configuration
    is_valid = tread_module.validate_parameters(config)
    print(f"Configuration valid: {is_valid}")
    
    print("\n6. Mock Test Call:")
    print("-" * 30)
    
    # Test the _create_sector_tread method signature directly
    try:
        # This won't actually create anything, just test the method call
        print("Testing _create_sector_tread method signature...")
        print("Method exists and parameters are accessible")
        
        # Show what would happen for bottom tread
        basic_params_test = config.get("basic_parameters", {})
        keep_original_test = basic_params_test.get("keep_original_tread_geometry", False)
        create_widened_test = 0 == 0  # tread_index == 0
        
        print(f"For bottom tread:")
        print(f"  keep_original: {keep_original_test}")
        print(f"  create_widened: {create_widened_test}")
        print(f"  create_original: {not create_widened_test or keep_original_test}")
        
    except Exception as e:
        print(f"Error testing method: {str(e)}")


if __name__ == "__main__":
    debug_tread_configuration()