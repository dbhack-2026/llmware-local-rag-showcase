from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RetrievedChunk:
    source: str
    text: str
    score: float


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_-]{2,}", text.lower()))


def retrieve(query: str, knowledge_dir: Path, top_k: int = 4) -> list[RetrievedChunk]:
    """Small dependency-free retriever used to keep the demo runnable offline.

    LLMWare remains responsible for local model loading/inference. The README also
    shows how this component can be replaced by LLMWare Library + embeddings.
    """
    query_tokens = _tokens(query)
    scored: list[RetrievedChunk] = []

    for path in sorted(knowledge_dir.glob("**/*")):
        if not path.is_file() or path.suffix.lower() not in {".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for index, paragraph in enumerate(re.split(r"\n\s*\n", text)):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            paragraph_tokens = _tokens(paragraph)
            overlap = len(query_tokens & paragraph_tokens)
            score = overlap / max(1, len(query_tokens))
            if score > 0:
                scored.append(
                    RetrievedChunk(
                        source=f"{path.name}#chunk-{index + 1}",
                        text=paragraph,
                        score=round(score, 4),
                    )
                )

    return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]
