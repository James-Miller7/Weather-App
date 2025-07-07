import axios from 'axios';

const API_BASE = "http://localhost:8000"

export const fetchWeather = async (city, state, country) => {
  const params = new URLSearchParams({ city });

  if (state) {
    params.append("state", state);
    params.append("country", "US")
  }
  else if (country) {
    params.append("country", country)
  }

  const response = await axios.get(`${API_BASE}/weather?${params}`);
  return response.data
};

