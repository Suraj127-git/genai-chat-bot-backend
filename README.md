# GenAI Chatbot Backend

A FastAPI-based backend service for the GenAI Chatbot system, featuring AI-powered chat functionality and news aggregation with ChromaDB vector storage.

## 🏗️ Architecture Overview

This backend service provides:
- **AI Chatbot**: Conversational AI with memory and context awareness
- **News Aggregation**: AI-powered news search and summarization
- **Vector Storage**: ChromaDB for persistent conversation memory
- **RESTful API**: FastAPI with comprehensive endpoints
- **Multi-LLM Support**: Groq and other providers

## 📁 Project Structure

```
genai-chat-bot-backend/
├── app/
│   ├── common/           # Shared utilities and configurations
│   ├── database/         # ChromaDB integration and vector storage
│   ├── factories/        # LLM provider factories
│   ├── graph/            # LangGraph workflow definitions
│   ├── nodes/            # Processing nodes for chat and news
│   ├── repositories/     # Data access layer
│   ├── services/         # Business logic layer
│   ├── state/            # Application state management
│   ├── tools/            # External integrations (search, etc.)
│   ├── instrumentation.py # Application monitoring
│   └── main.py           # FastAPI application entry point
├── tests/                # Test suites
├── AINews/               # AI news summaries storage
├── pyproject.toml        # Python dependencies and project configuration
├── Dockerfile           # Container configuration
├── railway.json         # Railway deployment configuration
├── .env.example         # Environment variables template
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- API keys for:
  - Groq API
  - Tavily API (for news search)

### Installation

1. **Clone and navigate to backend folder:**
   ```bash
   cd genai-chat-bot-backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# API Keys
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
CHROMA_PERSIST_DIRECTORY=./chroma_db

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

### API Configuration

The backend supports multiple LLM providers through a factory pattern:
- **Groq**: Primary provider for fast inference
- **Custom providers**: Extensible factory pattern for additional providers

## 📡 API Documentation

### Base URL
- Local: `http://localhost:8000`
- Production: `https://your-backend-service.railway.app`

### Endpoints

#### Health Check
```http
GET /health
```
Returns service health status and system information.

#### Chat Operations
```http
POST /chat/message
```
Send a message to the AI chatbot and receive a response.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "session_id": "optional-session-id",
  "usecase": "general"
}
```

**Response:**
```json
{
  "response": "I'm doing well, thank you! How can I help you today?",
  "session_id": "generated-session-id",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### News Operations
```http
POST /news/search
```
Search for AI-related news and get summaries.

**Request Body:**
```json
{
  "query": "latest AI developments",
  "max_results": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "title": "Latest AI Breakthrough",
      "summary": "Summary of the news article...",
      "url": "https://example.com/article",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ]
}
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_chat_basic.py    # Chat functionality tests
pytest tests/test_news.py          # News functionality tests
pytest tests/test_health.py        # Health check tests
pytest tests/test_benchmarks.py    # Performance benchmarks
```

## 🐳 Docker Deployment

### Local Docker Build

```bash
# Build the image
docker build -t genai-chat-bot-backend .

# Run the container
docker run -p 8000:8000 --env-file .env genai-chat-bot-backend
```

### Railway Deployment

The backend is configured for Railway deployment with the included `railway.json`:

1. **Connect to Railway:**
   ```bash
   npm install -g @railway/cli
   railway login
   railway init
   ```

2. **Set environment variables in Railway dashboard:**
   - `GROQ_API_KEY`
   - `TAVILY_API_KEY`

3. **Deploy:**
   ```bash
   railway up
   ```

## 🔍 Key Components

### ChromaDB Integration
- **Purpose**: Persistent vector storage for conversation memory
- **Location**: `app/database/chroma_manager.py`
- **Features**: Similarity search, metadata filtering, persistent storage

### LangGraph Workflows
- **Chat Graph**: Multi-step conversation processing
- **News Graph**: News search and summarization pipeline
- **Location**: `app/graph/enhanced_graph_builder.py`

### LLM Factory Pattern
- **Purpose**: Abstraction layer for multiple LLM providers
- **Location**: `app/factories/llm_factory.py`
- **Providers**: Groq, extensible for others

### Service Layer
- **Chat Service**: Business logic for chat operations
- **News Service**: Business logic for news operations
- **Location**: `app/services/`

## 🔒 Security Features

- **CORS Configuration**: Configurable allowed origins
- **Environment Variables**: Sensitive data externalized
- **Input Validation**: Request validation and sanitization
- **Error Handling**: Secure error responses without exposing internals

## 📊 Monitoring & Logging

- **Health Checks**: Comprehensive health endpoint
- **Structured Logging**: JSON-formatted logs with configurable levels
- **Performance Monitoring**: Built-in instrumentation hooks

## 🔄 Data Flow

1. **Chat Request Flow:**
   - Client sends message → API endpoint → Chat service → LangGraph → LLM → Response storage → Client

2. **News Request Flow:**
   - Client sends query → API endpoint → News service → LangGraph → Tavily search → LLM summarization → Client

3. **Memory Storage:**
   - Conversations → ChromaDB vector storage → Similarity search → Context enhancement

## 🛠️ Development

### Adding New Features

1. **New LLM Provider:**
   - Extend `app/factories/llm_factory.py`
   - Add provider configuration
   - Update environment variables

2. **New API Endpoints:**
   - Add route handlers in `app/main.py`
   - Implement service logic in `app/services/`
   - Add tests in `tests/`

3. **New Graph Nodes:**
   - Create node in `app/nodes/`
   - Integrate into graph builder
   - Update state management if needed

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Include docstrings for public methods
- Write comprehensive tests for new features

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Railway Deployment Guide](../DEPLOYMENT_GUIDE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

This project is part of the GenAI Chatbot System. See the root LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the [Deployment Guide](../DEPLOYMENT_GUIDE.md)
- Review the [Migration Documentation](CHROMADB_MIGRATION.md)
- Ensure all environment variables are properly configured
- Check the health endpoint for service status