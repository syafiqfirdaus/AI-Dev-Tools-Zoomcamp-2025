"""
Tests for stdio transport implementation.
"""

import asyncio
import json
import pytest
from io import StringIO
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_server.core.protocol import (
    JSONRPCError,
    JSONRPCErrorCodes,
    JSONRPCRequest,
    JSONRPCResponse,
)
from mcp_server.transport.stdio import StdioTransport


class TestStdioTransport:
    """Test stdio transport functionality."""
    
    @pytest.fixture
    def transport(self):
        return StdioTransport()
    
    @pytest.mark.asyncio
    async def test_transport_lifecycle(self, transport):
        """Test transport start and stop."""
        assert not transport._running
        
        with patch('sys.stdin'), patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.connect_read_pipe = AsyncMock()
            
            await transport.start()
            assert transport._running
            
            await transport.stop()
            assert not transport._running
    
    @pytest.mark.asyncio
    async def test_send_message(self, transport):
        """Test sending JSON-RPC response messages."""
        transport._running = True
        
        response = JSONRPCResponse.success({"result": "test"}, "test-id")
        
        with patch('sys.stdout') as mock_stdout:
            await transport.send_message(response)
            
            # Verify stdout.write was called with correct JSON
            mock_stdout.write.assert_called_once()
            written_data = mock_stdout.write.call_args[0][0]
            
            # Should be JSON + newline
            assert written_data.endswith('\n')
            json_data = written_data.rstrip('\n')
            parsed = json.loads(json_data)
            
            assert parsed['jsonrpc'] == '2.0'
            assert parsed['id'] == 'test-id'
            assert parsed['result'] == {'result': 'test'}
            
            mock_stdout.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_message_not_running(self, transport):
        """Test sending message when transport not running."""
        response = JSONRPCResponse.success({"result": "test"}, "test-id")
        
        with pytest.raises(RuntimeError, match="Transport not started"):
            await transport.send_message(response)
    
    @pytest.mark.asyncio
    async def test_receive_valid_message(self, transport):
        """Test receiving valid JSON-RPC request."""
        transport._running = True
        
        # Mock stdin reader
        mock_reader = AsyncMock()
        request_json = '{"jsonrpc": "2.0", "method": "test", "id": 1}\n'
        mock_reader.readline.return_value = request_json.encode('utf-8')
        transport._stdin_reader = mock_reader
        
        request = await transport.receive_message()
        
        assert request is not None
        assert request.method == "test"
        assert request.id == 1
        assert request.jsonrpc == "2.0"
    
    @pytest.mark.asyncio
    async def test_receive_empty_line(self, transport):
        """Test receiving empty line."""
        transport._running = True
        
        mock_reader = AsyncMock()
        mock_reader.readline.return_value = b'\n'
        transport._stdin_reader = mock_reader
        
        request = await transport.receive_message()
        assert request is None
    
    @pytest.mark.asyncio
    async def test_receive_eof(self, transport):
        """Test receiving EOF."""
        transport._running = True
        
        mock_reader = AsyncMock()
        mock_reader.readline.return_value = b''  # EOF
        transport._stdin_reader = mock_reader
        
        request = await transport.receive_message()
        assert request is None
    
    @pytest.mark.asyncio
    async def test_receive_malformed_json(self, transport):
        """Test receiving malformed JSON."""
        transport._running = True
        
        mock_reader = AsyncMock()
        mock_reader.readline.return_value = b'invalid json\n'
        transport._stdin_reader = mock_reader
        
        with patch.object(transport, 'send_message') as mock_send:
            request = await transport.receive_message()
            
            # Should return None for malformed input
            assert request is None
            
            # Should send error response
            mock_send.assert_called_once()
            error_response = mock_send.call_args[0][0]
            assert isinstance(error_response, JSONRPCResponse)
            assert error_response.error is not None
            assert error_response.error.code == JSONRPCErrorCodes.PARSE_ERROR
    
    @pytest.mark.asyncio
    async def test_receive_malformed_json_with_id(self, transport):
        """Test receiving malformed JSON that contains an ID."""
        transport._running = True
        
        mock_reader = AsyncMock()
        # JSON with syntax error but extractable ID
        mock_reader.readline.return_value = b'{"id": "test", "method": "test", invalid}\n'
        transport._stdin_reader = mock_reader
        
        with patch.object(transport, 'send_message') as mock_send:
            request = await transport.receive_message()
            
            assert request is None
            
            # Should send error response with extracted ID
            mock_send.assert_called_once()
            error_response = mock_send.call_args[0][0]
            assert error_response.id == "test"
    
    @pytest.mark.asyncio
    async def test_receive_not_running(self, transport):
        """Test receiving when transport not running."""
        request = await transport.receive_message()
        assert request is None
    
    @pytest.mark.asyncio
    async def test_receive_cancelled(self, transport):
        """Test receiving when task is cancelled."""
        transport._running = True
        
        mock_reader = AsyncMock()
        mock_reader.readline.side_effect = asyncio.CancelledError()
        transport._stdin_reader = mock_reader
        
        request = await transport.receive_message()
        assert request is None