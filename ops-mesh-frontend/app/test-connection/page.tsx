'use client';

import { useState, useEffect } from 'react';
import { DashboardService } from '@/lib/services/dashboardService';
import { AppointmentService } from '@/lib/services/appointmentService';
import { QueueService } from '@/lib/services/queueService';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

interface TestResult {
  test: string;
  status: 'success' | 'error' | 'pending';
  message: string;
  data?: any;
  timestamp: string;
}

export default function TestConnectionPage() {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const addTestResult = (test: string, status: 'success' | 'error' | 'pending', message: string, data?: any) => {
    const result: TestResult = {
      test,
      status,
      message,
      data,
      timestamp: new Date().toLocaleTimeString()
    };
    setTestResults(prev => [...prev, result]);
  };

  const runAllTests = async () => {
    setIsRunning(true);
    setTestResults([]);

    // Test 1: Backend Health Check
    addTestResult('Backend Health', 'pending', 'Checking backend health...');
    try {
      const response = await fetch('http://localhost:8000/health');
      const data = await response.json();
      if (response.ok) {
        addTestResult('Backend Health', 'success', 'Backend is healthy', data);
      } else {
        addTestResult('Backend Health', 'error', `Backend health check failed: ${response.status}`);
      }
    } catch (error) {
      addTestResult('Backend Health', 'error', `Backend connection failed: ${error}`);
    }

    // Test 2: Dashboard Stats
    addTestResult('Dashboard Stats', 'pending', 'Fetching dashboard statistics...');
    try {
      const stats = await DashboardService.getDashboardStats();
      addTestResult('Dashboard Stats', 'success', 'Dashboard stats retrieved successfully', stats);
    } catch (error) {
      addTestResult('Dashboard Stats', 'error', `Dashboard stats failed: ${error}`);
    }

    // Test 3: Appointments List
    addTestResult('Appointments List', 'pending', 'Fetching appointments...');
    try {
      const appointments = await AppointmentService.getAppointments();
      addTestResult('Appointments List', 'success', `Retrieved ${appointments.length} appointments`, appointments.slice(0, 3));
    } catch (error) {
      addTestResult('Appointments List', 'error', `Appointments fetch failed: ${error}`);
    }

    // Test 4: Queue Entries
    addTestResult('Queue Entries', 'pending', 'Fetching queue entries...');
    try {
      const queueEntries = await QueueService.getQueueEntries();
      addTestResult('Queue Entries', 'success', `Retrieved ${queueEntries.length} queue entries`, queueEntries.slice(0, 3));
    } catch (error) {
      addTestResult('Queue Entries', 'error', `Queue entries fetch failed: ${error}`);
    }

    // Test 5: Create Test Patient
    addTestResult('Create Patient', 'pending', 'Creating test patient...');
    try {
      const patientData = {
        first_name: 'Test',
        last_name: 'Connection',
        date_of_birth: '1990-01-01T00:00:00',
        phone: '555-TEST',
        email: 'test.connection@example.com'
      };
      const response = await fetch('http://localhost:8000/api/v1/patients/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData)
      });
      const patient = await response.json();
      if (response.ok) {
        addTestResult('Create Patient', 'success', 'Test patient created successfully', patient);
      } else {
        addTestResult('Create Patient', 'error', `Patient creation failed: ${response.status}`);
      }
    } catch (error) {
      addTestResult('Create Patient', 'error', `Patient creation failed: ${error}`);
    }

    // Test 6: Create Test Appointment
    addTestResult('Create Appointment', 'pending', 'Creating test appointment...');
    try {
      const appointmentData = {
        patient_id: 1, // Assuming patient ID 1 exists
        appointment_type: 'consultation',
        appointment_date: '2025-10-01T10:00:00',
        provider: 'Dr. Test',
        notes: 'Frontend connection test'
      };
      const response = await fetch('http://localhost:8000/api/v1/appointments/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(appointmentData)
      });
      const appointment = await response.json();
      if (response.ok) {
        addTestResult('Create Appointment', 'success', 'Test appointment created successfully', appointment);
      } else {
        addTestResult('Create Appointment', 'error', `Appointment creation failed: ${response.status}`);
      }
    } catch (error) {
      addTestResult('Create Appointment', 'error', `Appointment creation failed: ${error}`);
    }

    // Test 7: Walk-in Registration
    addTestResult('Walk-in Registration', 'pending', 'Testing walk-in registration...');
    try {
      const walkInData = {
        patient: {
          first_name: 'WalkIn',
          last_name: 'Test',
          date_of_birth: '1985-05-15T00:00:00',
          phone: '555-WALK',
          email: 'walkin.test@example.com'
        },
        reason: 'Frontend connection test',
        priority: 'medium'
      };
      const response = await fetch('http://localhost:8000/api/v1/walkin/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(walkInData)
      });
      const walkIn = await response.json();
      if (response.ok) {
        addTestResult('Walk-in Registration', 'success', 'Walk-in registration successful', walkIn);
      } else {
        addTestResult('Walk-in Registration', 'error', `Walk-in registration failed: ${response.status}`);
      }
    } catch (error) {
      addTestResult('Walk-in Registration', 'error', `Walk-in registration failed: ${error}`);
    }

    // Test 8: WebSocket Connection
    addTestResult('WebSocket Connection', 'pending', 'Testing WebSocket connection...');
    try {
      const ws = new WebSocket('ws://localhost:8000/api/v1/ws/dashboard');
      const timeout = setTimeout(() => {
        ws.close();
        addTestResult('WebSocket Connection', 'error', 'WebSocket connection timeout');
      }, 5000);

      ws.onopen = () => {
        clearTimeout(timeout);
        addTestResult('WebSocket Connection', 'success', 'WebSocket connection established');
        ws.close();
      };

      ws.onerror = () => {
        clearTimeout(timeout);
        addTestResult('WebSocket Connection', 'error', 'WebSocket connection failed');
      };
    } catch (error) {
      addTestResult('WebSocket Connection', 'error', `WebSocket test failed: ${error}`);
    }

    setIsRunning(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-100 text-green-800 border-green-200';
      case 'error': return 'bg-red-100 text-red-800 border-red-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'pending': return '⏳';
      default: return '❓';
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Frontend-Backend Connection Test</h1>
        <p className="text-gray-600">
          Comprehensive test suite to verify the connection between the frontend and backend systems.
        </p>
      </div>

      <div className="mb-6">
        <Button 
          onClick={runAllTests} 
          disabled={isRunning}
          className="w-full"
        >
          {isRunning ? 'Running Tests...' : 'Run All Connection Tests'}
        </Button>
      </div>

      <div className="grid gap-4">
        {testResults.map((result, index) => (
          <Card key={index} className="border-l-4 border-l-blue-500">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  {getStatusIcon(result.status)} {result.test}
                </CardTitle>
                <Badge className={getStatusColor(result.status)}>
                  {result.status.toUpperCase()}
                </Badge>
              </div>
              <CardDescription>
                {result.message} • {result.timestamp}
              </CardDescription>
            </CardHeader>
            {result.data && (
              <CardContent>
                <Separator className="mb-3" />
                <div className="bg-gray-50 p-3 rounded-md">
                  <h4 className="font-medium mb-2">Response Data:</h4>
                  <pre className="text-sm overflow-auto max-h-40">
                    {JSON.stringify(result.data, null, 2)}
                  </pre>
                </div>
              </CardContent>
            )}
          </Card>
        ))}
      </div>

      {testResults.length > 0 && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Test Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {testResults.filter(r => r.status === 'success').length}
                </div>
                <div className="text-sm text-gray-600">Successful</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-600">
                  {testResults.filter(r => r.status === 'error').length}
                </div>
                <div className="text-sm text-gray-600">Failed</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {testResults.length}
                </div>
                <div className="text-sm text-gray-600">Total Tests</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
