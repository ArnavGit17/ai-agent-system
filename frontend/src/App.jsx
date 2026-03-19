import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Zap, Trash2, Globe, Database } from 'lucide-react';
import ChatMessage from './components/ChatMessage.jsx';
import AgentStatus from './components/AgentStatus.jsx';
import UploadButton from './components/UploadButton.jsx';
import { sendQuery } from './hooks/api.js';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeAgent, setActiveAgent] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [useRag, setUseRag] = useState(true);
  const [useWeb, setUseWeb] = useState(true);
  const [docCount, setDocCount] = useState(0);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);

  const simulateAgentProgress = () => {
    const agents = ['planner', 'researcher', 'reasoner', 'critic'];
    let i = 0;
    const interval = setInterval(() => {
      if (i < agents.length) {
        setActiveAgent(agents[i]);
        i++;
      } else {
        clearInterval(interval);
      }
    }, 1800);
    return () => clearInterval(interval);
  };

  const handleSubmit = async (e) => {
    e?.preventDefault();
    const query = input.trim();
    if (!query || loading) return;

    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: query }]);
    setLoading(true);
    const cleanup = simulateAgentProgress();

    try {
      const res = await sendQuery(query, sessionId, useRag, useWeb);
      setSessionId(res.session_id);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: res.answer,
          meta: {
            plan: res.plan,
            evaluation: res.evaluation,
            sources: res.sources,
            duration_ms: res.duration_ms,
          },
        },
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: `**Error:** ${err.message}` },
      ]);
    } finally {
      setLoading(false);
      setActiveAgent(null);
      cleanup();
      inputRef.current?.focus();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSessionId(null);
  };

  return (
    <div className="h-screen flex flex-col bg-surface-0">
      {/* ── Header ── */}
      <header className="flex-shrink-0 border-b border-surface-3 bg-surface-1/80 backdrop-blur-md">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent to-purple-400 flex items-center justify-center shadow-lg shadow-accent/20">
              <Zap size={18} className="text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-tight text-gray-100">Autonomous Agent System</h1>
              <p className="text-[10px] text-gray-500 tracking-wider uppercase">Planner → Researcher → Reasoner → Critic</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <UploadButton onUpload={(r) => r.chunks_created && setDocCount(d => d + r.chunks_created)} />

            <button
              onClick={() => setUseWeb(w => !w)}
              className={`p-2 rounded-lg transition-all ${useWeb ? 'bg-blue-500/15 text-blue-400' : 'bg-surface-2 text-gray-600'}`}
              title="Toggle web search"
            >
              <Globe size={14} />
            </button>

            <button
              onClick={() => setUseRag(r => !r)}
              className={`p-2 rounded-lg transition-all ${useRag ? 'bg-emerald-500/15 text-emerald-400' : 'bg-surface-2 text-gray-600'}`}
              title="Toggle RAG"
            >
              <Database size={14} />
            </button>

            {messages.length > 0 && (
              <button onClick={clearChat} className="p-2 rounded-lg bg-surface-2 text-gray-500 hover:text-danger transition-colors" title="Clear chat">
                <Trash2 size={14} />
              </button>
            )}
          </div>
        </div>
      </header>

      {/* ── Messages ── */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-[60vh] text-center animate-fade-up">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent/20 to-purple-500/10 flex items-center justify-center mb-6 border border-accent/10">
                <Zap size={32} className="text-accent-glow" />
              </div>
              <h2 className="text-xl font-semibold text-gray-200 mb-2">Multi-Agent AI System</h2>
              <p className="text-sm text-gray-500 max-w-md leading-relaxed mb-6">
                Ask complex questions. The system breaks them into subtasks, retrieves from
                documents and the web, synthesizes an answer, and self-evaluates.
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {[
                  'Explain how transformers work in deep learning',
                  'Compare React vs Vue for enterprise apps',
                  'Summarize my uploaded research paper',
                ].map((q) => (
                  <button
                    key={q}
                    onClick={() => { setInput(q); inputRef.current?.focus(); }}
                    className="text-xs px-3 py-2 rounded-lg bg-surface-2 border border-surface-3 text-gray-400 hover:text-accent-glow hover:border-accent/30 transition-all"
                  >
                    {q}
                  </button>
                ))}
              </div>
              {docCount > 0 && (
                <p className="mt-4 text-[11px] text-emerald-500">{docCount} document chunks indexed</p>
              )}
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatMessage key={i} message={msg} />
          ))}

          {loading && <AgentStatus activeAgent={activeAgent} />}

          <div ref={bottomRef} />
        </div>
      </main>

      {/* ── Input ── */}
      <footer className="flex-shrink-0 border-t border-surface-3 bg-surface-1/80 backdrop-blur-md">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center gap-3 bg-surface-2 border border-surface-3 rounded-xl px-4 py-2 focus-within:border-accent/40 transition-colors">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a complex question..."
              disabled={loading}
              className="flex-1 bg-transparent text-sm text-gray-200 placeholder-gray-600 outline-none"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="flex-shrink-0 w-8 h-8 rounded-lg bg-accent hover:bg-accent-dim disabled:opacity-30 disabled:hover:bg-accent flex items-center justify-center transition-all"
            >
              <Send size={14} className="text-white" />
            </button>
          </div>
          <p className="text-center text-[10px] text-gray-600 mt-2">
            Pipeline: Planner → Researcher (RAG + Web) → Reasoner → Critic &middot; Powered by Gemini
          </p>
        </form>
      </footer>
    </div>
  );
}
