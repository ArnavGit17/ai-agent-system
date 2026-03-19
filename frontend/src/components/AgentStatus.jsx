import React from 'react';
import { Brain, Search, Sparkles, ShieldCheck, Loader2 } from 'lucide-react';

const AGENTS = [
  { key: 'planner', label: 'Planner', icon: Brain, color: '#6c5ce7' },
  { key: 'researcher', label: 'Researcher', icon: Search, color: '#0984e3' },
  { key: 'reasoner', label: 'Reasoner', icon: Sparkles, color: '#00b894' },
  { key: 'critic', label: 'Critic', icon: ShieldCheck, color: '#fdcb6e' },
];

export default function AgentStatus({ activeAgent }) {
  if (!activeAgent) return null;

  return (
    <div className="flex items-center gap-1 px-3 py-2 animate-fade-up">
      {AGENTS.map((ag) => {
        const Icon = ag.icon;
        const isActive = ag.key === activeAgent;
        const isPast = AGENTS.findIndex(a => a.key === activeAgent) > AGENTS.findIndex(a => a.key === ag.key);

        return (
          <div key={ag.key} className="flex items-center gap-1">
            <div
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium transition-all duration-300 ${
                isActive
                  ? 'bg-surface-2 border border-surface-3 glow-pulse'
                  : isPast
                  ? 'opacity-60'
                  : 'opacity-30'
              }`}
              style={isActive ? { borderColor: ag.color + '40' } : {}}
            >
              {isActive ? (
                <Loader2 size={10} className="animate-spin" style={{ color: ag.color }} />
              ) : (
                <Icon size={10} style={{ color: isPast ? ag.color : undefined }} />
              )}
              <span style={isActive || isPast ? { color: ag.color } : {}}>{ag.label}</span>
            </div>
            {ag.key !== 'critic' && (
              <div className={`w-4 h-px ${isPast ? 'bg-gray-600' : 'bg-surface-3'}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
