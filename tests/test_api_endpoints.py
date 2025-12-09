import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_success(self):
        """Test successful health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_health_check_detailed(self):
        """Test detailed health check information"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data
        
        # Check services status
        assert "chroma_db" in data["services"]
        assert "llm_provider" in data["services"]

class TestChatEndpoints:
    """Test chat functionality endpoints"""

    @patch('app.services.chat_service.ChatService.process_message')
    def test_chat_message_success(self, mock_process_message):
        """Test successful chat message"""
        mock_process_message.return_value = {
            "response": "Test response",
            "session_id": "test-session-123",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        response = client.post("/chat/message", json={
            "message": "Hello, how are you?",
            "usecase": "general"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Test response"
        assert data["session_id"] == "test-session-123"

    def test_chat_message_validation(self):
        """Test chat message validation"""
        # Missing message
        response = client.post("/chat/message", json={
            "usecase": "general"
        })
        assert response.status_code == 422

    def test_chat_message_empty(self):
        """Test empty chat message"""
        response = client.post("/chat/message", json={
            "message": "",
            "usecase": "general"
        })
        assert response.status_code == 422

class TestNewsEndpoints:
    """Test news functionality endpoints"""

    @patch('app.services.news_service.NewsService.search_news')
    def test_news_search_success(self, mock_search_news):
        """Test successful news search"""
        mock_search_news.return_value = {
            "results": [
                {
                    "title": "AI News Article",
                    "summary": "Summary of the article",
                    "url": "https://example.com/article",
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            ]
        }
        
        response = client.post("/news/search", json={
            "query": "latest AI developments",
            "max_results": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) > 0
        assert "title" in data["results"][0]

    def test_news_search_validation(self):
        """Test news search validation"""
        # Missing query
        response = client.post("/news/search", json={})
        assert response.status_code == 422

    def test_news_search_empty_query(self):
        """Test empty news search query"""
        response = client.post("/news/search", json={
            "query": "",
            "max_results": 5
        })
        assert response.status_code == 422

class TestErrorHandling:
    """Test error handling across endpoints"""

    def test_404_handler(self):
        """Test 404 error handling"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test method not allowed error"""
        response = client.post("/health")
        assert response.status_code == 405

    @patch('app.services.chat_service.ChatService.process_message')
    def test_internal_server_error(self, mock_process_message):
        """Test internal server error handling"""
        mock_process_message.side_effect = Exception("Internal error")
        
        response = client.post("/chat/message", json={
            "message": "Hello",
            "usecase": "general"
        })
        
        assert response.status_code == 500

@pytest.mark.asyncio
class TestAsyncOperations:
    """Test async operations"""

    async def test_async_health_check(self):
        """Test async health check"""
        response = client.get("/health")
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])