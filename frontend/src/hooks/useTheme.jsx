import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Theme definitions using Tailwind's native color tokens
const THEMES = {
  'calm': {
    name: 'Calm & Clean',
    light: {
      primary: '59 130 246', // blue-500
      accent: '16 185 129', // emerald-500
      background: '249 250 251', // gray-50
      card: '255 255 255', // white
      text: '31 41 55', // gray-800
    },
    dark: {
      primary: '37 99 235', // blue-600
      accent: '5 150 105', // emerald-600
      background: '17 24 39', // gray-900
      card: '31 41 55', // gray-800
      text: '243 244 246', // gray-100
    }
  },
  'sleek': {
    name: 'Sleek & Dark',
    light: {
      primary: '37 99 235', // blue-600
      accent: '99 102 241', // indigo-500
      background: '243 244 246', // gray-100
      card: '255 255 255', // white
      text: '17 24 39', // gray-900
    },
    dark: {
      primary: '29 78 216', // blue-700
      accent: '79 70 229', // indigo-600
      background: '15 23 42', // slate-900
      card: '30 41 59', // slate-800
      text: '226 232 240', // slate-200
    }
  },
  'sunset': {
    name: 'Sunset Glow',
    light: {
      primary: '249 115 22', // orange-500
      accent: '250 204 21', // yellow-400
      background: '255 251 235', // amber-50
      card: '254 243 199', // amber-100
      text: '154 52 18', // orange-900
    },
    dark: {
      primary: '234 88 12', // orange-600
      accent: '245 158 11', // amber-500
      background: '23 23 23', // neutral-900
      card: '38 38 38', // neutral-800
      text: '252 211 77', // amber-200
    }
  },
  'ocean': {
    name: 'Ocean Breeze',
    light: {
      primary: '14 165 233', // sky-500
      accent: '20 184 166', // teal-500
      background: '240 249 255', // sky-50
      card: '224 242 254', // sky-100
      text: '22 78 99', // cyan-900
    },
    dark: {
      primary: '2 132 199', // sky-600
      accent: '13 148 136', // teal-600
      background: '22 78 99', // cyan-900
      card: '21 94 117', // cyan-800
      text: '165 243 252', // cyan-200
    }
  },
  'forest': {
    name: 'Forest Haze',
    light: {
      primary: '34 197 94', // green-500
      accent: '132 204 22', // lime-500
      background: '240 253 244', // green-50
      card: '220 252 231', // green-100
      text: '20 83 45', // green-900
    },
    dark: {
      primary: '22 163 74', // green-600
      accent: '101 163 13', // lime-600
      background: '6 78 59', // emerald-900
      card: '6 95 70', // emerald-800
      text: '187 247 208', // green-200
    }
  },
  'royal': {
    name: 'Royal Plum',
    light: {
      primary: '168 85 247', // purple-500
      accent: '236 72 153', // pink-500
      background: '250 245 255', // purple-50
      card: '243 232 255', // purple-100
      text: '88 28 135', // purple-900
    },
    dark: {
      primary: '147 51 234', // purple-600
      accent: '219 39 119', // pink-600
      background: '49 46 129', // indigo-900
      card: '55 48 163', // indigo-800
      text: '196 181 253', // purple-200
    }
  },
  'steel': {
    name: 'Steel & Slate',
    light: {
      primary: '107 114 128', // gray-500
      accent: '156 163 175', // gray-400
      background: '249 250 251', // gray-50
      card: '243 244 246', // gray-100
      text: '17 24 39', // gray-900
    },
    dark: {
      primary: '75 85 99', // gray-600
      accent: '107 114 128', // gray-500
      background: '17 24 39', // gray-900
      card: '31 41 55', // gray-800
      text: '243 244 246', // gray-100
    }
  }
};

export const ThemeProvider = ({ children }) => {
  // Load theme from localStorage or default to 'calm' and 'light'
  const [currentTheme, setCurrentTheme] = useState(() => {
    try {
      return localStorage.getItem('myhub-theme') || 'calm';
    } catch {
      return 'calm';
    }
  });
  
  const [mode, setMode] = useState(() => {
    try {
      return localStorage.getItem('myhub-mode') || 'light';
    } catch {
      return 'light';
    }
  });

  // Apply theme colors to CSS variables
  useEffect(() => {
    const root = document.documentElement;
    const theme = THEMES[currentTheme];
    const colors = theme[mode];
    
    // Set primary CSS variables for the current theme
    root.style.setProperty('--color-primary', colors.primary);
    root.style.setProperty('--color-accent', colors.accent);
    root.style.setProperty('--color-background', colors.background);
    root.style.setProperty('--color-card', colors.card);
    root.style.setProperty('--color-text', colors.text);
    
    // Set additional semantic color variables
    if (mode === 'dark') {
      root.style.setProperty('--color-text-secondary', '156 163 175'); // gray-400
      root.style.setProperty('--color-text-muted', '107 114 128'); // gray-500
      root.style.setProperty('--color-border-primary', '75 85 99'); // gray-600
      root.style.setProperty('--color-border-secondary', '55 65 81'); // gray-700
      root.style.setProperty('--color-surface-hover', '55 65 81'); // gray-700
      root.style.setProperty('--color-danger', '239 68 68'); // red-500
      root.style.setProperty('--color-success', '34 197 94'); // green-500
      root.style.setProperty('--color-warning', '245 158 11'); // amber-500
    } else {
      root.style.setProperty('--color-text-secondary', '107 114 128'); // gray-500
      root.style.setProperty('--color-text-muted', '156 163 175'); // gray-400
      root.style.setProperty('--color-border-primary', '209 213 219'); // gray-300
      root.style.setProperty('--color-border-secondary', '229 231 235'); // gray-200
      root.style.setProperty('--color-surface-hover', '249 250 251'); // gray-50
      root.style.setProperty('--color-danger', '239 68 68'); // red-500
      root.style.setProperty('--color-success', '34 197 94'); // green-500
      root.style.setProperty('--color-warning', '245 158 11'); // amber-500
    }
    
    // Save to localStorage
    try {
      localStorage.setItem('myhub-theme', currentTheme);
      localStorage.setItem('myhub-mode', mode);
    } catch {
      // Ignore localStorage errors
    }
  }, [currentTheme, mode]);

  const toggleMode = () => {
    setMode(prev => prev === 'light' ? 'dark' : 'light');
  };

  const setTheme = (themeName) => {
    if (THEMES[themeName]) {
      setCurrentTheme(themeName);
    }
  };

  const value = {
    currentTheme,
    mode,
    setTheme,
    setMode,
    toggleMode,
    themes: THEMES,
    isDark: mode === 'dark'
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};
