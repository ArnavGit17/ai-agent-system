import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot, ChevronDown, ChevronUp, Clock } from 'lucide-react';
import PlanPanel from './PlanPanel.jsx';
import CriticPanel from './CriticPanel.jsx';
import SourcesPanel from './SourcesPanel.jsx';

export default function ChatMessage({ message }) {
  const [expanded, setExpanded] = useState(false);
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 animate-fade-up ${isUser ? 'justify-end' : ''}`}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center mt-1">
          <Bot size={16} className="text-accent-glow" />
        </div>
      )}

      <div className={`max-w-[75%] ${isUser ? 'order-first' : ''}`}>
        <div className={`rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-accent text-white rounded-br-md'
            : 'bg-surface-2 text-gray-200 rounded-bl-md'
        }`}>
          {isUser ? (
            <p className="text-sm">{message.content}</p>
          ) : (
            <div className="prose-agent text-sm">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Meta panels for assistant messages */}
        {!isUser && message.meta && (
          <div className="mt-2">
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-2 text-[11px] text-gray-500 hover:text-accent-glow transition-colors mb-2"
            >
              {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              {expanded ? 'Hide details' : 'Show plan, sources & evaluation'}
              {message.meta.duration_ms && (
                <span className="flex items-center gap-1 ml-2 text-gray-600">
                  <Clock size={10} />
                  {(message.meta.duration_ms / 1000).toFixed(1)}s
                </span>
              )}
            </button>

            {expanded && (
              <div className="space-y-3">
                <PlanPanel plan={message.meta.plan} />
                <SourcesPanel sources={message.meta.sources} />
                <CriticPanel evaluation={message.meta.evaluation} />
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-surface-3 flex items-center justify-center mt-1">
          <User size={16} className="text-gray-400" />
        </div>
      )}
    </div>
  );
}
