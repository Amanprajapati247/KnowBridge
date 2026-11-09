import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  ArrowRight, 
  CheckCircle, 
  AlertTriangle, 
  Lock, 
  FileCheck, 
  Clock,
  Sparkles
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-navy-950 via-navy-900 to-slate-900 text-white pt-20 pb-28 px-4 sm:px-6 lg:px-8 border-b border-navy-800 relative overflow-hidden">
        
        {/* Ambient Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-brand-500/10 blur-[120px] pointer-events-none rounded-full" />

        <div className="max-w-5xl mx-auto text-center relative z-10 space-y-6">
          
          <div className="inline-flex items-center space-x-2 bg-navy-800/80 border border-brand-500/30 rounded-full px-4 py-1.5 shadow-inner">
            <span className="w-2 h-2 rounded-full bg-brand-400 animate-pulse" />
            <span className="text-xs font-semibold text-brand-300 tracking-wide uppercase">
              Enterprise Project Continuity & Knowledge Handover
            </span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight text-white">
            Knowledge Should <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 via-teal-300 to-cyan-400">Never Leave</span> With People.
          </h1>

          <p className="text-lg sm:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
            When a key engineer, product lead, or team member departs, critical project decisions, unwritten context, and open blockers disappear with them. <strong>KnowBridge</strong> transforms scattered project documentation into an evidence-grounded, human-approved continuation plan.
          </p>

          {/* Genuine Real-World CTAs */}
          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="w-full sm:w-auto px-7 py-3.5 bg-gradient-to-r from-brand-600 to-teal-600 hover:from-brand-500 hover:to-teal-500 text-white font-semibold rounded-xl shadow-lg shadow-brand-900/40 hover:shadow-brand-700/50 transition flex items-center justify-center space-x-2 text-sm"
            >
              <span>Get Started Free</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </Link>

            <Link
              to="/login"
              className="w-full sm:w-auto px-7 py-3.5 bg-navy-800 hover:bg-navy-700 border border-navy-700 text-slate-200 font-semibold rounded-xl hover:text-white transition flex items-center justify-center space-x-2 text-sm"
            >
              <span>Sign In to Workspace</span>
            </Link>
          </div>

          <div className="pt-2 text-xs text-slate-400 flex items-center justify-center space-x-6">
            <span className="flex items-center space-x-1.5">
              <CheckCircle className="w-4 h-4 text-brand-400" />
              <span>Full Evidence Grounding</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <ShieldCheck className="w-4 h-4 text-brand-400" />
              <span>Backend Access Enforcement</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <FileCheck className="w-4 h-4 text-brand-400" />
              <span>100% Traceable Citations</span>
            </span>
          </div>

        </div>
      </section>

      {/* The Problem in Detail */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <h2 className="text-xs uppercase font-bold text-brand-700 tracking-wider">The Knowledge Loss Crisis</h2>
          <p className="text-3xl font-bold text-slate-900">Why Traditional Handover Fails</p>
          <p className="text-slate-600">
            Departing contributors don't have time to write comprehensive wikis from memory, while generic AI tools hallucinate unverified assumptions.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Scattered Rationale</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Decisions are buried in meeting notes, chat threads, and code comments. New arrivals have no idea why an architectural choice was made.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <Clock className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Contradictory Records</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Requirements documents specify one milestone deadline, but meeting minutes quietly postpone it. Without reconciliation, teams build to the wrong targets.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="w-12 h-12 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Sensitive Information Leaks</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Raw source files frequently contain confidential notes or private discussions that should never be broadcast to incoming personnel without review.
            </p>
          </div>

        </div>
      </section>

      {/* 5-Step Workflow */}
      <section className="bg-white py-20 px-4 sm:px-6 lg:px-8 border-y border-slate-200">
        <div className="max-w-7xl mx-auto">
          
          <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
            <h2 className="text-xs uppercase font-bold text-brand-700 tracking-wider">How KnowBridge Works</h2>
            <p className="text-3xl font-bold text-slate-900">The 5-Step Knowledge Transfer Engine</p>
            <p className="text-slate-600">
              A balanced methodology combining automated NLP extraction with rigorous human verification and role-based delivery.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            
            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 flex flex-col justify-between">
              <div>
                <span className="text-2xl font-black text-brand-600 mb-3 block">01</span>
                <h4 className="font-bold text-slate-900 mb-1">Connect</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Upload authorized PDF, DOCX, and TXT files. System chunks passages preserving page numbers and sections.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-200 text-[11px] text-slate-500 font-medium">
                Step 1: Ingestion
              </div>
            </div>

            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 flex flex-col justify-between">
              <div>
                <span className="text-2xl font-black text-teal-600 mb-3 block">02</span>
                <h4 className="font-bold text-slate-900 mb-1">Reconstruct</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Extracts decisions, completed/pending tasks, explicit owners, deadlines, risks, and unresolved questions.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-200 text-[11px] text-slate-500 font-medium">
                Step 2: AI Parsing
              </div>
            </div>

            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 flex flex-col justify-between">
              <div>
                <span className="text-2xl font-black text-cyan-600 mb-3 block">03</span>
                <h4 className="font-bold text-slate-900 mb-1">Verify</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Every claim links to its source passage. Contradictions between documents are flagged side-by-side.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-200 text-[11px] text-slate-500 font-medium">
                Step 3: Evidence Grounding
              </div>
            </div>

            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 flex flex-col justify-between">
              <div>
                <span className="text-2xl font-black text-indigo-600 mb-3 block">04</span>
                <h4 className="font-bold text-slate-900 mb-1">Review</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Project Lead edits statements, redacts sensitive details, resolves conflicts, and signs off on the handover.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-200 text-[11px] text-slate-500 font-medium">
                Step 4: Human Sign-Off
              </div>
            </div>

            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 flex flex-col justify-between">
              <div>
                <span className="text-2xl font-black text-emerald-600 mb-3 block">05</span>
                <h4 className="font-bold text-slate-900 mb-1">Handover</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Incoming member receives a sanitized, role-appropriate continuation plan. Unapproved drafts remain blocked.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-200 text-[11px] text-slate-500 font-medium">
                Step 5: Safe Onboarding
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* Trust & Enterprise Architecture */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="bg-navy-900 text-white rounded-3xl p-8 sm:p-12 border border-navy-800 shadow-xl grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          
          <div className="space-y-4">
            <span className="text-xs uppercase font-bold text-brand-400 tracking-wider">Enterprise Trust Guarantee</span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Built for High-Stakes Continuity</h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              KnowBridge never invents missing information. If an owner is absent from the records, the system explicitly marks it as "Not found in available sources" instead of generating assumptions.
            </p>

            <ul className="space-y-3 pt-2 text-sm text-slate-200">
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-brand-400 shrink-0" />
                <span>Deterministic conflict detection surfaces discrepancies rather than picking one.</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-brand-400 shrink-0" />
                <span>Incoming personnel cannot bypass backend authorization to view raw documents.</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-brand-400 shrink-0" />
                <span>Auditable activity trail preserves every edit, resolution, and approval timestamp.</span>
              </li>
            </ul>
          </div>

          <div className="bg-navy-950 p-8 rounded-2xl border border-navy-800 space-y-5 text-center">
            <h4 className="text-base font-bold text-white">Ready to Secure Your Team's Knowledge?</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Eliminate transition downtime, preserve critical architecture rationale, and onboard incoming contributors with verified evidence.
            </p>
            <div className="pt-2">
              <Link
                to="/register"
                className="inline-flex items-center justify-center space-x-2 w-full py-3 bg-brand-600 hover:bg-brand-500 text-white rounded-xl text-xs font-semibold shadow-md transition"
              >
                <span>Create Your Organization Workspace</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

        </div>
      </section>

    </div>
  );
};
