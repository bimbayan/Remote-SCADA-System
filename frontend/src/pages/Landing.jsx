import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sun, Zap, Activity, Cpu, Radio, ShieldCheck, ChevronRight, Github, LineChart, BellRing, MapPin, Cloud, BatteryFull, Gauge } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';

const features = [
  { icon: Gauge, title: 'Live KPI strip', desc: 'AC/DC power, GHI, module temp, PR & uptime — refreshed every 5 seconds with millisecond fidelity.' },
  { icon: Radio, title: 'Single-line diagram', desc: 'Interactive SLD from array to POI with live breaker positions and inverter LEDs.' },
  { icon: LineChart, title: 'Multi-parameter trend', desc: 'Dual-axis time-series with performance ratio, irradiance and temperature overlays.' },
  { icon: BellRing, title: 'Alarm intelligence', desc: 'Severity-scored alarm ticker, filterable event table and 7-day frequency histogram.' },
  { icon: BatteryFull, title: 'Battery & utilities', desc: 'ESS SOC/SOH donuts, cycle statistics, weather station panels and comms diagnostics.' },
  { icon: MapPin, title: 'Location predictor', desc: 'Enter any coordinates or city — get a live weather-driven PV yield estimate.' },
];

const stats = [
  { k: '500 kW', v: 'Digital-twin plant' },
  { k: '5 × 100 kW', v: 'String inverters' },
  { k: '200 kWh', v: 'Battery ESS' },
  { k: '168 h', v: 'Hourly forecast' },
];

