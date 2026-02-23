import requests
import sys

try:
    print("Checking: http://localhost:7990/web/external-images/")
    response = requests.get('http://localhost:7990/web/external-images/', timeout=5)
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Length: {len(response.text)} chars")
    
    if response.status_code == 200:
        print("SUCCESS: Page is available")
        # Check for key elements
        html = response.text
        if 'Внешние изображения товаров' in html:
            print("Found: Page title")
        if 'product-card' in html:
            print("Found: Product cards")
        if 'img-thumbnail' in html:
            print("Found: Image thumbnails")
    else:
        print(f"ERROR: HTTP {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to localhost:7990")
    print("Make sure the app is running")
except Exception as e:
    print(f"ERROR: {e}")