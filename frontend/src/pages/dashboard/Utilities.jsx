import React from 'react';
import { Panel, Donut, Led, ProgressBar } from '../../components/scada/Atoms';
import { BATTERY, KPI, SUBSTATION, RECOMMENDATIONS, PLANT_INFO } from '../../mock/mock';
import { Battery, Sun, Thermometer, Wind, Droplets, CheckCircle2, AlertTriangle, Info } from 'lucide-react';

const levelIcon = { info: Info, warning: AlertTriangle, success: CheckCircle2 };
const levelTone = { info: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30', warning: 'text-amber-400 bg-amber-500/10 border-amber-500/30', success: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' };

export default function Utilities() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Panel title="Battery ESS · BESS-01" right={<span className={`chip ${BATTERY.mode === 'Discharging' ? 'chip-amber' : 'chip-green'}`}><Led tone={BATTERY.mode === 'Discharging' ? 'amber' : 'green'} pulse size={7} /> {BATTERY.mode.toUpperCase()}</span>}>
          <div className="flex items-center justify-center">
            <Donut value={BATTERY.soc_pct} max={100} label="% SOC" color="#06b6d4" size={180} />
          </div>
          <div className="grid grid-cols-2 gap-2 mt-4">
            <div className="panel p-3"><div className="text-[10px] font-mono text-slate-500 uppercase">Capacity</div><div className="mono text-lg text-slate-100 mt-1">{BATTERY.capacity_kwh} kWh</div></div>
            <div className="panel p-3"><div className="text-[10px] font-mono text-slate-500 uppercase">Power</div><div className="mono text-lg text-slate-100 mt-1">{BATTERY.power_kw > 0 ? '+' : ''}{BATTERY.power_kw} kW</div></div>
            <div className="panel p-3"><div className="text-[10px] font-mono text-slate-500 uppercase">SOH</div><div className="mono text-lg text-emerald-400 mt-1">{BATTERY.soh_pct}%</div></div>
            <div className="panel p-3"><div className="text-[10px] font-mono text-slate-500 uppercase">Temp</div><div className="mono text-lg text-slate-100 mt-1">{BATTERY.temp_c}°C</div></div>
          </div>
        </Panel>

        <Panel title="Cycle statistics">
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Total cycles</div>
                <div className="mono text-slate-200">{BATTERY.cycle_count} / 6000</div>
              </div>
              <ProgressBar value={BATTERY.cycle_count} max={6000} tone="cyan" />
            </div>
            <div>
              <div className="flex items-center justify-between">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Depth of discharge (avg)</div>
                <div className="mono text-slate-200">62%</div>
              </div>
              <ProgressBar value={62} tone="cyan" />
            </div>
            <div>
              <div className="flex items-center justify-between">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Round-trip efficiency</div>
                <div className="mono text-emerald-400">92.4%</div>
              </div>
              <ProgressBar value={92.4} tone="green" />
            </div>
            <div>
              <div className="flex items-center justify-between">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Warranty progress</div>
                <div className="mono text-slate-200">6.9%</div>
              </div>
              <ProgressBar value={6.9} tone="cyan" />
            </div>
            <div className="pt-3 border-t border-[#1f1f27] text-xs text-slate-500">
              Last full calibration cycle: <span className="mono text-slate-300">2026-06-18</span>
            </div>
          </div>
        </Panel>

        <Panel title="Weather station · MET-01">
          <div className="space-y-3">
            <div className="panel p-3 flex items-center gap-3">
              <Sun className="w-5 h-5 text-amber-400" />
              <div className="flex-1"><div className="text-[10px] font-mono text-slate-500 uppercase">Irradiance (GHI)</div><div className="mono text-slate-100">{KPI.ghi_w_m2} W/m²</div></div>
            </div>
            <div className="panel p-3 flex items-center gap-3">
              <Thermometer className="w-5 h-5 text-red-400" />
              <div className="flex-1"><div className="text-[10px] font-mono text-slate-500 uppercase">Module temperature</div><div className="mono text-slate-100">{KPI.module_c}°C</div></div>
            </div>
            <div className="panel p-3 flex items-center gap-3">
              <Thermometer className="w-5 h-5 text-amber-400" />
              <div className="flex-1"><div className="text-[10px] font-mono text-slate-500 uppercase">Ambient</div><div className="mono text-slate-100">{KPI.ambient_c}°C</div></div>
            </div>
            <div className="panel p-3 flex items-center gap-3">
              <Wind className="w-5 h-5 text-cyan-400" />
              <div className="flex-1"><div className="text-[10px] font-mono text-slate-500 uppercase">Wind</div><div className="mono text-slate-100">{KPI.wind_ms} m/s</div></div>
            </div>
            <div className="panel p-3 flex items-center gap-3">
              <Droplets className="w-5 h-5 text-blue-400" />
              <div className="flex-1"><div className="text-[10px] font-mono text-slate-500 uppercase">Humidity</div><div className="mono text-slate-100">{KPI.humidity_pct}%</div></div>
            </div>
          </div>
        </Panel>
      </div>

      <Panel title="Decision intelligence · rule-based recommendations">
        <div className="grid md:grid-cols-2 gap-3">
          {RECOMMENDATIONS.map((r, i) => {
            const Icon = levelIcon[r.level] || Info;
            return (
              <div key={i} className={`panel p-4 border ${levelTone[r.level]}`}>
                <div className="flex items-start gap-3">
                  <Icon className="w-5 h-5 mt-0.5 shrink-0" />
                  <div>
                    <div className="font-semibold text-slate-100">{r.title}</div>
                    <div className="text-sm text-slate-400 mt-1 leading-relaxed">{r.body}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Panel>

      <Panel title="System information">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div><div className="text-[10px] font-mono text-slate-500 uppercase">Plant name</div><div className="text-slate-100 mt-1">{PLANT_INFO.name}</div></div>
          <div><div className="text-[10px] font-mono text-slate-500 uppercase">Rated capacity</div><div className="mono text-slate-100 mt-1">{PLANT_INFO.capacity_kw} kW AC</div></div>
          <div><div className="text-[10px] font-mono text-slate-500 uppercase">Inverters</div><div className="mono text-slate-100 mt-1">{PLANT_INFO.inverters} × 100 kW</div></div>
          <div><div className="text-[10px] font-mono text-slate-500 uppercase">Battery</div><div className="mono text-slate-100 mt-1">{PLANT_INFO.battery_kwh} kWh</div></div>
          <div><div className="text-[10px] font-mono text-slate-500 uppercase">Latitude</div><div className="mono text-slate-100 mt-1">{PLANT_INFO.latitude}°</div></div>
          <div><div className="text-[10px] font-mono text-slate-500 uppercase">Longitude</div><div className="mono text-slate-100 mt-1">{PLANT_INFO.longitude}°</div></div>
          <div><div className="text-[10px] font-mono text-slate-500 uppercase">Commissioned</div><div className="mono text-slate-100 mt-1">{PLANT_INFO.commissioned}</div></div>
          <div><div className="text-[10px] font-mono text-slate-500 uppercase">SCADA version</div><div className="mono text-slate-100 mt-1">v3.0.4</div></div>
        </div>
      </Panel>
    </div>
  );
}
