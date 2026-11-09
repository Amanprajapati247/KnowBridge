import {
  AuthResponse,
  User,
  Project,
  DocumentItem,
  DocumentPassage,
  ExtractedClaim,
  Handover,
  HandoverItem,
  AuditLog,
  DashboardStats
} from '../types';

const API_BASE = '/api';

function getHeaders(isFormData: boolean = false): HeadersInit {
  const token = localStorage.getItem('knowbridge_token');
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }
  return headers;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = 'An error occurred';
    try {
      const errorJson = await res.json();
      errorDetail = errorJson.detail || errorDetail;
    } catch {
      errorDetail = res.statusText || errorDetail;
    }
    throw new Error(errorDetail);
  }
  if (res.status === 204) {
    return {} as T;
  }
  return res.json();
}

export const api = {
  // --- AUTH ---
  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return handleResponse<AuthResponse>(res);
  },

  async register(data: { email: string; password: string; full_name: string; role: string }): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return handleResponse<AuthResponse>(res);
  },

  async getCurrentUser(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getHeaders()
    });
    return handleResponse<User>(res);
  },

  // --- PROJECTS ---
  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/projects/stats/dashboard`, {
      headers: getHeaders()
    });
    return handleResponse<DashboardStats>(res);
  },

  async listProjects(): Promise<Project[]> {
    const res = await fetch(`${API_BASE}/projects`, {
      headers: getHeaders()
    });
    return handleResponse<Project[]>(res);
  },

  async createProject(title: string, description?: string): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ title, description })
    });
    return handleResponse<Project>(res);
  },

  async getProject(id: number): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/${id}`, {
      headers: getHeaders()
    });
    return handleResponse<Project>(res);
  },

  async updateProject(id: number, data: { title?: string; description?: string; status?: string }): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/${id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<Project>(res);
  },

  async deleteProject(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/projects/${id}`, {
      method: 'DELETE',
      headers: getHeaders()
    });
    return handleResponse<void>(res);
  },

  async seedDemoProject(): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/seed-demo`, {
      method: 'POST',
      headers: getHeaders()
    });
    return handleResponse<Project>(res);
  },

  // --- DOCUMENTS ---
  async uploadDocuments(projectId: number, files: File[]): Promise<DocumentItem[]> {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    const res = await fetch(`${API_BASE}/projects/${projectId}/documents`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData
    });
    return handleResponse<DocumentItem[]>(res);
  },

  async listDocuments(projectId: number): Promise<DocumentItem[]> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/documents`, {
      headers: getHeaders()
    });
    return handleResponse<DocumentItem[]>(res);
  },

  async getPassages(documentId: number): Promise<DocumentPassage[]> {
    const res = await fetch(`${API_BASE}/documents/${documentId}/passages`, {
      headers: getHeaders()
    });
    return handleResponse<DocumentPassage[]>(res);
  },

  async downloadDocument(documentId: number, filename: string): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${documentId}/download`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to download document');
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },

  async deleteDocument(documentId: number): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${documentId}`, {
      method: 'DELETE',
      headers: getHeaders()
    });
    return handleResponse<void>(res);
  },

  // --- AI ANALYSIS & EVIDENCE ---
  async triggerAnalysis(projectId: number): Promise<{ message: string; total_claims: number; conflicts_detected: number }> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/analyze`, {
      method: 'POST',
      headers: getHeaders()
    });
    return handleResponse<{ message: string; total_claims: number; conflicts_detected: number }>(res);
  },

  async getClaims(projectId: number): Promise<ExtractedClaim[]> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/claims`, {
      headers: getHeaders()
    });
    return handleResponse<ExtractedClaim[]>(res);
  },

  async resolveConflict(claimId: number, data: { resolution_notes: string; chosen_date?: string; chosen_owner?: string }): Promise<ExtractedClaim> {
    const res = await fetch(`${API_BASE}/claims/${claimId}/resolve`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<ExtractedClaim>(res);
  },

  // --- HANDOVERS ---
  async generateHandover(projectId: number): Promise<Handover> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/handovers/generate`, {
      method: 'POST',
      headers: getHeaders()
    });
    return handleResponse<Handover>(res);
  },

  async listHandovers(projectId: number): Promise<Handover[]> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/handovers`, {
      headers: getHeaders()
    });
    return handleResponse<Handover[]>(res);
  },

  async getHandover(id: number): Promise<Handover> {
    const res = await fetch(`${API_BASE}/handovers/${id}`, {
      headers: getHeaders()
    });
    return handleResponse<Handover>(res);
  },

  async updateHandoverItem(handoverId: number, itemId: number, data: Partial<HandoverItem>): Promise<HandoverItem> {
    const res = await fetch(`${API_BASE}/handovers/${handoverId}/items/${itemId}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<HandoverItem>(res);
  },

  async approveHandover(handoverId: number, approvalNotes?: string): Promise<Handover> {
    const res = await fetch(`${API_BASE}/handovers/${handoverId}/approve`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ approval_notes: approvalNotes })
    });
    return handleResponse<Handover>(res);
  },

  // --- INCOMING MEMBER PORTAL ---
  async listApprovedHandovers(): Promise<Handover[]> {
    const res = await fetch(`${API_BASE}/incoming/handovers`, {
      headers: getHeaders()
    });
    return handleResponse<Handover[]>(res);
  },

  async getApprovedHandover(id: number): Promise<Handover> {
    const res = await fetch(`${API_BASE}/incoming/handovers/${id}`, {
      headers: getHeaders()
    });
    return handleResponse<Handover>(res);
  },

  // --- ACTIVITY ---
  async getProjectActivity(projectId: number): Promise<AuditLog[]> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/activity`, {
      headers: getHeaders()
    });
    return handleResponse<AuditLog[]>(res);
  }
};
