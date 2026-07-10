#!/usr/bin/env python3
"""Backend API tests for USER BUG FIX #2 - Testing /api/geocode with count=1 specifically."""

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


def test_jadavpur_university_count1_consistency():
    """BUG-SPECIFIC: Test Jadavpur University with count=1, run 3 times for consistency."""
    print("TEST 1: Jadavpur University with count=1 (3 runs for consistency)")
    url = f"{API_BASE}/geocode"
    
    all_passed = True
    for run in range(1, 4):
        print(f"  Run {run}/3:")
        params = {"q": "Jadavpur University", "count": 1}
        
        try:
            resp = httpx.get(url, params=params, timeout=30.0)
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
            data = resp.json()
            results = data.get("results", [])
            
            # MUST return exactly 1 result
            assert len(results) == 1, f"Expected exactly 1 result with count=1, got {len(results)}"
            
            first = results[0]
            lat = first["latitude"]
            lon = first["longitude"]
            name = first["name"]
            
            # Verify coordinates: lat ≈ 22.5 (±0.5), lon ≈ 88.4 (±0.5)
            assert 22.0 <= lat <= 23.0, f"Expected lat≈22.5 (±0.5), got {lat}"
            assert 87.9 <= lon <= 88.9, f"Expected lon≈88.4 (±0.5), got {lon}"
            
            # Verify name contains "Jadavpur"
            assert "jadavpur" in name.lower(), f"Expected name to contain 'Jadavpur', got '{name}'"
            
            print(f"    ✅ Run {run} PASSED - Found '{name}' at ({lat}, {lon})")
        except AssertionError as e:
            print(f"    ❌ Run {run} FAILED - {e}")
            all_passed = False
        except Exception as e:
            print(f"    ❌ Run {run} ERROR - {e}")
            all_passed = False
    
    if all_passed:
        print(f"  ✅ ALL 3 RUNS PASSED - Jadavpur University consistently returns 1 result")
    else:
        print(f"  ❌ SOME RUNS FAILED - Inconsistent behavior detected")
    
    return all_passed


def test_eiffel_tower_count1():
    """Landmark test: Eiffel Tower with count=1 should return exactly 1 result."""
    print("TEST 2: Eiffel Tower with count=1")
    url = f"{API_BASE}/geocode"
    params = {"q": "Eiffel Tower", "count": 1}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) == 1, f"Expected exactly 1 result with count=1, got {len(results)}"
        
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        
        # Eiffel Tower: lat≈48.85, lon≈2.29
        assert 48.35 <= lat <= 49.35, f"Expected lat≈48.85 (±0.5), got {lat}"
        assert 1.79 <= lon <= 2.79, f"Expected lon≈2.29 (±0.5), got {lon}"
        
        print(f"  ✅ PASSED - Found '{first['name']}' at ({lat}, {lon})")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_times_square_count1():
    """Landmark test: Times Square New York with count=1 should return exactly 1 result."""
    print("TEST 3: Times Square New York with count=1")
    url = f"{API_BASE}/geocode"
    params = {"q": "Times Square New York", "count": 1}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) == 1, f"Expected exactly 1 result with count=1, got {len(results)}"
        
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        
        # Times Square: lat≈40.75, lon≈-73.98
        assert 40.25 <= lat <= 41.25, f"Expected lat≈40.75 (±0.5), got {lat}"
        assert -74.48 <= lon <= -73.48, f"Expected lon≈-73.98 (±0.5), got {lon}"
        
        print(f"  ✅ PASSED - Found '{first['name']}' at ({lat}, {lon})")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_statue_of_liberty_count1():
    """Landmark test: Statue of Liberty with count=1 should return exactly 1 result.
    
    Note: Nominatim may return different Statue of Liberty locations (replicas exist).
    The important thing is that count=1 returns exactly 1 result.
    """
    print("TEST 4: Statue of Liberty with count=1")
    url = f"{API_BASE}/geocode"
    params = {"q": "Statue of Liberty", "count": 1}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) == 1, f"Expected exactly 1 result with count=1, got {len(results)}"
        
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        name = first["name"]
        
        # Verify it's a US location and contains "Statue of Liberty"
        assert "statue of liberty" in name.lower(), f"Expected name to contain 'Statue of Liberty', got '{name}'"
        assert first.get("country") == "United States", f"Expected US location, got {first.get('country')}"
        
        print(f"  ✅ PASSED - Found '{name}' at ({lat}, {lon})")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_sealdah_count1():
    """Landmark test: Sealdah with count=1 should return exactly 1 result."""
    print("TEST 5: Sealdah with count=1")
    url = f"{API_BASE}/geocode"
    params = {"q": "Sealdah", "count": 1}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        
        assert len(results) == 1, f"Expected exactly 1 result with count=1, got {len(results)}"
        
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        
        # Sealdah is in Kolkata area: lat≈22.5
        assert 22.0 <= lat <= 23.0, f"Expected Kolkata-area lat≈22.5, got {lat}"
        
        print(f"  ✅ PASSED - Found '{first['name']}' at ({lat}, {lon})")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_landmarks_count5():
    """Test landmarks with count=5 to verify they return up to 5 results."""
    print("TEST 6: Landmarks with count=5 (should return up to 5 results)")
    url = f"{API_BASE}/geocode"
    
    landmarks = [
        ("Jadavpur University", 22.5, 88.4),
        ("Eiffel Tower", 48.85, 2.29),
        ("Times Square New York", 40.75, -73.98),
    ]
    
    all_passed = True
    for landmark_name, expected_lat, expected_lon in landmarks:
        params = {"q": landmark_name, "count": 5}
        
        try:
            resp = httpx.get(url, params=params, timeout=30.0)
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            data = resp.json()
            results = data.get("results", [])
            
            # Should return between 1 and 5 results
            assert 1 <= len(results) <= 5, f"Expected 1-5 results with count=5, got {len(results)}"
            
            print(f"  ✅ '{landmark_name}' returned {len(results)} result(s)")
        except AssertionError as e:
            print(f"  ❌ '{landmark_name}' FAILED - {e}")
            all_passed = False
        except Exception as e:
            print(f"  ❌ '{landmark_name}' ERROR - {e}")
            all_passed = False
    
    if all_passed:
        print(f"  ✅ ALL LANDMARKS PASSED with count=5")
    
    return all_passed


