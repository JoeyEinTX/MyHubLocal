import { useState } from 'react';
import { useTheme } from '../hooks/useTheme';
import { PageHeader } from '../components/PageHeader';
import TelemetrySettings from './TelemetrySettings';

function ThemePreviewCard({ themeKey, themeData, currentTheme, mode, onSelect }) {
  const isSelected = currentTheme === themeKey;
  const colors = themeData[mode];
  
  return (
    <button
      onClick={() => onSelect(themeKey)}
      className={`group relative p-4 rounded-lg border-2 transition-all duration-200 text-left w-full bg-transparent ${
        isSelected
          ? 'border-primary shadow-md scale-105'
          : 'border-border-secondary hover:border-border-primary hover:shadow-sm'
      }`}
    >
      {/* Theme Name */}
      <div className={`text-sm font-medium mb-3 ${
        isSelected ? 'text-primary' : 'text-text'
      }`}>
        {themeData.name}
      </div>
      
      {/* Color Preview Grid */}
      <div className="grid grid-cols-4 gap-2 mb-3">
        {/* Primary Color */}
        <div className="space-y-1">
          <div
            className="w-full h-8 rounded border border-border-secondary"
            style={{ backgroundColor: `rgb(${colors.primary})` }}
            title="Primary Color"
          />
          <div className="text-xs text-center truncate text-text-secondary">
            Primary
          </div>
        </div>
        
        {/* Accent Color */}
        <div className="space-y-1">
          <div
            className="w-full h-8 rounded border border-border-secondary"
            style={{ backgroundColor: `rgb(${colors.accent})` }}
            title="Accent Color"
          />
          <div className="text-xs text-center truncate text-text-secondary">
            Accent
          </div>
        </div>
        
        {/* Success Color */}
        <div className="space-y-1">
          <div
            className="w-full h-8 rounded border border-border-secondary"
            style={{ backgroundColor: `rgb(${colors.success})` }}
            title="Success Color"
          />
          <div className="text-xs text-center truncate text-text-secondary">
            Success
          </div>
        </div>
        
        {/* Warning Color */}
        <div className="space-y-1">
          <div
            className="w-full h-8 rounded border border-border-secondary"
            style={{ backgroundColor: `rgb(${colors.warning})` }}
            title="Warning Color"
          />
          <div className="text-xs text-center truncate text-text-secondary">
            Warning
          </div>
        </div>
      </div>
      
      {/* Mini Preview Layout */}
      <div 
        className="relative h-12 rounded text-xs overflow-hidden border border-border-secondary"
        style={{ backgroundColor: `rgb(${colors.background})` }}
      >
        {/* Mini navbar */}
        <div 
          className="h-4 flex items-center px-2 border-b"
          style={{ 
            backgroundColor: `rgb(${colors.card})`,
            borderColor: `rgba(${colors.text}, 0.2)`,
            color: `rgb(${colors.text})`
          }}
        >
          <div 
            className="w-2 h-2 rounded-full mr-1"
            style={{ backgroundColor: `rgb(${colors.primary})` }}
          />
          <span style={{ fontSize: '8px' }}>MyHubLocal</span>
        </div>
        
        {/* Mini content */}
        <div className="p-1 flex space-x-1">
          <div 
            className="flex-1 h-6 rounded"
            style={{ backgroundColor: `rgb(${colors.card})` }}
          />
          <div 
            className="w-6 h-6 rounded"
            style={{ backgroundColor: `rgb(${colors.primary})` }}
          />
        </div>
      </div>
      
      {/* Selected Indicator */}
      {isSelected && (
        <div className="absolute top-2 right-2">
          <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center shadow-md">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
      )}
    </button>
  );
}

export default function Settings() {
  const { currentTheme, mode, toggleMode, setTheme, themes } = useTheme();
  const [activeTab, setActiveTab] = useState('appearance');

  const tabs = [
    { id: 'appearance', label: 'Appearance', icon: '🎨' },
    { id: 'telemetry', label: 'Telemetry', icon: '📊' }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Page Header */}
      <PageHeader 
        title="Settings"
        showThemeToggle={true}
        showBackToHome={true}
      />

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <p className="text-text-secondary">
            Customize your MyHub Local experience
          </p>
        </div>
        
        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-border-secondary">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary text-primary'
                      : 'border-transparent text-text-secondary hover:text-text hover:border-border-primary'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'appearance' && (
          <div>
            {/* Theme Selection */}
            <div className="rounded-lg shadow-md p-6 mb-6 bg-card border border-border-secondary">
              <h3 className="text-lg font-medium mb-4 text-text">
                Theme Selection
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(themes).map(([themeKey, themeData]) => (
                  <ThemePreviewCard
                    key={themeKey}
                    themeKey={themeKey}
                    themeData={themeData}
                    currentTheme={currentTheme}
                    mode={mode}
                    onSelect={setTheme}
                  />
                ))}
              </div>
            </div>

            {/* Hub Settings Section */}
            <div className="rounded-lg shadow-md p-6 mb-6 bg-card border border-border-secondary">
              <h3 className="text-lg font-medium mb-4 text-text">
                Hub Configuration
              </h3>
              
              <div className="text-sm space-y-2 text-text-secondary">
                <p><strong>Version:</strong> 0.1.0 (Development)</p>
                <p><strong>Platform:</strong> Raspberry Pi 5</p>
                <p><strong>Architecture:</strong> FastAPI + React</p>
                <p><strong>License:</strong> MIT</p>
                <p><strong>Current Theme:</strong> {themes[currentTheme].name} ({mode} mode)</p>
                <p><strong>Themes Available:</strong> {Object.keys(themes).length} themes × 2 modes = {Object.keys(themes).length * 2} variations</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'telemetry' && (
          <div>
            <TelemetrySettings />
          </div>
        )}
      </main>
    </div>
  );
}
