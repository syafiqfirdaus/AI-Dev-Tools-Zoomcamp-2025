"""
Abstract transport interface for MCP communication.
"""

from abc import ABC, abstractmethod
from typing import Optional

from mcp_server.core.protocol import JSONRPCRequest, JSONRPCResponse


class Transport(ABC):
    """Abstract base class for MCP transport mechanisms."""

    @abstractmethod
    async def start(self) -> None:
        """Start the transport layer."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the transport layer and clean up resources."""
        pass

    @abstractmethod
    async def send_message(self, message: JSONRPCResponse) -> None:
        """
        Send a JSON-RPC response message.
        
        Args:
            message: The JSON-RPC response to send
        """
        pass

    @abstractmethod
    async def receive_message(self) -> Optional[JSONRPCRequest]:
        """
        Receive a JSON-RPC request message.
        
        Returns:
            The received JSON-RPC request, or None if no message available
        """
        pass
