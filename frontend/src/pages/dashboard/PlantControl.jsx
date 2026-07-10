import React, { useState } from 'react';
import { Panel, Led, KpiCard } from '../../components/scada/Atoms';
import { Button } from '../../components/ui/button';
import { Slider } from '../../components/ui/slider';
import { Switch } from '../../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Label } from '../../components/ui/label';
import { toast } from 'sonner';
import { Power, Lock, ShieldAlert, Radio, Zap, PauseCircle, PlayCircle } from 'lucide-react';
import { KPI } from '../../mock/mock';

export default function PlantControl() {
  const [mode, setMode] = useState('auto');
  const [rampRate, setRampRate] = useState([10]);
  const [setpoint, setSetpoint] = useState([80]);
  const [reactive, setReactive] = useState([0]);
  const [remote, setRemote] = useState(true);
  const [freezeAlarms, setFreezeAlarms] = useState(false);

  const apply = () => toast.success('Setpoint dispatched to plant PLC', { description: `Mode: ${mode.toUpperCase()} · P=${setpoint[0]}% · Ramp=${rampRate[0]}%/min` });

  return (
    <div className="space-y-4">
      {/* Banner */}
      <div className="panel p-4 flex items-center gap-4 flex-wrap">
        <div className="w-12 h-12 rounded-lg bg-cyan-500/10 border border-cyan-500/30 grid place-items-center">
          <ShieldAlert className="w-6 h-6 text-cyan-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-lg font-semibold text-slate-100">Plant Control · Dispatch console</div>
          <div className="text-xs text-slate-500">All commands require operator authentication and are logged to the audit trail. Interlocks are enforced by the site PLC.</div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-emerald-500/30 bg-emerald-500/10">
          <Lock className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-xs font-mono text-emerald-400">Operator: J. Rao</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Panel title="Control mode">
          <div className="space-y-3">
            <Label className="text-slate-400 text-xs">Operating mode</Label>
            <Select value={mode} onValueChange={setMode}>
              <SelectTrigger className="bg-[#0a0a0f] border-slate-700"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">Auto (MPPT + policy)</SelectItem>
                <SelectItem value="manual">Manual dispatch</SelectItem>
                <SelectItem value="curtail">Curtailment</SelectItem>
                <SelectItem value="stop">Emergency stop</SelectItem>
              </SelectContent>
            </Select>
            <div className="flex items-center justify-between pt-2 border-t border-[#1f1f27]">
              <div><div className="text-xs text-slate-400">Remote control</div><div className="text-[10px] text-slate-600 mt-0.5">Grid operator can dispatch</div></div>
              <Switch checked={remote} onCheckedChange={setRemote} />
            </div>
            <div className="flex items-center justify-between">
              <div><div className="text-xs text-slate-400">Freeze alarms</div><div className="text-[10px] text-slate-600 mt-0.5">Silence during maintenance</div></div>
              <Switch checked={freezeAlarms} onCheckedChange={setFreezeAlarms} />
            </div>
          </div>
        </Panel>

        <Panel title="Active power setpoint">
          <div className="text-center py-2">
            <div className="text-4xl font-bold mono text-cyan-400">{setpoint[0]}%</div>
            <div className="text-xs text-slate-500 mt-1">{(setpoint[0] * 5).toFixed(0)} kW of 500 kW rated</div>
          </div>
          <Slider value={setpoint} onValueChange={setSetpoint} max={100} step={1} className="mt-4" />
          <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-2"><span>0%</span><span>50%</span><span>100%</span></div>

          <Label className="text-slate-400 text-xs mt-6 block">Ramp rate (%/min)</Label>
          <Slider value={rampRate} onValueChange={setRampRate} max={100} step={1} className="mt-2" />
          <div className="mono text-xs text-slate-300 mt-1">{rampRate[0]} %/min</div>
        </Panel>

        <Panel title="Reactive power (Q)">
          <div className="text-center py-2">
            <div className="text-4xl font-bold mono text-slate-100">{reactive[0] >= 0 ? '+' : ''}{reactive[0]}<span className="text-lg text-slate-500"> kVAr</span></div>
            <div className="text-xs text-slate-500 mt-1">{reactive[0] < 0 ? 'Under-excited' : reactive[0] > 0 ? 'Over-excited' : 'Unity'} · cosφ target 0.98</div>
          </div>
          <Slider value={reactive} onValueChange={setReactive} min={-100} max={100} step={1} className="mt-4" />
          <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-2"><span>-100</span><span>0</span><span>+100</span></div>
          <div className="mt-6 p-3 bg-slate-800/40 rounded-md text-xs text-slate-400">
            Grid code IEC 61727 compliance monitored automatically. Q setpoints override MPPT priority.
          </div>
        </Panel>
      </div>

      <Panel title="Alarm & interlock signals" right={<span className="text-[10px] font-mono text-slate-500">plant-wide</span>}>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {[
            { l: 'E-STOP', tone: 'green', v: 'Armed' },
            { l: 'FIRE PANEL', tone: 'green', v: 'Normal' },
            { l: 'DC ARC', tone: 'red', v: 'INV-04' },
            { l: 'GROUND FAULT', tone: 'green', v: 'Clear' },
            { l: 'OVER-VOLT', tone: 'green', v: 'Clear' },
            { l: 'UNDER-FREQ', tone: 'green', v: 'Clear' },
            { l: 'ISLAND', tone: 'green', v: 'Not detected' },
            { l: 'OIL TEMP', tone: 'amber', v: 'TX-01 rising' },
            { l: 'DOOR OPEN', tone: 'green', v: 'Closed' },
            { l: 'INTRUSION', tone: 'green', v: 'Normal' },
            { l: 'COMMS BESS', tone: 'amber', v: 'Degraded' },
            { l: 'BATTERY BMS', tone: 'green', v: 'OK' },
          ].map((s, i) => (
            <div key={i} className="panel p-3">
              <div className="flex items-center gap-2"><Led tone={s.tone} pulse={s.tone !== 'green'} size={9} /><div className="text-[10px] font-mono tracking-widest text-slate-500 uppercase">{s.l}</div></div>
              <div className="mt-1 text-sm text-slate-100">{s.v}</div>
            </div>
          ))}
        </div>
      </Panel>

      <div className="panel p-4 flex flex-wrap items-center gap-3 justify-between">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Radio className="w-3.5 h-3.5" /> Setpoints will be dispatched to the plant PLC on confirm.
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="border-slate-700 hover:bg-slate-800"><PauseCircle className="w-4 h-4 mr-2" /> Hold</Button>
          <Button variant="outline" className="border-red-500/30 text-red-400 hover:bg-red-500/10"><Power className="w-4 h-4 mr-2" /> Emergency stop</Button>
          <Button className="bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold" onClick={apply}><PlayCircle className="w-4 h-4 mr-2" /> Apply & dispatch</Button>
        </div>
      </div>
    </div>
  );
}
