#!/usr/bin/env python3
"""
FastAPI Development Workflow Example

This example demonstrates a practical development workflow using MCP servers
for building a FastAPI application with authentication middleware.

Scenario:
- Developer is building a REST API with FastAPI
- Needs to implement authentication middleware
- Uses Context7 for live documentation and code examples
- Coordinates between multiple MCP servers for different tasks

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

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from mcp_server.core.server import MCPServer
from mcp_server.transport.stdio import StdioTransport
from mcp_server.tools import (
    EchoTool,
    WeatherTool,
    Context7Client,
    Context7SearchTool,
    Context7DocumentationTool,
    Context7ExamplesTool,
)


class FastAPIWorkflowDemo:
    """
    Demonstrates a FastAPI development workflow using MCP servers.
    
    This class simulates a real development scenario where a developer
    is building a FastAPI application and needs:
    1. Documentation for FastAPI features
    2. Code examples for authentication middleware
    3. Library recommendations for security
    4. Best practices for API design
    """
    
    def __init__(self):
        self.logger = logging.getLogger("fastapi-workflow")
        self.server: Optional[MCPServer] = None
        self.context7_client: Optional[Context7Client] = None
        self.workflow_state = {
            "current_task": None,
            "completed_steps": [],
            "documentation_accessed": [],
            "code_examples_found": [],
            "libraries_discovered": []
        }
    
    async def setup_mcp_server(self) -> None:
        """Set up MCP server with required tools."""
        self.logger.info("🔧 Setting up MCP server for FastAPI development")
        
        # Create stdio transport and server
        transport = StdioTransport()
        self.server = MCPServer(transport, "fastapi-dev-server")
        
        # Register basic tools
        self.server.register_tool(EchoTool())
        self.server.register_tool(WeatherTool())
        
        # Setup Context7 tools
        context7_api_key = os.getenv("CONTEXT7_API_KEY")
        if context7_api_key:
            try:
                self.context7_client = Context7Client(context7_api_key)
                self.server.register_tool(Context7SearchTool(self.context7_client))
                self.server.register_tool(Context7DocumentationTool(self.context7_client))
                self.server.register_tool(Context7ExamplesTool(self.context7_client))
                self.logger.info("✅ Context7 tools registered with real API")
            except Exception as e:
                self.logger.warning(f"⚠️  Context7 setup failed: {e}")
                self.logger.info("📝 Will use mock responses for demonstration")
        else:
            self.logger.info("📝 No Context7 API key found - using mock responses")
        
        self.logger.info(f"🚀 MCP server ready with {len(self.server.tools_manager.tools)} tools")
    
    async def step_1_research_authentication_libraries(self) -> Dict[str, Any]:
        """
        Step 1: Research authentication libraries for FastAPI.
        
        Simulates a developer searching for authentication solutions.
        """
        self.logger.info("📚 Step 1: Researching authentication libraries")
        self.workflow_state["current_task"] = "library_research"
        
        step_results = {
            "step": 1,
            "task": "Research authentication libraries",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "libraries_found": [],
            "recommendations": []
        }
        
        if "context7_search_libraries" in self.server.tools_manager.tools:
            try:
                # Search for FastAPI authentication libraries
                search_queries = [
                    "fastapi authentication",
                    "fastapi jwt",
                    "fastapi oauth2",
                    "fastapi security"
                ]
                
                for query in search_queries:
                    self.logger.info(f"🔍 Searching for: {query}")
                    
                    result = await self.server.tools_manager.execute_tool(
                        "context7_search_libraries",
                        {"query": query, "limit": 5}
                    )
                    
                    if not result.is_error and result.content:
                        for content in result.content:
                            if hasattr(content, 'text'):
                                # Parse the response (in real scenario, this would be structured data)
                                libraries_info = content.text
                                step_results["libraries_found"].append({
                                    "query": query,
                                    "response": libraries_info[:200] + "..." if len(libraries_info) > 200 else libraries_info
                                })
                                self.workflow_state["libraries_discovered"].append(query)
                
                # Generate recommendations based on findings
                step_results["recommendations"] = [
                    "FastAPI-Users: Complete user management solution",
                    "python-jose: JWT token handling",
                    "passlib: Password hashing utilities",
                    "python-multipart: Form data handling for OAuth2"
                ]
                
                step_results["success"] = True
                self.logger.info("✅ Library research completed successfully")
                
            except Exception as e:
                self.logger.error(f"❌ Library search failed: {e}")
                step_results["error"] = str(e)
        else:
            # Fallback: Use echo tool to provide basic recommendations
            self.logger.info("📝 Using fallback approach for library recommendations")
            
            fallback_result = await self.server.tools_manager.execute_tool(
                "echo",
                {"message": "Recommended FastAPI auth libraries: FastAPI-Users, python-jose, passlib, python-multipart"}
            )
            
            if not fallback_result.is_error:
                step_results["libraries_found"].append({
                    "source": "fallback",
                    "recommendations": fallback_result.content[0].text if fallback_result.content else "No content"
                })
                step_results["success"] = True
        
        self.workflow_state["completed_steps"].append(step_results)
        return step_results
    
    async def step_2_get_fastapi_documentation(self) -> Dict[str, Any]:
        """
        Step 2: Retrieve FastAPI documentation for security features.
        
        Focuses on authentication and middleware documentation.
        """
        self.logger.info("📖 Step 2: Getting FastAPI security documentation")
        self.workflow_state["current_task"] = "documentation_retrieval"
        
        step_results = {
            "step": 2,
            "task": "Get FastAPI documentation",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "documentation_sections": [],
            "key_concepts": []
        }
        
        if "context7_get_documentation" in self.server.tools_manager.tools:
            try:
                # Get FastAPI documentation
                self.logger.info("📥 Retrieving FastAPI documentation")
                
                doc_result = await self.server.tools_manager.execute_tool(
                    "context7_get_documentation",
                    {"library": "fastapi", "version": "latest"}
                )
                
                if not doc_result.is_error and doc_result.content:
                    for content in doc_result.content:
                        if hasattr(content, 'text'):
                            doc_text = content.text
                            step_results["documentation_sections"].append({
                                "library": "fastapi",
                                "content_preview": doc_text[:300] + "..." if len(doc_text) > 300 else doc_text,
                                "length": len(doc_text)
                            })
                            self.workflow_state["documentation_accessed"].append("fastapi")
                
                # Also get security-specific documentation
                security_topics = ["security", "authentication", "middleware"]
                
                for topic in security_topics:
                    self.logger.info(f"📥 Getting documentation for: {topic}")
                    
                    topic_result = await self.server.tools_manager.execute_tool(
                        "context7_get_documentation",
                        {"library": f"fastapi-{topic}", "version": "latest"}
                    )
                    
                    if not topic_result.is_error and topic_result.content:
                        for content in topic_result.content:
                            if hasattr(content, 'text'):
                                step_results["documentation_sections"].append({
                                    "topic": topic,
                                    "content_preview": content.text[:200] + "...",
                                    "relevance": "high"
                                })
                
                # Extract key concepts
                step_results["key_concepts"] = [
                    "OAuth2 with Password (and hashing), Bearer with JWT tokens",
                    "Security dependencies and dependency injection",
                    "Middleware for request/response processing",
                    "HTTPBearer and HTTPBasic authentication schemes",
                    "Scopes for fine-grained permissions"
                ]
                
                step_results["success"] = True
                self.logger.info("✅ Documentation retrieval completed")
                
            except Exception as e:
                self.logger.error(f"❌ Documentation retrieval failed: {e}")
                step_results["error"] = str(e)
        else:
            # Fallback: Provide basic documentation outline
            self.logger.info("📝 Using fallback documentation outline")
            
            fallback_result = await self.server.tools_manager.execute_tool(
                "echo",
                {"message": "FastAPI Security: OAuth2, JWT, Dependencies, Middleware, Scopes"}
            )
            
            if not fallback_result.is_error:
                step_results["documentation_sections"].append({
                    "source": "fallback",
                    "outline": fallback_result.content[0].text if fallback_result.content else "No content"
                })
                step_results["success"] = True
        
        self.workflow_state["completed_steps"].append(step_results)
        return step_results
    
    async def step_3_get_middleware_examples(self) -> Dict[str, Any]:
        """
        Step 3: Get code examples for authentication middleware.
        
        Retrieves practical code examples for implementing auth middleware.
        """
        self.logger.info("💻 Step 3: Getting authentication middleware examples")
        self.workflow_state["current_task"] = "code_examples"
        
        step_results = {
            "step": 3,
            "task": "Get middleware code examples",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "examples": [],
            "patterns": []
        }
        
        if "context7_get_examples" in self.server.tools_manager.tools:
            try:
                # Get middleware examples
                middleware_topics = [
                    "authentication middleware",
                    "jwt middleware", 
                    "oauth2 implementation",
                    "security dependencies"
                ]
                
                for topic in middleware_topics:
                    self.logger.info(f"🔍 Getting examples for: {topic}")
                    
                    examples_result = await self.server.tools_manager.execute_tool(
                        "context7_get_examples",
                        {"library": "fastapi", "topic": topic, "limit": 3}
                    )
                    
                    if not examples_result.is_error and examples_result.content:
                        for content in examples_result.content:
                            if hasattr(content, 'text'):
                                example_text = content.text
                                step_results["examples"].append({
                                    "topic": topic,
                                    "code_preview": example_text[:400] + "..." if len(example_text) > 400 else example_text,
                                    "language": "python",
                                    "complexity": "intermediate"
                                })
                                self.workflow_state["code_examples_found"].append(topic)
                
                # Common patterns identified
                step_results["patterns"] = [
                    "Dependency injection for authentication",
                    "JWT token validation in middleware",
                    "Request context for user information",
                    "Exception handling for auth failures",
                    "Async middleware implementation"
                ]
                
                step_results["success"] = True
                self.logger.info("✅ Code examples retrieved successfully")
                
            except Exception as e:
                self.logger.error(f"❌ Code examples retrieval failed: {e}")
                step_results["error"] = str(e)
        else:
            # Fallback: Provide basic code structure
            self.logger.info("📝 Using fallback code structure")
            
            fallback_code = """
