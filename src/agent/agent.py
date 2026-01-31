"""Embedded Systems AI Agent using LangGraph"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from src.state import ProjectState
from src.config import GROQ_MODEL, GROQ_TEMPERATURE, PROJECTS_DIR
from src.tools import (
    EmbeddedSystemsTools,
    web_search_tool,
    component_lookup_tool,
    pinout_lookup_tool,
    code_template_tool,
    code_validator_tool,
    library_lookup_tool,
    file_operations_tool
)
from src.utils import extract_code_from_response


class EmbeddedSystemsAgent:
    """Main agent class using LangGraph for embedded systems development"""

    def __init__(self, groq_api_key: str, knowledge_base_path: str = None, auto_ingest: bool = True):
        """Initialize the agent
        
        Args:
            groq_api_key: Groq API key
            knowledge_base_path: Path to knowledge base directory
            auto_ingest: Whether to automatically ingest knowledge base files on startup
        """
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=GROQ_MODEL,
            temperature=GROQ_TEMPERATURE
        )

        self.tools_instance = EmbeddedSystemsTools(knowledge_base_path)

        # Initialize tools list
        self.tools = [
            web_search_tool,
            component_lookup_tool,
            pinout_lookup_tool,
            code_template_tool,
            code_validator_tool,
            library_lookup_tool,
            file_operations_tool
        ]

        # Create tool node
        self.tool_node = ToolNode(tools=self.tools)

        # Create the graph
        self.graph = self._create_graph()
        
        # Auto-ingest knowledge base if enabled
        self.auto_ingest = auto_ingest
        if auto_ingest:
            self._auto_ingest_on_startup()
    
    def _auto_ingest_on_startup(self):
        """Auto-ingest knowledge base files on startup"""
        try:
            # Check if there are files to ingest
            scan_results = self.scan_knowledge_base()
            
            if scan_results.get("error"):
                print(f"⚠️ Knowledge base scan error: {scan_results['error']}")
                return
            
            total_files = scan_results.get("total_files", 0)
            
            if total_files == 0:
                print("📚 Knowledge base is empty")
                return
            
            # Check if already ingested (with threshold tolerance for minor changes)
            ingested_count = len(self.tools_instance.get_ingested_files())
            tolerance = int(total_files * 0.05)  # 5% tolerance
            
            if ingested_count >= (total_files - tolerance):
                print(f"✅ Knowledge base already ingested ({ingested_count} files)")
                return
            
            print(f"📚 Auto-ingesting knowledge base ({total_files} files)...")
            print("⏳ This may take a few minutes on first run...")
            
            # Run ingestion synchronously
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            results = loop.run_until_complete(self.ingest_knowledge_base())
            loop.close()
            
            if results["success"]:
                print(f"✅ {results['message']}")
            else:
                print(f"⚠️ {results['message']}")
                if results.get('fail_count', 0) > 0:
                    print(f"   Errors: {results['fail_count']} files failed")
                    
        except Exception as e:
            print(f"⚠️ Auto-ingest error: {str(e)}")

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow
        
        Returns:
            Compiled state graph
        """
        # Agent function
        def call_agent(state: ProjectState):
            messages = state["messages"]
            response = self.llm.bind_tools(self.tools).invoke(messages)
            return {"messages": [response]}

        def call_tools(state: ProjectState):
            return self.tool_node.invoke({"messages": state["messages"]})

        # Conditional edge
        def should_continue(state: ProjectState):
            messages = state["messages"]
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            return "end"

        # Build graph
        workflow = StateGraph(ProjectState)
        workflow.add_node("agent", call_agent)
        workflow.add_node("tools", call_tools)

        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {"tools": "tools", "end": END}
        )
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    async def process_request(self, user_input: str, platform: str = "") -> Dict:
        """Process user request through the LangGraph workflow
        
        Args:
            user_input: User request text
            platform: Target platform
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Validate platform
            platform_name = platform if platform else "general"
            
            # Create initial state
            initial_state = ProjectState(
                messages=[
                    SystemMessage(content=f"""Expert embedded systems developer for Arduino, ESP32, Raspberry Pi.

IMPORTANT Tool Usage Guidelines:
- Use component_lookup_tool ONLY for specific sensors/modules (DHT22, HC-SR04, LED, etc.)
- Use pinout_lookup_tool for board pinouts (arduino_uno, esp32, raspberry_pi)
- Use web_search_tool for online tutorials and documentation
- Do NOT use component_lookup_tool for platforms/boards themselves

