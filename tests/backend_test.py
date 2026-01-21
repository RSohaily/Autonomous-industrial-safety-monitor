import requests
import sys
import base64
import json
from datetime import datetime
from io import BytesIO
from PIL import Image
import os

class WarehouseVisionAPITester:
    def __init__(self, base_url="https://vision-warehouse.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            
            if success:
                print(f"   Status: {response.status_code} ✅")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    self.log_test(name, True)
                    return True, response_data
                except:
                    self.log_test(name, True, "Non-JSON response")
                    return True, response.text
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                self.log_test(name, False, error_msg)
                return False, {}

        except requests.exceptions.Timeout:
            error_msg = f"Request timeout after {timeout}s"
            self.log_test(name, False, error_msg)
            return False, {}
        except Exception as e:
            error_msg = f"Request error: {str(e)}"
            self.log_test(name, False, error_msg)
            return False, {}

    def create_test_image_base64(self):
        """Create a simple test image with visual features as base64"""
        # Create a 200x200 image with some visual features (not blank)
        img = Image.new('RGB', (200, 200), color='white')
        
        # Add some visual features - draw rectangles to simulate components
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # Draw some rectangles to simulate bolts/components
        draw.rectangle([50, 50, 80, 80], fill='gray', outline='black')
        draw.rectangle([120, 60, 150, 90], fill='silver', outline='black')
        draw.rectangle([70, 120, 100, 150], fill='darkgray', outline='black')
        
        # Add some lines to simulate hazards
        draw.line([10, 180, 190, 180], fill='red', width=3)
        draw.line([180, 10, 180, 190], fill='orange', width=2)
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_base64

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )

    def test_stats_endpoint(self):
        """Test stats endpoint"""
        return self.run_test(
            "Stats Endpoint",
            "GET", 
            "stats",
            200
        )

    def test_history_endpoint(self):
        """Test history endpoint"""
        return self.run_test(
            "History Endpoint",
            "GET",
            "history", 
            200
        )

    def test_analyze_endpoint(self):
        """Test image analysis endpoint"""
        print("\n🖼️  Creating test image with visual features...")
        test_image_base64 = self.create_test_image_base64()
        
        test_data = {
            "image_base64": test_image_base64,
            "image_name": f"test_warehouse_image_{datetime.now().strftime('%H%M%S')}.jpg"
        }
        
        print(f"   Image size: {len(test_image_base64)} characters")
        print("   Image contains: rectangles (components) and lines (hazards)")
        
        # Use longer timeout for AI analysis
        return self.run_test(
            "Image Analysis Endpoint",
            "POST",
            "analyze",
            200,
            data=test_data,
            timeout=60  # Longer timeout for AI processing
        )

    def validate_analysis_response(self, response_data):
        """Validate the structure of analysis response"""
        required_fields = ['id', 'timestamp', 'image_name', 'detected_items', 'overall_safety_score', 'summary']
        
        print("\n🔍 Validating analysis response structure...")
        
        for field in required_fields:
            if field not in response_data:
                self.log_test(f"Analysis Response - {field} field", False, f"Missing field: {field}")
                return False
            else:
                print(f"   ✅ {field}: present")
        
        # Validate detected_items structure
        if isinstance(response_data.get('detected_items'), list):
            print(f"   ✅ detected_items: list with {len(response_data['detected_items'])} items")
            
            if len(response_data['detected_items']) > 0:
                item = response_data['detected_items'][0]
                item_fields = ['category', 'name', 'description', 'confidence', 'priority', 'action']
                
                for field in item_fields:
                    if field in item:
                        print(f"   ✅ item.{field}: {item[field]}")
                    else:
                        self.log_test(f"Analysis Response - item.{field}", False, f"Missing item field: {field}")
                        return False
        else:
            self.log_test("Analysis Response - detected_items structure", False, "detected_items is not a list")
            return False
        
        # Validate safety score
        valid_scores = ['Safe', 'Caution', 'Danger', 'Unknown']
        safety_score = response_data.get('overall_safety_score')
        if safety_score in valid_scores:
            print(f"   ✅ overall_safety_score: {safety_score}")
        else:
            self.log_test("Analysis Response - safety score", False, f"Invalid safety score: {safety_score}")
            return False
        
        self.log_test("Analysis Response Structure", True, "All required fields present and valid")
        return True

def main():
    print("🏭 WAREHOUSE VISION AI - BACKEND API TESTING")
    print("=" * 60)
    
    tester = WarehouseVisionAPITester()
    
    # Test basic endpoints first
    print("\n📡 TESTING BASIC ENDPOINTS")
    print("-" * 40)
    
    success, root_data = tester.test_root_endpoint()
    if not success:
        print("❌ Root endpoint failed - API may be down")
        return 1
    
    tester.test_stats_endpoint()
    tester.test_history_endpoint()
    
    # Test image analysis (the main feature)
    print("\n🤖 TESTING AI VISION ANALYSIS")
    print("-" * 40)
    
    success, analysis_data = tester.test_analyze_endpoint()
    if success and analysis_data:
        # Validate the analysis response structure
        tester.validate_analysis_response(analysis_data)
        
        # Print some analysis results for verification
        print(f"\n📊 ANALYSIS RESULTS PREVIEW:")
        print(f"   Safety Score: {analysis_data.get('overall_safety_score', 'N/A')}")
        print(f"   Items Detected: {len(analysis_data.get('detected_items', []))}")
        print(f"   Summary: {analysis_data.get('summary', 'N/A')[:100]}...")
        
        if analysis_data.get('detected_items'):
            print(f"   First Item: {analysis_data['detected_items'][0].get('name', 'N/A')}")
    
    # Test stats again to see if they updated
    print("\n📈 TESTING STATS AFTER ANALYSIS")
    print("-" * 40)
    success, stats_data = tester.test_stats_endpoint()
    if success and stats_data:
        print(f"   Total Analyses: {stats_data.get('total_analyses', 0)}")
        print(f"   Safe: {stats_data.get('safe_count', 0)}")
        print(f"   Caution: {stats_data.get('caution_count', 0)}")
        print(f"   Danger: {stats_data.get('danger_count', 0)}")
    
    # Final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 ALL TESTS PASSED - Backend API is working correctly!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - Check the details above")
        
        # Print failed tests summary
        failed_tests = [r for r in tester.test_results if not r['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())