# AI Weather Nowcasting System
### Project Documentation

---

## 1. Project Overview

### What the System Is
The **AI Weather Nowcasting System** is a real-time weather monitoring and short-term risk assessment web application. It tracks weather conditions across India and uses a hybrid artificial intelligence model to calculate immediate localized weather risks (such as heavy rain and storm threats) for the next 0 to 4 hours.

### What Problem It Solves
Traditional weather forecasts usually cover large areas (like entire states or broad districts) over 24- to 48-hour periods. They often miss sudden, localized weather shifts—such as sudden cloudbursts, severe localized downpours, or rapid thunderstorms. This system aims to provide quick, location-specific nowcasting to give users immediate awareness of changing weather.

### Why It Is Important
- **Early Warning:** Gives timely alerts for rapidly developing severe weather conditions.
- **Disaster Preparedness:** Helps local administrations, emergency teams, and residents take precautions before heavy downpours lead to waterlogging or localized flooding.
- **Public Safety:** Provides clear, color-coded threat indicators so everyday users can understand risk levels without needing meteorological training.

---

## 2. System Architecture

The project is built on a clean full-stack architecture consisting of a React frontend, a FastAPI backend, live weather APIs, and a trained machine learning pipeline.

```
[ User / Browser ]
        │
        ▼
[ React Frontend Dashboard ]
        │  HTTP Requests (GET /batch_predict, POST /predict)
        ▼
[ FastAPI Backend (v7.0) ]
        │
        ├─► [ OpenWeather API ] (Live temperature, humidity, rain, wind)
        │
        └─► [ ML Model & Hybrid Logic ] (Feature extraction & Risk calculation)
        │
        ▼
[ JSON Response ] ──► [ React UI (Map, Right Panel, Alert Banner) ]
```

### Components:
1. **Frontend (React Dashboard):**
   - Built with React, Vite, Tailwind CSS, and React-Leaflet.
   - Manages a single source of truth for location data and user selections.
   - Renders interactive map markers, risk badges, real-time metrics, alert banners, risk distribution analytics, and timeline sliders.
   - Includes seamless dark mode support (`ThemeToggle`).
2. **Backend (FastAPI v7.0.0):**
   - Built with Python and FastAPI.
   - Serves endpoints:
     - `GET /batch_predict`: Fetches and processes risk for a grid of 150-200 Indian locations concurrently.
     - `POST /predict`: Fetches weather and computes risk for a single searched city.
     - `GET /health`: Health-check endpoint.
3. **Data Source (OpenWeather API):**
   - Supplies live real-time atmospheric readings:
     - Temperature (°C)
     - Relative Humidity (%)
     - Current Rainfall (mm)
     - Wind Speed (m/s)
4. **Machine Learning & Hybrid Logic:**
   - **Model:** A Random Forest Classifier (`rainfall_model_v2.pkl`) trained on historical IMD rainfall and weather patterns.
   - **Encoders:** Categorical metadata (`rainfall_model_v2_meta.pkl`) mapping states and districts.
   - **Hybrid Rules Engine:** Combines live rainfall thresholds, physical safety rules, and model predictions to prevent false alarms during dry weather.

### Step-by-Step Data Flow:
1. **User Action:** The user opens the dashboard or searches for a city.
2. **API Call:** The frontend sends an HTTP request (`GET /batch_predict` or `POST /predict`) to the FastAPI backend.
3. **Live Data Ingestion:** The backend queries OpenWeather API using city coordinates or name.
4. **Feature Assembly & ML Prediction:** The backend prepares features (month, coordinates, weather metrics) and passes them to the Random Forest model.
5. **Hybrid Logic Check:** The backend applies safety rules (e.g., if live rain is low and wind is calm, it prevents high-risk false alarms).
6. **Response Delivery:** The backend returns structured JSON containing weather data, `risk_label` (0, 1, 2), `risk_text` (LOW, MODERATE, HIGH), individual probabilities, and an explanation.
7. **UI Update:** The React dashboard updates the map marker colors, right-side detail panel, and alert banner simultaneously.

---

## 3. Core Features (Implemented)

- **Real-Time Weather Ingestion:**
  Fetches live measurements for temperature, humidity, rainfall, and wind speed via OpenWeather API.
- **AI-Based Risk Classification:**
  Categorizes weather risk into three distinct levels:
  - `LOW` (Risk level 0) - Green
  - `MODERATE` (Risk level 1) - Orange
  - `HIGH` (Risk level 2) - Red
- **Hybrid Risk Logic:**
  Combines machine learning output with deterministic safety rules (e.g., rainfall $\ge$ 20 mm triggers HIGH risk; dry and calm conditions enforce LOW risk).
- **Interactive Nationwide Map:**
  Displays a map of India with 150+ monitored locations plotted as color-coded circular markers.
- **Dynamic Selection & Map Fly-To:**
  Clicking any city marker or searching for a city centers the map on that location and highlights it with a glowing halo ring.
- **Detailed City Inspection Panel:**
  Displays the selected city's exact temperature, humidity, rainfall, wind speed, risk level badge, and an atmospheric explanation.
- **Centralized Alert Banner:**
  Dynamically evaluates all active locations:
  - Displays `"High Risk in X locations"` if any high-risk zone is detected.
  - Displays `"Moderate Risk present"` if moderate-risk areas exist.
  - Displays `"All Clear"` if all monitored areas are calm.
- **Dark Mode Support:**
  Seamless dark mode toggle for low-light environments.
- **Forecast Timeline & Risk Analytics:**
  Interactive 6-hour forecast timeline slider and regional risk distribution summary panel.
- **Multi-Page Navigation Framework:**
  Provides structured navigation between application sections: Dashboard, Forecast, Analytics, Alerts, and Reports.

