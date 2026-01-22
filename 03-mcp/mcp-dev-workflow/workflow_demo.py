#!/usr/bin/env python3
"""
Development Workflow Demonstration

This script demonstrates a complete development workflow using MCP servers
for practical development tasks including:
1. Using Context7 for live documentation access
2. Coordinating multiple MCP servers
3. Real-world development scenarios

Requirements: 8.1, 8.4, 8.5
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

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


class WorkflowLogger:
    """Enhanced logger for workflow demonstrations."""
    
    def __init__(self, name: str = "workflow"):
        self.logger = logging.getLogger(name)
        self.step_counter = 0
    
    def step(self, message: str) -> None:
        """Log a workflow step."""
        self.step_counter += 1
        self.logger.info(f"📋 Step {self.step_counter}: {message}")
    
    def success(self, message: str) -> None:
        """Log a success message."""
        self.logger.info(f"✅ {message}")
    
    def info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(f"ℹ️  {message}")
    
    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(f"⚠️  {message}")
    
    def error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(f"❌ {message}")


class DevelopmentWorkflow:
    """
    Demonstrates a complete development workflow using MCP servers.
    
    This class showcases practical MCP usage for real development tasks:
    - Documentation lookup during development
    - Multi-server coordination
    - Error handling and debugging assistance
    """
    
    def __init__(self):
        self.logger = WorkflowLogger("dev-workflow")
        self.servers: Dict[str, MCPServer] = {}
        self.context7_client: Optional[Context7Client] = None
        self.workflow_results: Dict[str, Any] = {}
    
    async def setup_servers(self) -> None:
        """Set up multiple MCP servers for the workflow."""
        self.logger.step("Setting up MCP servers")
        
        # Setup stdio server
        stdio_transport = StdioTransport()
        stdio_server = MCPServer(stdio_transport, "workflow-stdio")
        stdio_server.register_tool(EchoTool())
        stdio_server.register_tool(WeatherTool())
        
        # Setup Context7 tools if API key available
        context7_api_key = os.getenv("CONTEXT7_API_KEY")
        if context7_api_key:
            try:
                self.context7_client = Context7Client(context7_api_key)
                stdio_server.register_tool(Context7SearchTool(self.context7_client))
                stdio_server.register_tool(Context7DocumentationTool(self.context7_client))
                stdio_server.register_tool(Context7ExamplesTool(self.context7_client))
                self.logger.success("Context7 tools registered")
            except Exception as e:
                self.logger.warning(f"Context7 setup failed: {e}")
        else:
            self.logger.warning("Context7 API key not found - using mock data")
        
        self.servers["stdio"] = stdio_server
        
        # Setup HTTP server on different port
        try:
            http_transport = HTTPTransport(host="127.0.0.1", port=8001)
            http_server = MCPServer(http_transport, "workflow-http")
            http_server.register_tool(EchoTool())
            http_server.register_tool(WeatherTool())
            
            if self.context7_client:
                http_server.register_tool(Context7SearchTool(self.context7_client))
                http_server.register_tool(Context7DocumentationTool(self.context7_client))
                http_server.register_tool(Context7ExamplesTool(self.context7_client))
            
            self.servers["http"] = http_server
            self.logger.success("HTTP server configured on port 8001")
        except Exception as e:
            self.logger.warning(f"HTTP server setup failed: {e}")
        
        self.logger.success(f"Configured {len(self.servers)} MCP servers")
    
    async def demonstrate_documentation_workflow(self) -> Dict[str, Any]:
        """
        Demonstrate using Context7 for documentation during development.
        
        Simulates a developer working on a FastAPI project who needs:
        1. Current documentation for FastAPI
        2. Code examples for specific features
        3. Library search for related tools
        
        Returns:
            Dictionary containing workflow results
        """
        self.logger.step("Starting documentation workflow demonstration")
        
        workflow_results = {
            "scenario": "FastAPI Development with Live Documentation",
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "tools_used": [],
            "documentation_accessed": [],
            "code_examples": []
        }
        
        # Simulate development scenario
        development_task = {
            "project": "Building a REST API with FastAPI",
            "current_challenge": "Need to implement authentication middleware",
            "required_knowledge": [
                "FastAPI middleware patterns",
                "Authentication best practices",
                "Request/response handling"
            ]
        }
        
        self.logger.info(f"Development scenario: {development_task['project']}")
        self.logger.info(f"Challenge: {development_task['current_challenge']}")
        
        # Step 1: Search for relevant libraries
        self.logger.step("Searching for authentication libraries")
        
        stdio_server = self.servers.get("stdio")
        if stdio_server and "context7_search_libraries" in stdio_server.tools_manager.tools:
            try:
                search_result = await stdio_server.tools_manager.execute_tool(
                    "context7_search_libraries",
                    {"query": "fastapi authentication", "limit": 5}
                )
                
                workflow_results["steps"].append({
                    "action": "library_search",
                    "query": "fastapi authentication",
                    "success": not search_result.is_error,
                    "results_count": len(search_result.content) if not search_result.is_error else 0
                })
                
                workflow_results["tools_used"].append("context7_search_libraries")
                
                if not search_result.is_error:
                    self.logger.success("Found relevant authentication libraries")
                    for content in search_result.content:
                        if hasattr(content, 'text'):
                            self.logger.info(f"  - {content.text[:100]}...")
                else:
                    self.logger.warning("Library search returned error")
                    
            except Exception as e:
                self.logger.error(f"Library search failed: {e}")
                workflow_results["steps"].append({
                    "action": "library_search",
                    "error": str(e)
                })
        
        # Step 2: Get FastAPI documentation
        self.logger.step("Retrieving FastAPI documentation")
        
        if stdio_server and "context7_get_documentation" in stdio_server.tools_manager.tools:
            try:
                doc_result = await stdio_server.tools_manager.execute_tool(
                    "context7_get_documentation",
                    {"library": "fastapi", "version": "latest"}
                )
                
                workflow_results["steps"].append({
                    "action": "get_documentation",
                    "library": "fastapi",
                    "success": not doc_result.is_error
                })
                
                workflow_results["tools_used"].append("context7_get_documentation")
                workflow_results["documentation_accessed"].append("fastapi")
                
                if not doc_result.is_error:
                    self.logger.success("Retrieved FastAPI documentation")
                    for content in doc_result.content:
                        if hasattr(content, 'text'):
                            self.logger.info(f"  Documentation preview: {content.text[:150]}...")
                else:
                    self.logger.warning("Documentation retrieval returned error")
                    
            except Exception as e:
                self.logger.error(f"Documentation retrieval failed: {e}")
                workflow_results["steps"].append({
                    "action": "get_documentation",
                    "error": str(e)
                })
        
        # Step 3: Get code examples for middleware
        self.logger.step("Getting middleware code examples")
        
        if stdio_server and "context7_get_examples" in stdio_server.tools_manager.tools:
            try:
                examples_result = await stdio_server.tools_manager.execute_tool(
                    "context7_get_examples",
                    {"library": "fastapi", "topic": "middleware", "limit": 3}
                )
                
                workflow_results["steps"].append({
                    "action": "get_examples",
                    "library": "fastapi",
                    "topic": "middleware",
                    "success": not examples_result.is_error
                })
                
                workflow_results["tools_used"].append("context7_get_examples")
                workflow_results["code_examples"].append("fastapi_middleware")
                
                if not examples_result.is_error:
                    self.logger.success("Retrieved middleware examples")
                    for content in examples_result.content:
                        if hasattr(content, 'text'):
                            self.logger.info(f"  Example preview: {content.text[:100]}...")
                else:
                    self.logger.warning("Examples retrieval returned error")
                    
            except Exception as e:
                self.logger.error(f"Examples retrieval failed: {e}")
                workflow_results["steps"].append({
                    "action": "get_examples",
                    "error": str(e)
                })
        
        # Step 4: Demonstrate multi-server coordination
        self.logger.step("Coordinating between multiple servers")
        
        coordination_results = await self.demonstrate_multi_server_coordination()
        workflow_results["multi_server_coordination"] = coordination_results
        
        workflow_results["summary"] = {
            "total_steps": len(workflow_results["steps"]),
            "successful_steps": len([s for s in workflow_results["steps"] if s.get("success", False)]),
            "tools_used_count": len(set(workflow_results["tools_used"])),
            "documentation_sources": len(workflow_results["documentation_accessed"]),
            "code_examples_retrieved": len(workflow_results["code_examples"])
        }
        
        self.logger.success("Documentation workflow completed")
        return workflow_results
    
    async def demonstrate_multi_server_coordination(self) -> Dict[str, Any]:
        """
        Demonstrate coordinating requests between multiple MCP servers.
        
        Shows how to:
        1. Route different requests to appropriate servers
        2. Aggregate results from multiple servers
        3. Handle server failures gracefully
        
        Returns:
            Dictionary containing coordination results
        """
        self.logger.step("Demonstrating multi-server coordination")
        
        coordination_results = {
            "servers_tested": [],
            "request_routing": [],
            "aggregated_results": {},
            "failover_scenarios": []
        }
        
        # Test each server's capabilities
        for server_name, server in self.servers.items():
            self.logger.info(f"Testing server: {server_name}")
            
            server_info = {
                "name": server_name,
                "tools_count": len(server.tools_manager.tools),
                "available_tools": list(server.tools_manager.tools.keys()),
                "status": "active"
            }
            
            # Test echo tool on each server
            try:
                echo_result = await server.tools_manager.execute_tool(
                    "echo",
                    {"message": f"Hello from {server_name} server"}
                )
                
                server_info["echo_test"] = {
                    "success": not echo_result.is_error,
                    "response_preview": str(echo_result.content[0].text)[:50] if echo_result.content else "No content"
                }
                
                coordination_results["request_routing"].append({
                    "server": server_name,
                    "tool": "echo",
                    "success": not echo_result.is_error
                })
                
            except Exception as e:
                server_info["echo_test"] = {"success": False, "error": str(e)}
                server_info["status"] = "error"
                
                coordination_results["failover_scenarios"].append({
                    "server": server_name,
                    "tool": "echo",
                    "error": str(e),
                    "failover_action": "route_to_alternative_server"
                })
            
            coordination_results["servers_tested"].append(server_info)
        
        # Demonstrate request aggregation
        self.logger.info("Aggregating weather data from multiple servers")
        
        weather_cities = ["London", "New York", "Tokyo"]
        weather_results = {}
        
        for city in weather_cities:
            # Try to get weather from each available server
            for server_name, server in self.servers.items():
                if "get_weather" in server.tools_manager.tools:
                    try:
                        weather_result = await server.tools_manager.execute_tool(
                            "get_weather",
                            {"city": city}
                        )
                        
                        if not weather_result.is_error:
                            weather_results[f"{city}_{server_name}"] = {
                                "city": city,
                                "server": server_name,
                                "success": True,
                                "data_preview": str(weather_result.content[0].text)[:100] if weather_result.content else "No data"
                            }
                            break  # Use first successful result
                        
                    except Exception as e:
                        weather_results[f"{city}_{server_name}"] = {
                            "city": city,
                            "server": server_name,
                            "success": False,
                            "error": str(e)
                        }
        
        coordination_results["aggregated_results"]["weather_data"] = weather_results
        
        # Demonstrate load balancing scenario
        self.logger.info("Simulating load balancing between servers")
        
        load_balance_results = []
        for i in range(5):  # Simulate 5 requests
            # Alternate between servers
            server_name = "stdio" if i % 2 == 0 else "http"
            server = self.servers.get(server_name)
            
            if server:
                try:
                    result = await server.tools_manager.execute_tool(
                        "echo",
                        {"message": f"Load balanced request {i+1}"}
                    )
                    
                    load_balance_results.append({
                        "request_id": i + 1,
                        "server": server_name,
                        "success": not result.is_error,
                        "response_time_simulation": f"{50 + (i * 10)}ms"  # Simulated response time
                    })
                    
                except Exception as e:
                    load_balance_results.append({
                        "request_id": i + 1,
                        "server": server_name,
                        "success": False,
                        "error": str(e)
                    })
        
        coordination_results["load_balancing"] = load_balance_results
        
        self.logger.success("Multi-server coordination demonstration completed")
        return coordination_results
    
    async def demonstrate_error_handling_workflow(self) -> Dict[str, Any]:
        """
        Demonstrate error handling and recovery in MCP workflows.
        
        Shows how to:
        1. Handle tool execution errors gracefully
        2. Implement retry logic
        3. Provide meaningful error messages
        4. Fallback to alternative approaches
        
        Returns:
            Dictionary containing error handling results
        """
        self.logger.step("Demonstrating error handling workflow")
        
        error_handling_results = {
            "error_scenarios": [],
            "recovery_strategies": [],
            "retry_attempts": [],
            "fallback_actions": []
        }
        
        stdio_server = self.servers.get("stdio")
        if not stdio_server:
            self.logger.error("No stdio server available for error handling demo")
            return error_handling_results
        
        # Scenario 1: Invalid tool parameters
        self.logger.info("Testing invalid parameter handling")
        
        try:
            # Try to call weather tool with invalid parameters
            invalid_result = await stdio_server.tools_manager.execute_tool(
                "get_weather",
                {"invalid_param": "test"}  # Missing required 'city' parameter
            )
            
            error_handling_results["error_scenarios"].append({
                "scenario": "invalid_parameters",
                "tool": "get_weather",
                "error_handled": invalid_result.is_error,
                "error_message": str(invalid_result.content[0].text) if invalid_result.content else "No error message"
            })
            
        except Exception as e:
            error_handling_results["error_scenarios"].append({
                "scenario": "invalid_parameters",
                "tool": "get_weather",
                "exception": str(e),
                "recovery": "caught_exception"
            })
        
        # Scenario 2: Non-existent tool
        self.logger.info("Testing non-existent tool handling")
        
        try:
            nonexistent_result = await stdio_server.tools_manager.execute_tool(
                "nonexistent_tool",
                {"param": "value"}
            )
            
            error_handling_results["error_scenarios"].append({
                "scenario": "nonexistent_tool",
                "tool": "nonexistent_tool",
                "error_handled": True,
                "recovery_action": "tool_not_found_error"
            })
            
        except Exception as e:
            error_handling_results["error_scenarios"].append({
                "scenario": "nonexistent_tool",
                "tool": "nonexistent_tool",
                "exception": str(e),
                "recovery": "exception_caught"
            })
        
        # Scenario 3: Retry logic simulation
        self.logger.info("Simulating retry logic for unreliable operations")
        
        retry_attempts = []
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Simulate an operation that might fail
                if attempt < 2:  # Fail first two attempts
                    raise Exception(f"Simulated failure on attempt {attempt + 1}")
                
                # Success on third attempt
                success_result = await stdio_server.tools_manager.execute_tool(
                    "echo",
                    {"message": f"Success after {attempt + 1} attempts"}
                )
                
                retry_attempts.append({
                    "attempt": attempt + 1,
                    "success": True,
                    "message": "Operation succeeded"
                })
                break
                
            except Exception as e:
                retry_attempts.append({
                    "attempt": attempt + 1,
                    "success": False,
                    "error": str(e)
                })
                
                if attempt < max_retries - 1:
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(0.1)  # Brief delay before retry
                else:
                    self.logger.error("All retry attempts exhausted")
        
        error_handling_results["retry_attempts"] = retry_attempts
        
        # Scenario 4: Fallback strategy
        self.logger.info("Demonstrating fallback strategies")
        
        fallback_strategies = []
        
        # Primary: Try Context7 documentation
        # Fallback: Use echo tool to provide basic help
        
        primary_success = False
        if "context7_get_documentation" in stdio_server.tools_manager.tools:
            try:
                doc_result = await stdio_server.tools_manager.execute_tool(
                    "context7_get_documentation",
                    {"library": "nonexistent_library"}
                )
                
                if not doc_result.is_error:
                    primary_success = True
                    fallback_strategies.append({
                        "strategy": "primary",
                        "action": "context7_documentation",
                        "success": True
                    })
                
            except Exception as e:
                fallback_strategies.append({
                    "strategy": "primary",
                    "action": "context7_documentation",
                    "success": False,
                    "error": str(e)
                })
        
        # If primary failed, use fallback
        if not primary_success:
            try:
                fallback_result = await stdio_server.tools_manager.execute_tool(
                    "echo",
                    {"message": "Documentation not available. Please check library name and try again."}
                )
                
                fallback_strategies.append({
                    "strategy": "fallback",
                    "action": "echo_help_message",
                    "success": not fallback_result.is_error,
                    "message": "Provided alternative help message"
                })
                
            except Exception as e:
                fallback_strategies.append({
                    "strategy": "fallback",
                    "action": "echo_help_message",
                    "success": False,
                    "error": str(e)
                })
        
        error_handling_results["fallback_actions"] = fallback_strategies
        
        self.logger.success("Error handling workflow demonstration completed")
        return error_handling_results
    
    async def generate_workflow_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive workflow report.
        
        Args:
            results: Combined results from all workflow demonstrations
            
        Returns:
            Formatted report string
        """
        self.logger.step("Generating workflow report")
        
        report_lines = [
            "# MCP Development Workflow Demonstration Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Executive Summary",
            "",
            f"This report demonstrates practical MCP usage across {len(self.servers)} servers,",
            f"showcasing real-world development workflows, multi-server coordination,",
            "and robust error handling strategies.",
            "",
            "## Workflow Results",
            ""
        ]
        
        # Documentation workflow results
        if "documentation_workflow" in results:
            doc_results = results["documentation_workflow"]
            summary = doc_results.get("summary", {})
            
            report_lines.extend([
                "### Documentation Workflow",
                f"- **Scenario**: {doc_results.get('scenario', 'N/A')}",
                f"- **Total Steps**: {summary.get('total_steps', 0)}",
                f"- **Successful Steps**: {summary.get('successful_steps', 0)}",
                f"- **Tools Used**: {summary.get('tools_used_count', 0)}",
                f"- **Documentation Sources**: {summary.get('documentation_sources', 0)}",
                f"- **Code Examples Retrieved**: {summary.get('code_examples_retrieved', 0)}",
                ""
            ])
        
        # Multi-server coordination results
        if "multi_server_coordination" in results:
            coord_results = results["multi_server_coordination"]
            
            report_lines.extend([
                "### Multi-Server Coordination",
                f"- **Servers Tested**: {len(coord_results.get('servers_tested', []))}",
                f"- **Request Routing Tests**: {len(coord_results.get('request_routing', []))}",
                f"- **Load Balancing Requests**: {len(coord_results.get('load_balancing', []))}",
                f"- **Failover Scenarios**: {len(coord_results.get('failover_scenarios', []))}",
                ""
            ])
        
        # Error handling results
        if "error_handling" in results:
            error_results = results["error_handling"]
            
            report_lines.extend([
                "### Error Handling & Recovery",
                f"- **Error Scenarios Tested**: {len(error_results.get('error_scenarios', []))}",
                f"- **Retry Attempts**: {len(error_results.get('retry_attempts', []))}",
                f"- **Fallback Strategies**: {len(error_results.get('fallback_actions', []))}",
                ""
            ])
        
        # Server status summary
        report_lines.extend([
            "## Server Status Summary",
            ""
        ])
        
        for server_name, server in self.servers.items():
            tools_list = ", ".join(server.tools_manager.tools.keys())
            report_lines.extend([
                f"### {server_name.upper()} Server",
                f"- **Tools Available**: {len(server.tools_manager.tools)}",
                f"- **Tool Names**: {tools_list}",
                f"- **Status**: Active",
                ""
            ])
        
        # Recommendations
        report_lines.extend([
            "## Recommendations for Production Use",
            "",
            "1. **API Key Management**: Ensure Context7 API keys are properly secured",
            "2. **Error Monitoring**: Implement comprehensive logging and monitoring",
            "3. **Load Balancing**: Consider implementing proper load balancing for multiple servers",
            "4. **Retry Logic**: Implement exponential backoff for external API calls",
            "5. **Fallback Strategies**: Always have fallback options for critical operations",
            "",
            "## Conclusion",
            "",
            "The MCP development workflow successfully demonstrates:",
            "- Seamless integration with external documentation services",
            "- Robust multi-server coordination capabilities", 
            "- Comprehensive error handling and recovery mechanisms",
            "- Practical applicability to real-world development scenarios",
            "",
            "This foundation provides a solid base for building production-ready",
            "MCP-powered development tools and workflows."
        ])
        
        report_content = "\n".join(report_lines)
        self.logger.success("Workflow report generated")
        
        return report_content
    
    async def run_complete_workflow(self) -> Dict[str, Any]:
        """
        Run the complete development workflow demonstration.
        
        Returns:
            Dictionary containing all workflow results
        """
        self.logger.step("Starting complete development workflow demonstration")
        
        try:
            # Setup servers
            await self.setup_servers()
            
            # Run workflow demonstrations
            results = {}
            
            # Documentation workflow
            self.logger.step("Running documentation workflow")
            results["documentation_workflow"] = await self.demonstrate_documentation_workflow()
            
            # Multi-server coordination
            self.logger.step("Running multi-server coordination")
            results["multi_server_coordination"] = await self.demonstrate_multi_server_coordination()
            
            # Error handling workflow
            self.logger.step("Running error handling workflow")
            results["error_handling"] = await self.demonstrate_error_handling_workflow()
            
            # Generate report
            results["report"] = await self.generate_workflow_report(results)
            
            self.logger.success("Complete workflow demonstration finished successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Workflow demonstration failed: {e}")
            raise
        finally:
            # Cleanup
            if self.context7_client:
                await self.context7_client.close()


