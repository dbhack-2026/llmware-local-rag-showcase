from __future__ import annotations

import threading
from typing import Any


class LocalLLM:
    """Lazy, thread-safe wrapper around LLMWare ModelCatalog."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model: Any | None = None
        self._load_lock = threading.Lock()
        self._inference_lock = threading.Lock()

    def load(self) -> None:
        if self._model is not None:
            return
        with self._load_lock:
            if self._model is None:
                from llmware.models import ModelCatalog

                self._model = ModelCatalog().load_model(self.model_name)

    @property
    def ready(self) -> bool:
        return self._model is not None

    def infer(self, prompt: str, context: str = "") -> dict[str, Any]:
        self.load()
        with self._inference_lock:
            output = self._model.inference(prompt, add_context=context)
        if isinstance(output, dict):
            return output
        return {"llm_response": str(output)}
