"""File operation utilities"""

from pathlib import Path
from typing import Dict, Optional


def read_file(file_path: str) -> Optional[str]:
    """Read file contents
    
    Args:
        file_path: Path to file
        
    Returns:
        File contents or None if error
    """
    try:
        path = Path(file_path)
        if path.exists():
            return path.read_text(encoding='utf-8')
        else:
            return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def write_file(file_path: str, content: str) -> bool:
    """Write content to file
    
    Args:
        file_path: Path to file
        content: Content to write
        
    Returns:
        True if successful
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False


def create_directory(dir_path: str) -> bool:
    """Create directory
    
    Args:
        dir_path: Path to directory
        
    Returns:
        True if successful
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory: {e}")
        return False


def list_directory(dir_path: str) -> Dict:
    """List directory contents
    
    Args:
        dir_path: Path to directory
        
    Returns:
        Dictionary with success status and file list
    """
    try:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            files = [str(f) for f in path.iterdir()]
            return {"success": True, "files": files}
        else:
            return {"error": f"Directory {dir_path} not found"}
    except Exception as e:
        return {"error": f"Error listing directory: {str(e)}"}
