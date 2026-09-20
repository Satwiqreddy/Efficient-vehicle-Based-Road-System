# Efficient-vehicle-Based-Road-System
# 🚗 Ground-Clearance-Aware Navigation System

> A smarter navigation system that recommends the safest road route based on your vehicle's ground clearance — not just the shortest or fastest path.

---

##  What Is This?

When you use Google Maps, it finds the fastest or shortest route. But it has no idea whether that road has deep potholes, broken surfaces, or high speed breakers that could damage the underside of your car.

This project solves that.

By analysing road surface conditions using street-level images and estimating obstacle severity, the system recommends a route that is safest for your vehicle's specific ground clearance — avoiding roads that could cause underbody damage or suspension wear.

---

##  System Architecture

The system is divided into five stages:

**1. User Input**
The user provides three things — their route (source & destination), vehicle type, and ground clearance value.

**2. Google APIs**
- Street View API fetches road-level images for each part of the route.
- Elevation API provides terrain height data.

**3. Processing Engine**
Road images go through a pipeline:
- Images are preprocessed (cleaned and enhanced).
- Depth estimation estimates how deep or tall obstacles appear.
- Road segmentation breaks the image into meaningful zones.
- Obstacle detection identifies potholes and speed breakers.

**4. Risk Assessment**
- The detected obstacles are compared against the vehicle's ground clearance.
- Each road segment is classified as Low, Medium, or High risk.

**5. Routing Service & User Interface**
- Every alternative route from Google Directions is scanned and scored; the lowest-risk one is recommended.
- The React UI shows all routes on Google Maps with colour-coded hazard markers, annotated Street View frames, a per-vehicle risk gauge and a printable report.

---

##  Who Is This For?

- Drivers of low ground-clearance vehicles (sedans, hatchbacks, sports cars)
- Anyone travelling on roads with poor surface conditions
- Commuters who want to protect their vehicle from avoidable damage

---

##  How It Works — In Simple Terms

1. You enter your **start point**, **end point**, and **vehicle type**.
2. The system fetches road images along your route from Google Street View.
3. Each image is analysed to detect obstacles like potholes and speed breakers.
4. A **risk score** is calculated for each road segment based on how dangerous it is for your vehicle.
5. The routing algorithm finds the path with the **lowest combined distance and risk**.
6. You see the safest route on a map, with colour-coded risk highlights.


## 🛠️ Tech Stack

| Purpose | Tool Used |
|---|---|
| Route & alternatives | Google Maps Directions API (`alternatives=true`) |
| Road imagery | Google Street View Static API, every panorama along the route (~10 m spacing), fetched in parallel |
| Obstacle detection | YOLOv8 (custom pothole + speed-breaker weights in `hazard_detection/models/`) |
| Risk scoring | `hazard_detection/src/risk_engine.py`, personalised by ground clearance |
| Backend | Python, FastAPI (`api_server.py`) — async jobs with live progress |
| Frontend | React + Vite (`frontend/`), Google Maps JavaScript API |

---

## 🚀 Run It

```bash
# 1. backend  (Python 3.10+, needs GOOGLE_MAPS_API_KEY in .env)
pip install -r hazard_detection/requirements.txt fastapi uvicorn polyline python-dotenv
python api_server.py                      # http://localhost:8000

# 2. frontend (dev, with hot reload)
cd frontend && npm install && npm run dev  # http://localhost:5173

#    — or build once and let the backend serve it —
cd frontend && npm run build && cd .. && python api_server.py   # http://localhost:8000
```

Enter a start, a destination and your vehicle, then **Analyze Route with AI**. A 2 km route takes ~1 min;
a route set with 3 alternatives across a city takes several minutes. The Google key must have
**Directions API**, **Street View Static API** and **Maps JavaScript API** enabled. See `frontend/README.md`
for settings, demo mode and key handling.

---

## 📄 Documentation

- [`requirements.md`](requirements.md) — Functional and non-functional requirements, user stories
- [`frontend/README.md`](frontend/README.md) — UI, backend connection, Google Maps key

---

##  Known Limitations

- Road images come from Google Street View, which may not always be up to date.
- Severity is currently driven by detection confidence; the MiDaS depth-based severity in `hazard_detection/src/depth_severity.py` is not yet wired into the API.
- The system is **not real-time** — it analyses a route when you query it, and re-downloads imagery on every query (a per-panorama cache is planned).

---

##  Future Scope

- Real-time road condition updates using crowdsourced dashcam data
- Mobile app (Android & iOS)
- Larger vehicle database with manufacturer specs
- Support for two-wheelers and electric vehicles

---
