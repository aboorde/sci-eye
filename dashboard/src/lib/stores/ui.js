import { writable } from 'svelte/store';

// Theme store
function createThemeStore() {
  const { subscribe, set, update } = writable('pharmalight');

  return {
    subscribe,
    toggle: () => {
      update(current => {
        const newTheme = current === 'pharmalight' ? 'pharmadark' : 'pharmalight';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Update class for Tailwind dark mode
        if (newTheme === 'pharmadark') {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
        
        return newTheme;
      });
    },
    init: () => {
      // Check for saved theme or use system preference
      const saved = localStorage.getItem('theme');
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const initialTheme = saved || (prefersDark ? 'pharmadark' : 'pharmalight');
      
      document.documentElement.setAttribute('data-theme', initialTheme);
      if (initialTheme === 'pharmadark') {
        document.documentElement.classList.add('dark');
      }
      
      set(initialTheme);
    }
  };
}

export const theme = createThemeStore();

// Sidebar state
export const sidebarOpen = writable(true);

// Article view mode
export const articleViewMode = writable('grid'); // 'grid' or 'list'

// Selected article for detail view
export const selectedArticle = writable(null);

// Toast notifications
function createToastStore() {
  const { subscribe, update } = writable([]);
  let nextId = 0;

  return {
    subscribe,
    show: (message, type = 'info', duration = 3000) => {
      const id = nextId++;
      const toast = { id, message, type };
      
      update(toasts => [...toasts, toast]);
      
      if (duration > 0) {
        setTimeout(() => {
          update(toasts => toasts.filter(t => t.id !== id));
        }, duration);
      }
      
      return id;
    },
    dismiss: (id) => {
      update(toasts => toasts.filter(t => t.id !== id));
    }
  };
}

export const toasts = createToastStore();

// Chart time range
export const chartTimeRange = writable('7d'); // '7d', '30d', '90d', 'all'

// Dashboard refresh interval
export const refreshInterval = writable(null);