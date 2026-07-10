// Mock data for Remote Solar SCADA System

export const PLANT_INFO = {
  name: 'Sunrise Solar Farm — Unit 1',
  capacity_kw: 500,
  inverters: 5,
  battery_kwh: 200,
  latitude: 12.9716,
  longitude: 77.5946,
  city: 'Bengaluru, India',
  commissioned: '2024-11-18',
};

export const KPI = {
  ac_power_kw: 382.4,
  dc_power_kw: 394.6,
  ghi_w_m2: 812,
  ambient_c: 31.2,
  module_c: 47.6,
  wind_ms: 3.1,
  humidity_pct: 54,
  daily_energy_kwh: 2140,
  monthly_energy_mwh: 62.8,
  lifetime_mwh: 1284.5,
  co2_avoided_t: 912.4,
  performance_ratio: 0.83,
  plant_uptime_pct: 99.4,
  battery_soc: 78.2,
  poi_power_kw: 371.8,
  grid_freq_hz: 50.02,
  grid_voltage_kv: 11.03,
};

export const INVERTERS = [
  { id: 'INV-01', rated_kw: 100, ac_kw: 78.4, dc_kw: 80.9, status: 'run', efficiency: 96.9, temp_c: 42.1, strings_ok: 12, strings_total: 12 },
  { id: 'INV-02', rated_kw: 100, ac_kw: 76.9, dc_kw: 79.3, status: 'run', efficiency: 96.9, temp_c: 43.8, strings_ok: 12, strings_total: 12 },
  { id: 'INV-03', rated_kw: 100, ac_kw: 77.1, dc_kw: 79.6, status: 'run', efficiency: 96.9, temp_c: 41.2, strings_ok: 11, strings_total: 12 },
  { id: 'INV-04', rated_kw: 100, ac_kw: 0.0, dc_kw: 0.0, status: 'fault', efficiency: 0, temp_c: 34.5, strings_ok: 0, strings_total: 12 },
  { id: 'INV-05', rated_kw: 100, ac_kw: 74.6, dc_kw: 76.9, status: 'run', efficiency: 96.9, temp_c: 44.5, strings_ok: 12, strings_total: 12 },
];

export const HOURLY_GENERATION = [
  { h: '05', gen: 0, target: 0 }, { h: '06', gen: 12, target: 15 }, { h: '07', gen: 68, target: 75 },
  { h: '08', gen: 158, target: 165 }, { h: '09', gen: 274, target: 285 }, { h: '10', gen: 356, target: 368 },
  { h: '11', gen: 420, target: 430 }, { h: '12', gen: 452, target: 460 }, { h: '13', gen: 448, target: 458 },
  { h: '14', gen: 412, target: 425 }, { h: '15', gen: 335, target: 350 }, { h: '16', gen: 246, target: 260 },
  { h: '17', gen: 128, target: 140 }, { h: '18', gen: 42, target: 50 }, { h: '19', gen: 0, target: 0 },
];

export const POWER_IRRADIANCE_TREND = Array.from({ length: 30 }, (_, i) => {
  const t = i;
  const power = Math.max(0, Math.sin((t / 30) * Math.PI) * 460 + (Math.random() - 0.5) * 20);
  const ghi = Math.max(0, Math.sin((t / 30) * Math.PI) * 950 + (Math.random() - 0.5) * 40);
  return { t: `${String(5 + Math.floor(t / 2)).padStart(2, '0')}:${(t % 2) * 30 === 0 ? '00' : '30'}`, power: +power.toFixed(1), ghi: +ghi.toFixed(0) };
});

export const PR_TREND = Array.from({ length: 30 }, (_, i) => ({
  t: i,
  pr: +(0.78 + Math.sin(i / 5) * 0.05 + (Math.random() - 0.5) * 0.02).toFixed(3),
}));

export const AC_SPARK = Array.from({ length: 40 }, (_, i) => ({
  t: i, v: +(370 + Math.sin(i / 3) * 20 + (Math.random() - 0.5) * 8).toFixed(1),
}));

