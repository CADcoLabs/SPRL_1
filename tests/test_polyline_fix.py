"""
Test script to verify the polyline creation fix.
Tests both the new AddLightweightPolyline and corrected AddPolyline methods.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.geometry_creation import AutoCADGeometryCreator
from core.autocad_connection import AutoCADConnectionManager
from core.exceptions import GeometryError, AutoCADConnectionError


class TestPolylineFix(unittest.TestCase):
    """Test cases for the corrected polyline creation methods."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock connection manager
        self.mock_connection_manager = Mock(spec=AutoCADConnectionManager)
        self.mock_connection_manager.is_connected.return_value = True
        
        # Create mock model space
        self.mock_model_space = Mock()
        self.mock_connection_manager.get_model_space.return_value = self.mock_model_space
        
        # Create geometry creator
        self.geometry_creator = AutoCADGeometryCreator(self.mock_connection_manager)

    def test_2d_coordinate_conversion(self):
        """Test 2D coordinate array conversion."""
        # Test data
        coords_2d = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]  # 3 points in 2D
        
        # Mock the VARIANT creation to verify the correct format
        with patch('win32com.client.VARIANT') as mock_variant:
            mock_variant.return_value = "mocked_variant_2d"
            
            result = self.geometry_creator._convert_to_variant_array_2d(coords_2d)
            
            # Verify VARIANT was called with correct parameters
            mock_variant.assert_called_once()
            args, kwargs = mock_variant.call_args
            self.assertEqual(len(args), 2)  # VT_ARRAY | VT_R8, coords
            self.assertEqual(args[1], coords_2d)  # Coordinates should be unchanged
            self.assertEqual(result, "mocked_variant_2d")

    def test_3d_coordinate_conversion(self):
        """Test 3D coordinate array conversion."""
        # Test data
        coords_3d = [10.0, 20.0, 0.0, 30.0, 40.0, 0.0, 50.0, 60.0, 0.0]  # 3 points in 3D
        
        # Mock the VARIANT creation to verify the correct format
        with patch('win32com.client.VARIANT') as mock_variant:
            mock_variant.return_value = "mocked_variant_3d"
            
            result = self.geometry_creator._convert_to_variant_array_3d(coords_3d)
            
            # Verify VARIANT was called with correct parameters
            mock_variant.assert_called_once()
            args, kwargs = mock_variant.call_args
            self.assertEqual(len(args), 2)  # VT_ARRAY | VT_R8, coords
            self.assertEqual(args[1], coords_3d)  # Coordinates should be unchanged
            self.assertEqual(result, "mocked_variant_3d")

    def test_2d_coordinate_validation_errors(self):
        """Test 2D coordinate validation catches errors."""
        # Test odd number of elements
        with self.assertRaises(GeometryError) as context:
            self.geometry_creator._convert_to_variant_array_2d([10.0, 20.0, 30.0])  # Odd number
        self.assertIn("even number of elements", str(context.exception))
        
        # Test insufficient elements
        with self.assertRaises(GeometryError) as context:
            self.geometry_creator._convert_to_variant_array_2d([10.0, 20.0])  # Only 1 point
        self.assertIn("At least 4 elements", str(context.exception))

    def test_3d_coordinate_validation_errors(self):
        """Test 3D coordinate validation catches errors."""
        # Test non-multiple of 3
        with self.assertRaises(GeometryError) as context:
            self.geometry_creator._convert_to_variant_array_3d([10.0, 20.0, 0.0, 30.0])  # Not multiple of 3
        self.assertIn("multiples of 3", str(context.exception))
        
        # Test insufficient elements
        with self.assertRaises(GeometryError) as context:
            self.geometry_creator._convert_to_variant_array_3d([10.0, 20.0, 0.0])  # Only 1 point
        self.assertIn("At least 6 elements", str(context.exception))

    def test_polyline_creation_lightweight_success(self):
        """Test successful lightweight polyline creation."""
        # Test points
        test_points = [(10, 20, 0), (30, 40, 0), (50, 60, 0), (10, 20, 0)]  # Closed rectangle
        
        # Mock AddLightWeightPolyline method exists
        self.mock_model_space.AddLightWeightPolyline = Mock()
        mock_polyline = Mock()
        mock_polyline.Closed = False
        self.mock_model_space.AddLightWeightPolyline.return_value = mock_polyline
        
        # Mock VARIANT creation
        with patch('win32com.client.VARIANT') as mock_variant:
            mock_variant.return_value = "mocked_variant"
            
            # Call create_polyline
            result = self.geometry_creator.create_polyline(test_points)
            
            # Verify AddLightWeightPolyline was called
            self.mock_model_space.AddLightWeightPolyline.assert_called_once_with("mocked_variant")
            
            # Verify polyline was closed (first and last points are same)
            self.assertTrue(mock_polyline.Closed)
            
            # Verify result
            self.assertEqual(result, mock_polyline)

    def test_polyline_creation_legacy_fallback(self):
        """Test fallback to legacy AddPolyline when lightweight fails."""
        # Test points
        test_points = [(10, 20, 0), (30, 40, 0), (50, 60, 0)]
        
        # Remove AddLightWeightPolyline method so hasattr returns False
        if hasattr(self.mock_model_space, 'AddLightWeightPolyline'):
            delattr(self.mock_model_space, 'AddLightWeightPolyline')
        
        # Mock AddPolyline method
        mock_polyline = Mock()
        mock_polyline.Closed = False
        self.mock_model_space.AddPolyline = Mock(return_value=mock_polyline)
        
        # Mock VARIANT creation
        with patch('win32com.client.VARIANT') as mock_variant:
            mock_variant.return_value = "mocked_variant"
            
            # Call create_polyline
            result = self.geometry_creator.create_polyline(test_points)
            
            # Verify AddPolyline was called (fallback)
            self.mock_model_space.AddPolyline.assert_called_once_with("mocked_variant")
            
            # Verify result
            self.assertEqual(result, mock_polyline)

    def test_polyline_insufficient_points(self):
        """Test error handling for insufficient points."""
        # Test with only 1 point
        test_points = [(10, 20, 0)]
        
        with self.assertRaises(GeometryError) as context:
            self.geometry_creator.create_polyline(test_points)
        
        self.assertIn("At least 2 points required", str(context.exception))

    def test_polyline_connection_error(self):
        """Test error handling when not connected to AutoCAD."""
        # Mock not connected
        self.mock_connection_manager.is_connected.return_value = False
        
        test_points = [(10, 20, 0), (30, 40, 0)]
        
        with self.assertRaises(AutoCADConnectionError) as context:
            self.geometry_creator.create_polyline(test_points)
        
        self.assertIn("Not connected to AutoCAD", str(context.exception))

    def test_coordinate_format_conversion(self):
        """Test that coordinates are properly formatted for each method."""
        test_points = [(10, 20, 5), (30, 40, 5), (50, 60, 5)]
        
        # Test 2D format for lightweight polyline
        creator = self.geometry_creator
        
        # Mock to capture the coordinate arrays passed to VARIANT
        captured_coords = []
        
        def capture_variant(*args):
            captured_coords.append(args[1])  # Second arg is the coordinates
            return "mocked_variant"
        
        with patch('win32com.client.VARIANT', side_effect=capture_variant):
            # Test 2D conversion
            creator._convert_to_variant_array_2d([10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
            
            # Should capture 2D coordinates
            self.assertEqual(captured_coords[-1], [10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
            
            # Test 3D conversion
            creator._convert_to_variant_array_3d([10.0, 20.0, 5.0, 30.0, 40.0, 5.0, 50.0, 60.0, 5.0])
            
            # Should capture 3D coordinates
            self.assertEqual(captured_coords[-1], [10.0, 20.0, 5.0, 30.0, 40.0, 5.0, 50.0, 60.0, 5.0])


if __name__ == '__main__':
    print("Running polyline fix tests...")
    unittest.main(verbosity=2)