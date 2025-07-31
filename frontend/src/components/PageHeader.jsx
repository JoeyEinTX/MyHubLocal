import { useTheme } from '../hooks/useTheme';

export function PageHeader({ title, onRefresh, showThemeToggle = true }) {
  const { currentTheme, setTheme, themes } = useTheme();

  const toggleThemeMode = () => {
    // Toggle between light and dark variant of current theme
    const currentThemeData = themes[currentTheme];
    const isCurrentlyDark = currentTheme.includes('-dark');
    
    if (isCurrentlyDark) {
      // Switch to light variant
      const lightTheme = currentTheme.replace('-dark', '-light');
      if (themes[lightTheme]) {
        setTheme(lightTheme);
      }
    } else {
      // Switch to dark variant
      const darkTheme = currentTheme.replace('-light', '-dark');
      if (themes[darkTheme]) {
        setTheme(darkTheme);
      }
    }
  };

  const isCurrentlyDark = currentTheme.includes('-dark');

  return (
    <header className="sticky top-0 z-50 bg-background border-b border-border-secondary backdrop-blur-sm bg-opacity-95">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left side - App name/logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-xl text-white font-bold">🏠</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-text">
                {title || "MyHub Local"}
              </h1>
              <p className="text-sm text-text-secondary">
                Smart Home Control
              </p>
            </div>
          </div>

          {/* Right side - Controls */}
          <div className="flex items-center space-x-3">
            {/* Refresh button */}
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="p-2 text-text-secondary hover:text-text hover:bg-surface-hover rounded-md transition-colors"
                title="Refresh devices"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            )}

            {/* Theme toggle */}
            {showThemeToggle && (
              <button
                onClick={toggleThemeMode}
                className="p-2 text-text-secondary hover:text-text hover:bg-surface-hover rounded-md transition-colors"
                title={`Switch to ${isCurrentlyDark ? 'light' : 'dark'} mode`}
              >
                {isCurrentlyDark ? (
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
            <a
              href="/settings"
              className="p-2 text-text-secondary hover:text-text hover:bg-surface-hover rounded-md transition-colors"
              title="Settings"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}
