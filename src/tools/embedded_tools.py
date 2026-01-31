"""Tool definitions using LangChain's @tool decorator"""

from typing import Dict, List
from langchain_core.tools import tool
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

from src.config import (
    COMPONENT_DB, PINOUTS, CODE_TEMPLATES, LIBRARY_DATABASE, WEB_SEARCH_MAX_RESULTS
)

# Check if web search is available
try:
    DDGS()
    WEB_SEARCH_AVAILABLE = True
except Exception:
    WEB_SEARCH_AVAILABLE = False


@tool
def web_search_tool(query: str, max_results: int = WEB_SEARCH_MAX_RESULTS) -> str:
    """Search the web for embedded systems information, tutorials, and documentation"""
    if not WEB_SEARCH_AVAILABLE:
        return "Web search not available. Please install duckduckgo-search package."

    try:
        ddgs = DDGS()
        results = []
        enhanced_query = f"{query} embedded systems arduino esp32 raspberry pi"

        search_results = ddgs.text(enhanced_query, max_results=max_results)

        for result in search_results:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })

        # Format results as string
        formatted_results = "🔍 Web Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. **{result['title']}**\n"
            formatted_results += f"   URL: {result['url']}\n"
            formatted_results += f"   {result['snippet'][:200]}...\n\n"

        return formatted_results

    except Exception as e:
        return f"Web search failed: {str(e)}"


@tool
def component_lookup_tool(component_name: str) -> str:
    """Look up information about electronic components, sensors, and modules"""
    component_key = component_name.lower().replace("-", "").replace(" ", "")

    # Find matching component
    for key, info in COMPONENT_DB.items():
        if component_key in key or component_name.lower() in info["type"].lower():
            result = f"🔌 **{info['type']}**\n\n"
            result += f"**Description:** {info['description']}\n"
            result += f"**Voltage:** {info['voltage']}\n"
            result += f"**Pins:** {', '.join(info['pins'])}\n"

            if 'libraries' in info:
                result += f"**Libraries:** {', '.join(info['libraries'])}\n"

            if 'arduino_code' in info:
                result += f"\n**Arduino Code:**\n```cpp\n{info['arduino_code']}\n```\n"

            if 'raspberry_pi_code' in info:
                result += f"\n**Raspberry Pi Code:**\n```python\n{info['raspberry_pi_code']}\n```\n"

            return result

    return f"❌ Component '{component_name}' not found in database. Try: DHT22, HC-SR04, LED"


@tool
def pinout_lookup_tool(platform: str) -> str:
    """Get detailed pinout information for microcontrollers and development boards"""
    platform_key = platform.lower().replace("-", "_").replace(" ", "_")

    if platform_key in PINOUTS:
        info = PINOUTS[platform_key]
        result = f"📌 **{info['description']}**\n\n"

        if 'digital_pins' in info:
            result += f"**Digital Pins:** {info['digital_pins']}\n"
        if 'analog_pins' in info:
            result += f"**Analog Pins:** {info['analog_pins']}\n"
        if 'power_pins' in info:
            result += f"**Power Pins:** {info['power_pins']}\n"
        if 'pwm_pins' in info:
            result += f"**PWM Pins:** {info['pwm_pins']}\n"
        if 'touch_pins' in info:
            result += f"**Touch Pins:** {info['touch_pins']}\n"

        result += f"\n**Special Functions:**\n"
        for func, pin in info['special_pins'].items():
            result += f"- {func}: {pin}\n"

        result += f"\n**Important Notes:**\n{info['notes']}"

        return result
    else:
        available = list(PINOUTS.keys())
        return f"❌ Pinout for '{platform}' not found. Available: {', '.join(available)}"


@tool
def code_template_tool(platform: str, template_type: str) -> str:
    """Get code templates for different platforms and use cases"""
    platform_key = platform.lower()
    template_key = template_type.lower()

    if platform_key in CODE_TEMPLATES:
        if template_key in CODE_TEMPLATES[platform_key]:
            template_code = CODE_TEMPLATES[platform_key][template_key]
            lang = "cpp" if platform_key in ["arduino", "esp32"] else "python"
            return f"📝 **{platform.title()} {template_type.title()} Template**\n\n```{lang}\n{template_code.strip()}\n```"
        else:
            available = list(CODE_TEMPLATES[platform_key].keys())
            return f"❌ Template '{template_type}' not found for {platform}. Available: {', '.join(available)}"
    else:
        available = list(CODE_TEMPLATES.keys())
        return f"❌ Platform '{platform}' not supported. Available: {', '.join(available)}"


@tool
def code_validator_tool(code: str, platform: str) -> Dict:
    """Validate code syntax and structure for embedded platforms"""
    try:
        validation_result = {
            "success": True,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }

        if platform.lower() in ["arduino", "esp32"]:
            # Arduino/ESP32 C++ validation
            if "setup()" not in code:
                validation_result["errors"].append("Missing required setup() function")

            if "loop()" not in code and platform.lower() != "library":
                validation_result["errors"].append("Missing required loop() function")

            # Check for common issues
            if "Serial.begin" in code and "Serial.h" not in code and "#include <Arduino.h>" not in code:
                validation_result["warnings"].append("Using Serial without including Arduino.h")

            # Check for WiFi usage without include
            if "WiFi." in code and "#include <WiFi.h>" not in code:
                validation_result["errors"].append("Using WiFi functions without including WiFi.h")

        elif platform.lower() == "raspberry_pi":
            # Python validation
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError as e:
                validation_result["errors"].append(f"Python syntax error: {str(e)}")

            # Check for GPIO usage
            if "GPIO." in code and "import RPi.GPIO" not in code:
                validation_result["warnings"].append("Using GPIO without importing RPi.GPIO")

            if "GPIO.cleanup()" not in code and "GPIO." in code:
                validation_result["suggestions"].append("Consider adding GPIO.cleanup() for proper resource cleanup")

        # General checks
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line.strip()) > 120:
                validation_result["warnings"].append(f"Line {i} is very long (>120 chars)")

        if validation_result["errors"]:
            validation_result["success"] = False

        return validation_result

    except Exception as e:
        return {"success": False, "error": f"Validation failed: {str(e)}"}


@tool
def library_lookup_tool(library_name: str, platform: str) -> Dict:
    """Look up library information and installation instructions"""
    platform_libs = LIBRARY_DATABASE.get(platform.lower(), {})
    lib_key = library_name.lower().replace("-", "").replace("_", "").replace(".", "")

    for key, info in platform_libs.items():
        if lib_key in key or library_name.lower() in info["name"].lower():
            return {"success": True, "library": info}

    return {"error": f"Library '{library_name}' not found for platform '{platform}'"}


@tool
def file_operations_tool(operation: str, file_path: str, content: str = "") -> Dict:
    """Perform file operations like read, write, create directories"""
    from pathlib import Path
    
    try:
        path = Path(file_path)

        if operation == "read":
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return {"success": True, "content": f.read()}
            else:
                return {"error": f"File {file_path} not found"}

        elif operation == "write":
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "message": f"File written to {file_path}"}

        elif operation == "create_dir":
            path.mkdir(parents=True, exist_ok=True)
            return {"success": True, "message": f"Directory created: {file_path}"}

        elif operation == "list":
            if path.exists() and path.is_dir():
                files = [str(f) for f in path.iterdir()]
                return {"success": True, "files": files}
            else:
                return {"error": f"Directory {file_path} not found"}

        else:
            return {"error": f"Unknown operation: {operation}"}

    except Exception as e:
        return {"error": f"File operation failed: {str(e)}"}
