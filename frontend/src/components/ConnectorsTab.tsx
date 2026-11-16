import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ExternalConnector, ExternalRecord } from '../types';
import { 
  GitBranch, 
  GitPullRequest, 
  GitCommit, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle, 
  ExternalLink, 
  Layers, 
  ShieldCheck, 
  Plus, 
  Calendar, 
  User, 
  Clock,
  Check
} from 'lucide-react';

interface ConnectorsTabProps {
  projectId: number;
}

export const ConnectorsTab: React.FC<ConnectorsTabProps> = ({ projectId }) => {
  const [connectors, setConnectors] = useState<ExternalConnector[]>([]);
  const [selectedConnectorId, setSelectedConnectorId] = useState<number | null>(null);
  const [records, setRecords] = useState<ExternalRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState<number | null>(null);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form state
  const [connectorType, setConnectorType] = useState<'GITHUB' | 'JIRA' | 'LINEAR'>('GITHUB');
  const [identifier, setIdentifier] = useState('Amanprajapati247/KnowBridge');
  const [branch, setBranch] = useState('main');
  const [token, setToken] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const conns = await api.listConnectors(projectId);
      setConnectors(conns);
      if (conns.length > 0) {
        const activeId = selectedConnectorId || conns[0].id;
        setSelectedConnectorId(activeId);
        const recs = await api.listConnectorRecords(projectId, activeId);
        setRecords(recs);
      } else {
        setRecords([]);
      }
    } catch (err) {
      console.error('Failed to load connectors:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  const handleSelectConnector = async (connId: number) => {
    setSelectedConnectorId(connId);
    try {
      const recs = await api.listConnectorRecords(projectId, connId);
      setRecords(recs);
    } catch (err) {
      console.error('Failed to load records for connector:', err);
    }
  };

  const handleSync = async (connId: number) => {
    setIsSyncing(connId);
    setSyncMessage(null);
    try {
      const res = await api.syncConnector(projectId, connId);
      setSyncMessage(res.sync_summary || `Synced ${res.synced_records} records, extracted ${res.new_claims_extracted} claims.`);
      await loadData();
    } catch (err: any) {
      setSyncMessage(`Sync failed: ${err.message || 'Unknown error'}`);
    } finally {
      setIsSyncing(null);
    }
  };

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (connectorType === 'GITHUB') {
        await api.connectGitHub(projectId, identifier, branch, token || undefined);
      } else {
        await api.connectTaskBoard(projectId, connectorType, identifier);
      }
      setShowAddModal(false);
      setToken('');
      await loadData();
    } catch (err: any) {
      alert(`Connection failed: ${err.message || 'Check credentials'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getRecordIcon = (type: string) => {
    switch (type) {
      case 'COMMIT': return <GitCommit className="w-3.5 h-3.5 text-slate-500" />;
      case 'PULL_REQUEST': return <GitPullRequest className="w-3.5 h-3.5 text-purple-600" />;
      case 'ISSUE': return <AlertCircle className="w-3.5 h-3.5 text-amber-500" />;
      default: return <Layers className="w-3.5 h-3.5 text-teal-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">Live Git & Task Connectors</h2>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200">
              Round 3 Feature
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 max-w-2xl">
            Automatically ingest commits, pull requests, issues, and architectural decisions from GitHub, Jira, and Linear.
            Syncs incrementally to prevent duplicates and anchors records with verifiable URLs.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl shadow-xs transition shrink-0"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Connect Tool</span>
        </button>
      </div>

      {syncMessage && (
        <div className="p-3 bg-teal-50 border border-teal-200 rounded-xl text-xs text-teal-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0" />
            <span>{syncMessage}</span>
          </div>
          <button onClick={() => setSyncMessage(null)} className="text-teal-600 hover:text-teal-900 font-bold text-xs">
            Dismiss
          </button>
        </div>
      )}

      {/* Connectors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {connectors.map((conn) => (
          <div 
            key={conn.id} 
            onClick={() => handleSelectConnector(conn.id)}
            className={`p-5 rounded-2xl border shadow-xs flex flex-col justify-between space-y-4 cursor-pointer transition ${
              selectedConnectorId === conn.id ? 'bg-white border-teal-500 ring-2 ring-teal-500/20' : 'bg-white border-slate-200 hover:border-slate-300'
            }`}
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider ${
                  conn.provider === 'GITHUB' ? 'bg-purple-50 text-purple-700 border border-purple-200' :
                  conn.provider === 'JIRA' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                  'bg-emerald-50 text-emerald-700 border border-emerald-200'
                }`}>
                  {conn.provider}
                </span>
                <span className="flex items-center space-x-1 text-[11px] font-medium text-emerald-600">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span>{conn.status}</span>
                </span>
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900 truncate" title={conn.name}>
                  {conn.name}
                </h3>
                {conn.branch && (
                  <div className="flex items-center space-x-1 text-[11px] text-slate-500 mt-0.5">
                    <GitBranch className="w-3 h-3 text-slate-400" />
                    <span>branch: {conn.branch}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <div className="text-slate-500">
                <span className="font-bold text-slate-900">{conn.records_count}</span> records
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  handleSync(conn.id);
                }}
                disabled={isSyncing === conn.id}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition"
              >
                <RefreshCw className={`w-3 h-3 ${isSyncing === conn.id ? 'animate-spin' : ''}`} />
                <span>{isSyncing === conn.id ? 'Syncing...' : 'Sync Now'}</span>
              </button>
            </div>
          </div>
        ))}

        {connectors.length === 0 && !isLoading && (
          <div className="col-span-3 p-8 bg-slate-50 rounded-2xl border border-dashed border-slate-300 text-center space-y-2">
            <GitBranch className="w-8 h-8 text-slate-400 mx-auto" />
            <h4 className="font-bold text-sm text-slate-700">No external connectors configured</h4>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              Connect a GitHub repository or Jira workspace to automatically import development activities and architectural decisions into this project.
            </p>
          </div>
        )}
      </div>

      {/* Imported Records Stream */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-sm text-slate-900">Imported Development Context ({records.length})</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Extracted operational changes, pull request discussions, and architectural decisions.
            </p>
          </div>
        </div>

        <div className="divide-y divide-slate-100 max-h-96 overflow-y-auto">
          {records.map((rec) => (
            <div key={rec.id} className="p-4 hover:bg-slate-50/70 transition space-y-1.5">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center space-x-2">
                  {getRecordIcon(rec.record_type)}
                  <span className="text-[10px] font-bold px-2 py-0.5 bg-slate-100 text-slate-600 rounded-md">
                    {rec.record_type}
                  </span>
                  <span className="font-semibold text-xs text-slate-900">{rec.title}</span>
                </div>
                {rec.external_url && (
                  <a
                    href={rec.external_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1 text-[11px] text-teal-600 hover:text-teal-800 shrink-0 font-medium"
                  >
                    <span>View Record</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>

              {rec.description && (
                <p className="text-xs text-slate-600 line-clamp-2 pl-5 font-normal">
                  {rec.description}
                </p>
              )}

              <div className="flex items-center space-x-4 pl-5 text-[10px] text-slate-400">
                {rec.author && (
                  <span className="flex items-center space-x-1">
                    <User className="w-3 h-3" />
                    <span>{rec.author}</span>
                  </span>
                )}
                {rec.created_at_external && (
                  <span className="flex items-center space-x-1">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(rec.created_at_external).toLocaleString()}</span>
                  </span>
                )}
                {rec.external_id && (
                  <span className="font-mono text-slate-400">id: {rec.external_id}</span>
                )}
              </div>
            </div>
          ))}

          {records.length === 0 && !isLoading && (
            <div className="p-8 text-center text-xs text-slate-400">
              No development records imported yet. Click "Sync Now" on a connector above.
            </div>
          )}
        </div>
      </div>

      {/* Connect Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white max-w-md w-full rounded-2xl shadow-xl border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-sm text-slate-900">Connect External Tool</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-slate-600 text-xs font-bold">
                ✕
              </button>
            </div>

            <form onSubmit={handleConnect} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Tool Type</label>
                <div className="grid grid-cols-3 gap-2">
                  {(['GITHUB', 'JIRA', 'LINEAR'] as const).map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => {
                        setConnectorType(t);
                        if (t === 'GITHUB') setIdentifier('Amanprajapati247/KnowBridge');
                        else if (t === 'JIRA') setIdentifier('CEMS-BOARD');
                        else setIdentifier('WORKSPACE-ENG');
                      }}
                      className={`py-2 text-xs font-semibold rounded-xl border transition ${
                        connectorType === t
                          ? 'border-slate-900 bg-slate-900 text-white'
                          : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  {connectorType === 'GITHUB' ? 'Repository (owner/repo)' : 'Project Key / Board Identifier'}
                </label>
                <input
                  type="text"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  required
                  placeholder={connectorType === 'GITHUB' ? 'owner/repository' : 'PROJ-KEY'}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-teal-500 focus:outline-none"
                />
              </div>

              {connectorType === 'GITHUB' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Target Branch</label>
                  <input
                    type="text"
                    value={branch}
                    onChange={(e) => setBranch(e.target.value)}
                    placeholder="main"
                    className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-teal-500 focus:outline-none"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Personal Access Token <span className="text-slate-400 font-normal">(Optional for public repos)</span>
                </label>
                <input
                  type="password"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="ghp_... or API key (Stored securely, never logged)"
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-teal-500 focus:outline-none font-mono"
                />
                <p className="text-[10px] text-slate-400 mt-1">
                  Tokens are encrypted in the database and never returned over public API responses.
                </p>
              </div>

              <div className="pt-3 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3.5 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl transition shadow-xs"
                >
                  {isSubmitting ? 'Connecting...' : 'Establish Connector'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
