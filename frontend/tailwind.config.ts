import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Warm & Calming Visual Identity
        primary: {
          blue: '#6B9BD1',
          green: '#8FA998',
          purple: '#9B87C4',
        },
        neutral: {
          white: '#F9F7F4',
          gray: '#E8E6E3',
          charcoal: '#3A3935',
        },
        accent: {
          orange: '#E8A87C',
          mint: '#A8D5BA',
          lavender: '#D4BFDB',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        'xl': '16px',
      },
      boxShadow: {
        'soft': '0 2px 12px rgba(0,0,0,0.06)',
      },
    },
  },
  plugins: [],
}

export default config
