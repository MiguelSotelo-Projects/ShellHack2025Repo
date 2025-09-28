// API configuration and utilities

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  baseUrl: API_BASE_URL,
  
  // Agent endpoints
  agents: {
    status: `${API_BASE_URL}/api/v1/agents/status`,
    discovery: `${API_BASE_URL}/api/v1/agents/discovery`,
    testCommunication: `${API_BASE_URL}/api/v1/agents/test-communication`,
    workflows: {
      patientRegistration: `${API_BASE_URL}/api/v1/agents/workflow/patient-registration`,
      appointmentScheduling: `${API_BASE_URL}/api/v1/agents/workflow/appointment-scheduling`,
      queueManagement: `${API_BASE_URL}/api/v1/agents/workflow/queue-management`,
      emergencyCoordination: `${API_BASE_URL}/api/v1/agents/workflow/emergency-coordination`,
    }
  },
  
  // Patient endpoints
  patients: {
    list: `${API_BASE_URL}/api/v1/patients/list`,
    create: `${API_BASE_URL}/api/v1/patients/create`,
    update: (id: string) => `${API_BASE_URL}/api/v1/patients/${id}`,
    get: (id: string) => `${API_BASE_URL}/api/v1/patients/${id}`,
  },
  
  // Queue endpoints
  queue: {
    status: `${API_BASE_URL}/api/v1/queue/status`,
    entries: `${API_BASE_URL}/api/v1/queue/entries`,
    callNext: `${API_BASE_URL}/api/v1/queue/call-next`,
    updateStatus: (id: string) => `${API_BASE_URL}/api/v1/queue/entries/${id}/status`,
  },
  
  // Dashboard endpoints
  dashboard: {
    stats: `${API_BASE_URL}/api/v1/dashboard/stats`,
    activity: `${API_BASE_URL}/api/v1/dashboard/activity`,
  }
};

export async function fetchAPI(url: string, options: RequestInit = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}