For direct questions, answer without tools. Be concise.
Platform: {platform_name}
"""),
                    HumanMessage(content=user_input)
                ],
                platform=platform_name,
                requirements=user_input,
                generated_code="",
                validation_result=None,
                documentation="",
                project_name="",
                current_step="processing",
                context_chunks=None,
                error_message="",
                search_results=None
            )

            # Run the graph with error handling
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, self.graph.invoke, initial_state
                )
            except Exception as graph_error:
                # If tool execution fails, return a helpful error
                error_msg = str(graph_error)
                if "tool_use_failed" in error_msg or "Failed to call a function" in error_msg:
                    return {
                        "success": False,
                        "error": "I couldn't use the tools properly. Please rephrase your question or ask for specific information."
                    }
                return {
                    "success": False,
                    "error": f"Processing error: {error_msg}"
                }

            # Extract the final response
            final_message = result["messages"][-1]
            
            # Get knowledge base sources if available
            sources = []
            try:
                kb_results = self.tools_instance.search_knowledge(user_input, k=3)
                sources = [{
                    "file": r.get('source_file', 'Unknown'),
                    "type": r.get('file_type', 'Unknown'),
                    "relevance": r.get('relevance_score', 'N/A')
                } for r in kb_results if r.get('source_file')]
            except:
                pass

            return {
                "success": True,
                "response": final_message.content if hasattr(final_message, 'content') else str(final_message),
                "platform": platform_name,
                "timestamp": datetime.now().isoformat(),
                "sources": sources
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Request processing failed: {str(e)}"
            }

    async def generate_project(self, platform: str, requirements: str,
                             project_name: str) -> Dict:
        """Generate complete project with code, documentation, and validation
        
        Args:
            platform: Target platform
            requirements: Project requirements
            project_name: Name of the project
            
        Returns:
            Dictionary with project generation results
        """
        try:
            # Validate platform
            if not platform or platform.lower() not in ['arduino', 'esp32', 'raspberry_pi']:
                return {
                    "success": False,
                    "error": f"Invalid platform: {platform}. Must be: arduino, esp32, or raspberry_pi"
                }
            
            # Step 1: Generate code (optimized request)
            code_request = f"Generate complete working {platform} code for: {requirements}. Include comments and error handling."

            code_result = await self.process_request(code_request, platform)

            if not code_result["success"]:
                return code_result

            # Step 2: Generate documentation (simplified)
            doc_request = f"Create brief markdown documentation for {platform} project '{project_name}': overview, hardware setup, and usage for: {requirements}"

            doc_result = await self.process_request(doc_request, platform)

            # Step 3: Save project
            # Ensure projects directory exists
            PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
            project_dir = PROJECTS_DIR / project_name
            project_dir.mkdir(parents=True, exist_ok=True)

            # Save files
            project_data = {
                "name": project_name,
                "platform": platform,
                "requirements": requirements,
                "generated_code": code_result.get("response", ""),
                "documentation": doc_result.get("response", "") if doc_result.get("success") else "",
                "timestamp": datetime.now().isoformat()
            }

            # Save project metadata
            try:
                with open(project_dir / "project.json", 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=2)

                # Save documentation
                with open(project_dir / "README.md", 'w', encoding='utf-8') as f:
                    f.write(project_data["documentation"])

                # Extract and save code if present
                code_content = extract_code_from_response(code_result["response"])
                if code_content:
                    if platform.lower() in ["arduino", "esp32"]:
                        code_file = project_dir / f"{project_name}.ino"
                    else:
                        code_file = project_dir / f"{project_name}.py"

                    with open(code_file, 'w', encoding='utf-8') as f:
                        f.write(code_content)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to save project files: {str(e)}"
                }

            return {
                "success": True,
                "project_name": project_name,
                "project_path": str(project_dir),
                "code_generated": bool(code_content),
                "documentation_generated": bool(doc_result.get("success")),
                "files_created": [
                    "project.json",
                    "README.md",
                    f"{project_name}.{'ino' if platform.lower() in ['arduino', 'esp32'] else 'py'}"
                ]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Project generation failed: {str(e)}"
            }

    async def add_knowledge(self, file_path: str) -> Dict:
        """Add documents to the knowledge base
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dict with success status and message
        """
        success, message = await self.tools_instance.add_knowledge(file_path)
        return {"success": success, "message": message}
    
    async def ingest_knowledge_base(self, directory_path: str = None) -> Dict:
        """Ingest entire knowledge base directory
        
        Args:
            directory_path: Path to knowledge base (defaults to KNOWLEDGE_BASE_DIR)
            
        Returns:
            Dict with ingestion results
        """
        if directory_path is None:
            from src.config import KNOWLEDGE_BASE_DIR
            directory_path = str(KNOWLEDGE_BASE_DIR)
        
        success, fail, errors = await self.tools_instance.ingest_directory(directory_path, recursive=True)
        
        return {
            "success": fail == 0,
            "success_count": success,
            "fail_count": fail,
            "errors": errors,
            "message": f"✅ Ingested {success} files" + (f" ({fail} failed)" if fail > 0 else "")
        }
    
    def scan_knowledge_base(self, directory_path: str = None) -> Dict:
        """Scan knowledge base without ingesting
        
        Args:
            directory_path: Path to knowledge base (defaults to KNOWLEDGE_BASE_DIR)
            
        Returns:
            Dict with scan results
        """
        if directory_path is None:
            from src.config import KNOWLEDGE_BASE_DIR
            directory_path = str(KNOWLEDGE_BASE_DIR)
        
        return self.tools_instance.scan_directory(directory_path, recursive=True)
