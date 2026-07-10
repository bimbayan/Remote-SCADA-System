import React, { useState, useEffect, useRef } from 'react';
import { Panel, KpiCard } from '../../components/scada/Atoms';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Button } from '../../components/ui/button';
import { Slider } from '../../components/ui/slider';
import { MapPin, Sun, Cloud, Zap, Battery, Loader2, AlertCircle, Search, Wind, Thermometer } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, ComposedChart } from 'recharts';
import { toast } from 'sonner';
import { geocode, getForecast } from '../../lib/api';

const axisColor = '#475569';
const grid = '#1f2937';

export default function Predictor() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showSug, setShowSug] = useState(false);
  const [selected, setSelected] = useState(null); // { name, country, admin1, latitude, longitude }
  const [size, setSize] = useState([500]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const debRef = useRef(null);
  const boxRef = useRef(null);

  // Debounced geocoding
  useEffect(() => {
    if (!query || query.length < 2) {
      setSuggestions([]);
      return;
    }
    if (debRef.current) clearTimeout(debRef.current);
    debRef.current = setTimeout(async () => {
      try {
        setSearching(true);
        const results = await geocode(query, 8);
        setSuggestions(results);
        setShowSug(true);
      } catch (e) {
        setSuggestions([]);
      } finally {
        setSearching(false);
      }
    }, 350);
    return () => debRef.current && clearTimeout(debRef.current);
  }, [query]);

  // Close dropdown on outside click
  useEffect(() => {
    const onClick = (e) => {
      if (boxRef.current && !boxRef.current.contains(e.target)) setShowSug(false);
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  const pick = (item) => {
    setSelected(item);
    setQuery(formatLocation(item));
    setShowSug(false);
    setResult(null);
  };

  const run = async () => {
    if (!selected) {
      toast.error('Please select a location from the list first');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await getForecast(selected.latitude, selected.longitude, size[0], 48);
      setResult(data);
      toast.success(`Forecast generated for ${selected.name}`, {
        description: `≈ ${data.totals.energy_kwh.toFixed(0)} kWh over next ${data.hours}h · peak ${data.totals.peak_kw.toFixed(1)} kW`,
      });
    } catch (e) {
      const msg = e?.response?.data?.detail || e.message || 'Forecast failed';
      setError(msg);
      toast.error('Forecast failed', { description: msg });
    } finally {
      setLoading(false);
    }
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
            <div className="text-sm text-slate-400 mt-1">Search any city on Earth. We call the live Open-Meteo forecast API and apply the transparent PV model (cell-temperature derating + 97% conversion) to estimate expected AC power for the next 48 hours.</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Panel title="Site inputs" className="lg:col-span-1">
          <div className="space-y-4">
            <div ref={boxRef} className="relative">
              <Label className="text-slate-400 text-xs">Location</Label>
              <div className="relative mt-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input
                  value={query}
                  onChange={(e) => { setQuery(e.target.value); setSelected(null); }}
                  onFocus={() => suggestions.length > 0 && setShowSug(true)}
                  placeholder="Search any city on Earth…"
                  className="pl-9 pr-9 bg-[#0a0a0f] border-slate-700"
                />
                {searching && <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 animate-spin" />}
              </div>
              {showSug && suggestions.length > 0 && (
                <div className="absolute z-30 mt-1 w-full max-h-72 overflow-y-auto panel border border-slate-700">
                  {suggestions.map((s, i) => (
                    <button
                      key={`${s.name}-${s.latitude}-${s.longitude}-${i}`}
                      onClick={() => pick(s)}
                      className="w-full text-left px-3 py-2 hover:bg-slate-800/60 border-b border-[#1f1f27] last:border-b-0 transition-colors"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div>
                          <div className="text-sm text-slate-100">{s.name}</div>
                          <div className="text-[10px] text-slate-500">{[s.admin1, s.country].filter(Boolean).join(', ')}</div>
                        </div>
                        <div className="font-mono text-[10px] text-slate-500">{s.latitude.toFixed(2)}, {s.longitude.toFixed(2)}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
              {selected && (
                <div className="mt-2 flex items-center gap-2 text-[10px] font-mono text-slate-500">
                  <MapPin className="w-3 h-3" />
                  <span>Selected: {selected.latitude.toFixed(4)}°, {selected.longitude.toFixed(4)}° · {selected.timezone || 'auto'}</span>
                </div>
              )}
            </div>

            <div>
              <div className="flex items-center justify-between">
                <Label className="text-slate-400 text-xs">Plant size</Label>
                <span className="mono text-cyan-400 text-sm">{size[0]} kW</span>
              </div>
              <Slider value={size} onValueChange={setSize} min={5} max={2000} step={5} className="mt-2" />
              <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1"><span>5 kW</span><span>2 MW</span></div>
            </div>

            <Button onClick={run} disabled={loading || !selected} className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold disabled:opacity-50 disabled:cursor-not-allowed">
              {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Calling Open-Meteo…</> : <><Zap className="w-4 h-4 mr-2" /> Predict yield</>}
            </Button>

            <div className="pt-3 border-t border-[#1f1f27] text-[11px] text-slate-500 leading-relaxed">
              Data lineage: <span className="text-slate-300">Open-Meteo</span> supplies live temperature, irradiance (GHI), cloud cover and wind for the searched location. AC power is derived server-side using cell-temp derating and 97% conversion efficiency — the same transparent formula as the plant digital twin.
            </div>
          </div>
        </Panel>

        <div className="lg:col-span-2 space-y-4">
          {error && (
            <div className="panel p-4 border-red-500/30 border">
              <div className="flex items-start gap-3"><AlertCircle className="w-5 h-5 text-red-400 mt-0.5" /><div><div className="font-semibold text-red-400">Forecast unavailable</div><div className="text-sm text-slate-400 mt-1">{error}</div></div></div>
            </div>
          )}

          {!result && !error && (
            <Panel title="Forecast output">
              <div className="py-16 text-center">
                <div className="w-16 h-16 mx-auto rounded-full bg-slate-800/60 grid place-items-center mb-4">
                  <Sun className="w-8 h-8 text-slate-600" />
                </div>
                <div className="text-slate-300 font-medium">Search a city, choose a plant size, then Predict</div>
                <div className="text-xs text-slate-500 mt-2">We’ll fetch 48 hours of real weather data and estimate expected AC power.</div>
              </div>
            </Panel>
          )}

          {result && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <KpiCard label="Peak AC power" value={result.totals.peak_kw.toFixed(1)} unit="kW" tone="info" icon={Zap} sub={`in next ${result.hours}h`} />
                <KpiCard label="Energy 48h" value={result.totals.energy_kwh.toFixed(0)} unit="kWh" tone="good" icon={Battery} sub="cumulative" />
                <KpiCard label="Capacity factor" value={result.totals.capacity_factor_pct.toFixed(1)} unit="%" tone="info" icon={Sun} sub="modelled" />
                <KpiCard label="Current GHI" value={result.rows[0]?.ghi_w_m2?.toFixed(0) ?? '0'} unit="W/m²" icon={Cloud} sub={`Ambient ${result.rows[0]?.ambient_c?.toFixed(1) ?? '–'}°C`} />
              </div>

              <Panel title="48-hour AC power forecast" right={<span className="mono text-[10px] text-slate-500">{result.location.latitude?.toFixed(3)}, {result.location.longitude?.toFixed(3)} · {result.meta.source}</span>}>
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
                      <XAxis dataKey="hour" stroke={axisColor} fontSize={10} tickLine={false} axisLine={false} interval={2} />
                      <YAxis yAxisId="l" stroke={axisColor} fontSize={10} tickLine={false} axisLine={false} label={{ value: 'kW', angle: -90, position: 'insideLeft', fill: axisColor, fontSize: 10 }} />
                      <YAxis yAxisId="r" orientation="right" stroke={axisColor} fontSize={10} tickLine={false} axisLine={false} />
                      <Tooltip contentStyle={{ background: '#0d0d13', border: '1px solid #1f1f27', fontSize: 12 }} labelFormatter={(v, payload) => payload?.[0]?.payload?.time || v} />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      <Area yAxisId="l" dataKey="ac_kw" stroke="#06b6d4" strokeWidth={2} fill="url(#acp)" name="AC kW" />
                      <Line yAxisId="r" dataKey="ghi_w_m2" stroke="#f59e0b" strokeWidth={2} dot={false} name="GHI W/m²" />
                      <Line yAxisId="r" dataKey="module_c" stroke="#ef4444" strokeWidth={1.5} dot={false} name="Module °C" strokeDasharray="4 4" />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              </Panel>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="panel p-3"><div className="text-[10px] font-mono text-slate-500 uppercase">Response time</div><div className="mono text-slate-100 mt-1">{result.meta.response_ms} ms</div></div>
                <div className="panel p-3"><div className="text-[10px] font-mono text-slate-500 uppercase">Timezone</div><div className="mono text-slate-100 mt-1">{result.location.timezone || 'auto'}</div></div>
                <div className="panel p-3"><div className="text-[10px] font-mono text-slate-500 uppercase">Rows</div><div className="mono text-slate-100 mt-1">{result.hours}</div></div>
                <div className="panel p-3"><div className="text-[10px] font-mono text-slate-500 uppercase">Plant size</div><div className="mono text-slate-100 mt-1">{result.size_kw} kW</div></div>
              </div>

              <Panel title="Hourly breakdown" right={<span className="text-[10px] font-mono text-slate-500">first 24 rows</span>}>
                <div className="overflow-x-auto max-h-72 overflow-y-auto">
                  <table className="w-full text-xs">
                    <thead className="sticky top-0 bg-[#141419]">
                      <tr className="text-left text-[10px] font-mono tracking-widest text-slate-500 uppercase border-b border-[#1f1f27]">
                        <th className="py-2 pr-3">Time</th>
                        <th className="py-2 pr-3">Day</th>
                        <th className="py-2 pr-3 text-right">GHI</th>
                        <th className="py-2 pr-3 text-right">Cloud</th>
                        <th className="py-2 pr-3 text-right">Wind</th>
                        <th className="py-2 pr-3 text-right">Ambient</th>
                        <th className="py-2 pr-3 text-right">Module</th>
                        <th className="py-2 pr-3 text-right">AC kW</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.rows.slice(0, 24).map((r, i) => (
                        <tr key={i} className="border-b border-[#141419]">
                          <td className="py-1.5 pr-3 mono text-slate-200">{r.hour}</td>
                          <td className="py-1.5 pr-3 text-slate-400">{r.day}</td>
                          <td className="py-1.5 pr-3 text-right mono text-slate-200">{r.ghi_w_m2}</td>
                          <td className="py-1.5 pr-3 text-right mono text-slate-400">{r.cloud_pct}%</td>
                          <td className="py-1.5 pr-3 text-right mono text-slate-400">{r.wind_ms}</td>
                          <td className="py-1.5 pr-3 text-right mono text-slate-200">{r.ambient_c.toFixed(1)}°</td>
                          <td className="py-1.5 pr-3 text-right mono text-slate-200">{r.module_c.toFixed(1)}°</td>
                          <td className="py-1.5 pr-3 text-right mono text-cyan-400">{r.ac_kw.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Panel>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function formatLocation(item) {
  return [item.name, item.admin1, item.country].filter(Boolean).join(', ');
}
