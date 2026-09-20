import React, { useState } from 'react';
import { Car, MapPin, ArrowRightLeft, MapPinned, ChevronDown } from 'lucide-react';
import { VEHICLE_DATABASE } from '../data/vehicles';
import { PRESET_ROUTES } from '../data/sampleRouteData';
import LoadingProverbs from './LoadingProverbs';

function clearanceNote(mm) {
  if (mm < 150) return 'low — tall speed breakers and deep potholes can hit the underbody';
  if (mm <= 180) return 'typical for a city car — take unmarked humps slowly';
  return 'high — most road hazards clear comfortably';
}

export default function HeroSection({
  startLocation,
  setStartLocation,
  destination,
  setDestination,
  selectedVehicle,
  setSelectedVehicle,
  onAnalyze,
  isAnalyzing,
  progress,
  analysisError,
  liveMode,
  backendOnline,
  onOpenPicker,
  canPick
}) {
  const [showPresets, setShowPresets] = useState(false);

  const handleSelectPreset = (preset) => {
    setStartLocation(preset.start);
    setDestination(preset.destination);
    setShowPresets(false);
  };

  const handleSwapLocations = () => {
    setStartLocation(destination);
    setDestination(startLocation);
  };

  const groups = [
    ['Hatchbacks & sedans', (v) => v.category === 'Sedan' || v.category === 'Hatchback'],
    ['SUVs', (v) => v.category === 'SUV'],
    ['MPVs & sports', (v) => ['MPV', 'Sports', 'Modified'].includes(v.category)],
  ];

  return (
    <section className="hero-section">
      <div className="hero-grid">
        <div className="hero-left-content hero-intro">
          <h1 className="hero-title">Check the road <mark className="hl">before</mark> you drive it.</h1>
          <p className="hero-subtitle">
            Enter two places. We fetch every driving route between them, look at each Street View
            frame along the way for <strong>potholes and speed breakers</strong>, and rate the routes for
            <strong> your car's ground clearance</strong>.
          </p>

          <ol className="how-list">
            <li><span>1</span><div>Routes come from <strong>Google Directions</strong>, including the alternatives.</div></li>
            <li><span>2</span><div>A <strong>YOLOv8 detector</strong> trained on Indian roads scans a Street View frame <strong>every 10 m</strong>.</div></li>
            <li><span>3</span><div>Each hazard is scored against your vehicle's ground clearance; the <strong>safest route is recommended</strong>.</div></li>
          </ol>
        </div>

        <div className="hero-right-card-wrapper">
          <div className="plan-route-card">
            <div className="card-header-row">
              <h2 className="card-title">Plan a route</h2>
              <button type="button" className="preset-pill-btn" onClick={() => setShowPresets(!showPresets)}>
                Examples <ChevronDown size={14} />
              </button>
            </div>

            {showPresets && (
              <>
              <div className="presets-backdrop" onClick={() => setShowPresets(false)} />
              <div className="presets-dropdown-menu">
                {PRESET_ROUTES.map((p, idx) => (
                  <button key={idx} type="button" className="preset-option-btn" onClick={() => handleSelectPreset(p)}>
                    <div>
                      <div className="preset-name">{p.start} → {p.destination}</div>
                      <div className="preset-meta">{p.distanceKm} km</div>
                    </div>
                  </button>
                ))}
              </div>
              </>
            )}

            <form className="route-form" onSubmit={(e) => { e.preventDefault(); onAnalyze(); }}>
              <div className="form-group">
                <div className="label-with-action">
                  <label className="form-label" htmlFor="start-input">
                    <span className="location-pin-icon pin-green"><MapPin size={15} /></span>
                    From
                  </label>
                  <button type="button" className="swap-btn-text" onClick={handleSwapLocations} title="Swap">
                    <ArrowRightLeft size={13} />
                    <span>Swap</span>
                  </button>
                </div>
                <input
                  id="start-input"
                  type="text"
                  className="form-input"
                  value={startLocation}
                  onChange={(e) => setStartLocation(e.target.value)}
                  placeholder="Place, landmark, or lat,lng"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="dest-input">
                  <span className="location-pin-icon pin-red"><MapPin size={15} /></span>
                  To
                </label>
                <input
                  id="dest-input"
                  type="text"
                  className="form-input"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  placeholder="Place, landmark, or lat,lng"
                  required
                />
              </div>

              <button
                type="button"
                className="btn-pick-on-map"
                onClick={onOpenPicker}
                disabled={!canPick}
                title={canPick ? 'Choose both points by clicking on a map' : 'Needs the Google Maps key (see Settings)'}
              >
                <MapPinned size={16} />
                <span>Pick points on a map instead</span>
              </button>

              <div className="form-group">
                <label className="form-label" htmlFor="vehicle-select">
                  <span className="location-pin-icon pin-blue"><Car size={15} /></span>
                  Vehicle
                </label>
                <div className="select-wrapper">
                  <select
                    id="vehicle-select"
                    className="form-select"
                    value={selectedVehicle.id}
                    onChange={(e) => {
                      const found = VEHICLE_DATABASE.find(v => v.id === e.target.value);
                      if (found) setSelectedVehicle(found);
                    }}
                  >
                    {groups.map(([label, test]) => (
                      <optgroup key={label} label={label}>
                        {VEHICLE_DATABASE.filter(test).map(v => (
                          <option key={v.id} value={v.id}>{v.name} — {v.groundClearance} mm</option>
                        ))}
                      </optgroup>
                    ))}
                  </select>
                </div>
                <span className="input-helper-text">
                  Ground clearance {selectedVehicle.groundClearance} mm: {clearanceNote(selectedVehicle.groundClearance)}.
                </span>
              </div>

              {!isAnalyzing ? (
                <>
                  <button type="submit" className="btn-analyze-route" disabled={liveMode && backendOnline === false}>
                    Analyze route
                  </button>
                  <div className={`form-subtext ${analysisError ? 'form-subtext-error' : ''}`}>
                    {analysisError
                      ? analysisError
                      : liveMode
                        ? (backendOnline === false
                            ? 'The analysis server is not running. Start it with `python api_server.py`, or switch to demo mode in Settings.'
                            : 'Usually 1–3 minutes per route set; longer routes take longer.')
                        : 'Demo mode: routes and hazards are illustrative. Switch to live in Settings for real detection.'}
                  </div>
                </>
              ) : (
                <LoadingProverbs selectedVehicle={selectedVehicle} progress={progress} />
              )}
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
