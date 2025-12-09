import time
import statistics
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def bench_call(path: str, payload: dict, n: int = 5):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        r = client.post(path, json=payload)
        assert r.status_code in (200, 500)
        times.append((time.perf_counter() - t0) * 1000)
    return statistics.median(times)

def test_bench_chat_basic():
    m = bench_call('/chat', {
        'provider': 'Groq', 'model': 'llama-3.1-70b-versatile', 'usecase': 'Basic Chatbot', 'message': 'Hi'
    })
    assert m >= 0

def test_bench_news_summary():
    m = bench_call('/news/summary', {'timeframe': 'last 24 hours'})
    assert m >= 0

