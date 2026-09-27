# Integration Report: AI Weather Nowcasting & Early Warning System

> **Document Type:** Technical Integration Specification & Architecture Audit  
> **Target Audience:** Machine Learning Engineering Team & Backend/Frontend Integrators  
> **Status:** Read-Only Audit Complete  

---

## 1. Stack & Running

### Frontend
- **Framework & Version:** React `19.2.8` bootstrapped with Vite `8.3.0` (ES modules, JSX)
- **Map Library:** Leaflet `1.9.4`, `react-leaflet` `5.0.0`, `react-leaflet-cluster` `4.1.3` (marker clustering), `leaflet.heat` `0.2.0`
- **Charting Library:** Recharts `2.8.0` (with React 19 compatibility overrides)
- **Styling:** Tailwind CSS `4.3.3` with `@tailwindcss/postcss`
- **Iconography:** Lucide React `1.47.0`
- **Routing:** React Router DOM `7.18.4` (`/`, `/forecast`, `/analytics`, `/alerts`, `/reports`)
- **State Management:** React component-level hooks (`useState`, `useRef`, `useCallback`, `useMemo`), lifted state in `Dashboard.jsx`, and browser `localStorage` (for `selected_city` and UI theme). No external Redux or Zustand store.

### Backend
- **Framework & Version:** FastAPI `0.141.1`, ASGI server Uvicorn `0.54.0`
- **Language & Runtime:** Python 3.10+ (Current active virtual environment: Python 3.14.7)
- **Scientific & ML Libraries:**
  - `scikit-learn` `1.9.1` (Random Forest model inference)
  - `pandas` `3.0.6` (tabular data manipulation & district coordinate index)
  - `numpy` `2.5.3` (feature vector processing)
  - `joblib` `1.6.0` (model & label encoder deserialization)
  - `pydantic` `2.13.5` (request schema validation)
  - `httpx` `0.28.1` (asynchronous non-blocking HTTP client)
  - `requests` `2.34.2` (synchronous HTTP client)
  - `python-dotenv` `1.2.3` (environment management)
- **Database:** None (No SQL or NoSQL database). Monitored points are loaded into memory from `data/india_locations.csv`, and results are retained in an in-memory TTL dictionary cache (`_UNIFIED_ALERTS_CACHE`, 300s TTL).
- **External Services:**
  - OpenWeatherMap Current Weather & Geocoding API
  - OpenStreetMap Nominatim Geocoding API (client-side search fallback)
  - Internal Deterministic Climatological Mock Generator (offline fallback)

### Exact Commands to Install & Run Locally

#### Backend Setup
```bash
cd backend
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\activate
# Linux / macOS:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
- **Port:** `8000` (`http://127.0.0.1:8000`)
- **Interactive OpenAPI Documentation:** `http://127.0.0.1:8000/docs`

#### Frontend Setup
```bash
cd frontend/frontend-react
npm install
npm run dev
```
- **Port:** `5173` (`http://localhost:5173`)
- **Vite Proxy / Backend Target:** Frontend makes direct CORS-enabled requests to `http://127.0.0.1:8000`.

### Operating System Assumptions
- Cross-platform compatible (Windows 10/11, Linux, macOS).
- File paths in Python use `os.path.join` and `pathlib` for agnostic separator resolution.

### Environment Variables & Config Files
- **Backend Configuration:** `.env` located at project root or `backend/.env`
- **Variable Names (Never hardcode secrets):**
  - `OPENWEATHER_API_KEY`: API key for live external weather telemetry. (If missing, invalid, or exhausted, the system automatically engages the built-in deterministic fallback generator without crashing).

### Hardware & Resource Footprint
- **RAM:** ~1.5 GB to 2.5 GB total
  - Backend + loaded scikit-learn models: ~350 MB to 500 MB
  - Frontend Vite dev server + Node: ~300 MB to 500 MB
  - Client Browser (rendering Leaflet map clusters): ~500 MB to 800 MB
- **CPU:** Dual-core minimum (4 cores recommended for asynchronous batch nowcasting).

---

## 2. Project Structure

