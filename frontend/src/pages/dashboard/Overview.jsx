import React from 'react';
import { Panel, StatusChip, Led, ProgressBar, KpiCard } from '../../components/scada/Atoms';
import { INVERTERS, SCB_STATIONS, KPI } from '../../mock/mock';
import { Zap, Gauge } from 'lucide-react';

export default function Overview() {
  const totalAc = INVERTERS.reduce((a, i) => a + i.ac_kw, 0);
  const rated = INVERTERS.reduce((a, i) => a + i.rated_kw, 0);

  return (
    <div className="space-y-4">
      <Panel title="Plant total output" right={<span className="text-[10px] font-mono text-slate-500">aggregate of 5 inverters</span>}>
        <div className="flex items-end justify-between mb-3">
          <div>
            <div className="text-4xl font-bold mono text-slate-50">{totalAc.toFixed(1)}<span className="text-lg text-slate-500 ml-2">kW</span></div>
            <div className="text-xs text-slate-500 mt-1">of {rated} kW rated · {((totalAc / rated) * 100).toFixed(1)}% loading</div>
          </div>
          <div className="text-right">
            <div className="text-[10px] font-mono text-slate-500 uppercase">Performance ratio</div>
            <div className="text-2xl font-bold mono text-emerald-400">{KPI.performance_ratio.toFixed(2)}</div>
          </div>
        </div>
        <div className="h-3 rounded-full bg-slate-800 overflow-hidden">
          <div className="h-full bg-gradient-to-r from-cyan-500 to-sky-400" style={{ width: `${(totalAc / rated) * 100}%` }} />
        </div>
      </Panel>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
        {INVERTERS.map((inv) => (
          <div key={inv.id} className="panel p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="font-mono text-sm text-slate-100 font-semibold">{inv.id}</div>
              <StatusChip status={inv.status} />
            </div>
            <div className="text-3xl font-bold mono text-slate-50">{inv.ac_kw.toFixed(1)}<span className="text-sm text-slate-500 ml-1">kW</span></div>
            <div className="text-[10px] text-slate-500 mt-0.5">of {inv.rated_kw} kW rated</div>
            <ProgressBar value={inv.ac_kw} max={inv.rated_kw} tone={inv.status === 'fault' ? 'red' : 'cyan'} />
            <div className="mt-3 grid grid-cols-3 gap-1 text-[10px] font-mono">
              <div><div className="text-slate-500">DC</div><div className="text-slate-200">{inv.dc_kw.toFixed(0)} kW</div></div>
              <div><div className="text-slate-500">EFF</div><div className="text-slate-200">{inv.efficiency.toFixed(1)}%</div></div>
              <div><div className="text-slate-500">T</div><div className="text-slate-200">{inv.temp_c.toFixed(0)}°</div></div>
            </div>
          </div>
        ))}
      </div>

      <Panel title="SCB / String status grid" right={<div className="flex items-center gap-3 text-[10px] font-mono text-slate-500"><span className="flex items-center gap-1"><Led tone="green" size={7} /> OK</span><span className="flex items-center gap-1"><Led tone="red" size={7} /> Fault</span></div>}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
          {SCB_STATIONS.map((scb) => (
            <div key={scb.id} className="panel p-3">
              <div className="font-mono text-xs text-slate-300 mb-2">{scb.id}</div>
              <div className="grid grid-cols-4 gap-1.5">
                {scb.strings.map((s) => (
                  <div key={s.id} className={`aspect-square rounded flex flex-col items-center justify-center border ${s.ok ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-red-500/40 bg-red-500/10'}`}>
                    <Led tone={s.ok ? 'green' : 'red'} pulse={!s.ok} size={6} />
                    <div className="text-[9px] mono text-slate-400 mt-0.5">{s.id}</div>
                    <div className={`text-[9px] mono ${s.ok ? 'text-slate-300' : 'text-red-400'}`}>{s.current}A</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}
