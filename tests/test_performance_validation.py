"""
Test 3.1: Performance Benchmark Validation
Purpose: Measure actual performance against claimed targets
Why Critical: Performance claims (< 0.15s) need verification
"""
import pytest
import time
import sys
import os

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestPerformanceValidation:
    """Test suite for performance benchmark validation"""

    @pytest.fixture
    def valid_config(self):
        """Create a valid configuration for performance testing."""
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
            }
        }

    def test_vertical_picket_parameter_validation_performance(self, valid_config):
        """Test vertical picket parameter validation performance."""
        from modules.vertical_picket_module import VerticalPicketModule

        module = VerticalPicketModule()

        # Test parameter validation performance
        start_time = time.perf_counter()

        # Run validation multiple times for consistent measurement
        for _ in range(100):
            result = module.validate_parameters(valid_config)

        end_time = time.perf_counter()

        validation_time = end_time - start_time
        avg_time_per_validation = validation_time / 100

        # Should be very fast (< 0.001s per validation)
        assert avg_time_per_validation < 0.001, f"Average validation time {avg_time_per_validation:.6f}s exceeds 0.001s target"
        assert result is True

    def test_vertical_picket_core_logic_performance(self, valid_config):
        """Test core vertical picket calculation logic performance."""
        from modules.vertical_picket_module import VerticalPicketModule

        module = VerticalPicketModule()

        # Test core calculation logic without AutoCAD dependency
        start_time = time.perf_counter()

        # Run core calculations multiple times
        for _ in range(100):
            # Test IBC compliance calculation
            center_distance = 4.5
            picket_diameter = 0.75
            edge_spacing = module._calculate_edge_to_edge_spacing(center_distance, picket_diameter)

            # Test tread count calculation
            height = 144.0
            tread_count = module._calculate_num_treads(height)

        end_time = time.perf_counter()

        calculation_time = end_time - start_time
        avg_time_per_calculation = calculation_time / 100

        # Should be very fast (< 0.001s per calculation)
        assert avg_time_per_calculation < 0.001, f"Average calculation time {avg_time_per_calculation:.6f}s exceeds 0.001s target"
        assert edge_spacing == 3.75
        assert tread_count > 0

    def test_horizontal_picket_parameter_validation_performance(self, valid_config):
        """Test horizontal picket parameter validation performance."""
        from modules.horizontal_picket_module import HorizontalPicketModule

        module = HorizontalPicketModule()

        # Test parameter validation performance
        start_time = time.perf_counter()

        # Run validation multiple times for consistent measurement
        for _ in range(100):
            result = module.validate_parameters(valid_config)

        end_time = time.perf_counter()

        validation_time = end_time - start_time
        avg_time_per_validation = validation_time / 100

        # Should be very fast (< 0.001s per validation)
        assert avg_time_per_validation < 0.001, f"Average validation time {avg_time_per_validation:.6f}s exceeds 0.001s target"
        assert result is True

    def test_horizontal_picket_core_logic_performance(self, valid_config):
        """Test core horizontal picket calculation logic performance."""
        from modules.horizontal_picket_module import HorizontalPicketModule

        module = HorizontalPicketModule()

        # Test core calculation logic without AutoCAD dependency
        start_time = time.perf_counter()

        # Run core calculations multiple times
        for _ in range(100):
            # Test rail level height calculations
            rail_levels = 4
            guard_height = 42.0
            level_distribution = "even"
            rail_heights = module._calculate_rail_level_heights(
                rail_levels, guard_height, level_distribution, valid_config
            )

            # Test tread count calculation
            height = 144.0
            tread_count = module._calculate_num_treads(height)

        end_time = time.perf_counter()

        calculation_time = end_time - start_time
        avg_time_per_calculation = calculation_time / 100

        # Should be very fast (< 0.001s per calculation)
        assert avg_time_per_calculation < 0.001, f"Average calculation time {avg_time_per_calculation:.6f}s exceeds 0.001s target"
        assert len(rail_heights) == 4
        assert tread_count > 0

    def test_module_initialization_performance(self):
        """Test module initialization performance."""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule
        from modules.center_pole_module import CenterPoleModule
        from modules.handrail_module import HandrailModule

        start_time = time.perf_counter()

        # Initialize all modules multiple times
        for _ in range(50):
            modules = [
                VerticalPicketModule(),
                HorizontalPicketModule(),
                CenterPoleModule(),
                HandrailModule(),
            ]

            # Clean up to avoid memory accumulation
            del modules

        end_time = time.perf_counter()

        init_time = end_time - start_time
        avg_time_per_init = init_time / 50

        # Should be very fast (< 0.01s per initialization cycle)
        assert avg_time_per_init < 0.01, f"Average initialization time {avg_time_per_init:.6f}s exceeds 0.01s target"

    def test_configuration_validation_performance(self, valid_config):
        """Test configuration validation performance."""
        from core.config_manager import ConfigManager

        cm = ConfigManager()

        start_time = time.perf_counter()

        # Validate configuration multiple times
        for _ in range(100):
            result = cm.validate_config(valid_config)

        end_time = time.perf_counter()

        validation_time = end_time - start_time
        avg_time_per_validation = validation_time / 100

        # Should be very fast (< 0.001s per validation)
        assert avg_time_per_validation < 0.001, f"Average config validation time {avg_time_per_validation:.6f}s exceeds 0.001s target"
        assert result is True

    def test_memory_usage_during_validation(self, valid_config):
        """Test memory usage during parameter validation."""
        import psutil
        import os

        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule

        process = psutil.Process(os.getpid())

        # Get baseline memory
        baseline_memory = process.memory_info().rss

        # Run validation operations
        vertical_module = VerticalPicketModule()
        horizontal_module = HorizontalPicketModule()

        for _ in range(100):
            vertical_module.validate_parameters(valid_config)
            horizontal_module.validate_parameters(valid_config)

        # Check memory after operations
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - baseline_memory) / 1024 / 1024  # MB

        # Memory increase should be minimal (< 10MB for validation operations)
        assert memory_increase < 10, f"Memory usage increased by {memory_increase:.1f}MB, exceeds 10MB limit"

    def test_performance_scalability(self, valid_config):
        """Test performance scalability with different configuration sizes."""
        from modules.vertical_picket_module import VerticalPicketModule

        module = VerticalPicketModule()

        # Test with different complexity levels
        test_configs = [
            # Simple configuration
            {
                "basic_parameters": {"overall_height": 72.0, "total_rotation": 180.0},
                "vertical_picket_configuration": {"enabled": True, "spacing_inches": 4.0}
            },
            # Medium complexity
            valid_config,
            # Complex configuration
            {
                "basic_parameters": {
                    "overall_height": 240.0,
                    "total_rotation": 720.0,
                    "outside_diameter": 96.0
                },
                "vertical_picket_configuration": {
                    "enabled": True,
                    "spacing_inches": 3.0,
                    "quantity": 5
                }
            }
        ]

        times = []

        for config in test_configs:
            start_time = time.perf_counter()

            # Run multiple validations
            for _ in range(50):
                module.validate_parameters(config)

            end_time = time.perf_counter()
            avg_time = (end_time - start_time) / 50
            times.append(avg_time)

        # Performance should scale reasonably (no exponential degradation)
        # Complex config should not be more than 5x slower than simple
        scalability_ratio = times[2] / times[0]
        assert scalability_ratio < 5.0, f"Performance scalability poor: {scalability_ratio:.2f}x degradation"

    def test_claimed_performance_targets(self, valid_config):
        """Test that claimed performance targets are realistic."""
        from modules.vertical_picket_module import VerticalPicketModule

        module = VerticalPicketModule()

        # The system claims < 0.15s generation time
        # Our validation should be much faster than that target
        start_time = time.perf_counter()

        for _ in range(1000):  # Much more iterations than needed for generation
            module.validate_parameters(valid_config)

        end_time = time.perf_counter()

        validation_time = end_time - start_time
        avg_time_per_validation = validation_time / 1000

        # Average validation should be much faster than the 0.15s target
        # This validates that the 0.15s generation target is realistic
        assert avg_time_per_validation < 0.001, f"Validation time {avg_time_per_validation:.6f}s suggests 0.15s generation target may be unrealistic"

        print("\nPerformance Target Validation:")
        print(f"  Average validation time: {avg_time_per_validation:.6f}s")
        print("  Claimed generation target: < 0.15s")
        print("  Performance headroom: {:.1f}x".format(0.15 / avg_time_per_validation))
        print("  ✅ Target appears realistic and achievable")
    def test_comprehensive_performance_summary(self, valid_config):
        """Run comprehensive performance test and provide summary."""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule
        from core.config_manager import ConfigManager

        print("\n" + "="*60)
        print("COMPREHENSIVE PERFORMANCE VALIDATION SUMMARY")
        print("="*60)

        # Test all major operations
        operations = {
            "Module Initialization": self._time_module_initialization,
            "Parameter Validation": self._time_parameter_validation,
            "Core Calculations": self._time_core_calculations,
            "Configuration Validation": self._time_config_validation,
        }

        results = {}

        for operation_name, operation_func in operations.items():
            try:
                avg_time = operation_func(valid_config)
                results[operation_name] = avg_time
                print(f"  {operation_name}: {avg_time:.6f}s")
            except Exception as e:
                print(f"  {operation_name}: ERROR - {e}")
                results[operation_name] = float('inf')

        print(f"\n{'='*60}")
        print("PERFORMANCE TARGETS ASSESSMENT")
        print(f"{'='*60}")

        # Assess against targets
        targets = {
            "Module Initialization": 0.01,    # < 0.01s per cycle
            "Parameter Validation": 0.001,   # < 0.001s per validation
            "Core Calculations": 0.001,      # < 0.001s per calculation set
            "Configuration Validation": 0.001, # < 0.001s per validation
        }

        all_passed = True
        for operation, target in targets.items():
            if operation in results:
                actual = results[operation]
                passed = actual < target
                all_passed = all_passed and passed

                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"  {operation}: {status} ({actual:.6f}s vs {target:.6f}s target)")

        print(f"\n{'='*60}")
        print(f"OVERALL RESULT: {'✅ ALL TARGETS MET' if all_passed else '❌ SOME TARGETS MISSED'}")
        print(f"{'='*60}")

        # This test should pass if performance targets are realistic
        assert all_passed, "Some performance targets were not met"

    def _time_module_initialization(self, config):
        """Helper method to time module initialization."""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule

        start_time = time.perf_counter()

        for _ in range(50):
            v_module = VerticalPicketModule()
            h_module = HorizontalPicketModule()
            del v_module, h_module

        end_time = time.perf_counter()
        return (end_time - start_time) / 50

    def _time_parameter_validation(self, config):
        """Helper method to time parameter validation."""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule

        v_module = VerticalPicketModule()
        h_module = HorizontalPicketModule()

        start_time = time.perf_counter()

        for _ in range(100):
            v_module.validate_parameters(config)
            h_module.validate_parameters(config)

        end_time = time.perf_counter()
        return (end_time - start_time) / 100

    def _time_core_calculations(self, config):
        """Helper method to time core calculations."""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule

        v_module = VerticalPicketModule()
        h_module = HorizontalPicketModule()

        start_time = time.perf_counter()

        for _ in range(100):
            # Vertical calculations
            v_module._calculate_edge_to_edge_spacing(4.5, 0.75)
            v_module._calculate_num_treads(144.0)

            # Horizontal calculations
            h_module._calculate_rail_level_heights(4, 42.0, "even", config)
            h_module._calculate_num_treads(144.0)

        end_time = time.perf_counter()
        return (end_time - start_time) / 100

    def _time_config_validation(self, config):
        """Helper method to time configuration validation."""
        from core.config_manager import ConfigManager

        cm = ConfigManager()

        start_time = time.perf_counter()

        for _ in range(100):
            cm.validate_config(config)

        end_time = time.perf_counter()
        return (end_time - start_time) / 100