```text
ai-weather-nowcasting/
├── backend/                              # FastAPI application & server configuration
│   ├── main.py                           # API routes, caching, and hybrid pipeline orchestration
│   └── requirements.txt                  # Python dependencies pinned for Python 3.10+
├── frontend/frontend-react/              # React 19 single-page application
│   ├── src/
│   │   ├── components/                   # Reusable UI widgets
│   │   │   ├── MapSection.jsx            # Leaflet map container, station markers & cluster group
│   │   │   ├── RightPanel.jsx            # Detailed city inspection, probability bars & alert card
│   │   │   ├── AlertBanner.jsx           # Top alert banner with dynamic nationwide count
│   │   │   ├── Timeline.jsx              # Bottom timeline controls
│   │   │   ├── RiskDistribution.jsx      # Summary breakdown of risk levels
│   │   │   ├── TopHeader.jsx             # Search bar, station indicator & theme toggle
│   │   │   └── Sidebar.jsx               # Navigation & hazard layer toggles
│   │   ├── pages/                        # Main routed views
│   │   │   ├── Dashboard.jsx             # Primary interactive command map & monitoring interface
│   │   │   ├── Forecast.jsx              # 0-4h lead time trajectory charts & station predictions
│   │   │   ├── Alerts.jsx                # Filterable emergency warnings command center
│   │   │   ├── Analytics.jsx             # Aggregated regional risk charts (Recharts)
│   │   │   └── Reports.jsx               # Exportable incident summaries & compliance log
│   │   ├── services/
│   │   │   └── api.js                    # Axios client functions for backend endpoints
│   │   ├── App.jsx                       # React Router configuration
│   │   └── main.jsx                      # DOM mount & root styles
│   └── package.json                      # Frontend dependencies & scripts
├── utils/                                # Data ingestion, feature engineering & model runners
│   ├── api_fetcher.py                    # OpenWeather API client + deterministic fallback mock
│   ├── locations_manager.py              # In-memory manager for 790+ Indian location coordinates
│   ├── v2_predictor.py                   # Random Forest loader, label encoders & hybrid risk evaluator
│   └── alert_system.py                   # Rule-based actionable directive generator
├── models/                               # Pre-trained ML binaries and serialization metadata
│   ├── rainfall_model_v2.pkl             # Trained Random Forest classifier
│   ├── rainfall_model_v2_meta.pkl        # LabelEncoders for Indian states and districts
│   └── scaler.pkl                        # Feature normalization scaler
├── scripts/                              # Dataset ETL, IMD preprocessing & training pipelines
├── data/                                 # Static location dictionaries & training records
│   └── india_locations.csv               # 790+ Indian district coordinates (lat, lon, state)
├── requirements.txt                      # Project-root Python dependencies
└── README.md                             # Project overview and hackathon documentation
```

---

## 3. Backend API

All endpoints return JSON and are CORS-enabled (`allow_origins=["*"]`). Authentication is currently **not required** (open endpoints for hackathon prototype evaluation).

### 1. Health Check
- **Path:** `GET /health`
- **Query / Body Params:** None
- **Status Codes:** `200 OK`
- **Response Shape:**
  ```json
  {
    "status": "ok",
    "version": "7.0.0",
    "system": "Real-Time Weather AI System",
    "model": "rainfall_model_v2.pkl",
    "logic": "Hybrid (Live Weather Rule Override + ML Inference)",
    "features": ["month", "day", "state_enc", "district_enc"],
    "total_india_locations": 791,
    "cached_geo_points": 142
  }
  ```

### 2. On-Demand Single Location Prediction
- **Path:** `POST /predict`
- **Query Params:** None
- **Body Schema (`PredictionRequest`):**
  ```json
  {
    "city": "Mumbai",
    "location": "Mumbai",
    "lat": 19.0760,
    "lon": 72.8777
  }
  ```
- **Status Codes:** `200 OK`, `400 Bad Request` (if city name missing)
- **Response Shape:**
  ```json
  {
    "city": "Mumbai",
    "state": "Maharashtra",
    "lat": 19.076,
    "lon": 72.8777,
    "risk_level": "LOW",
    "risk": "LOW",
    "temperature": 29.5,
    "humidity": 68.0,
    "rainfall": 0.0,
    "wind_speed": 3.2,
    "timestamp": "2026-09-27T21:40:00.000000",
    "reason": "Normal atmospheric conditions",
    "alert": {
      "type": "Normal",
      "severity": "LOW",
      "action": "No immediate defensive action required."
    },
    "explanation": "Dry and calm conditions: minimal weather hazard",
    "weather": {
      "temperature": 29.5,
      "humidity": 68.0,
      "rainfall": 0.0,
      "wind_speed": 3.2,
      "wind": 3.2,
      "pressure": 1011.0
    },
    "probabilities": {
      "thunderstorm": 0.12,
      "cloudburst": 0.05,
      "flash_flood": 0.08
    },
    "prediction": {
      "prob_thunderstorm": 0.12,
      "prob_cloudburst": 0.05,
      "prob_flood": 0.08,
      "confidence": 0.85,
      "risk_level": "LOW",
      "risk_text": "LOW",
      "reason": "Normal atmospheric conditions"
    }
  }
  ```

