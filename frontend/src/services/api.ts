import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
  Case,
  CaseCreate,
  CaseUpdate,
  CaseFilters,
  User,
  UserCreate,
  UserUpdate,
  Team,
  TeamCreate,
  TeamUpdate,
  TriageResult,
  AuditLog,
  AuditFilters,
  AnalyticsSnapshot,
  Document,
  PaginatedResponse,
  ApiResponse,
  PaginationParams
} from '@/types';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (username: string, password: string): Promise<{ token: string; user: User }> => {
    const response = await apiClient.post('/auth/login', { username, password });
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
    localStorage.removeItem('auth_token');
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  refreshToken: async (): Promise<{ token: string }> => {
    const response = await apiClient.post('/auth/refresh');
    return response.data;
  },
};

// Cases API
export const casesAPI = {
  // Get cases with pagination and filters
  getCases: async (
    params: PaginationParams & CaseFilters = { page: 1, size: 20 }
  ): Promise<PaginatedResponse<Case>> => {
    const response = await apiClient.get('/cases', { params });
    return response.data;
  },

  // Get single case by ID
  getCase: async (id: string): Promise<Case> => {
    const response = await apiClient.get(`/cases/${id}`);
    return response.data;
  },

  // Create new case
  createCase: async (caseData: CaseCreate): Promise<Case> => {
    const response = await apiClient.post('/cases', caseData);
    return response.data;
  },

  // Update case
  updateCase: async (id: string, caseData: CaseUpdate): Promise<Case> => {
    const response = await apiClient.put(`/cases/${id}`, caseData);
    return response.data;
  },

  // Delete case
  deleteCase: async (id: string): Promise<void> => {
    await apiClient.delete(`/cases/${id}`);
  },

  // Run triage on case
  runTriage: async (id: string): Promise<TriageResult> => {
    const response = await apiClient.post(`/triage/run`, { case_id: id });
    return response.data;
  },

  // Upload document for case
  uploadDocument: async (caseId: string, file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(`/cases/${caseId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get documents for case
  getCaseDocuments: async (caseId: string): Promise<Document[]> => {
    const response = await apiClient.get(`/cases/${caseId}/documents`);
    return response.data;
  },
};

// Users API
export const usersAPI = {
  getUsers: async (params: PaginationParams = { page: 1, size: 20 }): Promise<PaginatedResponse<User>> => {
    const response = await apiClient.get('/users', { params });
    return response.data;
  },

  getUser: async (id: string): Promise<User> => {
    const response = await apiClient.get(`/users/${id}`);
    return response.data;
  },

  createUser: async (userData: UserCreate): Promise<User> => {
    const response = await apiClient.post('/users', userData);
    return response.data;
  },

  updateUser: async (id: string, userData: UserUpdate): Promise<User> => {
    const response = await apiClient.put(`/users/${id}`, userData);
    return response.data;
  },

  deleteUser: async (id: string): Promise<void> => {
    await apiClient.delete(`/users/${id}`);
  },
};

// Teams API
export const teamsAPI = {
  getTeams: async (params: PaginationParams = { page: 1, size: 20 }): Promise<PaginatedResponse<Team>> => {
    const response = await apiClient.get('/teams', { params });
    return response.data;
  },

  getTeam: async (id: string): Promise<Team> => {
    const response = await apiClient.get(`/teams/${id}`);
    return response.data;
  },

  createTeam: async (teamData: TeamCreate): Promise<Team> => {
    const response = await apiClient.post('/teams', teamData);
    return response.data;
  },

  updateTeam: async (id: string, teamData: TeamUpdate): Promise<Team> => {
    const response = await apiClient.put(`/teams/${id}`, teamData);
    return response.data;
  },

  deleteTeam: async (id: string): Promise<void> => {
    await apiClient.delete(`/teams/${id}`);
  },
};

// Audit API
export const auditAPI = {
  getAuditLogs: async (
    params: { page: number; size: number; filters: AuditFilters }
  ): Promise<PaginatedResponse<AuditLog>> => {
    const response = await apiClient.get('/audit/logs', { params });
    return response.data;
  },

  getAuditLog: async (id: string): Promise<AuditLog> => {
    const response = await apiClient.get(`/audit/logs/${id}`);
    return response.data;
  },

  exportAuditLogs: async (filters: AuditFilters, format: 'json' | 'csv' | 'pdf' = 'json'): Promise<Blob> => {
    const response = await apiClient.get('/audit/export', {
      params: { ...filters, format },
      responseType: 'blob',
    });
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  getOverview: async (): Promise<{
    total_cases: number;
    pending_cases: number;
    avg_processing_time: number;
    escalation_rate: number;
    sla_compliance_rate: number;
  }> => {
    const response = await apiClient.get('/analytics/overview');
    return response.data;
  },

  getCaseVolume: async (period: 'day' | 'week' | 'month' = 'week'): Promise<Array<{ date: string; count: number }>> => {
    const response = await apiClient.get('/analytics/case-volume', { params: { period } });
    return response.data;
  },

  getRiskDistribution: async (): Promise<Array<{ risk_level: string; count: number; percentage: number }>> => {
    const response = await apiClient.get('/analytics/risk-distribution');
    return response.data;
  },

  getTeamPerformance: async (): Promise<Array<{
    team_id: string;
    team_name: string;
    total_cases: number;
    avg_processing_time: number;
    sla_compliance_rate: number;
    escalation_rate: number;
  }>> => {
    const response = await apiClient.get('/analytics/team-performance');
    return response.data;
  },

  getSLACompliance: async (period: 'day' | 'week' | 'month' = 'week'): Promise<Array<{ date: string; compliance_rate: number }>> => {
    const response = await apiClient.get('/analytics/sla-compliance', { params: { period } });
    return response.data;
  },

  getAnalyticsSnapshot: async (date?: string): Promise<AnalyticsSnapshot> => {
    const response = await apiClient.get('/analytics/snapshot', { params: { date } });
    return response.data;
  },

  getAllAnalytics: async (params: { timeRange: string; teamId?: string }): Promise<AnalyticsSnapshot> => {
    const response = await apiClient.get('/analytics/all', { params });
    return response.data;
  },
};

// Health API
export const healthAPI = {
  getHealth: async (): Promise<{
    status: string;
    timestamp: string;
    services: Record<string, { status: string; response_time_ms: number }>;
  }> => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

// Utility functions
export const downloadFile = (url: string, filename: string): void => {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatDuration = (milliseconds: number): string => {
  const seconds = Math.floor(milliseconds / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  } else {
    return `${seconds}s`;
  }
};

export default apiClient;
