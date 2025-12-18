"""
Example echo tool for testing the tools management system.
"""

from typing import Any, Dict

from mcp_server.core.protocol import ToolResult, ToolSchema
from mcp_server.tools.base import Tool


class EchoTool(Tool):
    """Simple echo tool that returns the input message."""
    
    def __init__(self):
        """Initialize echo tool."""
        super().__init__(
            name="echo",
            description="Echo back the provided message"
        )
    
    def get_schema(self) -> ToolSchema:
        """Get the tool's schema definition."""
        return ToolSchema(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back"
                    }
                },
                "required": ["message"],
                "additionalProperties": False
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute the echo tool."""
        # Validate arguments
        schema = self.get_schema().input_schema
        self._validate_arguments(arguments, schema)
        
        # Get message
        message = arguments["message"]
        
        # Return echoed message
        return self._create_text_result(f"Echo: {message}")