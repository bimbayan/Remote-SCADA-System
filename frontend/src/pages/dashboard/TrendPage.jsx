import React, { useState } from 'react';
import { Panel } from '../../components/scada/Atoms';
import { TRENDS } from '../../mock/mock';
import { Checkbox } from '../../components/ui/checkbox';
import { Label } from '../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Download } from 'lucide-react';
import { Button } from '../../components/ui/button';

const SERIES = [
  { key: 'ac', label: 'AC Power (kW)', color: '#06b6d4' },
  { key: 'dc', label: 'DC Power (kW)', color: '#8b5cf6' },
  { key: 'ghi', label: 'GHI (W/m²)', color: '#f59e0b', axis: 'r' },
  { key: 'pr', label: 'Performance Ratio', color: '#22c55e', axis: 'r2' },
  { key: 'module_c', label: 'Module Temp (°C)', color: '#ef4444' },
  { key: 'ambient_c', label: 'Ambient (°C)', color: '#fbbf24' },
];

const axisColor = '#475569';
const grid = '#1f2937';

export default function TrendPage() {
  const [visible, setVisible] = useState({ ac: true, dc: false, ghi: true, pr: true, module_c: false, ambient_c: false });
  const [range, setRange] = useState('5h');
  const [showRaw, setShowRaw] = useState(false);

  const rangeSlices = { '1h': 12, '5h': TRENDS.length, '24h': TRENDS.length };
  const data = TRENDS.slice(0, rangeSlices[range] || TRENDS.length);

  return (
    <div className="space-y-4">
      <Panel title="Multi-parameter time-series" right={
        <div className="flex items-center gap-2">
          <Select value={range} onValueChange={setRange}>
            <SelectTrigger className="w-28 h-8 bg-[#0a0a0f] border-slate-700 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="1h">Last 1h</SelectItem>
              <SelectItem value="5h">Last 5h</SelectItem>
              <SelectItem value="24h">Last 24h</SelectItem>
            </SelectContent>
          </Select>
          <Button size="sm" variant="outline" className="h-8 border-slate-700"><Download className="w-3.5 h-3.5 mr-1.5" /> CSV</Button>
        </div>
      }>
        <div className="flex flex-wrap gap-3 mb-4">
          {SERIES.map((s) => (
            <label key={s.key} className="flex items-center gap-2 cursor-pointer">
              <Checkbox checked={visible[s.key]} onCheckedChange={(v) => setVisible((prev) => ({ ...prev, [s.key]: v }))} />
              <span className="w-2.5 h-2.5 rounded-sm inline-block" style={{ background: s.color }} />
              <span className="text-xs text-slate-300">{s.label}</span>
            </label>
          ))}
        </div>

        <div style={{ height: 360 }}>
          <ResponsiveContainer>
            <LineChart data={data}>
              <CartesianGrid stroke={grid} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="t" stroke={axisColor} fontSize={11} tickLine={false} axisLine={false} />
              <YAxis yAxisId="l" stroke={axisColor} fontSize={11} tickLine={false} axisLine={false} />
              <YAxis yAxisId="r" orientation="right" stroke={axisColor} fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: '#0d0d13', border: '1px solid #1f1f27', fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              {SERIES.filter((s) => visible[s.key]).map((s) => (
                <Line key={s.key} yAxisId={s.axis === 'r' || s.axis === 'r2' ? 'r' : 'l'} dataKey={s.key} stroke={s.color} strokeWidth={2} dot={false} name={s.label} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <Panel title="Raw data" right={<button className="text-xs text-cyan-400 hover:text-cyan-300" onClick={() => setShowRaw((v) => !v)}>{showRaw ? 'Collapse' : 'Expand'}</button>}>
        {showRaw ? (
          <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="sticky top-0 bg-[#141419]">
                <tr className="text-left text-[10px] font-mono tracking-widest text-slate-500 uppercase border-b border-[#1f1f27]">
                  <th className="py-2 pr-3">Time</th>
                  <th className="py-2 pr-3 text-right">AC kW</th>
                  <th className="py-2 pr-3 text-right">DC kW</th>
                  <th className="py-2 pr-3 text-right">GHI W/m²</th>
                  <th className="py-2 pr-3 text-right">PR</th>
                  <th className="py-2 pr-3 text-right">Module °C</th>
                  <th className="py-2 pr-3 text-right">Ambient °C</th>
                </tr>
              </thead>
              <tbody>
                {data.map((r, i) => (
                  <tr key={i} className="border-b border-[#141419] hover:bg-slate-800/20">
                    <td className="py-2 pr-3 font-mono text-slate-300">{r.t}</td>
                    <td className="py-2 pr-3 text-right mono text-slate-100">{r.ac.toFixed(1)}</td>
                    <td className="py-2 pr-3 text-right mono text-slate-100">{r.dc.toFixed(1)}</td>
                    <td className="py-2 pr-3 text-right mono text-slate-100">{r.ghi}</td>
                    <td className="py-2 pr-3 text-right mono text-slate-100">{r.pr.toFixed(3)}</td>
                    <td className="py-2 pr-3 text-right mono text-slate-100">{r.module_c.toFixed(1)}</td>
                    <td className="py-2 pr-3 text-right mono text-slate-100">{r.ambient_c.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-xs text-slate-500">{data.length} rows available. Click Expand to inspect.</div>
        )}
      </Panel>
    </div>
  );
}
