import { useEffect, useRef, useState } from 'react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { SensorData } from '../types';

export default function Dashboard() {
  const [data, setData] = useState<SensorData[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetch('/api/sensors').then((res) => res.json()).then((d: SensorData) => setData([d])).catch(console.error);
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${scheme}://${window.location.host}/ws`);
    wsRef.current = ws;
    ws.onmessage = (event) => {
      const point: SensorData = JSON.parse(event.data);
      setData((prev) => [...prev.slice(-49), point]);
    };
    ws.onerror = console.error;
    return () => ws.close();
  }, []);

  const latest = data.at(-1);

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold text-blue-400">SCADA Live Dashboard</h1>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <MetricCard label="PV Current" value={latest?.pv_current} unit="A" />
        <MetricCard label="PV Voltage" value={latest?.pv_voltage} unit="V" />
        <MetricCard label="Battery SoC" value={latest?.battery_soc} unit="%" color="green" />
        <MetricCard label="Load Power" value={latest?.load_power} unit="kW" />
      </div>
      <div className="rounded-lg border border-gray-700 bg-gray-800 p-4">
        <h2 className="mb-4 text-xl font-semibold">PV Current Trend</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="timestamp" stroke="#9CA3AF" tickFormatter={(t) => new Date(t).toLocaleTimeString()} />
            <YAxis stroke="#9CA3AF" />
            <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
            <Line type="monotone" dataKey="pv_current" stroke="#60A5FA" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function MetricCard({ label, value, unit, color = 'blue' }: { label: string; value?: number; unit: string; color?: 'blue' | 'green' | 'red' }) {
  const colorMap = { blue: 'text-blue-400', green: 'text-green-400', red: 'text-red-400' };
  return (
    <div className="rounded-lg border border-gray-700 bg-gray-800 p-4">
      <p className="text-sm text-gray-400">{label}</p>
      <p className={`text-3xl font-bold ${colorMap[color]}`}>
        {value == null ? '--' : value.toFixed(2)} <span className="text-base text-gray-400">{unit}</span>
      </p>
    </div>
  );
}
