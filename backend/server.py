"""SolarisSCADA backend — Open-Meteo-backed live SCADA demo."""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="SolarisSCADA API", version="1.0.0")
api_router = APIRouter(prefix="/api")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Open-Meteo constants + PV model
# ---------------------------------------------------------------------------

OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
NOMINATIM_SEARCH = "https://nominatim.openstreetmap.org/search"
NOMINATIM_UA = "SolarisSCADA/1.0 (demo; educational)"

CURRENT_FIELDS = ",".join(
    [
        "temperature_2m",
        "relative_humidity_2m",
        "cloud_cover",
        "wind_speed_10m",
        "shortwave_radiation",
        "is_day",
    ]
)
HOURLY_FIELDS = ",".join(
    [
        "temperature_2m",
        "shortwave_radiation",
        "cloud_cover",
        "wind_speed_10m",
        "relative_humidity_2m",
    ]
)

PLANT_SIZE_KW = 500.0


def apply_pv_model(ghi: float, ambient_c: float, size_kw: float) -> Dict[str, float]:
    """Transparent PV model matching the reference project."""
    ghi_val = max(0.0, float(ghi or 0.0))
    amb_val = float(ambient_c or 0.0)
    t_cell = amb_val + ((45 - 20) / 800.0) * ghi_val
    temp_factor = max(0.75, min(1.0, 1 - 0.0042 * max(t_cell - 25.0, 0.0)))
    p_dc = size_kw * (ghi_val / 1000.0) * temp_factor
    p_ac = max(0.0, min(size_kw, p_dc * 0.97))
    return {
        "module_c": round(t_cell, 2),
        "temperature_factor": round(temp_factor, 4),
        "p_dc_kw": round(p_dc, 2),
        "p_ac_kw": round(p_ac, 2),
    }


async def _get(url: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """HTTP GET with timing + error normalisation."""
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            resp = await http.get(url, params=params, headers=headers or {})
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream {e.response.status_code}: {e.response.text[:200]}",
        ) from e
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Upstream unreachable: {e}") from e
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    return {"data": data, "response_ms": elapsed_ms}


