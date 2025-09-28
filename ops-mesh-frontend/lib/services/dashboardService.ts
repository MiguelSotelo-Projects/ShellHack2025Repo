import { api, fetchAPI } from '../api';

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

// Backend response format
interface BackendDashboardStats {
  success: boolean;
  total_patients: number;
  patients_served: number;
  queue_waiting: number;
  queue_in_progress: number;
  average_wait_time: number;
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
    try {
      const response: BackendDashboardStats = await fetchAPI(api.dashboard.stats);
      
      if (!response.success) {
        throw new Error('Failed to fetch dashboard stats');
      }
      
      // Transform backend response to frontend format
      return {
        queue_stats: {
          total_waiting: response.queue_waiting,
          total_in_progress: response.queue_in_progress,
          total_called: 0, // Not provided by backend
          walk_ins_waiting: Math.floor(response.queue_waiting * 0.7), // Estimate
          appointments_waiting: Math.floor(response.queue_waiting * 0.3), // Estimate
          urgent_waiting: Math.floor(response.queue_waiting * 0.1), // Estimate
          high_waiting: Math.floor(response.queue_waiting * 0.2), // Estimate
        },
        appointment_stats: {
          total_today: response.total_patients,
          checked_in_today: response.patients_served,
          completed_today: response.patients_served,
          check_in_rate: response.total_patients > 0 ? Math.round((response.patients_served / response.total_patients) * 100) : 0,
        },
        performance_metrics: {
          average_wait_time_minutes: response.average_wait_time,
          recent_check_ins: response.patients_served,
          recent_completions: response.patients_served,
        }
      };
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  }

  static async getQueueSummary(): Promise<QueueSummary> {
    try {
      const queueResponse = await fetchAPI(api.queue.entries);
      
      // The backend returns an array directly, not wrapped in a success object
      const queueEntries = Array.isArray(queueResponse) ? queueResponse : [];
      
      // Transform the data to match the expected format
      const waiting = queueEntries
        .filter((entry: any) => entry.status === 'waiting')
        .map((entry: any) => ({
          id: entry.id,
          ticket_number: entry.ticket_number,
          patient_name: entry.patient_name || 'Unknown',
          reason: entry.reason || 'No reason provided',
          priority: entry.priority,
          queue_type: entry.queue_type,
          wait_time_minutes: entry.estimated_wait_time || 30,
          estimated_wait_time: entry.estimated_wait_time
        }));
      
      const in_progress = queueEntries
        .filter((entry: any) => entry.status === 'in_progress')
        .map((entry: any) => ({
          id: entry.id,
          ticket_number: entry.ticket_number,
          patient_name: entry.patient_name || 'Unknown',
          reason: entry.reason || 'No reason provided',
          priority: entry.priority,
          queue_type: entry.queue_type,
          wait_time_minutes: entry.actual_wait_time || 0,
          estimated_wait_time: entry.estimated_wait_time
        }));
      
      const called = queueEntries
        .filter((entry: any) => entry.status === 'called')
        .map((entry: any) => ({
          id: entry.id,
          ticket_number: entry.ticket_number,
          patient_name: entry.patient_name || 'Unknown',
          reason: entry.reason || 'No reason provided',
          priority: entry.priority,
          queue_type: entry.queue_type,
          wait_time_minutes: entry.actual_wait_time || 0,
          estimated_wait_time: entry.estimated_wait_time
        }));
      
      return {
        waiting,
        in_progress,
        called
      };
    } catch (error) {
      console.error('Error fetching queue summary:', error);
      throw error;
    }
  }

  static async getKPIs(): Promise<KPIs> {
    try {
      // For now, return mock KPIs since we don't have these endpoints yet
      return {
        handoff_latency_seconds: 45,
        end_to_end_time_minutes: 25,
        auto_resolved_percentage: 85,
        total_processed_24h: 120,
        completed_24h: 98
      };
    } catch (error) {
      console.error('Error fetching KPIs:', error);
      throw error;
    }
  }
}

