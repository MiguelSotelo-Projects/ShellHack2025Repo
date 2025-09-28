import { api, fetchAPI } from '../api';

export interface Appointment {
  id: number;
  confirmation_code: string;
  status: 'scheduled' | 'confirmed' | 'checked_in' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';
  scheduled_time: string;
  provider_name: string;
  patient_name: string;
  reason?: string;
}

export interface AppointmentCheckIn {
  confirmation_code: string;
  last_name: string;
}

export interface AppointmentResponse {
  id: number;
  confirmation_code: string;
  status: string;
  scheduled_time: string;
  provider_name: string;
  patient_name: string;
  reason?: string;
}

export class AppointmentService {
  static async getAppointments(): Promise<Appointment[]> {
    try {
      // For now, return empty array since we don't have appointments endpoint yet
      return [];
    } catch (error) {
      console.error('Error fetching appointments:', error);
      throw error;
    }
  }

  static async getAppointmentById(id: number): Promise<Appointment> {
    try {
      // For now, throw error since we don't have appointments endpoint yet
      throw new Error('Appointment service not implemented yet');
    } catch (error) {
      console.error('Error fetching appointment:', error);
      throw error;
    }
  }

  static async checkInAppointment(checkIn: AppointmentCheckIn): Promise<Appointment> {
    try {
      // For now, throw error since we don't have appointments endpoint yet
      throw new Error('Appointment check-in not implemented yet');
    } catch (error) {
      console.error('Error checking in appointment:', error);
      throw error;
    }
  }

  static async getAppointmentByCode(confirmationCode: string): Promise<Appointment> {
    try {
      // For now, throw error since we don't have appointments endpoint yet
      throw new Error('Appointment lookup not implemented yet');
    } catch (error) {
      console.error('Error fetching appointment by code:', error);
      throw error;
    }
  }
}

