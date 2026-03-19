import React from 'react';
import { ExternalLink, FileText } from 'lucide-react';

export default function SourcesPanel({ sources }) {
  if (!sources?.length) return null;

  return (
    <div className="bg-surface-1 border border-surface-3 rounded-xl p-4 animate-fade-up">
      <h3 className="text-xs font-semibold uppercase tracking-widest text-accent-glow mb-3 flex items-center gap-2">
        <FileText size={14} /> Sources ({sources.length})
      </h3>
      <div className="flex flex-wrap gap-2">
        {sources.map((src, i) => {
          const isUrl = src.startsWith('http');
          return (
            <span key={i} className="inline-flex items-center gap-1.5 text-[11px] px-3 py-1.5 rounded-lg bg-surface-2 text-gray-400 hover:text-accent-glow transition-colors">
              {isUrl ? <ExternalLink size={10} /> : <FileText size={10} />}
              {isUrl ? new URL(src).hostname : src}
            </span>
          );
        })}
      </div>
    </div>
  );
}
