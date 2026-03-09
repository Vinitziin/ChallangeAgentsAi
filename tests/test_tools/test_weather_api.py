"""Unit tests for the weather API tool."""

from unittest.mock import patch, MagicMock
from app.tools.weather_api import get_weather


MOCK_WEATHER_RESPONSE = {
    "name": "São Paulo",
    "main": {
        "temp": 25.3,
        "feels_like": 26.1,
        "humidity": 72,
    },
    "weather": [{"description": "nublado"}],
    "wind": {"speed": 3.5},
}


@patch("app.tools.weather_api.requests.get")
def test_get_weather_returns_structured_data(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_WEATHER_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = get_weather.invoke({"city": "São Paulo"})

    assert result["city"] == "São Paulo"
    assert result["temperature"] == 25.3
    assert result["description"] == "nublado"
    assert result["humidity"] == 72
    assert result["wind_speed"] == 3.5


@patch("app.tools.weather_api.requests.get")
def test_get_weather_calls_api_with_correct_params(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_WEATHER_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    get_weather.invoke({"city": "Curitiba"})

    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args
    assert call_kwargs[1]["params"]["q"] == "Curitiba"
    assert call_kwargs[1]["params"]["units"] == "metric"
