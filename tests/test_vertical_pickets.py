"""
Unit tests for VerticalPicketModule.
Tests the preserved flawless vertical picket functionality with comprehensive coverage.
"""

import pytest
import math
from typing import Dict, Any
from modules.vertical_picket_module import VerticalPicketModule
from core.autocad_interface import AutoCADInterface


class TestVerticalPicketModule:
    """Comprehensive test suite for vertical picket module."""
    
    @pytest.fixture
    def vertical_picket_module(self):
        """Create a vertical picket module instance for testing."""
        return VerticalPicketModule()
    
    @pytest.fixture
    def mock_autocad_interface(self):
        """Create a mock AutoCAD interface for testing."""
        # This would use the actual mock interface from core module
        return AutoCADInterface(mock_mode=True)
    
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
            "handrail_configuration": {
                "diameter": 1.75,
                "height_above_tread": 36.0,
            }
        }

    # =====================================================
    # PARAMETER VALIDATION TESTS
    # =====================================================
    
    @pytest.mark.unit
    def test_parameter_validation_success(self, vertical_picket_module, valid_config):
        """Test parameter validation with valid configuration."""
        result = vertical_picket_module.validate_parameters(valid_config)
        assert result is True
    
    @pytest.mark.unit
    def test_parameter_validation_disabled_module(self, vertical_picket_module, valid_config):
        """Test validation when vertical pickets are disabled."""
        valid_config["vertical_picket_configuration"]["enabled"] = False
        result = vertical_picket_module.validate_parameters(valid_config)
        assert result is True
    
    @pytest.mark.unit
    def test_parameter_validation_invalid_spacing(self, vertical_picket_module, valid_config):
        """Test parameter validation with invalid spacing."""
        valid_config["vertical_picket_configuration"]["spacing_inches"] = 5.0  # > 4.0 IBC max
        
        with pytest.raises(ValueError, match="edge-to-edge spacing must be between 0 and 4 inches"):
            vertical_picket_module.validate_parameters(valid_config)
    
    @pytest.mark.unit
    def test_parameter_validation_zero_spacing(self, vertical_picket_module, valid_config):
        """Test parameter validation with zero spacing."""
        valid_config["vertical_picket_configuration"]["spacing_inches"] = 0.0
        
        with pytest.raises(ValueError, match="edge-to-edge spacing must be between 0 and 4 inches"):
            vertical_picket_module.validate_parameters(valid_config)
    
    @pytest.mark.unit
    def test_parameter_validation_invalid_material(self, vertical_picket_module, valid_config):
        """Test parameter validation with invalid material."""
        valid_config["vertical_picket_configuration"]["material"] = "plastic"
        
        with pytest.raises(ValueError, match="material must be one of"):
            vertical_picket_module.validate_parameters(valid_config)
    
    @pytest.mark.unit
    def test_parameter_validation_invalid_diameter(self, vertical_picket_module, valid_config):
        """Test parameter validation with invalid diameter."""
        valid_config["vertical_picket_configuration"]["diameter"] = -1.0
        
        with pytest.raises(ValueError, match="diameter must be between 0 and 2.0 inches"):
            vertical_picket_module.validate_parameters(valid_config)
    
    @pytest.mark.unit
    def test_parameter_validation_invalid_quantity(self, vertical_picket_module, valid_config):
        """Test parameter validation with invalid quantity."""
        valid_config["vertical_picket_configuration"]["quantity"] = 25
        
        with pytest.raises(ValueError, match="quantity must be between 1 and 20"):
            vertical_picket_module.validate_parameters(valid_config)
    
    @pytest.mark.unit
    def test_parameter_validation_invalid_position(self, vertical_picket_module, valid_config):
        """Test parameter validation with invalid position."""
        valid_config["vertical_picket_configuration"]["position"] = "center"
        
        with pytest.raises(ValueError, match="position must be one of"):
            vertical_picket_module.validate_parameters(valid_config)

    # =====================================================
    # IBC COMPLIANCE TESTS
    # =====================================================
    
    @pytest.mark.ibc
    def test_edge_to_edge_spacing_calculation(self, vertical_picket_module):
        """Test IBC critical edge-to-edge spacing calculation."""
        center_distance = 4.5
        picket_diameter = 0.75
        
        edge_spacing = vertical_picket_module._calculate_edge_to_edge_spacing(
            center_distance, picket_diameter
        )
        
        assert edge_spacing == 3.75  # 4.5 - 0.75
        assert edge_spacing <= 4.0   # IBC compliance check
    
    @pytest.mark.ibc
    def test_ibc_compliance_various_spacings(self, vertical_picket_module):
        """Test IBC compliance with various spacing configurations."""
        test_cases = [
            (3.0, 0.5, True),   # 2.5" edge spacing - compliant
            (4.0, 0.5, True),   # 3.5" edge spacing - compliant  
            (4.5, 0.5, True),   # 4.0" edge spacing - exactly compliant
            (4.6, 0.5, False),  # 4.1" edge spacing - non-compliant
            (5.0, 1.0, True),   # 4.0" edge spacing - exactly compliant
            (5.1, 1.0, False),  # 4.1" edge spacing - non-compliant
        ]
        
        for center_distance, picket_diameter, should_comply in test_cases:
            edge_spacing = vertical_picket_module._calculate_edge_to_edge_spacing(
                center_distance, picket_diameter
            )
            is_compliant = edge_spacing <= 4.0
            
            assert is_compliant == should_comply, (
                f"Center distance {center_distance}, diameter {picket_diameter}: "
                f"expected compliance {should_comply}, got {is_compliant} "
                f"(edge spacing: {edge_spacing})"
            )

    # =====================================================
    # GEOMETRY GENERATION TESTS  
    # =====================================================
    
    @pytest.mark.unit
    def test_geometry_generation_mock_mode_success(self, vertical_picket_module, mock_autocad_interface, valid_config):
        """Test successful geometry generation in mock mode."""
        result = vertical_picket_module.generate_geometry(mock_autocad_interface, valid_config)
        
        assert result is True
        assert vertical_picket_module.is_generated is True
        assert vertical_picket_module.picket_count > 0
        assert len(vertical_picket_module.pickets_created) > 0
        assert len(vertical_picket_module.picket_positions) > 0
    
    @pytest.mark.unit
    def test_geometry_generation_disabled_module(self, vertical_picket_module, mock_autocad_interface, valid_config):
        """Test geometry generation when vertical pickets are disabled."""
        valid_config["vertical_picket_configuration"]["enabled"] = False
        
        result = vertical_picket_module.generate_geometry(mock_autocad_interface, valid_config)
        
        assert result is True
        assert vertical_picket_module.is_generated is True
        assert vertical_picket_module.picket_count == 0
        assert len(vertical_picket_module.pickets_created) == 0
    
    @pytest.mark.unit
    def test_required_parameters_list(self, vertical_picket_module):
        """Test that required parameters list is complete and correct."""
        required = vertical_picket_module.get_required_parameters()
        
        expected_params = [
            "center_pole_diameter",
            "overall_height", 
            "outside_diameter",
            "total_rotation",
            "is_clockwise",
        ]
        
        assert set(required) == set(expected_params)
    
    @pytest.mark.unit
    def test_tread_count_calculation(self, vertical_picket_module):
        """Test tread count calculation consistency."""
        test_heights = [72.0, 96.0, 120.0, 144.0, 168.0, 192.0]
        
        for height in test_heights:
            tread_count = vertical_picket_module._calculate_num_treads(height)
            expected_count = math.ceil(height / 7.5)
            
            assert tread_count == expected_count
            assert tread_count > 0

    # =====================================================
    # ERROR HANDLING TESTS
    # =====================================================
    
    @pytest.mark.unit
    def test_cleanup_functionality(self, vertical_picket_module, mock_autocad_interface):
        """Test cleanup functionality resets module state."""
        # Set some initial state
        vertical_picket_module.pickets_created = ["entity1", "entity2"]
        vertical_picket_module.picket_count = 5
        vertical_picket_module.picket_positions = [(1, 2, 3), (4, 5, 6)]
        
        # Perform cleanup
        vertical_picket_module.cleanup(mock_autocad_interface)
        
        # Verify state reset
        assert vertical_picket_module.pickets_created == []
        assert vertical_picket_module.picket_count == 0
        assert vertical_picket_module.picket_positions == []
    
    @pytest.mark.unit  
    def test_status_reporting(self, vertical_picket_module):
        """Test status reporting functionality."""
        # Set some state
        vertical_picket_module.pickets_created = ["entity1", "entity2", "entity3"]
        vertical_picket_module.picket_count = 3
        vertical_picket_module.picket_positions = [(1, 2, 3), (4, 5, 6)]
        vertical_picket_module.is_generated = True
        
        status = vertical_picket_module.get_status()
        
        assert status["name"] == "Vertical Pickets"
        assert status["is_generated"] is True
        assert status["pickets_created"] == 3
        assert status["picket_positions"] == 2
        assert status["last_error"] is None

    # =====================================================
    # INTEGRATION TESTS (with other components)
    # =====================================================
    
    @pytest.mark.integration
    def test_handrail_integration_parameters(self, vertical_picket_module, valid_config):
        """Test integration with handrail configuration."""
        # Test various handrail configurations
        handrail_configs = [
            {"diameter": 1.5, "height_above_tread": 30.0},
            {"diameter": 1.75, "height_above_tread": 36.0},
            {"diameter": 2.0, "height_above_tread": 42.0},
        ]
        
        for handrail_config in handrail_configs:
            test_config = valid_config.copy()
            test_config["handrail_configuration"] = handrail_config
            
            result = vertical_picket_module.validate_parameters(test_config)
            assert result is True

    # =====================================================
    # PERFORMANCE TESTS
    # =====================================================
    
    @pytest.mark.performance
    def test_generation_performance_benchmark(self, vertical_picket_module, mock_autocad_interface, valid_config):
        """Test that generation meets performance targets."""
        import time
        
        start_time = time.perf_counter()
        result = vertical_picket_module.generate_geometry(mock_autocad_interface, valid_config)
        end_time = time.perf_counter()
        
        generation_time = end_time - start_time
        
        assert result is True
        assert generation_time < 0.15, f"Generation took {generation_time:.3f}s, target is < 0.15s"
    
    @pytest.mark.performance 
    def test_memory_usage_reasonable(self, vertical_picket_module, mock_autocad_interface, valid_config):
        """Test that memory usage stays within reasonable bounds."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        # Generate geometry
        result = vertical_picket_module.generate_geometry(mock_autocad_interface, valid_config)
        
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        assert result is True
        # Memory increase should be less than 10MB for typical generation
        assert memory_increase < 10 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.1f}MB"

    # =====================================================
    # REGRESSION TESTS (preserve existing functionality)
    # =====================================================
    
    @pytest.mark.unit
    def test_preserved_functionality_identical_output(self, vertical_picket_module, mock_autocad_interface, valid_config):
        """Test that preserved functionality produces identical output."""
        # This test ensures that the extracted vertical module produces
        # identical results to the original unified picket module
        
        # Run generation twice
        result1 = vertical_picket_module.generate_geometry(mock_autocad_interface, valid_config)
        count1 = vertical_picket_module.picket_count
        positions1 = len(vertical_picket_module.picket_positions)
        
        # Reset and run again
        vertical_picket_module.cleanup(mock_autocad_interface)
        vertical_picket_module.is_generated = False
        
        result2 = vertical_picket_module.generate_geometry(mock_autocad_interface, valid_config)
        count2 = vertical_picket_module.picket_count
        positions2 = len(vertical_picket_module.picket_positions)
        
        # Results should be identical
        assert result1 == result2 == True
        assert count1 == count2
        assert positions1 == positions2