import React, { useState } from 'react';
import { X, AlertCircle, ArrowRight, CheckCircle2, FileQuestion } from 'lucide-react';
import { ExtractedClaim } from '../types';

interface ConflictModalProps {
  claim: ExtractedClaim | null;
  onClose: () => void;
  onResolved: (claimId: number, data: { resolution_notes: string; chosen_date?: string; chosen_owner?: string }) => Promise<void>;
}

export const ConflictModal: React.FC<ConflictModalProps> = ({ claim, onClose, onResolved }) => {
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [chosenDate, setChosenDate] = useState('');
  const [chosenOwner, setChosenOwner] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!claim) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resolutionNotes.trim()) {
      setError('Please provide resolution notes explaining which source is authoritative.');
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await onResolved(claim.id, {
        resolution_notes: resolutionNotes,
        chosen_date: chosenDate.trim() || undefined,
        chosen_owner: chosenOwner.trim() || undefined
      });
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to submit conflict resolution.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full border border-rose-200 overflow-hidden transform transition-all animate-in fade-in duration-150">
        
        {/* Header */}
        <div className="bg-rose-900 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-rose-800 text-rose-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-rose-300" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-white">Cross-Document Contradiction Detected</h3>
              <p className="text-xs text-rose-200">Human-in-the-loop conflict resolution required</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-rose-300 hover:text-white p-1 rounded-lg hover:bg-rose-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          
          {/* Explanation Alert */}
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-sm text-rose-900">
            <h4 className="font-bold mb-1 flex items-center space-x-1.5">
              <span>Discrepancy in Statement:</span>
              <span className="text-slate-900">"{claim.title}"</span>
            </h4>
            <p className="text-rose-800 mt-1 leading-relaxed">
              {claim.conflict_details || 'Two separate documents specify contradictory target dates or assignees. KnowBridge never silently guesses which record is correct.'}
            </p>
          </div>

          {/* Conflict Comparison Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase tracking-wider">
                <span>Source Record A</span>
                <span className="bg-slate-200 px-2 py-0.5 rounded text-slate-700">Requirements Spec</span>
              </div>
              <p className="text-sm font-semibold text-slate-900">Beta Launch: November 15, 2026</p>
              <p className="text-xs text-slate-600">Specified in original Milestone schedule (Project_Requirements.pdf, Page 1)</p>
              <button
                type="button"
                onClick={() => setChosenDate('November 15, 2026')}
                className="w-full mt-2 text-xs bg-white border border-slate-300 hover:border-brand-500 text-slate-700 hover:text-brand-700 font-medium py-1.5 rounded-lg transition"
              >
                Select Nov 15 as Authoritative
              </button>
            </div>

            <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/50 space-y-2">
              <div className="flex items-center justify-between text-xs text-amber-700 font-semibold uppercase tracking-wider">
                <span>Source Record B</span>
                <span className="bg-amber-100 px-2 py-0.5 rounded text-amber-800">Meeting Notes</span>
              </div>
              <p className="text-sm font-semibold text-slate-900">Beta Launch: November 25, 2026</p>
              <p className="text-xs text-slate-600">Postponed in Sprint Review to accommodate student exams (Meeting_Notes.docx)</p>
              <button
                type="button"
                onClick={() => setChosenDate('November 25, 2026')}
                className="w-full mt-2 text-xs bg-white border border-amber-300 hover:border-brand-500 text-slate-700 hover:text-brand-700 font-medium py-1.5 rounded-lg transition"
              >
                Select Nov 25 as Authoritative
              </button>
            </div>

          </div>

          {/* Form Inputs for Lead Decision */}
          <div className="space-y-4 border-t border-slate-200 pt-4">
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Authoritative Date / Deadline:
                </label>
                <input
                  type="text"
                  value={chosenDate}
                  onChange={(e) => setChosenDate(e.target.value)}
                  placeholder="e.g. November 25, 2026"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Authoritative Task Owner:
                </label>
                <input
                  type="text"
                  value={chosenOwner}
                  onChange={(e) => setChosenOwner(e.target.value)}
                  placeholder="e.g. Alex Chen (Project Lead)"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Project Lead Resolution Notes <span className="text-rose-500">*</span>:
              </label>
              <textarea
                value={resolutionNotes}
                onChange={(e) => setResolutionNotes(e.target.value)}
                placeholder="Explain the rationale (e.g. Confirmed with team that Meeting Notes reflects the approved schedule change due to exam week)."
                rows={3}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500 focus:outline-none"
              />
            </div>

            {error && (
              <p className="text-xs text-rose-600 bg-rose-50 p-2.5 rounded-lg border border-rose-200">
                {error}
              </p>
            )}

          </div>

          {/* Modal Actions */}
          <div className="flex items-center justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-700 hover:bg-slate-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 bg-brand-600 hover:bg-brand-500 text-white font-medium rounded-lg text-sm shadow-sm transition flex items-center space-x-1.5"
            >
              {isSubmitting ? (
                <span>Resolving...</span>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Confirm Resolution & Update Handover</span>
                </>
              )}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
};
