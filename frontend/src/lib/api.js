import axios from 'axios';

const BACKEND = process.env.REACT_APP_BACKEND_URL || '';
const api = axios.create({ baseURL: `${BACKEND}/api`, timeout: 20000 });

export async function geocode(query, count = 6) {
  const { data } = await api.get('/geocode', { params: { q: query, count } });
  return data.results || [];
}

export async function getLive(lat, lon, size_kw = 500) {
  const { data } = await api.get('/live', { params: { lat, lon, size_kw } });
  return data;
}

export async function getForecast(lat, lon, size_kw = 500, hours = 48) {
  const { data } = await api.get('/forecast', { params: { lat, lon, size_kw, hours } });
  return data;
}

export async function health() {
  const { data } = await api.get('/health');
  return data;
}
