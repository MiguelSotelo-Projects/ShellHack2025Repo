import { api, fetchAPI } from '../api';

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
    try {
      const response = await fetchAPI(api.queue.entries);
      
      // The backend returns an array directly, not wrapped in a success object
      return Array.isArray(response) ? response : [];
    } catch (error) {
      console.error('Error fetching queue entries:', error);
      throw error;
    }
  }

  static async getQueueEntryById(id: number): Promise<QueueEntry> {
    try {
      const response = await fetchAPI(`${api.queue.entries}/${id}`);
      
      if (!response) {
        throw new Error('Queue entry not found');
      }
      
      return response;
    } catch (error) {
      console.error('Error fetching queue entry:', error);
      throw error;
    }
  }

  static async getQueueEntryByTicket(ticketNumber: string): Promise<QueueEntry> {
    try {
      const response = await fetchAPI(`${api.queue.entries}/ticket/${ticketNumber}`);
      
      if (!response) {
        throw new Error('Queue entry not found');
      }
      
      return response;
    } catch (error) {
      console.error('Error fetching queue entry by ticket:', error);
      throw error;
    }
  }

  static async createWalkIn(walkIn: WalkInRequest): Promise<QueueEntry> {
    try {
      const response = await fetchAPI(`${api.queue.entries}/walk-in`, {
        method: 'POST',
        body: JSON.stringify(walkIn)
      });
      
      if (!response) {
        throw new Error('Failed to create walk-in');
      }
      
      return response;
    } catch (error) {
      console.error('Error creating walk-in:', error);
      throw error;
    }
  }

  static async callPatient(queueId: number): Promise<{ message: string; ticket_number: string }> {
    try {
      const response = await fetchAPI(`${api.queue.entries}/${queueId}/call`, {
        method: 'POST'
      });
      
      if (!response) {
        throw new Error('Failed to call patient');
      }
      
      return response;
    } catch (error) {
      console.error('Error calling patient:', error);
      throw error;
    }
  }

  static async startService(queueId: number): Promise<{ message: string; ticket_number: string }> {
    try {
      const response = await fetchAPI(`${api.queue.entries}/${queueId}/start`, {
        method: 'POST'
      });
      
      if (!response) {
        throw new Error('Failed to start service');
      }
      
      return response;
    } catch (error) {
      console.error('Error starting service:', error);
      throw error;
    }
  }

  static async completeService(queueId: number): Promise<{ message: string; ticket_number: string }> {
    try {
      const response = await fetchAPI(`${api.queue.entries}/${queueId}/complete`, {
        method: 'POST'
      });
      
      if (!response) {
        throw new Error('Failed to complete service');
      }
      
      return response;
    } catch (error) {
      console.error('Error completing service:', error);
      throw error;
    }
  }

  static async dequeuePatient(queueId: number): Promise<{ message: string; ticket_number: string }> {
    try {
      const response = await fetchAPI(`${api.queue.entries}/${queueId}`, {
        method: 'DELETE'
      });
      
      if (!response) {
        throw new Error('Failed to dequeue patient');
      }
      
      return response;
    } catch (error) {
      console.error('Error dequeuing patient:', error);
      throw error;
    }
  }
}

