import React from 'react';
import { Cpu, Car, Map, ArrowRight } from 'lucide-react';
import HowItWorks from './HowItWorks';

export default function AboutView({ onBackToHome }) {
  return (
    <div className="about-view-container">
      <div className="about-hero-box">
        <div className="about-badge">Project Architecture & AI Models</div>
        <h1 className="about-title">About RoadGuard AI System</h1>
        <p className="about-lead">
          An intelligent vehicle-aware road safety framework designed to detect physical road surface hazards, calculate suspension risk based on ground clearance, and suggest safer driving parameters.
        </p>
        <button type="button" className="btn-action-primary" onClick={onBackToHome}>
          <ArrowRight size={16} />
          <span>Launch Route Analyzer</span>
        </button>
      </div>

      <div className="about-content-grid">
        <div className="about-feature-card">
          <div className="about-card-icon icon-green">
            <Cpu size={24} />
          </div>
          <h3>YOLOv8 Hazard Detection</h3>
          <p>
            Custom fine-tuned YOLOv8 neural network trained on over 5,000+ annotated road hazard instances including deep potholes, weathered depressions, unmarked speed humps, and rumble strips.
          </p>
        </div>

        <div className="about-feature-card">
          <div className="about-card-icon icon-blue">
            <Car size={24} />
          </div>
          <h3>Vehicle Ground Clearance Dynamics</h3>
          <p>
            Unlike generic navigation apps, RoadGuard calibrates risk specifically to your vehicle's physical ground clearance (from 75mm lowered sedans up to 226mm off-road SUVs).
          </p>
        </div>

        <div className="about-feature-card">
          <div className="about-card-icon icon-red">
            <Map size={24} />
          </div>
          <h3>Google Street View Waypoint Sampling</h3>
          <p>
            Automated polyline parsing samples every Street View panorama along the road (~10 m apart), extracting heading angles and field of view for high-accuracy road surface inspection.
          </p>
        </div>
      </div>

      <HowItWorks />
    </div>
  );
}