# Basic FastAPI Authentication Middleware Structure
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Token validation logic here
    return {"user": "authenticated"}

@app.get("/protected")
async def protected_route(user=Depends(verify_token)):
    return {"message": "Access granted", "user": user}
            """
            
            fallback_result = await self.server.tools_manager.execute_tool(
                "echo",
                {"message": fallback_code}
            )
            
            if not fallback_result.is_error:
                step_results["examples"].append({
                    "source": "fallback",
                    "code": fallback_result.content[0].text if fallback_result.content else "No content",
                    "type": "basic_structure"
                })
                step_results["success"] = True
        
        self.workflow_state["completed_steps"].append(step_results)
        return step_results
    
    async def step_4_validate_implementation(self) -> Dict[str, Any]:
        """
        Step 4: Validate implementation approach using multiple tools.
        
        Uses multiple MCP tools to validate the chosen implementation approach.
        """
        self.logger.info("✅ Step 4: Validating implementation approach")
        self.workflow_state["current_task"] = "validation"
        
        step_results = {
            "step": 4,
            "task": "Validate implementation approach",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "validation_checks": [],
            "recommendations": []
        }
        
        # Validation checklist
        validation_items = [
            "Security best practices compliance",
            "Performance considerations",
            "Error handling completeness",
            "Testing strategy",
            "Documentation coverage"
        ]
        
        for item in validation_items:
            self.logger.info(f"🔍 Validating: {item}")
            
            # Use echo tool to simulate validation feedback
            validation_result = await self.server.tools_manager.execute_tool(
                "echo",
                {"message": f"Validation check: {item} - Reviewing implementation approach"}
            )
            
            if not validation_result.is_error:
                step_results["validation_checks"].append({
                    "item": item,
                    "status": "reviewed",
                    "feedback": validation_result.content[0].text if validation_result.content else "No feedback"
                })
        
        # Generate final recommendations
        step_results["recommendations"] = [
            "Use FastAPI-Users for comprehensive user management",
            "Implement JWT with proper expiration and refresh tokens",
            "Add rate limiting middleware for security",
            "Use dependency injection for clean authentication flow",
            "Implement comprehensive error handling and logging",
            "Add unit tests for authentication middleware",
            "Document API endpoints with security requirements"
        ]
        
        step_results["success"] = True
        self.logger.info("✅ Implementation validation completed")
        
        self.workflow_state["completed_steps"].append(step_results)
        return step_results
    
    async def generate_implementation_summary(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive implementation summary.
        
        Args:
            all_results: Results from all workflow steps
            
        Returns:
            Dictionary containing implementation summary
        """
        self.logger.info("📊 Generating implementation summary")
        
        summary = {
            "workflow_name": "FastAPI Authentication Implementation",
            "completion_time": datetime.now().isoformat(),
            "total_steps": len(all_results),
            "successful_steps": len([r for r in all_results if r.get("success", False)]),
            "workflow_state": self.workflow_state,
            "implementation_plan": {},
            "next_steps": [],
            "resources": {}
        }
        
        # Extract key findings from each step
        for result in all_results:
            step_num = result.get("step", 0)
            
            if step_num == 1:  # Library research
                summary["resources"]["libraries"] = result.get("recommendations", [])
            elif step_num == 2:  # Documentation
                summary["resources"]["documentation"] = result.get("key_concepts", [])
            elif step_num == 3:  # Code examples
                summary["resources"]["patterns"] = result.get("patterns", [])
            elif step_num == 4:  # Validation
                summary["implementation_plan"]["recommendations"] = result.get("recommendations", [])
        
        # Generate implementation plan
        summary["implementation_plan"]["phases"] = [
            {
                "phase": 1,
                "name": "Setup Dependencies",
                "tasks": [
                    "Install FastAPI-Users, python-jose, passlib",
                    "Configure database models for users",
                    "Set up JWT secret key management"
                ]
            },
            {
                "phase": 2,
                "name": "Implement Authentication",
                "tasks": [
                    "Create user registration endpoint",
                    "Implement login with JWT token generation",
                    "Add password hashing and validation"
                ]
            },
            {
                "phase": 3,
                "name": "Add Middleware",
                "tasks": [
                    "Create JWT validation middleware",
                    "Implement dependency injection for auth",
                    "Add role-based access control"
                ]
            },
            {
                "phase": 4,
                "name": "Testing & Documentation",
                "tasks": [
                    "Write unit tests for auth functions",
                    "Add integration tests for endpoints",
                    "Document API security requirements"
                ]
            }
        ]
        
        # Next steps for developer
        summary["next_steps"] = [
            "Set up development environment with recommended libraries",
            "Implement user model and database schema",
            "Create authentication endpoints following examples",
            "Add middleware for JWT token validation",
            "Implement comprehensive testing suite",
            "Deploy with proper security configurations"
        ]
        
        # Calculate success metrics
        summary["metrics"] = {
            "completion_rate": f"{summary['successful_steps']}/{summary['total_steps']} steps",
            "libraries_discovered": len(self.workflow_state["libraries_discovered"]),
            "documentation_accessed": len(self.workflow_state["documentation_accessed"]),
            "code_examples_found": len(self.workflow_state["code_examples_found"]),
            "workflow_duration": "Simulated workflow - actual duration varies"
        }
        
        return summary
    
    async def run_complete_workflow(self) -> Dict[str, Any]:
        """
        Run the complete FastAPI development workflow.
        
        Returns:
            Dictionary containing complete workflow results
        """
        self.logger.info("🚀 Starting FastAPI development workflow")
        
        try:
            # Setup
            await self.setup_mcp_server()
            
            # Run workflow steps
            results = []
            
            # Step 1: Research libraries
            step1_result = await self.step_1_research_authentication_libraries()
            results.append(step1_result)
            
            # Step 2: Get documentation
            step2_result = await self.step_2_get_fastapi_documentation()
            results.append(step2_result)
            
            # Step 3: Get code examples
            step3_result = await self.step_3_get_middleware_examples()
            results.append(step3_result)
            
            # Step 4: Validate approach
            step4_result = await self.step_4_validate_implementation()
            results.append(step4_result)
            
            # Generate summary
            summary = await self.generate_implementation_summary(results)
            
            # Combine all results
            complete_results = {
                "workflow_results": results,
                "summary": summary,
                "mcp_server_info": {
                    "tools_available": len(self.server.tools_manager.tools),
                    "tool_names": list(self.server.tools_manager.tools.keys()),
                    "context7_enabled": self.context7_client is not None
                }
            }
            
            self.logger.info("🎉 FastAPI development workflow completed successfully")
            return complete_results
            
        except Exception as e:
            self.logger.error(f"❌ Workflow failed: {e}")
            raise
        finally:
            # Cleanup
            if self.context7_client:
                await self.context7_client.close()


