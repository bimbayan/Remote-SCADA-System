import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, Link, useLocation as useRouterLocation } from 'react-router-dom';
import { Sun, Home, LayoutDashboard, Sliders, Grid3x3, Cable, BellRing, LineChart, Wrench, MapPin, Wifi, WifiOff, ChevronLeft, Menu, ExternalLink } from 'lucide-react';
import { ALARMS } from '../mock/mock';
import LocationPicker from '../components/scada/LocationPicker';
import { useLocation } from '../lib/locationContext';

const NAV = [
  { to: 'home', label: 'Home', icon: Home, code: '01' },
  { to: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, code: '02' },
  { to: 'control', label: 'Plant Control', icon: Sliders, code: '03' },
  { to: 'overview', label: 'Overview', icon: Grid3x3, code: '04' },
  { to: 'substation', label: 'Substation', icon: Cable, code: '05' },
  { to: 'alarms', label: 'Alarms', icon: BellRing, code: '06' },
  { to: 'trend', label: 'Trend', icon: LineChart, code: '07' },
  { to: 'utilities', label: 'Utilities', icon: Wrench, code: '08' },
  { to: 'predictor', label: 'Predictor', icon: MapPin, code: '09' },
];

function useClock() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return now;
}

export default function DashboardLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [online, setOnline] = useState(true);
  const now = useClock();
  const loc = useRouterLocation();
  const { location: plant } = useLocation();

  useEffect(() => {
    // Flicker "link" indicator lightly
    const t = setInterval(() => setOnline((v) => (Math.random() > 0.02 ? true : v)), 3000);
    return () => clearInterval(t);
  }, []);

  const active = ALARMS.filter((a) => !a.ack);

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-200 flex">
      {/* SIDEBAR */}
      <aside className={`${collapsed ? 'w-16' : 'w-64'} shrink-0 bg-[#0d0d13] border-r border-[#1f1f27] flex flex-col transition-all duration-200`}>
        <div className="h-14 border-b border-[#1f1f27] flex items-center justify-between px-3">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-md bg-gradient-to-br from-cyan-400 to-sky-600 grid place-items-center shrink-0">
              <Sun className="w-5 h-5 text-slate-900" strokeWidth={2.5} />
            </div>
            {!collapsed && <div className="font-semibold tracking-tight text-slate-100 text-sm">Solaris<span className="text-cyan-400">SCADA</span></div>}
          </Link>
          <button onClick={() => setCollapsed((v) => !v)} className="text-slate-500 hover:text-slate-200 p-1 rounded transition-colors">
            {collapsed ? <Menu className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        <nav className="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto">
          {NAV.map((n) => (
            <NavLink key={n.to} to={n.to} className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/40 border border-transparent'
              }`
            }>
              <n.icon className="w-4 h-4 shrink-0" />
              {!collapsed && (
                <>
                  <span className="flex-1">{n.label}</span>
                  <span className="font-mono text-[10px] text-slate-600">{n.code}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Alarm ticker sidebar */}
        {!collapsed && (
          <div className="border-t border-[#1f1f27] p-3">
            <div className="text-[10px] font-mono tracking-widest text-slate-500 uppercase mb-2 flex items-center gap-1.5">
              <BellRing className="w-3 h-3 text-amber-400" /> Active alarms · {active.length}
            </div>
            <div className="space-y-1.5 max-h-40 overflow-hidden">
              {active.slice(0, 3).map((a) => (
                <div key={a.id} className="text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className={`led led-${a.severity === 'Critical' ? 'red' : a.severity === 'High' ? 'amber' : 'blue'} led-pulse w-2 h-2`} />
                    <span className="font-mono text-[10px] text-slate-500">{a.device}</span>
                  </div>
                  <div className="text-slate-400 truncate">{a.message}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </aside>

      {/* MAIN */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* TOPBAR */}
        <header className="h-14 border-b border-[#1f1f27] bg-[#0d0d13] flex items-center px-6 gap-4">
          <div className="min-w-0">
            <div className="text-[10px] font-mono tracking-widest text-slate-500 uppercase">Plant</div>
            <div className="text-sm font-semibold text-slate-100 leading-none mt-0.5 truncate max-w-[260px]">{plant.name}</div>
          </div>
          <div className="h-8 w-px bg-[#1f1f27] hidden md:block" />
          <div className="hidden md:block">
            <div className="text-[10px] font-mono tracking-widest text-slate-500 uppercase">Coordinates</div>
            <div className="text-sm text-slate-300 leading-none mt-0.5 mono">{plant.latitude.toFixed(3)}, {plant.longitude.toFixed(3)}</div>
          </div>

          <div className="flex-1" />

          <LocationPicker />

          <div className="flex items-center gap-2 px-3 py-1 rounded-md border border-[#1f1f27] bg-[#0a0a0f]">
            {online ? <Wifi className="w-3.5 h-3.5 text-emerald-400" /> : <WifiOff className="w-3.5 h-3.5 text-red-400" />}
            <span className="text-xs font-mono text-slate-300">API {online ? 'live' : 'offline'}</span>
            <span className={`led ${online ? 'led-green' : 'led-red'} led-pulse w-1.5 h-1.5`} />
          </div>

          <div className="hidden lg:block text-right">
            <div className="font-mono text-sm text-slate-100 leading-none">{now.toLocaleTimeString('en-GB')}</div>
            <div className="font-mono text-[10px] text-slate-500 mt-0.5">{now.toLocaleDateString('en-GB', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' })}</div>
          </div>

          <a href="https://github.com/bimbayan/Remote-SCADA-System" target="_blank" rel="noreferrer" className="text-slate-500 hover:text-slate-100 transition-colors">
            <ExternalLink className="w-4 h-4" />
          </a>
        </header>

        {/* Alarm marquee */}
        <div className="h-8 bg-[#0d0d13] border-b border-[#1f1f27] overflow-hidden relative">
          <div className="absolute inset-y-0 left-0 z-10 px-3 flex items-center gap-2 bg-[#0d0d13] border-r border-[#1f1f27]">
            <BellRing className="w-3 h-3 text-amber-400" />
            <span className="text-[10px] font-mono tracking-widest text-amber-400 uppercase">Live alarms</span>
          </div>
          <div className="ticker-scroll flex whitespace-nowrap items-center h-full pl-40">
            {[...active, ...active].map((a, i) => (
              <span key={i} className="text-xs mr-10 flex items-center gap-2">
                <span className={`led led-${a.severity === 'Critical' ? 'red' : a.severity === 'High' ? 'amber' : 'blue'} w-1.5 h-1.5`} />
                <span className="font-mono text-slate-500">[{a.ts.slice(-8)}]</span>
                <span className="text-slate-500">{a.severity.toUpperCase()}</span>
                <span className="text-slate-400">· {a.device}</span>
                <span className="text-slate-300">— {a.message}</span>
              </span>
            ))}
          </div>
        </div>

        {/* CONTENT */}
        <main key={loc.pathname} className="flex-1 overflow-auto p-6 fade-up">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
