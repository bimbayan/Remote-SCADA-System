import React, { useState } from 'react';
import { Panel, KpiCard } from '../../components/scada/Atoms';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Button } from '../../components/ui/button';
import { Slider } from '../../components/ui/slider';
import { MapPin, Sun, Thermometer, Wind, Cloud, Zap, Battery, Loader2, AlertCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, ComposedChart, Bar } from 'recharts';
import { toast } from 'sonner';

const axisColor = '#475569';
const grid = '#1f2937';

const PRESETS = [
  { name: 'Bengaluru, IN', lat: 12.9716, lon: 77.5946 },
  { name: 'Berlin, DE', lat: 52.5200, lon: 13.4050 },
  { name: 'Phoenix, US', lat: 33.4484, lon: -112.0740 },
  { name: 'Sydney, AU', lat: -33.8688, lon: 151.2093 },
  { name: 'Cairo, EG', lat: 30.0444, lon: 31.2357 },
  { name: 'Tokyo, JP', lat: 35.6762, lon: 139.6503 },
];

// Mock predictor: build 48h synthetic forecast around a sun curve seeded by lat
function mockForecast(lat, lon, size_kw) {
  const solarNoon = 12;
  const absLat = Math.abs(lat);
  const peakGhi = Math.max(180, 1000 - absLat * 8); // higher near equator
  const now = new Date();
  const rows = [];
  for (let i = 0; i < 48; i++) {
    const t = new Date(now.getTime() + i * 3600 * 1000);
    const hourLocal = t.getHours() + lon / 15;
    const h = ((hourLocal % 24) + 24) % 24;
    const dayProg = Math.cos(((h - solarNoon) / 6) * (Math.PI / 2));
    const ghi = h >= 6 && h <= 18 ? Math.max(0, dayProg * peakGhi + (Math.random() - 0.5) * 40) : 0;
    const ambient = 22 + (30 - absLat / 3) * 0.4 + Math.sin(h / 24 * 2 * Math.PI) * 5 + (Math.random() - 0.5) * 2;
    const tCell = ambient + ((45 - 20) / 800) * ghi;
    const tempFactor = Math.min(1, Math.max(0.75, 1 - 0.0042 * Math.max(tCell - 25, 0)));
    const pDC = size_kw * (ghi / 1000) * tempFactor;
    const pAC = Math.min(size_kw, Math.max(0, pDC * 0.97));
    rows.push({
      time: `${String(t.getHours()).padStart(2, '0')}:00`,
      day: t.toLocaleDateString('en-GB', { weekday: 'short' }),
      ghi: +ghi.toFixed(0),
      ambient: +ambient.toFixed(1),
      module: +tCell.toFixed(1),
      ac: +pAC.toFixed(2),
    });
  }
  return rows;
}

