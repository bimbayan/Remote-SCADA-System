# SolarisSCADA — Contracts

## API Contracts (all under `/api`)

### 1. `GET /api/health`
Health check. Returns `{ "status": "ok" }`.

### 2. `GET /api/geocode?q={query}&count={n}`
Proxy Open-Meteo geocoding to search cities.
- Upstream: `https://geocoding-api.open-meteo.com/v1/search?name={q}&count={n}&language=en&format=json`
- Response: `{ "results": [ { name, country, admin1, latitude, longitude, timezone, population } ] }`

### 3. `GET /api/live?lat={lat}&lon={lon}`
Fetch current environmental snapshot from Open-Meteo + apply transparent PV model at the given coords.
- Upstream: `https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,cloud_cover,wind_speed_10m,shortwave_radiation,is_day&timezone=auto`
- Response fields: `location {lat, lon, timezone}, current { ghi_w_m2, ambient_c, wind_ms, humidity_pct, cloud_cover_pct, is_day, module_c }, plant { p_dc_kw, p_ac_kw, performance_ratio }, meta { source, endpoint, response_ms, fetched_at }`
- Plant size fixed at 500 kW for the digital-twin demo.

### 4. `GET /api/forecast?lat={lat}&lon={lon}&size_kw={n}&hours={h}`
Fetch hourly forecast + apply PV model per hour.
- Upstream: `https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,shortwave_radiation,cloud_cover,wind_speed_10m,relative_humidity_2m&timezone=auto&forecast_days=7`
- Response: `{ location, size_kw, rows: [ { time, ambient_c, module_c, ghi_w_m2, ac_kw, dc_kw, cloud_pct } ], totals: { peak_kw, energy_kwh, capacity_factor_pct }, meta }`
- Slice to `hours` (default 48).

## PV Model (transparent, same as project)
```
T_cell = T_ambient + ((45 - 20) / 800) * GHI
temperature_factor = clip(1 - 0.0042 * max(T_cell - 25, 0), 0.75, 1)
P_DC = size_kw * (GHI / 1000) * temperature_factor
P_AC = clip(P_DC * 0.97, 0, size_kw)
```

## Mock data replacements
- `mock.js` KPI GHI/ambient/wind/humidity/module_c/ac_power_kw/dc_power_kw → live from `/api/live` (Dashboard, Home)
- Predictor page → live from `/api/geocode` (city search) + `/api/forecast` (48h projection)
- Inverters, alarms, SLD, substation, battery, hourly table, historical trends → REMAIN MOCK (labelled as "simulated")

## Frontend integration
- Add `src/lib/api.js` with `getLive(lat, lon)`, `getForecast(lat, lon, size, hours)`, `geocode(q)`.
- Dashboard.jsx + HomePage.jsx fetch live snapshot every 5 min from plant coords (12.9716, 77.5946) and hydrate the weather/KPI cards.
- Predictor.jsx replaces lat/lon inputs and Quick Presets with a debounced city search input backed by `/api/geocode`.
