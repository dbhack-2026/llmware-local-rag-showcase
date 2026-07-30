# Run the LLMWare Local RAG Showcase in VS Code on Windows

This guide runs the project directly on Windows using Python, Visual Studio Code, PowerShell, and a local LLM loaded through LLMWare. No cloud LLM API key is required.

## 1. Prerequisites

Install the following:

- Windows 10 or Windows 11, 64-bit.
- Python 3.11, 64-bit. During installation, select **Add Python to PATH**.
- Visual Studio Code.
- VS Code **Python** extension from Microsoft.
- Git for Windows, recommended when cloning from GitHub.
- At least 8 GB RAM; 16 GB is preferred for a smoother first run.
- Internet access for the initial Python package and model download.

Verify the tools in PowerShell:

```powershell
python --version
py -0p
git --version
code --version
```

Use Python 3.11 for this showcase. Newer Python versions can work, but local model and native runtime packages are usually most predictable on Python 3.11.

## 2. Get the project

### From a ZIP file

1. Extract `llmware-local-rag-showcase.zip` to a short path, for example:

```text
C:\dev\llmware-local-rag-showcase
```

2. Open PowerShell in that folder.

### From GitHub

```powershell
cd C:\dev
git clone https://github.com/dbhack-2026/llmware-local-rag-showcase.git
cd llmware-local-rag-showcase
```

## 3. Open the project in VS Code

```powershell
code .
```

Trust the workspace when prompted.

## 4. Create and activate a virtual environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

When PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This changes policy only for the current terminal.

## 5. Select the interpreter

Press `Ctrl+Shift+P`, run **Python: Select Interpreter**, and select:

```text
.venv\Scripts\python.exe
```

Confirm:

```powershell
python -c "import sys; print(sys.executable)"
```

## 6. Install dependencies

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -c "import llmware; print('LLMWare import successful')"
```

## 7. Start the service

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

Open:

- Swagger UI: `http://localhost:8080/docs`
- Health: `http://localhost:8080/health/live`
- Runtime information: `http://localhost:8080/v1/info`

The model loads lazily. The first `/v1/ask` request may download the selected model and initialize the runtime; later requests reuse the cache.

## 8. Test from PowerShell

Open a second terminal and activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Check runtime information:

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8080/v1/info" | ConvertTo-Json
```

Ask a private-knowledge question:

```powershell
$body = @{
    question = "Where should model weights be stored on Fabric?"
    use_knowledge_base = $true
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8080/v1/ask" `
    -ContentType "application/json" `
    -Body $body | ConvertTo-Json -Depth 8
```

The response includes the answer, selected model, matched private sources, and model usage when available.

Ask without the knowledge base:

```powershell
$body = @{
    question = "Explain retrieval-augmented generation in one paragraph."
    use_knowledge_base = $false
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8080/v1/ask" `
    -ContentType "application/json" `
    -Body $body | ConvertTo-Json -Depth 8
```

## 9. Add private knowledge

Add `.md` or `.txt` files under `knowledge\`, for example:

```text
knowledge\trade-support-runbook.md
knowledge\security-master-errors.txt
```

Restart the service or let Uvicorn reload it. The retriever ranks local text chunks and sends only the highest-ranked context to the local model.

Do not add production secrets, credentials, personal data, or unrestricted confidential documents to this demonstration folder.

## 10. Change the local model

The default model is `bling-answer-tool`. Override it for the current terminal:

```powershell
$env:LLMWARE_DEMO_MODEL_NAME = "llmware/bling-phi-3-gguf"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

Clear the override:

```powershell
Remove-Item Env:LLMWARE_DEMO_MODEL_NAME
```

Different models require different disk, RAM, startup time, runtime dependencies, and licensing review.

## 11. Debug in VS Code

Create `.vscode\launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run LLMWare FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8080",
        "--reload"
      ],
      "jinja": true,
      "justMyCode": true,
      "env": {
        "LLMWARE_DEMO_MODEL_NAME": "bling-answer-tool"
      }
    }
  ]
}
```

Open **Run and Debug**, select **Run LLMWare FastAPI**, press `F5`, and place breakpoints in `app/main.py`, `app/retrieval.py`, or `app/llm.py`.

## 12. Validate

```powershell
ruff check app tests
pytest -q
```

Tests validate the API and retrieval behavior without downloading the full generation model.

## 13. Restart later

```powershell
cd C:\dev\llmware-local-rag-showcase
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

## 14. Common Windows problems

### Python is not recognized

Reinstall Python 3.11 with **Add Python to PATH**, or disable Microsoft Store Python aliases under **Settings > Apps > Advanced app settings > App execution aliases**.

### Visual C++ build errors

Install **Build Tools for Visual Studio 2022**, select **Desktop development with C++**, reopen VS Code, and retry dependency installation.

### Path is too long

Use a short location such as `C:\dev\llmware-local-rag-showcase` and avoid deeply nested OneDrive or profile directories.

### First question returns HTTP 503

Review the Uvicorn terminal. Common causes are blocked model download, insufficient disk/RAM, missing runtime dependencies, unavailable model identifier, or corporate TLS inspection. Verify:

```powershell
Invoke-RestMethod http://localhost:8080/health/live
Invoke-RestMethod http://localhost:8080/v1/info
```

In restricted environments, preload approved models and Python packages through internal artifact repositories.

### Port 8080 is in use

```powershell
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
python -m uvicorn app.main:app --reload --port 8090
```

### VS Code uses the wrong interpreter

Run **Python: Select Interpreter**, choose `.venv\Scripts\python.exe`, and reopen the terminal.

## 15. Local flow

```text
PowerShell or Swagger UI
        |
        | POST /v1/ask
        v
FastAPI application
        |
        |-- reads private Markdown/text files
        |-- retrieves relevant chunks
        |-- builds a grounded prompt with source labels
        v
LLMWare ModelCatalog
        |
        `-- local model inference on Windows
```

The question and selected knowledge remain local except for initial package/model downloads. A fully offline deployment should preload all approved artifacts internally.
