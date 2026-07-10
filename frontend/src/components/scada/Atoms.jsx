import React from 'react';

export function Panel({ title, right, children, className = '' }) {
  return (
    <div className={`panel ${className}`}>
      {title && (
        <div className="panel-hdr">
          <span>{title}</span>
          {right}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}

export function KpiCard({ label, value, unit, sub, tone = 'default', icon: Icon }) {
  const toneColor = {
    default: 'text-slate-100',
    good: 'text-emerald-400',
    warn: 'text-amber-400',
    bad: 'text-red-400',
    info: 'text-cyan-400',
  }[tone];
  return (
    <div className="panel p-4 relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div className="text-[10px] font-mono tracking-widest text-slate-500 uppercase">{label}</div>
        {Icon && <Icon className="w-4 h-4 text-slate-600" />}
      </div>
      <div className="mt-2 flex items-baseline gap-1.5">
        <div className={`text-2xl font-bold mono ${toneColor}`}>{value}</div>
        {unit && <div className="text-xs text-slate-500 font-medium">{unit}</div>}
      </div>
      {sub && <div className="mt-1 text-xs text-slate-500">{sub}</div>}
    </div>
  );
}

export function Led({ tone = 'gray', pulse = false, size = 10 }) {
  const cls = { green: 'led-green', red: 'led-red', amber: 'led-amber', blue: 'led-blue', gray: 'led-gray' }[tone];
  return <span className={`led ${cls} ${pulse ? 'led-pulse' : ''}`} style={{ width: size, height: size }} />;
}

export function SeverityBadge({ s }) {
  const cls = { Critical: 'chip-red', High: 'chip-amber', Medium: 'chip-blue', Low: 'chip-gray' }[s] || 'chip-gray';
  return <span className={`chip ${cls}`}>{s}</span>;
}

export function StatusChip({ status }) {
  if (status === 'run') return <span className="chip chip-green"><Led tone="green" pulse size={7} /> RUN</span>;
  if (status === 'fault') return <span className="chip chip-red"><Led tone="red" pulse size={7} /> FAULT</span>;
  if (status === 'idle') return <span className="chip chip-gray"><Led tone="gray" size={7} /> IDLE</span>;
  return <span className="chip chip-blue"><Led tone="blue" pulse size={7} /> {status?.toUpperCase()}</span>;
}

export function ProgressBar({ value, max = 100, tone = 'cyan', showValue = false }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  const bg = { cyan: 'bg-cyan-500', green: 'bg-emerald-500', amber: 'bg-amber-500', red: 'bg-red-500' }[tone];
  return (
    <div className="w-full">
      <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
        <div className={`h-full ${bg} transition-all`} style={{ width: `${pct}%` }} />
      </div>
      {showValue && <div className="mt-1 text-[10px] font-mono text-slate-500 text-right">{pct.toFixed(1)}%</div>}
    </div>
  );
}

export function HalfDonut({ value = 0, max = 500, label = 'kW', title = 'POWER' }) {
  const pct = Math.max(0, Math.min(1, value / max));
  const angle = pct * 180;
  const r = 80;
  const cx = 100, cy = 100;
  const rad = (deg) => (Math.PI / 180) * deg;
  const x1 = cx + r * Math.cos(rad(180));
  const y1 = cy + r * Math.sin(rad(180));
  const x2 = cx + r * Math.cos(rad(180 + angle));
  const y2 = cy + r * Math.sin(rad(180 + angle));
  const largeArc = angle > 180 ? 1 : 0;
  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 200 120" width="100%" height="140">
        <path d={`M 20 100 A ${r} ${r} 0 0 1 180 100`} stroke="#1f2937" strokeWidth="12" fill="none" strokeLinecap="round" />
        <path d={`M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`} stroke="url(#donutGrad)" strokeWidth="12" fill="none" strokeLinecap="round" />
        <defs>
          <linearGradient id="donutGrad" x1="0" x2="1">
            <stop offset="0" stopColor="#06b6d4" />
            <stop offset="1" stopColor="#38bdf8" />
          </linearGradient>
        </defs>
        <text x="100" y="92" textAnchor="middle" fill="#f9fafb" fontSize="22" fontFamily="JetBrains Mono" fontWeight="700">{value.toFixed(1)}</text>
        <text x="100" y="108" textAnchor="middle" fill="#94a3b8" fontSize="10" fontFamily="JetBrains Mono">{label}</text>
      </svg>
      <div className="text-[10px] font-mono tracking-widest text-slate-500 uppercase mt-1">{title}</div>
    </div>
  );
}

export function Donut({ value = 0, max = 100, label = '%', color = '#06b6d4', size = 140 }) {
  const r = 60;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(1, value / max));
  return (
    <svg viewBox="0 0 160 160" width={size} height={size}>
      <circle cx="80" cy="80" r={r} fill="none" stroke="#1f2937" strokeWidth="12" />
      <circle cx="80" cy="80" r={r} fill="none" stroke={color} strokeWidth="12" strokeLinecap="round" strokeDasharray={`${c * pct} ${c}`} transform="rotate(-90 80 80)" />
      <text x="80" y="78" textAnchor="middle" fill="#f9fafb" fontSize="26" fontFamily="JetBrains Mono" fontWeight="700">{value.toFixed(1)}</text>
      <text x="80" y="96" textAnchor="middle" fill="#94a3b8" fontSize="11" fontFamily="JetBrains Mono">{label}</text>
    </svg>
  );
}