---

## 4. How the System Works (Step-by-Step)

1. **Dashboard Initialization:**
   - The user opens the dashboard.
   - The dashboard fires a single request to `GET /batch_predict?limit=150`.
2. **Backend Weather Processing:**
   - The backend reads coordinates for Indian districts.
   - Queries OpenWeather for live conditions at each point concurrently using httpx.AsyncClient.
3. **Hybrid Risk Calculation:**
   - For each location, the backend evaluates live rainfall and wind against predefined risk boundaries.
   - Passes encoded features through the Random Forest model.
   - Computes event probability scores for thunderstorm, cloudburst, and flood events.
   - Assigns final risk score and generates a human-readable explanation.
4. **Data Transmission:**
   - The sorted list of locations (prioritizing high-risk areas) is returned to the frontend.
5. **UI Synchronization:**
   - Map renders color-coded circle markers across India.
   - The top alert banner updates to reflect nationwide threat counts.
   - The Risk Distribution panel updates with the exact count of Critical, High, Medium, and Low risk locations.
   - The right panel displays the primary selected location's full atmospheric breakdown.

---

## 5. Current System Output

When a user interacts with the live application, they see:

- **Interactive Map:**
  - 150+ markers across India.
  - Visual status color:
    - 🟢 Green: Low risk / calm conditions
    - 🟠 Orange: Moderate advisory / rain alert
    - 🔴 Red: High risk / severe downpour warning
- **Selected Location Panel:**
  - City name and state.
  - Exact coordinates (Latitude & Longitude).
  - Risk Status Badge (`LOW RISK`, `MODERATE RISK`, or `HIGH RISK`).
  - Atmospheric explanation (e.g., *"Dry and calm conditions: minimal weather hazard"* or *"Heavy rainfall detected"*).
  - Live metric cards: Temperature (°C), Humidity (%), Rainfall (mm), Wind Speed (m/s).
  - Risk indicator bars for Thunderstorm, Cloudburst, and Flash Flood probabilities.
- **Dynamic Alert Banner & Analytics:**
  - Real-time status summarizing monitored locations (`"High Risk in X locations"`, `"Moderate Risk present"`, or `"All Clear"`).
  - Risk Distribution Panel summarizing the count of zones across different severity levels.
- **Timeline Slider:**
  - Control to toggle between 'Live Now' and '+X hrs' (up to +6 hrs).

---

## 6. Current Limitations (Honest Assessment)

To maintain transparency during evaluation, the following limitations are present in the current prototype:

- **Heuristic Multi-Event Probabilities:**
  Specific probabilities for Thunderstorm, Cloudburst, and Flash Flood currently rely on formula-based approximations combined with the main rainfall risk rather than dedicated multi-output deep neural networks.
- **Predominantly Low Risk in Dry Periods:**
  During dry, calm seasons or non-monsoon periods across India, most live API readings show zero rainfall and low wind. Consequently, most markers currently show LOW risk.
- **No User Authentication:**
  There is currently no login, user roles, or saved preference profiles implemented.
- **Limited Secondary Modules:**
  While components like Forecast Timeline and Risk Distribution are active on the dashboard, full independent secondary pages for Alerts and Reports are still placeholders.
- **No Historical Trend Tracking:**
  The system currently reflects instant snapshot nowcasting; it does not yet store a database of past historical predictions for retrospective accuracy tracking.

---

## 7. Current Status

- **Working Core Pipeline:** The end-to-end pipeline (live API data fetching $\rightarrow$ feature extraction $\rightarrow$ hybrid ML risk calculation $\rightarrow$ unified React dashboard) is fully functional and stable.
- **Unified State Management:** The frontend adheres strictly to a single-source-of-truth architecture, eliminating data mismatches between the map, right panel, search bar, and alert banner.
- **Stable APIs:** FastAPI backend endpoints (`/predict`, `/batch_predict`, `/health`) are running and handling concurrent queries.
- **Classification Stage:** The system represents a functional working prototype ready for demonstration, rather than a final production-grade meteorology suite.

---

## 8. What Is Left to Complete

The following roadmap items will transition the prototype into a production-ready solution:

1. **Dedicated Multi-Event ML Models:**
   Train separate classifiers for cloudbursts, severe thunderstorms, and flash floods using radar and satellite telemetry data.
2. **Improved Risk Distribution & Simulation Mode:**
   Introduce historical scenario replay (e.g., simulating the 2023 North India floods or Mumbai monsoon downpours) to demonstrate high-risk states when real-time national weather is calm.
3. **User Authentication & Role Management:**
   Add user sign-in (e.g., public citizen vs. municipal disaster officer) with customizable alert thresholds.
4. **Full Feature Implementation for Secondary Pages:**
   - **Forecast:** Extend the current 6-hour timeline to 12-hour / 24-hour predictive timeline graphs.
   - **Analytics:** Advanced historical analytics and rainfall radar charts.
   - **Alerts:** Automated notification dispatch via SMS / WebPush.
   - **Reports:** Downloadable PDF incident reports for emergency teams.
5. **Real Satellite Doppler Radar Overlay:**
   Integrate live radar tile layers from meteorological radar networks (like IMD Doppler radar feeds) directly onto the Leaflet map.

---

## 9. Conclusion

The **AI Weather Nowcasting System** is a functional prototype that demonstrates real-time localized weather risk assessment for India. By combining live weather telemetry with a hybrid machine learning pipeline and a responsive map dashboard, it establishes a solid architectural foundation for hyper-local early disaster warning. With the planned additions of dedicated multi-event models and historical radar layers, it can evolve into an impactful public safety tool.
