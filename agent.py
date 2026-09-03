"""AI proposal stage; generated code is never executed or written here."""
from __future__ import annotations

import json
import os
import re
from typing import Any

MAX_LOG_BYTES = 32_000
MAX_SOURCE_BYTES = 200_000

class AutoFixError(ValueError):
    pass

def _json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    try: value = json.loads(cleaned)
    except json.JSONDecodeError as exc: raise AutoFixError("model response was not valid JSON") from exc
    if not isinstance(value, dict): raise AutoFixError("model response must be a JSON object")
    return value

class AutoFixAgent:
    def __init__(self, *, client: Any | None = None, model: str | None = None) -> None:
        self.model_name = model or os.getenv("GEMINI_MODEL")
        self._client = client
        if self._client is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key: raise AutoFixError("GEMINI_API_KEY is required; publishing is never mocked")
            if not self.model_name: raise AutoFixError("GEMINI_MODEL must name an approved model")
            from google import genai
            self._client = genai.Client(api_key=api_key)
        if not self.model_name: raise AutoFixError("GEMINI_MODEL must name an approved model")

    def analyze_error(self, error_log: str) -> dict[str, Any]:
        bounded = error_log.encode("utf-8", "replace")[:MAX_LOG_BYTES].decode("utf-8", "replace")
        response = self._client.models.generate_content(model=self.model_name, contents=(
            "Return only JSON with string keys file,line,error,message. Identify the likely Python path and line. Do not include code or secrets.\n" + bounded))
        data = _json_object(response.text or "")
        if any(not isinstance(data.get(key), (str, int)) for key in ("file", "line", "error", "message")):
            raise AutoFixError("analysis must contain file, line, error and message")
        return data

    def generate_patch(self, analysis: dict[str, Any], source: str) -> dict[str, Any]:
        if len(source.encode("utf-8")) > MAX_SOURCE_BYTES: raise AutoFixError("source file exceeds review limit")
        response = self._client.models.generate_content(model=self.model_name, contents=(
            "Return only JSON {\"edits\":[{\"old\":\"exact source\",\"new\":\"replacement\"}]}. "
            "At most five small exact edits; never return a whole file, markdown or secrets.\n"
            f"Path: {analysis.get('file')}\nError: {analysis.get('error')}: {analysis.get('message')}\nOriginal source:\n{source}"))
        return _json_object(response.text or "")

    def generate_fix_code(self, analysis: dict[str, Any], source: str) -> dict[str, Any]:
        return self.generate_patch(analysis, source)
