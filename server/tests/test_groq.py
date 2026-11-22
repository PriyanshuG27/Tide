import json
import httpx
import pytest

from tide_server.classify.groq import GroqClassifier
from tide_server.classify.jev import JevError
from tide_server.classify.pipeline import Pipeline
from tide_common.protocol import Kind, Signal

POE = Signal(kind=Kind.WINDOW, data={"process": "chrome.exe", "title": "Fast AI Chat - Poe",
                                     "host": "poe.com", "description": "Google Chrome"})

GROQ_REPLY = {
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1726000000,
    "model": "openai/gpt-oss-120b",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": json.dumps({
                    "activity": "ai_assistant",
                    "confidence": 0.98,
                    "violation": 0.99
                })
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {"prompt_tokens": 120, "completion_tokens": 25, "total_tokens": 145}
}


def groq_with(handler):
    return GroqClassifier("https://api.groq.com/openai/v1/chat/completions", "gsk_test", "openai/gpt-oss-120b",
                          client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))


def test_groq_request_body_shape():
    classifier = groq_with(lambda r: None)
    body = classifier.request_body("test event text")
    assert body["model"] == "openai/gpt-oss-120b"
    assert body["response_format"] == {"type": "json_object"}
    assert body["temperature"] == 0.0
    assert len(body["messages"]) == 2
    assert body["messages"][1]["content"] == "test event text"


def test_groq_parse_valid():
    v = GroqClassifier.parse(GROQ_REPLY)
    assert v.label == "ai_assistant"
    assert v.confidence == 0.98
    assert v.violation == 0.99
    assert v.source == "jev"
    assert v.raw["model"] == "openai/gpt-oss-120b"


@pytest.mark.anyio
async def test_groq_classify_success():
    def handler(request: httpx.Request):
        assert request.headers["Authorization"] == "Bearer gsk_test"
        return httpx.Response(200, json=GROQ_REPLY)

    classifier = groq_with(handler)
    v = await classifier.classify("test text")
    assert v.label == "ai_assistant"
    assert v.confidence == 0.98


@pytest.mark.anyio
async def test_groq_pipeline_fallback_on_error():
    def failing_handler(request: httpx.Request):
        return httpx.Response(500, text="Internal Server Error")

    classifier = groq_with(failing_handler)
    pipeline = Pipeline(classifier)
    v = await pipeline.classify(POE, ["VS Code"])
    assert v.source == "heuristic"
    assert pipeline.last_error is not None
