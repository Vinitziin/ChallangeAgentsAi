"""Weather API tool using OpenWeatherMap."""

from dataclasses import dataclass
from typing import Any

import requests
from langchain_core.tools import tool

from app.config import settings


@dataclass
class WeatherData:
    """Structured weather information."""

    city: str
    temperature: float
    feels_like: float
    description: str
    humidity: int
    wind_speed: float


@tool
def get_weather(city: str) -> dict[str, Any]:
    """Get current weather information for a city.

    Args:
        city: Name of the city (e.g. 'São Paulo', 'New York').

    Returns:
        Weather data including temperature, description, humidity, and wind.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "pt_br",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        if status == 401:
            return {"error": "API key do OpenWeatherMap inválida ou ainda não ativada. Keys novas podem levar até 2h para ativar."}
        return {"error": f"Erro HTTP {status} ao consultar o clima."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro de conexão ao consultar o clima: {str(e)}"}

    data = response.json()

    weather = WeatherData(
        city=data["name"],
        temperature=data["main"]["temp"],
        feels_like=data["main"]["feels_like"],
        description=data["weather"][0]["description"],
        humidity=data["main"]["humidity"],
        wind_speed=data["wind"]["speed"],
    )

    return {
        "city": weather.city,
        "temperature": weather.temperature,
        "feels_like": weather.feels_like,
        "description": weather.description,
        "humidity": weather.humidity,
        "wind_speed": weather.wind_speed,
    }
