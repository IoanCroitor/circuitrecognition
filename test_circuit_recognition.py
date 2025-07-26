#!/usr/bin/env python3
"""
Test script for the circuit recognition service
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.circuit_recognizer import CircuitRecognitionService

def test_circuit_recognition():
    """Test the circuit recognition service with a sample image"""
    
    print("Testing Circuit Recognition Service...")
    print("=" * 50)
    
    # Initialize the service
    try:
        service = CircuitRecognitionService()
        print("✓ CircuitRecognitionService initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize service: {e}")
        return False
    
    # Test image path
    test_image_path = "raw_img.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"✗ Test image not found: {test_image_path}")
        return False
    
    print(f"✓ Found test image: {test_image_path}")
    
    try:
        # Read the test image
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
        
        print(f"✓ Loaded image data ({len(image_data)} bytes)")
        
        # Test with ASC format
        print("\nTesting ASC format output...")
        asc_result = service.process_image(image_data, output_format="asc")
        
        if asc_result and 'data' in asc_result:
            print("✓ ASC processing successful")
            print(f"  - Format: {asc_result['format']}")
            print(f"  - Processing time: {asc_result['processing_time']:.2f}s")
            print(f"  - Output length: {len(asc_result['data'])} characters")
            
            # Save ASC output
            with open("test_output.asc", "w") as f:
                f.write(asc_result['data'])
            print("✓ ASC output saved to test_output.asc")
        
        # Test with JSON format
        print("\nTesting JSON format output...")
        json_result = service.process_image(image_data, output_format="json")
        
        if json_result and 'data' in json_result:
            print("✓ JSON processing successful")
            print(f"  - Format: {json_result['format']}")
            print(f"  - Processing time: {json_result['processing_time']:.2f}s")
            
            # Save JSON output
            import json
            with open("test_output.json", "w") as f:
                json.dump(json_result['data'], f, indent=2)
            print("✓ JSON output saved to test_output.json")
        
        print("\n" + "=" * 50)
        print("✓ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_circuit_recognition()
    sys.exit(0 if success else 1)