import React, { useState } from 'react';
import { Car, MapPin, Search, Sparkles, Navigation2, ArrowRightLeft, MapPinned } from 'lucide-react';
import { VEHICLE_DATABASE } from '../data/vehicles';
import { PRESET_ROUTES } from '../data/sampleRouteData';
import LoadingProverbs from './LoadingProverbs';
import GroundClearanceGuide from './GroundClearanceGuide';

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
    const temp = startLocation;
    setStartLocation(destination);
    setDestination(temp);
  };

  return (
    <section className="hero-section">
      <div className="hero-grid">
        {/* Left Side: Headlines & Ground Clearance Guide */}
        <div className="hero-left-content">
          <div className="hero-badge-live">
            <span className="live-indicator-dot"></span>
            <span>Intelligent Road Hazard &amp; Safety Platform</span>
          </div>

          <h1 className="hero-title">
            Know the Road <br />
            <span className="highlight-green">Before You Drive.</span>
          </h1>

          <p className="hero-subtitle">
            Street-level computer vision hazard detection personalized for your vehicle's exact ground clearance.
          </p>

          <div className="hero-slogan-card">
            <Sparkles size={16} className="slogan-icon" />
            <span>AI Road Vision • YOLOv8 Neural Network • Zero Undercarriage Damage</span>
          </div>

          {/* Ground Clearance Reference Card */}
          <GroundClearanceGuide selectedVehicle={selectedVehicle} />
        </div>

        {/* Right Side: "Plan Your Route" Card */}
        <div className="hero-right-card-wrapper">
          <div className="plan-route-card">
            <div className="card-header-row">
              <div>
                <h2 className="card-title">Plan Your Route</h2>
                <span className="card-subtitle">Scan for potholes &amp; speed breakers</span>
              </div>
              <button 
                type="button"
                className="preset-pill-btn"
                onClick={() => setShowPresets(!showPresets)}
                title="Choose sample routes"
              >
                Presets ▾
              </button>
            </div>

            {showPresets && (
              <>
              <div className="presets-backdrop" onClick={() => setShowPresets(false)} />
              <div className="presets-dropdown-menu">
                <div className="presets-dropdown-title">Select Preset Route</div>
                {PRESET_ROUTES.map((p, idx) => (
                  <button 
                    key={idx}
                    type="button" 
                    className="preset-option-btn"
                    onClick={() => handleSelectPreset(p)}
                  >
                    <Navigation2 size={14} className="preset-icon" />
                    <div>
                      <div className="preset-name">{p.start} → {p.destination}</div>
                      <div className="preset-meta">{p.distanceKm} km</div>
                    </div>
                  </button>
                ))}
              </div>
              </>
            )}

            <form 
              className="route-form" 
              onSubmit={(e) => {
                e.preventDefault();
                onAnalyze();
              }}
            >
              {/* Start Location Input */}
              <div className="form-group">
                <div className="label-with-action">
                  <label className="form-label">
                    <span className="location-pin-icon pin-green">
                      <MapPin size={15} />
                    </span>
                    Start Location
                  </label>
                  <button 
                    type="button" 
                    className="swap-btn-text" 
                    onClick={handleSwapLocations}
                    title="Swap start and destination"
                  >
                    <ArrowRightLeft size={13} />
                    <span>Swap</span>
                  </button>
                </div>
                <div className="input-with-icon">
                  <input
                    type="text"
                    className="form-input"
                    value={startLocation}
                    onChange={(e) => setStartLocation(e.target.value)}
                    placeholder="Address, landmark, or lat,lng from the map picker"
                    required
                  />
                  <Search size={16} className="input-search-icon" />
                </div>
              </div>

              {/* Destination Input */}
              <div className="form-group">
                <label className="form-label">
                  <span className="location-pin-icon pin-red">
                    <MapPin size={15} />
                  </span>
                  Destination
                </label>
                <div className="input-with-icon">
                  <input
                    type="text"
                    className="form-input"
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    placeholder="Address, landmark, or lat,lng"
                    required
                  />
                  <Search size={16} className="input-search-icon" />
                </div>
              </div>

              {/* Select Your Vehicle */}
              <div className="form-group">
                <div className="label-with-action">
                  <label className="form-label">
                    <span className="location-pin-icon pin-blue">
                      <Car size={15} />
                    </span>
                    Select Your Vehicle
                  </label>
                  <span className="vehicle-gc-badge">
                    {selectedVehicle.groundClearance} mm Clearance
                  </span>
                </div>
                <div className="select-wrapper">
                  <select
                    className="form-select"
                    value={selectedVehicle.id}
                    onChange={(e) => {
                      const found = VEHICLE_DATABASE.find(v => v.id === e.target.value);
                      if (found) setSelectedVehicle(found);
                    }}
                  >
                    <optgroup label="Popular Indian Hatchbacks & Sedans">
                      {VEHICLE_DATABASE.filter(v => v.category === 'Sedan' || v.category === 'Hatchback').map(v => (
                        <option key={v.id} value={v.id}>
                          {v.name} ({v.groundClearance} mm)
                        </option>
                      ))}
                    </optgroup>
                    <optgroup label="Compact & Full SUVs">
                      {VEHICLE_DATABASE.filter(v => v.category === 'SUV').map(v => (
                        <option key={v.id} value={v.id}>
                          {v.name} ({v.groundClearance} mm)
                        </option>
                      ))}
                    </optgroup>
                    <optgroup label="MPVs & Performance Cars">
                      {VEHICLE_DATABASE.filter(v => v.category === 'MPV' || v.category === 'Sports' || v.category === 'Modified').map(v => (
                        <option key={v.id} value={v.id}>
                          {v.name} ({v.groundClearance} mm)
                        </option>
                      ))}
                    </optgroup>
                  </select>
                </div>
              </div>

              {/* When NOT analyzing: Show Analyze CTA Button */}
              {!isAnalyzing ? (
                <>
                  <button 
                    type="submit" 
                    className="btn-analyze-route"
                    disabled={liveMode && backendOnline === false}
                  >
                    <Search size={18} />
                    <span>Analyze Route with AI</span>
                  </button>
                  <button
                    type="button"
                    className="btn-pick-on-map"
                    onClick={onOpenPicker}
                    disabled={!canPick}
                    title={canPick ? 'Choose start and destination by clicking on a map' : 'Needs the Google Maps key (see Settings / backend .env)'}
                  >
                    <MapPinned size={17} />
                    <span>Select origin &amp; destination on map</span>
                  </button>
                  <div className={`form-subtext ${analysisError ? 'form-subtext-error' : ''}`}>
                    {analysisError
                      ? analysisError
                      : liveMode
                        ? (backendOnline === false
                            ? 'Backend offline — start `python api_server.py` or switch to Demo mode in Settings.'
                            : 'Live: Google Street View imagery scanned by YOLOv8 — typically 1–5 min per route set.')
                        : 'Demo mode: OSRM routing with dataset sample frames. Switch to Live in Settings for real detection.'}
                  </div>
                </>
              ) : (
                <LoadingProverbs 
                  selectedVehicle={selectedVehicle} 
                  progress={progress} 
                />
              )}
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
