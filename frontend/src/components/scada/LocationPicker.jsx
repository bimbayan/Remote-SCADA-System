import React, { useState, useEffect } from 'react';
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
  const [name, setName] = useState(location?.name || '');
  const [query, setQuery] = useState('');
  const [resolving, setResolving] = useState(false);

  useEffect(() => {
    if (open) {
      setName(location?.name || '');
      setQuery('');
    }
  }, [open, location]);

  const save = async () => {
    const q = query.trim();
    if (q.length < 2) {
      toast.error('Please enter a location (at least 2 characters)');
      return;
    }
    setResolving(true);
    try {
      const results = await geocode(q, 1);
      if (!results || results.length === 0) {
        toast.error('Location not found', { description: `No place matches "${q}". Try a nearby larger city.` });
        return;
      }
      const hit = results[0];
      setLocation({
        name: (name.trim() || `${q} Solar Plant`),
        city: q,
        admin1: hit.admin1,
        country: hit.country,
        latitude: hit.latitude,
        longitude: hit.longitude,
        timezone: hit.timezone,
        isDefault: false,
      });
      toast.success(`Plant location updated`, { description: `${q} · ${hit.latitude.toFixed(2)}°, ${hit.longitude.toFixed(2)}°` });
      setOpen(false);
    } catch (e) {
      toast.error('Could not resolve location', { description: e?.message || 'Network error' });
    } finally {
      setResolving(false);
    }
  };

  const clear = () => {
    reset();
    toast.success('Restored default plant location');
    setOpen(false);
  };

  const onKey = (e) => {
    if (e.key === 'Enter') save();
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-slate-700 hover:border-cyan-500/40 hover:bg-slate-800/40 transition-colors text-left">
          <MapPin className="w-3.5 h-3.5 text-cyan-400" />
          <div>
            <div className="text-[10px] font-mono text-slate-500 uppercase leading-none">Plant</div>
            <div className="text-xs text-slate-100 mt-0.5 leading-none max-w-[220px] truncate">{location.city}{location.country ? `, ${location.country}` : ''}</div>
          </div>
        </button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-[360px] bg-[#0d0d13] border-[#1f1f27] text-slate-200">
        <div className="space-y-3">
          <div>
            <div className="text-sm font-semibold text-slate-100">Set plant location</div>
            <div className="text-xs text-slate-500 mt-0.5">Any city or place. Only the label / topbar / system info updates — telemetry stays simulated.</div>
          </div>

          <div>
            <Label className="text-slate-400 text-xs">Plant name</Label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Ridge Valley PV Array" className="mt-1 bg-[#0a0a0f] border-slate-700" />
          </div>

          <div>
            <Label className="text-slate-400 text-xs">Location</Label>
            <div className="relative mt-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <Input value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={onKey} placeholder="Type any city or place…" className="pl-9 bg-[#0a0a0f] border-slate-700" />
            </div>
            <div className="mt-1 text-[10px] text-slate-500">Press Enter or click Save. We use the closest known city if the exact place isn't in the map database.</div>
          </div>

          <div className="flex justify-between gap-2 pt-2 border-t border-[#1f1f27]">
            <Button variant="ghost" size="sm" onClick={clear} className="text-xs text-slate-400 hover:text-slate-100 hover:bg-slate-800">Reset default</Button>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => setOpen(false)} className="border-slate-700">Cancel</Button>
              <Button size="sm" onClick={save} disabled={resolving || query.trim().length < 2} className="bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold disabled:opacity-50">
                {resolving ? <><Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> Saving…</> : <><Check className="w-3.5 h-3.5 mr-1.5" /> Save location</>}
              </Button>
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
