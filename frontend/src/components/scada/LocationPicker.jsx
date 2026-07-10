import React, { useState, useEffect, useRef } from 'react';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Button } from '../ui/button';
import { MapPin, Search, Loader2, Check } from 'lucide-react';
import { toast } from 'sonner';
import { geocode } from '../../lib/api';
import { useLocation } from '../../lib/locationContext';

export default function LocationPicker() {
  const { location, setLocation, reset } = useLocation();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [name, setName] = useState(location?.name || '');
  const [suggestions, setSuggestions] = useState([]);
  const [searching, setSearching] = useState(false);
  const [selected, setSelected] = useState(null);
  const debRef = useRef(null);

  useEffect(() => {
    if (open) setName(location?.name || '');
  }, [open, location]);

  useEffect(() => {
    if (!query || query.length < 2) {
      setSuggestions([]);
      return;
    }
    if (debRef.current) clearTimeout(debRef.current);
    debRef.current = setTimeout(async () => {
      try {
        setSearching(true);
        const results = await geocode(query, 8);
        setSuggestions(results);
      } catch (e) {
        setSuggestions([]);
      } finally {
        setSearching(false);
      }
    }, 350);
    return () => debRef.current && clearTimeout(debRef.current);
  }, [query]);

  const pick = (item) => {
    setSelected(item);
    setQuery('');
    setSuggestions([]);
  };

  const save = () => {
    if (!selected) {
      toast.error('Search and pick a city first');
      return;
    }
    setLocation({
      name: name.trim() || `${selected.name} Solar Plant`,
      city: selected.name,
      admin1: selected.admin1,
      country: selected.country,
      latitude: selected.latitude,
      longitude: selected.longitude,
      timezone: selected.timezone,
      isDefault: false,
    });
    toast.success(`Plant location updated — ${selected.name}`);
    setOpen(false);
    setSelected(null);
  };

  const clear = () => {
    reset();
    toast.success('Restored default plant location');
    setOpen(false);
    setSelected(null);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-slate-700 hover:border-cyan-500/40 hover:bg-slate-800/40 transition-colors text-left">
          <MapPin className="w-3.5 h-3.5 text-cyan-400" />
          <div>
            <div className="text-[10px] font-mono text-slate-500 uppercase leading-none">Plant</div>
            <div className="text-xs text-slate-100 mt-0.5 leading-none max-w-[220px] truncate">{location.city}, {location.country}</div>
          </div>
        </button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-[380px] bg-[#0d0d13] border-[#1f1f27] text-slate-200">
        <div className="space-y-3">
          <div>
            <div className="text-sm font-semibold text-slate-100">Set plant location</div>
            <div className="text-xs text-slate-500 mt-0.5">Any city on Earth. Only the label / topbar / system info changes — telemetry stays simulated.</div>
          </div>

          <div>
            <Label className="text-slate-400 text-xs">Plant name</Label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Ridge Valley PV Array" className="mt-1 bg-[#0a0a0f] border-slate-700" />
          </div>

          <div>
            <Label className="text-slate-400 text-xs">Search a city</Label>
            <div className="relative mt-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Type at least 2 letters…" className="pl-9 pr-9 bg-[#0a0a0f] border-slate-700" />
              {searching && <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 animate-spin" />}
            </div>
            {suggestions.length > 0 && (
              <div className="mt-1 max-h-52 overflow-y-auto border border-slate-700 rounded-md">
                {suggestions.map((s, i) => (
                  <button key={`${s.name}-${s.latitude}-${s.longitude}-${i}`} onClick={() => pick(s)} className="w-full text-left px-3 py-2 hover:bg-slate-800/60 border-b border-[#1f1f27] last:border-b-0 transition-colors">
                    <div className="flex items-center justify-between gap-2">
                      <div>
                        <div className="text-sm text-slate-100">{s.name}</div>
                        <div className="text-[10px] text-slate-500">{[s.admin1, s.country].filter(Boolean).join(', ')}</div>
                      </div>
                      <div className="font-mono text-[10px] text-slate-500">{s.latitude.toFixed(2)}, {s.longitude.toFixed(2)}</div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {selected && (
            <div className="panel p-2.5 border border-cyan-500/30 bg-cyan-500/5">
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-cyan-400" />
                <div className="text-sm text-slate-100">{selected.name}</div>
                <div className="text-[10px] text-slate-500 ml-auto mono">{selected.latitude.toFixed(3)}, {selected.longitude.toFixed(3)}</div>
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5 ml-6">{[selected.admin1, selected.country].filter(Boolean).join(', ')} · {selected.timezone || 'auto'}</div>
            </div>
          )}

          <div className="flex justify-between gap-2 pt-2 border-t border-[#1f1f27]">
            <Button variant="ghost" size="sm" onClick={clear} className="text-xs text-slate-400 hover:text-slate-100 hover:bg-slate-800">Reset default</Button>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => setOpen(false)} className="border-slate-700">Cancel</Button>
              <Button size="sm" onClick={save} disabled={!selected} className="bg-cyan-500 hover:bg-cyan-400 text-slate-900 disabled:opacity-50">Save location</Button>
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
