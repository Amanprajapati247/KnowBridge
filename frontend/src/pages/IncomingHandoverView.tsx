import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Handover, HandoverItem, AcknowledgmentReceipt } from '../types';
import { RAGAssistantTab } from '../components/RAGAssistantTab';
import { 
  ArrowLeft, 
  ShieldCheck, 
  CheckCircle2, 
  Clock, 
  Calendar, 
  FileText, 
  AlertTriangle, 
  HelpCircle, 
  ChevronRight,
  User,
  Quote,
  Hash,
  Sparkles,
  FileCheck
} from 'lucide-react';

export const IncomingHandoverView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const handoverId = Number(id);

  const [handover, setHandover] = useState<Handover | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completedItems, setCompletedItems] = useState<Record<number, boolean>>({});

  // Acknowledgment state
  const [receipt, setReceipt] = useState<AcknowledgmentReceipt | null>(null);
  const [ackConfirmed, setAckConfirmed] = useState(false);
  const [ackNotes, setAckNotes] = useState('');
  const [isAcknowledging, setIsAcknowledging] = useState(false);
  const [ackError, setAckError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchHandover() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await api.getApprovedHandover(handoverId);
        setHandover(data);
        
        // Check if already acknowledged
        try {
          const rec = await api.getAcknowledgmentReceipt(handoverId);
          setReceipt(rec);
        } catch {
          // Not acknowledged yet, which is expected
        }
      } catch (err: any) {
        setError(err.message || 'Access Denied: This handover is not approved for incoming member viewing.');
      } finally {
        setIsLoading(false);
      }
    }
    if (handoverId) {
      fetchHandover();
    }
  }, [handoverId]);

  const toggleCheck = (itemId: number) => {
    setCompletedItems(prev => ({
      ...prev,
      [itemId]: !prev[itemId]
    }));
  };

  const handleAcknowledge = async () => {
    if (!handover || !ackConfirmed) return;
    setIsAcknowledging(true);
    setAckError(null);
    try {
      await api.acknowledgeHandover(
        handoverId, 
        ackNotes || 'Handover reviewed, accepted, and acknowledged by incoming team member.'
      );
      const rec = await api.getAcknowledgmentReceipt(handoverId);
      setReceipt(rec);
    } catch (err: any) {
      setAckError(err.message || 'Failed to submit handover acknowledgment.');
    } finally {
      setIsAcknowledging(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-xs text-slate-500">
        Loading approved handover...
      </div>
    );
  }

  if (error || !handover) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center space-y-4">
        <div className="w-12 h-12 bg-rose-50 text-rose-600 rounded-2xl flex items-center justify-center mx-auto">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-slate-900">Access Restricted</h2>
        <p className="text-xs text-rose-600 bg-rose-50 p-4 rounded-xl border border-rose-200 leading-relaxed">
          {error || 'Unable to display this handover.'}
        </p>
        <Link
          to="/incoming"
          className="inline-block px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold"
        >
          Return to Incoming Portal
        </Link>
      </div>
    );
  }

  // Group items by section
  const decisions = handover.items.filter(i => i.section === 'DECISIONS');
  const pendingTasks = handover.items.filter(i => i.section === 'PENDING_TASKS');
  const completedTasks = handover.items.filter(i => i.section === 'COMPLETED_TASKS');
  const responsibilities = handover.items.filter(i => i.section === 'RESPONSIBILITIES');
  const risks = handover.items.filter(i => i.section === 'RISKS_BLOCKERS');
  const dependencies = handover.items.filter(i => i.section === 'DEPENDENCIES');
  const questions = handover.items.filter(i => i.section === 'UNRESOLVED_QUESTIONS');

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Back Link */}
      <Link to="/incoming" className="inline-flex items-center space-x-1.5 text-xs text-slate-500 hover:text-slate-800 transition">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Approved Handovers</span>
      </Link>

      {/* Header Document Banner */}
      <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-4">
          <div className="flex items-center space-x-2">
            <span className="text-xs uppercase font-bold px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Approved & Verified Handover</span>
            </span>
            <span className="text-xs text-slate-400 font-mono">v{handover.version}</span>
          </div>
          <div className="text-xs text-slate-400 flex items-center space-x-1">
            <Calendar className="w-3.5 h-3.5" />
            <span>Approved: {handover.approved_at ? new Date(handover.approved_at).toLocaleDateString() : 'Recent'}</span>
          </div>
        </div>

        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">{handover.title}</h1>
          <p className="text-xs text-slate-500 mt-1">
            Authorized sign-off note: <em>"{handover.approval_notes || 'Approved for team continuation'}"</em>
          </p>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
        <h3 className="text-xs uppercase font-bold text-brand-700 tracking-wider">1. Executive Summary</h3>
        <p className="text-sm text-slate-800 leading-relaxed font-normal">{handover.executive_summary}</p>
      </div>

      {/* Current Project State */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
        <h3 className="text-xs uppercase font-bold text-brand-700 tracking-wider">2. Current Project State</h3>
        <p className="text-sm text-slate-800 leading-relaxed">{handover.current_status}</p>
      </div>

      {/* Key Architectural & Operational Decisions */}
      {decisions.length > 0 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-xs uppercase font-bold text-slate-900 tracking-wider">3. Key Architectural Decisions & Rationale</h3>
          <div className="space-y-3">
            {decisions.map((d) => (
              <div key={d.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                <h4 className="text-xs font-bold text-slate-900">{d.title}</h4>
                <p className="text-xs text-slate-700 leading-relaxed">{d.content}</p>
                {d.evidence_excerpt && (
                  <p className="text-[11px] text-slate-500 italic mt-1 pt-1 border-t border-slate-200">
                    Source Evidence: "{d.evidence_excerpt}" ({d.source_filename || 'Doc'}, p. {d.source_page || 1})
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pending Deliverables Checklist for Incoming Member */}
      {pendingTasks.length > 0 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs uppercase font-bold text-slate-900 tracking-wider">
              4. Open Deliverables & Tasks ({pendingTasks.length})
            </h3>
            <span className="text-[11px] text-slate-500">Click checkbox as you complete onboarding tasks</span>
          </div>

          <div className="space-y-2">
            {pendingTasks.map((t) => (
              <div
                key={t.id}
                onClick={() => toggleCheck(t.id)}
                className={`p-3.5 rounded-xl border cursor-pointer transition flex items-start space-x-3 ${
                  completedItems[t.id]
                    ? 'bg-emerald-50/50 border-emerald-200 text-slate-400 line-through'
                    : 'bg-white border-slate-200 hover:border-brand-500 text-slate-800'
                }`}
              >
                <input
                  type="checkbox"
                  checked={!!completedItems[t.id]}
                  onChange={() => {}}
                  className="mt-0.5 rounded text-brand-600 focus:ring-brand-500"
                />
                <div className="flex-1 text-xs">
                  <p className="font-semibold text-slate-900">{t.title}</p>
                  <p className="text-slate-600 mt-0.5">{t.content}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Team Ownership & Responsibilities */}
      {responsibilities.length > 0 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <h3 className="text-xs uppercase font-bold text-slate-900 tracking-wider">5. Team Responsibilities & Ownership</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {responsibilities.map((r) => (
              <div key={r.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                <span className="font-bold text-slate-800 block">{r.title}</span>
                <span className="text-slate-600 mt-0.5 block">{r.content}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Risks, Blockers & Unresolved Questions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        
        {risks.length > 0 && (
          <div className="bg-white p-6 rounded-2xl border border-amber-200 shadow-sm space-y-3 bg-amber-50/20">
            <h3 className="text-xs uppercase font-bold text-amber-800 tracking-wider flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span>Known Risks & Blockers</span>
            </h3>
            <div className="space-y-2">
              {risks.map((r) => (
                <div key={r.id} className="p-3 bg-white rounded-xl border border-amber-200 text-xs">
                  <p className="font-bold text-slate-900">{r.title}</p>
                  <p className="text-slate-600 mt-0.5">{r.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {questions.length > 0 && (
          <div className="bg-white p-6 rounded-2xl border border-cyan-200 shadow-sm space-y-3 bg-cyan-50/20">
            <h3 className="text-xs uppercase font-bold text-cyan-800 tracking-wider flex items-center space-x-1.5">
              <HelpCircle className="w-4 h-4 text-cyan-600" />
              <span>Unresolved Questions</span>
            </h3>
            <div className="space-y-2">
              {questions.map((q) => (
                <div key={q.id} className="p-3 bg-white rounded-xl border border-cyan-200 text-xs">
                  <p className="font-bold text-slate-900">{q.title}</p>
                  <p className="text-slate-600 mt-0.5">{q.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>

      {/* Recommended Next Actions */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
        <h3 className="text-xs uppercase font-bold text-slate-900 tracking-wider">6. Recommended Next Actions</h3>
        <pre className="text-xs text-slate-800 whitespace-pre-wrap font-sans leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
          {handover.recommended_actions}
        </pre>
      </div>

      {/* Semantic Hybrid RAG for Incoming Member */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-teal-600" />
          <h3 className="text-sm font-bold text-slate-900">Ask Questions Over Approved Handover</h3>
        </div>
        <p className="text-xs text-slate-500">
          Incoming members can query this approved handover in natural language. Answers are strictly grounded in verified passages.
        </p>
        <RAGAssistantTab projectId={handover.project_id} />
      </div>

      {/* Cryptographic Handover Acknowledgment Card */}
      <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-teal-50 text-teal-700 rounded-2xl">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Cryptographic Handover Acknowledgment</h3>
              <p className="text-xs text-slate-500">
                Formal sign-off and receipt generation anchored to immutable snapshot hash (SHA-256).
              </p>
            </div>
          </div>
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 uppercase font-mono">
            v{handover.version}
          </span>
        </div>

        {receipt ? (
          /* Acknowledged State: Verified Receipt Display */
          <div className="p-6 bg-teal-50/50 rounded-2xl border border-teal-200 space-y-4">
            <div className="flex items-center justify-between">
              <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-teal-600 text-white shadow-xs">
                <CheckCircle2 className="w-4 h-4" />
                <span>HANDOVER CRYPTOGRAPHICALLY ACKNOWLEDGED</span>
              </span>
              <span className="text-[11px] text-teal-800 font-semibold">
                Status: {receipt.is_valid ? 'VERIFIED INTEGRITY' : 'PENDING'}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-2">
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Verifiable Receipt Token</span>
                <span className="font-mono text-xs font-bold text-slate-900 bg-white px-2.5 py-1.5 rounded-lg border border-teal-200 block truncate" title={receipt.receipt_token}>
                  {receipt.receipt_token}
                </span>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Snapshot SHA-256 Hash</span>
                <span className="font-mono text-xs text-slate-600 bg-white px-2.5 py-1.5 rounded-lg border border-teal-200 block truncate" title={receipt.snapshot_hash}>
                  {receipt.snapshot_hash}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-teal-100">
              <span>Signed by: <b>{receipt.user_email}</b></span>
              <span>Timestamp: <b>{new Date(receipt.acknowledged_at).toLocaleString()}</b></span>
            </div>

            {receipt.signature_notes && (
              <p className="text-xs text-slate-700 bg-white p-3 rounded-xl border border-teal-100 italic">
                "{receipt.signature_notes}"
              </p>
            )}

            <div className="text-[10px] text-slate-400 italic">
              Verification Notice: The SHA-256 hash mathematically proves that the handover content reviewed at sign-off exactly matches the approved project snapshot.
            </div>
          </div>
        ) : (
          /* Unacknowledged State: Form */
          <div className="space-y-4">
            {ackError && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700">
                {ackError}
              </div>
            )}

            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-700">
                Handover Acceptance Notes <span className="text-slate-400 font-normal">(Optional)</span>
              </label>
              <textarea
                value={ackNotes}
                onChange={(e) => setAckNotes(e.target.value)}
                placeholder="e.g. Reviewed architecture, set up local environment, scheduled sprint kickoff with lead..."
                rows={2}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-teal-500 focus:outline-none"
              />
            </div>

            <label className="flex items-start space-x-3 cursor-pointer p-3 bg-slate-50 rounded-xl border border-slate-200 hover:bg-slate-100/60 transition">
              <input
                type="checkbox"
                checked={ackConfirmed}
                onChange={(e) => setAckConfirmed(e.target.checked)}
                className="mt-0.5 rounded text-teal-600 focus:ring-teal-500"
              />
              <span className="text-xs text-slate-700 leading-relaxed">
                I confirm that I have reviewed the approved handover report, understand the system decisions, open deliverables, and active risks, and accept ownership of incoming engineering tasks.
              </span>
            </label>

            <button
              onClick={handleAcknowledge}
              disabled={isAcknowledging || !ackConfirmed}
              className="w-full py-3 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white font-bold rounded-xl text-xs shadow-sm transition flex items-center justify-center space-x-2"
            >
              <FileCheck className="w-4 h-4 text-teal-400" />
              <span>{isAcknowledging ? 'Recording Cryptographic Acknowledgment...' : 'Sign & Acknowledge Handover'}</span>
            </button>
          </div>
        )}
      </div>

    </div>
  );
};
