"""Enhanced CLI interface with LangGraph integration"""

import asyncio
from datetime import datetime
from typing import Optional

from src.agent import EmbeddedSystemsAgent
from src.utils import save_code_to_file


class EmbeddedSystemsCLI:
    """Command-line interface for the embedded systems agent"""

    def __init__(self, groq_api_key: str, auto_ingest: bool = True):
        """Initialize CLI
        
        Args:
            groq_api_key: Groq API key
            auto_ingest: Whether to auto-ingest knowledge base
        """
        self.agent = EmbeddedSystemsAgent(groq_api_key, auto_ingest=auto_ingest)
        self.current_platform = ""
        self.session_history = []

    async def run_interactive_session(self):
        """Run enhanced interactive session"""
        print("🤖 Embedded Systems AI Agent with LangGraph")
        print("=" * 50)
        print("Available commands:")
        print("- chat: General conversation and questions")
        print("- generate: Generate code for specific platform")
        print("- project: Create complete project")
        print("- search: Search web for information")
        print("- knowledge: Add knowledge files")
        print("- tools: List available tools")
        print("- platform: Set current platform")
        print("- history: Show session history")
        print("- quit: Exit")
        print("=" * 50)

        while True:
            try:
                command = input(f"\n[{self.current_platform or 'general'}] > ").strip().lower()

                if command == "quit":
                    print("👋 Goodbye!")
                    break
                elif command == "chat":
                    await self._handle_chat()
                elif command == "generate":
                    await self._handle_generate()
                elif command == "project":
                    await self._handle_project()
                elif command == "search":
                    await self._handle_search()
                elif command == "knowledge":
                    await self._handle_knowledge()
                elif command == "tools":
                    await self._handle_tools()
                elif command == "platform":
                    await self._handle_platform()
                elif command == "history":
                    await self._handle_history()
                elif command == "help":
                    await self._show_help()
                else:
                    print("❓ Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    async def _handle_chat(self):
        """Handle general chat/questions"""
        question = input("Ask me anything about embedded systems: ").strip()
        if not question:
            return

        print("🤔 Thinking...")
        result = await self.agent.process_request(question, self.current_platform)

        if result["success"]:
            print(f"\n💡 {result['response']}")
            self.session_history.append({
                "type": "chat",
                "question": question,
                "response": result['response'][:100] + "..." if len(result['response']) > 100 else result['response'],
                "timestamp": result['timestamp']
            })
        else:
            print(f"❌ Error: {result['error']}")

    async def _handle_generate(self):
        """Handle code generation"""
        if not self.current_platform:
            platform = input("Platform (arduino/esp32/raspberry_pi): ").strip().lower()
        else:
            platform = self.current_platform
            print(f"Using current platform: {platform}")

        requirements = input("Describe what you want to build: ").strip()
        if not requirements:
            return

        print("⚡ Generating code...")

        request = f"Generate {platform} code for: {requirements}"
        result = await self.agent.process_request(request, platform)

        if result["success"]:
            print(f"\n✅ Code generated for {platform}:")
            print("=" * 50)
            print(result['response'])
            print("=" * 50)

            self.session_history.append({
                "type": "code_generation",
                "platform": platform,
                "requirements": requirements,
                "timestamp": result['timestamp']
            })

            # Ask if user wants to save
            save = input("\n💾 Save this code? (y/n): ").strip().lower()
            if save == 'y':
                filename = input("Filename (without extension): ").strip()
                if filename:
                    await self._save_code(result['response'], platform, filename)
        else:
            print(f"❌ Error: {result['error']}")

    async def _handle_project(self):
        """Handle complete project generation"""
        if not self.current_platform:
            platform = input("Platform (arduino/esp32/raspberry_pi): ").strip().lower()
        else:
            platform = self.current_platform
            print(f"Using current platform: {platform}")

        project_name = input("Project name: ").strip()
        requirements = input("Project requirements: ").strip()

        if not project_name or not requirements:
            print("⚠️ Project name and requirements are required")
            return

        print("🏗️ Creating complete project...")

        result = await self.agent.generate_project(platform, requirements, project_name)

        if result["success"]:
            print(f"\n✅ Project '{project_name}' created successfully!")
            print(f"📁 Location: {result['project_path']}")
            print(f"📄 Files created: {', '.join(result['files_created'])}")

            self.session_history.append({
                "type": "project_creation",
                "project_name": project_name,
                "platform": platform,
                "timestamp": datetime.now().isoformat()
            })
        else:
            print(f"❌ Error: {result['error']}")

    async def _handle_search(self):
        """Handle web search"""
        query = input("Search query: ").strip()
        if not query:
            return

        print("🔍 Searching...")

        search_request = f"Search for: {query}"
        result = await self.agent.process_request(search_request)

        if result["success"]:
            print(f"\n🔍 Search results:")
            print(result['response'])
        else:
            print(f"❌ Search error: {result['error']}")

    async def _handle_knowledge(self):
        """Handle knowledge base operations"""
        print("Knowledge base operations:")
        print("1. Add PDF document")
        print("2. Add text file")
        print("3. List knowledge files")

        choice = input("Choose option (1-3): ").strip()

        if choice == "1" or choice == "2":
            file_path = input("File path: ").strip()
            if file_path:
                success = await self.agent.add_knowledge(file_path)
                if success:
                    print("✅ File added to knowledge base")
                else:
                    print("❌ Failed to add file")

        elif choice == "3":
            kb_path = self.agent.tools_instance.knowledge_base_path
            if kb_path.exists():
                files = list(kb_path.rglob("*"))
                print(f"\n📚 Knowledge base contents ({len(files)} files):")
                for file in files[:10]:
                    print(f"  - {file.name}")
                if len(files) > 10:
                    print(f"  ... and {len(files) - 10} more files")
            else:
                print("📚 Knowledge base is empty")

    async def _handle_tools(self):
        """Show available tools"""
        print("\n🔧 Available Tools:")
        print("=" * 30)
        tools_info = [
            ("🌐 web_search_tool", "Search web for embedded systems information"),
            ("🔌 component_lookup_tool", "Look up electronic components and sensors"),
            ("📌 pinout_lookup_tool", "Get pinout information for microcontrollers"),
            ("📝 code_template_tool", "Get code templates for different platforms"),
            ("✅ code_validator_tool", "Validate code syntax and structure"),
            ("📚 library_lookup_tool", "Look up library information"),
            ("📁 file_operations_tool", "File and directory operations"),
        ]

        for tool_name, description in tools_info:
            print(f"{tool_name}: {description}")

        print("=" * 30)

        # Tool usage example
        tool_demo = input("\nWant to try a tool? (component/pinout/template/n): ").strip().lower()

        if tool_demo == "component":
            component = input("Component name (e.g., DHT22, HC-SR04): ").strip()
            if component:
                request = f"Look up component information for {component}"
                result = await self.agent.process_request(request)
                print(f"\n{result.get('response', 'No information found')}")

        elif tool_demo == "pinout":
            platform = input("Platform (arduino_uno/esp32/raspberry_pi): ").strip()
            if platform:
                request = f"Show pinout information for {platform}"
                result = await self.agent.process_request(request)
                print(f"\n{result.get('response', 'No pinout found')}")

        elif tool_demo == "template":
            platform = input("Platform: ").strip()
            template_type = input("Template type (basic/sensor_reading/web_server): ").strip()
            if platform and template_type:
                request = f"Get {template_type} template for {platform}"
                result = await self.agent.process_request(request)
                print(f"\n{result.get('response', 'No template found')}")

    async def _handle_platform(self):
        """Set current platform"""
        platforms = ["arduino", "esp32", "raspberry_pi"]
        print(f"\nAvailable platforms: {', '.join(platforms)}")
        platform = input("Set current platform (or 'clear' to reset): ").strip().lower()

        if platform == "clear":
            self.current_platform = ""
            print("✅ Platform cleared")
        elif platform in platforms:
            self.current_platform = platform
            print(f"✅ Current platform set to: {platform}")
        else:
            print("❌ Invalid platform")

    async def _handle_history(self):
        """Show session history"""
        if not self.session_history:
            print("📝 No history yet")
            return

        print(f"\n📝 Session History ({len(self.session_history)} items):")
        print("=" * 40)

        for i, item in enumerate(self.session_history[-5:], 1):
            print(f"{i}. [{item['type']}] {item.get('timestamp', 'Unknown time')}")
            if item['type'] == 'chat':
                print(f"   Q: {item['question'][:50]}...")
                print(f"   A: {item['response']}")
            elif item['type'] == 'code_generation':
                print(f"   Platform: {item['platform']}")
                print(f"   Requirements: {item['requirements'][:50]}...")
            elif item['type'] == 'project_creation':
                print(f"   Project: {item['project_name']} ({item['platform']})")
            print()

    async def _show_help(self):
        """Show detailed help"""
        help_text = """
🤖 Embedded Systems AI Agent Help
================================

COMMANDS:
- chat: Ask questions about embedded systems, get advice, troubleshoot issues
- generate: Generate code for Arduino, ESP32, or Raspberry Pi
- project: Create complete projects with code, documentation, and file structure
- search: Search the web for tutorials, datasheets, and documentation
- knowledge: Add PDF manuals and documentation to the knowledge base
- tools: Explore available tools (component lookup, pinouts, templates)
- platform: Set default platform to avoid retyping
- history: View your session activity
- help: Show this help message
- quit: Exit the application

PLATFORMS SUPPORTED:
- Arduino (Uno, Nano, Mega, etc.)
- ESP32 (WiFi, Bluetooth, sensors)
- Raspberry Pi (GPIO, camera, I2C, SPI)

EXAMPLE WORKFLOWS:
1. Set platform → Generate code → Validate → Save
2. Add knowledge PDFs → Ask specific questions → Get context-aware answers
3. Search for components → Get pinouts → Generate integration code
4. Create complete project → Get documentation → Save everything

TIPS:
- Use specific requirements for better code generation
- Add datasheets to knowledge base for better context
- Validate code before uploading to hardware
- Save projects for future reference
"""
        print(help_text)

    async def _save_code(self, response: str, platform: str, filename: str):
        """Save generated code to file
        
        Args:
            response: AI response containing code
            platform: Target platform
            filename: Output filename
        """
        try:
            from src.utils import extract_code_from_response
            
            # Extract code from response
            code = extract_code_from_response(response)
            if not code:
                print("⚠️ No code found in response")
                return

            filepath = save_code_to_file(code, filename, platform)
            print(f"✅ Code saved to {filepath}")

        except Exception as e:
            print(f"❌ Error saving code: {e}")
