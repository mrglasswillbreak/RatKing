'use client';
import { motion } from 'framer-motion';
import { Moon, Navigation, Search, Sun } from 'lucide-react';
import { campusNodes, type RouteStep } from '../lib/graph';
import { useTheme } from '@/features/theme/components/theme-provider';

export function InstructionSheet({ steps, destinationId, onDestinationChange, follow, onFollowToggle }: { steps: RouteStep[]; destinationId: string; onDestinationChange: (id: string) => void; follow: boolean; onFollowToggle: () => void }) {
  const { resolvedTheme, setTheme } = useTheme();
  return <motion.aside drag="y" dragConstraints={{ top: -360, bottom: 0 }} initial={{ y: 0 }} className="glass-panel absolute inset-x-3 bottom-4 z-10 rounded-[2rem] border border-white/40 p-3 shadow-glass dark:border-white/10">
    <div className="mx-auto mb-3 h-1.5 w-12 rounded-full bg-slate-300 dark:bg-slate-600" />
    <div className="flex items-center gap-2">
      <div className="flex flex-1 items-center gap-2 rounded-full bg-white/80 px-4 py-3 text-slate-900 shadow-sm dark:bg-slate-900/80 dark:text-white"><Search size={18} /><select value={destinationId} onChange={(event) => onDestinationChange(event.target.value)} className="w-full bg-transparent outline-none">{campusNodes.map((node) => <option key={node.id} value={node.id}>{node.name}</option>)}</select></div>
      <button onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')} className="rounded-full bg-white/80 p-3 shadow-sm dark:bg-slate-900/80">{resolvedTheme === 'dark' ? <Sun /> : <Moon />}</button>
      <button onClick={onFollowToggle} className={`rounded-full p-3 shadow-sm ${follow ? 'bg-brand-500 text-white' : 'bg-white/80 dark:bg-slate-900/80'}`}><Navigation /></button>
    </div>
    <div className="mt-4 max-h-72 space-y-3 overflow-auto px-2 pb-2 text-sm text-slate-700 dark:text-slate-200">
      <p className="font-semibold text-slate-950 dark:text-white">Turn-by-turn guidance</p>
      {steps.map((step, index) => <div key={`${step.text}-${index}`} className="rounded-2xl bg-white/60 p-3 dark:bg-slate-950/50"><span className="font-medium text-brand-600">{index + 1}. </span>{step.text}<span className="ml-2 text-xs opacity-70">{step.distance}m</span></div>)}
    </div>
  </motion.aside>;
}
