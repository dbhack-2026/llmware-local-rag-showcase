from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.config import settings
from app.llm import LocalLLM
from app.retrieval import retrieve
from app.schemas import AskRequest, AskResponse, Source

local_llm = LocalLLM(settings.model_name)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Lazy loading keeps health endpoints available while the model is downloaded.
    yield


app = FastAPI(
    title="LLMWare Local RAG Showcase",
    version="1.0.0",
    description="Private local LLM inference and source-grounded Q&A with LLMWare.",
    lifespan=lifespan,
)


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "UP"}


@app.get("/health/ready")
def ready() -> dict[str, str | bool]:
    return {"status": "UP", "model_loaded": local_llm.ready}


@app.get("/v1/info")
def info() -> dict[str, str | bool]:
    return {
        "framework": "llmware",
        "model": settings.model_name,
        "inference": "local",
        "knowledge_dir": str(settings.knowledge_dir),
        "model_loaded": local_llm.ready,
    }


@app.post("/v1/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    chunks = (
        retrieve(request.question, settings.knowledge_dir, settings.top_k)
        if request.use_knowledge_base
        else []
    )
    context = "\n\n".join(
        f"SOURCE [{item.source}]\n{item.text}" for item in chunks
    )[: settings.max_context_chars]

    instruction = (
        "Answer the question using only the supplied context. "
        "When context is insufficient, say so. Cite source labels in square brackets."
        if chunks
        else "Answer the question clearly and concisely."
    )

    try:
        result = local_llm.infer(
            prompt=f"{instruction}\n\nQUESTION: {request.question}",
            context=context,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Local model inference failed: {type(exc).__name__}: {exc}",
        ) from exc

    answer = str(result.get("llm_response") or result.get("response") or result)
    return AskResponse(
        answer=answer,
        model=settings.model_name,
        sources=[
            Source(source=c.source, score=c.score, excerpt=c.text[:300]) for c in chunks
        ],
        usage=result.get("usage", {}) if isinstance(result, dict) else {},
    )