def test_cities_count1_regression():
    """REGRESSION: City queries with count=1 should still work via Open-Meteo Tier 1."""
    print("TEST 7: City queries with count=1 (regression)")
    url = f"{API_BASE}/geocode"
    
    cities = [
        ("Bengaluru", 12.97, 77.59),
        ("Berlin", 52.52, 13.41),
        ("Tokyo", 35.69, 139.69),
        ("Phoenix", 33.45, -112.07),
    ]
    
    all_passed = True
    for city_name, expected_lat, expected_lon in cities:
        params = {"q": city_name, "count": 1}
        
        try:
            resp = httpx.get(url, params=params, timeout=30.0)
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            data = resp.json()
            results = data.get("results", [])
            
            assert len(results) == 1, f"Expected exactly 1 result with count=1, got {len(results)}"
            
            first = results[0]
            lat = first["latitude"]
            lon = first["longitude"]
            
            # Verify coordinates are in expected range (±1 degree tolerance)
            assert abs(lat - expected_lat) <= 1.0, f"Expected lat≈{expected_lat}, got {lat}"
            assert abs(lon - expected_lon) <= 1.0, f"Expected lon≈{expected_lon}, got {lon}"
            
            print(f"  ✅ '{city_name}' at ({lat}, {lon})")
        except AssertionError as e:
            print(f"  ❌ '{city_name}' FAILED - {e}")
            all_passed = False
        except Exception as e:
            print(f"  ❌ '{city_name}' ERROR - {e}")
            all_passed = False
    
    if all_passed:
        print(f"  ✅ ALL CITIES PASSED with count=1")
    
    return all_passed


