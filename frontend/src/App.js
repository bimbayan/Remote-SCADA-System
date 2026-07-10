import React from 'react';
import './App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import DashboardLayout from './pages/DashboardLayout';
import HomePage from './pages/dashboard/HomePage';
import Dashboard from './pages/dashboard/Dashboard';
import PlantControl from './pages/dashboard/PlantControl';
import Overview from './pages/dashboard/Overview';
import Substation from './pages/dashboard/Substation';
import AlarmPage from './pages/dashboard/AlarmPage';
import TrendPage from './pages/dashboard/TrendPage';
import Utilities from './pages/dashboard/Utilities';
import Predictor from './pages/dashboard/Predictor';
import { Toaster } from './components/ui/sonner';
import { LocationProvider } from './lib/locationContext';

function App() {
  return (
    <div className="App">
      <LocationProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/app" element={<DashboardLayout />}>
              <Route index element={<Navigate to="home" replace />} />
              <Route path="home" element={<HomePage />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="control" element={<PlantControl />} />
              <Route path="overview" element={<Overview />} />
              <Route path="substation" element={<Substation />} />
              <Route path="alarms" element={<AlarmPage />} />
              <Route path="trend" element={<TrendPage />} />
              <Route path="utilities" element={<Utilities />} />
              <Route path="predictor" element={<Predictor />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </LocationProvider>
      <Toaster theme="dark" position="top-right" />
    </div>
  );
}

export default App;
