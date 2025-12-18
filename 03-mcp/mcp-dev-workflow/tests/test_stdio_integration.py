"""
Integration tests for stdio transport with MCP server.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, patch

from mcp_server.core.server import MCPServer
from mcp_server.transport.stdio import StdioTransport


class TestStdioIntegration:
    """Test stdio transport integration with MCP server."""
    
    @pytest.mark.asyncio
    async def test_stdio_server_integration(self):
        """Test complete stdio server integration."""
        transport = StdioTransport()
        server = MCPServer(transport, "test-server")
        
        # Mock stdin/stdout for testing
        with patch('sys.stdin'), patch('sys.stdout') as mock_stdout, \
             patch('asyncio.get_event_loop') as mock_loop:
            
            mock_loop.return_value.connect_read_pipe = AsyncMock()
            
            # Mock stdin reader to provide initialize request
            mock_reader = AsyncMock()
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocol_version": "2024-11-05",
                    "capabilities": {},
                    "client_info": {"name": "test-client", "version": "1.0"}
                },
                "id": 1
            }
            
            mock_reader.readline.side_effect = [
                json.dumps(init_request).encode('utf-8') + b'\n',
                b''  # EOF to stop the loop
            ]
            transport._stdin_reader = mock_reader
            
            # Start server
            await server.start()
            
            # Process one message manually (since we're not running the full loop)
            request = await transport.receive_message()
            assert request is not None
            assert request.method == "initialize"
            
            response = await server.handle_request(request)
            assert response is not None
            assert response.error is None
            
            await transport.send_message(response)
            
            # Verify response was written to stdout
            mock_stdout.write.assert_called()
            written_data = mock_stdout.write.call_args[0][0]
            
            # Parse the response
            json_data = written_data.rstrip('\n')
            parsed_response = json.loads(json_data)
            
            assert parsed_response['jsonrpc'] == '2.0'
            assert parsed_response['id'] == 1
            assert 'result' in parsed_response
            assert 'protocol_version' in parsed_response['result']
            assert 'capabilities' in parsed_response['result']
            assert 'server_info' in parsed_response['result']
            
            # Clean up
            await server.stop()
    
    @pytest.mark.asyncio
    async def test_stdio_error_handling_integration(self):
        """Test error handling in stdio integration."""
        transport = StdioTransport()
        server = MCPServer(transport, "test-server")
        
        with patch('sys.stdin'), patch('sys.stdout') as mock_stdout, \
             patch('asyncio.get_event_loop') as mock_loop:
            
            mock_loop.return_value.connect_read_pipe = AsyncMock()
            
            # Mock stdin reader to provide malformed request
            mock_reader = AsyncMock()
            mock_reader.readline.return_value = b'invalid json\n'
            transport._stdin_reader = mock_reader
            
            await server.start()
            
            # Process malformed message
            request = await transport.receive_message()
            assert request is None  # Should return None for malformed input
            
            # Verify error response was sent
            mock_stdout.write.assert_called()
            written_data = mock_stdout.write.call_args[0][0]
            
            json_data = written_data.rstrip('\n')
            parsed_response = json.loads(json_data)
            
            assert parsed_response['jsonrpc'] == '2.0'
            assert 'error' in parsed_response
            assert parsed_response['error']['code'] == -32700  # Parse error
            
            await server.stop()