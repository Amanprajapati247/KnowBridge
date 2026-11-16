import React, { useState } from 'react';
import { api } from '../services/api';
import { RAGQueryResponse } from '../types';
import { 
  Search, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  AlertCircle, 
  BookOpen, 
  FileText, 
  Layers, 
  ShieldCheck, 
  ExternalLink,
  ChevronRight,
  Database
} from 'lucide-react';

interface RAGAssistantTabProps {
  projectId: number;
}

export const RAGAssistantTab: React.FC<RAGAssistantTabProps> = ({ projectId }) => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<RAGQueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sampleQuestions = [
    'What are the pending tasks?',
    'Why was the launch date changed?',
    'Who is responsible for the database migration?',
    'What are the unresolved blockers?',
    'Which architectural decisions were made?'
  ];

  const handleAsk = async (questionToAsk?: string) => {
    const q = questionToAsk || query;
    if (!q.trim()) return;
    
    setIsLoading(true);
    setError(null);
    if (questionToAsk) setQuery(questionToAsk);

    try {
      const res = await api.queryRAG(q, projectId);
      setResponse(res);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve answers from RAG engine.');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'VERIFIED':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>VERIFIED BY PASSAGES</span>
          </span>
        );
      case 'CONFLICT':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>DISCREPANCY DETECTED</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>UNCERTAIN EVIDENCE</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-slate-900">Semantic Hybrid RAG Assistant</h2>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200">
                Round 3 Feature
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1 max-w-2xl">
              Grounded Question & Answering powered by dense vector embeddings and Okapi BM25 keyword search.
              All responses are anchored directly to verified passages with page numbers and source excerpts.
            </p>
          </div>
          <div className="flex items-center space-x-2 text-[11px] text-slate-500 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200 shrink-0">
            <Database className="w-3.5 h-3.5 text-teal-600" />
            <span>Hybrid Reciprocal Rank Fusion (RRF)</span>
          </div>
        </div>

        {/* Quick Question Chips */}
        <div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
            Suggested Verification Questions:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {sampleQuestions.map((sq, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleAsk(sq)}
                className="text-[11px] px-3 py-1 bg-slate-50 hover:bg-teal-50/70 border border-slate-200 hover:border-teal-300 rounded-full text-slate-700 transition"
              >
                {sq}
              </button>
            ))}
          </div>
        </div>

        {/* Search Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk();
          }}
          className="relative pt-2"
        >
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-5 pointer-events-none" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything about decisions, tasks, deadlines, owners, or blockers in this project..."
            className="w-full pl-9 pr-24 py-2.5 bg-slate-50/60 border border-slate-200 rounded-xl text-xs sm:text-sm focus:ring-2 focus:ring-teal-500 focus:bg-white focus:outline-none"
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="absolute right-1.5 top-3.5 px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white text-xs font-semibold rounded-lg transition flex items-center space-x-1.5 shadow-xs"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isLoading ? 'Searching...' : 'Ask RAG'}</span>
          </button>
        </form>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-xs text-rose-700">
          {error}
        </div>
      )}

      {/* Answer View */}
      {response && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
            <div className="space-y-1">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Natural Language Query</span>
              <h3 className="font-bold text-sm text-slate-900">{response.question}</h3>
            </div>
            <div>{getStatusBadge(response.evidence_status)}</div>
          </div>

          {/* Direct Answer */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Grounded Response</h4>
            <div className="p-4 bg-slate-50/80 rounded-xl border border-slate-200 text-xs sm:text-sm text-slate-800 leading-relaxed font-sans">
              {response.answer}
            </div>
          </div>

          {/* Citations List */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-1.5">
                <BookOpen className="w-3.5 h-3.5 text-teal-600" />
                <span>Supporting Evidence Citations ({response.citations.length})</span>
              </h4>
              <span className="text-[10px] text-slate-400">Method: {response.retrieval_mode}</span>
            </div>

            <div className="grid grid-cols-1 gap-3">
              {response.citations.map((c, idx) => (
                <div key={idx} className="p-4 bg-white rounded-xl border border-slate-200 hover:border-teal-300 transition space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-2">
                      <FileText className="w-3.5 h-3.5 text-slate-500" />
                      <span className="font-bold text-slate-800">{c.filename}</span>
                      {c.page_number && (
                        <span className="text-[10px] px-2 py-0.5 bg-slate-100 text-slate-600 rounded-md font-mono">
                          Page {c.page_number}
                        </span>
                      )}
                      <span className="text-[10px] px-2 py-0.5 bg-teal-50 text-teal-700 rounded-md font-semibold">
                        {c.source_type}
                      </span>
                    </div>
                    {c.external_url && (
                      <a
                        href={c.external_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center space-x-1 text-[11px] text-teal-600 hover:text-teal-800 font-medium"
                      >
                        <span>Source</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>

                  <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-100 italic leading-relaxed">
                    "{c.excerpt}"
                  </p>
                </div>
              ))}

              {response.citations.length === 0 && (
                <div className="p-6 bg-amber-50/50 rounded-xl border border-amber-200 text-center text-xs text-amber-800">
                  No verified passages directly answered this query. Grounded AI disclosed absence to prevent hallucinating false facts.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