### 3. Unified Alerts & Zones Feed (Single Source of Truth)
- **Path:** `GET /alerts` (Aliases: `GET /zones`, `GET /dashboard`, `GET /analytics`)
- **Query Params:** `limit: int = 380` (default 380 zones)
- **Status Codes:** `200 OK`
- **Response Shape:**
  ```json
  {
    "summary": {
      "total": 380,
      "high": 48,
      "moderate": 92,
      "low": 240
    },
    "alerts": [
      {
        "id": 0,
        "city": "Mumbai",
        "fullName": "Mumbai",
        "state": "Maharashtra",
        "lat": 19.076,
        "lon": 72.8777,
        "risk_level": "LOW",
        "risk": "LOW",
        "severity": "LOW",
        "type": "Normal",
        "hazard": "Normal",
        "message": "Normal in Mumbai (Rain: 0.0 mm, Wind: 3.2 m/s)",
        "action": "No immediate defensive action required.",
        "reason": "Normal atmospheric conditions",
        "temperature": 29.5,
        "humidity": 68.0,
        "rainfall": 0.0,
        "wind_speed": 3.2,
        "timestamp": "2026-09-27T21:40:00.000000",
        "weather": {
          "temperature": 29.5,
          "humidity": 68.0,
          "rainfall": 0.0,
          "wind_speed": 3.2,
          "wind": 3.2,
          "pressure": 1011.0
        },
        "prediction": {
          "risk_level": "LOW",
          "risk_label": 0,
          "risk_text": "LOW",
          "probability": 0.85,
          "prob_flood": 0.08,
          "prob_thunderstorm": 0.12,
          "prob_cloudburst": 0.05,
          "reason": "Normal atmospheric conditions"
        },
        "probabilities": {
          "flash_flood": 0.08,
          "thunderstorm": 0.12,
          "cloudburst": 0.05
        },
        "alert": {
          "type": "Normal",
          "severity": "LOW",
          "action": "No immediate defensive action required."
        }
      }
    ],
    "last_updated": "2026-09-27T21:40:00.000000"
  }
  ```

### 4. Batch Prediction Feed
- **Path:** `GET /batch_predict`
- **Query Params:** `limit: int = 380`, `state: Optional[str] = None`
- **Status Codes:** `200 OK`
- **Response Shape:** Flat JSON array of alert objects (matching the `alerts` array from `/alerts`).

### 5. Instant Nowcasting
- **Path:** `GET /nowcast`
- **Query Params:** `city: str` (e.g., `?city=Pune`)
- **Status Codes:** `200 OK`, `{"error": "Location not found"}`

### Current Data Sourcing
- **Location Coordinates:** `data/india_locations.csv` loaded by `utils/locations_manager.py`.
- **Live Weather Data:** `utils/api_fetcher.py` queries `https://api.openweathermap.org/data/2.5/weather` via `requests` or `httpx`.
- **Offline / Quota Fallback:** In `utils/api_fetcher.py:get_fallback_mock()`, a deterministic climatological hash generates consistent weather values without pseudo-random jitter.
- **Model Ingestion Mechanism:** In-process Python invocation (`joblib.load()`) of `models/rainfall_model_v2.pkl` and `models/rainfall_model_v2_meta.pkl` called directly within `utils/v2_predictor.py:predict_v2()`. No subprocesses or external microservice calls are currently used.

---

## 4. Frontend

### Views & Data Subscriptions

