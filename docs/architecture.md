# Architecture Document
## Ground-Clearance-Aware Navigation System

**Project:** ground-clearance-nav  
**Version:** 1.0  
**Date:** 2026-03-25  

---

## 1. Architectural Style

The system follows a **sequential pipeline architecture**. Each module is a self-contained processing stage that reads from the previous stage's output file and writes its own output file. Modules do not import each other's source code — they communicate only through JSON contracts.

This design choice means:
- Any module can be replaced or upgraded independently.
- Each module can be tested in isolation without the full pipeline running.
- Team members can work on separate branches without merge conflicts.

---

## 2. Module Dependency Graph

```
                    ┌─────────────────────┐
                    │   config.py          │
                    │ (global constants)   │
                    └──────────┬──────────┘
                               │ imported by all modules
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐        ...
│ route_extraction │  │ risk_scoring     │
└────────┬─────────┘  └──────────────────┘
         │ segments.json
         ▼
┌──────────────────┐
│ image_collection │
└────────┬─────────┘
         │ images/
         ▼
┌──────────────────┐
│  road_analysis   │
└────────┬─────────┘
         │ detections.json
         ▼
┌──────────────────┐
│  risk_scoring    │
└────────┬─────────┘
         │ risk_map.json
         ▼
┌──────────────────┐
│  routing_engine  │
└────────┬─────────┘
         │ safe_route.json
         ▼
┌──────────────────┐
│    frontend      │
└──────────────────┘
```

---

## 3. Inter-Module Contracts

These are the exact JSON schemas each module must produce and consume. Treat these as immutable contracts — changing a field name breaks the downstream module.

### Contract 1 — Route Extraction → Image Collection

**File:** `modules/route_extraction/output/segments.json`

```json
[
  {
    "segment_id": "seg_001",
    "start":    { "lat": 13.0827, "lng": 80.2707 },
    "end":      { "lat": 13.0831, "lng": 80.2712 },
    "midpoint": { "lat": 13.0829, "lng": 80.2710 },
    "heading":  45.2,
    "length_m": 50.0
  }
]
```

| Field | Type | Description |
|---|---|---|
| segment_id | string | Unique identifier, zero-padded (seg_001 … seg_NNN) |
| start / end | object | GPS coordinates of segment endpoints |
| midpoint | object | Used for Street View image fetch |
| heading | float | Camera bearing in degrees (0–360) |
| length_m | float | Actual segment length in metres |

---

### Contract 2 — Image Collection → Road Analysis

**File:** `modules/image_collection/output/images/seg_NNN.jpg`  
**Metadata file:** `modules/image_collection/output/image_manifest.json`

```json
[
  {
    "segment_id": "seg_001",
    "image_path": "modules/image_collection/output/images/seg_001.jpg",
    "status": "ok",
    "fallback": false
  }
]
```

| Field | Type | Description |
|---|---|---|
| status | string | `"ok"` or `"no_imagery"` |
| fallback | bool | True if a blank placeholder was used |

> **Note:** If `fallback` is true, road_analysis must assign `severity = 0` without running inference.

---

### Contract 3 — Road Analysis → Risk Scoring

**File:** `modules/road_analysis/output/detections.json`

```json
[
  {
    "segment_id": "seg_001",
    "obstacle_detected": true,
    "obstacle_type": "pothole",
    "confidence": 0.87,
    "severity": 3,
    "depth_score": 0.72,
    "bbox": [120, 200, 300, 380]
  }
]
```

| Field | Type | Description |
|---|---|---|
| obstacle_detected | bool | Whether any obstacle was found |
| obstacle_type | string | `"pothole"`, `"speed_breaker"`, or `"none"` |
| confidence | float | YOLO detection confidence (0–1) |
| severity | int | 0 = none, 1 = low, 2 = medium, 3 = high |
| depth_score | float | MiDaS normalised depth of obstacle crop (0–1) |
| bbox | array | Bounding box [x1, y1, x2, y2] in pixels |

---

### Contract 4 — Risk Scoring → Routing Engine

**File:** `modules/risk_scoring/output/risk_map.json`

