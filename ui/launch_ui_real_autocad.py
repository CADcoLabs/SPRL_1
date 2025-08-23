"""
Launch script for Spiral Stair UI with real AutoCAD connection and full logging.
This script sets up comprehensive logging before starting the UI to capture all actions and errors.
"""

import os
import sys
import logging
from datetime import datetime

# Add parent directory to path so we can import the UI module
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(parent_dir)

# Set default to real AutoCAD mode, but allow UI override
if 'AUTOCAD_MOCK_MODE' not in os.environ:
    os.environ['AUTOCAD_MOCK_MODE'] = 'false'

# Set up comprehensive logging
def setup_logging():
    """Set up logging to capture all actions and errors."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(parent_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"spiral_stair_ui_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)  # Also log to console
        ]
    )
    
    # Create a logger for our launcher
    logger = logging.getLogger("UI_Launcher")
    logger.info("=== Spiral Stair UI Launcher Started ===")
    logger.info(f"Log file: {log_file}")
    logger.info(f"AutoCAD Mock Mode: {os.environ.get('AUTOCAD_MOCK_MODE', 'Not Set')}")
    
    return logger

def main():
    """Main application entry point with full logging."""
    # Set up logging first
    logger = setup_logging()
    
    try:
        logger.info("Starting Spiral Stair UI with real AutoCAD connection...")
        
        # Import UI after setting up logging
        from ui.main_ui import main as ui_main
        
        logger.info("UI module imported successfully")
        logger.info("Launching UI...")
        
        # Launch the UI
        ui_main()
        
        logger.info("UI closed normally")
        
    except Exception as e:
        logger.error(f"Error launching UI: {str(e)}", exc_info=True)
        print(f"Failed to launch UI: {str(e)}")
        # Let's also provide more user-friendly error messages
        if "AutoCAD" in str(e):
            print("\nAutoCAD Connection Error:")
            print("- Make sure AutoCAD 2025 is installed and running")
            print("- Check that AutoCAD COM interface is enabled")
            print("- Try launching AutoCAD first, then run this script again")
            print("- If you want to test without AutoCAD, set AUTOCAD_MOCK_MODE=true")
        sys.exit(1)
    finally:
        logger.info("=== Spiral Stair UI Launcher Finished ===")

if __name__ == "__main__":
    main()