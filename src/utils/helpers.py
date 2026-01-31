"""Utility functions for file operations and code extraction"""

import re
from pathlib import Path
from typing import Optional


def extract_code_from_response(response: str) -> str:
    """Extract code blocks from AI response
    
    Args:
        response: AI response text containing code blocks
        
    Returns:
        Extracted code string
    """
    # Look for code blocks
    code_patterns = [
        r'```(?:cpp|c\+\+|arduino|ino)\n(.*?)```',
        r'```python\n(.*?)```',
        r'```\n(.*?)```'
    ]

    for pattern in code_patterns:
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            return matches[0].strip()

    # If no code blocks found, look for code-like content
    lines = response.split('\n')
    code_lines = []
    in_code = False

    for line in lines:
        # Detect code by common patterns
        if any(keyword in line for keyword in ['#include', 'void setup', 'void loop', 'import ', 'def ', 'if __name__']):
            in_code = True

        if in_code:
            code_lines.append(line)

        # Stop at explanation or other sections
        if line.lower().startswith(('explanation:', 'components:', 'setup:')):
            break

    return '\n'.join(code_lines).strip()


def save_code_to_file(code: str, filename: str, platform: str) -> Path:
    """Save generated code to a file
    
    Args:
        code: Code content to save
        filename: Name of the file (without extension)
        platform: Platform type (arduino, esp32, raspberry_pi)
        
    Returns:
        Path to the saved file
    """
    # Determine file extension
    if platform in ["arduino", "esp32"]:
        extension = ".ino"
    else:
        extension = ".py"

    filepath = Path(filename).with_suffix(extension)

    filepath.write_text(code, encoding='utf-8')
    return filepath


def validate_platform(platform: str) -> bool:
    """Validate if platform is supported
    
    Args:
        platform: Platform name
        
    Returns:
        True if platform is valid
    """
    valid_platforms = ["arduino", "esp32", "raspberry_pi"]
    return platform.lower() in valid_platforms
