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
      const response = await fetchAPI(api.dashboard.stats);
      
      if (!response.success) {
        throw new Error('Failed to fetch dashboard stats');
      }
      
      return response.stats;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  }

  static async getQueueSummary(): Promise<QueueSummary> {
    try {
      const [queueResponse, patientsResponse] = await Promise.all([
        fetchAPI(api.queue.entries),
        fetchAPI(api.patients.list)
      ]);
      
      if (!queueResponse.success || !patientsResponse.success) {
        throw new Error('Failed to fetch queue summary');
      }
      
      // Transform the data to match the expected format
      const waiting = queueResponse.queue_entries
        .filter((entry: any) => entry.status === 'waiting')
        .map((entry: any) => ({
          id: entry.id,
          ticket_number: entry.ticket_number,
          patient_name: entry.patient ? `${entry.patient.first_name} ${entry.patient.last_name}` : 'Unknown',
          reason: entry.reason || 'No reason provided',
          priority: entry.priority,
          queue_type: entry.queue_type,
          wait_time_minutes: entry.estimated_wait_time || 30,
          estimated_wait_time: entry.estimated_wait_time
        }));
      
      const in_progress = queueResponse.queue_entries
        .filter((entry: any) => entry.status === 'in_progress')
        .map((entry: any) => ({
          id: entry.id,
          ticket_number: entry.ticket_number,
          patient_name: entry.patient ? `${entry.patient.first_name} ${entry.patient.last_name}` : 'Unknown',
          reason: entry.reason || 'No reason provided',
          priority: entry.priority,
          queue_type: entry.queue_type,
          wait_time_minutes: entry.actual_wait_time || 0,
          estimated_wait_time: entry.estimated_wait_time
        }));
      
      const called = queueResponse.queue_entries
        .filter((entry: any) => entry.status === 'called')
        .map((entry: any) => ({
          id: entry.id,
          ticket_number: entry.ticket_number,
          patient_name: entry.patient ? `${entry.patient.first_name} ${entry.patient.last_name}` : 'Unknown',
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

