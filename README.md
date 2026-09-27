# 🌦️ AI Weather Nowcasting & Early Warning System

An intelligent, real-time meteorological monitoring and short-term risk prediction platform designed to detect hyper-local severe weather threats and generate actionable early warnings before disaster strikes.

---

## 🚀 Overview

### The Problem
Extreme and localized weather anomalies—such as cloudbursts, severe thunderstorms, and sudden flash floods—develop within short windows of 30 to 120 minutes. Traditional numerical weather models are designed for macro-scale forecasts spanning 24 to 48 hours over entire districts or states. They lack the hyper-local precision and rapid update frequency needed to detect micro-scale convective events. Furthermore, conventional weather apps report raw technical metrics (e.g., pressure in hPa or humidity percentages) without translating them into immediate, life-saving actions. This leaves citizens, municipal administrators, and emergency responders unprepared during rapid climate escalations.

### The Solution
The **AI Weather Nowcasting & Early Warning System** bridges the gap between raw atmospheric telemetry and emergency response. It ingests live weather observations, computes convective instability and moisture indices via automated feature engineering, and uses a calibrated machine learning model alongside domain safety rules to predict localized risk levels (**Low**, **Moderate**, and **High**) for the next 0 to 4 hours. Instead of delivering ambiguous data, the system outputs clear, plain-language actionable advisories directly to an interactive geospatial dashboard.

---

## 🎯 Key Features

- **Real-Time Weather Ingestion:** Continuously fetches live atmospheric metrics including temperature, relative humidity, precipitation rate, wind speed, and atmospheric pressure via the OpenWeather API.
- **ML-Based Risk Prediction:** Combines a trained Random Forest classifier with meteorological thresholding to identify hazard tiers while eliminating false alarms during dry weather.
- **Actionable Alerts System:** Converts numerical hazard scores into concrete defensive directives (e.g., immediate evacuation notices, stormwater pump activation, or indoor shelter advisories).
- **Scalable Multi-Zone Monitoring:** High-concurrency architecture capable of evaluating up to ~380 geographical zones across India simultaneously.
- **Interactive Dashboard:** Geospatial mapping built with Leaflet, featuring color-coded threat markers, dynamic fly-to zooming, live telemetry cards, and nationwide risk summaries.
- **Dark / Light Mode UI:** Built-in theme switcher with persistent local storage state and high-contrast accessibility.
- **Fault-Tolerant Fallback System:** Deterministic climatological fallback generator ensures zero downtime and consistent testability even during API rate limits or network outages.

---

## 🧠 System Architecture

```text
User → Frontend (React) → Backend (FastAPI) → Weather API  
                                     ↓  
                                 ML Model  
                                     ↓  
                                  Alerts  
```

### Architectural Layers

- **Presentation Layer (React + Leaflet):** Provides responsive UI, live telemetry visualization, interactive map rendering, and one-click dark/light theme toggles.
- **API & Orchestration Layer (FastAPI):** Asynchronous ASGI server managing concurrent zone processing, query caching, and parameter validation.
- **Data Acquisition Layer (OpenWeather API):** Ingests live observational readings; gracefully switches to the deterministic climatological fallback engine if credentials or networks fail.
- **Intelligence & Alert Layer (Scikit-learn & Rule Engine):** Executes feature engineering, runs inference through the Random Forest model, and synthesizes prioritized actionable directives.

---

## 🔄 Data Flow

The end-to-end data pipeline follows a structured 7-step sequence:

```
[1. User selects city / zone]
             │
             ▼
[2. Backend fetches live weather data]
             │
             ▼
[3. Feature engineering applied (Moisture Index, Instability Index, Rain Intensity)]
             │
             ▼
[4. ML model & hybrid rules predict risk (Low / Moderate / High)]
             │
             ▼
[5. Actionable alert generated with safety recommendations]
             │
             ▼
[6. Structured JSON payload delivered to frontend]
             │
             ▼
[7. UI updates map markers, detail cards, and alert banner]
```

1. **User Action:** The user opens the dashboard or searches for a specific location.
2. **Telemetry Ingestion:** The FastAPI backend fetches live atmospheric readings from OpenWeather or cached nodes.
3. **Feature Engineering:** Computes composite indices:
   - $\text{Moisture Index} = \text{Humidity} \times \text{Rainfall}$
   - $\text{Instability Index} = \text{Temperature} \times \text{Humidity}$
   - $\text{Rain Intensity} = \text{Rainfall} \times \text{Wind Speed}$
4. **Model Inference:** Engineered features are passed into the trained ML model (`rainfall_model_v2.pkl`) and checked against domain safety boundaries.
5. **Alert Synthesis:** The alert engine evaluates the risk severity and attaches actionable safety instructions.
6. **Data Delivery:** Sanitized JSON payload with coordinates, metrics, risk tier, probabilities, and advice is returned.
7. **UI Synchronization:** React re-renders map markers, metric cards, and the centralized alert banner in real time.

---

## ⚙️ Tech Stack

### Frontend
- **React 19** - Modern component-based user interface
- **Tailwind CSS v4** - Utility-first styling and theme tokens
- **Vite** - High-speed frontend build tooling and local dev server
- **React-Leaflet** - Geospatial map rendering and interactive markers
- **Lucide React** - Clean, modern iconography

### Backend
- **FastAPI** - Modern, asynchronous, high-performance web framework for Python
- **Uvicorn** - Production-grade ASGI web server
- **Pydantic** - Robust request validation and settings management
- **HTTPX** - High-concurrency asynchronous HTTP client for parallel API calls

