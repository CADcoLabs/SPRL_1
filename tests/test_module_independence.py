"""
Test 2.2: Module Independence Verification
Purpose: Prove modules truly operate independently - failure in one shouldn't affect others
Why Critical: Core architectural principle - zero cross-module dependencies
"""
import pytest
import sys
import os
from typing import Dict, Any

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestModuleIndependence:
    """Test suite for module independence verification"""

    @pytest.fixture
    def valid_config(self) -> Dict[str, Any]:
        """Create a valid configuration for testing."""
        return {
            "basic_parameters": {
                "center_pole_diameter": 5.563,
                "overall_height": 144.0,
                "outside_diameter": 72.0,
                "total_rotation": 450.0,
                "is_clockwise": True,
            },
            "vertical_picket_configuration": {
                "enabled": True,
                "spacing_inches": 3.5,
                "material": "aluminum",
                "diameter": 0.75,
                "quantity": 3,
                "position": "outer",
            },
            "horizontal_picket_configuration": {
                "enabled": True,
                "guard_height": 42.0,
                "rail_levels": 4,
                "rail_material": "aluminum",
                "spacing_inches": 3.5,
            },
            "handrail_configuration": {
                "diameter": 1.75,
                "height_above_tread": 36.0,
            }
        }

    def test_vertical_module_isolation_from_horizontal(self, valid_config):
        """Verify vertical module can operate when horizontal module fails"""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule

        # Create modules
        vertical_module = VerticalPicketModule()
        horizontal_module = HorizontalPicketModule()

        # Make horizontal module fail by giving it invalid config
        invalid_config = valid_config.copy()
        invalid_config["horizontal_picket_configuration"]["rail_levels"] = -1  # Invalid

        # Vertical module should still work
        vertical_result = vertical_module.validate_parameters(valid_config)
        assert vertical_result is True, f"Vertical module validation failed: {vertical_module.last_error}"

        # Horizontal module should fail
        with pytest.raises(ValueError):
            horizontal_module.validate_parameters(invalid_config)

        # But vertical module should still be unaffected
        assert vertical_module.last_error is None

    def test_horizontal_module_isolation_from_vertical(self, valid_config):
        """Verify horizontal module can operate when vertical module fails"""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule

        # Create modules
        vertical_module = VerticalPicketModule()
        horizontal_module = HorizontalPicketModule()

        # Make vertical module fail by giving it invalid config
        invalid_config = valid_config.copy()
        invalid_config["vertical_picket_configuration"]["spacing_inches"] = 5.0  # > 4.0 IBC limit

        # Horizontal module should still work
        horizontal_result = horizontal_module.validate_parameters(valid_config)
        assert horizontal_result is True, f"Horizontal module validation failed: {horizontal_module.last_error}"

        # Vertical module should fail
        with pytest.raises(ValueError):
            vertical_module.validate_parameters(invalid_config)

        # But horizontal module should still be unaffected
        assert horizontal_module.last_error is None

    def test_module_state_isolation(self):
        """Verify modules don't share state between instances"""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule

        # Create multiple instances
        module1 = VerticalPicketModule()
        module2 = VerticalPicketModule()
        h_module1 = HorizontalPicketModule()
        h_module2 = HorizontalPicketModule()

        # Modify one instance
        module1.last_error = "Test error on module1"
        module1.picket_count = 5
        h_module1.last_error = "Test error on h_module1"

        # Other instances should be unaffected
        assert module2.last_error is None
        assert module2.picket_count == 0
        assert h_module2.last_error is None

        # Different module types should be unaffected
        assert module1.last_error != h_module1.last_error

    def test_no_shared_dependencies_between_modules(self):
        """Verify no shared dependencies between modules"""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule
        from modules.center_pole_module import CenterPoleModule
        from modules.handrail_module import HandrailModule

        modules = [
            VerticalPicketModule(),
            HorizontalPicketModule(),
            CenterPoleModule(),
            HandrailModule(),
        ]

        # All modules should be able to be instantiated independently
        for module in modules:
            assert module is not None

        # Check that they don't share any common state variables that could interfere
        for i, module1 in enumerate(modules):
            for j, module2 in enumerate(modules):
                if i != j and hasattr(module1, 'last_error') and hasattr(module2, 'last_error'):
                    # They should start with independent error states
                    assert module1.last_error == module2.last_error  # Both should be None initially

    def test_configuration_isolation(self, valid_config):
        """Verify module configurations don't interfere with each other"""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule

        vertical_module = VerticalPicketModule()
        horizontal_module = HorizontalPicketModule()

        # Both modules should accept their respective configuration sections
        vertical_result = vertical_module.validate_parameters(valid_config)
        horizontal_result = horizontal_module.validate_parameters(valid_config)

        assert vertical_result is True
        assert horizontal_result is True

        # Verify they only care about their own config sections
        # Remove horizontal config - should not affect vertical module
        config_no_horizontal = valid_config.copy()
        del config_no_horizontal["horizontal_picket_configuration"]

        vertical_result_no_horizontal = vertical_module.validate_parameters(config_no_horizontal)
        assert vertical_result_no_horizontal is True

        # Remove vertical config - should not affect horizontal module
        config_no_vertical = valid_config.copy()
        del config_no_vertical["vertical_picket_configuration"]

        horizontal_result_no_vertical = horizontal_module.validate_parameters(config_no_vertical)
        assert horizontal_result_no_vertical is True

    def test_error_isolation(self, valid_config):
        """Verify errors in one module don't propagate to others"""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule
        from modules.center_pole_module import CenterPoleModule

        modules = [
            VerticalPicketModule(),
            HorizontalPicketModule(),
            CenterPoleModule(),
        ]

        # Make one module fail
        invalid_config = valid_config.copy()
        invalid_config["vertical_picket_configuration"]["spacing_inches"] = 5.0  # Invalid

        # This should only affect the vertical module
        with pytest.raises(ValueError):
            modules[0].validate_parameters(invalid_config)

        # Other modules should still work fine
        for module in modules[1:]:
            result = module.validate_parameters(valid_config)
            assert result is True, f"Module {module.__class__.__name__} affected by other module's error"

    def test_cleanup_isolation(self):
        """Verify cleanup operations are isolated per module"""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule

        # Mock AutoCAD interface
        class MockAutoCAD:
            def __init__(self):
                self.entities = []

        mock_autocad = MockAutoCAD()

        vertical_module = VerticalPicketModule()
        horizontal_module = HorizontalPicketModule()

        # Set some state on modules
        vertical_module.pickets_created = ["v_entity1", "v_entity2"]
        vertical_module.picket_count = 2
        horizontal_module.horizontal_rails_created = ["h_entity1", "h_entity2"]
        horizontal_module.rail_count = 2

        # Cleanup should only affect the calling module
        vertical_module.cleanup(mock_autocad)

        # Vertical module should be reset
        assert vertical_module.pickets_created == []
        assert vertical_module.picket_count == 0

        # Horizontal module should be unaffected
        assert horizontal_module.horizontal_rails_created == ["h_entity1", "h_entity2"]
        assert horizontal_module.rail_count == 2

    def test_module_lifecycle_independence(self, valid_config):
        """Verify complete module lifecycle operations are independent"""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule

        # Mock AutoCAD interface
        class MockAutoCAD:
            def __init__(self):
                self.entities = []

        mock_autocad = MockAutoCAD()

        vertical_module = VerticalPicketModule()
        horizontal_module = HorizontalPicketModule()

        # Both modules should be able to complete full lifecycle independently
        v_validate = vertical_module.validate_parameters(valid_config)
        h_validate = horizontal_module.validate_parameters(valid_config)

        assert v_validate is True
        assert h_validate is True

        # Both should be able to get their required parameters
        v_params = vertical_module.get_required_parameters()
        h_params = horizontal_module.get_required_parameters()

        assert isinstance(v_params, list)
        assert isinstance(h_params, list)

        # Both should be able to clean up independently
        vertical_module.cleanup(mock_autocad)
        horizontal_module.cleanup(mock_autocad)

        # Both should still be functional after cleanup
        assert vertical_module.validate_parameters(valid_config) is True
        assert horizontal_module.validate_parameters(valid_config) is True