export const ALARMS = [
  { id: 'A1042', ts: '2026-07-10 14:22:11', severity: 'Critical', device: 'INV-04', code: 'F-207', message: 'DC arc fault detected; inverter shutdown', ack: false },
  { id: 'A1041', ts: '2026-07-10 13:58:04', severity: 'High', device: 'INV-03', code: 'W-118', message: 'String 07 current below expected threshold', ack: false },
  { id: 'A1040', ts: '2026-07-10 12:41:29', severity: 'Medium', device: 'MET-01', code: 'I-052', message: 'Pyranometer soiling above 4%', ack: true },
  { id: 'A1039', ts: '2026-07-10 11:17:03', severity: 'Medium', device: 'TX-01', code: 'W-091', message: 'Transformer oil temperature rising: 62°C', ack: true },
  { id: 'A1038', ts: '2026-07-10 09:44:56', severity: 'Low', device: 'BESS-01', code: 'I-014', message: 'Battery SOC balance drift 1.8%', ack: true },
  { id: 'A1037', ts: '2026-07-10 08:29:12', severity: 'High', device: 'RMU-A', code: 'W-063', message: 'Breaker close signal delay > 200ms', ack: true },
  { id: 'A1036', ts: '2026-07-09 18:02:41', severity: 'Low', device: 'COMM', code: 'I-004', message: 'Modbus link latency spike on INV-02', ack: true },
  { id: 'A1035', ts: '2026-07-09 16:12:00', severity: 'Medium', device: 'INV-01', code: 'W-121', message: 'Grid over-voltage 253V (limit 250V)', ack: true },
  { id: 'A1034', ts: '2026-07-09 14:33:22', severity: 'Critical', device: 'GRID', code: 'F-301', message: 'POI reverse power flow detected 4s', ack: true },
];

export const ALARM_HISTOGRAM = [
  { day: 'Mon', critical: 1, high: 2, medium: 3, low: 1 },
  { day: 'Tue', critical: 0, high: 1, medium: 4, low: 2 },
  { day: 'Wed', critical: 0, high: 3, medium: 2, low: 3 },
  { day: 'Thu', critical: 2, high: 1, medium: 5, low: 1 },
  { day: 'Fri', critical: 1, high: 4, medium: 2, low: 0 },
  { day: 'Sat', critical: 0, high: 2, medium: 3, low: 2 },
  { day: 'Sun', critical: 1, high: 3, medium: 4, low: 1 },
];

export const SCB_STATIONS = [1, 2, 3, 4, 5].map((n) => ({
  id: `SCB-0${n}`,
  strings: Array.from({ length: 12 }, (_, i) => ({
    id: `S${String(i + 1).padStart(2, '0')}`,
    current: +(7 + (Math.random() - 0.3) * 1.4).toFixed(2),
    ok: !(n === 4 || (n === 3 && i === 6)),
  })),
}));

export const SUBSTATION = {
  transformer: { id: 'TX-01', rating_kva: 630, load_pct: 71, oil_c: 58, winding_c: 74, tap: 3 },
  rmus: [
    { id: 'RMU-A', breaker: 'CLOSED', current_a: 342, voltage_kv: 11.03 },
    { id: 'RMU-B', breaker: 'CLOSED', current_a: 328, voltage_kv: 11.02 },
    { id: 'RMU-C', breaker: 'OPEN', current_a: 0, voltage_kv: 11.03 },
  ],
  comms: [
    { device: 'PLC Master', protocol: 'Modbus TCP', link: 'up', latency_ms: 12 },
    { device: 'RTU-South', protocol: 'DNP3', link: 'up', latency_ms: 41 },
    { device: 'Meter POI', protocol: 'IEC 61850', link: 'up', latency_ms: 8 },
    { device: 'Weather St.', protocol: 'Modbus RTU', link: 'up', latency_ms: 22 },
    { device: 'BESS BMS', protocol: 'CAN over IP', link: 'degraded', latency_ms: 128 },
  ],
};

export const BATTERY = {
  id: 'BESS-01',
  capacity_kwh: 200,
  soc_pct: 78.2,
  soh_pct: 96.4,
  power_kw: -32.5,
  cycle_count: 412,
  temp_c: 28.6,
  mode: 'Discharging',
};

export const TRENDS = Array.from({ length: 60 }, (_, i) => {
  const min = i * 5;
  const hh = String(6 + Math.floor(min / 60)).padStart(2, '0');
  const mm = String(min % 60).padStart(2, '0');
  const ghi = Math.max(0, Math.sin((i / 60) * Math.PI) * 900 + (Math.random() - 0.5) * 30);
  return {
    t: `${hh}:${mm}`,
    ghi: +ghi.toFixed(0),
    ac: +(ghi / 2.2).toFixed(1),
    dc: +(ghi / 2.1).toFixed(1),
    pr: +(0.79 + Math.sin(i / 8) * 0.04).toFixed(3),
    module_c: +(28 + ghi / 60).toFixed(1),
    ambient_c: +(24 + ghi / 200).toFixed(1),
  };
});

export const RECOMMENDATIONS = [
  { level: 'info', title: 'Battery reserve is high (78%)', body: 'Enable export or shift flexible loads to preserve headroom for evening peak.' },
  { level: 'warning', title: 'INV-04 offline — 100 kW capacity down', body: 'DC arc fault (F-207) latched. Dispatch field crew; expected recovery within 4h.' },
  { level: 'success', title: 'Performance ratio 0.83 — nominal', body: 'No intervention indicated. Continue monitoring module temperature at INV-05 (44.5°C).' },
  { level: 'info', title: 'Soiling loss trending up (4.1%)', body: 'Schedule cleaning within 48h to reclaim ~14 kWh/day.' },
];
