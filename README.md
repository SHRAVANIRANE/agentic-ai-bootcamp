# Inventory Demand Forecasting Agent

An AI-assisted retail inventory system that forecasts demand, recommends reorder quantities, and explains decisions in plain English using Llama 3 via Ollama.

## System Architecture

```text
CSV Data (73,100 rows)
        ↓
DataPreprocessor → FeatureEngineer → XGBoostForecaster (+ SHAP)
                                              ↓
                                    ForecastingService
                                              ↓
                              LLMService (Llama 3 via Ollama)
                                              ↓
                                    FastAPI REST API
                                              ↓
                                    React Dashboard
```

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| ML forecasting | XGBoost |
| LLM reasoning | Llama 3 via Ollama |
| Agent orchestration | LangChain ReAct Agent |
| Backend API | FastAPI + Uvicorn |
| Frontend | React + Vite + Recharts |
| Data processing | Pandas + NumPy |

## Project Structure

```text
inventory-demand-forecasting-shap/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # forecast, reorder, agent endpoints
│   │   ├── agents/            # LangChain ReAct agent + tools
│   │   ├── core/              # config, logging
│   │   ├── models/            # Pydantic schemas
│   │   ├── pipeline/          # preprocessor, feature engineer, XGBoost
│   │   └── services/          # forecasting, reorder, LLM, data services
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # ForecastChart, ReorderTable, AgentChat
│   │   └── pages/             # Dashboard
│   └── package.json
├── data/
│   └── retail_store_inventory.csv
├── notebooks/
│   └── inventory_forecasting.ipynb
└── docker-compose.yml
```

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- Ollama installed and running
- Llama model: `llama3:8b-instruct-q4_0`

## Setup & Run Locally (Windows PowerShell)

### 1. Clone the repo

```powershell
git clone https://github.com/SHRAVANIRANE/agentic-ai-bootcamp.git
cd agentic-ai-bootcamp
```

### 2. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start Ollama. Keep this terminal open, or skip this command if Ollama is already running:

```powershell
ollama serve
```

In another terminal, pull the model:

```powershell
ollama pull llama3:8b-instruct-q4_0
```

Start the backend in a new PowerShell terminal:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

### 3. Frontend

Start the frontend in another terminal:

```powershell
cd frontend
npm install
$env:VITE_API_URL="http://localhost:8000/api/v1"
npm start
```

Frontend: `http://localhost:3000`

Use `S001` and `P0001` as the first sample store/product pair.

---

## API Endpoints

### Forecast demand
```http
POST /api/v1/forecast/
```

```json
{
  "store_id": "S001",
  "product_id": "P0001",
  "horizon_days": 7
}
```

### Reorder recommendation
```http
POST /api/v1/reorder/
```

```json
{
  "store_id": "S001",
  "product_id": "P0001",
  "current_inventory": 100,
  "lead_time_days": 7
}
```

### AI agent chat
```http
POST /api/v1/agent/chat
```

```json
{
  "message": "Should I reorder P0001 at S001 if I have 50 units left?",
  "store_id": "S001",
  "product_id": "P0001"
}
```

---

## How It Works

### Forecasting Pipeline
1. Raw CSV is cleaned and validated by `DataPreprocessor`
2. `FeatureEngineer` builds lag features, rolling stats, calendar features, price sensitivity
3. `XGBoostForecaster` trains a per-product model with time-based train/val split
4. SHAP values identify the top demand drivers for each product
5. Multi-step ahead forecast is generated with confidence intervals

### LLM Explanation
- SHAP top drivers + forecast stats are passed to Llama 3
- Llama 3 generates plain English business explanations

---

## Docker Deployment

```bash
docker compose up --build
```

Services:
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Ollama: `http://localhost:11434`
- Redis: `localhost:6379`

After the Ollama container starts, pull the model into it:

```bash
docker compose exec ollama ollama pull llama3:8b-instruct-q4_0
```

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## Key Features

- **Zero manual training** — models train automatically
- **SHAP explainability** — shows which features drove the prediction
- **LLM reasoning** — Llama 3 explains trends and reorder decisions
- **LangChain ReAct agent** — conversational interface for inventory Q&A
- **Production ready** — async FastAPI, structured logging, Pydantic validation