async def _try_nominatim(q: str, count: int) -> List[Dict[str, Any]]:
    """Fallback geocoder using OpenStreetMap Nominatim.

    Covers landmarks, universities, streets, POIs — everything Open-Meteo misses.
    Requires a descriptive User-Agent per OSM usage policy.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            resp = await http.get(
                NOMINATIM_SEARCH,
                params={
                    "q": q,
                    "format": "json",
                    "addressdetails": 1,
                    "limit": max(1, min(count, 20)),
                    "accept-language": "en",
                },
                headers={"User-Agent": NOMINATIM_UA, "Accept": "application/json"},
            )
            if resp.status_code != 200:
                return []
            hits = resp.json() or []
    except httpx.HTTPError:
        return []

    results: List[Dict[str, Any]] = []
    for h in hits:
        try:
            lat = float(h.get("lat"))
            lon = float(h.get("lon"))
        except (TypeError, ValueError):
            continue
        addr = h.get("address") or {}
        # Pick the most useful "name" — first the object's own name, else its city/town/village
        name = (
            h.get("name")
            or addr.get("city")
            or addr.get("town")
            or addr.get("village")
            or addr.get("suburb")
            or addr.get("neighbourhood")
            or (h.get("display_name") or "").split(",", 1)[0]
            or q
        )
        results.append(
            {
                "name": name,
                "country": addr.get("country"),
                "admin1": addr.get("state") or addr.get("region") or addr.get("county"),
                "latitude": lat,
                "longitude": lon,
                "timezone": None,  # Open-Meteo forecast will auto-resolve when called with lat/lon
                "population": None,
                "country_code": (addr.get("country_code") or "").upper() or None,
            }
        )
    return results


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class GeocodeItem(BaseModel):
    name: str
    country: Optional[str] = None
    admin1: Optional[str] = None
    latitude: float
    longitude: float
    timezone: Optional[str] = None
    population: Optional[int] = None
    country_code: Optional[str] = None


class GeocodeResponse(BaseModel):
    results: List[GeocodeItem]


class LiveResponse(BaseModel):
    location: Dict[str, Any]
    current: Dict[str, Any]
    plant: Dict[str, Any]
    meta: Dict[str, Any]


class ForecastRow(BaseModel):
    time: str
    day: str
    hour: str
    ambient_c: float
    module_c: float
    ghi_w_m2: float
    cloud_pct: float
    wind_ms: float
    ac_kw: float
    dc_kw: float


class ForecastResponse(BaseModel):
    location: Dict[str, Any]
    size_kw: float
    hours: int
    rows: List[ForecastRow]
    totals: Dict[str, float]
    meta: Dict[str, Any]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@api_router.get("/")
async def root() -> Dict[str, str]:
    return {"service": "SolarisSCADA API", "status": "ok"}


@api_router.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}


@api_router.get("/geocode", response_model=GeocodeResponse)
async def geocode(
    q: str = Query(..., min_length=2, description="City, landmark or place name"),
    count: int = Query(6, ge=1, le=20),
) -> GeocodeResponse:
    """Search places with a two-tier strategy:
    1. Open-Meteo geocoding (fast, city/town level, no key).
    2. If no results, fall back to OSM Nominatim which covers landmarks,
       universities, streets and other POIs.
    """
    # Tier 1 — Open-Meteo
    om_hits: List[Dict[str, Any]] = []
    try:
        payload = await _get(
            OPEN_METEO_GEOCODE,
            {"name": q, "count": count, "language": "en", "format": "json"},
        )
        om_hits = payload["data"].get("results") or []
    except HTTPException:
        om_hits = []

    results: List[GeocodeItem] = []
    for r in om_hits:
        if "latitude" not in r or "longitude" not in r:
            continue
        results.append(
            GeocodeItem(
                name=r.get("name", ""),
                country=r.get("country"),
                admin1=r.get("admin1"),
                latitude=r["latitude"],
                longitude=r["longitude"],
                timezone=r.get("timezone"),
                population=r.get("population"),
                country_code=r.get("country_code"),
            )
        )

    # Tier 2 — Nominatim fallback for landmarks / POIs
    if not results:
        osm_hits = await _try_nominatim(q, count)
        for r in osm_hits:
            results.append(GeocodeItem(**r))

    return GeocodeResponse(results=results)


@api_router.get("/live", response_model=LiveResponse)
async def live(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    size_kw: float = Query(PLANT_SIZE_KW, gt=0, le=100000),
) -> LiveResponse:
    """Current environmental snapshot + modelled plant KPI at (lat, lon)."""
    payload = await _get(
        OPEN_METEO_FORECAST,
        {
            "latitude": lat,
            "longitude": lon,
            "current": CURRENT_FIELDS,
            "timezone": "auto",
        },
    )
    data = payload["data"]
    cur = data.get("current") or {}

    ghi = cur.get("shortwave_radiation", 0) or 0
    ambient = cur.get("temperature_2m", 0) or 0
    pv = apply_pv_model(ghi, ambient, size_kw)

    pr = (
        round(pv["p_ac_kw"] / max(1e-6, size_kw * ghi / 1000.0), 3)
        if ghi and ghi > 20
        else 0.0
    )

    return LiveResponse(
        location={
            "latitude": data.get("latitude", lat),
            "longitude": data.get("longitude", lon),
            "timezone": data.get("timezone"),
            "elevation_m": data.get("elevation"),
        },
        current={
            "ghi_w_m2": round(float(ghi), 1),
            "ambient_c": round(float(ambient), 1),
            "wind_ms": round(float(cur.get("wind_speed_10m") or 0), 1),
            "humidity_pct": round(float(cur.get("relative_humidity_2m") or 0), 1),
            "cloud_cover_pct": round(float(cur.get("cloud_cover") or 0), 1),
            "is_day": bool(cur.get("is_day", 0)),
            "module_c": pv["module_c"],
            "observed_at": cur.get("time"),
        },
        plant={
            "size_kw": size_kw,
            "p_dc_kw": pv["p_dc_kw"],
            "p_ac_kw": pv["p_ac_kw"],
            "temperature_factor": pv["temperature_factor"],
            "performance_ratio": pr,
        },
        meta={
            "source": "Open-Meteo",
            "endpoint": OPEN_METEO_FORECAST,
            "response_ms": payload["response_ms"],
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
    )


@api_router.get("/forecast", response_model=ForecastResponse)
async def forecast(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    size_kw: float = Query(PLANT_SIZE_KW, gt=0, le=100000),
    hours: int = Query(48, ge=1, le=168),
) -> ForecastResponse:
    """Hourly PV forecast for the next N hours (default 48)."""
    payload = await _get(
        OPEN_METEO_FORECAST,
        {
            "latitude": lat,
            "longitude": lon,
            "hourly": HOURLY_FIELDS,
            "timezone": "auto",
            "forecast_days": 7,
        },
    )
    data = payload["data"]
    h = data.get("hourly") or {}
    times: List[str] = h.get("time") or []
    ghis: List[float] = h.get("shortwave_radiation") or []
    temps: List[float] = h.get("temperature_2m") or []
    clouds: List[float] = h.get("cloud_cover") or []
    winds: List[float] = h.get("wind_speed_10m") or []

    # Start slice from the current local hour bucket.
    now_iso = datetime.now().isoformat(timespec="hours")
    start_idx = 0
    for i, t in enumerate(times):
        if t >= now_iso:
            start_idx = i
            break
    times = times[start_idx : start_idx + hours]
    ghis = ghis[start_idx : start_idx + hours]
    temps = temps[start_idx : start_idx + hours]
    clouds = clouds[start_idx : start_idx + hours]
    winds = winds[start_idx : start_idx + hours]

    rows: List[ForecastRow] = []
    total_energy = 0.0
    peak = 0.0
    for i, t in enumerate(times):
        ghi = float(ghis[i] if i < len(ghis) else 0) or 0
        amb = float(temps[i] if i < len(temps) else 0) or 0
        cloud = float(clouds[i] if i < len(clouds) else 0) or 0
        wind = float(winds[i] if i < len(winds) else 0) or 0
        pv = apply_pv_model(ghi, amb, size_kw)
        total_energy += pv["p_ac_kw"]
        peak = max(peak, pv["p_ac_kw"])
        try:
            dt = datetime.fromisoformat(t)
            hour_lbl = dt.strftime("%H:%M")
            day_lbl = dt.strftime("%a")
        except Exception:
            hour_lbl = t[-5:] if len(t) >= 5 else t
            day_lbl = ""
        rows.append(
            ForecastRow(
                time=t,
                day=day_lbl,
                hour=hour_lbl,
                ambient_c=round(amb, 2),
                module_c=pv["module_c"],
                ghi_w_m2=round(ghi, 1),
                cloud_pct=round(cloud, 1),
                wind_ms=round(wind, 1),
                ac_kw=pv["p_ac_kw"],
                dc_kw=pv["p_dc_kw"],
            )
        )

    n = max(1, len(rows))
    capacity_factor = 100.0 * (total_energy / (n * size_kw)) if size_kw > 0 else 0.0

    return ForecastResponse(
        location={
            "latitude": data.get("latitude", lat),
            "longitude": data.get("longitude", lon),
            "timezone": data.get("timezone"),
        },
        size_kw=size_kw,
        hours=len(rows),
        rows=rows,
        totals={
            "peak_kw": round(peak, 2),
            "energy_kwh": round(total_energy, 1),
            "capacity_factor_pct": round(capacity_factor, 2),
        },
        meta={
            "source": "Open-Meteo",
            "endpoint": OPEN_METEO_FORECAST,
            "response_ms": payload["response_ms"],
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
    )


# ---------------------------------------------------------------------------
# Wire-up
# ---------------------------------------------------------------------------

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client() -> None:
    client.close()
