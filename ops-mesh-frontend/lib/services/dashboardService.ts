import { apiClient } from '../api';

export interface DashboardStats {
  queue_stats: {
    total_waiting: number;
    total_in_progress: number;
    total_called: number;
    walk_ins_waiting: number;
    appointments_waiting: number;
    urgent_waiting: number;
    high_waiting: number;
  };
  appointment_stats: {
    total_today: number;
    checked_in_today: number;
    completed_today: number;
    check_in_rate: number;
  };
  performance_metrics: {
    average_wait_time_minutes: number;
    recent_check_ins: number;
    recent_completions: number;
  };
}

export interface QueueSummary {
  waiting: QueuePatient[];
  in_progress: QueuePatient[];
  called: QueuePatient[];
}

export interface QueuePatient {
  id: number;
  ticket_number: string;
  patient_name: string;
  reason: string;
  priority: string;
  queue_type: string;
  wait_time_minutes: number;
  estimated_wait_time?: number;
}

export interface KPIs {
  handoff_latency_seconds: number;
  end_to_end_time_minutes: number;
  auto_resolved_percentage: number;
  total_processed_24h: number;
  completed_24h: number;
}

export class DashboardService {
  static async getDashboardStats(): Promise<DashboardStats> {
    const response = await apiClient.get<DashboardStats>('/dashboard/stats');
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    if (!response.data) {
      throw new Error('Failed to fetch dashboard stats');
    }
    
    return response.data;
  }

  static async getQueueSummary(): Promise<QueueSummary> {
    const response = await apiClient.get<QueueSummary>('/dashboard/queue-summary');
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    if (!response.data) {
      throw new Error('Failed to fetch queue summary');
    }
    
    return response.data;
  }

  static async getKPIs(): Promise<KPIs> {
    const response = await apiClient.get<KPIs>('/dashboard/kpis');
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    if (!response.data) {
      throw new Error('Failed to fetch KPIs');
    }
    
    return response.data;
  }
}