| Page / Component | Route | Backend API Called | Fields Consumed |
| :--- | :--- | :--- | :--- |
| **Dashboard** (`Dashboard.jsx`) | `/` | `GET /alerts?limit=380`<br>`POST /predict` (search) | `summary` (`total`, `high`, `moderate`, `low`), `alerts[]` (`city`, `lat`, `lon`, `risk`, `weather`, `probabilities`, `reason`, `action`) |
| **Map Section** (`MapSection.jsx`) | Mounted on `/` | Subscribed to `allCities` state | `lat`, `lon`, `risk`, `city`, `weather.temperature`, `weather.rainfall`, `weather.humidity`, `reason` |
| **Right Inspection Panel** (`RightPanel.jsx`) | Mounted on `/` | Subscribed to `selectedCity` state | `city`, `state`, `risk_level`, `weather.*`, `prediction.prob_thunderstorm`, `prediction.prob_cloudburst`, `prediction.prob_flood`, `reason`, `alert.action`, `timestamp` |
| **Forecast View** (`Forecast.jsx`) | `/forecast` | `GET /batch_predict?limit=100`<br>`GET /nowcast?city=` | `city`, `forecast[]` (`hour`, `rainfall`, `humidity`, `wind_speed`, `temperature`, `risk`), `probabilities.*` |
| **Alerts Command Center** (`Alerts.jsx`) | `/alerts` | `GET /alerts?limit=380` | `summary.*`, `alerts[]` (`id`, `city`, `state`, `severity`, `type`, `message`, `action`, `rainfall`, `wind_speed`, `timestamp`) |
| **Analytics View** (`Analytics.jsx`) | `/analytics` | `GET /batch_predict?limit=100` | Aggregates `risk_level`, `rainfall`, `humidity`, `wind_speed` across locations into Recharts bar/pie charts |
| **Reports View** (`Reports.jsx`) | `/reports` | `GET /alerts` | `summary.*`, `alerts[]` for generating incident logs |

### Map Layer Mechanism
- **Layer Type:** Point vector markers (`L.marker` / `react-leaflet.Marker`) aggregated inside `<MarkerClusterGroup>` from `react-leaflet-cluster`.
- **Base Tile Layer:** OpenStreetMap raster tiles (`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`).
- **Coordinate Expectation:** WGS84 `[lat, lon]` (latitude first, longitude second).
- **Missing Map Layers:** No GeoJSON polygon rendering layer is currently mounted in `MapSection.jsx`. Raster layers (GeoTIFFs / XYZ heat tiles) are not currently ingested or rendered.

### Severity & Alert Styling
- **Colors:**
  - `HIGH`: Red (`#ef4444` / `bg-red-500` / `border-red-200`)
  - `MODERATE`: Amber/Orange (`#f59e0b` / `bg-orange-500` / `border-orange-200`)
  - `LOW`: Emerald/Green (`#10b981` / `bg-emerald-500` / `border-emerald-200`)
- **Labels:** The UI renders risk badges as `"HIGH RISK"`, `"MODERATE RISK"`, and `"LOW RISK"`.
- **Explanations:** Rendered directly from `item.reason` (e.g., *"Heavy rainfall indicates flood risk | High humidity supports storm formation"*).

### Verbatim Frontend Mock / Fallback Payloads

#### Example 1: Alert Item from `GET /alerts`
```json
{
  "id": 14,
  "city": "Bengaluru",
  "fullName": "Bengaluru",
  "state": "Karnataka",
  "lat": 12.9716,
  "lon": 77.5946,
  "risk_level": "MODERATE",
  "risk": "MODERATE",
  "severity": "MODERATE",
  "type": "Heavy Rain",
  "hazard": "Heavy Rain",
  "message": "Heavy Rain in Bengaluru (Rain: 8.5 mm, Wind: 5.2 m/s)",
  "action": "Monitor local water drainage and exercise caution on roadways.",
  "reason": "Moderate convective indicators observed",
  "temperature": 24.2,
  "humidity": 78.0,
  "rainfall": 8.5,
  "wind_speed": 5.2,
  "timestamp": "2026-09-27T16:00:00.000Z",
  "weather": {
    "temperature": 24.2,
    "humidity": 78.0,
    "rainfall": 8.5,
    "wind_speed": 5.2,
    "wind": 5.2,
    "pressure": 1012.0
  },
  "prediction": {
    "risk_level": "MODERATE",
    "risk_label": 1,
    "risk_text": "MODERATE",
    "probability": 0.75,
    "prob_flood": 0.45,
    "prob_thunderstorm": 0.40,
    "prob_cloudburst": 0.35,
    "reason": "Moderate convective indicators observed"
  },
  "probabilities": {
    "flash_flood": 0.45,
    "thunderstorm": 0.40,
    "cloudburst": 0.35
  },
  "alert": {
    "type": "Heavy Rain",
    "severity": "MODERATE",
    "action": "Monitor local water drainage and exercise caution on roadways."
  }
}
```

