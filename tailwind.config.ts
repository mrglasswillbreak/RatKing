import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: { 50: '#eef8ff', 500: '#0a84ff', 600: '#006edb' },
        ink: '#111827'
      },
      boxShadow: { glass: '0 18px 60px rgba(15, 23, 42, 0.18)' }
    }
  },
  plugins: []
};
export default config;
