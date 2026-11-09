import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Project, DashboardStats } from '../types';
import { 
  FolderPlus, 
  Sparkles, 
  ArrowRight, 
  BarChart3,
  Search,
  Plus,
  AlertCircle
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

export const MainDashboard: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSeeding, setIsSeeding] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Modal State
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [createLoading, setCreateLoading] = useState(false);

  const navigate = useNavigate();

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [projList, dashStats] = await Promise.all([
        api.listProjects(),
        api.getDashboardStats()
      ]);
      setProjects(projList);
      setStats(dashStats);
    } catch (err) {
      console.error('Error loading dashboard:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleImportStarter = async () => {
    setIsSeeding(true);
    try {
      const demoProj = await api.seedDemoProject();
      await loadData();
      navigate(`/projects/${demoProj.id}`);
    } catch (err: any) {
      alert(`Import error: ${err.message}`);
    } finally {
      setIsSeeding(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setCreateLoading(true);
    try {
      const created = await api.createProject(newTitle.trim(), newDesc.trim() || undefined);
      setIsCreateOpen(false);
      setNewTitle('');
      setNewDesc('');
      await loadData();
      navigate(`/projects/${created.id}`);
    } catch (err: any) {
      alert(`Error creating project: ${err.message}`);
    } finally {
      setCreateLoading(false);
    }
  };

  const filteredProjects = projects.filter(p =>
    p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Analytics data for Recharts
  const chartData = [
    { name: 'Workspaces', count: stats?.total_projects || 0, fill: '#0f766e' },
    { name: 'Documents', count: stats?.total_documents || 0, fill: '#14b8a6' },
    { name: 'Open Tasks', count: stats?.open_tasks || 0, fill: '#0284c7' },
    { name: 'Identified Risks', count: stats?.identified_risks || 0, fill: '#f59e0b' },
    { name: 'Conflicts', count: stats?.conflicts_count || 0, fill: '#ef4444' }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Banner / Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold text-slate-900">Project Knowledge Hub</h1>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-200 text-slate-700">
              Project Lead Workspace
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Manage projects, upload source materials, resolve cross-document contradictions, and publish verified handovers.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center space-x-3">
          <button
            onClick={handleImportStarter}
            disabled={isSeeding}
            className="px-4 py-2.5 bg-gradient-to-r from-brand-600 to-teal-600 hover:from-brand-500 hover:to-teal-500 text-white font-semibold rounded-xl text-xs shadow-md transition flex items-center space-x-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>{isSeeding ? 'Importing Project...' : 'Import Starter Project'}</span>
          </button>

          <button
            onClick={() => setIsCreateOpen(true)}
            className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl text-xs shadow-sm transition flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>New Project</span>
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
          <span className="text-xs text-slate-500 font-medium">Total Projects</span>
          <p className="text-2xl font-bold text-slate-900">{stats?.total_projects ?? 0}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
          <span className="text-xs text-slate-500 font-medium">Uploaded Docs</span>
          <p className="text-2xl font-bold text-teal-600">{stats?.total_documents ?? 0}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
          <span className="text-xs text-slate-500 font-medium">Handovers</span>
          <p className="text-2xl font-bold text-slate-900">{stats?.generated_handovers ?? 0}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
          <span className="text-xs text-slate-500 font-medium">Open Tasks</span>
          <p className="text-2xl font-bold text-sky-600">{stats?.open_tasks ?? 0}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
          <span className="text-xs text-slate-500 font-medium">Active Risks</span>
          <p className="text-2xl font-bold text-amber-600">{stats?.identified_risks ?? 0}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-rose-200 shadow-sm space-y-1 bg-rose-50/30">
          <span className="text-xs text-rose-700 font-medium flex items-center space-x-1">
            <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>Conflicts</span>
          </span>
          <p className="text-2xl font-bold text-rose-600">{stats?.conflicts_count ?? 0}</p>
        </div>

      </div>

      {/* Analytics Chart Row */}
      {stats && stats.total_projects > 0 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-brand-600" />
              <h3 className="text-sm font-bold text-slate-900">Project Knowledge Distribution</h3>
            </div>
            <span className="text-xs text-slate-500">Live aggregated metrics from uploaded records</span>
          </div>
          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Projects Directory Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        
        {/* Table Filter Bar */}
        <div className="p-4 border-b border-slate-200 flex items-center justify-between gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search projects..."
              className="w-full pl-9 pr-3 py-1.5 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-brand-500 focus:outline-none"
            />
          </div>
          <span className="text-xs text-slate-500">
            Showing <strong>{filteredProjects.length}</strong> of {projects.length} project(s)
          </span>
        </div>

        {/* Table Content */}
        {isLoading ? (
          <div className="p-12 text-center text-slate-400 text-xs">Loading projects...</div>
        ) : filteredProjects.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
              <FolderPlus className="w-6 h-6" />
            </div>
            <h4 className="text-sm font-bold text-slate-700">No Projects Found</h4>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Click <strong>"Import Starter Project"</strong> above to populate a comprehensive reference workspace with multi-document records.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3">Project Title</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Documents</th>
                  <th className="px-6 py-3">Claims Extracted</th>
                  <th className="px-6 py-3">Handover State</th>
                  <th className="px-6 py-3">Last Updated</th>
                  <th className="px-6 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredProjects.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50/70 transition">
                    <td className="px-6 py-4">
                      <Link to={`/projects/${p.id}`} className="font-bold text-slate-900 hover:text-brand-600 block text-sm">
                        {p.title}
                      </Link>
                      <p className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">{p.description || 'No description'}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase bg-slate-100 text-slate-700 border border-slate-200">
                        {p.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-700">
                      {p.document_count} file(s)
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-700">
                      {p.claim_count} claims
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase ${
                        p.handover_status === 'APPROVED'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : p.handover_status === 'DRAFT'
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-slate-100 text-slate-500'
                      }`}>
                        {p.handover_status || 'NOT STARTED'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-500">
                      {new Date(p.updated_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link
                        to={`/projects/${p.id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 bg-slate-100 hover:bg-brand-50 hover:text-brand-700 text-slate-700 rounded-lg font-medium transition"
                      >
                        <span>Workspace</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      </div>

      {/* Create Project Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 border border-slate-200 space-y-4">
            <h3 className="text-base font-bold text-slate-900">Create New Workspace</h3>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Project Title <span className="text-rose-500">*</span></label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Distributed Payment Gateway"
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Description (Optional)</label>
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Briefly describe the project scope and team context..."
                  rows={3}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsCreateOpen(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createLoading}
                  className="px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold transition"
                >
                  {createLoading ? 'Creating...' : 'Create Workspace'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
