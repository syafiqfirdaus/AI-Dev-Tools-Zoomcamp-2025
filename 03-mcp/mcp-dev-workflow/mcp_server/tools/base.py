"""
Base classes for MCP tools and tool management.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from mcp_server.core.protocol import Content, ToolResult, ToolSchema


class Tool(ABC):
    """Base class for MCP tools."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize tool.
        
        Args:
            name: Tool name
            description: Tool description
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def get_schema(self) -> ToolSchema:
        """
        Get the tool's schema definition.
        
        Returns:
            ToolSchema defining the tool's interface
        """
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with given arguments.
        
        Args:
            arguments: Tool execution parameters
            
        Returns:
            ToolResult containing execution results
        """
        pass
    
    def _validate_arguments(self, arguments: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """
        Validate arguments against the tool's input schema.
        
        Args:
            arguments: Arguments to validate
            schema: JSON schema to validate against
            
        Raises:
            ValueError: If arguments don't match schema
        """
        # Basic validation - check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in arguments:
                raise ValueError(f"Missing required argument: {field}")
        
        # Check for unexpected fields if additionalProperties is False
        if not schema.get("additionalProperties", True):
            allowed_fields = set(schema.get("properties", {}).keys())
            provided_fields = set(arguments.keys())
            unexpected = provided_fields - allowed_fields
            if unexpected:
                raise ValueError(f"Unexpected arguments: {', '.join(unexpected)}")
    
    def _create_text_result(self, text: str, is_error: bool = False) -> ToolResult:
        """
        Create a simple text result.
        
        Args:
            text: Text content
            is_error: Whether this is an error result
            
        Returns:
            ToolResult with text content
        """
        return ToolResult(
            content=[Content(type="text", text=text)],
            is_error=is_error
        )
    
    def _create_error_result(self, error_message: str) -> ToolResult:
        """
        Create an error result.
        
        Args:
            error_message: Error message
            
        Returns:
            ToolResult with error content
        """
        return self._create_text_result(error_message, is_error=True)


class ToolsManager:
    """Manager for MCP tool registration and execution."""
    
    def __init__(self):
        """Initialize tools manager."""
        self.tools: Dict[str, Tool] = {}
    
    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool with the manager.
        
        Args:
            tool: Tool instance to register
            
        Raises:
            ValueError: If tool name already exists
        """
        if tool.name in self.tools:
            raise ValueError(f"Tool with name '{tool.name}' already registered")
        
        self.tools[tool.name] = tool
    
    def unregister_tool(self, name: str) -> None:
        """
        Unregister a tool by name.
        
        Args:
            name: Name of tool to unregister
            
        Raises:
            ValueError: If tool doesn't exist
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        
        del self.tools[name]
    
    def get_tool(self, name: str) -> Tool:
        """
        Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance
            
        Raises:
            ValueError: If tool doesn't exist
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        
        return self.tools[name]
    
    def list_tools(self) -> List[ToolSchema]:
        """
        List all registered tools.
        
        Returns:
            List of tool schemas
        """
        return [tool.get_schema() for tool in self.tools.values()]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """
        Execute a tool by name.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            ToolResult from tool execution
            
        Raises:
            ValueError: If tool doesn't exist
        """
        tool = self.get_tool(name)
        return await tool.execute(arguments)
    
    def has_tool(self, name: str) -> bool:
        """
        Check if a tool is registered.
        
        Args:
            name: Tool name
            
        Returns:
            True if tool exists, False otherwise
        """
        return name in self.tools
    
    def get_tool_names(self) -> List[str]:
        """
        Get list of all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())