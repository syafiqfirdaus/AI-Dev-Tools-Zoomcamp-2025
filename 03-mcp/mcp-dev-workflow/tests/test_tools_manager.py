"""
Tests for the tools management system.
"""

import pytest

from mcp_server.core.protocol import ToolResult, ToolSchema
from mcp_server.tools import Tool, ToolsManager, EchoTool, WeatherTool


class TestTool(Tool):
    """Test tool for unit testing."""
    
    def __init__(self, name: str = "test_tool"):
        super().__init__(name, "Test tool for unit testing")
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "value": {"type": "string"}
                },
                "required": ["value"]
            }
        )
    
    async def execute(self, arguments):
        return self._create_text_result(f"Test: {arguments.get('value', 'default')}")


class TestToolsManager:
    """Test cases for ToolsManager."""
    
    def test_register_tool(self):
        """Test tool registration."""
        manager = ToolsManager()
        tool = TestTool()
        
        manager.register_tool(tool)
        
        assert manager.has_tool("test_tool")
        assert manager.get_tool("test_tool") is tool
    
    def test_register_duplicate_tool_raises_error(self):
        """Test that registering duplicate tool names raises error."""
        manager = ToolsManager()
        tool1 = TestTool("duplicate")
        tool2 = TestTool("duplicate")
        
        manager.register_tool(tool1)
        
        with pytest.raises(ValueError, match="already registered"):
            manager.register_tool(tool2)
    
    def test_unregister_tool(self):
        """Test tool unregistration."""
        manager = ToolsManager()
        tool = TestTool()
        
        manager.register_tool(tool)
        assert manager.has_tool("test_tool")
        
        manager.unregister_tool("test_tool")
        assert not manager.has_tool("test_tool")
    
    def test_unregister_nonexistent_tool_raises_error(self):
        """Test that unregistering nonexistent tool raises error."""
        manager = ToolsManager()
        
        with pytest.raises(ValueError, match="not found"):
            manager.unregister_tool("nonexistent")
    
    def test_get_nonexistent_tool_raises_error(self):
        """Test that getting nonexistent tool raises error."""
        manager = ToolsManager()
        
        with pytest.raises(ValueError, match="not found"):
            manager.get_tool("nonexistent")
    
    def test_list_tools(self):
        """Test listing tools."""
        manager = ToolsManager()
        tool1 = TestTool("tool1")
        tool2 = TestTool("tool2")
        
        manager.register_tool(tool1)
        manager.register_tool(tool2)
        
        schemas = manager.list_tools()
        assert len(schemas) == 2
        
        names = [schema.name for schema in schemas]
        assert "tool1" in names
        assert "tool2" in names
    
    def test_get_tool_names(self):
        """Test getting tool names."""
        manager = ToolsManager()
        tool1 = TestTool("tool1")
        tool2 = TestTool("tool2")
        
        manager.register_tool(tool1)
        manager.register_tool(tool2)
        
        names = manager.get_tool_names()
        assert set(names) == {"tool1", "tool2"}
    
    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """Test tool execution."""
        manager = ToolsManager()
        tool = TestTool()
        
        manager.register_tool(tool)
        
        result = await manager.execute_tool("test_tool", {"value": "hello"})
        
        assert isinstance(result, ToolResult)
        assert not result.is_error
        assert len(result.content) == 1
        assert result.content[0].text == "Test: hello"
    
    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool_raises_error(self):
        """Test that executing nonexistent tool raises error."""
        manager = ToolsManager()
        
        with pytest.raises(ValueError, match="not found"):
            await manager.execute_tool("nonexistent", {})


class TestEchoTool:
    """Test cases for EchoTool."""
    
    def test_echo_tool_schema(self):
        """Test echo tool schema."""
        tool = EchoTool()
        schema = tool.get_schema()
        
        assert schema.name == "echo"
        assert "echo back" in schema.description.lower()
        assert "message" in schema.input_schema["properties"]
        assert "message" in schema.input_schema["required"]
    
    @pytest.mark.asyncio
    async def test_echo_tool_execution(self):
        """Test echo tool execution."""
        tool = EchoTool()
        
        result = await tool.execute({"message": "Hello, World!"})
        
        assert isinstance(result, ToolResult)
        assert not result.is_error
        assert len(result.content) == 1
        assert result.content[0].text == "Echo: Hello, World!"
    
    @pytest.mark.asyncio
    async def test_echo_tool_missing_message_raises_error(self):
        """Test echo tool with missing message raises error."""
        tool = EchoTool()
        
        with pytest.raises(ValueError, match="Missing required argument"):
            await tool.execute({})
    
    @pytest.mark.asyncio
    async def test_echo_tool_extra_arguments_raises_error(self):
        """Test echo tool with extra arguments raises error."""
        tool = EchoTool()
        
        with pytest.raises(ValueError, match="Unexpected arguments"):
            await tool.execute({"message": "hello", "extra": "field"})


