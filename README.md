# 📦 Inventory Demand Forecasting Agent

An industry-level, fully deployable AI system that forecasts retail inventory demand, recommends optimal reorder quantities, and explains decisions in plain English using **Llama 3 via Ollama**.

---

## 🏗️ System Architecture

```
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

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| ML Forecasting | XGBoost + SHAP Explainability |
| LLM Reasoning | Llama 3 (8B) via Ollama |
| Agent Orchestration | LangChain ReAct Agent |
| Backend API | FastAPI + Uvicorn |
| Frontend | React + Vite + Recharts |
| Data Processing | Pandas + NumPy |

---

## 📁 Project Structure

```
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

## ⚙️ Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) installed and running
- Llama 3 model pulled

```bash
# Install Ollama then pull the model
ollama pull llama3
```

---

## 🛠️ Setup & Run

### 1. Clone the repo

```bash
git clone https://github.com/SHRAVANIRANE/agentic-ai-bootcamp.git
cd agentic-ai-bootcamp
cd inventory-demand-forecasting-shap
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs at: `http://localhost:3000`

### 4. Make sure Ollama is running

```bash
ollama serve
```

---

## 📡 API Endpoints

### Forecast demand
```bash
POST /api/v1/forecast/
{
  "store_id": "S001",
  "product_id": "P0001",
  "horizon_days": 7
}
```

### Reorder recommendation
```bash
POST /api/v1/reorder/
{
  "store_id": "S001",
  "product_id": "P0001",
  "current_inventory": 100,
  "lead_time_days": 7
}
```

### AI Agent chat
```bash
POST /api/v1/agent/chat
{
  "message": "Should I reorder P0001 at S001 if I have 50 units left?",
  "store_id": "S001",
  "product_id": "P0001"
}
```

### Trend explanation
```bash
GET /api/v1/forecast/trends?store_id=S001&product_id=P0001
```

---

## 🧠 How It Works

### Forecasting Pipeline
1. Raw CSV is cleaned and validated by `DataPreprocessor`
2. `FeatureEngineer` builds lag features (7/14/21/28 days), rolling stats, calendar features, price sensitivity
3. `XGBoostForecaster` trains a per-product model with time-based train/val split
4. SHAP values identify the top demand drivers for each product
5. Multi-step ahead forecast is generated with confidence intervals

### Reorder Engine
Uses industry-standard supply chain formulas:
```
Safety Stock  = 1.65 × σ_demand × √lead_time × multiplier
Reorder Point = (avg_daily_demand × lead_time) + safety_stock
Order Qty     = forecasted_demand + safety_stock - current_inventory
```

### LLM Explanation
- SHAP top drivers + forecast stats are passed to Llama 3
- Llama 3 generates plain English business explanations
- Falls back to rule-based explanation if Ollama is unavailable

---

## 📊 Dataset

- **73,100 rows** of retail store inventory data
- **5 stores** × **multiple products** × **2 years** of daily data
- Features: Units Sold, Price, Discount, Weather, Promotions, Competitor Pricing, Seasonality

---

## 🐳 Docker Deployment

```bash
docker compose up --build
```

Services started:
- Backend API on port `8000`
- Frontend on port `3000`
- Ollama on port `11434`
- Redis on port `6379`

---

## ✅ Running Tests

```bash
cd backend
PYTHONPATH=. pytest tests/ -v
```

---

## 🌟 Key Features

- **Zero manual training** — models train automatically on first API request and cache in memory
- **SHAP explainability** — every forecast shows which features drove the prediction
- **LLM reasoning** — Llama 3 explains trends and reorder decisions in plain English
- **LangChain ReAct agent** — conversational interface for inventory Q&A
- **Fallback handling** — works even when Ollama is slow or unavailable
- **Production ready** — async FastAPI, structured logging, Pydantic validation, Docker support
