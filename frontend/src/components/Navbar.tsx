import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Layers, 
  LogOut, 
  User as UserIcon, 
  CheckCircle2,
  Briefcase
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, role, logout } = useAuth();

  return (
    <header className="bg-navy-900 border-b border-navy-800 text-white sticky top-0 z-40 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand / Logo */}
        <Link to="/" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-cyan-500 flex items-center justify-center text-white shadow-md group-hover:scale-105 transition-transform">
            <Layers className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-xl tracking-tight text-white">KnowBridge</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30">
                Enterprise
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Project Knowledge Handover Platform</p>
          </div>
        </Link>

        {/* Navigation & Controls */}
        <div className="flex items-center space-x-4">
          {user ? (
            <>
              {role === 'PROJECT_LEAD' ? (
                <Link
                  to="/dashboard"
                  className="text-sm font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-lg hover:bg-navy-800 transition flex items-center space-x-1.5"
                >
                  <Briefcase className="w-4 h-4 text-brand-400" />
                  <span>Workspaces</span>
                </Link>
              ) : (
                <Link
                  to="/incoming"
                  className="text-sm font-medium text-brand-300 hover:text-white px-3 py-1.5 rounded-lg hover:bg-navy-800 transition flex items-center space-x-1.5"
                >
                  <CheckCircle2 className="w-4 h-4 text-brand-400" />
                  <span>Onboarding Portal</span>
                </Link>
              )}

              {/* User Role Badge */}
              <div className="hidden sm:flex items-center bg-navy-800 border border-navy-700 rounded-lg px-2.5 py-1">
                <span className="text-xs text-slate-300 flex items-center space-x-1.5">
                  <UserIcon className="w-3.5 h-3.5 text-brand-400" />
                  <span className="text-slate-400 font-normal">Account:</span>
                  <strong className={role === 'PROJECT_LEAD' ? 'text-amber-300 font-semibold' : 'text-teal-300 font-semibold'}>
                    {role === 'PROJECT_LEAD' ? 'Project Lead' : 'Incoming Member'}
                  </strong>
                </span>
              </div>

              {/* User Profile & Logout */}
              <div className="flex items-center space-x-3 border-l border-navy-800 pl-4">
                <div className="text-right hidden md:block">
                  <p className="text-xs font-semibold text-white leading-tight">{user.full_name}</p>
                  <p className="text-[10px] text-slate-400 truncate max-w-[140px]">{user.email}</p>
                </div>
                <button
                  onClick={logout}
                  className="p-2 text-slate-400 hover:text-rose-400 hover:bg-navy-800 rounded-lg transition"
                  title="Sign out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </>
          ) : (
            <div className="flex items-center space-x-3">
              <Link
                to="/login"
                className="text-sm font-medium text-slate-300 hover:text-white px-3 py-2 rounded-lg hover:bg-navy-800 transition"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="text-sm font-medium bg-brand-600 hover:bg-brand-500 text-white px-4 py-2 rounded-lg shadow-sm transition"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
