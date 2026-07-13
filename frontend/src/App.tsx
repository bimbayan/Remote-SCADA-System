import { useState } from 'react';
import Dashboard from './components/Dashboard';
import Alarms from './components/Alarms';
import Predict from './components/Predict';

type Tab = 'dashboard' | 'alarms' | 'predict';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <nav className="flex gap-3 border-b border-gray-700 bg-gray-800 p-4">
        <TabButton active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')}>Dashboard</TabButton>
        <TabButton active={activeTab === 'alarms'} onClick={() => setActiveTab('alarms')}>Alarms</TabButton>
        <TabButton active={activeTab === 'predict'} onClick={() => setActiveTab('predict')}>ML Predictor</TabButton>
      </nav>
      <main>
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'alarms' && <Alarms />}
        {activeTab === 'predict' && <Predict />}
      </main>
    </div>
  );
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button onClick={onClick} className={`rounded-md px-4 py-2 font-semibold ${active ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-700'}`}>
      {children}
    </button>
  );
}

export default App;
