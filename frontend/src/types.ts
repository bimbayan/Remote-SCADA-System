export interface SensorData {
  timestamp: string;
  pv_current: number;
  pv_voltage: number;
  battery_soc: number;
  load_power: number;
}

export interface Alarm {
  id: number;
  timestamp: string;
  device: string;
  message: string;
  severity: 'Critical' | 'Warning' | 'Info';
}
