import { apiClient } from '../api';

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
    const response = await apiClient.get<AppointmentResponse[]>('/appointments/');
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    return response.data || [];
  }

  static async getAppointmentById(id: number): Promise<Appointment> {
    const response = await apiClient.get<Appointment>(`/appointments/${id}`);
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    if (!response.data) {
      throw new Error('Appointment not found');
    }
    
    return response.data;
  }

  static async checkInAppointment(checkIn: AppointmentCheckIn): Promise<Appointment> {
    const response = await apiClient.post<Appointment>('/appointments/check-in', checkIn);
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    if (!response.data) {
      throw new Error('Check-in failed');
    }
    
    return response.data;
  }

  static async getAppointmentByCode(confirmationCode: string): Promise<Appointment> {
    const response = await apiClient.get<Appointment>(`/appointments/code/${confirmationCode}`);
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    if (!response.data) {
      throw new Error('Appointment not found');
    }
    
    return response.data;
  }
}

