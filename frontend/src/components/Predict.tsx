import { useState } from 'react';

export default function Predict() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    try {
      const res = await fetch('/api/predict', { method: 'POST', body: formData });
      setResult(await res.json());
    } catch {
      setResult({ error: 'Upload failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl p-6">
      <h1 className="mb-6 text-3xl font-bold text-purple-400">ML Predictor</h1>
      <div className="rounded-lg border border-gray-700 bg-gray-800 p-6">
        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} className="block w-full text-sm text-gray-300" />
        <button onClick={handleUpload} disabled={!file || loading} className="mt-4 rounded-md bg-blue-600 px-6 py-2 font-bold text-white disabled:opacity-50">
          {loading ? 'Processing...' : 'Run Prediction'}
        </button>
        {result && <pre className="mt-6 overflow-auto rounded-md bg-gray-900 p-4 text-sm text-green-300">{JSON.stringify(result, null, 2)}</pre>}
      </div>
    </div>
  );
}