export default function Predictor() {
  const [city, setCity] = useState('Bengaluru, IN');
  const [lat, setLat] = useState(12.9716);
  const [lon, setLon] = useState(77.5946);
  const [size, setSize] = useState([500]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const run = () => {
    setLoading(true);
    setTimeout(() => {
      const rows = mockForecast(lat, lon, size[0]);
      const totalEnergy = rows.reduce((a, r) => a + r.ac, 0);
      const peak = Math.max(...rows.map((r) => r.ac));
      const capacityFactor = totalEnergy / (rows.length * size[0]);
      setResult({ rows, totalEnergy, peak, capacityFactor, currentGhi: rows[0].ghi, currentAmbient: rows[0].ambient });
      setLoading(false);
      toast.success(`Forecast generated for ${city}`, { description: `≈ ${totalEnergy.toFixed(0)} kWh over next 48h` });
    }, 800);
  };

  const applyPreset = (p) => {
    setCity(p.name);
    setLat(p.lat);
    setLon(p.lon);
  };

  return (
    <div className="space-y-4">
      <div className="panel p-5">
        <div className="flex items-start gap-4 flex-wrap">
          <div className="w-12 h-12 rounded-lg bg-cyan-500/10 border border-cyan-500/30 grid place-items-center">
            <MapPin className="w-6 h-6 text-cyan-400" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xl font-semibold text-slate-50">Location-aware yield predictor</div>
            <div className="text-sm text-slate-400 mt-1">Enter any location on Earth. We model expected AC power for the next 48 hours using irradiance, cell-temperature derating and 97% conversion efficiency — the same transparent formula as the plant digital twin.</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Panel title="Site inputs" className="lg:col-span-1">
          <div className="space-y-4">
            <div>
              <Label className="text-slate-400 text-xs">Location name</Label>
              <Input value={city} onChange={(e) => setCity(e.target.value)} className="mt-1 bg-[#0a0a0f] border-slate-700" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-slate-400 text-xs">Latitude</Label>
                <Input type="number" step="0.0001" value={lat} onChange={(e) => setLat(parseFloat(e.target.value) || 0)} className="mt-1 bg-[#0a0a0f] border-slate-700 mono" />
              </div>
              <div>
                <Label className="text-slate-400 text-xs">Longitude</Label>
                <Input type="number" step="0.0001" value={lon} onChange={(e) => setLon(parseFloat(e.target.value) || 0)} className="mt-1 bg-[#0a0a0f] border-slate-700 mono" />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between">
                <Label className="text-slate-400 text-xs">Plant size</Label>
                <span className="mono text-cyan-400 text-sm">{size[0]} kW</span>
              </div>
              <Slider value={size} onValueChange={setSize} min={5} max={2000} step={5} className="mt-2" />
              <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1"><span>5 kW</span><span>2 MW</span></div>
            </div>

            <Button onClick={run} disabled={loading} className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold">
              {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Modeling forecast…</> : <><Zap className="w-4 h-4 mr-2" /> Predict yield</>}
            </Button>

            <div className="pt-3 border-t border-[#1f1f27]">
              <div className="text-[10px] font-mono text-slate-500 uppercase mb-2">Quick presets</div>
              <div className="grid grid-cols-2 gap-2">
                {PRESETS.map((p) => (
                  <button key={p.name} onClick={() => applyPreset(p)} className="text-xs text-slate-300 hover:text-cyan-400 border border-slate-700 hover:border-cyan-500/40 rounded-md px-2 py-1.5 transition-colors text-left">
                    {p.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </Panel>

        <div className="lg:col-span-2 space-y-4">
          {!result ? (
            <Panel title="Forecast output">
              <div className="py-16 text-center">
                <div className="w-16 h-16 mx-auto rounded-full bg-slate-800/60 grid place-items-center mb-4">
                  <Sun className="w-8 h-8 text-slate-600" />
                </div>
                <div className="text-slate-300 font-medium">Enter a location & press Predict</div>
                <div className="text-xs text-slate-500 mt-2">We’ll simulate 48 hours of AC power based on latitude, cell-temperature derating and conversion efficiency.</div>
              </div>
            </Panel>
          ) : (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <KpiCard label="Peak AC power" value={result.peak.toFixed(1)} unit="kW" tone="info" icon={Zap} sub="in next 48h" />
                <KpiCard label="Energy 48h" value={result.totalEnergy.toFixed(0)} unit="kWh" tone="good" icon={Battery} sub="cumulative" />
                <KpiCard label="Capacity factor" value={(result.capacityFactor * 100).toFixed(1)} unit="%" tone="info" icon={Sun} sub="modelled" />
                <KpiCard label="Current GHI" value={result.currentGhi} unit="W/m²" icon={Cloud} sub={`Ambient ${result.currentAmbient.toFixed(1)}°C`} />
              </div>

              <Panel title="48-hour AC power forecast" right={<span className="mono text-[10px] text-slate-500">{lat.toFixed(3)}, {lon.toFixed(3)}</span>}>
                <div style={{ height: 260 }}>
                  <ResponsiveContainer>
                    <ComposedChart data={result.rows}>
                      <defs>
                        <linearGradient id="acp" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.5} />
                          <stop offset="100%" stopColor="#06b6d4" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke={grid} strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="time" stroke={axisColor} fontSize={10} tickLine={false} axisLine={false} interval={2} />
                      <YAxis yAxisId="l" stroke={axisColor} fontSize={10} tickLine={false} axisLine={false} />
                      <YAxis yAxisId="r" orientation="right" stroke={axisColor} fontSize={10} tickLine={false} axisLine={false} />
                      <Tooltip contentStyle={{ background: '#0d0d13', border: '1px solid #1f1f27', fontSize: 12 }} />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      <Area yAxisId="l" dataKey="ac" stroke="#06b6d4" strokeWidth={2} fill="url(#acp)" name="AC kW" />
                      <Line yAxisId="r" dataKey="ghi" stroke="#f59e0b" strokeWidth={2} dot={false} name="GHI W/m²" />
                      <Line yAxisId="r" dataKey="module" stroke="#ef4444" strokeWidth={1.5} dot={false} name="Module °C" strokeDasharray="4 4" />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              </Panel>

              <Panel title="Hourly breakdown" right={<span className="text-[10px] font-mono text-slate-500">first 24 rows</span>}>
                <div className="overflow-x-auto max-h-72 overflow-y-auto">
                  <table className="w-full text-xs">
                    <thead className="sticky top-0 bg-[#141419]">
                      <tr className="text-left text-[10px] font-mono tracking-widest text-slate-500 uppercase border-b border-[#1f1f27]">
                        <th className="py-2 pr-3">Time</th>
                        <th className="py-2 pr-3">Day</th>
                        <th className="py-2 pr-3 text-right">GHI</th>
                        <th className="py-2 pr-3 text-right">Ambient</th>
                        <th className="py-2 pr-3 text-right">Module</th>
                        <th className="py-2 pr-3 text-right">AC kW</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.rows.slice(0, 24).map((r, i) => (
                        <tr key={i} className="border-b border-[#141419]">
                          <td className="py-1.5 pr-3 mono text-slate-200">{r.time}</td>
                          <td className="py-1.5 pr-3 text-slate-400">{r.day}</td>
                          <td className="py-1.5 pr-3 text-right mono text-slate-200">{r.ghi}</td>
                          <td className="py-1.5 pr-3 text-right mono text-slate-200">{r.ambient.toFixed(1)}°</td>
                          <td className="py-1.5 pr-3 text-right mono text-slate-200">{r.module.toFixed(1)}°</td>
                          <td className="py-1.5 pr-3 text-right mono text-cyan-400">{r.ac.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Panel>

              <div className="panel p-4 border-amber-500/20 border">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-amber-400 mt-0.5" />
                  <div className="text-sm text-slate-300">
                    <span className="font-semibold text-amber-400">Data lineage:</span> This preview uses a client-side irradiance model seeded by latitude. When wired to the backend it will call Open-Meteo (<span className="mono text-xs">/v1/forecast</span>) with the same coordinates and use the transparent PV formula.
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
