import requests
import sys
from datetime import datetime
import json

class CS2ProjectionAPITester:
    def __init__(self, base_url="https://gamestats-compare.preview.emergentagent.com"):
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
        
        result = {
            "test": name,
            "status": "PASS" if success else "FAIL",
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {name}: {details}")
        return success

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {response.status_code}, Message: {data.get('message', 'N/A')}"
            else:
                details = f"Status: {response.status_code}"
                
            return self.log_test("API Root Endpoint", success, details)
        except Exception as e:
            return self.log_test("API Root Endpoint", False, f"Error: {str(e)}")

    def test_get_matches(self):
        """Test get matches endpoint"""
        try:
            response = requests.get(f"{self.api_url}/matches", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                matches_count = len(data)
                
                # Validate structure
                if matches_count > 0:
                    first_match = data[0]
                    required_fields = ['match', 'projections', 'last_updated']
                    has_required_fields = all(field in first_match for field in required_fields)
                    
                    if has_required_fields:
                        match_data = first_match['match']
                        projections_data = first_match['projections']
                        
                        # Check match structure
                        match_fields = ['id', 'team1', 'team2', 'tournament', 'start_time', 'map1', 'map2']
                        match_valid = all(field in match_data for field in match_fields)
                        
                        # Check projections structure
                        projections_valid = True
                        if projections_data:
                            proj_fields = ['match_id', 'player_name', 'team', 'stat_type', 'projected_value', 'confidence', 'dfs_lines']
                            projections_valid = all(field in projections_data[0] for field in proj_fields)
                        
                        if match_valid and projections_valid:
                            details = f"Status: {response.status_code}, Matches: {matches_count}, Projections: {len(projections_data)}"
                        else:
                            success = False
                            details = f"Invalid data structure - Match valid: {match_valid}, Projections valid: {projections_valid}"
                    else:
                        success = False
                        details = f"Missing required fields: {required_fields}"
                else:
                    details = f"Status: {response.status_code}, No matches returned"
            else:
                details = f"Status: {response.status_code}"
                
            return self.log_test("Get Matches", success, details)
        except Exception as e:
            return self.log_test("Get Matches", False, f"Error: {str(e)}")

    def test_get_stats(self):
        """Test get stats endpoint"""
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['total_projections', 'value_opportunities', 'avg_confidence', 'last_refresh']
                has_required_fields = all(field in data for field in required_fields)
                
                if has_required_fields:
                    details = f"Status: {response.status_code}, Projections: {data['total_projections']}, Value Ops: {data['value_opportunities']}, Avg Confidence: {data['avg_confidence']}%"
                else:
                    success = False
                    details = f"Missing required fields: {required_fields}"
            else:
                details = f"Status: {response.status_code}"
                
            return self.log_test("Get Stats", success, details)
        except Exception as e:
            return self.log_test("Get Stats", False, f"Error: {str(e)}")

    def test_match_detail(self):
        """Test match detail endpoint"""
        try:
            # First get matches to get a valid match ID
            matches_response = requests.get(f"{self.api_url}/matches", timeout=10)
            if matches_response.status_code != 200:
                return self.log_test("Match Detail", False, "Could not get matches for testing")
            
            matches_data = matches_response.json()
            if not matches_data:
                return self.log_test("Match Detail", False, "No matches available for testing")
            
            match_id = matches_data[0]['match']['id']
            
            # Test match detail endpoint
            response = requests.get(f"{self.api_url}/matches/{match_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['match', 'projections', 'last_updated']
                has_required_fields = all(field in data for field in required_fields)
                
                if has_required_fields:
                    projections_count = len(data['projections'])
                    details = f"Status: {response.status_code}, Match ID: {match_id[:8]}..., Projections: {projections_count}"
                else:
                    success = False
                    details = f"Missing required fields: {required_fields}"
            else:
                details = f"Status: {response.status_code}"
                
            return self.log_test("Match Detail", success, details)
        except Exception as e:
            return self.log_test("Match Detail", False, f"Error: {str(e)}")

    def test_refresh_data(self):
        """Test refresh data endpoint"""
        try:
            response = requests.post(f"{self.api_url}/refresh", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['status', 'matches_count', 'projections_count', 'last_updated']
                has_required_fields = all(field in data for field in required_fields)
                
                if has_required_fields and data['status'] == 'success':
                    details = f"Status: {response.status_code}, Matches: {data['matches_count']}, Projections: {data['projections_count']}"
                else:
                    success = False
                    details = f"Invalid response structure or status: {data.get('status', 'unknown')}"
            else:
                details = f"Status: {response.status_code}"
                
            return self.log_test("Refresh Data", success, details)
        except Exception as e:
            return self.log_test("Refresh Data", False, f"Error: {str(e)}")

    def test_invalid_match_id(self):
        """Test invalid match ID handling"""
        try:
            invalid_id = "invalid-match-id-12345"
            response = requests.get(f"{self.api_url}/matches/{invalid_id}", timeout=10)
            success = response.status_code == 404
            
            details = f"Status: {response.status_code} (Expected 404 for invalid ID)"
            return self.log_test("Invalid Match ID Handling", success, details)
        except Exception as e:
            return self.log_test("Invalid Match ID Handling", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting CS2 Projection API Tests...")
        print(f"🎯 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run tests
        self.test_api_root()
        self.test_get_matches()
        self.test_get_stats()
        self.test_match_detail()
        self.test_refresh_data()
        self.test_invalid_match_id()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Tests completed: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed!")
            return False

def main():
    tester = CS2ProjectionAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_tests': tester.tests_run,
                'passed_tests': tester.tests_passed,
                'success_rate': f"{(tester.tests_passed/tester.tests_run)*100:.1f}%" if tester.tests_run > 0 else "0%",
                'timestamp': datetime.now().isoformat()
            },
            'test_results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())