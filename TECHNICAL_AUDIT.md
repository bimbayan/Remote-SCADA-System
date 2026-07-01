# Remote SCADA System — Technical Audit and Demo Plan

Audit date: 30 June 2026

## Executive assessment

The repository is an eight-phase solar PV digital-twin prototype. Its strongest
working path is: PVGIS historical resource data -> a simplified PV power model
-> a five-inverter/battery simulator -> CSV historian -> Streamlit dashboard.
It is not connected to a PLC, RTU, physical inverter, or plant historian.

The updated Phase 7 path now calls Open-Meteo over HTTPS for current model
conditions and a seven-day hourly forecast, derives PV output transparently,
and exposes application-level pagination over the 168 returned hourly records.
It labels upstream, modelled, and simulated values separately.

Overall confidence: **95%**. This assessment comes from tracing every project
Python file and inspecting the tracked datasets and Git state.

## Phase-by-phase code map

| Phase | What the code does | Current condition | Confidence |
|---|---|---|---:|
| 1 | Random sensor generator, basic linear model, toy Streamlit chart | Prototype only; dashboard does not consume the generated sensor CSV | 99% |
| 2 | Generic CSV upload and linear-regression prediction | Works only with the expected training columns and local pickle | 98% |
| 3 | Downloads PVGIS ERA5 hourly data, computes PV power, trains regression | Real external ingestion and useful offline pipeline; dashboard file is empty | 99% |
| 4 | Introduces plant simulator/dashboard and sizing estimator | Main simulator works; dataset streamer is broken by `LngV_FILE` and incorrect `__main__` guard | 99% |
| 5 | Adds richer inverter, panel, battery, and alarm presentation | Dashboard-only iteration over local CSV | 98% |
| 6 | Five-inverter PV/battery/transformer loop and rolling CSV dashboard | Functional deterministic simulator, not live field telemetry | 99% |
| 7 | Previously read the Phase 6 CSV and showed many fixed/random values | Now the real API-backed deployment dashboard | 99% |
| 8 | Rule-based underperformance, battery, and inverter recommendations | Function exists but the old dashboard import/use was commented out | 99% |

## What was genuinely working before this change

- PVGIS calls in Phase 3 and the Phase 4 sizing estimator are genuine HTTPS API
  requests. Confidence: **99%**.
- Phase 6 creates a 500 kW plant topology with 5 inverters, 10 logical panel
  groups, a 200 kWh battery, transformer loss estimates, and occasional faults.
  Confidence: **99%**.
- The simulator writes six rows per timestep (five inverters and one plant
  summary), while the dashboard polls the CSV. Confidence: **99%**.
- The committed root telemetry has 300 rows, or 50 timesteps, ending on
  5 January 2026. It is a replay file, not currently changing telemetry.
  Confidence: **100%**.

## Material limitations found

1. Phase 6 uses a fixed random seed and a sine-shaped daylight curve. Its GHI,
   temperatures, faults, and equipment output are synthetic. Confidence: **100%**.
2. Phase 6 selects `plant_df.iloc[0]`, so when the rolling file has multiple
   snapshots it presents the oldest retained plant row rather than the latest.
   Confidence: **100%**.
3. The history cap is 300 *rows*, not 300 snapshots. At six rows per interval,
   only about 50 timesteps (roughly four minutes at five-second intervals) are
   retained. Confidence: **100%**.
4. CSV replacement is not atomic; the dashboard can read while the simulator is
   writing. There is no database, message queue, retry/backoff, or file lock.
   Confidence: **97%**.
5. Several old KPIs are literals (`SOH`, cycle count, THD, power factor, wash
   date) and the losses/alarm risk are randomized during rendering. Confidence:
   **100%**.
6. The Phase 8 decision engine was disconnected. Its rules are explainable but
   are not machine learning and do not issue control actions. Confidence: **100%**.
7. No authentication, authorization, audit trail, command interlock, OPC-UA,
   Modbus, MQTT, or TLS client identity exists. This is a monitoring digital
   twin, not production SCADA. Confidence: **99%**.

## Implemented live-data architecture

1. `live_data.py` calls Open-Meteo `/v1/forecast` with latitude/longitude.
2. One response supplies current temperature, humidity, cloud cover, wind, GHI,
   day/night state, and 168 hourly forecast records.
3. A transparent model calculates:

   - `T_cell = T_ambient + ((45 - 20) / 800) * GHI`
   - `temperature_factor = clip(1 - 0.0042 * max(T_cell - 25, 0), 0.75, 1)`
   - `P_DC = 500 * (GHI / 1000) * temperature_factor`
   - `P_AC = clip(P_DC * 0.97, 0, 500)`

4. The current plant estimate is split deterministically over five inverters.
5. The API Data Explorer shows the exact GET URL, response latency, fetch time,
   record count, page size, page number, and records X–Y of N.
6. API results are cached for five minutes, keeping the demo well under the free
   service limits.

Architecture confidence: **96%**. The exact endpoint was independently called
on 30 June 2026 and returned current conditions plus 168 hourly records.

## Why Open-Meteo is the primary source

| Source | Best use | Assessment | Confidence |
|---|---|---|---:|
| Open-Meteo | Current weather model conditions and forecast | Best live demo: JSON, global, keyless, GHI/temp/humidity/cloud/wind, simple call | 97% |
| EU JRC PVGIS 5.3 | Historical solar resource and PV yield validation | Already used correctly in this project; authoritative for sizing/backtesting, not live telemetry | 98% |
| NASA POWER | Historical-to-near-real-time hourly solar/met time series | Strong validation/backup source, but slower and less immediate for a live dashboard | 94% |

Authoritative references:

- Open-Meteo API: https://open-meteo.com/en/docs
- Open-Meteo licence: https://open-meteo.com/en/license
- PVGIS API: https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/using-pvgis-5/api-non-interactive-service_en
- NASA POWER hourly API: https://power.larc.nasa.gov/docs/services/api/temporal/hourly/

Scraping is not recommended. These APIs are more stable, permitted, structured,
and defensible to reviewers than pretending an HTML page is plant telemetry.
Confidence: **98%**.

## Git and deployment state

- Local branch: `mainline`; local HEAD and cached `origin/mainline` both resolve
  to `cd364ac7cbea2e07825d5d32b845e90eb463ea1f`. Confidence: **100%**.
- The working tree was clean before implementation. Confidence: **100%**.
- A fresh remote fetch could not be completed in this environment because the
  GitHub operation hung; therefore current GitHub parity is **not claimed**.
  Confidence that cached refs match: **100%**; confidence that GitHub has not
  advanced since the last fetch: **not established**.
- Root `app.py`, `requirements.txt`, and `render.yaml` now define a reproducible
  Render deployment. Confidence: **96%**.

## Verification status

- Exact Open-Meteo request: passed; 168 hourly records returned. Confidence:
  **100%**.
- `git diff --check`: passed. Confidence: **100%**.
- Unit tests cover response transformation, six-row snapshot construction,
  series handling, and 0–500 kW bounds. The local Python launcher is broken and
  points to a removed user profile, so the tests could not execute locally.
  Test-design confidence: **91%**; execution confidence: **not established**.

## Suggested presentation wording

“The environmental layer is live and comes from Open-Meteo over HTTPS/JSON. The
plant layer is a 500 kW digital twin that converts current irradiance and
temperature into estimated production. Because no physical RTU is attached,
inverter and battery tags are explicitly modelled. The explorer paginates the
168 hourly upstream records at the application layer, while PVGIS/NASA POWER
provide the path for historical validation.”

Accuracy confidence: **98%**.

