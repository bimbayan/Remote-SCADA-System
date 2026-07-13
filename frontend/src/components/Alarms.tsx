import { useEffect, useState } from 'react';
import { Alarm } from '../types';

export default function Alarms() {
  const [alarms, setAlarms] = useState<Alarm[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/alarms').then((res) => res.json()).then(setAlarms).finally(() => setLoading(false));
  }, []);

  const severityColor = (s: string) => s === 'Critical'
    ? 'bg-red-900/50 text-red-300 border-red-700'
    : s === 'Warning'
      ? 'bg-yellow-900/50 text-yellow-300 border-yellow-700'
      : 'bg-blue-900/50 text-blue-300 border-blue-700';

  return (
    <div className="p-6">
      <h1 className="mb-6 text-3xl font-bold text-red-400">Alarm History</h1>
      {loading ? <p>Loading alarms...</p> : (
        <div className="overflow-x-auto rounded-lg border border-gray-700 bg-gray-800">
          <table className="w-full text-left">
            <thead className="bg-gray-700 text-gray-300">
              <tr><th className="p-3">Time</th><th className="p-3">Device</th><th className="p-3">Message</th><th className="p-3">Severity</th></tr>
            </thead>
            <tbody>
              {alarms.map((alarm) => (
                <tr key={alarm.id} className="border-t border-gray-700 hover:bg-gray-700/50">
                  <td className="p-3">{new Date(alarm.timestamp).toLocaleString()}</td>
                  <td className="p-3">{alarm.device}</td>
                  <td className="p-3">{alarm.message}</td>
                  <td className="p-3"><span className={`rounded-full border px-3 py-1 text-xs font-bold ${severityColor(alarm.severity)}`}>{alarm.severity}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
