"""
Weather tool for demonstrating MCP tool capabilities.
Provides weather information for cities using mock data.
"""

import json
from datetime import datetime
from typing import Any, Dict

from mcp_server.core.protocol import ToolResult, ToolSchema
from mcp_server.tools.base import Tool


class WeatherTool(Tool):
    """Weather tool that provides weather information for cities."""
    
    def __init__(self):
        """Initialize weather tool."""
        super().__init__(
            name="get_weather",
            description="Get current weather information for a specified city"
        )
        
        # Mock weather data for demonstration
        self._mock_weather_data = {
            "london": {
                "temperature": 15.2,
                "humidity": 68,
                "description": "Partly cloudy",
                "wind_speed": 12.5,
                "pressure": 1013.2
            },
            "new york": {
                "temperature": 22.1,
                "humidity": 55,
                "description": "Sunny",
                "wind_speed": 8.3,
                "pressure": 1018.7
            },
            "tokyo": {
                "temperature": 18.7,
                "humidity": 72,
                "description": "Light rain",
                "wind_speed": 6.2,
                "pressure": 1009.8
            },
            "paris": {
                "temperature": 16.8,
                "humidity": 61,
                "description": "Overcast",
                "wind_speed": 9.7,
                "pressure": 1015.3
            },
            "sydney": {
                "temperature": 25.4,
                "humidity": 58,
                "description": "Clear sky",
                "wind_speed": 14.1,
                "pressure": 1020.1
            },
            "berlin": {
                "temperature": 12.3,
                "humidity": 74,
                "description": "Foggy",
                "wind_speed": 5.8,
                "pressure": 1011.9
            }
        }
    
    def get_schema(self) -> ToolSchema:
        """Get the tool's schema definition."""
        return ToolSchema(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city to get weather for",
                        "minLength": 1,
                        "maxLength": 100
                    },
                    "units": {
                        "type": "string",
                        "description": "Temperature units (metric, imperial, or kelvin)",
                        "enum": ["metric", "imperial", "kelvin"],
                        "default": "metric"
                    }
                },
                "required": ["city"],
                "additionalProperties": False
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute the weather tool."""
        try:
            # Validate arguments
            schema = self.get_schema().input_schema
            self._validate_arguments(arguments, schema)
            
            # Extract and validate city parameter
            city = arguments["city"].strip()
            if not city:
                return self._create_error_result("City name cannot be empty")
            
            # Extract units parameter (default to metric)
            units = arguments.get("units", "metric")
            
            # Normalize city name for lookup
            city_normalized = city.lower()
            
            # Check if city exists in our mock data
            if city_normalized not in self._mock_weather_data:
                available_cities = ", ".join(sorted(self._mock_weather_data.keys()))
                return self._create_error_result(
                    f"Weather data not available for '{city}'. "
                    f"Available cities: {available_cities}"
                )
            
            # Get weather data
            weather_data = self._mock_weather_data[city_normalized].copy()
            
            # Convert temperature based on units
            temperature = weather_data["temperature"]
            if units == "imperial":
                # Convert Celsius to Fahrenheit
                temperature = (temperature * 9/5) + 32
                temp_unit = "°F"
            elif units == "kelvin":
                # Convert Celsius to Kelvin
                temperature = temperature + 273.15
                temp_unit = "K"
            else:  # metric (default)
                temp_unit = "°C"
            
            # Format weather information
            weather_info = {
                "city": city.title(),
                "temperature": round(temperature, 1),
                "temperature_unit": temp_unit,
                "humidity": weather_data["humidity"],
                "description": weather_data["description"],
                "wind_speed": weather_data["wind_speed"],
                "pressure": weather_data["pressure"],
                "timestamp": datetime.now().isoformat(),
                "units": units
            }
            
            # Create formatted response
            response_text = self._format_weather_response(weather_info)
            
            return self._create_text_result(response_text)
            
        except ValueError as e:
            return self._create_error_result(f"Invalid input: {str(e)}")
        except Exception as e:
            return self._create_error_result(f"Weather service error: {str(e)}")
    
    def _format_weather_response(self, weather_info: Dict[str, Any]) -> str:
        """Format weather information into a readable response."""
        return f"""Weather for {weather_info['city']}:
Temperature: {weather_info['temperature']}{weather_info['temperature_unit']}
Humidity: {weather_info['humidity']}%
Conditions: {weather_info['description']}
Wind Speed: {weather_info['wind_speed']} km/h
Pressure: {weather_info['pressure']} hPa
Last Updated: {weather_info['timestamp']}
Units: {weather_info['units']}"""