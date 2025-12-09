# GenAI Chatbot Backend - ChromaDB Migration

This document outlines the migration from Qdrant to ChromaDB and removal of LOGTAIL dependencies.

## Migration Summary

### Database Changes
- **Removed**: Qdrant vector database
- **Added**: ChromaDB with persistent storage
- **Benefits**: Simplified deployment, no external database service required

### Logging Changes
- **Removed**: LOGTAIL SDK and external logging service
- **Added**: Standard Python logging with console output
- **Benefits**: Reduced dependencies, simplified configuration

## Configuration Changes

### Environment Variables

#### Removed Variables
```bash
# Qdrant Configuration
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=your_api_key

# LOGTAIL Configuration  
LOGTAIL_SOURCE_TOKEN=your_source_token
LOGTAIL_HOST=your_host_url
```

#### New Variables
```bash
# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=qa_collection

# OpenAI API (for embeddings)
OPENAI_API_KEY=your_openai_api_key
```

### Dependencies

#### Removed Dependencies
- `qdrant-client`
- `logtail-python`

#### New Dependencies
- `chromadb`
- `sentence-transformers`
- `numpy`

## Code Changes

### Database Layer
- **New**: `app/database/chroma_manager.py` - ChromaDB integration
- **New**: `app/repositories/chroma_repository.py` - Repository pattern for ChromaDB
- **Removed**: `app/database/qdrant_manager.py`
- **Removed**: `app/repositories/qdrant_repository.py`

### Updated Files
- `app/nodes/enhanced_chatbot_node.py` - Now uses ChromaRepository
- `app/nodes/enhanced_ai_news_node.py` - Now uses ChromaRepository
- `app/graph/enhanced_graph_builder.py` - Now uses ChromaRepository
- `app/common/logger.py` - Removed LOGTAIL, uses standard logging

## Deployment

### Railway.com Deployment

1. **Build Configuration**
   - Uses Python 3.11-slim base image
   - Includes system dependencies (gcc, g++) for ChromaDB
   - Creates persistent storage directory for ChromaDB
   - Health checks configured for Railway monitoring

2. **Environment Setup**
   - Set required API keys in Railway dashboard
   - Configure ChromaDB persistence path
   - Optional: Set custom collection name

3. **Required Environment Variables**
   ```bash
   GROQ_API_KEY=your_groq_api_key
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   CHROMA_PERSIST_DIRECTORY=/app/chroma_db
   ```

### Local Development

1. **Install Dependencies**
   ```bash
   cd genai-chat-bot-backend
   pip install -e .
   ```

2. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Application**
   ```bash
   uvicorn app.main:app --reload
   ```

## Testing

### Manual Testing
1. Test health endpoint: `GET /health`
2. Test chat functionality: `POST /chat`
3. Test news functionality: `POST /news/summary`
4. Verify ChromaDB persistence by checking `./chroma_db` directory

### Automated Testing
Run the existing test suite:
```bash
pytest tests/
```

## Troubleshooting

### Common Issues

1. **ChromaDB Import Errors**
   - Ensure all dependencies are installed: `pip install -e .`
   - Check Python version compatibility (3.10+)

2. **Embedding Model Issues**
   - Verify OpenAI API key is set correctly
   - Check network connectivity for model downloads

3. **Persistence Issues**
   - Ensure `CHROMA_PERSIST_DIRECTORY` is writable
   - Check disk space availability

### Performance Considerations

- ChromaDB uses local file-based storage
- For production, consider using ChromaDB server mode
- Monitor memory usage with large datasets

## Migration Benefits

1. **Simplified Architecture**: No external vector database required
2. **Reduced Costs**: No Qdrant hosting fees
3. **Easier Deployment**: Single container deployment on Railway
4. **Better Performance**: Local storage eliminates network latency
5. **Simplified Logging**: Standard Python logging without external services

## Rollback Plan

If issues arise, you can rollback by:
1. Restoring Qdrant files from git history
2. Reverting pyproject.toml dependencies
3. Restoring original environment variables
4. Rebuilding with Qdrant configuration

## Support

For issues related to this migration:
1. Check application logs for error messages
2. Verify all environment variables are set correctly
3. Ensure ChromaDB directory has proper permissions
4. Test with minimal configuration first