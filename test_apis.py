#!/usr/bin/env python3
"""
API Verification Script - Test free APIs twice and extract partner recommendations
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

class APITester:
    def __init__(self):
        self.results = []
        self.partner_apis = {}
        
    def test_api(self, name: str, url: str, method: str = "GET", 
                 headers: Optional[Dict] = None, test_count: int = 2) -> Dict[str, Any]:
        """Test an API endpoint multiple times"""
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"URL: {url}")
        print(f"{'='*60}")
        
        test_results = []
        
        for attempt in range(1, test_count + 1):
            print(f"\nAttempt {attempt}/{test_count}...")
            
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=10)
                else:
                    response = requests.request(method, url, headers=headers, timeout=10)
                
                elapsed = time.time() - start_time
                
                result = {
                    "attempt": attempt,
                    "status_code": response.status_code,
                    "success": 200 <= response.status_code < 300,
                    "response_time": round(elapsed, 2),
                    "content_length": len(response.content),
                    "headers": dict(response.headers),
                    "error": None
                }
                
                # Try to parse JSON
                try:
                    result["sample_data"] = response.json()
                    if isinstance(result["sample_data"], dict):
                        result["sample_data"] = {k: v for k, v in list(result["sample_data"].items())[:3]}
                    elif isinstance(result["sample_data"], list):
                        result["sample_data"] = result["sample_data"][:2]
                except:
                    result["sample_data"] = response.text[:200]
                
                test_results.append(result)
                
                print(f"  ✓ Status: {response.status_code}")
                print(f"  ✓ Response Time: {elapsed:.2f}s")
                print(f"  ✓ Content Length: {len(response.content)} bytes")
                
                # Extract partner/related API links from response
                self._extract_partner_apis(name, response)
                
                time.sleep(1)  # Rate limiting
                
            except requests.exceptions.Timeout:
                result = {
                    "attempt": attempt,
                    "status_code": None,
                    "success": False,
                    "response_time": 10.0,
                    "error": "Timeout after 10s"
                }
                test_results.append(result)
                print(f"  ✗ Timeout")
                
            except requests.exceptions.ConnectionError as e:
                result = {
                    "attempt": attempt,
                    "status_code": None,
                    "success": False,
                    "error": f"Connection Error: {str(e)[:100]}"
                }
                test_results.append(result)
                print(f"  ✗ Connection Error")
                
            except Exception as e:
                result = {
                    "attempt": attempt,
                    "status_code": None,
                    "success": False,
                    "error": str(e)[:200]
                }
                test_results.append(result)
                print(f"  ✗ Error: {str(e)[:100]}")
        
        # Calculate overall reliability
        success_count = sum(1 for r in test_results if r.get("success", False))
        reliability = (success_count / test_count) * 100
        
        avg_response_time = sum(r.get("response_time", 0) for r in test_results if r.get("response_time")) / test_count
        
        final_result = {
            "name": name,
            "url": url,
            "method": method,
            "test_count": test_count,
            "success_count": success_count,
            "reliability": reliability,
            "avg_response_time": round(avg_response_time, 2),
            "verified": reliability >= 50,  # At least 50% success rate
            "test_results": test_results,
            "tested_at": datetime.utcnow().isoformat()
        }
        
        print(f"\n{'─'*60}")
        print(f"Reliability: {reliability}% ({success_count}/{test_count} successful)")
        print(f"Avg Response Time: {avg_response_time:.2f}s")
        print(f"Verified: {'✓ YES' if final_result['verified'] else '✗ NO'}")
        
        self.results.append(final_result)
        return final_result
    
    def _extract_partner_apis(self, source_name: str, response: requests.Response):
        """Extract partner/related API links from response"""
        try:
            # Check headers for API links
            link_header = response.headers.get('Link', '')
            if 'api' in link_header.lower():
                if source_name not in self.partner_apis:
                    self.partner_apis[source_name] = []
                self.partner_apis[source_name].append(link_header)
            
            # Check JSON response for API references
            try:
                data = response.json()
                if isinstance(data, dict):
                    for key, value in data.items():
                        if 'api' in key.lower() or 'url' in key.lower():
                            if isinstance(value, str) and ('http' in value or 'api' in value):
                                if source_name not in self.partner_apis:
                                    self.partner_apis[source_name] = []
                                self.partner_apis[source_name].append(f"{key}: {value}")
            except:
                pass
                
        except Exception as e:
            pass
    
    def save_results(self, filename: str = "verification_results.json"):
        """Save test results to JSON file"""
        output = {
            "tested_at": datetime.utcnow().isoformat(),
            "total_apis_tested": len(self.results),
            "verified_count": sum(1 for r in self.results if r["verified"]),
            "failed_count": sum(1 for r in self.results if not r["verified"]),
            "partner_apis_discovered": len(self.partner_apis),
            "results": self.results,
            "partner_network": self.partner_apis
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"Results saved to: {filename}")
        print(f"Total APIs Tested: {len(self.results)}")
        print(f"Verified: {output['verified_count']}")
        print(f"Failed: {output['failed_count']}")
        print(f"Partner APIs Discovered: {len(self.partner_apis)}")
        print(f"{'='*60}")


def main():
    """Test top priority free APIs"""
    tester = APITester()
    
    # Top priority APIs to test
    apis_to_test = [
        # Crypto/Finance
        ("CoinGecko - Bitcoin Price", "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"),
        ("Binance - BTC Price", "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"),
        ("CoinCap - Assets", "https://api.coincap.io/v2/assets?limit=5"),
        
        # Security
        ("NVD - Recent CVEs", "https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=5"),
        
        # Weather/Environment
        ("Open-Meteo - Weather", "https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current_weather=true"),
        ("USGS - Earthquakes", "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"),
        
        # Government
        ("World Bank - GDP Indicator", "https://api.worldbank.org/v2/country/USA/indicator/NY.GDP.MKTP.CD?format=json&per_page=1"),
        
        # Tech/News
        ("HackerNews - Top Stories", "https://hacker-news.firebaseio.com/v0/topstories.json"),
        ("GitHub - Public Events", "https://api.github.com/events"),
        
        # Transportation
        ("Open Sky - Aircraft", "https://opensky-network.org/api/states/all?lamin=40&lomin=-75&lamax=41&lomax=-74"),
    ]
    
    print("Starting API Verification Process...")
    print(f"Testing {len(apis_to_test)} APIs (2 attempts each)")
    
    for name, url in apis_to_test:
        tester.test_api(name, url, test_count=2)
    
    # Save results
    tester.save_results("/tmp/free-apis-verified/verification_results.json")
    
    # Generate summary report
    verified = [r for r in tester.results if r["verified"]]
    failed = [r for r in tester.results if not r["verified"]]
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    print(f"\n✓ VERIFIED APIs ({len(verified)}):")
    for r in verified:
        print(f"  - {r['name']}: {r['reliability']}% reliable, {r['avg_response_time']}s avg")
    
    if failed:
        print(f"\n✗ FAILED APIs ({len(failed)}):")
        for r in failed:
            print(f"  - {r['name']}: {r['reliability']}% reliable")
    
    if tester.partner_apis:
        print(f"\n🔗 PARTNER APIs DISCOVERED ({len(tester.partner_apis)}):")
        for source, partners in tester.partner_apis.items():
            print(f"  {source}:")
            for partner in partners[:3]:
                print(f"    - {partner[:80]}")


if __name__ == "__main__":
    main()
