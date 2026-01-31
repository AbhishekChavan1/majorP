"""Streamlit UI for Embedded Systems AI Agent"""

import os
import asyncio
import streamlit as st
from datetime import datetime
from pathlib import Path

from src.agent import EmbeddedSystemsAgent
from src.utils import extract_code_from_response
from src.ui.components import (
    render_sidebar_menu,
    render_code_display,
    render_validation_results,
    render_component_info,
    render_pinout_info,
    render_search_results,
    render_project_summary,
    render_session_history,
    render_error_message,
    render_success_message,
    render_info_message,
)


# Helper function to build directory tree
def _build_tree(path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> str:
    """Build a text representation of directory structure"""
    if current_depth >= max_depth:
        return ""
    
    tree = ""
    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'chroma_db', '.sb3_cache'}
        items = [item for item in items if item.name not in skip_dirs]
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            next_prefix = "    " if is_last else "│   "
            
            if item.is_dir():
                tree += f"{prefix}{current_prefix}📁 {item.name}/\n"
                tree += _build_tree(item, prefix + next_prefix, max_depth, current_depth + 1)
            else:
                # Show file with extension icon
                ext = item.suffix.lower()
                if ext == '.py':
                    icon = "🐍"
                elif ext == '.ino':
                    icon = "🔧"
                elif ext == '.md':
                    icon = "📝"
                elif ext == '.adoc':
                    icon = "📄"
                elif ext == '.pdf':
                    icon = "📕"
                elif ext == '.json':
                    icon = "🗂️"
                elif ext in ['.yaml', '.yml']:
                    icon = "⚙️"
                else:
                    icon = "📄"
                
                tree += f"{prefix}{current_prefix}{icon} {item.name}\n"
    except PermissionError:
        tree += f"{prefix}(Permission Denied)\n"
    
    return tree

