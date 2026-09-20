import React from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle2, Info, Wrench } from 'lucide-react';

export default function GroundClearanceGuide({ selectedVehicle }) {
  const clearance = selectedVehicle?.groundClearance || 165;

  const getTier = (gc) => {
    if (gc < 150) return { label: 'High Scraping Risk', color: 'danger', icon: ShieldAlert };
    if (gc <= 180) return { label: 'Moderate Risk', color: 'warning', icon: AlertTriangle };
    return { label: 'Safe Clearance', color: 'success', icon: CheckCircle2 };
  };

  const currentTier = getTier(clearance);
  const TierIcon = currentTier.icon;

  return (
    <div className="gc-guide-card">
      {/* Header */}
      <div className="gc-guide-header">
        <div className="gc-title-group">
          <Info size={16} className="gc-info-icon" />
          <h3 className="gc-title">Vehicle Ground Clearance Guide</h3>
        </div>
        <div className={`gc-current-badge badge-${currentTier.color}`}>
          <TierIcon size={14} />
          <span>{selectedVehicle?.name}: {clearance} mm ({currentTier.label})</span>
        </div>
      </div>

      {/* 3 Risk Tiers */}
      <div className="gc-tiers-grid">
        <div className={`gc-tier-item tier-danger ${clearance < 150 ? 'tier-active' : ''}`}>
          <div className="tier-header">
            <span className="tier-dot dot-danger"></span>
            <span className="tier-range">&lt; 150 mm</span>
          </div>
          <div className="tier-label">High Risk</div>
          <div className="tier-desc">Sedans &amp; sport hatches — vulnerable to tall speed breakers and deep potholes.</div>
        </div>

        <div className={`gc-tier-item tier-warn ${clearance >= 150 && clearance <= 180 ? 'tier-active' : ''}`}>
          <div className="tier-header">
            <span className="tier-dot dot-warn"></span>
            <span className="tier-range">150 – 180 mm</span>
          </div>
          <div className="tier-label">Moderate Risk</div>
          <div className="tier-desc">Standard city cars — safe with caution over unscientific speed bumps.</div>
        </div>

        <div className={`gc-tier-item tier-safe ${clearance > 180 ? 'tier-active' : ''}`}>
          <div className="tier-header">
            <span className="tier-dot dot-safe"></span>
            <span className="tier-range">&gt; 180 mm</span>
          </div>
          <div className="tier-label">Safe &amp; Robust</div>
          <div className="tier-desc">Compact &amp; full SUVs — superior underbody protection on broken roads.</div>
        </div>
      </div>

      {/* What Regular Road Impacts Damage */}
      <div className="gc-damage-footer">
        <div className="damage-title-row">
          <Wrench size={13} className="damage-icon" />
          <span>Underbody components protected by AI route scoring:</span>
        </div>
        <div className="damage-pills-row">
          <span className="damage-pill">Oil Sump &amp; Pan</span>
          <span className="damage-pill">Exhaust Catalytic System</span>
          <span className="damage-pill">Suspension Bushings</span>
          <span className="damage-pill">Wheel Alignment</span>
        </div>
      </div>
    </div>
  );
}