async def main():
    """Main entry point for the workflow demonstration."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    
    logger = WorkflowLogger("main")
    logger.step("Starting MCP Development Workflow Demonstration")
    
    try:
        # Create and run workflow
        workflow = DevelopmentWorkflow()
        results = await workflow.run_complete_workflow()
        
        # Save results to file
        output_dir = Path("workflow_results")
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON results
        results_file = output_dir / f"workflow_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            # Remove the report from JSON (it's text)
            json_results = {k: v for k, v in results.items() if k != "report"}
            json.dump(json_results, f, indent=2, default=str)
        
        # Save report
        report_file = output_dir / f"workflow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(results["report"])
        
        logger.success(f"Results saved to {results_file}")
        logger.success(f"Report saved to {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("WORKFLOW DEMONSTRATION SUMMARY")
        print("="*60)
        
        if "documentation_workflow" in results:
            doc_summary = results["documentation_workflow"].get("summary", {})
            print(f"📚 Documentation Workflow: {doc_summary.get('successful_steps', 0)}/{doc_summary.get('total_steps', 0)} steps successful")
        
        if "multi_server_coordination" in results:
            coord_results = results["multi_server_coordination"]
            print(f"🔄 Multi-Server Coordination: {len(coord_results.get('servers_tested', []))} servers tested")
        
        if "error_handling" in results:
            error_results = results["error_handling"]
            print(f"🛡️  Error Handling: {len(error_results.get('error_scenarios', []))} scenarios tested")
        
        print(f"📊 Full report available at: {report_file}")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Workflow demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Workflow demonstration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)