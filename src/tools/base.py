"""Base tools class for embedded systems"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.config import (
    KNOWLEDGE_BASE_DIR, EMBEDDINGS_MODEL, CHROMA_DB_PATH,
    TEXT_SPLITTER_CHUNK_SIZE, TEXT_SPLITTER_CHUNK_OVERLAP
)


class EmbeddedSystemsTools:
    """Collection of tools for embedded systems development"""

    # Supported file types - Comprehensive coverage of knowledge base
    SUPPORTED_EXTENSIONS = {
        # Documentation & Text
        '.pdf': 'PDF Document',
        '.txt': 'Text File',
        '.md': 'Markdown',
        '.adoc': 'AsciiDoc',
        
        # Code - Embedded
        '.ino': 'Arduino Code',
        '.pde': 'Processing Code',
        
        # Code - C/C++
        '.cpp': 'C++ Code',
        '.c': 'C Code',
        '.h': 'Header File',
        '.hpp': 'C++ Header',
        
        # Code - Python & Java
        '.py': 'Python Code',
        '.java': 'Java Code',
        
        # Configuration & Data
        '.json': 'JSON Data',
        '.csv': 'CSV Data',
        '.yaml': 'YAML Config',
        '.yml': 'YAML Config',
        '.properties': 'Properties Config',
        '.sh': 'Shell Script',
        
        # Exclude binary - will be skipped
        '.sb3': 'Scratch Project',
        '.jpg': 'Image',
        '.png': 'Image',
        '.svg': 'Vector Image',
        '.webm': 'Video',
        '.gz': 'Archive',
        '.tar': 'Archive',
        '.jar': 'Java Archive',
        '.fzz': 'Fritzing',
        '.vlw': 'Font',
        '.ttf': 'Font'
    }
    
    # Binary extensions that should be skipped
    SKIP_EXTENSIONS = {
        '.sb3', '.jpg', '.png', '.svg', '.webm', 
        '.gz', '.tar', '.jar', '.fzz', '.vlw', '.ttf',
        '.idx', '.pack', '.rev'  # Git objects
    }

    def __init__(self, knowledge_base_path: str = None):
        if knowledge_base_path is None:
            knowledge_base_path = str(KNOWLEDGE_BASE_DIR)
            
        self.knowledge_base_path = Path(knowledge_base_path)
        self.knowledge_base_path.mkdir(exist_ok=True)

        # Initialize embeddings and vector store
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)
            self.vectorstore = Chroma(
                persist_directory=str(CHROMA_DB_PATH),
                embedding_function=self.embeddings
            )
        except Exception as e:
            print(f"⚠️ Vector store initialization failed: {e}")
            self.vectorstore = None

        # Text splitter for documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=TEXT_SPLITTER_CHUNK_SIZE,
            chunk_overlap=TEXT_SPLITTER_CHUNK_OVERLAP
        )
        
        # Track ingested files
        self.ingested_files: Dict[str, Dict] = {}

    async def add_knowledge(self, file_path: str) -> Tuple[bool, str]:
        """Add documents to the knowledge base with source tracking
        
        Args:
            file_path: Path to document file
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False, f"File not found: {file_path}"
            
            file_ext = file_path.suffix.lower()
            
            # Check if file type is supported
            if file_ext not in self.SUPPORTED_EXTENSIONS:
                return False, f"Unsupported file type: {file_ext}"
            
            # Skip binary files
            if file_ext in self.SKIP_EXTENSIONS:
                return False, f"Binary file skipped: {file_ext}"
            
            # Load document based on file type
            documents = self._load_file(file_path)
            if not documents:
                return False, f"No content extracted from {file_path.name}"
            
            # Split into chunks with source metadata
            texts = self.text_splitter.split_documents(documents)
            
            if not texts:
                return False, f"No text chunks created from {file_path.name}"
            
            # Add source information to metadata
            for doc in texts:
                doc.metadata['source_file'] = str(file_path.name)
                doc.metadata['source_path'] = str(file_path)
                doc.metadata['file_type'] = self.SUPPORTED_EXTENSIONS[file_ext]
                doc.metadata['chunk_size'] = len(doc.page_content)

            # Add to vector store
            if self.vectorstore:
                self.vectorstore.add_documents(texts)
                
                # Track the ingested file
                self.ingested_files[str(file_path.name)] = {
                    'path': str(file_path),
                    'type': self.SUPPORTED_EXTENSIONS[file_ext],
                    'chunks': len(texts),
                    'size': file_path.stat().st_size
                }
                
                message = f"✅ Added {len(texts)} chunks from {file_path.name} ({self.SUPPORTED_EXTENSIONS[file_ext]})"
                return True, message
            else:
                return False, "Vector store not available"

        except Exception as e:
            return False, f"Error: {str(e)[:100]}"

    def _load_file(self, file_path: Path) -> Optional[List[Document]]:
        """Load file based on its extension with comprehensive support"""
        import sys
        import io
        import warnings
        
        try:
            file_ext = file_path.suffix.lower()
            
            # Skip binary and image files
            if file_ext in self.SKIP_EXTENSIONS:
                return None
            
            # Check if extension is supported
            if file_ext not in self.SUPPORTED_EXTENSIONS:
                return None
            
            # PDF - use PyPDFLoader with better error handling
            if file_ext == '.pdf':
                try:
                    # Check file size first - skip very small PDFs (likely corrupted)
                    if file_path.stat().st_size < 100:
                        return None
                    
                    # Suppress PDF parsing warnings and errors
                    warnings.filterwarnings('ignore')
                    old_stderr = sys.stderr
                    old_stdout = sys.stdout
                    sys.stderr = io.StringIO()
                    sys.stdout = io.StringIO()
                    
                    try:
                        loader = PyPDFLoader(str(file_path))
                        docs = loader.load()
                    finally:
                        # Restore stderr and stdout
                        sys.stderr = old_stderr
                        sys.stdout = old_stdout
                    
                    # Skip if no content was extracted
                    if not docs or all(len(doc.page_content.strip()) < 50 for doc in docs):
                        return None
                        
                except Exception as e:
                    # Silently skip problematic PDFs
                    return None
                
            # Text-based documentation
            elif file_ext in ['.txt', '.md', '.adoc']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Skip empty or very small files
                if len(content.strip()) < 10:
                    return None
                    
                docs = [Document(page_content=content, metadata={'source': str(file_path)})]
                
            # All code files (Arduino, Python, C++, Java, etc.)
            elif file_ext in ['.ino', '.pde', '.cpp', '.c', '.h', '.hpp', '.py', '.java', 
                             '.json', '.csv', '.yaml', '.yml', '.properties', '.sh']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Skip empty files
                if len(content.strip()) < 10:
                    return None
                    
                docs = [Document(page_content=content, metadata={'source': str(file_path)})]
                
            else:
                return None
            
            return docs if docs else None
            
        except Exception as e:
            return None  # Silent fail for unreadable files

    def search_knowledge(self, query: str, k: int = 3) -> List[Dict]:
        """Search the knowledge base with source references
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of results with content and source information
        """
        if not self.vectorstore:
            return [{"content": "Knowledge base not available", "source": "N/A"}]
        
        try:
            # Search with metadata
            docs = self.vectorstore.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs:
                result = {
                    "content": doc.page_content,
                    "source_file": doc.metadata.get('source_file', 'Unknown'),
                    "file_type": doc.metadata.get('file_type', 'Unknown'),
                    "source_path": doc.metadata.get('source_path', 'N/A'),
                    "relevance_score": f"{(1 - score):.2%}",  # Convert distance to similarity %
                    "chunk_size": doc.metadata.get('chunk_size', 'N/A')
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            return [{"content": f"Knowledge search error: {str(e)}", "source": "N/A"}]
    
    def get_ingested_files(self) -> List[Dict]:
        """Get list of ingested files with statistics"""
        return list(self.ingested_files.values())
    
    def get_file_info(self, filename: str) -> Optional[Dict]:
        """Get information about a specific ingested file"""
        return self.ingested_files.get(filename)
    
    async def ingest_directory(self, directory_path: str, recursive: bool = True) -> Tuple[int, int, List[str]]:
        """Ingest all supported files from a directory
        
        Args:
            directory_path: Path to directory
            recursive: Whether to scan subdirectories
            
        Returns:
            Tuple of (success_count, fail_count, error_messages)
        """
        dir_path = Path(directory_path)
        
        if not dir_path.exists() or not dir_path.is_dir():
            return 0, 1, [f"Directory not found: {directory_path}"]
        
        success_count = 0
        fail_count = 0
        skipped_count = 0
        errors = []
        processed_files = set()  # Track processed to avoid duplicates
        
        # Find all supported files
        if recursive:
            file_pattern = "**/*"
        else:
            file_pattern = "*"
        
        all_files = []
        for file_path in dir_path.glob(file_pattern):
            if not file_path.is_file():
                continue
            
            file_ext = file_path.suffix.lower()
            
            # Skip binary and image files
            if file_ext in self.SKIP_EXTENSIONS:
                skipped_count += 1
                continue
            
            # Skip unsupported file types
            if file_ext not in self.SUPPORTED_EXTENSIONS:
                skipped_count += 1
                continue
            
            all_files.append(file_path)
        
        # Process files with progress tracking
        total_files = len(all_files)
        
        if total_files == 0:
            return 0, 0, ["No supported files found in directory"]
        
        for idx, file_path in enumerate(all_files, 1):
            # Avoid processing same file twice
            file_id = str(file_path.resolve())
            if file_id in processed_files:
                continue
            processed_files.add(file_id)
            
            # Show progress every 50 files
            if idx % 50 == 0 or idx == total_files:
                print(f"  Processing {idx}/{total_files}...", end='\r')
            
            # Ingest the file
            success, message = await self.add_knowledge(str(file_path))
            
            if success:
                success_count += 1
            else:
                fail_count += 1
                # Only keep track of real errors, not "no content" messages
                if "No content extracted" not in message and "Binary file skipped" not in message:
                    errors.append(f"{file_path.name}: {message}")
        
        print()  # New line after progress
        return success_count, fail_count, errors
    
    def scan_directory(self, directory_path: str, recursive: bool = True) -> Dict:
        """Scan directory and report what would be ingested
        
        Args:
            directory_path: Path to directory
            recursive: Whether to scan subdirectories
            
        Returns:
            Dict with statistics
        """
        dir_path = Path(directory_path)
        
        if not dir_path.exists():
            return {"error": f"Directory not found: {directory_path}"}
        
        stats = {
            "directory": str(dir_path),
            "files_by_type": {},
            "total_files": 0,
            "total_size_mb": 0,
            "tree": {}
        }
        
        if recursive:
            file_pattern = "**/*"
        else:
            file_pattern = "*"
        
        for file_path in dir_path.glob(file_pattern):
            if not file_path.is_file():
                continue
            
            file_ext = file_path.suffix.lower()
            
            # Skip unsupported and binary files
            if file_ext not in self.SUPPORTED_EXTENSIONS or file_ext == '.sb3':
                continue
            
            file_type = self.SUPPORTED_EXTENSIONS[file_ext]
            size_mb = file_path.stat().st_size / (1024 * 1024)
            
            # Update stats
            if file_type not in stats["files_by_type"]:
                stats["files_by_type"][file_type] = {"count": 0, "size_mb": 0}
            
            stats["files_by_type"][file_type]["count"] += 1
            stats["files_by_type"][file_type]["size_mb"] += size_mb
            stats["total_files"] += 1
            stats["total_size_mb"] += size_mb
        
        return stats