```json
{
  "vehicle_clearance_mm": 150,
  "vehicle_type": "sedan",
  "alpha": 0.7,
  "segments": [
    {
      "segment_id": "seg_001",
      "risk_score": 1.0,
      "risk_label": "High",
      "length_m": 50.0,
      "start": { "lat": 13.0827, "lng": 80.2707 },
      "end":   { "lat": 13.0831, "lng": 80.2712 }
    }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| risk_score | float | 0.0 – 1.0, used as edge weight in A* |
| risk_label | string | Human-readable: Low / Medium / High |
| length_m | float | Passed through for cost function |

---

### Contract 5 — Routing Engine → Frontend

**File:** `modules/routing_engine/output/safe_route.json`

```json
{
  "recommended_route": {
    "segments": ["seg_001", "seg_004", "seg_007"],
    "total_distance_m": 1450,
    "total_risk_score": 0.4,
    "risk_label": "Medium",
    "coordinates": [
      { "lat": 13.0827, "lng": 80.2707 },
      { "lat": 13.0835, "lng": 80.2715 }
    ]
  },
  "alternative_route": {
    "segments": ["seg_001", "seg_002", "seg_003"],
    "total_distance_m": 1600,
    "total_risk_score": 0.1,
    "risk_label": "Low",
    "coordinates": [...]
  },
  "risk_overlay": [
    { "segment_id": "seg_001", "risk_label": "High",   "color": "#e74c3c" },
    { "segment_id": "seg_002", "risk_label": "Low",    "color": "#2ecc71" },
    { "segment_id": "seg_003", "risk_label": "Medium", "color": "#f39c12" }
  ]
}
```

---

## 4. Configuration (`config.py`)

All modules import constants from a single `config.py` at the repo root. This is the only file shared across modules.

```python
# config.py

# Routing
SEGMENT_LENGTH_M = 50       # metres per road segment
ALPHA = 0.7                  # risk weight in A* cost function
RISK_SCALE = 1000            # scales risk to match distance magnitude

# Image collection
STREETVIEW_SIZE = "640x480"
STREETVIEW_FOV = 90

# Risk thresholds (depth_score → severity)
DEPTH_LOW_THRESHOLD    = 0.3
DEPTH_MEDIUM_THRESHOLD = 0.6

# Vehicle clearance profiles (mm)
VEHICLE_PROFILES = {
    "hatchback": 165,
    "sedan":     150,
    "suv":       210,
    "truck":     230,
    "custom":    None        # user-supplied value
}

# Risk score table: clearance_band × severity → risk_score
RISK_TABLE = {
    "low_clearance": {1: 0.2, 2: 0.6, 3: 1.0},   # < 160 mm
    "mid_clearance": {1: 0.1, 2: 0.4, 3: 0.8},   # 160–200 mm
    "high_clearance": {1: 0.05, 2: 0.2, 3: 0.5}, # > 200 mm
}
```

---

## 5. Error Handling Strategy

| Scenario | Module | Handling |
|---|---|---|
| Maps API returns no route | route_extraction | Raise `NoRouteError`, surface to user |
| Street View returns no imagery | image_collection | Save placeholder, set `fallback=True` in manifest |
| YOLO detects nothing | road_analysis | Set `obstacle_detected=False`, severity=0 |
| MiDaS inference fails | road_analysis | Log warning, fall back to severity from YOLO confidence only |
| No low-risk path found | routing_engine | Return minimum-risk available path with `"warning": "no_safe_route"` |
| API key missing | any | Check at startup, exit with clear message before pipeline runs |

---

## 6. Execution Flow (End to End)

```
python main.py \
  --source "Anna Nagar, Chennai" \
  --destination "T Nagar, Chennai" \
  --vehicle sedan

Step 1: route_extraction   → writes segments.json        (~2s)
Step 2: image_collection   → writes images/ + manifest   (~30–90s depending on segment count)
Step 3: road_analysis      → writes detections.json      (~20–60s)
Step 4: risk_scoring       → writes risk_map.json        (<1s)
Step 5: routing_engine     → writes safe_route.json      (<1s)
Step 6: frontend           → opens map in browser        (<2s)
```

Total estimated time for a 5 km route (~100 segments): **60–180 seconds**  
Bottleneck: Street View API calls (rate-limited). Mitigated by caching images locally.

---

## 7. Caching Strategy

To avoid re-fetching Street View images on repeated queries for the same area:

- Images are stored as `seg_{lat}_{lng}.jpg` keyed on midpoint coordinates (rounded to 4 decimal places).
- On startup, `image_collection` checks if an image already exists before calling the API.
- `segments.json` and `detections.json` are also cached per source–destination pair.
- Cache is stored in `cache/` at repo root and is excluded from version control via `.gitignore`.

---
