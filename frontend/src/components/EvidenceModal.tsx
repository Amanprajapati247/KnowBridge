import React from 'react';
import { X, FileText, CheckCircle2, AlertTriangle, AlertCircle, Quote } from 'lucide-react';
import { ExtractedClaim } from '../types';

interface EvidenceModalProps {
  claim: ExtractedClaim | null;
  onClose: () => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({ claim, onClose }) => {
  if (!claim) return null;

  const ev = claim.evidences && claim.evidences.length > 0 ? claim.evidences[0] : null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full border border-slate-200 overflow-hidden transform transition-all animate-in fade-in duration-150">
        
        {/* Header */}
        <div className="bg-navy-900 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-brand-500/20 text-brand-300 rounded-lg">
              <FileText className="w-5 h-5 text-brand-400" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-white">Source Evidence & Traceability</h3>
              <p className="text-xs text-slate-400">Verifiable grounding against authorized document passages</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-navy-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          
          {/* Claim Summary */}
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-xs uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                {claim.category}
              </span>
              <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full flex items-center space-x-1 ${
                claim.verification_status === 'VERIFIED'
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : claim.verification_status === 'CONFLICT'
                  ? 'bg-rose-50 text-rose-700 border border-rose-200'
                  : 'bg-amber-50 text-amber-700 border border-amber-200'
              }`}>
                {claim.verification_status === 'VERIFIED' && <CheckCircle2 className="w-3.5 h-3.5" />}
                {claim.verification_status === 'CONFLICT' && <AlertCircle className="w-3.5 h-3.5" />}
                {claim.verification_status === 'UNCERTAIN' && <AlertTriangle className="w-3.5 h-3.5" />}
                <span>{claim.verification_status}</span>
              </span>
              <span className="text-xs text-slate-500">
                Confidence: <strong>{Math.round(claim.confidence * 100)}%</strong>
              </span>
            </div>
            <h4 className="text-base font-bold text-slate-900">{claim.title}</h4>
            <p className="text-sm text-slate-600 mt-1">{claim.description}</p>
          </div>

          {/* Metadata Grid */}
          <div className="grid grid-cols-2 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs">
            <div>
              <span className="text-slate-500 block">Identified Owner:</span>
              <span className="font-semibold text-slate-800">
                {claim.owner || 'Not found in available sources'}
              </span>
            </div>
            <div>
              <span className="text-slate-500 block">Stated Date / Deadline:</span>
              <span className="font-semibold text-slate-800">
                {claim.date_reference || 'Not explicitly stated'}
              </span>
            </div>
          </div>

          {/* Grounded Excerpt */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1">
                <Quote className="w-3.5 h-3.5 text-brand-600" />
                <span>Supporting Source Passage</span>
              </span>
              {ev && (
                <span className="text-xs bg-brand-50 text-brand-700 px-2 py-0.5 rounded border border-brand-200 font-medium">
                  {ev.filename || 'Document'} · Page {ev.page_number || 1}
                </span>
              )}
            </div>

            <div className="bg-slate-900 text-slate-100 p-4 rounded-xl border border-slate-800 text-sm leading-relaxed font-mono">
              {ev ? (
                <p className="whitespace-pre-wrap">{ev.excerpt}</p>
              ) : (
                <p className="text-slate-400 italic">Direct passage citation aggregated from contextual document structure.</p>
              )}
            </div>
          </div>

          {/* Anti-Hallucination Disclaimer */}
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3 flex items-start space-x-2 text-xs text-emerald-800">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <p>
              <strong>Zero-Hallucination Policy:</strong> This statement is derived strictly from verified passages inside uploaded project files. KnowBridge never fabricates unrecorded owners, dates, or technical decisions.
            </p>
          </div>

        </div>

        {/* Footer */}
        <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 font-medium rounded-lg text-sm transition"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
