import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { Handover } from '../types';
import { 
  CheckCircle2, 
  ArrowRight, 
  Lock, 
  ShieldCheck, 
  FileCheck, 
  Calendar, 
  User, 
  AlertCircle 
} from 'lucide-react';

export const IncomingPortal: React.FC = () => {
  const [handovers, setHandovers] = useState<Handover[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const approved = await api.listApprovedHandovers();
        setHandovers(approved);
      } catch (err) {
        console.error('Error fetching approved handovers:', err);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="bg-navy-900 text-white p-8 rounded-3xl border border-navy-800 shadow-xl space-y-3">
        <div className="inline-flex items-center space-x-2 bg-brand-500/20 text-brand-300 border border-brand-500/30 px-3 py-1 rounded-full text-xs font-semibold">
          <ShieldCheck className="w-4 h-4 text-brand-400" />
          <span>Incoming Member Onboarding Portal</span>
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight">Approved Project Handovers</h1>
        <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
          Welcome to the team! Below are the finalized, verified handovers authorized by Project Leads. All statements have been vetted, sensitive internal discussions redacted, and contradictions resolved.
        </p>
      </div>

      {/* Permission Boundary Note */}
      <div className="bg-teal-50 border border-teal-200 p-4 rounded-2xl flex items-start space-x-3 text-xs text-teal-900">
        <Lock className="w-4 h-4 text-teal-700 shrink-0 mt-0.5" />
        <div>
          <strong className="font-bold">Role-Based Permission Enforcement:</strong> As an incoming team member, you only have access to <strong>approved handovers</strong>. Unapproved draft reports, private reviewer notes, and unvetted raw source files remain inaccessible at both the API and database levels.
        </div>
      </div>

      {/* Listing */}
      {isLoading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading approved handovers...</div>
      ) : handovers.length === 0 ? (
        <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 text-xs space-y-3">
          <FileCheck className="w-10 h-10 text-slate-400 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">No Approved Handovers Available Yet</h3>
          <p className="text-slate-500 max-w-md mx-auto">
            The Project Lead is currently reviewing and approving continuation reports. Once signed off, verified handovers will immediately appear in this portal.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {handovers.map((h) => (
            <div key={h.id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4 hover:border-brand-500 transition">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase font-bold text-brand-700 bg-brand-50 border border-brand-200 px-2.5 py-0.5 rounded-full">
                  Version {h.version} · Approved
                </span>
                <span className="text-xs text-slate-400 flex items-center space-x-1">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>{h.approved_at ? new Date(h.approved_at).toLocaleDateString() : 'Recent'}</span>
                </span>
              </div>

              <div>
                <h3 className="text-lg font-bold text-slate-900">{h.title}</h3>
                <p className="text-xs text-slate-600 line-clamp-2 mt-1 leading-relaxed">
                  {h.executive_summary}
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs space-y-1">
                <div className="flex items-center justify-between text-slate-600">
                  <span>Sign-off Note:</span>
                  <span className="font-semibold text-slate-800">{h.approval_notes || 'Approved by Project Lead'}</span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span>Verified Deliverables:</span>
                  <span className="font-semibold text-teal-700">{h.items.length} actionable items</span>
                </div>
              </div>

              <div className="pt-2 flex justify-end">
                <Link
                  to={`/incoming/${h.id}`}
                  className="px-4 py-2 bg-slate-900 hover:bg-brand-600 text-white rounded-xl text-xs font-semibold shadow-sm transition flex items-center space-x-1.5"
                >
                  <span>Open Continuation Plan</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
};