#### Example 2: Static CSV Record (`public/india_locations.csv` via `api.js`)
```json
{
  "id": 0,
  "city": "Mumbai",
  "fullName": "Mumbai",
  "lat": 19.0760,
  "lon": 72.8777,
  "risk": "LOW",
  "weather": null,
  "prediction": null,
  "isDataset": true
}
```

---

## 5. Gap Analysis (UI / Backend vs ML Model Contract)

*(Note: The remote repository `github.com/phoenix6463mjj-png/nowcast_sih` was confirmed private/404 during research; comparisons below are drawn strictly against the contract specification provided in the handoff brief).*

| Dimension | Current Frontend / Backend Implementation | ML Teammate Model Output | Gap & Required Conversion |
| :--- | :--- | :--- | :--- |
| **Spatial Format** | Discrete point markers `[lat, lon]` for ~380 specific stations from CSV | • Gridded GeoTIFF rasters `prob_L{1,2,3,4,6}h.tif` (0.1° EPSG:4326 grid)<br>• `alerts.geojson` (polygons)<br>• `grids.json` | **Major:** UI cannot natively ingest raw GeoTIFFs without a GeoTIFF-to-PNG/XYZ tile converter. Frontend Leaflet map lacks `<GeoJSON>` component for polygon rendering. |
| **Coordinate Order** | Array `[lat, lon]` in Leaflet markers | GeoJSON standard `[lon, lat]` in `alerts.geojson` | Leaflet `<GeoJSON>` natively expects `[lon, lat]` GeoJSON standard. Point marker code needs `[lat, lon]`. |
| **Lead Times** | Fixed 0 to 4 hours in `Forecast.jsx` (`Now`, `+1h`, `+2h`, `+3h`, `+4h`) | 1, 2, 3, 4, 6 hours (`L1h`, `L2h`, `L3h`, `L4h`, `L6h`) | **Mismatch:** ML model produces Lead 6h (UI currently stops at +4h). ML model does not produce Lead 0h (nowcast leads start at L1h; Lead 0 is observation). |
| **Hazard Types** | Generic labels (`Thunderstorm`, `Heavy Rain`, `Flash Flood`, `Normal`) | `thunderstorm`, `cloudburst`, `flash_flood` | Align string identifiers to lowercase exact matches. |
| **Metrics & Units** | All three metrics rendered as 0–100% probabilities in `RightPanel.jsx` | • Thunderstorm: Probability ($0.0 - 1.0$)<br>• Cloudburst: Risk Index (score)<br>• Flash Flood: Risk Ratio ($> 1.0$ threshold) | **Visual Disconnect:** Cloudburst is an index and Flash Flood is a ratio, but UI displays both as 0–100% percentage bars. Needs metric-specific labeling. |
| **Severity Taxonomy** | `LOW`, `MODERATE`, `HIGH` | `Watch`, `Warning`, `Advisory` (standard IMD/meteorological conventions) | Need 1-to-1 mapping:<br>• `MODERATE` $\leftrightarrow$ `Watch`<br>• `HIGH` $\leftrightarrow$ `Warning`<br>• `LOW` $\leftrightarrow$ `Advisory` / `Normal` |
| **Explainability** | Single text sentence (`item.reason`) | `explain.json` containing SHAP feature attributions, per-alert calculation steps, and impact summary | UI currently lacks a widget to display SHAP contribution bars or calculation steps. |
| **Live vs Replay Validation** | Generic `"Live AI Nowcasting"` status badge | Forecast issue time, replay episodes (26 demo timestamps), `"in-sample"` and `"not validated — live"` tags | UI currently lacks issue time selector and validation status chips. |

---

## 6. System Status

