# LLMWare Local RAG Showcase

A production-shaped Python service demonstrating the main value of **LLMWare**:

- local/private LLM inference through `ModelCatalog`;
- configurable local model selection;
- source-grounded answers over private Markdown and text knowledge;
- FastAPI endpoints callable from Spring Boot;
- Docker and OpenShift/Fabric deployment manifests;
- no cloud LLM API key required.

> The first inference request may download the selected model. For an offline Fabric environment, preload the approved model into the mounted cache or PVC.

## Architecture

```text
Spring Boot / Client
        |
        | HTTP POST /v1/ask
        v
FastAPI service
  |-- private-document retrieval
  |-- grounded prompt with source labels
  `-- LLMWare ModelCatalog
          `-- local model inference
```

The included retriever is deliberately lightweight so the showcase starts without a separate vector database. For production, replace `app/retrieval.py` with LLMWare Library plus embeddings and PGVector/Qdrant while keeping the REST contract stable.

## Run locally

For detailed Windows and VS Code instructions, see [`docs/RUN_LOCALLY_WINDOWS_VSCODE.md`](docs/RUN_LOCALLY_WINDOWS_VSCODE.md).

Python 3.11 is recommended.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8080
```

### Linux/macOS

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Swagger UI: `http://localhost:8080/docs`

## Try it

```bash
curl http://localhost:8080/v1/info
```

```bash
curl -X POST http://localhost:8080/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Where should model weights be stored on Fabric?","use_knowledge_base":true}'
```

## Run with Docker

```bash
docker compose up --build
```

The named volume preserves downloaded model files across container restarts.

## Deploy to Fabric/OpenShift

1. Build and push the image to your approved registry.
2. Replace `YOUR_REGISTRY` in `deploy/openshift.yaml`.
3. Apply the manifests:

```bash
oc apply -f deploy/pvc.yaml
oc apply -f deploy/openshift.yaml
```

The sample starts with one replica because each replica loads its own model copy. Profile CPU, memory, latency, and concurrency before scaling.

## Call from Spring Boot

```java
public record AskRequest(String question, boolean useKnowledgeBase) {}
public record AskResponse(String answer, String model, boolean localInference) {}

AskResponse response = restClient.post()
    .uri("/v1/ask")
    .body(new AskRequest(question, true))
    .retrieve()
    .body(AskResponse.class);
```

## Project structure

```text
app/                 FastAPI, LLM wrapper, retrieval and schemas
deploy/              OpenShift Deployment, Service and PVC
knowledge/           Sample private knowledge documents
tests/               API and retrieval tests
docs/                Windows/VS Code run guide
Dockerfile            Container image
Docker-compose.yml    Local container run
```

## What this showcases

| Capability | Implementation |
|---|---|
| Local model loading | `app/llm.py` |
| Lazy initialization | `LocalLLM.load()` |
| Private RAG context | `app/retrieval.py`, `knowledge/` |
| Source citations | `/v1/ask` response |
| Spring Boot integration | REST contract and Java example |
| Fabric packaging | `Dockerfile`, `deploy/` |
| Health endpoints | `/health/live`, `/health/ready` |

## Validate

```bash
pip install -r requirements-dev.txt
ruff check app tests
pytest -q
```

## Production extensions

- Use LLMWare Library for PDF, DOCX, PPTX and HTML parsing.
- Add embeddings and PGVector/Qdrant for semantic or hybrid retrieval.
- Store Confluence and Jira ACL metadata and filter before prompt construction.
- Add incremental ingestion for changed pages and resolved incidents.
- Move larger inference workloads to vLLM/KServe while retaining LLMWare for ingestion and retrieval.
- Add OAuth, AD-group authorization, audit events, prompt redaction and metrics.

## License

Apache-2.0. Review the license of each selected model separately before enterprise deployment.
