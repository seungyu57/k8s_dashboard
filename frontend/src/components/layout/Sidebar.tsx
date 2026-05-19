import type React from 'react';
import { Activity, Boxes, Cpu, Gauge, ListTree, Server } from 'lucide-react';

export type PageKey = 'overview' | 'nodes' | 'nodeDetail' | 'pods' | 'podDetail' | 'events' | 'logs' | 'gpu';

type Props = { current: PageKey; onNavigate: (page: PageKey) => void };

const items: { key: PageKey; label: string; icon: React.ReactNode }[] = [
  { key: 'overview', label: 'Overview', icon: <Gauge size={18} /> },
  { key: 'nodes', label: 'Nodes', icon: <Server size={18} /> },
  { key: 'pods', label: 'Pods', icon: <Boxes size={18} /> },
  { key: 'events', label: 'Events', icon: <Activity size={18} /> },
  { key: 'logs', label: 'Pod Logs', icon: <ListTree size={18} /> },
  { key: 'gpu', label: 'GPU', icon: <Cpu size={18} /> },
];

export function Sidebar({ current, onNavigate }: Props) {
  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 p-4">
      <div className="mb-8">
        <div className="text-lg font-bold">K8s ReadOnly</div>
        <div className="text-xs text-slate-500">local cluster</div>
      </div>
      <nav className="space-y-1">
        {items.map((item) => (
          <button
            key={item.key}
            onClick={() => onNavigate(item.key)}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition ${current === item.key ? 'bg-sky-500/15 text-sky-300' : 'text-slate-300 hover:bg-slate-900'}`}
          >
            {item.icon}
            {item.label}
          </button>
        ))}
      </nav>
    </aside>
  );
}
