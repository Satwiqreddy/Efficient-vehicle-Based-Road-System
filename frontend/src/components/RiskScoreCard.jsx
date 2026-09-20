import React from 'react';

export default function RiskScoreCard({ routeData }) {
  const score = routeData.overallScore ?? 0;
  const riskLevel = routeData.riskLevel || 'Low Risk';

  // Calculate SVG circle progress
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  let strokeColor = '#ef4444';
  let badgeClass = 'risk-badge-high';
  if (score < 45) {
    strokeColor = '#16a34a';
    badgeClass = 'risk-badge-low';
  } else if (score < 70) {
    strokeColor = '#f59e0b';
    badgeClass = 'risk-badge-med';
  }

  const analysisTime = routeData.analysisTimeSec;
  const timeLabel = analysisTime == null ? '—'
    : analysisTime >= 60 ? `${Math.floor(analysisTime / 60)}m ${Math.round(analysisTime % 60)}s`
    : `${analysisTime}s`;

  return (
    <div className="risk-score-card">
      <div className="card-section-title">Overall Risk Score</div>

      <div className="risk-score-layout">
        <div className="circular-gauge-wrapper">
          <svg className="circular-gauge-svg" width="130" height="130" viewBox="0 0 130 130">
            <circle className="gauge-track" cx="65" cy="65" r={radius} strokeWidth="10" />
            <circle
              className="gauge-value"
              cx="65"
              cy="65"
              r={radius}
              strokeWidth="10"
              stroke={strokeColor}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              transform="rotate(-90 65 65)"
            />
          </svg>

          <div className="gauge-center-content">
            <span className="gauge-score-number">{score}</span>
            <span className="gauge-score-total">/ 100</span>
          </div>

          <div className={`gauge-risk-status ${badgeClass}`}>{riskLevel}</div>
        </div>

        <div className="risk-metrics-list">
          <div className="metric-row-item">
            <span className="metric-label">Distance</span>
            <span className="metric-val">{routeData.distanceKm ?? '—'} km</span>
          </div>
          {routeData.durationMin != null && (
            <div className="metric-row-item">
              <span className="metric-label">Drive Time</span>
              <span className="metric-val">{routeData.durationMin} min</span>
            </div>
          )}
          <div className="metric-row-item">
            <span className="metric-label">Potholes</span>
            <span className={`metric-val ${routeData.potholeCount ? 'text-danger' : ''}`}>{routeData.potholeCount ?? 0}</span>
          </div>
          <div className="metric-row-item">
            <span className="metric-label">Speed Breakers</span>
            <span className={`metric-val ${routeData.speedBreakerCount ? 'text-warning' : ''}`}>{routeData.speedBreakerCount ?? 0}</span>
          </div>
          {routeData.framesScanned != null && (
            <div className="metric-row-item">
              <span className="metric-label">Frames Scanned</span>
              <span className="metric-val">{routeData.framesScanned}</span>
            </div>
          )}
          <div className="metric-row-item">
            <span className="metric-label">Analysis Time</span>
            <span className="metric-val">{timeLabel}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
