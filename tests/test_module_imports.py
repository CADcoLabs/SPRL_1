"""
Test 1.1: Basic Module Import Validation
Purpose: Verify both new picket modules can be imported without errors
Why Critical: Foundation test - if modules don't import, nothing else works
"""
import pytest
import sys
import os

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestModuleImports:
    """Test suite for module import validation"""
    
    def test_vertical_picket_module_import(self):
        """Verify vertical picket module imports successfully"""
        try:
            from modules.vertical_picket_module import VerticalPicketModule
            module = VerticalPicketModule()
            assert module is not None
            assert hasattr(module, 'validate_parameters')
            assert hasattr(module, 'generate_geometry')
            assert hasattr(module, 'get_required_parameters')
            assert hasattr(module, 'cleanup')
        except ImportError as e:
            pytest.fail(f"Failed to import VerticalPicketModule: {e}")
        except Exception as e:
            pytest.fail(f"Error instantiating VerticalPicketModule: {e}")

    def test_horizontal_picket_module_import(self):
        """Verify horizontal picket module imports successfully"""
        try:
            from modules.horizontal_picket_module import HorizontalPicketModule
            module = HorizontalPicketModule()
            assert module is not None
            assert hasattr(module, 'validate_parameters')
            assert hasattr(module, 'generate_geometry')
            assert hasattr(module, 'get_required_parameters')
            assert hasattr(module, 'cleanup')
        except ImportError as e:
            pytest.fail(f"Failed to import HorizontalPicketModule: {e}")
        except Exception as e:
            pytest.fail(f"Error instantiating HorizontalPicketModule: {e}")

    def test_base_component_inheritance(self):
        """Verify both modules inherit from BaseStairComponent"""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule
        from core.base_component import BaseStairComponent
        
        vertical_module = VerticalPicketModule()
        horizontal_module = HorizontalPicketModule()
        
        assert isinstance(vertical_module, BaseStairComponent)
        assert isinstance(horizontal_module, BaseStairComponent)

    def test_module_interface_compliance(self):
        """Verify both modules implement required interface methods"""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule
        
        required_methods = [
            'validate_parameters',
            'generate_geometry', 
            'get_required_parameters',
            'cleanup'
        ]
        
        for ModuleClass in [VerticalPicketModule, HorizontalPicketModule]:
            module = ModuleClass()
            for method in required_methods:
                assert hasattr(module, method), f"{ModuleClass.__name__} missing method: {method}"
                assert callable(getattr(module, method)), f"{ModuleClass.__name__}.{method} is not callable"

    def test_legacy_picket_module_still_available(self):
        """Verify original picket module is still importable for compatibility"""
        try:
            from modules.picket_module import PicketModule
            module = PicketModule()
            assert module is not None
        except ImportError as e:
            pytest.fail(f"Legacy picket module no longer available: {e}")

    def test_all_core_modules_importable(self):
        """Verify all core infrastructure modules can be imported"""
        core_modules = [
            'core.base_component',
            'core.config_manager',
            'core.autocad_interface',
            'core.exceptions',
            'core.logging_config'
        ]
        
        for module_name in core_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import core module {module_name}: {e}")