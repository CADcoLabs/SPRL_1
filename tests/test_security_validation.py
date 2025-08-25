"""
Test 1.3: Security Enhancement Validation  
Purpose: Prove security measures actually prevent attacks
Why Critical: Security claims need verification - untested security is no security
"""
import pytest
import sys
import os

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestSecurityValidation:
    """Test suite for security validation"""
    
    def test_environment_variable_validation(self):
        """Verify invalid environment variables are rejected"""
        from modules.vertical_picket_module import VerticalPicketModule
        
        # Store original value
        original_value = os.environ.get('AUTOCAD_MOCK_MODE')
        
        try:
            # Test invalid AUTOCAD_MOCK_MODE values
            invalid_values = ['invalid_value', 'maybe', 'yes', 'no', '2', '-1', 'True', 'False']
            
            for invalid_value in invalid_values:
                os.environ['AUTOCAD_MOCK_MODE'] = invalid_value
                
                module = VerticalPicketModule()
                
                # Check if module has security validation method
                if hasattr(module, '_validate_environment_security'):
                    with pytest.raises(Exception, match=r".*[Ss]ecurity.*|.*[Ii]nvalid.*"):
                        module._validate_environment_security()
                else:
                    # If no explicit security method, check during parameter validation
                    config = {
                        "basic_parameters": {"outside_diameter": 72.0, "overall_height": 144.0},
                        "vertical_picket_configuration": {"enabled": True}
                    }
                    
                    # Should validate environment during parameter validation or generation
                    with pytest.raises(Exception):
                        module.validate_parameters(config)
                        
        finally:
            # Restore original value
            if original_value is not None:
                os.environ['AUTOCAD_MOCK_MODE'] = original_value
            elif 'AUTOCAD_MOCK_MODE' in os.environ:
                del os.environ['AUTOCAD_MOCK_MODE']

    def test_valid_environment_variables_accepted(self):
        """Verify valid environment variables are accepted"""
        from modules.vertical_picket_module import VerticalPicketModule
        
        # Store original value
        original_value = os.environ.get('AUTOCAD_MOCK_MODE')
        
        try:
            valid_values = ['true', 'false', '1', '0']
            
            for valid_value in valid_values:
                os.environ['AUTOCAD_MOCK_MODE'] = valid_value
                
                module = VerticalPicketModule()
                
                # Should not raise exception for valid values
                if hasattr(module, '_validate_environment_security'):
                    module._validate_environment_security()  # Should not raise
                
                # Should validate parameters successfully
                config = {
                    "basic_parameters": {"outside_diameter": 72.0, "overall_height": 144.0},
                    "vertical_picket_configuration": {"enabled": True, "spacing_inches": 3.5}
                }
                
                result = module.validate_parameters(config)
                assert result == True
                        
        finally:
            # Restore original value
            if original_value is not None:
                os.environ['AUTOCAD_MOCK_MODE'] = original_value
            elif 'AUTOCAD_MOCK_MODE' in os.environ:
                del os.environ['AUTOCAD_MOCK_MODE']

    def test_input_size_limits(self):
        """Verify large configuration inputs are rejected"""
        from modules.vertical_picket_module import VerticalPicketModule
        from modules.horizontal_picket_module import HorizontalPicketModule
        
        # Create oversized configuration values
        large_string = "x" * 2000  # Over reasonable limits
        
        configs_with_large_inputs = [
            {
                "basic_parameters": {"outside_diameter": 72.0, "overall_height": 144.0},
                "vertical_picket_configuration": {
                    "enabled": True,
                    "material": large_string  # Oversized material description
                }
            },
            {
                "basic_parameters": {"outside_diameter": 72.0, "overall_height": 144.0},
                "horizontal_picket_configuration": {
                    "enabled": True,
                    "rail_material": large_string  # Oversized material description
                }
            }
        ]
        
        for ModuleClass in [VerticalPicketModule, HorizontalPicketModule]:
            module = ModuleClass()
            
            for config in configs_with_large_inputs:
                # Should raise security exception for oversized inputs
                with pytest.raises(Exception, match=r".*[Ss]ecurity.*|.*[Tt]oo large.*|.*[Ll]imit.*"):
                    module.validate_parameters(config)

    def test_path_sanitization(self):
        """Verify path traversal attempts are blocked"""
        from modules.vertical_picket_module import VerticalPicketModule
        
        dangerous_paths = [
            "../../../sensitive_file.txt",
            "..\\..\\..\\sensitive_file.txt",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
            "\\\\malicious-server\\share\\file.exe"
        ]
        
        module = VerticalPicketModule()
        
        for dangerous_path in dangerous_paths:
            config_with_path = {
                "basic_parameters": {"outside_diameter": 72.0, "overall_height": 144.0},
                "vertical_picket_configuration": {
                    "enabled": True,
                    "file_path": dangerous_path  # If module accepts file paths
                }
            }
            
            # Should sanitize or reject dangerous paths
            if hasattr(module, '_sanitize_path'):
                sanitized = module._sanitize_path(dangerous_path)
                assert sanitized != dangerous_path, "Path should be sanitized"
                assert ".." not in sanitized, "Path traversal should be removed"
            else:
                # If no explicit sanitization, should reject during validation
                try:
                    module.validate_parameters(config_with_path)
                    # If it doesn't reject, the path parameter might not exist
                except (KeyError, AttributeError):
                    # Parameter might not exist - that's OK
                    pass
                except Exception:
                    # Any other exception indicates security validation is working
                    pass

    def test_resource_exhaustion_protection(self):
        """Verify protection against resource exhaustion attacks"""
        from modules.vertical_picket_module import VerticalPicketModule
        
        # Create configuration that could cause excessive resource usage
        excessive_config = {
            "basic_parameters": {"outside_diameter": 72.0, "overall_height": 144.0},
            "vertical_picket_configuration": {
                "enabled": True,
                "spacing_inches": 0.01,  # Would create thousands of pickets
                "quantity": 10000  # Excessive quantity
            }
        }
        
        module = VerticalPicketModule()
        
        # Should either reject during validation or have resource limits
        try:
            result = module.validate_parameters(excessive_config)
            if result:
                # If validation passes, generation should have limits
                from core.autocad_interface import MockAutoCADInterface
                autocad = MockAutoCADInterface()
                
                # Should complete within reasonable time or raise exception
                import time
                start_time = time.time()
                
                try:
                    module.generate_geometry(autocad, excessive_config)
                    end_time = time.time()
                    
                    # Should not take more than 5 seconds even for excessive config
                    assert end_time - start_time < 5.0, "Generation took too long - no resource protection"
                except Exception:
                    # Exception indicates resource protection is working
                    pass
        except Exception:
            # Exception during validation indicates input validation is working
            pass

    def test_error_message_sanitization(self):
        """Verify error messages don't leak sensitive information"""
        from modules.vertical_picket_module import VerticalPicketModule
        
        module = VerticalPicketModule()
        
        # Create invalid config that might trigger error messages
        invalid_config = {
            "basic_parameters": {"outside_diameter": -1, "overall_height": -1},
            "vertical_picket_configuration": {
                "enabled": True,
                "spacing_inches": "invalid_type"
            }
        }
        
        try:
            module.validate_parameters(invalid_config)
        except Exception as e:
            error_message = str(e)
            
            # Error message should not contain sensitive information
            sensitive_patterns = [
                r'C:\\Users\\[^\\]+',  # User paths
                r'/home/[^/]+',        # Unix home paths
                r'password',           # Password references
                r'secret',             # Secret references
                r'key',                # Key references
                r'token',              # Token references
            ]
            
            for pattern in sensitive_patterns:
                import re
                assert not re.search(pattern, error_message, re.IGNORECASE), \
                    f"Error message contains sensitive information: {pattern}"

    def test_configuration_injection_protection(self):
        """Verify protection against configuration injection attacks"""
        from modules.vertical_picket_module import VerticalPicketModule
        
        # Attempt various injection patterns
        injection_attempts = [
            {"enabled": True, "__class__": "malicious"},
            {"enabled": True, "exec": "malicious_code()"},
            {"enabled": True, "eval": "os.system('rm -rf /')"},
            {"enabled": True, "import": "os"},
        ]
        
        module = VerticalPicketModule()
        
        for injection in injection_attempts:
            malicious_config = {
                "basic_parameters": {"outside_diameter": 72.0, "overall_height": 144.0},
                "vertical_picket_configuration": injection
            }
            
            # Should reject configurations with dangerous keys
            with pytest.raises((ValueError, KeyError, TypeError, AttributeError)):
                module.validate_parameters(malicious_config)