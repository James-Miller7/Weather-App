import { use, useState } from 'react'
import { fetchWeather } from './api/client'
import './App.css'
import countries from "i18n-iso-countries";
import enLocale from "i18n-iso-countries/langs/en.json";


function App() {
  const [city, setCity] = useState("")
  const [state, setState] = useState("")
  const [country, setCountry] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [weather, setWeather] = useState(null)
  const [error, setError] = useState(null)
  const state_options = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
  ];
  countries.registerLocale(enLocale);

  const countryCodes = countries.getAlpha2Codes();

  const countryCodeArray = Object.keys(countryCodes);


  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    try {
      const data = await fetchWeather(city, state, country)
      setWeather(data)
    } catch (err) {
      console.error(err)
      setError("Could not fetch weather")
    } finally {
      setIsLoading(false)
    }

  }
  return (
    <div className='container'>
      <h1 className='header'>Weather App</h1>
      <form onSubmit={handleSubmit} >
        <input placeholder='City' value={city} onChange={e => setCity(e.target.value)} required />
        <select name="state" value={state} onChange={e => setState(e.target.value)}>
          <option value="">-- Select State --</option>
          {state_options.map((state) => (
            <option key={state} value={state}>
              {state}
            </option>
          ))}
        </select>
        <select name="country" value={country} onChange={e => setCountry(e.target.value)}>
          <option value="">-- Select Country --</option>
          {countryCodeArray.map((code) => (
            <option key={code} value={code}>
              {countries.getName(code, "en")}
            </option>
          ))}
        </select>
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Loading..." : "Get Weather"}
        </button>
      </form>

      {isLoading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {weather && (
        <div>
          <h2>Current Weather in {weather.location.name}, {weather.location.country}</h2>
          <p>{weather.current_weather.description}</p>
          <p>Temperature: {weather.current_weather.temp}°F</p>
          <p>Feels Like: {weather.current_weather.feels_like}</p>


          <h3>Today's Forecast</h3>
          {weather.todays_forecast.map((entry, idx) => (
            <div key={idx}>
              <strong>{entry.time}</strong>: {entry.temp}°F, {entry.description}
            </div>
          ))}

          <h3>5-Day Forecast</h3>
          {weather.daily_forecast.map((day, idx) => (
            <div key={idx}>
              <strong>{day.date}</strong>: {day.description} - High: {day.high}°F, Low: {day.low}°F, Average: {day.avg}°F
            </div>
          ))}
        </div>


      )
      }
    </div >

  )
}

export default App
