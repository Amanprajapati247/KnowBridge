import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { 
  Project, 
  DocumentItem, 
  ExtractedClaim, 
  Handover, 
  HandoverItem, 
  AuditLog, 
  DocumentPassage 
} from '../types';
import { EvidenceModal } from '../components/EvidenceModal';
import { ConflictModal } from '../components/ConflictModal';
import { 
  ArrowLeft, 
  FileText, 
  UploadCloud, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  AlertCircle, 
  Trash2, 
  ShieldCheck, 
  Eye, 
  Clock, 
  Edit3, 
  Check, 
  X, 
  Lock, 
  HelpCircle, 
  Layers, 
  ListOrdered, 
  Search,
  Activity,
  FileCheck
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

type WorkspaceTab = 'overview' | 'documents' | 'claims' | 'conflicts' | 'handover' | 'activity';

export const ProjectWorkspace: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const projectId = Number(id);

  const [project, setProject] = useState<Project | null>(null);
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('overview');
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [claims, setClaims] = useState<ExtractedClaim[]>([]);
  const [handovers, setHandovers] = useState<Handover[]>([]);
  const [activeHandover, setActiveHandover] = useState<Handover | null>(null);
  const [activityLogs, setActivityLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Upload state
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Passage viewer modal state
  const [viewPassagesDoc, setViewPassagesDoc] = useState<DocumentItem | null>(null);
  const [passagesList, setPassagesList] = useState<DocumentPassage[]>([]);
  const [loadingPassages, setLoadingPassages] = useState(false);

  // Analysis state
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Evidence & Conflict Modals
  const [selectedEvidenceClaim, setSelectedEvidenceClaim] = useState<ExtractedClaim | null>(null);
  const [selectedConflictClaim, setSelectedConflictClaim] = useState<ExtractedClaim | null>(null);

  // Handover editing state
  const [editingItemId, setEditingItemId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [approvalNotes, setApprovalNotes] = useState('');
  const [isApproving, setIsApproving] = useState(false);

  const loadAll = async () => {
    setIsLoading(true);
    try {
      const [proj, docs, clms, hands, logs] = await Promise.all([
        api.getProject(projectId),
        api.listDocuments(projectId),
        api.getClaims(projectId),
        api.listHandovers(projectId),
        api.getProjectActivity(projectId)
      ]);
      setProject(proj);
      setDocuments(docs);
      setClaims(clms);
      setHandovers(hands);
      if (hands.length > 0) {
        // Fetch full active handover details
        const detailedHandover = await api.getHandover(hands[0].id);
        setActiveHandover(detailedHandover);
      } else {
        setActiveHandover(null);
      }
      setActivityLogs(logs);
    } catch (err) {
      console.error('Workspace load error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      loadAll();
    }
  }, [projectId]);

  // Upload handler
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFiles.length === 0) return;
    setIsUploading(true);
    setUploadError(null);
    try {
      await api.uploadDocuments(projectId, selectedFiles);
      setSelectedFiles([]);
      await loadAll();
    } catch (err: any) {
      setUploadError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDocument = async (docId: number) => {
    if (!window.confirm('Delete this document and all extracted passages?')) return;
    try {
      await api.deleteDocument(docId);
      await loadAll();
    } catch (err: any) {
      alert(`Delete error: ${err.message}`);
    }
  };

  const handleOpenPassages = async (doc: DocumentItem) => {
    setViewPassagesDoc(doc);
    setLoadingPassages(true);
    try {
      const p = await api.getPassages(doc.id);
      setPassagesList(p);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingPassages(false);
    }
  };

  // Run AI analysis
  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const res = await api.triggerAnalysis(projectId);
      await loadAll();
      setActiveTab('claims');
      alert(`Analysis Complete: Extracted ${res.total_claims} claims. Conflicts detected: ${res.conflicts_detected}`);
    } catch (err: any) {
      alert(`Analysis failed: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Conflict resolution handler
  const handleResolveConflict = async (claimId: number, data: { resolution_notes: string; chosen_date?: string; chosen_owner?: string }) => {
    await api.resolveConflict(claimId, data);
    await loadAll();
  };

  // Generate Handover
  const handleGenerateHandover = async () => {
    try {
      const h = await api.generateHandover(projectId);
      await loadAll();
      setActiveTab('handover');
    } catch (err: any) {
      alert(`Handover generation error: ${err.message}`);
    }
  };

  // Handover Item Edits
  const startEditing = (item: HandoverItem) => {
    setEditingItemId(item.id);
    setEditTitle(item.title);
    setEditContent(item.content);
  };

  const saveEdit = async (itemId: number) => {
    if (!activeHandover) return;
    try {
      await api.updateHandoverItem(activeHandover.id, itemId, {
        title: editTitle,
        content: editContent
      });
      setEditingItemId(null);
      await loadAll();
    } catch (err: any) {
      alert(`Update error: ${err.message}`);
    }
  };

  const toggleItemRedaction = async (item: HandoverItem) => {
    if (!activeHandover) return;
    try {
      await api.updateHandoverItem(activeHandover.id, item.id, {
        is_redacted: !item.is_redacted,
        reviewer_notes: !item.is_redacted ? 'Redacted by Project Lead for incoming view' : ''
      });
      await loadAll();
    } catch (err: any) {
      alert(`Redaction error: ${err.message}`);
    }
  };

  const toggleItemAcceptance = async (item: HandoverItem, accept: boolean) => {
    if (!activeHandover) return;
    try {
      await api.updateHandoverItem(activeHandover.id, item.id, {
        is_accepted: accept,
        is_rejected: !accept
      });
      await loadAll();
    } catch (err: any) {
      alert(`Status update error: ${err.message}`);
    }
  };

  // Approve Handover
  const handleApproveHandover = async () => {
    if (!activeHandover) return;
    if (!window.confirm('Approve and sign off this Handover report? It will become visible to incoming team members.')) return;
    setIsApproving(true);
    try {
      await api.approveHandover(activeHandover.id, approvalNotes.trim() || 'Officially approved by Project Lead');
      setApprovalNotes('');
      await loadAll();
      alert('Handover successfully APPROVED! Incoming members can now view the continuation report.');
    } catch (err: any) {
      alert(`Approval error: ${err.message}`);
    } finally {
      setIsApproving(false);
    }
  };

  if (isLoading || !project) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-xs text-slate-500">
        Loading project workspace...
      </div>
    );
  }

  const conflictsList = claims.filter(c => c.verification_status === 'CONFLICT');
  const decisionsList = claims.filter(c => c.category === 'DECISION');
  const tasksList = claims.filter(c => c.category === 'TASK');
  const risksList = claims.filter(c => c.category in ['RISK', 'BLOCKER']);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Top Workspace Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <Link to="/dashboard" className="inline-flex items-center space-x-1 text-xs text-slate-500 hover:text-slate-800 transition">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Projects Hub</span>
            </Link>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-extrabold text-slate-900">{project.title}</h1>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                project.status === 'ACTIVE'
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : 'bg-amber-50 text-amber-700 border border-amber-200'
              }`}>
                {project.status}
              </span>
            </div>
            <p className="text-xs text-slate-600 max-w-3xl">{project.description || 'No description provided.'}</p>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRunAnalysis}
              disabled={isAnalyzing || documents.length === 0}
              className="px-4 py-2.5 bg-gradient-to-r from-brand-600 to-teal-600 hover:from-brand-500 hover:to-teal-500 text-white font-semibold rounded-xl text-xs shadow-md transition flex items-center space-x-2 disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>{isAnalyzing ? 'Extracting Knowledge...' : 'Run AI Analysis'}</span>
            </button>

            <button
              onClick={handleGenerateHandover}
              disabled={claims.length === 0}
              className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl text-xs shadow-sm transition flex items-center space-x-2 disabled:opacity-50"
            >
              <FileCheck className="w-4 h-4" />
              <span>Generate Handover</span>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 gap-6 text-xs font-semibold overflow-x-auto pt-2">
          <button
            onClick={() => setActiveTab('overview')}
            className={`pb-3 border-b-2 transition flex items-center space-x-1.5 ${
              activeTab === 'overview'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Overview & Analytics</span>
          </button>

          <button
            onClick={() => setActiveTab('documents')}
            className={`pb-3 border-b-2 transition flex items-center space-x-1.5 ${
              activeTab === 'documents'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Source Documents ({documents.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('claims')}
            className={`pb-3 border-b-2 transition flex items-center space-x-1.5 ${
              activeTab === 'claims'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>AI Extracted Claims ({claims.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('conflicts')}
            className={`pb-3 border-b-2 transition flex items-center space-x-1.5 ${
              activeTab === 'conflicts'
                ? 'border-rose-600 text-rose-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <AlertCircle className="w-4 h-4 text-rose-500" />
            <span>Conflicts & Discrepancies ({conflictsList.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('handover')}
            className={`pb-3 border-b-2 transition flex items-center space-x-1.5 ${
              activeTab === 'handover'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <FileCheck className="w-4 h-4 text-brand-600" />
            <span>Handover Review Studio ({activeHandover ? `v${activeHandover.version} - ${activeHandover.status}` : 'None'})</span>
          </button>

          <button
            onClick={() => setActiveTab('activity')}
            className={`pb-3 border-b-2 transition flex items-center space-x-1.5 ${
              activeTab === 'activity'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>Activity Trail ({activityLogs.length})</span>
          </button>
        </div>

      </div>

      {/* TAB 1: OVERVIEW & ANALYTICS */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          
          {/* Quick Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-500">Decisions Recorded</span>
              <p className="text-xl font-bold text-slate-900">{decisionsList.length}</p>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-500">Tasks Extracted</span>
              <p className="text-xl font-bold text-brand-600">{tasksList.length}</p>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-500">Risks & Blockers</span>
              <p className="text-xl font-bold text-amber-600">{risksList.length}</p>
            </div>
            <div className="bg-white p-4 rounded-xl border border-rose-200 bg-rose-50/20">
              <span className="text-xs text-rose-700">Flagged Conflicts</span>
              <p className="text-xl font-bold text-rose-600">{conflictsList.length}</p>
            </div>
          </div>

          {/* Project State Summary Banner */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <h3 className="text-sm font-bold text-slate-900">Current Reconstruction State</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              KnowBridge has ingested <strong>{documents.length}</strong> document(s) and mapped <strong>{claims.length}</strong> verified factual statements. 
              {conflictsList.length > 0 ? (
                <span className="text-rose-600 font-semibold block mt-1">
                  ⚠️ Action required: {conflictsList.length} contradiction(s) detected across documents. Please resolve them in the Conflicts tab before approving the handover.
                </span>
              ) : (
                <span className="text-emerald-700 font-semibold block mt-1">
                  ✓ All extracted statements have clean evidence links and verified statuses.
                </span>
              )}
            </p>
          </div>

        </div>
      )}

      {/* TAB 2: DOCUMENTS */}
      {activeTab === 'documents' && (
        <div className="space-y-6">
          
          {/* Upload Drag and Drop Box */}
          <div className="bg-white p-6 rounded-2xl border-2 border-dashed border-slate-300 shadow-sm text-center">
            <form onSubmit={handleUpload} className="space-y-3">
              <div className="w-12 h-12 bg-brand-50 text-brand-600 rounded-2xl flex items-center justify-center mx-auto">
                <UploadCloud className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-800">Upload Project Documents</h4>
                <p className="text-xs text-slate-500">Supports PDF, DOCX, and TXT (up to 25MB each)</p>
              </div>

              <input
                type="file"
                multiple
                accept=".pdf,.docx,.txt,.md"
                onChange={(e) => {
                  if (e.target.files) {
                    setSelectedFiles(Array.from(e.target.files));
                  }
                }}
                className="text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-brand-50 hover:file:text-brand-700 cursor-pointer"
              />

              {selectedFiles.length > 0 && (
                <div className="text-xs text-slate-600 font-medium">
                  Selected {selectedFiles.length} file(s): {selectedFiles.map(f => f.name).join(', ')}
                </div>
              )}

              {uploadError && (
                <p className="text-xs text-rose-600 font-semibold">{uploadError}</p>
              )}

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={selectedFiles.length === 0 || isUploading}
                  className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold shadow-sm transition disabled:opacity-50"
                >
                  {isUploading ? 'Uploading & Extracting Passages...' : 'Upload & Process Documents'}
                </button>
              </div>
            </form>
          </div>

          {/* Document Listing Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-200">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Authorized Source Files</h3>
            </div>
            {documents.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">No documents uploaded yet.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-b border-slate-200">
                    <tr>
                      <th className="px-6 py-3">Filename</th>
                      <th className="px-6 py-3">Type</th>
                      <th className="px-6 py-3">Size</th>
                      <th className="px-6 py-3">Passages</th>
                      <th className="px-6 py-3">Uploaded At</th>
                      <th className="px-6 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {documents.map((d) => (
                      <tr key={d.id} className="hover:bg-slate-50 transition">
                        <td className="px-6 py-3 font-semibold text-slate-900 flex items-center space-x-2">
                          <FileText className="w-4 h-4 text-brand-600 shrink-0" />
                          <span>{d.filename}</span>
                        </td>
                        <td className="px-6 py-3 uppercase text-slate-500 font-bold">{d.file_type}</td>
                        <td className="px-6 py-3 text-slate-500">{(d.file_size / 1024).toFixed(1)} KB</td>
                        <td className="px-6 py-3 font-medium text-brand-700">{d.passage_count} passages</td>
                        <td className="px-6 py-3 text-slate-500">{new Date(d.uploaded_at).toLocaleDateString()}</td>
                        <td className="px-6 py-3 text-right space-x-2">
                          <button
                            onClick={() => handleOpenPassages(d)}
                            className="p-1.5 hover:bg-slate-100 rounded text-slate-600 hover:text-brand-600 transition"
                            title="Inspect Extracted Passages"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteDocument(d.id)}
                            className="p-1.5 hover:bg-rose-50 rounded text-slate-400 hover:text-rose-600 transition"
                            title="Delete Document"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </div>
      )}

      {/* TAB 3: EXTRACTED CLAIMS */}
      {activeTab === 'claims' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-500">
              Showing <strong>{claims.length}</strong> reconstructed facts anchored to source files.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {claims.map((c) => (
              <div key={c.id} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                    {c.category}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    c.verification_status === 'VERIFIED'
                      ? 'bg-emerald-50 text-emerald-700'
                      : c.verification_status === 'CONFLICT'
                      ? 'bg-rose-50 text-rose-700'
                      : 'bg-amber-50 text-amber-700'
                  }`}>
                    {c.verification_status}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-slate-900">{c.title}</h4>
                <p className="text-xs text-slate-600 line-clamp-2">{c.description}</p>

                <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-100">
                  <span>Owner: <strong>{c.owner || 'Not found'}</strong></span>
                  <span>Date: <strong>{c.date_reference || 'N/A'}</strong></span>
                </div>

                <div className="flex justify-end pt-1">
                  <button
                    onClick={() => setSelectedEvidenceClaim(c)}
                    className="text-xs text-brand-600 hover:text-brand-700 font-semibold flex items-center space-x-1"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>View Supporting Evidence</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: CONFLICTS & VERIFICATION */}
      {activeTab === 'conflicts' && (
        <div className="space-y-6">
          <div className="bg-rose-50 border border-rose-200 p-4 rounded-xl text-xs text-rose-800">
            <strong>Cross-Document Reconciliation:</strong> When two documents disagree (e.g. conflicting milestone deadlines), KnowBridge flags both source passages and halts automation until the Project Lead resolves the discrepancy.
          </div>

          {conflictsList.length === 0 ? (
            <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 text-xs text-slate-500 space-y-2">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto" />
              <p className="font-bold text-slate-800 text-sm">No Active Contradictions</p>
              <p>All extracted statements are consistent across all uploaded documents.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {conflictsList.map((conf) => (
                <div key={conf.id} className="bg-white p-6 rounded-2xl border border-rose-200 shadow-sm space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-rose-700 flex items-center space-x-1">
                      <AlertCircle className="w-4 h-4 text-rose-600" />
                      <span>Conflicting Claim: {conf.title}</span>
                    </span>
                    <button
                      onClick={() => setSelectedConflictClaim(conf)}
                      className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold shadow-sm transition"
                    >
                      Resolve Contradiction
                    </button>
                  </div>

                  <p className="text-xs text-slate-700 leading-relaxed font-mono bg-slate-50 p-3 rounded-lg border border-slate-200">
                    {conf.conflict_details || conf.description}
                  </p>

                  <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100">
                    <span>Category: <strong>{conf.category}</strong></span>
                    <span>Confidence: <strong>{Math.round(conf.confidence * 100)}%</strong></span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 5: HANDOVER REVIEW STUDIO */}
      {activeTab === 'handover' && (
        <div className="space-y-6">
          {!activeHandover ? (
            <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 text-xs space-y-3">
              <FileCheck className="w-10 h-10 text-brand-600 mx-auto" />
              <h3 className="text-base font-bold text-slate-900">No Handover Report Generated Yet</h3>
              <p className="text-slate-500 max-w-sm mx-auto">
                Click <strong>"Generate Handover"</strong> above to assemble the 14-section evidence-grounded report.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              
              {/* Handover Status & Action Header */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <h2 className="text-lg font-bold text-slate-900">{activeHandover.title}</h2>
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                      activeHandover.status === 'APPROVED'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-amber-50 text-amber-700 border border-amber-200'
                    }`}>
                      {activeHandover.status} (v{activeHandover.version})
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Created: {new Date(activeHandover.created_at).toLocaleString()} · {activeHandover.items.length} items
                  </p>
                </div>

                {activeHandover.status === 'DRAFT' && (
                  <div className="flex items-center space-x-3">
                    <input
                      type="text"
                      value={approvalNotes}
                      onChange={(e) => setApprovalNotes(e.target.value)}
                      placeholder="Optional sign-off notes..."
                      className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs w-56"
                    />
                    <button
                      onClick={handleApproveHandover}
                      disabled={isApproving}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl text-xs shadow-md transition flex items-center space-x-1.5"
                    >
                      <ShieldCheck className="w-4 h-4" />
                      <span>{isApproving ? 'Approving...' : 'Sign & Approve Handover'}</span>
                    </button>
                  </div>
                )}
              </div>

              {/* Handover 14 Standard Sections */}
              <div className="space-y-6">
                
                {/* 1. Executive Summary */}
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
                  <h3 className="text-xs uppercase font-bold text-brand-700 tracking-wider">1. Executive Summary</h3>
                  <p className="text-sm text-slate-800 leading-relaxed">{activeHandover.executive_summary}</p>
                </div>

                {/* 2 & 3. Current Project Status */}
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
                  <h3 className="text-xs uppercase font-bold text-brand-700 tracking-wider">2 & 3. Project Overview & Current Status</h3>
                  <p className="text-sm text-slate-800 leading-relaxed">{activeHandover.current_status}</p>
                </div>

                {/* Handover Structured Items (Sections 4 through 10) */}
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden p-6 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                    <h3 className="text-xs uppercase font-bold text-slate-800 tracking-wider">Structured Statements & Claims</h3>
                    <span className="text-xs text-slate-500">Edit, redact, or accept each statement before approval</span>
                  </div>

                  <div className="space-y-4">
                    {activeHandover.items.map((item) => (
                      <div
                        key={item.id}
                        className={`p-4 rounded-xl border transition ${
                          item.is_redacted
                            ? 'bg-slate-100 border-slate-300 opacity-75'
                            : item.is_rejected
                            ? 'bg-rose-50/50 border-rose-200 line-through opacity-60'
                            : 'bg-white border-slate-200 hover:border-slate-300'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                            {item.section}
                          </span>

                          <div className="flex items-center space-x-2">
                            {item.is_redacted && (
                              <span className="text-[10px] bg-slate-700 text-white font-bold px-2 py-0.5 rounded flex items-center space-x-1">
                                <Lock className="w-3 h-3" />
                                <span>REDACTED (Hidden from Incoming)</span>
                              </span>
                            )}

                            {activeHandover.status === 'DRAFT' && (
                              <div className="flex items-center space-x-1">
                                <button
                                  onClick={() => startEditing(item)}
                                  className="p-1 hover:bg-slate-100 text-slate-500 hover:text-slate-800 rounded"
                                  title="Edit text"
                                >
                                  <Edit3 className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  onClick={() => toggleItemRedaction(item)}
                                  className={`p-1 rounded text-xs ${
                                    item.is_redacted ? 'text-amber-600 hover:bg-amber-50' : 'text-slate-400 hover:text-slate-700'
                                  }`}
                                  title={item.is_redacted ? 'Remove Redaction' : 'Redact item'}
                                >
                                  <Lock className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  onClick={() => toggleItemAcceptance(item, !item.is_accepted)}
                                  className={`p-1 rounded ${
                                    item.is_accepted ? 'text-emerald-600 hover:bg-emerald-50' : 'text-slate-400 hover:text-emerald-600'
                                  }`}
                                  title={item.is_accepted ? 'Reject statement' : 'Accept statement'}
                                >
                                  {item.is_accepted ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
                                </button>
                              </div>
                            )}
                          </div>
                        </div>

                        {editingItemId === item.id ? (
                          <div className="space-y-2 mt-2">
                            <input
                              type="text"
                              value={editTitle}
                              onChange={(e) => setEditTitle(e.target.value)}
                              className="w-full px-2 py-1 border border-slate-300 rounded text-xs font-bold"
                            />
                            <textarea
                              value={editContent}
                              onChange={(e) => setEditContent(e.target.value)}
                              rows={2}
                              className="w-full px-2 py-1 border border-slate-300 rounded text-xs"
                            />
                            <div className="flex justify-end space-x-2">
                              <button
                                onClick={() => setEditingItemId(null)}
                                className="px-2 py-1 text-xs text-slate-500"
                              >
                                Cancel
                              </button>
                              <button
                                onClick={() => saveEdit(item.id)}
                                className="px-3 py-1 bg-brand-600 text-white rounded text-xs font-semibold"
                              >
                                Save
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div>
                            <h4 className="text-xs font-bold text-slate-900">{item.title}</h4>
                            <p className="text-xs text-slate-700 mt-1">{item.content}</p>
                            {item.evidence_excerpt && (
                              <p className="text-[11px] text-slate-500 mt-1.5 italic bg-slate-50 p-2 rounded border border-slate-100">
                                Source: <strong>{item.source_filename || 'Project Document'}</strong> (p. {item.source_page || 1}): "{item.evidence_excerpt}"
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* 11. Recommended Next Actions */}
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-xs uppercase font-bold text-cyan-700 tracking-wider">11. Recommended Next Actions</h3>
                    <span className="text-[10px] bg-cyan-50 text-cyan-700 px-2 py-0.5 rounded border border-cyan-200 font-bold">
                      AI Recommendations (Non-verified Advice)
                    </span>
                  </div>
                  <pre className="text-xs text-slate-800 whitespace-pre-wrap font-sans leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
                    {activeHandover.recommended_actions}
                  </pre>
                </div>

                {/* 12. Missing Information */}
                <div className="bg-white p-6 rounded-2xl border border-amber-200 shadow-sm space-y-2 bg-amber-50/20">
                  <h3 className="text-xs uppercase font-bold text-amber-800 tracking-wider">12. Identified Missing Information</h3>
                  <pre className="text-xs text-slate-800 whitespace-pre-wrap font-sans leading-relaxed">
                    {activeHandover.missing_information}
                  </pre>
                </div>

                {/* 13. Conflicting Information */}
                <div className="bg-white p-6 rounded-2xl border border-rose-200 shadow-sm space-y-2 bg-rose-50/20">
                  <h3 className="text-xs uppercase font-bold text-rose-800 tracking-wider">13. Cross-Document Contradictions</h3>
                  <pre className="text-xs text-slate-800 whitespace-pre-wrap font-sans leading-relaxed">
                    {activeHandover.conflicting_information}
                  </pre>
                </div>

              </div>

            </div>
          )}
        </div>
      )}

      {/* TAB 6: ACTIVITY TRAIL */}
      {activeTab === 'activity' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Project Audit Log Timeline</h3>
          <div className="space-y-4">
            {activityLogs.map((log) => (
              <div key={log.id} className="flex items-start space-x-3 text-xs border-b border-slate-100 pb-3">
                <div className="p-1.5 bg-slate-100 text-slate-600 rounded-lg shrink-0 mt-0.5">
                  <Clock className="w-3.5 h-3.5" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-slate-900">{log.action}</span>
                    <span className="text-[10px] text-slate-400">by {log.user_name || 'System'}</span>
                  </div>
                  <p className="text-slate-600 mt-0.5">{log.details}</p>
                </div>
                <span className="text-[10px] text-slate-400">{new Date(log.timestamp).toLocaleTimeString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extracted Passage Viewer Modal */}
      {viewPassagesDoc && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col border border-slate-200">
            <div className="p-4 border-b border-slate-200 flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900">Extracted Passages: {viewPassagesDoc.filename}</h3>
              <button onClick={() => setViewPassagesDoc(null)} className="text-slate-400 hover:text-slate-800">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-4 overflow-y-auto space-y-3 flex-1 text-xs">
              {loadingPassages ? (
                <p>Loading passages...</p>
              ) : passagesList.map((p) => (
                <div key={p.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-bold uppercase">
                    <span>Passage #{p.passage_number} (Page {p.page_number || 1})</span>
                    <span>{p.section_title || 'General'}</span>
                  </div>
                  <p className="text-slate-800 font-mono text-[11px] leading-relaxed">{p.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Supporting Evidence Modal */}
      <EvidenceModal
        claim={selectedEvidenceClaim}
        onClose={() => setSelectedEvidenceClaim(null)}
      />

      {/* Conflict Resolution Modal */}
      <ConflictModal
        claim={selectedConflictClaim}
        onClose={() => setSelectedConflictClaim(null)}
        onResolved={handleResolveConflict}
      />

    </div>
  );
};
