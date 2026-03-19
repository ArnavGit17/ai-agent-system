import React from 'react';
import { ListChecks, Globe, Database } from 'lucide-react';

export default function PlanPanel({ plan }) {
  if (!plan) return null;

  return (
    <div className="bg-surface-1 border border-surface-3 rounded-xl p-4 animate-fade-up">
      <h3 className="text-xs font-semibold uppercase tracking-widest text-accent-glow mb-3 flex items-center gap-2">
        <ListChecks size={14} /> Task Breakdown
      </h3>
      {plan.rewritten_query !== plan.original_query && (
        <p className="text-xs text-gray-400 mb-3 italic">
          Rewritten: "{plan.rewritten_query}"
        </p>
      )}
      <div className="space-y-2">
        {plan.subtasks.map((st, i) => (
          <div key={st.id || i} className="flex items-start gap-3 text-sm">
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-accent/20 text-accent text-[10px] flex items-center justify-center font-bold mt-0.5">
              {i + 1}
            </span>
            <div className="flex-1">
              <p className="text-gray-300">{st.description}</p>
              <div className="flex gap-2 mt-1">
                {st.tools_needed?.map((t) => (
                  <span key={t} className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-surface-3 text-gray-400">
                    {t === 'web_search' ? <Globe size={9} /> : <Database size={9} />}
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
