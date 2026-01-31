"""Reusable Streamlit components"""

import streamlit as st
from typing import Dict, List, Optional


def render_sidebar_menu() -> str:
    """Render sidebar menu and return selected option"""
    with st.sidebar:
        st.title("🤖 Embedded Agent")
        st.divider()
        
        option = st.radio(
            "Select an option:",
            options=[
                "💬 Chat",
                "⚡ Generate Code",
                "🏗️ Create Project",
                "🔍 Search",
                "🔌 Component Lookup",
                "📌 Pinout Information",
                "📚 Manage Knowledge",
                "ℹ️ About"
            ],
            label_visibility="collapsed"
        )
        
        st.divider()
        st.subheader("Platform")
        platform = st.selectbox(
            "Select Platform:",
            options=["Arduino", "ESP32", "Raspberry Pi"],
            label_visibility="collapsed"
        )
        
        return option, platform.lower().replace(" ", "_")


def render_code_display(code: str, language: str = "cpp") -> None:
    """Display code with syntax highlighting"""
    st.code(code, language=language, line_numbers=True)


def render_validation_results(results: Dict) -> None:
    """Display code validation results"""
    if not results:
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if results.get("success"):
            st.success("✅ Valid Code")
        else:
            st.error("❌ Invalid Code")
    
    with col2:
        errors = results.get("errors", [])
        if errors:
            st.error(f"Errors: {len(errors)}")
    
    with col3:
        warnings = results.get("warnings", [])
        if warnings:
            st.warning(f"Warnings: {len(warnings)}")
    
    if results.get("errors"):
        with st.expander("🔴 Errors"):
            for error in results["errors"]:
                st.error(f"• {error}")
    
    if results.get("warnings"):
        with st.expander("🟡 Warnings"):
            for warning in results["warnings"]:
                st.warning(f"• {warning}")
    
    if results.get("suggestions"):
        with st.expander("💡 Suggestions"):
            for suggestion in results["suggestions"]:
                st.info(f"• {suggestion}")


def render_component_info(component_info: Dict) -> None:
    """Display component information"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Type", component_info.get("type", "Unknown"))
        st.metric("Voltage", component_info.get("voltage", "Unknown"))
    
    with col2:
        if "pins" in component_info:
            st.write("**Pins:**")
            for pin in component_info["pins"]:
                st.text(f"  • {pin}")
    
    if "libraries" in component_info:
        with st.expander("📚 Libraries"):
            for lib in component_info["libraries"]:
                st.text(f"• {lib}")
    
    if "arduino_code" in component_info:
        with st.expander("Arduino Code"):
            render_code_display(component_info["arduino_code"], "cpp")
    
    if "raspberry_pi_code" in component_info:
        with st.expander("Raspberry Pi Code"):
            render_code_display(component_info["raspberry_pi_code"], "python")


def render_pinout_info(pinout_info: Dict) -> None:
    """Display pinout information"""
    st.subheader(pinout_info.get("description", "Pinout"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        if "digital_pins" in pinout_info:
            st.write("**Digital Pins:**")
            st.code(pinout_info["digital_pins"], language="text")
        
        if "analog_pins" in pinout_info:
            st.write("**Analog Pins:**")
            st.code(pinout_info["analog_pins"], language="text")
    
    with col2:
        if "power_pins" in pinout_info:
            st.write("**Power Pins:**")
            st.code(pinout_info["power_pins"], language="text")
        
        if "pwm_pins" in pinout_info:
            st.write("**PWM Pins:**")
            st.code(pinout_info["pwm_pins"], language="text")
    
    if "special_pins" in pinout_info:
        with st.expander("Special Functions"):
            for func, pin in pinout_info["special_pins"].items():
                st.text(f"**{func}**: {pin}")
    
    if "notes" in pinout_info:
        st.info(pinout_info["notes"])


def render_search_results(results: str) -> None:
    """Display web search results"""
    st.markdown(results)


def render_project_summary(project_info: Dict) -> None:
    """Display generated project summary"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Platform", project_info.get("platform", "Unknown"))
        st.metric("Code Generated", "✅ Yes" if project_info.get("code_generated") else "❌ No")
    
    with col2:
        st.metric("Documentation", "✅ Yes" if project_info.get("documentation_generated") else "❌ No")
        
    st.success(f"Project created at: `{project_info.get('project_path')}`")
    
    if project_info.get("files_created"):
        with st.expander("Files Created"):
            for file in project_info["files_created"]:
                st.text(f"📄 {file}")


def render_loading_spinner(message: str = "Processing...") -> None:
    """Display loading spinner with message"""
    with st.spinner(f"🔄 {message}"):
        pass


def render_session_history(history: List[Dict]) -> None:
    """Display session history"""
    if not history:
        st.info("No history yet")
        return
    
    st.subheader(f"📝 Session History ({len(history)} items)")
    
    for i, item in enumerate(reversed(history[-10:]), 1):
        with st.expander(f"{i}. {item.get('type', 'Unknown').replace('_', ' ').title()}"):
            if item["type"] == "chat":
                st.write(f"**Question:** {item['question']}")
                st.write(f"**Response:** {item['response'][:200]}...")
            elif item["type"] == "code_generation":
                st.write(f"**Platform:** {item['platform']}")
                st.write(f"**Requirements:** {item['requirements']}")
            elif item["type"] == "project_creation":
                st.write(f"**Project:** {item['project_name']}")
                st.write(f"**Platform:** {item['platform']}")
            
            st.caption(f"Time: {item.get('timestamp', 'Unknown')}")


def render_error_message(error: str) -> None:
    """Display error message"""
    st.error(f"❌ Error: {error}")


def render_success_message(message: str) -> None:
    """Display success message"""
    st.success(f"✅ {message}")


def render_info_message(message: str) -> None:
    """Display info message"""
    st.info(f"ℹ️ {message}")


def render_warning_message(message: str) -> None:
    """Display warning message"""
    st.warning(f"⚠️ {message}")


def render_source_references(search_results: List[Dict]) -> None:
    """Display search results with source references"""
    if not search_results:
        st.info("No results found")
        return
    
    st.subheader("📚 Knowledge Base Results")
    
    for i, result in enumerate(search_results, 1):
        with st.expander(f"📄 Result {i} - {result.get('source_file', 'Unknown')} ({result.get('relevance_score', 'N/A')})"):
            # Content
            st.write("**Content:**")
            st.text(result.get('content', 'N/A')[:500] + "..." if len(result.get('content', '')) > 500 else result.get('content', 'N/A'))
            
            # Metadata
            st.divider()
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("File Type", result.get('file_type', 'N/A'))
            with col2:
                st.metric("Relevance", result.get('relevance_score', 'N/A'))
            with col3:
                st.metric("Chunk Size", f"{result.get('chunk_size', 'N/A')} chars")
            with col4:
                st.metric("Source", result.get('source_file', 'N/A'))
            
            # Full path
            st.caption(f"📍 Path: `{result.get('source_path', 'N/A')}`")


def render_ingested_files(files: List[Dict]) -> None:
    """Display list of ingested files with statistics"""
    if not files:
        st.info("No files ingested yet")
        return
    
    st.subheader("📂 Ingested Files")
    
    for file_info in files:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("File", file_info.get('path', 'N/A').split('/')[-1])
        with col2:
            st.metric("Type", file_info.get('type', 'N/A'))
        with col3:
            st.metric("Chunks", file_info.get('chunks', 0))
