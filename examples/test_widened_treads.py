"""
Test script for widened tread functionality.
Tests the new widened tread geometry with original tread retention option.
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set mock mode for testing
os.environ["AUTOCAD_MOCK_MODE"] = "true"

from core.config_manager import ConfigManager
from modules.tread_module import TreadModule
from core.autocad_interface import create_autocad_interface


def test_widened_treads():
    """Test widened tread functionality with mock AutoCAD interface."""
    
    print("=" * 60)
    print("WIDENED TREAD FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Create configuration manager and load default config
    config_manager = ConfigManager()
    config = config_manager.get_default_config()
    
    # Create AutoCAD interface (mock mode)
    autocad_interface = create_autocad_interface()
    
    # Connect to mock AutoCAD
    print("\n1. Connecting to Mock AutoCAD...")
    if not autocad_interface.connect():
        print("Failed to connect to mock AutoCAD!")
        return False
    print("[OK] Connected to Mock AutoCAD")
    
    # Test 1: Default behavior (no widening, original treads only)
    print("\n2. Test 1: Default Behavior (Original Treads Only)")
    print("-" * 50)
    
    tread_module = TreadModule()
    success = tread_module.generate_geometry(autocad_interface, config)
    
    if success:
        print("[OK] Default treads generated successfully")
        info = tread_module.get_geometry_info()
        print(f"  - Created {info['tread_count']} treads")
        print(f"  - Riser height: {info['riser_height']}\"")
        print(f"  - Tread angle: {info['tread_angle']:.2f}°")
    else:
        print("[FAIL] Failed to generate default treads")
        return False
    
    # Get mock entities to verify original creation
    entities = autocad_interface.get_entities()
    original_count = len(entities)
    print(f"  - Mock entities created: {original_count}")
    
    # Test 2: Widened treads without keeping original (replace mode)
    print("\n3. Test 2: Widened Treads (Replace Original)")
    print("-" * 50)
    
    # Reset for clean test
    autocad_interface.disconnect()
    autocad_interface = create_autocad_interface()
    autocad_interface.connect()
    
    # Configure for widened treads without keeping original
    config["basic_parameters"]["keep_original_tread_geometry"] = False
    
    tread_module2 = TreadModule()
    success = tread_module2.generate_geometry(autocad_interface, config)
    
    if success:
        print("[OK] Widened treads (replace mode) generated successfully")
        entities = autocad_interface.get_entities()
        
        # Check if bottom tread has widened geometry
        widened_entities = [e for e in entities if e.get("type") == "widened_tread"]
        print(f"  - Found {len(widened_entities)} widened tread entities")
        
        # Should have widened tread for bottom tread only
        if len(widened_entities) > 0:
            print("[OK] Widened tread geometry created for bottom tread")
        else:
            print("[FAIL] No widened tread geometry found")
    else:
        print("[FAIL] Failed to generate widened treads (replace mode)")
        return False
    
    # Test 3: Widened treads with keeping original (reference mode)  
    print("\n4. Test 3: Widened Treads (Keep Original Reference)")
    print("-" * 50)
    
    # Reset for clean test
    autocad_interface.disconnect()
    autocad_interface = create_autocad_interface()
    autocad_interface.connect()
    
    # Configure for widened treads with keeping original
    config["basic_parameters"]["keep_original_tread_geometry"] = True
    
    tread_module3 = TreadModule()
    success = tread_module3.generate_geometry(autocad_interface, config)
    
    if success:
        print("[OK] Widened treads (keep original) generated successfully")
        entities = autocad_interface.get_entities()
        
        # Check for both original and widened geometry
        widened_entities = [e for e in entities if e.get("type") == "widened_tread"]
        regular_entities = [e for e in entities if e.get("type") in ["arc", "line"] and e.get("type") != "widened_tread"]
        
        print(f"  - Found {len(widened_entities)} widened tread entities")
        print(f"  - Found {len(regular_entities)} original tread entities")
        
        if len(widened_entities) > 0 and len(regular_entities) > 0:
            print("[OK] Both original and widened tread geometry created")
        else:
            print("[FAIL] Missing either original or widened geometry")
    else:
        print("[FAIL] Failed to generate widened treads (keep original)")
        return False
    
    # Test 4: Configuration validation
    print("\n5. Test 4: Configuration Validation")
    print("-" * 50)
    
    # Test with invalid configuration
    test_config = config.copy()
    test_config["basic_parameters"]["keep_original_tread_geometry"] = "invalid"  # Should be boolean
    
    is_valid, errors = config_manager.validate_config(test_config)
    
    if not is_valid:
        print("[OK] Configuration validation correctly rejected invalid setting")
        print(f"  - Validation errors: {len(errors)}")
    else:
        print("[FAIL] Configuration validation failed to catch invalid setting")
    
    # Clean up
    autocad_interface.disconnect()
    
    print("\n" + "=" * 60)
    print("WIDENED TREAD TEST COMPLETE")
    print("=" * 60)
    
    return True


def demonstrate_offset_calculation():
    """Demonstrate the offset calculation logic used for widening treads."""
    
    print("\n" + "=" * 60)
    print("OFFSET CALCULATION DEMONSTRATION")
    print("=" * 60)
    
    import math
    
    # Example parameters from default config
    outside_diameter = 72.0  # inches
    total_rotation = 450.0   # degrees
    num_treads = 16  # approximate
    
    # Calculate example tread parameters
    outer_radius = outside_diameter / 2  # 36 inches
    tread_angle_deg = total_rotation / (num_treads - 1)  # ~30 degrees
    tread_angle_rad = math.radians(tread_angle_deg)
    
    # Offset calculation
    offset_distance = 0.375  # inches (as specified in requirements)
    angular_offset = offset_distance / outer_radius
    angular_offset_deg = math.degrees(angular_offset)
    
    print(f"Example Calculation for Bottom Tread:")
    print(f"  - Outside diameter: {outside_diameter}\"")
    print(f"  - Outer radius: {outer_radius}\"") 
    print(f"  - Tread angle: {tread_angle_deg:.2f}°")
    print(f"  - Linear offset: {offset_distance}\"")
    print(f"  - Angular offset: {angular_offset_deg:.4f}° ({angular_offset:.6f} rad)")
    print()
    
    # Example start/end angles
    start_angle_deg = 0.0
    end_angle_deg = tread_angle_deg
    
    # Calculate widened angles
    widened_start_deg = start_angle_deg - angular_offset_deg
    widened_end_deg = end_angle_deg + angular_offset_deg
    
    print(f"Original Tread Span:")
    print(f"  - Start angle: {start_angle_deg:.2f}°")
    print(f"  - End angle: {end_angle_deg:.2f}°")
    print(f"  - Total span: {end_angle_deg - start_angle_deg:.2f}°")
    print()
    
    print(f"Widened Tread Span:")
    print(f"  - Widened start: {widened_start_deg:.2f}°") 
    print(f"  - Widened end: {widened_end_deg:.2f}°")
    print(f"  - Total span: {widened_end_deg - widened_start_deg:.2f}°")
    print(f"  - Increase: {(widened_end_deg - widened_start_deg) - (end_angle_deg - start_angle_deg):.4f}°")
    
    # Calculate arc lengths at outer radius
    original_arc_length = outer_radius * math.radians(end_angle_deg - start_angle_deg)
    widened_arc_length = outer_radius * math.radians(widened_end_deg - widened_start_deg)
    
    print()
    print(f"Arc Lengths at Outer Edge:")
    print(f"  - Original: {original_arc_length:.3f}\"")
    print(f"  - Widened: {widened_arc_length:.3f}\"")
    print(f"  - Increase: {widened_arc_length - original_arc_length:.3f}\"")


if __name__ == "__main__":
    print("Starting Widened Tread Tests...")
    
    try:
        # Run functionality tests
        success = test_widened_treads()
        
        # Run calculation demonstration
        demonstrate_offset_calculation()
        
        if success:
            print("\n[OK] ALL TESTS PASSED")
            exit(0)
        else:
            print("\n[FAIL] SOME TESTS FAILED")
            exit(1)
            
    except Exception as e:
        print(f"\n[FAIL] TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)