import React from 'react';
import { Shield, CheckCircle } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-navy-950 text-slate-400 border-t border-navy-900 py-10 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white">KnowBridge</span>
              <span className="text-[10px] bg-brand-500/20 text-brand-300 border border-brand-500/30 px-2 py-0.5 rounded">
                Enterprise Edition
              </span>
            </div>
            <p className="text-sm text-slate-400 max-w-md">
              "Knowledge Should Never Leave With People." Reconstructs verified project continuity from authorized source files with verifiable evidence grounding.
            </p>
            <div className="flex items-center space-x-4 text-xs text-slate-500 pt-1">
              <span className="flex items-center space-x-1">
                <Shield className="w-3.5 h-3.5 text-brand-400" />
                <span>Zero Hallucination Tolerance</span>
              </span>
              <span className="flex items-center space-x-1">
                <CheckCircle className="w-3.5 h-3.5 text-brand-400" />
                <span>Evidence-Anchored Claims</span>
              </span>
            </div>
          </div>

          <div>
            <h4 className="text-xs uppercase font-semibold text-slate-300 tracking-wider mb-3">Platform Capabilities</h4>
            <ul className="space-y-2 text-xs">
              <li className="hover:text-slate-200">1. Cross-Document Contradiction Engine</li>
              <li className="hover:text-slate-200">2. Role-Based Onboarding & Redaction</li>
              <li className="hover:text-slate-200">3. Complete Audit & Governance Trail</li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs uppercase font-semibold text-slate-300 tracking-wider mb-3">Enterprise Security</h4>
            <p className="text-xs leading-relaxed text-slate-400">
              Backend-enforced permission controls ensure confidential drafts and unredacted discussions never leak to incoming personnel without Project Lead sign-off.
            </p>
          </div>

        </div>

        <div className="border-t border-navy-900 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
          <p>© 2026 KnowBridge Technologies Inc. All rights reserved.</p>
          <p className="mt-2 sm:mt-0">Enterprise Project Knowledge Continuity System</p>
        </div>
      </div>
    </footer>
  );
};
