#!/usr/bin/env python3
"""
Multi-Server Coordination Example

This example demonstrates coordinating requests across multiple MCP servers,
including load balancing, failover, and request aggregation patterns.

Demonstrates:
1. Running multiple MCP servers simultaneously
2. Load balancing requests across servers
3. Failover mechanisms when servers are unavailable
4. Aggregating results from multiple sources
5. Performance monitoring and metrics

Requirements: 8.5
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from mcp_server.core.server import MCPServer
from mcp_server.transport.stdio import StdioTransport
from mcp_server.transport.http import HTTPTransport
from mcp_server.tools import (
    EchoTool,
    WeatherTool,
    Context7Client,
    Context7SearchTool,
    Context7DocumentationTool,
    Context7ExamplesTool,
)


class ServerMetrics:
    """Track performance metrics for MCP servers."""
    
    def __init__(self, server_name: str):
        self.server_name = server_name
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.last_request_time = None
        self.status = "active"
    
    def record_request(self, success: bool, response_time: float):
        """Record a request and its outcome."""
        self.request_count += 1
        self.total_response_time += response_time
        self.last_request_time = datetime.now()
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def mark_unavailable(self):
        """Mark server as unavailable."""
        self.status = "unavailable"
    
    def mark_available(self):
        """Mark server as available."""
        self.status = "active"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.request_count == 0:
            return 0.0
        return (self.success_count / self.request_count) * 100
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time."""
        if self.request_count == 0:
            return 0.0
        return self.total_response_time / self.request_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "server_name": self.server_name,
            "request_count": self.request_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": round(self.success_rate, 2),
            "average_response_time": round(self.average_response_time, 3),
            "status": self.status,
            "last_request_time": self.last_request_time.isoformat() if self.last_request_time else None
        }


