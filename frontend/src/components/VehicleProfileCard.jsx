import React from 'react';
import { Info } from 'lucide-react';

export default function VehicleProfileCard({ vehicle }) {
  const clearance = vehicle.groundClearance || 165;
  
  const isVulnerable = clearance < 165;

  return (
    <div className="vehicle-profile-card">
      <div className="card-section-title">Your Vehicle</div>

      <div className="vehicle-info-row">
        {/* Car Visual Graphic */}
        <div className="vehicle-car-visual">
          <div className="car-vector-badge">
            <svg viewBox="0 0 100 45" fill="none" xmlns="http://www.w3.org/2000/svg" className="car-vector-svg">
              <path d="M12 28L18 16C19 14 22 12 26 12H68C72 12 75 14 77 16L86 28H94C96 28 98 30 98 32V36H2V32C2 30 4 28 6 28H12Z" fill="#94A3B8" />
              <path d="M22 15L25 24H48V15H25C23.5 15 22.5 15 22 15Z" fill="#E2E8F0" />
              <path d="M52 15V24H73L69 15H52Z" fill="#E2E8F0" />
              <circle cx="22" cy="36" r="7" fill="#334155" stroke="#FFFFFF" strokeWidth="2" />
              <circle cx="76" cy="36" r="7" fill="#334155" stroke="#FFFFFF" strokeWidth="2" />
              <circle cx="22" cy="36" r="3" fill="#94A3B8" />
              <circle cx="76" cy="36" r="3" fill="#94A3B8" />
            </svg>
          </div>
        </div>

        <div className="vehicle-details-col">
          <div className="vehicle-name-heading">{vehicle.name}</div>
          <div className="vehicle-spec-clearance">
            Ground Clearance: <span className="highlight-val">{vehicle.groundClearance} mm</span>
          </div>
          <div className="vehicle-category-tag">{vehicle.category}</div>
        </div>
      </div>

      {/* Advisory Tip Banner */}
      <div className={`vehicle-advisory-banner ${isVulnerable ? 'advisory-warn' : 'advisory-info'}`}>
        <div className="advisory-icon">
          <Info size={16} />
        </div>
        <div className="advisory-text">
          {isVulnerable 
            ? "Lower ground clearance vehicles are more vulnerable to road hazards and underbody scraping."
            : clearance >= 190
              ? "High ground clearance vehicle provides superior protection against road undulations & humps."
              : "Moderate clearance: Exercise normal caution over highlighted high-risk road depressions."
          }
        </div>
      </div>
    </div>
  );
}
