import React from 'react';
import { Camera, Cpu, BarChart3, Car, ShieldCheck, ArrowRight, Lightbulb } from 'lucide-react';

export default function HowItWorks() {
  const steps = [
    {
      num: 1,
      color: '#3b82f6',
      icon: Camera,
      title: 'Collect Road Images',
      desc: 'Google Street View along your route'
    },
    {
      num: 2,
      color: '#16a34a',
      icon: Cpu,
      title: 'AI Detection',
      desc: 'YOLOv8 detects potholes & speed breakers'
    },
    {
      num: 3,
      color: '#f59e0b',
      icon: BarChart3,
      title: 'Severity Analysis',
      desc: 'Estimate hazard severity & depth'
    },
    {
      num: 4,
      color: '#8b5cf6',
      icon: Car,
      title: 'Vehicle Personalization',
      desc: 'Adjust risk based on ground clearance'
    },
    {
      num: 5,
      color: '#ef4444',
      icon: ShieldCheck,
      title: 'Risk Score',
      desc: 'Generate overall route risk score'
    }
  ];

  return (
    <section className="how-it-works-section" id="about-pipeline">
      <div className="how-it-works-header">
        <h3 className="section-title">How It Works</h3>
        <p className="section-subtitle">From road images to personalized risk analysis</p>
      </div>

      {/* Steps Pipeline Flow */}
      <div className="steps-flow-container">
        {steps.map((step, index) => {
          const IconComponent = step.icon;
          return (
            <React.Fragment key={step.num}>
              <div className="pipeline-step-card">
                <div 
                  className="step-badge-number"
                  style={{ backgroundColor: step.color }}
                >
                  {step.num}
                </div>

                <div 
                  className="step-icon-box"
                  style={{ backgroundColor: `${step.color}1f`, color: step.color }}
                >
                  <IconComponent size={24} />
                </div>

                <h4 className="step-title">{step.title}</h4>
                <p className="step-desc">{step.desc}</p>
              </div>

              {index < steps.length - 1 && (
                <div className="pipeline-step-arrow">
                  <ArrowRight size={18} />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Two Highlight Banner Cards */}
      <div className="how-it-works-banners-row">
        {/* Banner 1: Why It Matters */}
        <div className="feature-banner-card banner-why">
          <div className="banner-icon-col icon-yellow">
            <Lightbulb size={22} />
          </div>
          <div className="banner-text-col">
            <h4 className="banner-title">Why It Matters?</h4>
            <p className="banner-desc">
              Helps you choose safer routes, avoid vehicle underbody damage, and drive with total confidence.
            </p>
          </div>
        </div>

        {/* Banner 2: Built for Indian Roads */}
        <div className="feature-banner-card banner-india">
          <div className="banner-flag-icon">
            🇮🇳
          </div>
          <div className="banner-text-col">
            <h4 className="banner-title">Built for Indian Roads</h4>
            <p className="banner-desc">
              Trained on real Indian road conditions including potholes, speed breakers, barricades, and unmarked humps.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
