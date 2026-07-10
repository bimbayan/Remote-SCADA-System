"""
Comprehensive backend API tests for SolarisSCADA
Tests all 4 endpoints: /api/health, /api/geocode, /api/live, /api/forecast
"""

import os
import sys
import requests
from datetime import datetime
from typing import Dict, Any, List

# Read backend URL from frontend/.env
def get_backend_url():
    env_path = "/app/frontend/.env"
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=', 1)[1]
    raise ValueError("REACT_APP_BACKEND_URL not found in /app/frontend/.env")

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

print(f"Testing backend at: {API_BASE}")
print("=" * 80)

# Test counters
tests_passed = 0
tests_failed = 0
test_results = []

def log_test(name: str, passed: bool, details: str = ""):
    global tests_passed, tests_failed
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"  Details: {details}")
    if passed:
        tests_passed += 1
    else:
        tests_failed += 1
    test_results.append({"name": name, "passed": passed, "details": details})

# ============================================================================
# TEST 1: GET /api/health
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: GET /api/health")
print("=" * 80)

try:
    resp = requests.get(f"{API_BASE}/health", timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        has_status = "status" in data and data["status"] == "ok"
        has_ts = "ts" in data
        
        if has_status and has_ts:
            # Verify ts is valid ISO format
            try:
                datetime.fromisoformat(data["ts"].replace('Z', '+00:00'))
                log_test("Health endpoint returns correct structure", True, f"Response: {data}")
            except:
                log_test("Health endpoint ts format", False, f"Invalid ISO timestamp: {data['ts']}")
        else:
            log_test("Health endpoint structure", False, f"Missing fields. Got: {data}")
    else:
        log_test("Health endpoint status code", False, f"Expected 200, got {resp.status_code}")
except Exception as e:
    log_test("Health endpoint", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 2: GET /api/geocode
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: GET /api/geocode")
print("=" * 80)

# Test 2.1: Happy path - Bengaluru
try:
    resp = requests.get(f"{API_BASE}/geocode", params={"q": "Bengaluru"}, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            # Check structure
            required_fields = ["name", "latitude", "longitude"]
            has_all = all(f in result for f in required_fields)
            
            # Check Bengaluru coordinates (approximately)
            lat_ok = 12.5 <= result["latitude"] <= 13.5
            lon_ok = 77.0 <= result["longitude"] <= 78.0
            
            if has_all and lat_ok and lon_ok:
                log_test("Geocode Bengaluru", True, f"Found: {result['name']} at ({result['latitude']}, {result['longitude']})")
            else:
                log_test("Geocode Bengaluru coordinates", False, f"Unexpected coords: ({result.get('latitude')}, {result.get('longitude')})")
        else:
            log_test("Geocode Bengaluru results", False, "No results returned")
    else:
        log_test("Geocode Bengaluru status", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Geocode Bengaluru", False, f"Exception: {str(e)}")

# Test 2.2: Happy path - Berlin
try:
    resp = requests.get(f"{API_BASE}/geocode", params={"q": "Berlin"}, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            lat_ok = 52.0 <= result["latitude"] <= 53.0
            lon_ok = 13.0 <= result["longitude"] <= 14.0
            if lat_ok and lon_ok:
                log_test("Geocode Berlin", True, f"Found: {result['name']} at ({result['latitude']}, {result['longitude']})")
            else:
                log_test("Geocode Berlin coordinates", False, f"Unexpected coords: ({result.get('latitude')}, {result.get('longitude')})")
        else:
            log_test("Geocode Berlin results", False, "No results returned")
    else:
        log_test("Geocode Berlin status", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Geocode Berlin", False, f"Exception: {str(e)}")

# Test 2.3: Happy path - Phoenix
try:
    resp = requests.get(f"{API_BASE}/geocode", params={"q": "Phoenix"}, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        if "results" in data and len(data["results"]) > 0:
            log_test("Geocode Phoenix", True, f"Found {len(data['results'])} results")
        else:
            log_test("Geocode Phoenix results", False, "No results returned")
    else:
        log_test("Geocode Phoenix status", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Geocode Phoenix", False, f"Exception: {str(e)}")

# Test 2.4: Happy path - Tokyo
try:
    resp = requests.get(f"{API_BASE}/geocode", params={"q": "Tokyo"}, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            lat_ok = 35.0 <= result["latitude"] <= 36.0
            lon_ok = 139.0 <= result["longitude"] <= 140.0
            if lat_ok and lon_ok:
                log_test("Geocode Tokyo", True, f"Found: {result['name']} at ({result['latitude']}, {result['longitude']})")
            else:
                log_test("Geocode Tokyo coordinates", False, f"Unexpected coords: ({result.get('latitude')}, {result.get('longitude')})")
        else:
            log_test("Geocode Tokyo results", False, "No results returned")
    else:
        log_test("Geocode Tokyo status", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Geocode Tokyo", False, f"Exception: {str(e)}")

# Test 2.5: Validation - query too short (1 char)
try:
    resp = requests.get(f"{API_BASE}/geocode", params={"q": "a"}, timeout=10)
    if resp.status_code == 422:
        log_test("Geocode validation (1 char)", True, "Correctly rejected with 422")
    else:
        log_test("Geocode validation (1 char)", False, f"Expected 422, got {resp.status_code}")
except Exception as e:
    log_test("Geocode validation (1 char)", False, f"Exception: {str(e)}")

# Test 2.6: No matches - should return empty results, not error
try:
    resp = requests.get(f"{API_BASE}/geocode", params={"q": "zzzzzzzzz9999"}, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        if "results" in data and len(data["results"]) == 0:
            log_test("Geocode no matches", True, "Returns empty results array")
        else:
            log_test("Geocode no matches", False, f"Expected empty results, got: {data}")
    else:
        log_test("Geocode no matches status", False, f"Expected 200, got {resp.status_code}")
except Exception as e:
    log_test("Geocode no matches", False, f"Exception: {str(e)}")

# Test 2.7: Count parameter - count=1
try:
    resp = requests.get(f"{API_BASE}/geocode", params={"q": "London", "count": 1}, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        if "results" in data and len(data["results"]) <= 1:
            log_test("Geocode count=1", True, f"Returned {len(data['results'])} results")
        else:
            log_test("Geocode count=1", False, f"Expected <=1 results, got {len(data['results'])}")
    else:
        log_test("Geocode count=1 status", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Geocode count=1", False, f"Exception: {str(e)}")

# Test 2.8: Count parameter - count=15
try:
    resp = requests.get(f"{API_BASE}/geocode", params={"q": "Springfield", "count": 15}, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        log_test("Geocode count=15", True, f"Returned {len(data['results'])} results")
    else:
        log_test("Geocode count=15 status", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Geocode count=15", False, f"Exception: {str(e)}")

# Test 2.9: Response structure validation
try:
    resp = requests.get(f"{API_BASE}/geocode", params={"q": "Paris"}, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            expected_fields = ["name", "latitude", "longitude"]
            optional_fields = ["country", "admin1", "timezone", "population", "country_code"]
            
            has_required = all(f in result for f in expected_fields)
            if has_required:
                log_test("Geocode response structure", True, f"Has all required fields: {expected_fields}")
            else:
                missing = [f for f in expected_fields if f not in result]
                log_test("Geocode response structure", False, f"Missing fields: {missing}")
        else:
            log_test("Geocode response structure", False, "No results to validate")
    else:
        log_test("Geocode response structure", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Geocode response structure", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 3: GET /api/live
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: GET /api/live")
print("=" * 80)

# Test 3.1: Happy path - Bengaluru
try:
    resp = requests.get(f"{API_BASE}/live", params={"lat": 12.9716, "lon": 77.5946}, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        
        # Check top-level structure
        required_keys = ["location", "current", "plant", "meta"]
        has_all_keys = all(k in data for k in required_keys)
        
        if not has_all_keys:
            log_test("Live Bengaluru structure", False, f"Missing keys: {[k for k in required_keys if k not in data]}")
        else:
            # Check current fields
            current = data["current"]
            current_fields = ["ghi_w_m2", "ambient_c", "wind_ms", "humidity_pct", "cloud_cover_pct", "is_day", "module_c", "observed_at"]
            has_current = all(f in current for f in current_fields)
            
            # Check plant fields
            plant = data["plant"]
            plant_fields = ["p_ac_kw", "p_dc_kw", "size_kw"]
            has_plant = all(f in plant for f in plant_fields)
            
            # Check meta
            meta = data["meta"]
            has_meta = "source" in meta and meta["source"] == "Open-Meteo" and "response_ms" in meta
            
            # Validate PV model constraints
            p_ac = plant["p_ac_kw"]
            size_kw = plant["size_kw"]
            p_ac_valid = 0 <= p_ac <= size_kw
            
            # Check is_day is boolean
            is_day_bool = isinstance(current["is_day"], bool)
            
            # Check module_c > ambient_c when GHI > 0
            ghi = current["ghi_w_m2"]
            module_c = current["module_c"]
            ambient_c = current["ambient_c"]
            temp_logic = (ghi == 0) or (module_c >= ambient_c)
            
            if has_current and has_plant and has_meta and p_ac_valid and is_day_bool and temp_logic:
                log_test("Live Bengaluru", True, f"p_ac_kw={p_ac}, size_kw={size_kw}, ghi={ghi}, module_c={module_c}, ambient_c={ambient_c}")
            else:
                issues = []
                if not has_current: issues.append("missing current fields")
                if not has_plant: issues.append("missing plant fields")
                if not has_meta: issues.append("missing/invalid meta")
                if not p_ac_valid: issues.append(f"p_ac_kw={p_ac} not in [0, {size_kw}]")
                if not is_day_bool: issues.append("is_day not boolean")
                if not temp_logic: issues.append(f"module_c={module_c} < ambient_c={ambient_c} when GHI={ghi}")
                log_test("Live Bengaluru validation", False, f"Issues: {', '.join(issues)}")
    else:
        log_test("Live Bengaluru status", False, f"Status {resp.status_code}: {resp.text[:200]}")
except Exception as e:
    log_test("Live Bengaluru", False, f"Exception: {str(e)}")

# Test 3.2: Custom size_kw=100
try:
    resp = requests.get(f"{API_BASE}/live", params={"lat": 12.9716, "lon": 77.5946, "size_kw": 100}, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        plant = data["plant"]
        p_ac = plant["p_ac_kw"]
        size_kw = plant["size_kw"]
        
        if size_kw == 100 and 0 <= p_ac <= 100:
            log_test("Live size_kw=100", True, f"p_ac_kw={p_ac} <= 100")
        else:
            log_test("Live size_kw=100", False, f"size_kw={size_kw}, p_ac_kw={p_ac}")
    else:
        log_test("Live size_kw=100 status", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Live size_kw=100", False, f"Exception: {str(e)}")

# Test 3.3: Validation - invalid latitude
try:
    resp = requests.get(f"{API_BASE}/live", params={"lat": 200, "lon": 77.5946}, timeout=10)
    if resp.status_code == 422:
        log_test("Live validation (lat=200)", True, "Correctly rejected with 422")
    else:
        log_test("Live validation (lat=200)", False, f"Expected 422, got {resp.status_code}")
except Exception as e:
    log_test("Live validation (lat=200)", False, f"Exception: {str(e)}")

# Test 3.4: Validation - invalid longitude
try:
    resp = requests.get(f"{API_BASE}/live", params={"lat": 12.9716, "lon": -500}, timeout=10)
    if resp.status_code == 422:
        log_test("Live validation (lon=-500)", True, "Correctly rejected with 422")
    else:
        log_test("Live validation (lon=-500)", False, f"Expected 422, got {resp.status_code}")
except Exception as e:
    log_test("Live validation (lon=-500)", False, f"Exception: {str(e)}")

# Test 3.5: PV model sanity - nighttime (expect low/zero GHI)
# We'll test a location that's likely nighttime or use the same location and check logic
try:
    resp = requests.get(f"{API_BASE}/live", params={"lat": 12.9716, "lon": 77.5946}, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        current = data["current"]
        plant = data["plant"]
        ghi = current["ghi_w_m2"]
        
        # If GHI is 0, expect ac_kw and dc_kw to be 0
        if ghi == 0:
            if plant["p_ac_kw"] == 0 and plant["p_dc_kw"] == 0:
                log_test("Live PV model (GHI=0)", True, "ac_kw=0 and dc_kw=0 when GHI=0")
            else:
                log_test("Live PV model (GHI=0)", False, f"GHI=0 but ac_kw={plant['p_ac_kw']}, dc_kw={plant['p_dc_kw']}")
        else:
            # GHI > 0, module_c should be > ambient_c
            if current["module_c"] > current["ambient_c"]:
                log_test("Live PV model (GHI>0)", True, f"module_c={current['module_c']} > ambient_c={current['ambient_c']}")
            else:
                log_test("Live PV model (GHI>0)", False, f"module_c={current['module_c']} <= ambient_c={current['ambient_c']} when GHI={ghi}")
    else:
        log_test("Live PV model check", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Live PV model check", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 4: GET /api/forecast
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: GET /api/forecast")
print("=" * 80)

# Test 4.1: Happy path - Berlin, 48 hours
try:
    resp = requests.get(f"{API_BASE}/forecast", params={"lat": 52.52, "lon": 13.405, "size_kw": 500, "hours": 48}, timeout=20)
    if resp.status_code == 200:
        data = resp.json()
        
        # Check top-level structure
        required_keys = ["location", "size_kw", "hours", "rows", "totals", "meta"]
        has_all_keys = all(k in data for k in required_keys)
        
        if not has_all_keys:
            log_test("Forecast Berlin structure", False, f"Missing keys: {[k for k in required_keys if k not in data]}")
        else:
            # Verify size_kw
            size_kw_match = data["size_kw"] == 500
            
            # Verify hours matches rows length
            hours_match = data["hours"] == len(data["rows"]) and len(data["rows"]) <= 48
            
            # Check row structure
            if len(data["rows"]) > 0:
                row = data["rows"][0]
                row_fields = ["time", "day", "hour", "ambient_c", "module_c", "ghi_w_m2", "cloud_pct", "wind_ms", "ac_kw", "dc_kw"]
                has_row_fields = all(f in row for f in row_fields)
                
                # Verify all ac_kw values are in [0, size_kw]
                all_ac_valid = all(0 <= r["ac_kw"] <= 500 for r in data["rows"])
                all_dc_valid = all(r["dc_kw"] >= 0 for r in data["rows"])
                
                # Check totals
                totals = data["totals"]
                has_totals = all(k in totals for k in ["peak_kw", "energy_kwh", "capacity_factor_pct"])
                
                # Verify peak_kw matches max ac_kw
                peak_kw = totals["peak_kw"]
                max_ac = max(r["ac_kw"] for r in data["rows"])
                peak_match = abs(peak_kw - max_ac) < 0.1  # Allow small rounding difference
                
                # Check meta
                meta = data["meta"]
                has_meta = "source" in meta and meta["source"] == "Open-Meteo" and "response_ms" in meta and isinstance(meta["response_ms"], int)
                
                # Check location has timezone
                has_timezone = "timezone" in data["location"]
                
                if size_kw_match and hours_match and has_row_fields and all_ac_valid and all_dc_valid and has_totals and peak_match and has_meta and has_timezone:
                    log_test("Forecast Berlin 48h", True, f"rows={len(data['rows'])}, peak_kw={peak_kw}, energy_kwh={totals['energy_kwh']}")
                else:
                    issues = []
                    if not size_kw_match: issues.append(f"size_kw={data['size_kw']} != 500")
                    if not hours_match: issues.append(f"hours={data['hours']} != len(rows)={len(data['rows'])}")
                    if not has_row_fields: issues.append("missing row fields")
                    if not all_ac_valid: issues.append("some ac_kw out of range")
                    if not all_dc_valid: issues.append("some dc_kw < 0")
                    if not has_totals: issues.append("missing totals fields")
                    if not peak_match: issues.append(f"peak_kw={peak_kw} != max_ac={max_ac}")
                    if not has_meta: issues.append("invalid meta")
                    if not has_timezone: issues.append("missing timezone")
                    log_test("Forecast Berlin 48h validation", False, f"Issues: {', '.join(issues)}")
            else:
                log_test("Forecast Berlin 48h", False, "No rows returned")
    else:
        log_test("Forecast Berlin 48h status", False, f"Status {resp.status_code}: {resp.text[:200]}")
except Exception as e:
    log_test("Forecast Berlin 48h", False, f"Exception: {str(e)}")

# Test 4.2: hours=1
try:
    resp = requests.get(f"{API_BASE}/forecast", params={"lat": 52.52, "lon": 13.405, "hours": 1}, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        if len(data["rows"]) == 1:
            log_test("Forecast hours=1", True, "Returned 1 row")
        else:
            log_test("Forecast hours=1", False, f"Expected 1 row, got {len(data['rows'])}")
    else:
        log_test("Forecast hours=1 status", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Forecast hours=1", False, f"Exception: {str(e)}")

# Test 4.3: hours=168
try:
    resp = requests.get(f"{API_BASE}/forecast", params={"lat": 52.52, "lon": 13.405, "hours": 168}, timeout=20)
    if resp.status_code == 200:
        data = resp.json()
        if len(data["rows"]) <= 168:
            log_test("Forecast hours=168", True, f"Returned {len(data['rows'])} rows")
        else:
            log_test("Forecast hours=168", False, f"Expected <=168 rows, got {len(data['rows'])}")
    else:
        log_test("Forecast hours=168 status", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Forecast hours=168", False, f"Exception: {str(e)}")

# Test 4.4: Validation - hours=0
try:
    resp = requests.get(f"{API_BASE}/forecast", params={"lat": 52.52, "lon": 13.405, "hours": 0}, timeout=10)
    if resp.status_code == 422:
        log_test("Forecast validation (hours=0)", True, "Correctly rejected with 422")
    else:
        log_test("Forecast validation (hours=0)", False, f"Expected 422, got {resp.status_code}")
except Exception as e:
    log_test("Forecast validation (hours=0)", False, f"Exception: {str(e)}")

# Test 4.5: Validation - hours=169
try:
    resp = requests.get(f"{API_BASE}/forecast", params={"lat": 52.52, "lon": 13.405, "hours": 169}, timeout=10)
    if resp.status_code == 422:
        log_test("Forecast validation (hours=169)", True, "Correctly rejected with 422")
    else:
        log_test("Forecast validation (hours=169)", False, f"Expected 422, got {resp.status_code}")
except Exception as e:
    log_test("Forecast validation (hours=169)", False, f"Exception: {str(e)}")

# Test 4.6: Validation - invalid lat
try:
    resp = requests.get(f"{API_BASE}/forecast", params={"lat": 200, "lon": 13.405}, timeout=10)
    if resp.status_code == 422:
        log_test("Forecast validation (lat=200)", True, "Correctly rejected with 422")
    else:
        log_test("Forecast validation (lat=200)", False, f"Expected 422, got {resp.status_code}")
except Exception as e:
    log_test("Forecast validation (lat=200)", False, f"Exception: {str(e)}")

# Test 4.7: Validation - invalid lon
try:
    resp = requests.get(f"{API_BASE}/forecast", params={"lat": 52.52, "lon": -500}, timeout=10)
    if resp.status_code == 422:
        log_test("Forecast validation (lon=-500)", True, "Correctly rejected with 422")
    else:
        log_test("Forecast validation (lon=-500)", False, f"Expected 422, got {resp.status_code}")
except Exception as e:
    log_test("Forecast validation (lon=-500)", False, f"Exception: {str(e)}")

# Test 4.8: PV model sanity - check for GHI=0 rows
try:
    resp = requests.get(f"{API_BASE}/forecast", params={"lat": 52.52, "lon": 13.405, "hours": 48}, timeout=20)
    if resp.status_code == 200:
        data = resp.json()
        zero_ghi_rows = [r for r in data["rows"] if r["ghi_w_m2"] == 0]
        
        if zero_ghi_rows:
            # Check if ac_kw and dc_kw are 0 for these rows
            all_zero = all(r["ac_kw"] == 0 and r["dc_kw"] == 0 for r in zero_ghi_rows)
            if all_zero:
                log_test("Forecast PV model (GHI=0)", True, f"Found {len(zero_ghi_rows)} rows with GHI=0, all have ac_kw=0 and dc_kw=0")
            else:
                bad_rows = [r for r in zero_ghi_rows if r["ac_kw"] != 0 or r["dc_kw"] != 0]
                log_test("Forecast PV model (GHI=0)", False, f"Some GHI=0 rows have non-zero power: {bad_rows[0]}")
        else:
            log_test("Forecast PV model (GHI=0)", True, "No GHI=0 rows found (location has sun)")
        
        # Check module_c > ambient_c for GHI > 0
        positive_ghi_rows = [r for r in data["rows"] if r["ghi_w_m2"] > 0]
        if positive_ghi_rows:
            all_temp_ok = all(r["module_c"] >= r["ambient_c"] for r in positive_ghi_rows)
            if all_temp_ok:
                log_test("Forecast PV model (GHI>0 temp)", True, "module_c >= ambient_c for all GHI>0 rows")
            else:
                bad_rows = [r for r in positive_ghi_rows if r["module_c"] < r["ambient_c"]]
                log_test("Forecast PV model (GHI>0 temp)", False, f"Some rows have module_c < ambient_c: {bad_rows[0]}")
    else:
        log_test("Forecast PV model sanity", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Forecast PV model sanity", False, f"Exception: {str(e)}")

# Test 4.9: Custom size_kw - verify capping
try:
    resp = requests.get(f"{API_BASE}/forecast", params={"lat": 12.9716, "lon": 77.5946, "size_kw": 5, "hours": 24}, timeout=20)
    if resp.status_code == 200:
        data = resp.json()
        all_ac_valid = all(0 <= r["ac_kw"] <= 5 for r in data["rows"])
        if all_ac_valid and data["size_kw"] == 5:
            log_test("Forecast size_kw=5", True, f"All ac_kw values in [0, 5]")
        else:
            log_test("Forecast size_kw=5", False, f"Some ac_kw out of range or size_kw mismatch")
    else:
        log_test("Forecast size_kw=5 status", False, f"Status {resp.status_code}")
except Exception as e:
    log_test("Forecast size_kw=5", False, f"Exception: {str(e)}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total tests: {tests_passed + tests_failed}")
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {tests_failed}")
print("=" * 80)

# Exit with appropriate code
sys.exit(0 if tests_failed == 0 else 1)
