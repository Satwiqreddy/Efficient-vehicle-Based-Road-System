import React from 'react';
import { Heart } from 'lucide-react';

export default function Footer({ onNavHome, onNavAbout }) {
  return (
    <footer className="app-footer">
      <div className="footer-main-container">
        <div className="footer-brand-side">
          <div className="footer-logo">
            <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" className="road-logo-svg small">
              <path d="M16 2L3 28H13L15 16L16 8L17 16L19 28H29L16 2Z" fill="#16A34A" />
              <line x1="16" y1="10" x2="16" y2="13" stroke="white" strokeWidth="2" strokeLinecap="round" />
              <line x1="16" y1="17" x2="16" y2="21" stroke="white" strokeWidth="2" strokeLinecap="round" />
              <line x1="16" y1="25" x2="16" y2="27" stroke="white" strokeWidth="2" strokeLinecap="round" />
            </svg>
            <div className="footer-brand-text">
              <span className="footer-title">RoadGuard</span>
              <span className="footer-subtitle">Safer Roads • Smarter Journeys</span>
            </div>
          </div>
        </div>

        <nav className="footer-links">
          <button type="button" className="footer-link-btn" onClick={onNavHome}>Home</button>
          <button type="button" className="footer-link-btn" onClick={onNavAbout}>About</button>
          <a href="mailto:support@roadguard.ai" className="footer-link-btn">Contact</a>
        </nav>

        <div className="footer-copy">
          <span>Made with <Heart size={14} className="heart-icon-inline" fill="#ef4444" color="#ef4444" /> for safer roads in India</span>
        </div>
      </div>

      {/* Aesthetic attributes badge bar */}
      <div className="footer-attributes-bar">
        <span>Clean</span> • <span>Professional</span> • <span>Modern</span> • <span>Reliable</span> • <span>Easy to use</span> • <span>Eye-friendly</span>
      </div>
    </footer>
  );
}
