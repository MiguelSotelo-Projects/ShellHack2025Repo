import { apiClient } from '../api';

export interface QueueEntry {
  id: number;
  ticket_number: string;
  status: 'waiting' | 'called' | 'in_progress' | 'completed' | 'cancelled';
  queue_type: 'walk_in' | 'appointment' | 'emergency';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  reason?: string;
  estimated_wait_time?: number;
  patient_name?: string;
  appointment_code?: string;
  created_at: string;
}

export interface WalkInRequest {
  first_name: string;
  last_name: string;
  reason: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  phone?: string;
}

export interface QueueEntryResponse {
  id: number;
  ticket_number: string;
  status: string;
  queue_type: string;
  priority: string;
  reason?: string;
  estimated_wait_time?: number;
  patient_name?: string;
  appointment_code?: string;
  created_at: string;
}

export class QueueService {
  static async getQueueEntries(): Promise<QueueEntry[]> {
    const response = await apiClient.get<QueueEntryResponse[]>('/queue/');
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    return response.data || [];
  }

  static async getQueueEntryById(id: number): Promise<QueueEntry> {
    const response = await apiClient.get<QueueEntry>(`/queue/${id}`);
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    if (!response.data) {
      throw new Error('Queue entry not found');
    }
    
    return response.data;
  }

  static async getQueueEntryByTicket(ticketNumber: string): Promise<QueueEntry> {
    const response = await apiClient.get<QueueEntry>(`/queue/ticket/${ticketNumber}`);
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    if (!response.data) {
      throw new Error('Queue entry not found');
    }
    
    return response.data;
  }

  static async createWalkIn(walkIn: WalkInRequest): Promise<QueueEntry> {
    const response = await apiClient.post<QueueEntry>('/queue/walk-in', walkIn);
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    if (!response.data) {
      throw new Error('Failed to create walk-in');
    }
    
    return response.data;
  }

  static async callPatient(queueId: number): Promise<{ message: string; ticket_number: string }> {
    const response = await apiClient.post<{ message: string; ticket_number: string }>(`/queue/${queueId}/call`);
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    if (!response.data) {
      throw new Error('Failed to call patient');
    }
    
    return response.data;
  }

  static async startService(queueId: number): Promise<{ message: string; ticket_number: string }> {
    const response = await apiClient.post<{ message: string; ticket_number: string }>(`/queue/${queueId}/start`);
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    if (!response.data) {
      throw new Error('Failed to start service');
    }
    
    return response.data;
  }

  static async completeService(queueId: number): Promise<{ message: string; ticket_number: string }> {
    const response = await apiClient.post<{ message: string; ticket_number: string }>(`/queue/${queueId}/complete`);
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    if (!response.data) {
      throw new Error('Failed to complete service');
    }
    
    return response.data;
  }
}

