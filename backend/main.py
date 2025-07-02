from fastapi import FastAPI, Query, HTTPException
import os
from dotenv import load_dotenv
import httpx
from datetime import datetime, timezone, date
from timezonefinder import TimezoneFinder
import pytz
from collections import defaultdict, Counter
from typing import List



# Load the .env file
load_dotenv()

# Declare app 
app = FastAPI()
# Set up a base url and retrieve api key
BASE_URL = "http://api.openweathermap.org"
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

# Endpoint that will take in city and return current weather along with forecast
@app.get("/weather")
async def get_weather(
  city: str = Query(..., description="City name"), # City parameter is required
  state: str | None = Query(None, description="State Code (ex. NJ for New Jersey) only for United States"), # Optional and only for US
  country: str | None = Query(None, description="ISO 2 letter country code (ex US for United States)") # Optional
  ):
  # Construct query based on what was inputted
  query = city
  if state:
    query += f",{state}"
  if country:
    query += f",{country}"

  # URL for getting call to get longitude and latitude
  geo_url = f"{BASE_URL}/geo/1.0/direct?q={query}&limit=1&appid={OPENWEATHER_KEY}"

  ## Call api and process response
  async with httpx.AsyncClient() as client:
    geo_response = await client.get(geo_url)
    geo_response.raise_for_status()
    geo_data = geo_response.json()

    if not geo_data:
      raise HTTPException(status_code=404, detail="Location not found")
    
    location = geo_data[0]
    lat = location["lat"]
    lon = location["lon"]

  # Construct URL to get current weather
  weather_url = f"{BASE_URL}/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=imperial"

  # Call api and process response
  async with httpx.AsyncClient() as client:
    weather_response = await client.get(weather_url)
    weather_response.raise_for_status()
    weather_data = weather_response.json()

  # Construct URL for forecast api call
  forecast_url = f"{BASE_URL}/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=imperial"

  # Call api and get results
  async with httpx.AsyncClient() as client:
    forecast_response = await client.get(forecast_url)
    forecast_response.raise_for_status()
    forecast_data = forecast_response.json()
    if not forecast_data:
      raise HTTPException(status_code=404, detail="Forecast not found")
    


  now = datetime.now(timezone.utc)

  today_forecast = [] # List to hold forecasts for the rest of the day
  daily_forecast = defaultdict(list) # dictionary that will hold forecasts for next 5 days including today

  # Get local timezone and local time
  tf = TimezoneFinder()
  timezone_str = tf.timezone_at(lng=lon, lat=lat)
  if timezone_str is None:
    timezone_str = "UTC"
  
  local_tz = pytz.timezone(timezone_str)
  now_local = datetime.now(timezone.utc).astimezone(local_tz)

  # For each piece of data in forecast_data 
  for entry in forecast_data["list"]:
    # Makes datetime object
    entry_time_utc = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

    #Sets entry datetime
    entry["_dt_utc"] = entry_time_utc 

    # Get local time 
    entry_time_local = entry_time_utc.astimezone(local_tz)

    # If in current day and later than the present add to today_forecast
    if entry_time_local.date() == now_local.date() and entry_time_local.time() >= now_local.time():
      today_forecast.append(entry)

    # Add to daily_forecast list index associated with appropiate date
    daily_forecast[entry_time_utc.date()].append(entry)

  # Call function to summarize data of the daily_forecasts
  summary = summarize_forecast_by_day(daily_forecast)



  todays_data = []
  # Process each entry in the today_forecast and keep only wanted details
  for entry in today_forecast:
    dt = entry["_dt_utc"]
    dt_local = dt.astimezone(local_tz)
    todays_data.append({
        "time": dt_local.strftime("%H:%M"),
        "temp": entry["main"]["temp"],
        "description": entry["weather"][0]["description"],
    })

  # Return all information including current weather and the forecast for the day and next few days
  return {
    "location": {
      "name": location["name"],
      "lat": lat,
      "lon": lon,
      "country": location.get("country"),
      "state": location.get("state")
    },
    "current_weather": {
      "temp": weather_data["main"]["temp"],
      "feels_like": weather_data["main"]["feels_like"],
      "description": weather_data["weather"][0]["description"]
    },
    "daily_forecast": summary,
    "todays_forecast": todays_data
  }



# Function to summarize the data of forecasts by day
def summarize_forecast_by_day(daily_forecast: dict[date, list]) -> list[dict]:
  summaries = []
  for date, entries in daily_forecast.items():
    temps = []
    descriptions = []
    for entry in entries:
      # Add temp and description to each list
      temps.append(entry["main"]["temp"])
      descriptions.append(entry["weather"][0]["description"])

    # Get high,low,avg of the day temps
    high = max(temps)
    low = min(temps)
    avg = sum(temps) / len(temps)

    # Get most common description which will be displayed
    most_common_desc = Counter(descriptions).most_common(1)[0][0]

    # Add data to summaries
    summaries.append({
      "date": date.isoformat(),
      "high": round(high,1),
      "low": round(low,1),
      "avg": round(avg,1),
      "description": most_common_desc
    })
  return summaries


