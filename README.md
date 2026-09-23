# AI Weather Nowcasting System

Hyper-local, real-time severe weather risk prediction and early warning intelligence platform for India.

---

## 1. Project Overview

The **AI Weather Nowcasting System** is a production-grade, real-time weather risk prediction and early warning intelligence platform. It continuously monitors hundreds of zones across India, analyzes real-time meteorological metrics, and categorizes localized threats into actionable risk levels: **High**, **Moderate**, and **Low**. 

By focusing on rapid nowcasting (0 to 6 hours), the system delivers immediate, high-fidelity alerts for critical convective weather events such as thunderstorms, cloudbursts, and flash floods before they cause severe damage to communities and infrastructure.

---

## 2. Problem Statement

Traditional regional weather forecasts operate on macro-scale geographical grids and update over extended intervals (6 to 24 hours). This creates serious vulnerabilities during severe convective weather events:
- **Delayed Warnings**: Sudden meteorological anomalies like cloudbursts and flash floods develop within minutes, often striking before conventional warnings are issued.
- **Lack of Hyper-Local Granularity**: City-wide or district-wide alerts fail to identify which municipal ward, coastal zone, or river basin is at imminent risk.
- **Data Inconsistencies & Fragmented Feeds**: Emergency personnel and citizens often face conflicting reports across disparate sources.
- **High Disaster Vulnerability**: Delayed evacuations, uncoordinated traffic diversions, and unprepared civic drainage systems lead to avoidable loss of lives, livelihoods, and public infrastructure.

---

## 3. Solution

The AI Weather Nowcasting System bridges the critical gap between broad-scale forecasting and hyper-local emergency response:
- **Single Source of Truth Alert Engine**: A centralized pipeline aggregates real-time weather telemetry, computes automated risk indicators, and serves unified, deduplicated data across all interfaces.
- **Instant Risk Classification**: Uses meteorological feature engineering and a calibrated inference engine to detect high-risk thresholds for thunderstorms, cloudbursts, and flash floods.
- **Dynamic Geospatial Visualization**: Interactive Leaflet maps cluster hundreds of monitoring nodes across India, allowing operators to assess national risk at a glance or inspect street-level coordinates.
- **Actionable Guidance**: Every alert pairs severity ratings with concrete, emergency-ready directives (e.g., immediate evacuation, clearance of low-lying drains, or halt of outdoor operations).

---

## 4. Key Features

- **Real-Time Weather Monitoring**: Continuous telemetry tracking for temperature, rainfall rate, humidity, wind speed, pressure, and cloud cover.
- **AI-Driven Risk Prediction**: Multi-hazard risk assessment classifying events into High, Moderate, and Low tiers.
- **Interactive Geospatial Map with Clustering**: High-performance Leaflet mapping with dynamic marker clustering, visual risk halos, and smooth flight transitions.
- **380+ Zones Monitored Simultaneously**: Extensive coverage across all Indian states, union territories, metro hubs, and high-risk climatic belts.
- **Alerts Command Center**: Dedicated alerts management dashboard with multi-criteria filtering, search, and instant refresh.
- **Probability Breakdown**: Granular probability bars for thunderstorms, cloudbursts, and flash floods with explainable weather factor analysis.
- **Professional Dark/Light Mode**: Class-based theme toggle with local storage persistence and zero-flicker reload.
- **Backend Caching & Rate Protection**: Thread-safe in-memory caching and concurrency semaphores to maintain sub-50ms repeat response times while protecting external API quotas.

---

## 5. System Architecture

```text
User / Operator
      │
      ▼
Frontend (React 19 + Tailwind CSS + Leaflet)
      │  HTTP Requests (e.g., /alerts?limit=380)
      ▼
Backend API Layer (FastAPI / Uvicorn)
      │
      ├── In-Memory Cache (TTL Protection & Concurrency Semaphore)
      │
      ▼
Data Acquisition (Weather Telemetry API / Open-Meteo / Nominatim)
      │
      ▼
Feature Engineering & ML Risk Engine
      │ (Rainfall intensity, convective lapse rates, humidity thresholds)
      ▼
Actionable Alert Generator
      │ (Severity categorization, emergency instructions, deduplication)
      ▼
JSON Response -> Frontend Dashboard & Geospatial Visualizer
```

### Layer Breakdown
- **Presentation Layer**: Built with React, Tailwind CSS, and Lucide icons. Delivers responsive navigation, interactive mapping, live metric cards, and charts.
- **API & Orchestration Layer**: Powered by FastAPI with asynchronous request handling, query limits, deduplication mechanisms, and thread-safe caching.
- **Data & Intelligence Layer**: Coordinates real-time API queries, performs atmospheric feature transformation, computes multi-hazard probabilities, and generates actionable advisories.

---

## 6. Data Flow