class MultiServerCoordinator:
    """
    Coordinates requests across multiple MCP servers.
    
    Provides:
    - Load balancing with round-robin and weighted strategies
    - Automatic failover to healthy servers
    - Request aggregation and result merging
    - Performance monitoring and metrics
    - Health checking and server status tracking
    """
    
    def __init__(self):
        self.logger = logging.getLogger("multi-server")
        self.servers: Dict[str, MCPServer] = {}
        self.metrics: Dict[str, ServerMetrics] = {}
        self.current_server_index = 0
        self.context7_client: Optional[Context7Client] = None
    
    async def setup_servers(self) -> None:
        """Set up multiple MCP servers for coordination testing."""
        self.logger.info("🔧 Setting up multiple MCP servers")
        
        # Server 1: stdio server (primary)
        stdio_transport = StdioTransport()
        stdio_server = MCPServer(stdio_transport, "coordinator-stdio")
        stdio_server.register_tool(EchoTool())
        stdio_server.register_tool(WeatherTool())
        
        # Server 2: HTTP server on port 8001 (secondary)
        try:
            http_transport = HTTPTransport(host="127.0.0.1", port=8001)
            http_server = MCPServer(http_transport, "coordinator-http-8001")
            http_server.register_tool(EchoTool())
            http_server.register_tool(WeatherTool())
            
            self.servers["http-8001"] = http_server
            self.metrics["http-8001"] = ServerMetrics("http-8001")
            self.logger.info("✅ HTTP server configured on port 8001")
        except Exception as e:
            self.logger.warning(f"⚠️  HTTP server 8001 setup failed: {e}")
        
        # Server 3: HTTP server on port 8002 (tertiary)
        try:
            http_transport2 = HTTPTransport(host="127.0.0.1", port=8002)
            http_server2 = MCPServer(http_transport2, "coordinator-http-8002")
            http_server2.register_tool(EchoTool())
            http_server2.register_tool(WeatherTool())
            
            self.servers["http-8002"] = http_server2
            self.metrics["http-8002"] = ServerMetrics("http-8002")
            self.logger.info("✅ HTTP server configured on port 8002")
        except Exception as e:
            self.logger.warning(f"⚠️  HTTP server 8002 setup failed: {e}")
        
        # Add stdio server last (it's always available)
        self.servers["stdio"] = stdio_server
        self.metrics["stdio"] = ServerMetrics("stdio")
        
        # Setup Context7 tools on all servers if API key available
        context7_api_key = os.getenv("CONTEXT7_API_KEY")
        if context7_api_key:
            try:
                self.context7_client = Context7Client(context7_api_key)
                
                for server in self.servers.values():
                    server.register_tool(Context7SearchTool(self.context7_client))
                    server.register_tool(Context7DocumentationTool(self.context7_client))
                    server.register_tool(Context7ExamplesTool(self.context7_client))
                
                self.logger.info("✅ Context7 tools registered on all servers")
            except Exception as e:
                self.logger.warning(f"⚠️  Context7 setup failed: {e}")
        
        self.logger.info(f"🚀 Multi-server setup complete: {len(self.servers)} servers available")
    
    async def execute_with_timing(self, server: MCPServer, tool_name: str, arguments: Dict[str, Any]) -> Tuple[Any, float, bool]:
        """
        Execute a tool with timing measurement.
        
        Args:
            server: MCP server to use
            tool_name: Name of tool to execute
            arguments: Tool arguments
            
        Returns:
            Tuple of (result, response_time, success)
        """
        start_time = time.time()
        success = False
        result = None
        
        try:
            result = await server.tools_manager.execute_tool(tool_name, arguments)
            success = not result.is_error
        except Exception as e:
            result = {"error": str(e)}
            success = False
        
        response_time = time.time() - start_time
        return result, response_time, success
    
    async def round_robin_request(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute request using round-robin load balancing.
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments
            
        Returns:
            Dictionary containing request result and metadata
        """
        available_servers = [(name, server) for name, server in self.servers.items() 
                           if self.metrics[name].status == "active"]
        
        if not available_servers:
            return {
                "success": False,
                "error": "No available servers",
                "strategy": "round_robin"
            }
        
        # Select server using round-robin
        server_name, server = available_servers[self.current_server_index % len(available_servers)]
        self.current_server_index += 1
        
        # Execute request
        result, response_time, success = await self.execute_with_timing(server, tool_name, arguments)
        
        # Record metrics
        self.metrics[server_name].record_request(success, response_time)
        
        return {
            "success": success,
            "result": result,
            "server_used": server_name,
            "response_time": response_time,
            "strategy": "round_robin"
        }
    
    async def weighted_request(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute request using weighted load balancing based on performance.
        
        Servers with better performance (higher success rate, lower response time)
        get higher weight and more requests.
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments
            
        Returns:
            Dictionary containing request result and metadata
        """
        available_servers = [(name, server) for name, server in self.servers.items() 
                           if self.metrics[name].status == "active"]
        
        if not available_servers:
            return {
                "success": False,
                "error": "No available servers",
                "strategy": "weighted"
            }
        
        # Calculate weights based on performance
        weights = []
        for server_name, _ in available_servers:
            metrics = self.metrics[server_name]
            
            # Weight based on success rate and inverse of response time
            success_weight = metrics.success_rate / 100.0 if metrics.request_count > 0 else 1.0
            time_weight = 1.0 / (metrics.average_response_time + 0.1) if metrics.request_count > 0 else 1.0
            
            # Combine weights (favor success rate more than response time)
            combined_weight = (success_weight * 0.7) + (time_weight * 0.3)
            weights.append(combined_weight)
        
        # Select server based on weights
        total_weight = sum(weights)
        if total_weight == 0:
            # Fallback to round-robin if no weights
            selected_index = self.current_server_index % len(available_servers)
        else:
            # Weighted random selection
            import random
            rand_val = random.uniform(0, total_weight)
            cumulative_weight = 0
            selected_index = 0
            
            for i, weight in enumerate(weights):
                cumulative_weight += weight
                if rand_val <= cumulative_weight:
                    selected_index = i
                    break
        
        server_name, server = available_servers[selected_index]
        
        # Execute request
        result, response_time, success = await self.execute_with_timing(server, tool_name, arguments)
        
        # Record metrics
        self.metrics[server_name].record_request(success, response_time)
        
        return {
            "success": success,
            "result": result,
            "server_used": server_name,
            "response_time": response_time,
            "strategy": "weighted",
            "server_weight": weights[selected_index] if selected_index < len(weights) else 0
        }
    
    async def failover_request(self, tool_name: str, arguments: Dict[str, Any], max_attempts: int = 3) -> Dict[str, Any]:
        """
        Execute request with automatic failover to backup servers.
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments
            max_attempts: Maximum number of servers to try
            
        Returns:
            Dictionary containing request result and metadata
        """
        available_servers = [(name, server) for name, server in self.servers.items() 
                           if self.metrics[name].status == "active"]
        
        if not available_servers:
            return {
                "success": False,
                "error": "No available servers",
                "strategy": "failover"
            }
        
        attempts = []
        
        for attempt in range(min(max_attempts, len(available_servers))):
            server_name, server = available_servers[attempt]
            
            # Execute request
            result, response_time, success = await self.execute_with_timing(server, tool_name, arguments)
            
            # Record attempt
            attempts.append({
                "server": server_name,
                "success": success,
                "response_time": response_time,
                "attempt": attempt + 1
            })
            
            # Record metrics
            self.metrics[server_name].record_request(success, response_time)
            
            if success:
                return {
                    "success": True,
                    "result": result,
                    "server_used": server_name,
                    "response_time": response_time,
                    "strategy": "failover",
                    "attempts": attempts
                }
            else:
                self.logger.warning(f"⚠️  Server {server_name} failed, trying next server")
        
        return {
            "success": False,
            "error": "All servers failed",
            "strategy": "failover",
            "attempts": attempts
        }
    
    async def aggregate_request(self, tool_name: str, arguments_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute multiple requests and aggregate results.
        
        Useful for gathering data from multiple sources or processing
        multiple inputs simultaneously.
        
        Args:
            tool_name: Name of tool to execute
            arguments_list: List of argument dictionaries for each request
            
        Returns:
            Dictionary containing aggregated results
        """
        self.logger.info(f"🔄 Aggregating {len(arguments_list)} requests across servers")
        
        available_servers = [(name, server) for name, server in self.servers.items() 
                           if self.metrics[name].status == "active"]
        
        if not available_servers:
            return {
                "success": False,
                "error": "No available servers",
                "strategy": "aggregate"
            }
        
        # Distribute requests across available servers
        tasks = []
        server_assignments = []
        
        for i, arguments in enumerate(arguments_list):
            # Round-robin server assignment
            server_name, server = available_servers[i % len(available_servers)]
            server_assignments.append(server_name)
            
            # Create async task
            task = self.execute_with_timing(server, tool_name, arguments)
            tasks.append(task)
        
        # Execute all requests concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Process results
        aggregated_results = []
        successful_requests = 0
        
        for i, (result, response_time, success) in enumerate(results):
            if isinstance(result, Exception):
                # Handle exceptions
                aggregated_results.append({
                    "request_index": i,
                    "server": server_assignments[i],
                    "success": False,
                    "error": str(result),
                    "arguments": arguments_list[i]
                })
            else:
                aggregated_results.append({
                    "request_index": i,
                    "server": server_assignments[i],
                    "success": success,
                    "result": result,
                    "response_time": response_time,
                    "arguments": arguments_list[i]
                })
                
                if success:
                    successful_requests += 1
            
            # Record metrics
            server_name = server_assignments[i]
            if not isinstance(result, Exception):
                self.metrics[server_name].record_request(success, response_time)
        
        return {
            "success": successful_requests > 0,
            "total_requests": len(arguments_list),
            "successful_requests": successful_requests,
            "failed_requests": len(arguments_list) - successful_requests,
            "total_time": total_time,
            "strategy": "aggregate",
            "results": aggregated_results,
            "server_distribution": {server: server_assignments.count(server) 
                                  for server in set(server_assignments)}
        }
    
    async def health_check_servers(self) -> Dict[str, Any]:
        """
        Perform health checks on all servers.
        
        Returns:
            Dictionary containing health status of all servers
        """
        self.logger.info("🏥 Performing health checks on all servers")
        
        health_results = {}
        
        for server_name, server in self.servers.items():
            try:
                # Use echo tool for health check
                result, response_time, success = await self.execute_with_timing(
                    server, "echo", {"message": f"health_check_{server_name}"}
                )
                
                if success:
                    self.metrics[server_name].mark_available()
                    health_results[server_name] = {
                        "status": "healthy",
                        "response_time": response_time,
                        "last_check": datetime.now().isoformat()
                    }
                else:
                    self.metrics[server_name].mark_unavailable()
                    health_results[server_name] = {
                        "status": "unhealthy",
                        "error": "Tool execution failed",
                        "last_check": datetime.now().isoformat()
                    }
                
            except Exception as e:
                self.metrics[server_name].mark_unavailable()
                health_results[server_name] = {
                    "status": "unavailable",
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                }
        
        healthy_count = len([r for r in health_results.values() if r["status"] == "healthy"])
        
        return {
            "total_servers": len(self.servers),
            "healthy_servers": healthy_count,
            "unhealthy_servers": len(self.servers) - healthy_count,
            "server_status": health_results
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics for all servers.
        
        Returns:
            Dictionary containing performance metrics
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "server_metrics": {name: metrics.to_dict() for name, metrics in self.metrics.items()},
            "summary": {
                "total_servers": len(self.servers),
                "active_servers": len([m for m in self.metrics.values() if m.status == "active"]),
                "total_requests": sum(m.request_count for m in self.metrics.values()),
                "total_successes": sum(m.success_count for m in self.metrics.values()),
                "overall_success_rate": (
                    sum(m.success_count for m in self.metrics.values()) / 
                    max(sum(m.request_count for m in self.metrics.values()), 1)
                ) * 100
            }
        }
    
    async def run_coordination_demo(self) -> Dict[str, Any]:
        """
        Run a comprehensive multi-server coordination demonstration.
        
        Returns:
            Dictionary containing all demonstration results
        """
        self.logger.info("🚀 Starting multi-server coordination demonstration")
        
        demo_results = {
            "start_time": datetime.now().isoformat(),
            "scenarios": {},
            "performance_metrics": {},
            "health_checks": {}
        }
        
        # Scenario 1: Round-robin load balancing
        self.logger.info("📋 Scenario 1: Round-robin load balancing")
        
        round_robin_results = []
        for i in range(10):  # 10 requests
            result = await self.round_robin_request("echo", {"message": f"round_robin_test_{i}"})
            round_robin_results.append(result)
            await asyncio.sleep(0.1)  # Brief delay between requests
        
        demo_results["scenarios"]["round_robin"] = {
            "total_requests": len(round_robin_results),
            "successful_requests": len([r for r in round_robin_results if r["success"]]),
            "server_distribution": {},
            "results": round_robin_results
        }
        
        # Calculate server distribution
        for result in round_robin_results:
            if result["success"]:
                server = result["server_used"]
                demo_results["scenarios"]["round_robin"]["server_distribution"][server] = \
                    demo_results["scenarios"]["round_robin"]["server_distribution"].get(server, 0) + 1
        
        # Scenario 2: Weighted load balancing
        self.logger.info("📋 Scenario 2: Weighted load balancing")
        
        weighted_results = []
        for i in range(10):  # 10 requests
            result = await self.weighted_request("echo", {"message": f"weighted_test_{i}"})
            weighted_results.append(result)
            await asyncio.sleep(0.1)
        
        demo_results["scenarios"]["weighted"] = {
            "total_requests": len(weighted_results),
            "successful_requests": len([r for r in weighted_results if r["success"]]),
            "server_distribution": {},
            "results": weighted_results
        }
        
        # Calculate server distribution for weighted
        for result in weighted_results:
            if result["success"]:
                server = result["server_used"]
                demo_results["scenarios"]["weighted"]["server_distribution"][server] = \
                    demo_results["scenarios"]["weighted"]["server_distribution"].get(server, 0) + 1
        
        # Scenario 3: Failover testing
        self.logger.info("📋 Scenario 3: Failover testing")
        
        # Simulate server failure by marking one as unavailable
        if len(self.servers) > 1:
            first_server = list(self.servers.keys())[0]
            self.metrics[first_server].mark_unavailable()
            self.logger.info(f"🔴 Simulating failure of server: {first_server}")
        
        failover_results = []
        for i in range(5):  # 5 requests with failover
            result = await self.failover_request("echo", {"message": f"failover_test_{i}"})
            failover_results.append(result)
            await asyncio.sleep(0.1)
        
        # Restore server
        if len(self.servers) > 1:
            self.metrics[first_server].mark_available()
            self.logger.info(f"🟢 Restored server: {first_server}")
        
        demo_results["scenarios"]["failover"] = {
            "total_requests": len(failover_results),
            "successful_requests": len([r for r in failover_results if r["success"]]),
            "results": failover_results
        }
        
        # Scenario 4: Request aggregation
        self.logger.info("📋 Scenario 4: Request aggregation")
        
        # Prepare multiple weather requests
        weather_cities = ["London", "New York", "Tokyo", "Paris", "Sydney"]
        weather_arguments = [{"city": city} for city in weather_cities]
        
        aggregation_result = await self.aggregate_request("get_weather", weather_arguments)
        demo_results["scenarios"]["aggregation"] = aggregation_result
        
        # Health checks
        self.logger.info("📋 Performing final health checks")
        health_check_result = await self.health_check_servers()
        demo_results["health_checks"] = health_check_result
        
        # Performance metrics
        demo_results["performance_metrics"] = self.get_performance_metrics()
        
        demo_results["end_time"] = datetime.now().isoformat()
        
        self.logger.info("✅ Multi-server coordination demonstration completed")
        return demo_results


async def main():
    """Main entry point for the multi-server coordination example."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    
    logger = logging.getLogger("main")
    
    print("🚀 Multi-Server Coordination Example")
    print("=" * 50)
    print("This example demonstrates coordinating requests across multiple MCP servers")
    print("including load balancing, failover, and request aggregation.")
    print()
    
    try:
        # Create coordinator and run demo
        coordinator = MultiServerCoordinator()
        await coordinator.setup_servers()
        
        results = await coordinator.run_coordination_demo()
        
        # Save results
        output_dir = Path("workflow_results")
        output_dir.mkdir(exist_ok=True)
        
        results_file = output_dir / f"multi_server_coordination_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*50)
        print("COORDINATION SUMMARY")
        print("="*50)
        
        metrics = results["performance_metrics"]["summary"]
        print(f"🖥️  Total servers: {metrics['total_servers']}")
        print(f"✅ Active servers: {metrics['active_servers']}")
        print(f"📊 Total requests: {metrics['total_requests']}")
        print(f"🎯 Success rate: {metrics['overall_success_rate']:.1f}%")
        
        print("\n📋 SCENARIO RESULTS:")
        for scenario_name, scenario_data in results["scenarios"].items():
            if "total_requests" in scenario_data:
                success_rate = (scenario_data["successful_requests"] / scenario_data["total_requests"]) * 100
                print(f"• {scenario_name.title()}: {scenario_data['successful_requests']}/{scenario_data['total_requests']} ({success_rate:.1f}%)")
        
        print(f"\n📊 Results saved to: {results_file}")
        print("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if hasattr(coordinator, 'context7_client') and coordinator.context7_client:
            await coordinator.context7_client.close()


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Example interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)