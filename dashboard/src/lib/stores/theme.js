import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Theme constants
export const THEMES = {
  LIGHT: 'pharmalight',
  DARK: 'pharmadark'
};

// Create theme store
function createThemeStore() {
  // Check for saved theme preference or default to light mode
  const storedTheme = browser ? localStorage.getItem('theme') : null;
  const prefersDark = browser ? window.matchMedia('(prefers-color-scheme: dark)').matches : false;
  const initialTheme = storedTheme || (prefersDark ? THEMES.DARK : THEMES.LIGHT);
  
  const { subscribe, set, update } = writable(initialTheme);
  
  return {
    subscribe,
    toggle: () => {
      update(theme => {
        const newTheme = theme === THEMES.LIGHT ? THEMES.DARK : THEMES.LIGHT;
        if (browser) {
          localStorage.setItem('theme', newTheme);
          updateDocument(newTheme);
        }
        return newTheme;
      });
    },
    set: (theme) => {
      if (browser) {
        localStorage.setItem('theme', theme);
        updateDocument(theme);
      }
      set(theme);
    },
    init: () => {
      if (browser) {
        updateDocument(initialTheme);
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
          if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? THEMES.DARK : THEMES.LIGHT;
            updateDocument(newTheme);
            set(newTheme);
          }
        });
      }
    }
  };
}

// Update document theme
function updateDocument(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  
  // Update class for Tailwind dark mode
  if (theme === THEMES.DARK) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}

export const theme = createThemeStore();

// Derived store for checking if dark mode is active
export const isDarkMode = derived(theme, $theme => $theme === THEMES.DARK);