class TestWeatherTool:
    """Test cases for WeatherTool."""
    
    def test_weather_tool_schema(self):
        """Test weather tool schema."""
        tool = WeatherTool()
        schema = tool.get_schema()
        
        assert schema.name == "get_weather"
        assert "weather information" in schema.description.lower()
        assert "city" in schema.input_schema["properties"]
        assert "units" in schema.input_schema["properties"]
        assert "city" in schema.input_schema["required"]
        assert "units" not in schema.input_schema["required"]  # units is optional
    
    @pytest.mark.asyncio
    async def test_weather_tool_execution_valid_city(self):
        """Test weather tool execution with valid city."""
        tool = WeatherTool()
        
        result = await tool.execute({"city": "London"})
        
        assert isinstance(result, ToolResult)
        assert not result.is_error
        assert len(result.content) == 1
        assert "London" in result.content[0].text
        assert "Temperature:" in result.content[0].text
        assert "°C" in result.content[0].text  # Default metric units
    
    @pytest.mark.asyncio
    async def test_weather_tool_execution_with_units(self):
        """Test weather tool execution with different units."""
        tool = WeatherTool()
        
        # Test imperial units
        result = await tool.execute({"city": "London", "units": "imperial"})
        
        assert isinstance(result, ToolResult)
        assert not result.is_error
        assert "°F" in result.content[0].text
        
        # Test kelvin units
        result = await tool.execute({"city": "London", "units": "kelvin"})
        
        assert isinstance(result, ToolResult)
        assert not result.is_error
        assert "K" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_weather_tool_invalid_city(self):
        """Test weather tool with invalid city."""
        tool = WeatherTool()
        
        result = await tool.execute({"city": "InvalidCity"})
        
        assert isinstance(result, ToolResult)
        assert result.is_error
        assert "not available" in result.content[0].text.lower()
        assert "Available cities:" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_weather_tool_empty_city(self):
        """Test weather tool with empty city name."""
        tool = WeatherTool()
        
        result = await tool.execute({"city": ""})
        
        assert isinstance(result, ToolResult)
        assert result.is_error
        assert "cannot be empty" in result.content[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_weather_tool_missing_city_returns_error(self):
        """Test weather tool with missing city returns error result."""
        tool = WeatherTool()
        
        result = await tool.execute({})
        
        assert isinstance(result, ToolResult)
        assert result.is_error
        assert "missing required argument" in result.content[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_weather_tool_case_insensitive_city(self):
        """Test weather tool handles case insensitive city names."""
        tool = WeatherTool()
        
        # Test different cases
        result1 = await tool.execute({"city": "london"})
        result2 = await tool.execute({"city": "LONDON"})
        result3 = await tool.execute({"city": "London"})
        
        # All should succeed
        assert not result1.is_error
        assert not result2.is_error
        assert not result3.is_error
        
        # All should contain London in the response
        assert "London" in result1.content[0].text
        assert "London" in result2.content[0].text
        assert "London" in result3.content[0].text
    
    @pytest.mark.asyncio
    async def test_weather_tool_temperature_conversion(self):
        """Test weather tool temperature conversion."""
        tool = WeatherTool()
        
        # Get temperature in different units for the same city
        metric_result = await tool.execute({"city": "London", "units": "metric"})
        imperial_result = await tool.execute({"city": "London", "units": "imperial"})
        kelvin_result = await tool.execute({"city": "London", "units": "kelvin"})
        
        # All should succeed
        assert not metric_result.is_error
        assert not imperial_result.is_error
        assert not kelvin_result.is_error
        
        # Extract temperature values (this is a basic check)
        metric_text = metric_result.content[0].text
        imperial_text = imperial_result.content[0].text
        kelvin_text = kelvin_result.content[0].text
        
        # Check that different unit symbols are present
        assert "°C" in metric_text
        assert "°F" in imperial_text
        assert "K" in kelvin_text


class TestToolBase:
    """Test cases for Tool base class functionality."""
    
    def test_validate_arguments_success(self):
        """Test successful argument validation."""
        tool = TestTool()
        schema = {
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
            "additionalProperties": False
        }
        
        # Should not raise
        tool._validate_arguments({"value": "test"}, schema)
    
    def test_validate_arguments_missing_required(self):
        """Test validation with missing required field."""
        tool = TestTool()
        schema = {
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"]
        }
        
        with pytest.raises(ValueError, match="Missing required argument"):
            tool._validate_arguments({}, schema)
    
    def test_validate_arguments_unexpected_fields(self):
        """Test validation with unexpected fields."""
        tool = TestTool()
        schema = {
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "additionalProperties": False
        }
        
        with pytest.raises(ValueError, match="Unexpected arguments"):
            tool._validate_arguments({"value": "test", "extra": "field"}, schema)
    
    def test_create_text_result(self):
        """Test creating text result."""
        tool = TestTool()
        
        result = tool._create_text_result("test message")
        
        assert isinstance(result, ToolResult)
        assert not result.is_error
        assert len(result.content) == 1
        assert result.content[0].text == "test message"
    
    def test_create_error_result(self):
        """Test creating error result."""
        tool = TestTool()
        
        result = tool._create_error_result("error message")
        
        assert isinstance(result, ToolResult)
        assert result.is_error
        assert len(result.content) == 1
        assert result.content[0].text == "error message"