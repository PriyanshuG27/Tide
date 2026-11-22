"""Groq LLM classifier using fast OpenAI-compatible JSON completions."""
import json
from typing import Any

import httpx

from .heuristics import Verdict
from .jev import ACTIVITY_CRITERIA, JevError

SYSTEM_PROMPT = """You are an exam activity classifier in an academic lab.
Analyze the student's foreground window/event against the exam policy to detect unauthorized assistance.

Categories:
- allowed_tool: An app the exam policy allows (editor, terminal, file explorer, packet analyzer, VM), or a local file.
- ai_assistant: An AI chatbot, AI coding assistant, or any AI tool that answers questions or writes code.
- communication: Messaging, chat, social media, or email.
- web_lookup: Searching or reading websites for answers: search engines, Q&A, tutorials, code sites.
- remote_or_file_share: Remote desktop, screen sharing, cloud drives, or file transfer.
- other: Anything else, such as games, media, or system utilities.

Confidence Guidelines:
- If the event is undeniably an AI assistant or communication app (e.g., ChatGPT, Claude, Poe, NoteGPT, WhatsApp, Discord, Telegram), assign confidence 0.95 to 0.99.
- If the activity is legitimate or ambiguous, assign confidence <= 0.70.

Violation Guidelines:
- Assign a float from 0.0 to 1.0 representing the probability that this event breaks the exam policy (1.0 = definite violation, 0.0 = completely allowed).

You MUST respond strictly with a valid JSON object matching:
{
  "activity": "allowed_tool" | "ai_assistant" | "communication" | "web_lookup" | "remote_or_file_share" | "other",
  "confidence": <float between 0.0 and 1.0>,
  "violation": <float between 0.0 and 1.0>
}"""


class GroqClassifier:
    def __init__(self, url: str, key: str, model: str, client: httpx.AsyncClient | None = None,
                 timeout: float = 4.0) -> None:
        self.url, self.key, self.model = url, key, model
        self.client = client or httpx.AsyncClient(timeout=timeout)

    def request_body(self, text: str) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0,
        }

    @staticmethod
    def parse(body: dict[str, Any]) -> Verdict:
        content = body["choices"][0]["message"]["content"]
        data = json.loads(content)
        activity = str(data.get("activity", "other"))
        if activity not in ACTIVITY_CRITERIA:
            activity = "other"
        confidence = float(data.get("confidence", 0.5))
        violation = float(data.get("violation", 0.0))
        return Verdict(
            label=activity,
            confidence=round(confidence, 3),
            violation=round(violation, 3),
            source="jev",  # Preserves frontend 'Jev live' badge and decide.py auto-act rules
            raw={"model": body.get("model"), "provider": "groq", "data": data}
        )

    async def classify(self, text: str) -> Verdict:
        try:
            r = await self.client.post(
                self.url,
                json=self.request_body(text),
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
            )
            r.raise_for_status()
            return self.parse(r.json())
        except (httpx.HTTPError, KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
            raise JevError(repr(e)) from e
