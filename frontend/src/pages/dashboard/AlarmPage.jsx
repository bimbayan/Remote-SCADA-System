import React, { useState, useMemo } from 'react';
import { Panel, SeverityBadge, Led } from '../../components/scada/Atoms';
import { ALARMS, ALARM_HISTOGRAM } from '../../mock/mock';
import { Input } from '../../components/ui/input';
import { Button } from '../../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Search, CheckCheck } from 'lucide-react';
import { toast } from 'sonner';

const axisColor = '#475569';
const grid = '#1f2937';

export default function AlarmPage() {
  const [query, setQuery] = useState('');
  const [severity, setSeverity] = useState('all');
  const [alarms, setAlarms] = useState(ALARMS);

  const filtered = useMemo(() => {
    return alarms.filter((a) =>
      (severity === 'all' || a.severity === severity) &&
      (a.message.toLowerCase().includes(query.toLowerCase()) || a.device.toLowerCase().includes(query.toLowerCase()) || a.code.toLowerCase().includes(query.toLowerCase()))
    );
  }, [alarms, query, severity]);

  const counts = useMemo(() => ({
    Critical: alarms.filter((a) => a.severity === 'Critical').length,
    High: alarms.filter((a) => a.severity === 'High').length,
    Medium: alarms.filter((a) => a.severity === 'Medium').length,
    Low: alarms.filter((a) => a.severity === 'Low').length,
    Unacked: alarms.filter((a) => !a.ack).length,
  }), [alarms]);

  const ackAll = () => {
    setAlarms((prev) => prev.map((a) => ({ ...a, ack: true })));
    toast.success('All active alarms acknowledged');
  };

  const ackOne = (id) => {
    setAlarms((prev) => prev.map((a) => (a.id === id ? { ...a, ack: true } : a)));
    toast.success(`Alarm ${id} acknowledged`);
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="panel p-4"><div className="text-[10px] font-mono text-slate-500 uppercase">Critical</div><div className="text-2xl font-bold mono text-red-400 mt-1">{counts.Critical}</div></div>
        <div className="panel p-4"><div className="text-[10px] font-mono text-slate-500 uppercase">High</div><div className="text-2xl font-bold mono text-amber-400 mt-1">{counts.High}</div></div>
        <div className="panel p-4"><div className="text-[10px] font-mono text-slate-500 uppercase">Medium</div><div className="text-2xl font-bold mono text-cyan-400 mt-1">{counts.Medium}</div></div>
        <div className="panel p-4"><div className="text-[10px] font-mono text-slate-500 uppercase">Low</div><div className="text-2xl font-bold mono text-slate-300 mt-1">{counts.Low}</div></div>
        <div className="panel p-4"><div className="text-[10px] font-mono text-slate-500 uppercase">Unacked</div><div className="text-2xl font-bold mono text-slate-100 mt-1">{counts.Unacked}</div></div>
      </div>

      <Panel title="Alarm frequency · last 7 days">
        <div style={{ height: 220 }}>
          <ResponsiveContainer>
            <BarChart data={ALARM_HISTOGRAM}>
              <CartesianGrid stroke={grid} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="day" stroke={axisColor} fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke={axisColor} fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: '#0d0d13', border: '1px solid #1f1f27', fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="critical" stackId="a" fill="#ef4444" name="Critical" />
              <Bar dataKey="high" stackId="a" fill="#f59e0b" name="High" />
              <Bar dataKey="medium" stackId="a" fill="#38bdf8" name="Medium" />
              <Bar dataKey="low" stackId="a" fill="#64748b" name="Low" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <Panel title="Alarm event log" right={<Button size="sm" variant="outline" onClick={ackAll} className="border-slate-700 hover:bg-slate-800 text-slate-200"><CheckCheck className="w-3.5 h-3.5 mr-1.5" /> Acknowledge all</Button>}>
        <div className="flex flex-wrap gap-2 mb-3">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search device, code or message…" className="pl-9 bg-[#0a0a0f] border-slate-700" />
          </div>
          <Select value={severity} onValueChange={setSeverity}>
            <SelectTrigger className="w-40 bg-[#0a0a0f] border-slate-700"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All severities</SelectItem>
              <SelectItem value="Critical">Critical</SelectItem>
              <SelectItem value="High">High</SelectItem>
              <SelectItem value="Medium">Medium</SelectItem>
              <SelectItem value="Low">Low</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[10px] font-mono tracking-widest text-slate-500 uppercase border-b border-[#1f1f27]">
                <th className="py-2 pr-3">ID</th>
                <th className="py-2 pr-3">Timestamp</th>
                <th className="py-2 pr-3">Severity</th>
                <th className="py-2 pr-3">Device</th>
                <th className="py-2 pr-3">Code</th>
                <th className="py-2 pr-3">Message</th>
                <th className="py-2 pr-3">Status</th>
                <th className="py-2 pr-3"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((a) => (
                <tr key={a.id} className={`border-b border-[#141419] hover:bg-slate-800/20 ${!a.ack ? 'bg-red-500/[0.02]' : ''}`}>
                  <td className="py-3 pr-3 font-mono text-xs text-slate-400">{a.id}</td>
                  <td className="py-3 pr-3 font-mono text-xs text-slate-300">{a.ts}</td>
                  <td className="py-3 pr-3"><SeverityBadge s={a.severity} /></td>
                  <td className="py-3 pr-3 font-mono text-slate-100">{a.device}</td>
                  <td className="py-3 pr-3 font-mono text-slate-300">{a.code}</td>
                  <td className="py-3 pr-3 text-slate-300">{a.message}</td>
                  <td className="py-3 pr-3">{a.ack ? <span className="chip chip-gray">ACK</span> : <span className="chip chip-amber"><Led tone="amber" pulse size={6} /> UNACK</span>}</td>
                  <td className="py-3 pr-3">{!a.ack && <Button size="sm" variant="outline" className="h-7 px-2 text-xs border-slate-700" onClick={() => ackOne(a.id)}>Ack</Button>}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={8} className="py-8 text-center text-slate-500 text-sm">No alarms match the current filter.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
