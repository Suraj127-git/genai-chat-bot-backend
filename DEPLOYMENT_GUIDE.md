# Deployment Guide - Optimized Builds

## Quick Start

Choose your deployment strategy based on your needs:

### 1. Ultra-Lightweight (Recommended for Production)
**Best for**: Resource-constrained environments, cost optimization
```bash
# Build
docker build -t genai-chat-bot:ultra-light -f Dockerfile.ultra-light .

# Run with lightweight ChromaDB
docker run -d \
  --name genai-chat-bot \
  -p 8000:8000 \
  -e USE_LIGHTWEIGHT_DB=true \
  -e GROQ_API_KEY=your_key_here \
  genai-chat-bot:ultra-light
```

### 2. Optimized Standard
**Best for**: Balanced performance and features
```bash
# Build
docker build -t genai-chat-bot:optimized -f Dockerfile.optimized .

# Run with full features
docker run -d \
  --name genai-chat-bot \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_key_here \
  genai-chat-bot:optimized
```

### 3. Current Build (Development)
**Best for**: Development, testing full features
```bash
# Build current version
docker build -t genai-chat-bot:current -f Dockerfile .

# Run
docker run -d \
  --name genai-chat-bot \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_key_here \
  genai-chat-bot:current
```

## Environment Configuration

### Core Environment Variables
```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional - Performance
USE_LIGHTWEIGHT_DB=true  # Enable lightweight ChromaDB (saves 500MB+)
PORT=8000                # Port to listen on (default: 8000)
HOST=0.0.0.0            # Host to bind to (default: 0.0.0.0)

# Optional - ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db  # Data persistence path
```

### Railway Deployment
```yaml
# railway.json for ultra-lightweight
deploy:
  startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  healthcheckPath: "/health"
  restartPolicyType: "ON_FAILURE"
  restartPolicyMaxRetries: 10
  
# Set environment variable in Railway dashboard:
USE_LIGHTWEIGHT_DB=true
```

### Docker Compose
```yaml
version: '3.8'
services:
  genai-chat-bot:
    build:
      context: .
      dockerfile: Dockerfile.ultra-light
    ports:
      - "8000:8000"
    environment:
      - USE_LIGHTWEIGHT_DB=true
      - GROQ_API_KEY=${GROQ_API_KEY}
      - CHROMA_PERSIST_DIRECTORY=/app/data
    volumes:
      - chroma_data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  chroma_data:
```

## Size Comparison

| Build Type | Size | RAM Usage | Startup Time | Best For |
|------------|------|-----------|--------------|----------|
| Ultra-Light | ~250MB | ~200MB | 3-5s | Production, CI/CD |
| Optimized | ~400MB | ~300MB | 5-7s | Development |
| Current | ~1.2GB | ~800MB | 10-15s | Full features |

## Performance Tuning

### For Maximum Performance:
```bash
# Use lightweight mode + minimal resources
docker run -d \
  --name genai-chat-bot \
  --memory=512m \
  --cpus=0.5 \
  -p 8000:8000 \
  -e USE_LIGHTWEIGHT_DB=true \
  -e GROQ_API_KEY=your_key_here \
  genai-chat-bot:ultra-light
```

### For Development:
```bash
# Full features, more resources
docker run -d \
  --name genai-chat-bot \
  --memory=2g \
  --cpus=1.0 \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_key_here \
  genai-chat-bot:optimized
```

## Monitoring

### Health Checks
```bash
# Check if service is healthy
curl http://localhost:8000/health

# Get service stats
curl http://localhost:8000/stats
```

### Logs
```bash
# View logs
docker logs genai-chat-bot

# Follow logs
docker logs -f genai-chat-bot
```

### Resource Usage
```bash
# Check container stats
docker stats genai-chat-bot

# Check image size
docker images genai-chat-bot:ultra-light
```

## Troubleshooting

### Common Issues:

1. **Build fails with Alpine**
   - Use standard Debian-based image
   - Install additional build dependencies

2. **ChromaDB permissions**
   - Ensure volume permissions are correct
   - Use non-root user in container

3. **Memory issues**
   - Increase container memory limits
   - Use lightweight mode (`USE_LIGHTWEIGHT_DB=true`)

4. **Slow startup**
   - Check if sentence-transformers is loading
   - Verify lightweight mode is enabled

### Debug Mode:
```bash
# Run with debug logging
docker run -d \
  --name genai-chat-bot \
  -p 8000:8000 \
  -e USE_LIGHTWEIGHT_DB=true \
  -e GROQ_API_KEY=your_key_here \
  -e LOG_LEVEL=DEBUG \
  genai-chat-bot:ultra-light
```

## Cost Optimization

### For Cloud Deployment:
1. Use ultra-lightweight build
2. Set appropriate memory limits
3. Use spot instances where possible
4. Enable auto-scaling based on CPU/memory

### Example AWS ECS Task Definition:
```json
{
  "family": "genai-chat-bot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "genai-chat-bot",
      "image": "genai-chat-bot:ultra-light",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "USE_LIGHTWEIGHT_DB",
          "value": "true"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```