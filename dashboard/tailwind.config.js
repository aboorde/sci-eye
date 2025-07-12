/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Source Serif Pro', 'serif']
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        }
      }
    }
  },
  plugins: [require('daisyui')],
  darkMode: 'class',
  daisyui: {
    themes: [
      {
        pharmalight: {
          'primary': '#0ea5e9',          // Sky blue - clinical, trustworthy
          'primary-focus': '#0284c7',
          'primary-content': '#ffffff',
          'secondary': '#8b5cf6',        // Purple - innovation, research
          'secondary-focus': '#7c3aed',
          'secondary-content': '#ffffff',
          'accent': '#10b981',           // Emerald - health, growth
          'accent-focus': '#059669',
          'accent-content': '#ffffff',
          'neutral': '#2a2e37',
          'neutral-focus': '#16181d',
          'neutral-content': '#ffffff',
          'base-100': '#ffffff',
          'base-200': '#f9fafb',
          'base-300': '#f3f4f6',
          'base-content': '#111827',
          'info': '#06b6d4',             // Cyan - information
          'success': '#10b981',          // Green - positive results
          'warning': '#f59e0b',          // Amber - caution
          'error': '#ef4444',            // Red - safety alerts
          '--rounded-box': '0.5rem',
          '--rounded-btn': '0.375rem',
          '--rounded-badge': '1rem',
          '--animation-btn': '0.25s',
          '--animation-input': '0.2s',
          '--btn-text-case': 'none',
          '--btn-focus-scale': '0.95',
          '--border-btn': '1px',
          '--tab-border': '1px',
          '--tab-radius': '0.5rem'
        },
        pharmadark: {
          'primary': '#38bdf8',          // Lighter sky blue for dark mode
          'primary-focus': '#0ea5e9',
          'primary-content': '#0c4a6e',
          'secondary': '#a78bfa',        // Lighter purple
          'secondary-focus': '#8b5cf6',
          'secondary-content': '#1e1b4b',
          'accent': '#34d399',           // Lighter emerald
          'accent-focus': '#10b981',
          'accent-content': '#064e3b',
          'neutral': '#1e293b',
          'neutral-focus': '#0f172a',
          'neutral-content': '#e2e8f0',
          'base-100': '#0f172a',         // Deep slate background
          'base-200': '#1e293b',
          'base-300': '#334155',
          'base-content': '#e2e8f0',
          'info': '#22d3ee',
          'success': '#34d399',
          'warning': '#fbbf24',
          'error': '#f87171',
          '--rounded-box': '0.5rem',
          '--rounded-btn': '0.375rem',
          '--rounded-badge': '1rem',
          '--animation-btn': '0.25s',
          '--animation-input': '0.2s',
          '--btn-text-case': 'none',
          '--btn-focus-scale': '0.95',
          '--border-btn': '1px',
          '--tab-border': '1px',
          '--tab-radius': '0.5rem'
        }
      }
    ]
  }
}