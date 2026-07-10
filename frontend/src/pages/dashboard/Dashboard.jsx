import React from 'react';
import { KPI, HOURLY_GENERATION, POWER_IRRADIANCE_TREND, INVERTERS, BATTERY } from '../../mock/mock';
import { Panel, KpiCard, HalfDonut, Led, StatusChip } from '../../components/scada/Atoms';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend, Area, ComposedChart } from 'recharts';
import { Zap, Sun, Thermometer, Wind, Droplets, Gauge } from 'lucide-react';

const axisColor = '#475569';
const grid = '#1f2937';

export default function Dashboard() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <KpiCard label="AC Power" value={KPI.ac_power_kw.toFixed(1)} unit="kW" tone="info" icon={Zap} />
        <KpiCard label="DC Power" value={KPI.dc_power_kw.toFixed(1)} unit="kW" icon={Zap} />
        <KpiCard label="Irradiance" value={KPI.ghi_w_m2.toFixed(0)} unit="W/m²" tone="info" icon={Sun} />
        <KpiCard label="Module Temp" value={KPI.module_c.toFixed(1)} unit="°C" tone="warn" icon={Thermometer} />
        <KpiCard label="POI Export" value={KPI.poi_power_kw.toFixed(1)} unit="kW" tone="good" icon={Gauge} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Panel title="Meter POI · Live">
          <HalfDonut value={KPI.poi_power_kw} max={500} label="kW EXPORT" title="POI Power" />
          <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
            <div className="panel p-2"><div className="text-[10px] font-mono text-slate-500">FREQ</div><div className="mono text-slate-100">{KPI.grid_freq_hz} Hz</div></div>
            <div className="panel p-2"><div className="text-[10px] font-mono text-slate-500">V-BUS</div><div className="mono text-slate-100">{KPI.grid_voltage_kv} kV</div></div>
          </div>
        </Panel>

        <Panel title="Hourly generation" className="lg:col-span-2" right={<span className="text-[10px] font-mono text-slate-500">kW</span>}>
          <div style={{ height: 240 }}>
            <ResponsiveContainer>
              <BarChart data={HOURLY_GENERATION}>
                <CartesianGrid stroke={grid} strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="h" stroke={axisColor} fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke={axisColor} fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: '#0d0d13', border: '1px solid #1f1f27', fontSize: 12 }} />
                <Bar dataKey="gen" fill="#06b6d4" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <Panel title="Power / Irradiance trend" right={<div className="flex items-center gap-3 text-[10px] font-mono text-slate-500"><span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-cyan-500" />AC kW</span><span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-amber-500" />GHI W/m²</span></div>}>
        <div style={{ height: 260 }}>
          <ResponsiveContainer>
            <ComposedChart data={POWER_IRRADIANCE_TREND}>
              <defs>
                <linearGradient id="pow" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={grid} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="t" stroke={axisColor} fontSize={11} tickLine={false} axisLine={false} />
              <YAxis yAxisId="l" stroke={axisColor} fontSize={11} tickLine={false} axisLine={false} />
              <YAxis yAxisId="r" orientation="right" stroke={axisColor} fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: '#0d0d13', border: '1px solid #1f1f27', fontSize: 12 }} />
              <Area yAxisId="l" dataKey="power" stroke="#06b6d4" strokeWidth={2} fill="url(#pow)" name="AC kW" />
              <Line yAxisId="r" dataKey="ghi" stroke="#f59e0b" strokeWidth={2} dot={false} name="GHI W/m²" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="panel p-4"><div className="text-[10px] font-mono text-slate-500 uppercase">Ambient</div><div className="mt-1 flex items-center gap-2"><Thermometer className="w-4 h-4 text-amber-400" /><span className="text-xl font-bold mono text-slate-100">{KPI.ambient_c}°C</span></div></div>
        <div className="panel p-4"><div className="text-[10px] font-mono text-slate-500 uppercase">Wind</div><div className="mt-1 flex items-center gap-2"><Wind className="w-4 h-4 text-cyan-400" /><span className="text-xl font-bold mono text-slate-100">{KPI.wind_ms} m/s</span></div></div>
        <div className="panel p-4"><div className="text-[10px] font-mono text-slate-500 uppercase">Humidity</div><div className="mt-1 flex items-center gap-2"><Droplets className="w-4 h-4 text-blue-400" /><span className="text-xl font-bold mono text-slate-100">{KPI.humidity_pct}%</span></div></div>
        <div className="panel p-4"><div className="text-[10px] font-mono text-slate-500 uppercase">Irradiance</div><div className="mt-1 flex items-center gap-2"><Sun className="w-4 h-4 text-yellow-400" /><span className="text-xl font-bold mono text-slate-100">{KPI.ghi_w_m2} W/m²</span></div></div>
      </div>

      <Panel title="Single-line diagram (SLD)" right={<span className="text-[10px] font-mono text-slate-500">live status</span>}>
        <div className="relative bg-[#08080c] rounded-md p-6">
          <svg viewBox="0 0 1000 260" width="100%" height="280">
            {/* Grid header */}
            <text x="20" y="20" fill="#64748b" fontSize="10" fontFamily="JetBrains Mono">GRID / POI</text>
            <text x="920" y="20" fill="#64748b" fontSize="10" fontFamily="JetBrains Mono">ARRAY</text>

            {/* Grid symbol */}
            <rect x="20" y="110" width="70" height="40" fill="#0d0d13" stroke="#38bdf8" />
            <text x="55" y="135" textAnchor="middle" fill="#38bdf8" fontSize="11" fontFamily="JetBrains Mono">GRID</text>

            {/* Meter */}
            <rect x="120" y="110" width="70" height="40" fill="#0d0d13" stroke="#22c55e" />
            <text x="155" y="135" textAnchor="middle" fill="#22c55e" fontSize="11" fontFamily="JetBrains Mono">METER</text>

            {/* Transformer */}
            <circle cx="250" cy="122" r="14" fill="none" stroke="#38bdf8" />
            <circle cx="250" cy="138" r="14" fill="none" stroke="#38bdf8" />
            <text x="250" y="175" textAnchor="middle" fill="#94a3b8" fontSize="10" fontFamily="JetBrains Mono">TX-01</text>

            {/* Bus bar */}
            <line x1="280" y1="130" x2="720" y2="130" stroke="#f59e0b" strokeWidth="3" />
            <text x="500" y="122" textAnchor="middle" fill="#f59e0b" fontSize="10" fontFamily="JetBrains Mono">AC BUS 415 V</text>

            {/* Connections meter->grid */}
            <line x1="90" y1="130" x2="120" y2="130" stroke="#38bdf8" strokeWidth="2" />
            <line x1="190" y1="130" x2="236" y2="130" stroke="#22c55e" strokeWidth="2" />
            <line x1="264" y1="130" x2="280" y2="130" stroke="#38bdf8" strokeWidth="2" />

            {/* Inverters */}
            {INVERTERS.map((inv, i) => {
              const x = 320 + i * 80;
              const isFault = inv.status === 'fault';
              return (
                <g key={inv.id}>
                  <line x1={x} y1="130" x2={x} y2="180" stroke={isFault ? '#ef4444' : '#22c55e'} strokeWidth="2" />
                  <rect x={x - 25} y="180" width="50" height="40" fill="#0d0d13" stroke={isFault ? '#ef4444' : '#22c55e'} strokeWidth="1.5" rx="2" />
                  <text x={x} y="202" textAnchor="middle" fill={isFault ? '#ef4444' : '#22c55e'} fontSize="10" fontFamily="JetBrains Mono">{inv.id.replace('INV-', '')}</text>
                  <circle cx={x + 18} cy={185} r="3" fill={isFault ? '#ef4444' : '#22c55e'}>
                    {!isFault && <animate attributeName="opacity" values="0.3;1;0.3" dur="1.5s" repeatCount="indefinite" />}
                  </circle>
                  <text x={x} y="244" textAnchor="middle" fill="#94a3b8" fontSize="9" fontFamily="JetBrains Mono">{inv.ac_kw.toFixed(0)} kW</text>
                </g>
              );
            })}

            {/* BESS */}
            <line x1="780" y1="130" x2="780" y2="180" stroke="#38bdf8" strokeWidth="2" />
            <rect x="755" y="180" width="50" height="40" fill="#0d0d13" stroke="#38bdf8" rx="2" />
            <text x="780" y="202" textAnchor="middle" fill="#38bdf8" fontSize="10" fontFamily="JetBrains Mono">BESS</text>
            <text x="780" y="244" textAnchor="middle" fill="#94a3b8" fontSize="9" fontFamily="JetBrains Mono">{BATTERY.soc_pct.toFixed(0)}%</text>

            {/* Array */}
            <line x1="860" y1="130" x2="920" y2="130" stroke="#38bdf8" strokeWidth="2" />
            <rect x="920" y="105" width="60" height="50" fill="#0d0d13" stroke="#f59e0b" />
            <text x="950" y="135" textAnchor="middle" fill="#f59e0b" fontSize="10" fontFamily="JetBrains Mono">PV[⇄]</text>
          </svg>
        </div>
      </Panel>
    </div>
  );
}
