import { useTheme } from '../hooks/useTheme';
import { PageHeader } from '../components/PageHeader';

function ThemePreviewCard({ themeKey, themeData, currentTheme, mode, onSelect }) {
  const isSelected = currentTheme === themeKey;
  const colors = themeData[mode];
  
  return (
    <button
      onClick={() => onSelect(themeKey)}
      className={`group relative p-4 rounded-lg border-2 transition-all duration-200 text-left w-full ${
        isSelected
          ? 'border-primary bg-primary bg-opacity-10 scale-105'
          : 'border-border-secondary hover:border-border-primary hover:bg-surface-hover'
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
            className="w-full h-8 rounded border"
            style={{ backgroundColor: `rgb(${colors.primary})` }}
            title="Primary"
          />
          <span className="text-xs text-text-muted">Primary</span>
        </div>
        
        {/* Accent Color */}
        <div className="space-y-1">
          <div
            className="w-full h-8 rounded border"
            style={{ backgroundColor: `rgb(${colors.accent})` }}
            title="Accent"
          />
          <span className="text-xs text-text-muted">Accent</span>
        </div>
        
        {/* Background Color */}
        <div className="space-y-1">
          <div
            className="w-full h-8 rounded border"
            style={{ 
              backgroundColor: `rgb(${colors.background})`,
              border: `1px solid rgb(${colors.text})`
            }}
            title="Background"
          />
          <span className="text-xs text-text-muted">Background</span>
        </div>
        
        {/* Card Color */}
        <div className="space-y-1">
          <div
            className="w-full h-8 rounded border"
            style={{ 
              backgroundColor: `rgb(${colors.card})`,
              border: `1px solid rgb(${colors.text})`
            }}
            title="Card"
          />
          <span className="text-xs text-text-muted">Card</span>
        </div>
      </div>
      
      {/* Mini Preview Layout */}
      <div 
        className="relative h-12 rounded text-xs overflow-hidden border"
        style={{ backgroundColor: `rgb(${colors.background})` }}
      >
        {/* Mini navbar */}
        <div 
          className="h-4 flex items-center px-2 border-b"
          style={{ 
            backgroundColor: `rgb(${colors.card})`,
            borderColor: `rgb(${colors.text})`,
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
            className="w-4 h-6 rounded"
            style={{ backgroundColor: `rgb(${colors.accent})` }}
          />
        </div>
      </div>
      
      {/* Selection indicator */}
      {isSelected && (
        <div className="absolute top-2 right-2">
          <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center">
            <span className="text-white text-xs">✓</span>
          </div>
        </div>
      )}
    </button>
  );
}

export default function Settings() {
  const { currentTheme, mode, toggleMode, setTheme, themes } = useTheme();

  return (
    <div className="min-h-screen bg-background">
      {/* Page Header */}
      <PageHeader 
        title="Settings"
        showThemeToggle={true}
      />

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text mb-2">
            Settings
          </h1>
          <p className="text-text-secondary">
            Customize your MyHub Local experience
          </p>
        </div>
        
        {/* Theme Settings Section */}
        <div className="rounded-lg shadow-md p-6 mb-6 bg-card border border-border-secondary">
          <h3 className="text-lg font-medium mb-4 text-text">
            Appearance
          </h3>
          
          {/* Light/Dark Mode Toggle */}
          <div className="flex items-center justify-between mb-6 pb-6 border-b border-border-secondary">
            <div>
              <h4 className="font-medium text-text">
                Theme Mode
              </h4>
              <p className="text-sm text-text-secondary">
              Switch between light and dark mode
            </p>
          </div>
          
          <button
            onClick={toggleMode}
            className="px-6 py-3 rounded-md font-medium transition-all duration-200 flex items-center space-x-3 bg-primary hover:opacity-80 text-white"
          >
            <span className="text-lg">{mode === 'dark' ? '☀️' : '🌙'}</span>
            <span>{mode === 'dark' ? 'Switch to Light' : 'Switch to Dark'}</span>
          </button>
        </div>

        {/* Theme Color Palette Selection */}
        <div>
          <h4 className="font-medium text-text mb-2">
            Color Theme
          </h4>
          <p className="text-sm text-text-secondary mb-6">
            Choose your preferred color palette. Changes apply instantly across the app.
          </p>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
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
      </div>

      {/* Hub Settings Section (Placeholder) */}
      <div className="rounded-lg shadow-md p-6 mb-6 bg-card border border-border-secondary">
        <h3 className="text-lg font-medium mb-4 text-text">
          Hub Configuration
        </h3>
        
        <div className="text-sm text-text-secondary space-y-2">
          <p>• Z-Wave USB device configuration</p>
          <p>• Network settings</p>
          <p>• Device discovery settings</p>
          <p>• Automation rules and scenes</p>
          <p className="mt-4 italic text-text-muted">Coming soon...</p>
        </div>
      </div>

      {/* About Section */}
      <div className="rounded-lg shadow-md p-6 bg-card border border-border-secondary">
        <h3 className="text-lg font-medium mb-4 text-text">
          About MyHubLocal
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
      </main>
    </div>
  );
}
