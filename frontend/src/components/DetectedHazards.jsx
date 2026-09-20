import React, { useState } from 'react';
import { AlertTriangle, MapPin, Crosshair, ShieldCheck } from 'lucide-react';

const SEVERITY_STYLE = {
  High: { badge: 'badge-high', text: 'text-high', color: '#ef4444' },
  Medium: { badge: 'badge-medium', text: 'text-medium', color: '#f59e0b' },
  Low: { badge: 'badge-low', text: 'text-low', color: '#10b981' },
};

export default function DetectedHazards({ hazards, onFocusHazard, focusedHazardId }) {
  const [filterType, setFilterType] = useState('all');

  const potholes = hazards.filter(h => h.category === 'pothole');
  const speedBreakers = hazards.filter(h => h.category === 'speedbreaker');

  const filteredHazards = hazards.filter(h => filterType === 'all' || h.category === filterType);

  return (
    <section className="detected-hazards-section">
      <div className="hazards-header-bar">
        <h3 className="hazards-title">Detected Hazards on This Route</h3>

        <div className="hazards-filter-tabs">
          <button type="button" className={`filter-tab-btn ${filterType === 'all' ? 'active' : ''}`} onClick={() => setFilterType('all')}>
            All ({hazards.length})
          </button>
          <button type="button" className={`filter-tab-btn ${filterType === 'pothole' ? 'active' : ''}`} onClick={() => setFilterType('pothole')}>
            Potholes ({potholes.length})
          </button>
          <button type="button" className={`filter-tab-btn ${filterType === 'speedbreaker' ? 'active' : ''}`} onClick={() => setFilterType('speedbreaker')}>
            Speed Breakers ({speedBreakers.length})
          </button>
        </div>
      </div>

      {filteredHazards.length === 0 ? (
        <div className="hazards-empty-state">
          <div className="hazards-empty-icon"><ShieldCheck size={28} /></div>
          <div className="hazards-empty-title">
            {hazards.length === 0 ? 'No hazards detected on this route' : `No ${filterType === 'pothole' ? 'potholes' : 'speed breakers'} on this route`}
          </div>
          <div className="hazards-empty-desc">
            {hazards.length === 0
              ? 'YOLOv8 found no potholes or speed breakers in the scanned Street View frames. Drive normally and stay alert.'
              : 'Try the other filter or pick a different route above.'}
          </div>
        </div>
      ) : (
        <div className="hazard-cards-grid">
          {filteredHazards.map((hazard) => {
            const isFocused = focusedHazardId === hazard.id;
            const severity = hazard.adjustedSeverity || hazard.severity;
            const riskScore = hazard.adjustedRisk ?? hazard.baseRisk;
            const style = SEVERITY_STYLE[severity] || SEVERITY_STYLE.Low;

            return (
              <div key={hazard.id} className={`hazard-card-item ${isFocused ? 'hazard-card-focused' : ''}`}>
                {/* Annotated frame from the backend (bounding box already drawn by the detector) */}
                <div className="hazard-image-container">
                  <img
                    src={hazard.imageUrl}
                    alt={hazard.type}
                    className="hazard-image-media"
                    loading="lazy"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      if (e.target.nextSibling) e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                  <div className="hazard-image-fallback" style={{ display: 'none' }}>
                    <AlertTriangle size={32} />
                    <span>{hazard.type}</span>
                  </div>

                  <div className="hazard-detect-tag" style={{ backgroundColor: style.color }}>
                    <Crosshair size={11} />
                    <span>{hazard.type.toUpperCase()} · {hazard.confidence}%</span>
                  </div>

                  <div className={`hazard-risk-badge ${style.badge}`}>{severity} Risk</div>
                </div>

                <div className="hazard-body-content">
                  <div className="hazard-type-title">
                    <span className="hazard-type-icon"><AlertTriangle size={16} /></span>
                    <span className="hazard-type-text">{hazard.type}</span>
                    {hazard.sightings > 1 && (
                      <span className="sightings-chip" title="Detected in this many consecutive Street View frames">
                        {hazard.sightings}× seen
                      </span>
                    )}
                  </div>

                  <div className="hazard-meta-grid">
                    <div className="meta-cell">
                      <span className="meta-cell-label">AI Confidence</span>
                      <span className="meta-cell-value font-semibold">{hazard.confidence}%</span>
                    </div>
                    <div className="meta-cell">
                      <span className="meta-cell-label">Severity</span>
                      <span className={`meta-cell-value font-semibold ${style.text}`}>{severity}</span>
                    </div>
                    <div className="meta-cell">
                      <span className="meta-cell-label">Risk Score</span>
                      <span className={`meta-cell-value font-bold ${style.text}`}>{riskScore}</span>
                    </div>
                    <div className="meta-cell">
                      <span className="meta-cell-label">Location</span>
                      <span className="meta-cell-value">{hazard.locationOffsetKm} km</span>
                    </div>
                  </div>

                  <button type="button" className="btn-view-on-map" onClick={() => onFocusHazard(hazard)}>
                    <MapPin size={15} />
                    <span>View on Map</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
