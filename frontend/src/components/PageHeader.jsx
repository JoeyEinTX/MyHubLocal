import { useTheme } from '../hooks/useTheme';
import { Link } from 'react-router-dom';

export function PageHeader({ title, onRefresh, showThemeToggle = true, showBackToHome = false, onScenesClick }) {
  const { currentTheme, mode, toggleMode, themes, isDark } = useTheme();

  const handleThemeToggle = () => {
    toggleMode();
  };

  return (
    <header className="sticky top-0 z-50 bg-background border-b border-border-secondary backdrop-blur-sm bg-opacity-95 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left side - Logo only */}
          <div className="flex items-center">
            <Link to="/" className="hover:opacity-90 transition-opacity">
              <img 
                src="/a-minimalist-vector-logo-design-featurin_k9DcxDcZSkGlchPqT4R7Yw_4PojX8wIQaGvcPgXEC-Fog.png" 
                alt="MyHub Logo" 
                className="h-14 w-auto object-contain border border-red-500"
                onLoad={() => console.log('Logo loaded successfully')}
                onError={(e) => {
                  console.error('Logo failed to load:', e);
                  e.target.style.border = '2px solid red';
                  e.target.alt = 'LOGO ERROR';
                }}
              />
            </Link>
          </div>

          {/* Right side - Controls */}
          <div className="flex items-center space-x-3">
            {/* Refresh button */}
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="p-2.5 bg-success/10 hover:bg-success/20 text-success hover:text-success rounded-xl transition-all duration-200 hover:scale-105 shadow-sm hover:shadow-md border border-success/20 hover:border-success/40"
                title="Refresh devices"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            )}

            {/* Scenes button */}
            {onScenesClick && (
              <button
                onClick={onScenesClick}
                className="p-2.5 bg-accent/10 hover:bg-accent/20 text-accent hover:text-accent rounded-xl transition-all duration-200 hover:scale-105 shadow-sm hover:shadow-md border border-accent/20 hover:border-accent/40"
                title="Scenes"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
            )}

            {/* Theme toggle */}
            {showThemeToggle && (
              <button
                onClick={handleThemeToggle}
                className="p-2.5 bg-primary/10 hover:bg-primary/20 text-primary hover:text-primary rounded-xl transition-all duration-200 hover:scale-105 shadow-sm hover:shadow-md border border-primary/20 hover:border-primary/40"
                title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
              >
                {isDark ? (
                  // Sun icon for light mode
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                ) : (
                  // Moon icon for dark mode
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                )}
              </button>
            )}

            {/* Settings link */}
            {!showBackToHome && (
              <Link
                to="/settings"
                className="p-2.5 bg-secondary/50 hover:bg-secondary text-text-secondary hover:text-primary rounded-xl transition-all duration-200 hover:scale-105 shadow-sm hover:shadow-md border border-border/30"
                title="Settings"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
