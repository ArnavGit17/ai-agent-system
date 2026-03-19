import React from 'react';
import { ShieldCheck, AlertTriangle, Lightbulb } from 'lucide-react';
import ScoreGauge from './ScoreGauge.jsx';

export default function CriticPanel({ evaluation }) {
  if (!evaluation) return null;

  return (
    <div className="bg-surface-1 border border-surface-3 rounded-xl p-4 animate-fade-up">
      <h3 className="text-xs font-semibold uppercase tracking-widest text-accent-glow mb-4 flex items-center gap-2">
        {evaluation.approved ? <ShieldCheck size={14} className="text-success" /> : <AlertTriangle size={14} className="text-warning" />}
        Critic Evaluation
        <span className={`ml-auto text-[10px] px-2 py-0.5 rounded-full ${evaluation.approved ? 'bg-success/20 text-success' : 'bg-warning/20 text-warning'}`}>
          {evaluation.approved ? 'APPROVED' : 'NEEDS WORK'}
        </span>
      </h3>

      <div className="flex justify-around mb-4">
        <ScoreGauge label="Relevance" score={evaluation.relevance_score} />
        <ScoreGauge label="Accuracy" score={evaluation.accuracy_score} />
        <ScoreGauge label="Complete" score={evaluation.completeness_score} />
        <ScoreGauge label="Overall" score={evaluation.overall_score} size={60} />
      </div>

      {evaluation.feedback && (
        <p className="text-xs text-gray-400 mb-3 leading-relaxed">{evaluation.feedback}</p>
      )}

      {evaluation.improvements?.length > 0 && (
        <div className="space-y-1">
          {evaluation.improvements.map((imp, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-gray-500">
              <Lightbulb size={11} className="text-warning mt-0.5 flex-shrink-0" />
              {imp}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
