import React from 'react';
import { Panel, Led, StatusChip, ProgressBar, KpiCard } from '../../components/scada/Atoms';
import { SUBSTATION, KPI } from '../../mock/mock';
import { Zap, Cable, Thermometer, Radio } from 'lucide-react';

export default function Substation() {
  const tx = SUBSTATION.transformer;
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Panel title="Transformer TX-01" right={<span className="chip chip-green"><Led tone="green" pulse size={7} /> ENERGIZED</span>}>
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <div className="text-[10px] font-mono text-slate-500 uppercase">Loading</div>
              <div className="flex items-baseline gap-2 mt-1">
                <div className="text-3xl font-bold mono text-slate-50">{tx.load_pct}%</div>
                <div className="text-xs text-slate-500">of {tx.rating_kva} kVA</div>
              </div>
              <ProgressBar value={tx.load_pct} max={100} tone={tx.load_pct > 80 ? 'amber' : 'cyan'} />
            </div>
            <div className="panel p-3">
              <div className="text-[10px] font-mono text-slate-500 uppercase">Oil temp</div>
              <div className="mono text-lg text-slate-100 mt-1">{tx.oil_c}°C</div>
            </div>
            <div className="panel p-3">
              <div className="text-[10px] font-mono text-slate-500 uppercase">Winding</div>
              <div className="mono text-lg text-slate-100 mt-1">{tx.winding_c}°C</div>
            </div>
            <div className="panel p-3">
              <div className="text-[10px] font-mono text-slate-500 uppercase">Tap</div>
              <div className="mono text-lg text-slate-100 mt-1">Position {tx.tap}</div>
            </div>
            <div className="panel p-3">
              <div className="text-[10px] font-mono text-slate-500 uppercase">Vector</div>
              <div className="mono text-lg text-slate-100 mt-1">Dyn11</div>
            </div>
          </div>
        </Panel>

        <Panel title="RMU / breaker status" className="lg:col-span-2">
          <div className="space-y-2">
            {SUBSTATION.rmus.map((r) => (
              <div key={r.id} className="panel p-3 flex items-center gap-4 flex-wrap">
                <div className="flex items-center gap-2 w-24">
                  <Led tone={r.breaker === 'CLOSED' ? 'green' : 'red'} pulse size={9} />
                  <span className="font-mono text-sm text-slate-100 font-semibold">{r.id}</span>
                </div>
                <div className={`chip ${r.breaker === 'CLOSED' ? 'chip-green' : 'chip-red'}`}>{r.breaker}</div>
                <div className="flex-1 min-w-0 grid grid-cols-2 gap-3">
                  <div>
                    <div className="text-[10px] font-mono text-slate-500 uppercase">Current</div>
                    <div className="mono text-slate-200">{r.current_a} A</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-mono text-slate-500 uppercase">Voltage</div>
                    <div className="mono text-slate-200">{r.voltage_kv} kV</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <Panel title="HV / MV single-line diagram" right={<span className="text-[10px] font-mono text-slate-500">33 kV / 11 kV</span>}>
        <div className="bg-[#08080c] rounded-md p-6 overflow-x-auto">
          <svg viewBox="0 0 900 260" width="100%" height="280" style={{ minWidth: 800 }}>
            {/* HV grid */}
            <text x="20" y="20" fill="#64748b" fontSize="10" fontFamily="JetBrains Mono">33 kV UTILITY</text>
            <path d="M 40 60 L 40 40 M 30 40 L 50 40 M 30 40 L 40 25 M 50 40 L 40 25" stroke="#38bdf8" strokeWidth="2" fill="none" />
            <line x1="40" y1="60" x2="40" y2="110" stroke="#38bdf8" strokeWidth="2" />

            {/* CB HV */}
            <rect x="25" y="110" width="30" height="20" fill="#0d0d13" stroke="#22c55e" />
            <text x="70" y="124" fill="#94a3b8" fontSize="10" fontFamily="JetBrains Mono">CB-HV1 · CLOSED</text>
            <line x1="40" y1="130" x2="40" y2="160" stroke="#22c55e" strokeWidth="2" />

            {/* Transformer */}
            <circle cx="40" cy="170" r="14" fill="none" stroke="#f59e0b" />
            <circle cx="40" cy="188" r="14" fill="none" stroke="#f59e0b" />
            <text x="70" y="180" fill="#94a3b8" fontSize="10" fontFamily="JetBrains Mono">TX-01 · 33/11 kV · 630 kVA</text>

            {/* MV bus */}
            <line x1="40" y1="210" x2="40" y2="230" stroke="#f59e0b" strokeWidth="2" />
            <line x1="40" y1="230" x2="820" y2="230" stroke="#f59e0b" strokeWidth="4" />
            <text x="200" y="220" fill="#f59e0b" fontSize="10" fontFamily="JetBrains Mono">11 kV MV BUS</text>

            {/* RMUs */}
            {SUBSTATION.rmus.map((r, i) => {
              const x = 180 + i * 220;
              const isClosed = r.breaker === 'CLOSED';
              const color = isClosed ? '#22c55e' : '#ef4444';
              return (
                <g key={r.id}>
                  <line x1={x} y1="230" x2={x} y2="170" stroke={color} strokeWidth="2" />
                  <rect x={x - 20} y="170" width="40" height="20" fill="#0d0d13" stroke={color} />
                  <line x1={x - 12} y1="175" x2={x + 12} y2="185" stroke={color} strokeWidth="2" />
                  <text x={x} y="160" textAnchor="middle" fill={color} fontSize="11" fontFamily="JetBrains Mono">{r.id}</text>
                  <text x={x} y="140" textAnchor="middle" fill="#94a3b8" fontSize="9" fontFamily="JetBrains Mono">{r.current_a} A</text>
                  <text x={x} y="125" textAnchor="middle" fill="#94a3b8" fontSize="9" fontFamily="JetBrains Mono">{r.voltage_kv} kV</text>
                  <text x={x} y="110" textAnchor="middle" fill={color} fontSize="9" fontFamily="JetBrains Mono">{r.breaker}</text>
                </g>
              );
            })}

            {/* Inverter feeder */}
            <line x1="820" y1="230" x2="820" y2="170" stroke="#38bdf8" strokeWidth="2" />
            <rect x="780" y="140" width="80" height="30" fill="#0d0d13" stroke="#38bdf8" />
            <text x="820" y="160" textAnchor="middle" fill="#38bdf8" fontSize="10" fontFamily="JetBrains Mono">INVERTER SKID</text>
            <text x="820" y="125" textAnchor="middle" fill="#94a3b8" fontSize="9" fontFamily="JetBrains Mono">{KPI.ac_power_kw.toFixed(0)} kW</text>
          </svg>
        </div>
      </Panel>

      <Panel title="Communications diagnostics">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-[10px] font-mono tracking-widest text-slate-500 uppercase border-b border-[#1f1f27]">
              <th className="py-2 pr-3">Device</th>
              <th className="py-2 pr-3">Protocol</th>
              <th className="py-2 pr-3">Link</th>
              <th className="py-2 pr-3 text-right">Latency</th>
              <th className="py-2 pr-3">Signal</th>
            </tr>
          </thead>
          <tbody>
            {SUBSTATION.comms.map((c, i) => (
              <tr key={i} className="border-b border-[#141419] hover:bg-slate-800/20">
                <td className="py-3 pr-3 font-mono text-slate-100">{c.device}</td>
                <td className="py-3 pr-3 mono text-slate-300">{c.protocol}</td>
                <td className="py-3 pr-3"><span className={`chip ${c.link === 'up' ? 'chip-green' : c.link === 'degraded' ? 'chip-amber' : 'chip-red'}`}><Led tone={c.link === 'up' ? 'green' : c.link === 'degraded' ? 'amber' : 'red'} pulse size={7} /> {c.link.toUpperCase()}</span></td>
                <td className="py-3 pr-3 text-right mono text-slate-200">{c.latency_ms} ms</td>
                <td className="py-3 pr-3 w-40"><ProgressBar value={100 - Math.min(100, c.latency_ms)} max={100} tone={c.latency_ms > 80 ? 'amber' : 'cyan'} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}
