# Agentic RAG Debugger

An intelligent Python debugging system that uses Retrieval-Augmented Generation (RAG) and multi-agent workflows to automatically fix code issues with syntax validation.

## 🚀 Features

- **Intelligent Code Analysis**: Uses vector similarity search to find relevant code context
- **Multi-Agent Workflow**: Retrieval → Analysis → Validation loop with self-correction
- **Syntax Validation**: Automatic linting with Flake8 to ensure generated fixes are syntactically correct
- **Web Interface**: React frontend for easy interaction
- **REST API**: FastAPI backend for programmatic access
- **Vector Database**: Qdrant for efficient code similarity search

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Retrieve      │───▶│    Analyze      │───▶│   Validate      │
│  (Find Context) │    │  (Generate Fix) │    │ (Check Syntax)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                               ┌─────────────────┐
                                               │     Router      │
                                               │ (Retry/Finish)  │
                                               └─────────────────┘
```

## 📁 Project Structure

```
AgenticRag/
├── agent.py           # Core multi-agent workflow
├── api.py             # FastAPI REST endpoints
├── ingest.py          # Code indexing and vector storage
├── target_code/       # Sample buggy Python files
│   ├── auth.py
│   ├── analytics.py
│   └── ecommerce.py
├── client/            # React frontend
│   ├── src/
│   └── package.json
├── qdrant_db/         # Vector database storage
└── package.json
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama with `qwen2.5-coder:7b` model

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Ollama model:
```bash
ollama pull qwen2.5-coder:7b
```

3. Index your codebase:
```bash
python ingest.py
```

### Frontend Setup

1. Navigate to client directory:
```bash
cd client
npm install
```

## 🚀 Usage

### Start the Backend
```bash
uvicorn api:app --reload --port 8000
```

### Start the Frontend
```bash
cd client
npm run dev
```

### API Endpoints

#### Debug Code
```bash
POST /debug
{
  "error_message": "The login function is not working properly"
}
```

#### Update Code Index
```bash
POST /ingest
```

### Command Line Usage
```bash
python agent.py
```

## 🔧 Configuration

- **MAX_RETRIES**: Maximum fix attempts (default: 3)
- **TARGET_FOLDER**: Code directory to index (default: `./target_code`)
- **COLLECTION_NAME**: Qdrant collection name (default: `codebase_index`)

## 🧪 Example

Input:
```
"The calculate_total method is broken in the shopping cart"
```

Process:
1. **Retrieve**: Finds relevant code from `ecommerce.py`
2. **Analyze**: Generates fix using LLM
3. **Validate**: Checks syntax with Flake8
4. **Retry**: If syntax errors found, regenerates fix

Output:
```python
def calculate_total(self):
    self.total = 0  # Reset total
    for item in self.items:
        self.total += item['price']  # Fixed: use dict access
    return self.total
```

## 🔍 Sample Bugs Included

- **auth.py**: Password hashing comparison bug
- **analytics.py**: Division by zero error
- **ecommerce.py**: Dictionary access and total calculation bugs

## 🛡️ Dependencies

### Backend
- FastAPI - Web framework
- LangChain - LLM orchestration
- Qdrant - Vector database
- Ollama - Local LLM inference
- Flake8 - Python linting

### Frontend
- React - UI framework
- Vite - Build tool
- Axios - HTTP client
- React Markdown - Code rendering

## 📝 License

MIT License