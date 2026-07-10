import React from 'react';
import { KPI, HOURLY_GENERATION, INVERTERS, AC_SPARK, PR_TREND, ALARMS, BATTERY } from '../../mock/mock';
import { Panel, KpiCard, ProgressBar, StatusChip, Led } from '../../components/scada/Atoms';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, AreaChart, Area, Legend } from 'recharts';
import { Zap, Sun, Gauge, Battery, TrendingUp, Activity, Cloud, Timer } from 'lucide-react';

const axisColor = '#475569';
const grid = '#1f2937';

export default function HomePage() {
  const active = ALARMS.filter((a) => !a.ack);
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <KpiCard label="AC Power" value={KPI.ac_power_kw.toFixed(1)} unit="kW" tone="info" icon={Zap} sub={`of ${500} kW capacity`} />
        <KpiCard label="Daily Energy" value={(KPI.daily_energy_kwh / 1000).toFixed(2)} unit="MWh" tone="good" icon={Sun} sub="since 00:00" />
        <KpiCard label="Performance Ratio" value={KPI.performance_ratio.toFixed(2)} unit="PR" tone="good" icon={Gauge} sub="30-min rolling" />
        <KpiCard label="Plant Uptime" value={KPI.plant_uptime_pct.toFixed(1)} unit="%" tone="good" icon={Timer} sub="trailing 30 days" />
        <KpiCard label="Battery SOC" value={BATTERY.soc_pct.toFixed(1)} unit="%" tone="info" icon={Battery} sub={BATTERY.mode} />
        <KpiCard label="Active Alarms" value={active.length} unit="" tone={active.length ? 'warn' : 'good'} icon={Activity} sub={`${active.filter((a) => a.severity === 'Critical').length} critical`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Panel title="Hourly generation vs. target" className="lg:col-span-2" right={<span className="text-[10px] font-mono text-slate-500">kW · today</span>}>
          <div style={{ height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={HOURLY_GENERATION}>
                <CartesianGrid stroke={grid} strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="h" stroke={axisColor} fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke={axisColor} fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: '#0d0d13', border: '1px solid #1f1f27', fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="target" fill="#334155" name="Target" radius={[3, 3, 0, 0]} />
                <Bar dataKey="gen" fill="#06b6d4" name="Generated" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Live AC power · 5-min" right={<span className="chip chip-green"><Led tone="green" pulse size={7} /> LIVE</span>}>
          <div style={{ height: 120 }}>
            <ResponsiveContainer>
              <AreaChart data={AC_SPARK}>
                <defs>
                  <linearGradient id="ac" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Area dataKey="v" stroke="#06b6d4" strokeWidth={2} fill="url(#ac)" />
                <Tooltip contentStyle={{ background: '#0d0d13', border: '1px solid #1f1f27', fontSize: 12 }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 text-2xl font-bold mono text-cyan-400">{KPI.ac_power_kw.toFixed(1)} <span className="text-xs text-slate-500">kW</span></div>

          <div className="mt-4 text-[10px] font-mono tracking-widest text-slate-500 uppercase">Performance Ratio · 30-min</div>
          <div style={{ height: 100 }}>
            <ResponsiveContainer>
              <LineChart data={PR_TREND}>
                <Line dataKey="pr" stroke="#22c55e" strokeWidth={2} dot={false} />
                <Tooltip contentStyle={{ background: '#0d0d13', border: '1px solid #1f1f27', fontSize: 12 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <Panel title="Inverter fleet health" right={<span className="text-[10px] font-mono text-slate-500">5 devices · auto-refresh 5s</span>}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[10px] font-mono tracking-widest text-slate-500 uppercase border-b border-[#1f1f27]">
                <th className="py-2 pr-3">Device</th>
                <th className="py-2 pr-3">Status</th>
                <th className="py-2 pr-3">Load</th>
                <th className="py-2 pr-3 text-right">AC kW</th>
                <th className="py-2 pr-3 text-right">DC kW</th>
                <th className="py-2 pr-3 text-right">Eff.</th>
                <th className="py-2 pr-3 text-right">Temp</th>
                <th className="py-2 pr-3">Strings</th>
              </tr>
            </thead>
            <tbody>
              {INVERTERS.map((inv) => (
                <tr key={inv.id} className="border-b border-[#141419] hover:bg-slate-800/20">
                  <td className="py-3 pr-3 font-mono text-slate-100">{inv.id}</td>
                  <td className="py-3 pr-3"><StatusChip status={inv.status} /></td>
                  <td className="py-3 pr-3 w-40"><ProgressBar value={inv.ac_kw} max={inv.rated_kw} tone={inv.status === 'fault' ? 'red' : 'cyan'} /></td>
                  <td className="py-3 pr-3 text-right mono text-slate-100">{inv.ac_kw.toFixed(1)}</td>
                  <td className="py-3 pr-3 text-right mono text-slate-300">{inv.dc_kw.toFixed(1)}</td>
                  <td className="py-3 pr-3 text-right"><span className={`chip ${inv.efficiency > 95 ? 'chip-green' : 'chip-amber'}`}>{inv.efficiency.toFixed(1)}%</span></td>
                  <td className="py-3 pr-3 text-right mono text-slate-300">{inv.temp_c.toFixed(1)}°C</td>
                  <td className="py-3 pr-3 font-mono text-xs text-slate-400">{inv.strings_ok}/{inv.strings_total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="panel p-3 flex items-center gap-3"><Led tone="green" pulse /><div><div className="text-[10px] font-mono text-slate-500 uppercase">Inverters</div><div className="text-sm font-semibold text-slate-100">4 of 5 online</div></div></div>
        <div className="panel p-3 flex items-center gap-3"><Led tone="amber" pulse /><div><div className="text-[10px] font-mono text-slate-500 uppercase">Alarms</div><div className="text-sm font-semibold text-slate-100">{active.length} unacked</div></div></div>
        <div className="panel p-3 flex items-center gap-3"><Led tone="blue" /><div><div className="text-[10px] font-mono text-slate-500 uppercase">Battery</div><div className="text-sm font-semibold text-slate-100">{BATTERY.soc_pct.toFixed(0)}% · {BATTERY.mode}</div></div></div>
        <div className="panel p-3 flex items-center gap-3"><Led tone="green" /><div><div className="text-[10px] font-mono text-slate-500 uppercase">Mode</div><div className="text-sm font-semibold text-slate-100">Auto</div></div></div>
        <div className="panel p-3 flex items-center gap-3"><Led tone="green" pulse /><div><div className="text-[10px] font-mono text-slate-500 uppercase">Grid</div><div className="text-sm font-semibold text-slate-100">{KPI.grid_freq_hz} Hz · {KPI.grid_voltage_kv} kV</div></div></div>
      </div>
    </div>
  );
}
