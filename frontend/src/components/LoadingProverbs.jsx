import React, { useState, useEffect } from 'react';
import { Compass, Camera, BrainCircuit, ShieldCheck, Sparkles } from 'lucide-react';

const DRIVING_PROVERBS = [
  { quote: 'Better late than never — slow down near potholes.', author: 'Road Safety Wisdom', tag: 'Pothole Caution' },
  { quote: 'A smooth journey starts with knowing the bumps ahead.', author: 'Defensive Driving Principle', tag: 'Route Awareness' },
  { quote: "Your car's ground clearance is its first line of underbody defense.", author: 'Automotive Care', tag: 'Clearance Guide' },
  { quote: 'Speed breakers protect pedestrians — respect them to save your suspension.', author: 'Safe Driving Habit', tag: 'Suspension Health' },
  { quote: 'An ounce of prevention on the road saves a ton of repair bills in the garage.', author: "Driver's Rule of Thumb", tag: 'Preventive Care' },
  { quote: "The road doesn't care about your hurry — drive with patience and precision.", author: 'Road Wisdom', tag: 'Patience & Safety' },
  { quote: "Potholes don't discriminate — but your vehicle's ride height decides the impact.", author: 'Ground Clearance Fact', tag: 'Vehicle Dynamics' },
  { quote: "Smooth roads don't make good drivers — anticipation and awareness do.", author: 'Defensive Driving', tag: 'Driver Focus' }
];

const STEPS = [
  { icon: Compass, label: 'Google Directions', detail: 'Extracting waypoints & road geometry', doneDetail: 'Alternative routes extracted' },
  { icon: Camera, label: 'Street View Imagery', detail: 'Downloading forward-facing road frames', doneDetail: 'Road frames collected' },
  { icon: BrainCircuit, label: 'YOLOv8 AI Detection', detail: 'Scanning potholes & speed breakers', doneDetail: 'Hazards geotagged & classified' },
  { icon: ShieldCheck, label: 'Personalized Risk Scoring', detail: 'Assessing ground clearance impact', doneDetail: 'Safety rating & route plan ready' }
];

// progress comes straight from the backend job: { stage: 0-3, progress: 0-100, message }
export default function LoadingProverbs({ selectedVehicle, progress }) {
  const [proverbIndex, setProverbIndex] = useState(0);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false);
      setTimeout(() => {
        setProverbIndex((prev) => (prev + 1) % DRIVING_PROVERBS.length);
        setFade(true);
      }, 350);
    }, 4500);
    return () => clearInterval(interval);
  }, []);

  const currentStep = progress?.stage ?? 0;
  const progressPercent = Math.max(2, Math.min(100, Math.round(progress?.progress ?? 0)));
  const currentProverb = DRIVING_PROVERBS[proverbIndex];

  return (
    <div className="proverb-loading-card">
      <div className="loading-header">
        <div className="loading-badge-row">
          <span className="live-pulse-dot"></span>
          <span className="loading-title">AI Road Assessment in Progress</span>
        </div>
        <span className="loading-vehicle-tag">
          🚗 {selectedVehicle?.name || 'Vehicle'} • {selectedVehicle?.groundClearance || 165} mm
        </span>
      </div>

      <div className="proverb-quote-box">
        <div className="proverb-top-meta">
          <span className="proverb-sparkle-icon"><Sparkles size={15} /></span>
          <span className="proverb-category-tag">{currentProverb.tag}</span>
        </div>
        <p className={`proverb-quote-text ${fade ? 'proverb-visible' : 'proverb-hidden'}`}>
          "{currentProverb.quote}"
        </p>
        <span className={`proverb-quote-author ${fade ? 'proverb-visible' : 'proverb-hidden'}`}>
          — {currentProverb.author}
        </span>
      </div>

      <div className="loading-progress-section">
        <div className="loading-progress-track">
          <div className="loading-progress-fill" style={{ width: `${progressPercent}%` }}></div>
        </div>
        <div className="loading-progress-meta">
          <span className="progress-label">Analysis Pipeline</span>
          <span className="progress-value">{progressPercent}%</span>
        </div>
      </div>

      <div className="loading-stages-grid">
        {STEPS.map((s, idx) => {
          const isDone = idx < currentStep;
          const isActive = idx === currentStep;
          const IconComp = s.icon;
          return (
            <div key={idx} className={`stage-chip ${isDone ? 'stage-done' : isActive ? 'stage-active' : 'stage-pending'}`}>
              <div className="stage-icon-circle">
                {isDone ? <span className="stage-tick">✓</span> : <IconComp size={13} className={isActive ? 'icon-spin-subtle' : ''} />}
              </div>
              <div className="stage-text-block">
                <div className="stage-name-row">
                  <span className="stage-name">{s.label}</span>
                  {isDone && <span className="stage-done-badge">DONE</span>}
                  {isActive && <span className="stage-live-badge">RUNNING</span>}
                </div>
                <span className="stage-desc">{isDone ? s.doneDetail : s.detail}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="loading-status-footer">
        <div className="spinner-ring"></div>
        <span className="status-text-live">
          {progress?.message || 'Connecting to backend...'}
        </span>
      </div>
    </div>
  );
}