def test_validation_regression():
    """REGRESSION: Validation should still work correctly."""
    print("TEST 8: Validation (regression)")
    url = f"{API_BASE}/geocode"
    
    all_passed = True
    
    # Test 1: q="a" should return 422
    try:
        resp = httpx.get(url, params={"q": "a", "count": 1}, timeout=30.0)
        assert resp.status_code == 422, f"Expected 422 for 1-char query, got {resp.status_code}"
        print(f"  ✅ 1-char query correctly rejected with 422")
    except AssertionError as e:
        print(f"  ❌ 1-char validation FAILED - {e}")
        all_passed = False
    except Exception as e:
        print(f"  ❌ 1-char validation ERROR - {e}")
        all_passed = False
    
    # Test 2: missing q should return 422
    try:
        resp = httpx.get(url, params={"count": 1}, timeout=30.0)
        assert resp.status_code == 422, f"Expected 422 for missing q, got {resp.status_code}"
        print(f"  ✅ Missing q correctly rejected with 422")
    except AssertionError as e:
        print(f"  ❌ Missing q validation FAILED - {e}")
        all_passed = False
    except Exception as e:
        print(f"  ❌ Missing q validation ERROR - {e}")
        all_passed = False
    
    # Test 3: gibberish should return 200 with empty results
    try:
        resp = httpx.get(url, params={"q": "zzzzzz9999qqqq", "count": 1}, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200 for gibberish, got {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        assert len(results) == 0, f"Expected 0 results for gibberish, got {len(results)}"
        print(f"  ✅ Gibberish query correctly returned empty results")
    except AssertionError as e:
        print(f"  ❌ Gibberish validation FAILED - {e}")
        all_passed = False
    except Exception as e:
        print(f"  ❌ Gibberish validation ERROR - {e}")
        all_passed = False
    
    if all_passed:
        print(f"  ✅ ALL VALIDATION TESTS PASSED")
    
    return all_passed


def test_response_shape():
    """Verify response shape: every result has {name, latitude, longitude} required."""
    print("TEST 9: Response shape validation")
    url = f"{API_BASE}/geocode"
    params = {"q": "London", "count": 5}
    
    try:
        resp = httpx.get(url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        
        assert "results" in data, "Missing 'results' key in response"
        results = data["results"]
        
        assert len(results) >= 1, f"Expected >=1 result for 'London', got {len(results)}"
        
        for i, result in enumerate(results):
            assert "name" in result, f"Result {i} missing 'name' field"
            assert "latitude" in result, f"Result {i} missing 'latitude' field"
            assert "longitude" in result, f"Result {i} missing 'longitude' field"
            assert isinstance(result["name"], str), f"Result {i} 'name' is not a string"
            assert isinstance(result["latitude"], (int, float)), f"Result {i} 'latitude' is not a number"
            assert isinstance(result["longitude"], (int, float)), f"Result {i} 'longitude' is not a number"
            
            # Optional fields should be present (can be null)
            assert "country" in result, f"Result {i} missing 'country' field"
            assert "admin1" in result, f"Result {i} missing 'admin1' field"
            assert "timezone" in result, f"Result {i} missing 'timezone' field"
            assert "population" in result, f"Result {i} missing 'population' field"
            assert "country_code" in result, f"Result {i} missing 'country_code' field"
        
        print(f"  ✅ PASSED - All {len(results)} results have correct shape")
        return True
    except AssertionError as e:
        print(f"  ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_chain_sanity():
    """Chain sanity: use lat/lon from Jadavpur University → call /api/forecast."""
    print("TEST 10: Chain sanity - Jadavpur University → /api/forecast")
    
    try:
        # Step 1: Get Jadavpur University coordinates
        geocode_url = f"{API_BASE}/geocode"
        params = {"q": "Jadavpur University", "count": 1}
        resp = httpx.get(geocode_url, params=params, timeout=30.0)
        assert resp.status_code == 200, f"Geocode failed: {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        assert len(results) == 1, "Expected 1 result for Jadavpur University"
        
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
        
        peak_kw = totals["peak_kw"]
        assert peak_kw > 0, f"Expected peak_kw > 0, got {peak_kw}"
        
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
    print("USER BUG FIX #2 TESTING - /api/geocode with count=1")
    print("Testing Nominatim limit=max(5, count) fix")
    print("=" * 80)
    print()
    
    tests = [
        ("1. Jadavpur University count=1 (3 runs)", test_jadavpur_university_count1_consistency),
        ("2. Eiffel Tower count=1", test_eiffel_tower_count1),
        ("3. Times Square count=1", test_times_square_count1),
        ("4. Statue of Liberty count=1", test_statue_of_liberty_count1),
        ("5. Sealdah count=1", test_sealdah_count1),
        ("6. Landmarks count=5", test_landmarks_count5),
        ("7. Cities count=1 (regression)", test_cities_count1_regression),
        ("8. Validation (regression)", test_validation_regression),
        ("9. Response shape", test_response_shape),
        ("10. Chain sanity", test_chain_sanity),
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
    else:
        print("🎉 ALL TESTS PASSED! Bug fix verified successfully.")
        print()
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