const pipeline = [
  { icon: Cloud, title: 'Open-Meteo API', desc: 'Live GHI, ambient, wind, humidity + 7-day hourly forecast over HTTPS.' },
  { icon: Cpu, title: 'Transparent PV model', desc: 'Cell-temp derating, 97% conversion, deterministic split across five inverters.' },
  { icon: Activity, title: 'Simulator + historian', desc: '500 kW plant, 200 kWh BESS, alarm engine with rolling snapshots.' },
  { icon: ShieldCheck, title: 'Recommendation engine', desc: 'Explainable rules for PR shortfall, battery policy and dispatch guidance.' },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-200">
      {/* NAV */}
      <nav className="sticky top-0 z-40 backdrop-blur-md bg-[#0a0a0f]/80 border-b border-[#1f1f27]">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-md bg-gradient-to-br from-cyan-400 to-sky-600 grid place-items-center">
              <Sun className="w-5 h-5 text-slate-900" strokeWidth={2.5} />
            </div>
            <div className="font-semibold tracking-tight text-slate-100">Solaris<span className="text-cyan-400">SCADA</span></div>
            <Badge variant="outline" className="ml-3 text-[10px] font-mono tracking-wider border-cyan-500/30 text-cyan-400">v3.0</Badge>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-slate-400">
            <a href="#features" className="hover:text-slate-100 transition-colors">Features</a>
            <a href="#architecture" className="hover:text-slate-100 transition-colors">Architecture</a>
            <a href="#pipeline" className="hover:text-slate-100 transition-colors">Data pipeline</a>
            <a href="https://github.com/bimbayan/Remote-SCADA-System" target="_blank" rel="noreferrer" className="hover:text-slate-100 transition-colors flex items-center gap-1.5"><Github className="w-4 h-4" />GitHub</a>
          </div>
          <Link to="/app/home">
            <Button className="bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold">
              Launch demo <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
        </div>
      </nav>

      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 grid-bg opacity-40" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0a0a0f]/60 to-[#0a0a0f]" />
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-cyan-500/10 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-6 pt-24 pb-24">
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/5 text-cyan-400 text-xs font-mono mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 led-pulse" /> Live · Open-Meteo API connected
            </div>
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-slate-50 leading-[1.05]">
              Remote SCADA for a<br />
              <span className="bg-gradient-to-r from-cyan-300 to-sky-500 bg-clip-text text-transparent">500&nbsp;kW solar plant</span>
            </h1>
            <p className="mt-6 text-lg text-slate-400 leading-relaxed max-w-2xl">
              A digital twin of a five-inverter photovoltaic plant with battery storage, live weather ingestion, single-line diagrams, alarm intelligence and a location-aware yield predictor — running fully in your browser.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/app/home">
                <Button size="lg" className="bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold h-12 px-6">
                  <Zap className="w-4 h-4 mr-2" /> Enter control room
                </Button>
              </Link>
              <Link to="/app/predictor">
                <Button size="lg" variant="outline" className="border-slate-700 hover:bg-slate-800 text-slate-200 h-12 px-6">
                  <MapPin className="w-4 h-4 mr-2" /> Try the predictor
                </Button>
              </Link>
            </div>

            <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl">
              {stats.map((s, i) => (
                <div key={i} className="panel p-4">
                  <div className="text-2xl font-bold text-slate-50 mono">{s.k}</div>
                  <div className="text-xs text-slate-500 mt-1 uppercase tracking-wider">{s.v}</div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* FEATURES */}
      <section id="features" className="relative py-24 border-t border-[#1f1f27]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-end justify-between mb-12 flex-wrap gap-4">
            <div>
              <div className="text-xs font-mono tracking-widest text-cyan-400 uppercase">Capabilities</div>
              <h2 className="mt-2 text-3xl md:text-4xl font-bold text-slate-50">Built for operators, not dashboards.</h2>
            </div>
            <p className="text-slate-400 max-w-md">Every pane surfaces one operational question. No hidden state, no silent staleness — every value is labelled as measured, modelled or simulated.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map((f, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.4, delay: i * 0.05 }} className="panel p-6 hover:border-cyan-500/30 transition-colors group">
                <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 grid place-items-center mb-4 group-hover:bg-cyan-500/20 transition-colors">
                  <f.icon className="w-5 h-5 text-cyan-400" />
                </div>
                <div className="font-semibold text-slate-100 mb-1">{f.title}</div>
                <div className="text-sm text-slate-400 leading-relaxed">{f.desc}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ARCHITECTURE PREVIEW */}
      <section id="architecture" className="relative py-24 border-t border-[#1f1f27]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-xs font-mono tracking-widest text-cyan-400 uppercase">Control room preview</div>
          <h2 className="mt-2 text-3xl md:text-4xl font-bold text-slate-50 max-w-2xl">Eight pages, one operating picture.</h2>

          <div className="mt-10 panel p-2 relative">
            <div className="absolute top-3 left-4 flex items-center gap-1.5 z-10">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500/70" />
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500/70" />
              <span className="w-2.5 h-2.5 rounded-full bg-green-500/70" />
            </div>
            <div className="pt-8 grid grid-cols-2 md:grid-cols-4 gap-1 p-2">
              {['Home', 'Dashboard', 'Plant Control', 'Overview', 'Substation', 'Alarms', 'Trend', 'Predictor'].map((p, i) => (
                <Link key={i} to={`/app/${p.toLowerCase().replace(' ', '')}`} className="panel p-4 hover:border-cyan-500/40 transition-colors group">
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-mono text-slate-500 uppercase tracking-wider">Page {String(i + 1).padStart(2, '0')}</div>
                    <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-cyan-400 transition-colors" />
                  </div>
                  <div className="mt-3 font-semibold text-slate-100">{p}</div>
                  <div className="mt-2 h-1 rounded-full bg-slate-800 overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-cyan-500 to-sky-400" style={{ width: `${40 + (i * 7) % 55}%` }} />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* DATA PIPELINE */}
      <section id="pipeline" className="relative py-24 border-t border-[#1f1f27]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-xs font-mono tracking-widest text-cyan-400 uppercase">Data lineage</div>
          <h2 className="mt-2 text-3xl md:text-4xl font-bold text-slate-50">From the atmosphere to the operator.</h2>

          <div className="mt-10 grid md:grid-cols-4 gap-4">
            {pipeline.map((p, i) => (
              <div key={i} className="panel p-5 relative">
                <div className="absolute top-3 right-3 text-[10px] font-mono text-slate-600">0{i + 1}</div>
                <div className="w-10 h-10 rounded-lg bg-slate-800 border border-slate-700 grid place-items-center mb-4">
                  <p.icon className="w-5 h-5 text-cyan-400" />
                </div>
                <div className="font-semibold text-slate-100">{p.title}</div>
                <div className="mt-1 text-sm text-slate-400 leading-relaxed">{p.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative py-24 border-t border-[#1f1f27] overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 to-transparent" />
        <div className="relative max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-50 tracking-tight">Step into the control room.</h2>
          <p className="mt-4 text-slate-400 max-w-2xl mx-auto">Every KPI, chart and diagram in the SCADA is live in the demo. Try the location predictor to see what your rooftop could deliver right now.</p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link to="/app/home"><Button size="lg" className="bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold h-12 px-6">Launch demo <ChevronRight className="w-4 h-4 ml-1" /></Button></Link>
            <a href="https://github.com/bimbayan/Remote-SCADA-System" target="_blank" rel="noreferrer"><Button size="lg" variant="outline" className="border-slate-700 hover:bg-slate-800 text-slate-200 h-12 px-6"><Github className="w-4 h-4 mr-2" /> Source on GitHub</Button></a>
          </div>
        </div>
      </section>

      <footer className="border-t border-[#1f1f27] py-8">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap items-center justify-between gap-4 text-sm text-slate-500">
          <div>© 2026 SolarisSCADA · Digital-twin demo. Weather data by Open-Meteo.</div>
          <div className="font-mono text-xs">v3.0 · build.2026.07.10</div>
        </div>
      </footer>
    </div>
  );
}
