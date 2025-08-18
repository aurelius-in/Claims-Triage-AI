// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

// User types
export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  team_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export enum UserRole {
  ADMIN = 'admin',
  SUPERVISOR = 'supervisor',
  AGENT = 'agent',
  AUDITOR = 'auditor'
}

// Team types
export interface Team {
  id: string;
  name: string;
  description?: string;
  domain: string;
  capacity: number;
  current_load: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  users?: User[];
}

// Case types
export interface Case {
  id: string;
  external_id: string;
  case_type: CaseType;
  title: string;
  description: string;
  urgency_level: UrgencyLevel;
  risk_level: RiskLevel;
  status: CaseStatus;
  assigned_team_id?: string;
  assigned_user_id?: string;
  priority_score: number;
  estimated_value?: number;
  customer_info: CustomerInfo;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
  team?: Team;
  assigned_user?: User;
  documents?: Document[];
  triage_results?: TriageResult[];
}

export enum CaseType {
  AUTO_INSURANCE = 'auto_insurance',
  HEALTH_INSURANCE = 'health_insurance',
  PROPERTY_INSURANCE = 'property_insurance',
  LIFE_INSURANCE = 'life_insurance',
  FRAUD_INVESTIGATION = 'fraud_investigation',
  HEALTHCARE_PRIOR_AUTH = 'healthcare_prior_auth',
  HEALTHCARE_CLAIMS = 'healthcare_claims',
  BANK_DISPUTE = 'bank_dispute',
  LOAN_APPLICATION = 'loan_application',
  LEGAL_INTAKE = 'legal_intake',
  LEGAL_CONTRACT_REVIEW = 'legal_contract_review'
}

export enum UrgencyLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  EXTREME = 'extreme'
}

export enum CaseStatus {
  PENDING = 'pending',
  IN_REVIEW = 'in_review',
  ESCALATED = 'escalated',
  RESOLVED = 'resolved',
  CLOSED = 'closed'
}

export interface CustomerInfo {
  name: string;
  email?: string;
  phone?: string;
  policy_number?: string;
  account_number?: string;
}

// Document types
export interface Document {
  id: string;
  case_id: string;
  filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  uploaded_by: string;
  created_at: string;
}

// Triage Result types
export interface TriageResult {
  id: string;
  case_id: string;
  agent_results: AgentResult[];
  final_decision: TriageDecision;
  confidence_score: number;
  processing_time_ms: number;
  created_at: string;
  case?: Case;
}

export interface AgentResult {
  agent_name: string;
  status: 'success' | 'error' | 'timeout';
  output: any;
  confidence: number;
  processing_time_ms: number;
  error_message?: string;
}

export interface TriageDecision {
  assigned_team_id: string;
  assigned_user_id?: string;
  priority_score: number;
  sla_target_hours: number;
  escalation_reason?: string;
  next_actions: string[];
  risk_factors: string[];
}

// Audit Log types
export interface AuditLog {
  id: string;
  user_id: string;
  action: AuditAction;
  resource_type: ResourceType;
  resource_id?: string;
  details: string;
  timestamp: string;
  ip_address?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export type AuditAction = 
  | 'create' 
  | 'update' 
  | 'delete' 
  | 'login' 
  | 'logout' 
  | 'export' 
  | 'import' 
  | 'triage_run' 
  | 'triage_complete' 
  | 'triage_failed';

export type ResourceType = 
  | 'case' 
  | 'user' 
  | 'team' 
  | 'document' 
  | 'triage_result' 
  | 'analytics';

// Analytics types
export interface AnalyticsSnapshot {
  id: string;
  snapshot_date: string;
  total_cases: number;
  cases_by_status: Record<CaseStatus, number>;
  cases_by_type: Record<CaseType, number>;
  cases_by_urgency: Record<UrgencyLevel, number>;
  cases_by_risk: Record<RiskLevel, number>;
  avg_processing_time_hours: number;
  escalation_rate: number;
  sla_compliance_rate: number;
  team_performance: TeamPerformance[];
  created_at: string;
}

export interface TeamPerformance {
  team_id: string;
  team_name: string;
  total_cases: number;
  avg_processing_time_hours: number;
  sla_compliance_rate: number;
  escalation_rate: number;
}

export interface AnalyticsOverview {
  total_cases: number;
  pending_cases: number;
  avg_processing_time: number;
  escalation_rate: number;
  sla_compliance_rate: number;
}

// Form types
export interface CaseCreate {
  external_id: string;
  case_type: CaseType;
  title: string;
  description: string;
  customer_info: CustomerInfo;
  estimated_value?: number;
  metadata?: Record<string, any>;
}

export interface CaseUpdate {
  title?: string;
  description?: string;
  urgency_level?: UrgencyLevel;
  risk_level?: RiskLevel;
  status?: CaseStatus;
  assigned_team_id?: string;
  assigned_user_id?: string;
  priority_score?: number;
  estimated_value?: number;
  customer_info?: CustomerInfo;
  metadata?: Record<string, any>;
}

export interface UserCreate {
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  team_id?: string;
  password: string;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  role?: UserRole;
  team_id?: string;
  is_active?: boolean;
}

export interface TeamCreate {
  name: string;
  description?: string;
  domain: string;
  capacity: number;
}

export interface TeamUpdate {
  name?: string;
  description?: string;
  domain?: string;
  capacity?: number;
  is_active?: boolean;
}

// Filter and pagination types
export interface PaginationParams {
  page: number;
  size: number;
}

export interface CaseFilters {
  status?: CaseStatus[];
  case_type?: CaseType[];
  urgency_level?: UrgencyLevel[];
  risk_level?: RiskLevel[];
  team_id?: string;
  assigned_user_id?: string;
  created_after?: string;
  created_before?: string;
}

export interface AuditFilters {
  action: string;
  resourceType: string;
  userId: string;
  dateFrom: string;
  dateTo: string;
  search: string;
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// UI State types
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface TableState {
  page: number;
  pageSize: number;
  totalRows: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filters: Record<string, any>;
}

// Chart data types
export interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

export interface TimeSeriesData {
  date: string;
  value: number;
  category?: string;
}

export interface RiskDistribution {
  risk_level: RiskLevel;
  count: number;
  percentage: number;
}

export interface TeamLoadData {
  team_name: string;
  current_load: number;
  capacity: number;
  utilization_percentage: number;
}

// Notification types
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Theme types
export interface ThemeConfig {
  mode: 'light' | 'dark';
  primaryColor: string;
  secondaryColor: string;
}

// Settings types
export interface UserSettings {
  theme: ThemeConfig;
  notifications: {
    email: boolean;
    push: boolean;
    sound: boolean;
  };
  dashboard: {
    defaultView: 'overview' | 'triage' | 'analytics';
    refreshInterval: number;
  };
}