```text
1. User Accesses Dashboard
   └─ Browser loads React client and initializes theme from localStorage.

2. Frontend Requests Alert Telemetry
   └─ Client dispatches GET request to `/alerts?limit=380`.

3. Cache Verification
   └─ FastAPI checks in-memory cache. If fresh (< 380s old), returns instantly.

4. Data Ingestion & Transformation
   └─ On cache miss, coordinates are gathered, weather data is fetched asynchronously
      under semaphore concurrency limits.

5. Risk Inference & Alert Synthesis
   └─ Atmospheric metrics are processed through the nowcasting engine to compute
      flash flood, cloudburst, and thunderstorm probabilities.

6. Caching & Delivery
   └─ Normalized records are cached and delivered as a unified payload containing
      precomputed summary metrics and deduplicated city records.

7. UI Rendering
   └─ React updates summary metric cards, markers on the Leaflet map cluster,
      and population alerts simultaneously.
```

---

## 7. Tech Stack

- **Frontend**:
  - React 19
  - Tailwind CSS v4
  - React Leaflet & Leaflet MarkerCluster
  - Recharts
  - Lucide React
  - Vite
- **Backend**:
  - Python 3.10+
  - FastAPI
  - Uvicorn (ASGI server)
  - Pydantic
- **ML & Logic**:
  - Python scientific stack (NumPy, Scikit-learn, Pandas)
  - Atmospheric feature engineering and convective instability scoring
- **APIs & Data Sources**:
  - Open-Meteo API
  - OpenStreetMap Nominatim Geocoding
- **Architecture & Performance**:
  - Asynchronous I/O (`asyncio`, `asyncio.Semaphore`)
  - In-memory time-to-live (TTL) caching

---

## 8. Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- Git

### 1. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn main:app --reload --port 8000
```
Backend will be live at `http://127.0.0.1:8000` (API documentation: `http://127.0.0.1:8000/docs`).

### 2. Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend/frontend-react

# Install npm dependencies
npm install

# Start development server
npm run dev
```
Frontend will be accessible at `http://localhost:5173`.

---

## 9. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/alerts` | Returns precomputed summary (`total`, `high`, `moderate`, `low`) and deduplicated active weather alerts. Accepts `limit` query param (default: 380). |
| `GET` | `/zones` | Returns monitored zone telemetry and risk statuses across Indian geographical nodes. |
| `GET` | `/dashboard` | Unified feed providing synchronized metrics and layer coordinates for map rendering. |
| `POST` | `/predict` | On-demand single-location inference taking coordinates (`lat`, `lon`) and location name to compute real-time risk scores. |
| `POST` | `/batch_predict` | Asynchronous batch inference for custom coordinate arrays. |
| `GET` | `/health` | System health check and model initialization status. |

---

## 10. Performance & Scaling

- **380+ Hyper-Local Nodes**: Capable of evaluating 380+ micro-zones across India in parallel without API rate exhaustion.
- **Asynchronous Concurrency Control**: Uses `asyncio.Semaphore` (capped at 20-25 workers) to prevent socket starvation and maintain smooth burst handling.
- **In-Memory Cache (TTL)**: Thread-safe caching retains computed nowcasts for 380 seconds, ensuring repeat queries resolve in under 50ms and counts never flicker on refresh.
- **Optimized Leaflet Map Rendering**: Utilizes cluster chunking and viewport-based marker culling to ensure smooth 60fps pan/zoom performance even on mobile hardware.

---

## 11. UI/UX Highlights

- **Clean Dashboard**: Data-dense yet uncluttered dashboard inspired by Linear and Stripe design systems.
- **Seamless Theme Toggling**: Integrated Dark and Light themes with persistent state and anti-flicker pre-hydration.
- **Geospatial Risk Clustering**: Smart marker aggregation groups nearby nodes and expands smoothly on click.
- **Micro-Interactions**: Smooth scale feedback, subtle hover highlights, and intuitive collapsible alert panels.
- **Zero Layout Shifts**: Engineered with strict height constraints and responsive flex structures to eliminate visual stutter.

---

## 12. Future Improvements

- **Deep Learning Nowcasting**: Integration of ConvLSTM and U-Net models for radar precipitation echo extrapolation.
- **Model Explainability (SHAP / LIME)**: Transparent feature attribution dashboards explaining atmospheric drivers to meteorologists.
- **INSAT-3D & Radar Fusion**: Ingestion of live satellite imagery and Doppler Weather Radar (DWR) composite grids from IMD.
- **Automated Multi-Channel Alerting**: Webhooks, SMS emergency broadcasts, and WhatsApp notifications for local disaster management cells.

---

## 13. Use Cases

- **Disaster Management Authorities (NDRF / SDRF)**: Pre-positioning rescue personnel and heavy machinery in high-risk zones hours ahead of flooding.
- **Municipal Corporations & Smart Cities**: Managing storm-water drainage gates, proactive traffic diversions, and public advisory announcements.
- **Agriculture & Supply Chain Logistics**: Protecting perishable agricultural logistics and rerouting transport fleets away from active convective paths.
- **Aviation & Maritime Operations**: Early tactical awareness for localized airfield downdrafts and coastal storm surge risks.

---

## 14. Conclusion

The **AI Weather Nowcasting System** transforms raw meteorological telemetry into actionable, hyper-local life-saving intelligence. By uniting predictive machine learning, high-concurrency API engineering, and responsive geospatial visualization, it provides emergency planners, municipal administrators, and citizens with the advance warning needed to mitigate weather disasters before they strike.

---

## 15. Author

Developed by **Rakesh Dinda**  
*AI Weather Nowcasting System — Hyper-Local Early Warning for a Safer Tomorrow*
