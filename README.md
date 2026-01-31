# 🤖 Embedded Systems AI Agent

An intelligent AI-powered assistant for embedded systems development, specializing in Arduino, ESP32, and Raspberry Pi projects. Built with LangGraph, LangChain, and Groq LLM.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://python.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## ✨ Features

### 🎯 Core Capabilities
- **💬 Intelligent Chat** - Natural language conversations about embedded systems
- **⚡ Code Generation** - Generate production-ready code for multiple platforms
- **🏗️ Project Creation** - Complete project scaffolding with documentation
- **🔍 Web Search** - Real-time search for tutorials and documentation
- **🔌 Component Lookup** - Detailed information about sensors and modules
- **📌 Pinout Information** - Interactive pinout diagrams and specifications
- **📚 Knowledge Management** - RAG-based knowledge base with vector search

### 🛠️ Supported Platforms
- **Arduino** (Uno, Nano, Mega)
- **ESP32** (WiFi, Bluetooth, IoT)
- **Raspberry Pi** (GPIO, sensors, cameras)

### 🧠 AI Technologies
- **LangGraph** - Agentic workflow orchestration
- **LangChain** - LLM framework and tool integration
- **Groq** - Ultra-fast LLM inference
- **ChromaDB** - Vector database for knowledge retrieval
- **HuggingFace Embeddings** - Semantic search

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- GROQ API Key ([Get it here](https://console.groq.com/))
- Docker (optional, for containerized deployment)

### Installation

#### Option 1: Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AbhishekChavan1/majorP.git
   cd majorP
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   # Windows (PowerShell)
   $env:GROQ_API_KEY="your_groq_api_key_here"
   
   # Linux/Mac
   export GROQ_API_KEY="your_groq_api_key_here"
   ```

5. **Run the application:**
   ```bash
   python run_ui.py
   ```

6. **Access the UI:**
   Open your browser at `http://localhost:8501`

#### Option 2: Docker Deployment

1. **Create `.env` file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

2. **Run with Docker Compose:**
   ```bash
   # Windows
   docker-run.bat
   
   # Linux/Mac
   chmod +x docker-run.sh
   ./docker-run.sh
   
   # Or manually
   docker-compose up -d
   ```

3. **Access the application:**
   `http://localhost:8501`

See [DOCKER.md](DOCKER.md) for detailed Docker documentation.

## 📖 Usage Guide

### 1. Chat Mode
Ask questions about embedded systems, get code suggestions, and troubleshooting help.

**Example queries:**
- "How do I read a DHT22 sensor with Arduino?"
- "Explain I2C communication on ESP32"
- "What pins can I use for PWM on Raspberry Pi?"

### 2. Code Generation
Generate complete, working code for your projects.

**Steps:**
1. Select platform (Arduino/ESP32/Raspberry Pi)
2. Describe your requirements
3. Click "Generate"
4. Download or copy the code

**Example:**
```
Platform: Arduino
Requirements: Read temperature from DHT22, display on LCD, send data via Serial
```

### 3. Project Creation
Create complete projects with:
- Working code
- Documentation (README)
- Hardware setup guide
- Component list

### 4. Knowledge Management
Upload your own documentation:
- **Supported formats:** PDF, TXT, Markdown, Code files (.ino, .py, .cpp)
- **Auto-ingestion:** Scans knowledge_base/ directory on startup
- **Search:** Semantic search across all documents
- **Source tracking:** See which files were referenced

### 5. Component & Pinout Lookup
Quick reference for:
- Sensor specifications (DHT22, HC-SR04, etc.)
- Board pinouts (Arduino Uno, ESP32, Raspberry Pi)
- Wiring diagrams
- Library requirements

## 🏗️ Project Structure

```
EmbeddedAgent/
├── src/
│   ├── agent/          # LangGraph agent implementation
│   │   └── agent.py    # Main agent logic
│   ├── tools/          # LangChain tools
│   │   ├── base.py     # Knowledge base & RAG
│   │   └── embedded_tools.py  # Platform-specific tools
│   ├── ui/             # Streamlit interface
│   │   ├── streamlit_app.py
│   │   └── components.py
│   ├── cli/            # Command-line interface
│   ├── utils/          # Helper functions
│   ├── config.py       # Configuration
│   └── state.py        # State management
├── knowledge_base/     # Document storage
│   ├── arduino-examples/
│   ├── ESP32-Arduino-IoT-Labs/
│   ├── documentation/
│   └── chroma_db/      # Vector database
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

### Environment Variables
```bash
GROQ_API_KEY=your_api_key        # Required
HF_TOKEN=your_hf_token           # Optional (for higher rate limits)
```

### Config File (`src/config.py`)
```python
GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_TEMPERATURE = 0.2
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"
WEB_SEARCH_MAX_RESULTS = 5
```

## 🧪 Advanced Features

### Custom Knowledge Base
Add your own documentation:
1. Place files in `knowledge_base/` directory
2. Supported: PDF, TXT, MD, code files
3. Auto-ingested on startup
4. Searchable via semantic search

### Bulk Ingestion
```python
# Programmatic ingestion
from src.agent import EmbeddedSystemsAgent

agent = EmbeddedSystemsAgent(api_key, auto_ingest=True)
await agent.ingest_knowledge_base()
```

### CLI Usage
```bash
python main.py

# Available commands:
- chat: Interactive conversation
- generate: Code generation
- project: Create complete project
- search: Web search
- knowledge: Manage knowledge base
```

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build

# Remove volumes (reset data)
docker-compose down -v
```

## 📊 Performance

- **Code Generation:** ~5-10 seconds
- **Project Creation:** ~15-20 seconds
- **Knowledge Search:** <1 second
- **Web Search:** ~2-3 seconds

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain** - Framework for LLM applications
- **LangGraph** - Workflow orchestration
- **Groq** - Ultra-fast LLM inference
- **Streamlit** - Web UI framework
- **HuggingFace** - Embeddings and models
- **ChromaDB** - Vector database

## 📧 Contact

**Project Link:** [https://github.com/AbhishekChavan1/majorP](https://github.com/AbhishekChavan1/majorP)

## 🐛 Troubleshooting

### Common Issues

**1. ImportError: No module named 'langchain_chroma'**
```bash
pip install langchain-chroma langchain-huggingface --upgrade
```

**2. Port 8501 already in use**
```bash
# Find and kill the process
netstat -ano | findstr :8501  # Windows
lsof -i :8501                 # Linux/Mac
```

**3. GROQ API Key not found**
- Ensure GROQ_API_KEY is set in environment or .env file
- Restart terminal/application after setting

**4. Knowledge base not loading**
- Check file permissions in `knowledge_base/` directory
- Ensure supported file formats (PDF, TXT, MD, code)
- Check logs for ingestion errors

**5. Docker container won't start**
```bash
docker-compose logs
docker-compose down -v
docker-compose up -d --build
```

## 🎓 Examples

### Example 1: Blink LED
```arduino
// Generated for Arduino Uno
void setup() {
  pinMode(13, OUTPUT);
}

void loop() {
  digitalWrite(13, HIGH);
  delay(1000);
  digitalWrite(13, LOW);
  delay(1000);
}
```

### Example 2: Temperature Monitoring
```python
# Generated for Raspberry Pi
import Adafruit_DHT
import time

sensor = Adafruit_DHT.DHT22
pin = 4

while True:
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    print(f"Temp: {temperature}°C, Humidity: {humidity}%")
    time.sleep(2)
```

### Example 3: WiFi Connection (ESP32)
```cpp
#include <WiFi.h>

const char* ssid = "your_ssid";
const char* password = "your_password";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nConnected!");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Your code here
}
```

## 🚦 Roadmap

- [ ] Support for more platforms (STM32, Teensy)
- [ ] Visual circuit designer
- [ ] Code optimization suggestions
- [ ] Hardware compatibility checker
- [ ] Multi-language support
- [ ] Mobile app interface
- [ ] Cloud deployment templates

## ⭐ Star History

If you find this project helpful, please give it a star! ⭐

---

**Built with ❤️ for the embedded systems community**
