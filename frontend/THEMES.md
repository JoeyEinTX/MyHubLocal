# Advanced Theme System Usage Guide

## Overview

MyHubLocal now includes a **comprehensive theme system** with 7 unique color themes, each available in light and dark modes, for a total of **14 theme variations**. The system uses only Tailwind's native color palette and includes **persistent theme storage** and **visual theme previews**.

### 🎨 Available Themes

1. **Calm & Clean** - Blue primary with emerald accents (professional)
2. **Sleek & Dark** - Blue primary with indigo accents (modern)
3. **Sunset Glow** - Orange primary with yellow/amber accents (warm)
4. **Ocean Breeze** - Sky primary with teal accents (cool)
5. **Forest Haze** - Green primary with lime accents (natural)
6. **Royal Plum** - Purple primary with pink accents (elegant)
7. **Steel & Slate** - Gray monochrome theme (minimal)

### ✨ New Features

- **🎨 Visual Theme Previews** - Rich preview cards showing color palettes and mini layouts
- **💾 Persistent Storage** - Your theme preferences are saved and restored automatically
- **🔄 Instant Switching** - Themes apply immediately without page reload
- **🎯 Semantic Classes** - All components use theme-agnostic color tokens

## How to Use

### Theme Selection Interface
1. Navigate to **Settings** page (`/settings`)
2. **Toggle Light/Dark Mode** with the prominent mode button
3. **Select Color Theme** from the visual grid of theme preview cards
4. **Hover over previews** to see detailed color information
5. Changes apply **instantly** and are **automatically saved**

### Theme Preview Cards Include:
- **Theme name** and selection indicator
- **Color swatches** for Primary, Accent, Background, and Card colors
- **Mini layout preview** showing how the theme looks in context
- **Hover effects** and smooth transitions

## Semantic Color System

### Core Semantic Classes
All components now use **semantic color tokens** that automatically adapt to any theme:

```jsx
// ✅ Primary semantic classes
<div className="bg-background">     {/* App background */}
<div className="bg-card">           {/* Card/panel background */}
<div className="text-text">         {/* Primary text */}
<div className="text-primary">      {/* Brand/link text */}
<div className="bg-primary">        {/* Primary buttons/highlights */}
<div className="bg-accent">         {/* Secondary buttons/accents */}
```

### Extended Semantic Classes
```jsx
// ✅ Extended semantic classes for specific use cases
<div className="text-text-secondary">   {/* Secondary text */}
<div className="text-text-muted">       {/* Muted/disabled text */}
<div className="border-border-primary"> {/* Primary borders */}
<div className="border-border-secondary"> {/* Secondary borders */}
<div className="bg-surface-hover">      {/* Hover backgrounds */}
<div className="bg-danger">             {/* Error/danger actions */}
<div className="bg-success">            {/* Success indicators */}
<div className="bg-warning">            {/* Warning indicators */}
```

### Component Example
```jsx
function MyComponent() {
  return (
    <div className="bg-card border border-border-secondary rounded-lg p-4">
      <h2 className="text-text font-bold">Title</h2>
      <p className="text-text-secondary">Description text</p>
      <button className="bg-primary text-white px-4 py-2 rounded">
        Action
      </button>
      <button className="bg-accent text-white px-4 py-2 rounded">
        Secondary
      </button>
    </div>
  );
}
```

## Technical Implementation

### Persistent Storage
```javascript
// Theme preferences are automatically saved to localStorage
localStorage.setItem('myhub-theme', 'sunset');  // Theme name
localStorage.setItem('myhub-mode', 'dark');     // Light/dark mode
```

### CSS Variables
Dynamic theming uses CSS custom properties:
```css
:root {
  --color-primary: 59 130 246;        /* RGB values */
  --color-accent: 16 185 129;
  --color-background: 249 250 251;
  --color-card: 255 255 255;
  --color-text: 31 41 55;
  --color-text-secondary: 107 114 128;
  /* ... additional semantic colors */
}
```

### Theme Context API
```jsx
import { useTheme } from '../hooks/useTheme';

function MyComponent() {
  const { 
    currentTheme,    // 'calm', 'sunset', etc.
    mode,           // 'light' or 'dark'
    isDark,         // boolean helper
    setTheme,       // function to change theme
    toggleMode,     // function to toggle light/dark
    themes          // all available theme data
  } = useTheme();
  
  return (
    <div className="bg-card text-text">
      <p>Current: {themes[currentTheme].name} ({mode})</p>
      <button onClick={toggleMode}>Toggle Mode</button>
      <button onClick={() => setTheme('royal')}>Royal Theme</button>
    </div>
  );
}
```

## Migration & Best Practices

### ❌ Avoid Hard-coded Colors
```jsx
// ❌ Don't use direct Tailwind colors in components
<div className="bg-blue-500 text-gray-900">
<div className="border-gray-200 dark:border-gray-600">
```

### ✅ Use Semantic Classes
```jsx
// ✅ Use semantic theme classes
<div className="bg-primary text-text">
<div className="border-border-secondary">
```

### Component Standards
1. **Always use semantic classes** for colors that should change with themes
2. **Only use direct colors** for fixed elements (e.g., `text-white` on colored buttons)
3. **Test with multiple themes** to ensure proper contrast and readability
4. **Use `text-text-secondary`** for less important text
5. **Use `border-border-secondary`** for standard borders

## Performance & Benefits

✅ **Instant theme switching** - No page reloads required  
✅ **Persistent preferences** - Settings restored on page refresh  
✅ **Type-safe colors** - All colors defined in Tailwind config  
✅ **No hard-coded colors** - Components automatically adapt  
✅ **Rich previews** - Visual feedback before selection  
✅ **14 total variations** - 7 themes × 2 modes  
✅ **Accessibility friendly** - Proper contrast ratios maintained  
✅ **Developer friendly** - Simple semantic class system  

## Files Architecture

### Core Theme System
- `tailwind.config.js` - Theme definitions using Tailwind colors
- `src/hooks/useTheme.jsx` - Theme context, persistence, CSS variables

### Component Implementation  
- `src/App.jsx` - App layout with semantic classes
- `src/pages/Settings.jsx` - Enhanced theme selection interface
- `src/pages/Home.jsx` - Semantic styling implementation
- `src/components/DeviceCard.jsx` - Component-level semantic classes

### Documentation
- `frontend/THEMES.md` - Complete theme system guide

The theme system is now production-ready with a user-friendly interface, complete persistence, and robust semantic styling that ensures all components automatically adapt to theme changes.