# Page configuration
st.set_page_config(
    page_title="Embedded Systems AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_agent() -> EmbeddedSystemsAgent:
    """Get or create agent instance with auto-ingestion"""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("❌ GROQ_API_KEY environment variable not set")
        st.stop()
    
    # Initialize with auto-ingest enabled (happens on first load)
    return EmbeddedSystemsAgent(groq_api_key, auto_ingest=True)


def initialize_session_state():
    """Initialize session state variables"""
    if "session_history" not in st.session_state:
        st.session_state.session_history = []
    
    if "generated_code" not in st.session_state:
        st.session_state.generated_code = ""
    
    if "last_response" not in st.session_state:
        st.session_state.last_response = ""


def add_to_history(item_type: str, **kwargs):
    """Add item to session history"""
    history_item = {
        "type": item_type,
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }
    st.session_state.session_history.append(history_item)


async def handle_chat(agent: EmbeddedSystemsAgent, question: str, platform: str):
    """Handle chat interaction"""
    with st.spinner("🤔 Thinking..."):
        result = await agent.process_request(question, platform)
    
    if result["success"]:
        st.session_state.last_response = result["response"]
        render_success_message("Response received")
        
        st.markdown(result["response"])
        
        # Display sources if available
        if result.get("sources"):
            with st.expander("📚 Sources Referenced"):
                for src in result["sources"]:
                    st.markdown(f"- **{src['file']}** ({src['type']}) - Relevance: {src['relevance']}")
        
        add_to_history(
            "chat",
            question=question,
            response=result["response"][:100] + "..." if len(result["response"]) > 100 else result["response"]
        )
    else:
        render_error_message(result["error"])


async def handle_code_generation(agent: EmbeddedSystemsAgent, requirements: str, platform: str):
    """Handle code generation"""
    with st.spinner("⚡ Generating code..."):
        request = f"Generate {platform} code for: {requirements}"
        result = await agent.process_request(request, platform)
    
    if result["success"]:
        st.session_state.generated_code = result["response"]
        render_success_message("Code generated successfully")
        
        st.subheader("Generated Code")
        language = "cpp" if platform in ["arduino", "esp32"] else "python"
        render_code_display(result["response"], language)
        
        # Display sources
        if result.get("sources"):
            with st.expander("📚 References Used"):
                for src in result["sources"]:
                    st.markdown(f"- **{src['file']}** ({src['type']}) - Relevance: {src['relevance']}")
        
        # Code validation
        code_content = extract_code_from_response(result["response"])
        if code_content:
            st.subheader("Code Validation")
            from src.tools.embedded_tools import code_validator_tool
            validation_result = code_validator_tool.invoke({"code": code_content, "platform": platform})
            render_validation_results(validation_result)
        
        # Download option
        ext = ".ino" if platform in ["arduino", "esp32"] else ".py"
        st.download_button(
            label="⬇️ Download Code",
            data=code_content if code_content else result["response"],
            file_name=f"generated_code{ext}",
            mime="text/plain"
        )
        
        add_to_history(
            "code_generation",
            platform=platform,
            requirements=requirements
        )
    else:
        render_error_message(result["error"])


async def handle_project_generation(agent: EmbeddedSystemsAgent, project_name: str, requirements: str, platform: str):
    """Handle project generation"""
    if not project_name or not requirements:
        render_error_message("Project name and requirements are required")
        return
    
    with st.spinner("🏗️ Creating project..."):
        result = await agent.generate_project(platform, requirements, project_name)
    
    if result["success"]:
        render_success_message(f"Project '{project_name}' created successfully!")
        render_project_summary(result)
        
        add_to_history(
            "project_creation",
            project_name=project_name,
            platform=platform
        )
    else:
        render_error_message(result["error"])


async def handle_web_search(agent: EmbeddedSystemsAgent, query: str):
    """Handle web search"""
    from src.tools.embedded_tools import web_search_tool
    
    with st.spinner("🔍 Searching web..."):
        try:
            result = web_search_tool.invoke({"query": query, "max_results": 5})
            st.subheader("🌐 Web Search Results")
            st.markdown(result)
        except Exception as e:
            render_error_message(f"Search failed: {str(e)}")


def handle_component_lookup(component_name: str):
    """Handle component lookup"""
    from src.tools.embedded_tools import component_lookup_tool
    
    with st.spinner(f"🔍 Looking up {component_name}..."):
        result = component_lookup_tool.invoke({"component_name": component_name})
    
    if "❌" not in result:
        st.markdown(result)
    else:
        render_error_message(result)


def handle_pinout_lookup(platform: str):
    """Handle pinout lookup"""
    from src.tools.embedded_tools import pinout_lookup_tool
    
    with st.spinner(f"📌 Getting pinout for {platform}..."):
        result = pinout_lookup_tool.invoke({"platform": platform})
    
    if "❌" not in result:
        st.markdown(result)
    else:
        render_error_message(result)


async def handle_knowledge_upload(agent: EmbeddedSystemsAgent, uploaded_file):
    """Handle knowledge base upload with source tracking"""
    import tempfile
    from pathlib import Path
    
    if uploaded_file is None:
        return
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name
        
        with st.spinner("📚 Adding to knowledge base..."):
            result = await agent.add_knowledge(tmp_path)
        
        if result.get("success"):
            render_success_message(result.get("message", f"Added {uploaded_file.name}"))
        else:
            render_error_message(result.get("message", f"Failed to add {uploaded_file.name}"))
        
        # Clean up
        Path(tmp_path).unlink()
    
    except Exception as e:
        render_error_message(f"Error uploading file: {str(e)}")


def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Render sidebar
    option, platform = render_sidebar_menu()
    
    # Main content area
    st.title("🤖 Embedded Systems AI Agent")
    st.markdown("Generate code, manage projects, and get expert advice for embedded systems development")
    
    # Route to appropriate handler
    agent = get_agent()
    
    if option == "💬 Chat":
        st.header("💬 Chat")
        st.markdown("Ask questions about embedded systems, get advice, and learn new concepts")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            question = st.text_area("Ask me anything:", placeholder="e.g., How do I read a DHT22 sensor?")
        with col2:
            st.markdown("")
            submit = st.button("Send 📤", use_container_width=True)
        
        if submit and question:
            asyncio.run(handle_chat(agent, question, platform))
    
    elif option == "⚡ Generate Code":
        st.header("⚡ Generate Code")
        st.markdown(f"Generate code for **{platform.replace('_', ' ').title()}**")
        
        requirements = st.text_area(
            "Describe what you want to build:",
            placeholder="e.g., A weather station that reads temperature and humidity from a DHT22 sensor"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.button("Generate 🚀", use_container_width=True)
        
        if submit and requirements:
            asyncio.run(handle_code_generation(agent, requirements, platform))
    
    elif option == "🏗️ Create Project":
        st.header("🏗️ Create Project")
        st.markdown("Create a complete project with code, documentation, and file structure")
        
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("Project name:", placeholder="my_awesome_project")
        with col2:
            platform_select = st.selectbox("Platform:", options=["Arduino", "ESP32", "Raspberry Pi"])
        
        requirements = st.text_area(
            "Project requirements:",
            placeholder="Describe your project in detail"
        )
        
        if st.button("Create Project 🏗️", use_container_width=True):
            asyncio.run(handle_project_generation(
                agent,
                project_name,
                requirements,
                platform_select.lower().replace(" ", "_")
            ))
    
    elif option == "🔍 Search":
        st.header("🔍 Search")
        st.markdown("Search the web for embedded systems information, tutorials, and documentation")
        
        query = st.text_input(
            "Search query:",
            placeholder="e.g., Arduino WiFi shield tutorial"
        )
        
        if st.button("Search 🔎", use_container_width=True) and query:
            asyncio.run(handle_web_search(agent, query))
    
    elif option == "🔌 Component Lookup":
        st.header("🔌 Component Lookup")
        st.markdown("Look up information about electronic components and sensors")
        
        component = st.selectbox(
            "Select a component:",
            options=["DHT22", "HC-SR04", "LED", "Other"]
        )
        
        if component == "Other":
            component = st.text_input("Enter component name:")
        
        if st.button("Look Up 🔍", use_container_width=True) and component:
            handle_component_lookup(component)
    
    elif option == "📌 Pinout Information":
        st.header("📌 Pinout Information")
        st.markdown("Get detailed pinout information for microcontrollers and development boards")
        
        pinout = st.selectbox(
            "Select platform:",
            options=["Arduino UNO", "ESP32", "Raspberry Pi"]
        )
        
        if st.button("Get Pinout 📌", use_container_width=True):
            pinout_key = {
                "Arduino UNO": "arduino_uno",
                "ESP32": "esp32",
                "Raspberry Pi": "raspberry_pi"
            }[pinout]
            handle_pinout_lookup(pinout_key)
    
    elif option == "📚 Manage Knowledge":
        st.header("📚 Manage Knowledge Base")
        st.markdown("Add documents to enhance the agent with your knowledge")
        
        kb_tab1, kb_tab2, kb_tab3, kb_tab4 = st.tabs(["Upload Files", "Search Knowledge", "View Files", "Bulk Ingest"])
        
        with kb_tab1:
            st.markdown("**Supported formats:** PDF, TXT, Markdown, AsciiDoc, Python, Arduino, C++, JSON, YAML, CSV")
            
            uploaded_file = st.file_uploader(
                "Upload a document:",
                type=["pdf", "txt", "md", "adoc", "py", "ino", "cpp", "h", "json", "yaml", "yml", "csv"],
                help="Datasheets, documentation, code, or config files"
            )
            
            if uploaded_file is not None:
                if st.button("Add to Knowledge Base 📚", use_container_width=True):
                    asyncio.run(handle_knowledge_upload(agent, uploaded_file))
        
        with kb_tab2:
            st.subheader("Search Knowledge Base")
            search_query = st.text_input("Enter search query:", placeholder="e.g., DHT22 sensor wiring")
            
            if search_query and st.button("Search 🔍", use_container_width=True):
                with st.spinner("Searching knowledge base..."):
                    results = agent.tools_instance.search_knowledge(search_query, k=3)
                    from src.ui.components import render_source_references
                    render_source_references(results)
        
        with kb_tab3:
            st.subheader("Ingested Files")
            files = agent.tools_instance.get_ingested_files()
            
            if files:
                from src.ui.components import render_ingested_files
                render_ingested_files(files)
                
                st.divider()
                st.metric("Total Files", len(files))
                st.metric("Total Chunks", sum(f.get('chunks', 0) for f in files))
            else:
                st.info("No files ingested yet. Upload files in the 'Upload Files' tab.")
        
        with kb_tab4:
            st.subheader("📂 Bulk Ingest Knowledge Base")
            st.markdown("""
            Automatically ingest all supported files from the knowledge_base directory.
            
            **This will scan and process:**
            - Arduino sketches (.ino)
            - Python files (.py)
            - C++ code (.cpp, .h)
            - Documentation (.md, .adoc, .txt)
            - Configuration files (.json, .yaml, .csv)
            - PDF datasheets
            """)
            
            # Scan button
            if st.button("📊 Scan Knowledge Base", use_container_width=True):
                with st.spinner("Scanning knowledge_base directory..."):
                    scan_results = agent.scan_knowledge_base()
                    
                    if "error" in scan_results:
                        st.error(f"❌ {scan_results['error']}")
                    else:
                        st.success("✅ Scan Complete")
                        
                        st.write(f"📁 Directory: `{scan_results['directory']}`")
                        st.write(f"📄 Total Files Found: **{scan_results['total_files']}**")
                        st.write(f"💾 Total Size: **{scan_results['total_size_mb']:.2f} MB**")
                        
                        if scan_results['files_by_type']:
                            st.subheader("Files by Type")
                            
                            cols = st.columns(3)
                            for idx, (file_type, stats) in enumerate(scan_results['files_by_type'].items()):
                                with cols[idx % 3]:
                                    st.metric(
                                        file_type,
                                        f"{stats['count']} files",
                                        f"{stats['size_mb']:.2f} MB"
                                    )
            
            st.divider()
            
            # Ingest button
            ingest_col1, ingest_col2 = st.columns(2)
            
            with ingest_col1:
                if st.button("🚀 Start Bulk Ingest", use_container_width=True, type="primary"):
                    with st.spinner("Ingesting all files from knowledge_base..."):
                        ingest_results = asyncio.run(agent.ingest_knowledge_base())
                        
                        if ingest_results["success"]:
                            st.success(f"✅ {ingest_results['message']}")
                            st.metric("✅ Successfully Ingested", ingest_results['success_count'])
                        else:
                            st.warning(f"⚠️ {ingest_results['message']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("✅ Successful", ingest_results['success_count'])
                            with col2:
                                st.metric("❌ Failed", ingest_results['fail_count'])
                            
                            if ingest_results['errors']:
                                st.subheader("Errors")
                                for error in ingest_results['errors'][:5]:
                                    st.error(error)
                                if len(ingest_results['errors']) > 5:
                                    st.info(f"... and {len(ingest_results['errors']) - 5} more errors")
            
            with ingest_col2:
                if st.button("ℹ️ View Structure", use_container_width=True):
                    with st.spinner("Loading knowledge base structure..."):
                        from pathlib import Path
                        from src.config import KNOWLEDGE_BASE_DIR
                        
                        structure = _build_tree(KNOWLEDGE_BASE_DIR, max_depth=3)
                        st.text(structure)
    
    elif option == "ℹ️ About":
        st.header("ℹ️ About")
        st.markdown("""
        ### Embedded Systems AI Agent
        
        A powerful AI-driven tool for embedded systems development with support for:
        - **Arduino** (Uno, Nano, Mega, etc.)
        - **ESP32** (WiFi, Bluetooth, IoT)
        - **Raspberry Pi** (GPIO, sensors, cameras)
        
        #### Features
        - 💬 **Chat**: Ask questions and get expert advice
        - ⚡ **Code Generation**: Generate production-ready code
        - 🏗️ **Project Creation**: Generate complete projects with documentation
        - 🔍 **Web Search**: Search for tutorials and documentation
        - 🔌 **Component Lookup**: Information about sensors and modules
        - 📌 **Pinout Information**: Detailed pinout for all platforms
        - 📚 **Knowledge Management**: Add custom documentation
        
        #### Technologies
        - **LangChain**: LLM framework
        - **LangGraph**: Workflow orchestration
        - **Groq**: Fast LLM inference
        - **Streamlit**: Web UI
        - **Chroma**: Vector database
        
        #### Getting Started
        1. Set your GROQ_API_KEY environment variable
        2. Install dependencies: `pip install -r requirements.txt`
        3. Run: `streamlit run src/ui/streamlit_app.py`
        
        #### Documentation
        - 📖 [README.md](https://github.com/yourrepo) - Full documentation
        - 🚀 [QUICKSTART.md](https://github.com/yourrepo) - Getting started guide
        - 🏗️ [ARCHITECTURE.md](https://github.com/yourrepo) - System architecture
        """)
    
    # Sidebar: Session history
    with st.sidebar:
        st.divider()
        if st.session_state.session_history:
            with st.expander("📝 Session History"):
                render_session_history(st.session_state.session_history)


if __name__ == "__main__":
    main()
