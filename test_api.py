import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "test-key-123"

# Test health check
def test_health():
    print("Testing health check...")
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/health", headers=headers)
    print(f"Health check response: {response.status_code} - {response.json()}")

# Test ASC to JSON conversion
def test_asc_to_json():
    print("\nTesting ASC to JSON conversion...")
    headers = {"X-API-Key": API_KEY}
    
    # Read the example ASC file
    with open("example.asc", "rb") as f:
        files = {"file": ("example.asc", f, "text/plain")}
        response = requests.post(f"{BASE_URL}/asc-to-json/convert", headers=headers, files=files)
    
    print(f"ASC to JSON response: {response.status_code}")
    if response.status_code == 200:
        print("Response data:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")

# Test ASC parsing
def test_parse_asc():
    print("\nTesting ASC parsing...")
    headers = {"X-API-Key": API_KEY}
    
    # Read the example ASC file
    with open("example.asc", "rb") as f:
        files = {"file": ("example.asc", f, "text/plain")}
        response = requests.post(f"{BASE_URL}/asc-to-json/parse", headers=headers, files=files)
    
    print(f"ASC parsing response: {response.status_code}")
    if response.status_code == 200:
        print("Response data:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
# Test circuit recognition
def test_circuit_recognition():
    print("\nTesting circuit recognition...")
    headers = {"X-API-Key": API_KEY}
    
    # Test with ASC output format
    with open("raw_img.jpg", "rb") as f:
        files = {"file": ("raw_img.jpg", f, "image/jpeg")}
        data = {"output_format": "asc"}
        response = requests.post(f"{BASE_URL}/recognize-circuit", headers=headers, files=files, data=data)
    
    print(f"Circuit recognition (ASC) response: {response.status_code}")
    if response.status_code == 200:
        print("Response data:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    
    # Test with JSON output format
    with open("raw_img.jpg", "rb") as f:
        files = {"file": ("raw_img.jpg", f, "image/jpeg")}
        data = {"output_format": "json"}
        response = requests.post(f"{BASE_URL}/recognize-circuit", headers=headers, files=files, data=data)
    
    print(f"\nCircuit recognition (JSON) response: {response.status_code}")
    if response.status_code == 200:
        print("Response data:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")

# Test circuit recognition with parsing
def test_circuit_recognition_parse():
    print("\nTesting circuit recognition with parsing...")
    headers = {"X-API-Key": API_KEY}
    
    with open("raw_img.jpg", "rb") as f:
        files = {"file": ("raw_img.jpg", f, "image/jpeg")}
        response = requests.post(f"{BASE_URL}/recognize-circuit/parse", headers=headers, files=files)
    
    print(f"Circuit recognition (parsed) response: {response.status_code}")
    if response.status_code == 200:
        print("Response data:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_health()
    test_asc_to_json()
    test_parse_asc()
    test_circuit_recognition()
    test_circuit_recognition_parse()