async def main():
    """Main entry point for the FastAPI development workflow example."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    
    logger = logging.getLogger("main")
    
    print("🚀 FastAPI Development Workflow Example")
    print("=" * 50)
    print("This example demonstrates using MCP servers for FastAPI development")
    print("including authentication middleware implementation.")
    print()
    
    # Check for Context7 API key
    if os.getenv("CONTEXT7_API_KEY"):
        print("✅ Context7 API key found - will use real API calls")
    else:
        print("📝 No Context7 API key - will use mock responses for demonstration")
    
    print("=" * 50)
    print()
    
    try:
        # Run workflow
        workflow = FastAPIWorkflowDemo()
        results = await workflow.run_complete_workflow()
        
        # Save results
        output_dir = Path("workflow_results")
        output_dir.mkdir(exist_ok=True)
        
        results_file = output_dir / f"fastapi_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Print summary
        summary = results["summary"]
        print("\n" + "="*50)
        print("WORKFLOW SUMMARY")
        print("="*50)
        print(f"📋 Workflow: {summary['workflow_name']}")
        print(f"✅ Completion: {summary['metrics']['completion_rate']}")
        print(f"📚 Libraries discovered: {summary['metrics']['libraries_discovered']}")
        print(f"📖 Documentation accessed: {summary['metrics']['documentation_accessed']}")
        print(f"💻 Code examples found: {summary['metrics']['code_examples_found']}")
        print(f"📊 Results saved to: {results_file}")
        
        print("\n🎯 NEXT STEPS:")
        for i, step in enumerate(summary["next_steps"][:3], 1):
            print(f"{i}. {step}")
        
        print("\n📚 KEY LIBRARIES TO USE:")
        for lib in summary["resources"].get("libraries", [])[:3]:
            print(f"• {lib}")
        
        print("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return False


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