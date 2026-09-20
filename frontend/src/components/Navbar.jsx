import React from 'react';
import { Moon, Sun, Settings, Clock, Info } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, darkMode, setDarkMode, onOpenSettings, backendOnline, liveMode }) {
  const statusClass = !liveMode ? 'demo' : backendOnline === null ? 'unknown' : backendOnline ? 'online' : 'offline';
  const statusLabel = !liveMode ? 'Demo mode' : backendOnline === null ? 'Checking…' : backendOnline ? 'AI backend online' : 'Backend offline';

  return (
    <header className="navbar-container">
      <div className="navbar-content">
        {/* Brand Logo */}
        <div className="navbar-brand" onClick={() => setActiveTab('home')} style={{ cursor: 'pointer' }}>
          <div className="brand-logo-icon">
            <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" className="road-logo-svg">
              <path d="M16 2L3 28H13L15 16L16 8L17 16L19 28H29L16 2Z" fill="#16A34A" />
              <line x1="16" y1="10" x2="16" y2="13" stroke="white" strokeWidth="2" strokeLinecap="round" />
              <line x1="16" y1="17" x2="16" y2="21" stroke="white" strokeWidth="2" strokeLinecap="round" />
              <line x1="16" y1="25" x2="16" y2="27" stroke="white" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
          <div className="brand-text">
            <span className="brand-name">RoadGuard</span>
            <span className="brand-tagline">Safer Roads • Smarter Journeys</span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="navbar-nav">
          <button
            className={`nav-link-btn ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
          >
            Home
          </button>
          <button
            className="nav-link-btn"
            onClick={() => setActiveTab('history')}
          >
            <Clock size={16} className="nav-icon-inline" />
            History
          </button>
          <button
            className={`nav-link-btn ${activeTab === 'about' ? 'active' : ''}`}
            onClick={() => setActiveTab('about')}
          >
            <Info size={16} className="nav-icon-inline" />
            About
          </button>
        </nav>

        {/* Header Right Actions */}
        <div className="navbar-actions">
          <button
            type="button"
            className={`backend-status-chip status-${statusClass}`}
            onClick={onOpenSettings}
            title={`${statusLabel} — click to configure`}
          >
            <span className="status-dot"></span>
            <span className="status-label">{statusLabel}</span>
          </button>

          <button
            className="action-icon-btn"
            title="Settings"
            onClick={onOpenSettings}
            aria-label="Settings"
          >
            <Settings size={18} />
          </button>

          <button
            className="action-icon-btn theme-toggle-btn"
            onClick={() => setDarkMode(!darkMode)}
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle theme"
          >
            {darkMode ? <Sun size={18} className="theme-sun-icon" /> : <Moon size={18} />}
          </button>
        </div>
      </div>
    </header>
  );
}