### Operational
- End-to-end full stack communication (React 19 $\leftrightarrow$ FastAPI) active and stable.
- Geospatial station clustering rendering ~380 nodes across India.
- Dynamic city search with geocoding, risk evaluation, and map centering.
- Single source of truth alert counter ensuring zero mismatch between banner and panels.
- Dark and light mode themes working with zero flicker.
- Full offline operational capability via built-in deterministic climatological fallback engine (`utils/api_fetcher.py`). The application can be demonstrated 100% offline without internet or external API keys.

### Partial / Needs Polish
- `Forecast.jsx` timeline currently uses client-side mathematical extrapolation when multi-hour forecast arrays are omitted by the backend.
- Multi-hazard event probabilities (thunderstorm, cloudburst, flash flood) currently use rule-based thresholds on rainfall and wind rather than reading spatial ML grids.

### Missing / TODO for ML Model Integration
- No backend route currently exists to ingest or serve `alerts.geojson`, `grids.json`, `explain.json`, or GeoTIFF files.
- `MapSection.jsx` does not include a `<GeoJSON>` component to render severe-weather polygons over India.
- `Timeline.jsx` lacks a `+6h` button.

---

## 7. Recommended Integration Plan

To connect the ML model with the existing full-stack application with minimal effort and zero disruption to working components, follow this 4-step execution path:

```
[ML Output Folder: alerts.geojson + explain.json + grids.json]
                           │
                           ▼
[Backend Adapter Endpoint: GET /api/v1/forecast/latest]
                           │
                           ▼
[Frontend React: MapSection (<GeoJSON>) + RightPanel (SHAP)]
```

### Step 1: Create a Forecast Ingestion Service in Backend
- **Action:** Create a directory `data/forecasts/latest/` to receive the ML output bundle (`alerts.geojson`, `grids.json`, `manifest.json`, `explain.json`).
- **File to Edit:** `backend/main.py`
- **Implementation:**
  1. Add endpoint `GET /api/v1/forecast/alerts`: reads `alerts.geojson` directly from `data/forecasts/latest/` and returns standard FeatureCollection JSON.
  2. Add endpoint `GET /api/v1/forecast/explain?alert_id=`: returns the calculation steps and SHAP breakdown for the selected alert from `explain.json`.
  3. Map ML `severity` fields:
     - `"Warning"` $\rightarrow$ `HIGH`
     - `"Watch"` $\rightarrow$ `MODERATE`
- **Estimated Effort:** ~2 hours

### Step 2: Render Alert Polygons in React-Leaflet
- **File to Edit:** `frontend/frontend-react/src/components/MapSection.jsx`
- **Implementation:**
  1. Fetch `alerts.geojson` from `http://127.0.0.1:8000/api/v1/forecast/alerts`.
  2. Import `{ GeoJSON }` from `react-leaflet`.
  3. Render polygons with color mapping:
     ```javascript
     <GeoJSON 
       data={alertsGeoJson} 
       style={(feature) => ({
         color: feature.properties.severity === 'Warning' ? '#ef4444' : '#f59e0b',
         weight: 2,
         fillOpacity: 0.35
       })}
       onEachFeature={(feature, layer) => {
         layer.on('click', () => onSelectAlert(feature.properties));
       }}
     />
     ```
- **Estimated Effort:** ~1.5 hours

### Step 3: Align Lead Times (Add 6h Lead)
- **Files to Edit:**
  - `frontend/frontend-react/src/components/Timeline.jsx`
  - `frontend/frontend-react/src/pages/Forecast.jsx`
- **Implementation:** Update `TIMELINE_STEPS` from `["Now", "+1h", "+2h", "+3h", "+4h"]` to `["Now", "+1h", "+2h", "+3h", "+4h", "+6h"]` and pass the selected lead time parameter to the backend.
- **Estimated Effort:** ~45 minutes

### Step 4: Display Explainability & Verification Badges
- **File to Edit:** `frontend/frontend-react/src/components/RightPanel.jsx`
- **Implementation:**
  1. Relabel metric bars:
     - *Thunderstorm:* Probability (`%`)
     - *Cloudburst:* Risk Index (Score)
     - *Flash Flood:* Risk Ratio (e.g., `1.4x Threshold`)
  2. Render SHAP feature importance pills from `explain.json`.
  3. Add status chip: `"Live Snapshot"` or `"In-Sample Replay"`.
- **Estimated Effort:** ~1.5 hours

### Total Estimated Integration Time: ~5 to 6 hours