### Data & ML
- **NumPy** - High-performance numerical computations and feature vector processing
- **Pandas** - Location dataset management and coordinate manipulation
- **Scikit-learn** - Machine learning classification algorithms (Random Forest)
- **Joblib** - Fast serialization and loading of trained model artifacts

### APIs & Data Sources
- **OpenWeather API** - Real-time global atmospheric telemetry
- **Deterministic Climatological Fallback Engine** - Built-in zero-dependency offline mock

---

## 📦 Project Structure

```text
ai-weather-nowcasting/
├── backend/          # FastAPI application, route handlers, and API schemas
├── frontend/         # React client, UI components, Leaflet maps, and Tailwind styles
├── utils/            # Atmospheric feature engineering, weather fetcher, and alert engines
├── models/           # Pre-trained machine learning model artifacts (.pkl) and training scripts
├── scripts/          # Data preprocessing, label recalculation, and model training utilities
└── data/             # Historical Indian meteorological records and location coordinate CSVs
```

---

## ⚡ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

---

### 1. Clone the Repository
```bash
git clone <repo_url>
cd ai-weather-nowcasting
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\activate
# Linux / macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Backend Server
```bash
uvicorn main:app --reload --port 8000
```
- API is running at: `http://127.0.0.1:8000`
- Interactive Swagger docs: `http://127.0.0.1:8000/docs`

### 4. Frontend Setup
```bash
# Open a new terminal and navigate to frontend directory
cd frontend/frontend-react

# Install npm dependencies
npm install

# Start development server
npm run dev
```
- Frontend will be accessible at: `http://localhost:5173`

---

## 🔑 Environment Variables

The project uses a `.env` file located in the project root or `backend/` directory to store sensitive credentials:

```ini
# OpenWeather API Key for live atmospheric telemetry
OPENWEATHER_API_KEY=your_api_key_here
```

> **Note:**
> - The `.env` file is excluded from version control via `.gitignore` to prevent secret leakage.
> - A reference template `.env.example` is provided in the repository.
> - **Fallback Mode:** If no API key is supplied, the system automatically runs on its built-in climatological fallback engine without errors.

---

## 📊 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Verifies service health, active ML model, and system status. |
| `POST` | `/predict` | Computes on-demand nowcast prediction and alert for a specified city or coordinate pair. |
| `GET` | `/alerts` | Returns precomputed risk summaries (`total`, `high`, `moderate`, `low`) and active warnings. |
| `GET` | `/zones?limit=` | Fetches real-time status and telemetry for multiple monitored Indian zones (supports limit). |
| `GET` | `/nowcast?city=` | Instant weather query and nowcast inference for a specific target city. |

---

## 🎨 UI Features

- **Clean Command Dashboard:** Data-dense, uncluttered layout showing real-time atmospheric threat posture at a glance.
- **Geospatial Map Visualization:** Interactive Leaflet map with color-coded circular markers (Green: Low, Orange: Moderate, Red: High) and smooth camera transitions.
- **Actionable Alert Cards:** Highlighted threat notifications containing specific emergency recommendations rather than ambiguous numbers.
- **Interactive Micro-Interactions:** Subtle hover states, animated risk badges, and glowing selection indicators.
- **Persistent Dark / Light Theme:** Instant toggling between dark and light modes with zero-flicker reload and local storage state persistence.

---

## ⚡ Performance Optimizations

- **Asynchronous API Calls:** Non-blocking network I/O using `httpx.AsyncClient` enables rapid data acquisition.
- **Batch Processing:** Concurrent processing of hundreds of geographic zones in parallel.
- **Smart In-Memory Caching:** 300-second TTL cache eliminates redundant external calls, keeping repeat query latency under 50ms.
- **Concurrency Control:** Managed with `asyncio.Semaphore` to protect upstream API quotas and prevent socket starvation.

---

## 🔒 Security

- **Environment-Isolated Secrets:** External API credentials are kept strictly in `.env` files and loaded via `python-dotenv`.
- **Git Protection:** `.gitignore` rules prevent accidentally committing `.env`, virtual environments (`venv/`), build artifacts, or secret keys.
- **Input Validation:** Strict Pydantic models validate incoming API payloads, types, and coordinate ranges.

---

## 📈 Future Improvements

- **SHAP / LIME Explainability:** Integration of feature attribution graphs so meteorologists can see exact atmospheric drivers behind predictions.
- **External Risk Signal Fusion:** Incorporating river gauge levels, civic drainage topography, and urban population density.
- **Multi-Channel Alert Dispatch:** Automated push notifications, emergency SMS broadcasts, and webhook integrations for disaster relief cells.
- **Doppler Radar & Satellite Overlay:** Live integration of IMD Doppler radar reflectivity feeds directly onto the map visualizer.

---

## 👥 Team

- **Rakesh Dinda** - Project Lead & Full-Stack / AI Architect
- *Open for Open-Source Contributors & Hackathon Collaborators*

---

## 🏁 Conclusion

The **AI Weather Nowcasting & Early Warning System** delivers an end-to-end, production-grade solution to the challenge of unpredictable micro-weather disasters. By uniting real-time API telemetry, automated atmospheric feature engineering, calibrated machine learning, and an intuitive geospatial dashboard, the platform turns raw weather data into decisive, life-saving early warnings. Built with high concurrency, fault-tolerant fallbacks, and a modern design system, it stands as an impactful, scalable, and hackathon-winning platform ready for real-world deployment.
