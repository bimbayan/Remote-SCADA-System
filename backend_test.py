#!/usr/bin/env python3
"""Backend API tests for SolarisSCADA - Focus on /api/geocode endpoint with Nominatim fallback."""

import os
import sys
import httpx
from pathlib import Path

# Load REACT_APP_BACKEND_URL from frontend/.env
frontend_env = Path("/app/frontend/.env")
BACKEND_URL = None
if frontend_env.exists():
    for line in frontend_env.read_text().splitlines():
        if line.startswith("REACT_APP_BACKEND_URL="):
            BACKEND_URL = line.split("=", 1)[1].strip()
            break

if not BACKEND_URL:
    print("❌ FATAL: REACT_APP_BACKEND_URL not found in /app/frontend/.env")
    sys.exit(1)

API_BASE = f"{BACKEND_URL}/api"
print(f"🔗 Testing against: {API_BASE}\n")


def test_geocode_jadavpur_university():
    """BUG-SPECIFIC: Jadavpur University must return >=1 result with lat≈22.5, lon≈88.3."""
    print("TEST 1: Jadavpur University (landmark, should use Nominatim fallback)")
    url = f"{API_BASE}/geocode"
    params = {"q": "Jadavpur University", "count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) >= 1, f"Expected >=1 result for 'Jadavpur University', got {len(results)}"
        
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        name = first["name"].lower()
        
        # Verify coordinates are in Kolkata area (Jadavpur University is at ~22.5, 88.3)
        assert 22.0 <= lat <= 23.0, f"Expected lat≈22.5 (±0.5), got {lat}"
        assert 88.0 <= lon <= 89.0, f"Expected lon≈88.3 (±0.5), got {lon}"
        
        # Verify name contains "jadavpur"
        assert "jadavpur" in name, f"Expected name to contain 'jadavpur', got '{first['name']}'"
        
        print(f"  ✅ PASSED - Found '{first['name']}' at ({lat}, {lon})")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_geocode_eiffel_tower():
    """Landmark test: Eiffel Tower should return result at lat≈48.85, lon≈2.29."""
    print("TEST 2: Eiffel Tower (landmark)")
    url = f"{API_BASE}/geocode"
    params = {"q": "Eiffel Tower", "count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) >= 1, f"Expected >=1 result for 'Eiffel Tower', got {len(results)}"
        
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        
        # Eiffel Tower is at approximately 48.858, 2.294
        assert 48.5 <= lat <= 49.2, f"Expected lat≈48.85 (±0.35), got {lat}"
        assert 2.0 <= lon <= 2.6, f"Expected lon≈2.29 (±0.31), got {lon}"
        
        print(f"  ✅ PASSED - Found '{first['name']}' at ({lat}, {lon})")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_geocode_times_square():
    """Landmark test: Times Square New York should return result at lat≈40.75, lon≈-73.98."""
    print("TEST 3: Times Square New York (landmark)")
    url = f"{API_BASE}/geocode"
    params = {"q": "Times Square New York", "count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) >= 1, f"Expected >=1 result for 'Times Square New York', got {len(results)}"
        
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        
        # Times Square is at approximately 40.758, -73.985
        assert 40.5 <= lat <= 41.0, f"Expected lat≈40.75 (±0.25), got {lat}"
        assert -74.3 <= lon <= -73.7, f"Expected lon≈-73.98 (±0.28), got {lon}"
        
        print(f"  ✅ PASSED - Found '{first['name']}' at ({lat}, {lon})")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_geocode_sealdah():
    """Landmark test: Sealdah should return a Kolkata-area result."""
    print("TEST 4: Sealdah (Kolkata landmark)")
    url = f"{API_BASE}/geocode"
    params = {"q": "Sealdah", "count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) >= 1, f"Expected >=1 result for 'Sealdah', got {len(results)}"
        
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        
        # Sealdah is in Kolkata area (approximately 22.57, 88.37)
        assert 22.0 <= lat <= 23.0, f"Expected Kolkata-area lat (22-23), got {lat}"
        assert 88.0 <= lon <= 89.0, f"Expected Kolkata-area lon (88-89), got {lon}"
        
        print(f"  ✅ PASSED - Found '{first['name']}' at ({lat}, {lon})")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_geocode_bengaluru_regression():
    """REGRESSION: Bengaluru should still work via Open-Meteo (Tier 1)."""
    print("TEST 5: Bengaluru (city, regression test)")
    url = f"{API_BASE}/geocode"
    params = {"q": "Bengaluru", "count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) >= 1, f"Expected >=1 result for 'Bengaluru', got {len(results)}"
        
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        
        # Bengaluru is at approximately 12.97, 77.59
        assert 12.5 <= lat <= 13.5, f"Expected lat≈12.97, got {lat}"
        assert 77.0 <= lon <= 78.0, f"Expected lon≈77.59, got {lon}"
        
        print(f"  ✅ PASSED - Found '{first['name']}' at ({lat}, {lon})")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_geocode_berlin_regression():
    """REGRESSION: Berlin should still work via Open-Meteo (Tier 1)."""
    print("TEST 6: Berlin (city, regression test)")
    url = f"{API_BASE}/geocode"
    params = {"q": "Berlin", "count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) >= 1, f"Expected >=1 result for 'Berlin', got {len(results)}"
        
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        
        # Berlin is at approximately 52.52, 13.41
        assert 52.0 <= lat <= 53.0, f"Expected lat≈52.52, got {lat}"
        assert 13.0 <= lon <= 14.0, f"Expected lon≈13.41, got {lon}"
        
        print(f"  ✅ PASSED - Found '{first['name']}' at ({lat}, {lon})")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_geocode_tokyo_regression():
    """REGRESSION: Tokyo should still work via Open-Meteo (Tier 1)."""
    print("TEST 7: Tokyo (city, regression test)")
    url = f"{API_BASE}/geocode"
    params = {"q": "Tokyo", "count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) >= 1, f"Expected >=1 result for 'Tokyo', got {len(results)}"
        
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        
        # Tokyo is at approximately 35.69, 139.69
        assert 35.0 <= lat <= 36.0, f"Expected lat≈35.69, got {lat}"
        assert 139.0 <= lon <= 140.0, f"Expected lon≈139.69, got {lon}"
        
        print(f"  ✅ PASSED - Found '{first['name']}' at ({lat}, {lon})")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_geocode_phoenix_regression():
    """REGRESSION: Phoenix should still work via Open-Meteo (Tier 1)."""
    print("TEST 8: Phoenix (city, regression test)")
    url = f"{API_BASE}/geocode"
    params = {"q": "Phoenix", "count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) >= 1, f"Expected >=1 result for 'Phoenix', got {len(results)}"
        
        # Phoenix, Arizona is at approximately 33.45, -112.07
        # Just verify we got results, don't enforce exact coordinates since there are multiple Phoenix cities
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        
        print(f"  ✅ PASSED - Found '{first['name']}' at ({lat}, {lon})")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_geocode_validation_short_query():
    """REGRESSION: 1-char query should return 422."""
    print("TEST 9: Validation - 1-char query (should return 422)")
    url = f"{API_BASE}/geocode"
    params = {"q": "a", "count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 422, f"Expected 422 for 1-char query, got {resp.status_code}"
        
        print(f"  ✅ PASSED - Correctly rejected 1-char query with 422")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_geocode_validation_missing_query():
    """REGRESSION: Missing q parameter should return 422."""
    print("TEST 10: Validation - missing q parameter (should return 422)")
    url = f"{API_BASE}/geocode"
    params = {"count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 422, f"Expected 422 for missing q, got {resp.status_code}"
        
        print(f"  ✅ PASSED - Correctly rejected missing q with 422")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_geocode_gibberish():
    """REGRESSION: Pure gibberish should return empty results array."""
    print("TEST 11: Gibberish query (should return empty results)")
    url = f"{API_BASE}/geocode"
    params = {"q": "zzzzzz9999xxxxqqqqq", "count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) == 0, f"Expected 0 results for gibberish, got {len(results)}"
        
        print(f"  ✅ PASSED - Correctly returned empty results for gibberish")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_geocode_response_shape():
    """Response shape check: all results must have {name, latitude, longitude}."""
    print("TEST 12: Response shape validation")
    url = f"{API_BASE}/geocode"
    params = {"q": "London", "count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) >= 1, f"Expected >=1 result for 'London', got {len(results)}"
        
        for i, result in enumerate(results):
            assert "name" in result, f"Result {i} missing 'name' field"
            assert "latitude" in result, f"Result {i} missing 'latitude' field"
            assert "longitude" in result, f"Result {i} missing 'longitude' field"
            assert isinstance(result["name"], str), f"Result {i} 'name' is not a string"
            assert isinstance(result["latitude"], (int, float)), f"Result {i} 'latitude' is not a number"
            assert isinstance(result["longitude"], (int, float)), f"Result {i} 'longitude' is not a number"
        
        print(f"  ✅ PASSED - All {len(results)} results have required fields (name, latitude, longitude)")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_geocode_forecast_chain():
    """OPTIONAL: Chain /api/geocode with /api/forecast using Jadavpur University coordinates."""
    print("TEST 13: Chain geocode → forecast (Jadavpur University)")
    
    try:
        # Step 1: Get Jadavpur University coordinates
        geocode_url = f"{API_BASE}/geocode"
        geocode_params = {"q": "Jadavpur University", "count": 5}
        resp = httpx.get(geocode_url, params=geocode_params, timeout=30.0)
        assert resp.status_code == 200, f"Geocode failed: {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        assert len(results) >= 1, "No results for Jadavpur University"
        
        lat = results[0]["latitude"]
        lon = results[0]["longitude"]
        print(f"  → Got coordinates: ({lat}, {lon})")
        
        # Step 2: Call /api/forecast with those coordinates
        forecast_url = f"{API_BASE}/forecast"
        forecast_params = {"lat": lat, "lon": lon, "size_kw": 500, "hours": 48}
        resp = httpx.get(forecast_url, params=forecast_params, timeout=30.0)
        assert resp.status_code == 200, f"Forecast failed: {resp.status_code}"
        data = resp.json()
        
        # Verify response structure
        assert "rows" in data, "Missing 'rows' in forecast response"
        assert "totals" in data, "Missing 'totals' in forecast response"
        rows = data["rows"]
        totals = data["totals"]
        
        assert len(rows) == 48, f"Expected 48 rows, got {len(rows)}"
        assert "peak_kw" in totals, "Missing 'peak_kw' in totals"
        
        # Verify at least some daytime rows have peak_kw > 0
        peak_kw = totals["peak_kw"]
        assert peak_kw > 0, f"Expected peak_kw > 0 for daytime hours, got {peak_kw}"
        
        print(f"  ✅ PASSED - Forecast returned 48 rows with peak_kw={peak_kw}")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def main():
    """Run all tests and report results."""
    print("=" * 80)
    print("BACKEND API TESTS - /api/geocode with Nominatim Fallback")
    print("=" * 80)
    print()
    
    tests = [
        # BUG-SPECIFIC
        ("Jadavpur University (BUG FIX)", test_geocode_jadavpur_university),
        
        # LANDMARK TESTS
        ("Eiffel Tower", test_geocode_eiffel_tower),
        ("Times Square New York", test_geocode_times_square),
        ("Sealdah", test_geocode_sealdah),
        
        # REGRESSION - CITIES
        ("Bengaluru (regression)", test_geocode_bengaluru_regression),
        ("Berlin (regression)", test_geocode_berlin_regression),
        ("Tokyo (regression)", test_geocode_tokyo_regression),
        ("Phoenix (regression)", test_geocode_phoenix_regression),
        
        # REGRESSION - VALIDATION
        ("1-char validation (regression)", test_geocode_validation_short_query),
        ("Missing q validation (regression)", test_geocode_validation_missing_query),
        
        # REGRESSION - GIBBERISH
        ("Gibberish query (regression)", test_geocode_gibberish),
        
        # RESPONSE SHAPE
        ("Response shape validation", test_geocode_response_shape),
        
        # OPTIONAL CHAIN
        ("Geocode → Forecast chain", test_geocode_forecast_chain),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    
    print(f"\n✅ PASSED: {passed}/{len(results)}")
    print(f"❌ FAILED: {failed}/{len(results)}\n")
    
    if failed > 0:
        print("Failed tests:")
        for name, result in results:
            if not result:
                print(f"  - {name}")
        print()
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
