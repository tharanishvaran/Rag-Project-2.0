import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const THEMES = [
  { id: 'dark-cyber', name: 'Dark Cyber', icon: '🌌', type: 'dark', color: '#00f2fe' },
  { id: 'electric-violet', name: 'Electric Violet', icon: '🟣', type: 'dark', color: '#d946ef' },
  { id: 'emerald-tech', name: 'Emerald Tech', icon: '🌿', type: 'dark', color: '#10b981' },
  { id: 'light-luxury', name: 'Executive Light', icon: '☀️', type: 'light', color: '#6366f1' },
];

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('smartdoc_theme') || 'dark-cyber';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('smartdoc_theme', theme);
  }, [theme]);

  const changeTheme = (newTheme) => {
    if (THEMES.some(t => t.id === newTheme)) {
      setTheme(newTheme);
    }
  };

  return (
    <ThemeContext.Provider value={{ theme, changeTheme, themes: THEMES }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
