import type { Metadata, Viewport } from 'next';
import './globals.css';
import { ThemeProvider } from '@/features/theme/components/theme-provider';
import { ServiceWorkerRegister } from '@/features/offline/components/service-worker-register';

export const metadata: Metadata = {
  title: 'LASU Campus Navigator',
  description: 'Offline-first Apple Maps inspired navigation for LASU Ojo campus.',
  manifest: '/manifest.json',
  appleWebApp: { capable: true, title: 'LASU Navigator', statusBarStyle: 'black-translucent' }
};

export const viewport: Viewport = { themeColor: '#0a84ff', width: 'device-width', initialScale: 1, viewportFit: 'cover' };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" suppressHydrationWarning><body><ThemeProvider><ServiceWorkerRegister />{children}</ThemeProvider></body></html>;
}
