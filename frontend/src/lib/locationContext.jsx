import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

const STORAGE_KEY = 'solaris.plant.location';

const DEFAULT_LOCATION = {
  name: 'Sunrise Solar Farm — Unit 1',
  city: 'Bengaluru',
  admin1: 'Karnataka',
  country: 'India',
  latitude: 12.9716,
  longitude: 77.5946,
  timezone: 'Asia/Kolkata',
  isDefault: true,
};

const LocationContext = createContext({ location: DEFAULT_LOCATION, setLocation: () => {} });

export function LocationProvider({ children }) {
  const [location, setLocationState] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) {
      // ignore
    }
    return DEFAULT_LOCATION;
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(location));
    } catch (e) {
      // ignore
    }
  }, [location]);

  const setLocation = useCallback((next) => {
    setLocationState((prev) => ({ ...prev, ...next }));
  }, []);

  const reset = useCallback(() => setLocationState(DEFAULT_LOCATION), []);

  return (
    <LocationContext.Provider value={{ location, setLocation, reset }}>
      {children}
    </LocationContext.Provider>
  );
}

export function useLocation() {
  return useContext(LocationContext);
}

export function formatLocation(loc) {
  if (!loc) return '';
  return [loc.city, loc.admin1, loc.country].filter(Boolean).join(', ');
}
