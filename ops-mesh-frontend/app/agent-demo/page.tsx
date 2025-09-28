'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { api, fetchAPI } from '@/lib/api';
import AgentStatusVisual from '@/components/AgentStatusVisual';

interface AgentStatus {
  agent_id: string;
  status: string;
  last_heartbeat: string;
  capabilities: string[];
}

interface WorkflowResult {
  success: boolean;
  message: string;
  workflow_id: string;
}

interface LogEntry {
  timestamp: string;
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  agent?: string;
}

export default function AgentDemoPage() {
  const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>([]);
  const [discoveryInfo, setDiscoveryInfo] = useState<any>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState<WorkflowResult[]>([]);

  // Form states
  const [patientData, setPatientData] = useState({
    first_name: 'John',
    last_name: 'Doe',
    phone: '555-0123',
    email: 'john.doe@example.com',
    priority: 'medium'
  });

  const [appointmentData, setAppointmentData] = useState({
    patient_id: '1',
    provider: 'Dr. Smith',
    appointment_time: '2024-01-15T10:00:00',
    type: 'routine',
    reason: 'Annual checkup'
  });

  const [queueData, setQueueData] = useState({
    action: 'get_queue_status'
  });

  const [emergencyData, setEmergencyData] = useState({
    patient_id: '1',
    emergency_type: 'cardiac',
    severity: 'critical'
  });

  const addLog = (level: LogEntry['level'], message: string, agent?: string) => {
    const newLog: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      level,
      message,
      agent
    };
    setLogs(prev => [newLog, ...prev.slice(0, 49)]); // Keep last 50 logs
  };

  const fetchAgentStatus = async () => {
    try {
      const data = await fetchAPI(api.agents.status);
      
      if (data.success) {
        setAgentStatuses(data.agents);
        addLog('info', `Retrieved status for ${data.total_agents} agents`);
      }
    } catch (error) {
      addLog('error', `Failed to fetch agent status: ${error}`);
    }
  };

  const fetchDiscoveryInfo = async () => {
    try {
      const data = await fetchAPI(api.agents.discovery);
      
      if (data.success) {
        setDiscoveryInfo(data.discovery);
        addLog('info', 'Retrieved agent discovery information');
      }
    } catch (error) {
      addLog('error', `Failed to fetch discovery info: ${error}`);
    }
  };

  const testAgentCommunication = async () => {
    setLoading(true);
    addLog('info', 'Testing agent-to-agent communication...');
    
    try {
      const data = await fetchAPI(api.agents.testCommunication, { method: 'GET' });
      
      if (data.success) {
        addLog('success', 'Agent communication test passed');
        setTestResults(prev => [...prev, data]);
      } else {
        addLog('error', 'Agent communication test failed');
      }
    } catch (error) {
      addLog('error', `Communication test failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const startPatientRegistrationWorkflow = async () => {
    setLoading(true);
    addLog('info', 'Starting patient registration workflow...', 'FrontDesk Agent');
    
    try {
      const data = await fetchAPI(api.agents.workflows.patientRegistration, {
        method: 'POST',
        body: JSON.stringify(patientData)
      });
      
      if (data.success) {
        addLog('success', `Patient registration workflow started: ${data.workflow_id}`);
        setTestResults(prev => [...prev, data]);
      } else {
        addLog('error', 'Failed to start patient registration workflow');
      }
    } catch (error) {
      addLog('error', `Patient registration failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const startAppointmentSchedulingWorkflow = async () => {
    setLoading(true);
    addLog('info', 'Starting appointment scheduling workflow...', 'Appointment Agent');
    
    try {
      const response = await fetch('/api/v1/agents/workflow/appointment-scheduling', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(appointmentData)
      });
      const data = await response.json();
      
      if (data.success) {
        addLog('success', `Appointment scheduling workflow started: ${data.workflow_id}`);
        setTestResults(prev => [...prev, data]);
      } else {
        addLog('error', 'Failed to start appointment scheduling workflow');
      }
    } catch (error) {
      addLog('error', `Appointment scheduling failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const startQueueManagementWorkflow = async () => {
    setLoading(true);
    addLog('info', 'Starting queue management workflow...', 'Queue Agent');
    
    try {
      const response = await fetch('/api/v1/agents/workflow/queue-management', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(queueData)
      });
      const data = await response.json();
      
      if (data.success) {
        addLog('success', `Queue management workflow started: ${data.workflow_id}`);
        setTestResults(prev => [...prev, data]);
      } else {
        addLog('error', 'Failed to start queue management workflow');
      }
    } catch (error) {
      addLog('error', `Queue management failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const startEmergencyCoordinationWorkflow = async () => {
    setLoading(true);
    addLog('info', 'Starting emergency coordination workflow...', 'Orchestrator Agent');
    
    try {
      const response = await fetch('/api/v1/agents/workflow/emergency-coordination', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(emergencyData)
      });
      const data = await response.json();
      
      if (data.success) {
        addLog('success', `Emergency coordination workflow started: ${data.workflow_id}`);
        setTestResults(prev => [...prev, data]);
      } else {
        addLog('error', 'Failed to start emergency coordination workflow');
      }
    } catch (error) {
      addLog('error', `Emergency coordination failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgentStatus();
    fetchDiscoveryInfo();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'bg-green-100 text-green-800 border-green-200';
      case 'inactive': return 'bg-red-100 text-red-800 border-red-200';
      case 'starting': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getLogColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'success': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-blue-600';
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">A2A Protocol Demo</h1>
        <p className="text-gray-600">
          Interactive demonstration of Agent-to-Agent communication and workflow orchestration
        </p>
      </div>

      {/* Visual Agent Status */}
      <AgentStatusVisual />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Discovery Information */}
        <Card>
          <CardHeader>
            <CardTitle>Discovery Service</CardTitle>
            <CardDescription>Agent discovery and registration info</CardDescription>
          </CardHeader>
          <CardContent>
            {discoveryInfo ? (
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Total Agents:</span>
                  <span className="text-sm">{discoveryInfo.discovery_stats?.total_agents || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Available Agents:</span>
                  <span className="text-sm">{discoveryInfo.available_agents?.length || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Service Status:</span>
                  <Badge className="bg-green-100 text-green-800">Active</Badge>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No discovery information available</p>
            )}
            <div className="mt-4">
              <Button onClick={fetchDiscoveryInfo} variant="outline" size="sm">
                Refresh Discovery
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Workflow Testing */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Patient Registration Workflow */}
        <Card>
          <CardHeader>
            <CardTitle>Patient Registration Workflow</CardTitle>
            <CardDescription>Test FrontDesk → Queue → Notification agent communication</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Label htmlFor="first_name">First Name</Label>
                  <Input
                    id="first_name"
                    value={patientData.first_name}
                    onChange={(e) => setPatientData(prev => ({ ...prev, first_name: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="last_name">Last Name</Label>
                  <Input
                    id="last_name"
                    value={patientData.last_name}
                    onChange={(e) => setPatientData(prev => ({ ...prev, last_name: e.target.value }))}
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  value={patientData.phone}
                  onChange={(e) => setPatientData(prev => ({ ...prev, phone: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  value={patientData.email}
                  onChange={(e) => setPatientData(prev => ({ ...prev, email: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="priority">Priority</Label>
                <Select value={patientData.priority} onValueChange={(value) => setPatientData(prev => ({ ...prev, priority: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="urgent">Urgent</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button 
                onClick={startPatientRegistrationWorkflow} 
                disabled={loading}
                className="w-full"
              >
                {loading ? 'Processing...' : 'Start Registration Workflow'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Appointment Scheduling Workflow */}
        <Card>
          <CardHeader>
            <CardTitle>Appointment Scheduling Workflow</CardTitle>
            <CardDescription>Test Appointment → Notification agent communication</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="patient_id">Patient ID</Label>
                <Input
                  id="patient_id"
                  value={appointmentData.patient_id}
                  onChange={(e) => setAppointmentData(prev => ({ ...prev, patient_id: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="provider">Provider</Label>
                <Input
                  id="provider"
                  value={appointmentData.provider}
                  onChange={(e) => setAppointmentData(prev => ({ ...prev, provider: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="appointment_time">Appointment Time</Label>
                <Input
                  id="appointment_time"
                  type="datetime-local"
                  value={appointmentData.appointment_time}
                  onChange={(e) => setAppointmentData(prev => ({ ...prev, appointment_time: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="type">Type</Label>
                <Select value={appointmentData.type} onValueChange={(value) => setAppointmentData(prev => ({ ...prev, type: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="routine">Routine</SelectItem>
                    <SelectItem value="urgent">Urgent</SelectItem>
                    <SelectItem value="follow_up">Follow-up</SelectItem>
                    <SelectItem value="consultation">Consultation</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="reason">Reason</Label>
                <Textarea
                  id="reason"
                  value={appointmentData.reason}
                  onChange={(e) => setAppointmentData(prev => ({ ...prev, reason: e.target.value }))}
                />
              </div>
              <Button 
                onClick={startAppointmentSchedulingWorkflow} 
                disabled={loading}
                className="w-full"
              >
                {loading ? 'Processing...' : 'Start Scheduling Workflow'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        {/* Queue Management */}
        <Card>
          <CardHeader>
            <CardTitle>Queue Management</CardTitle>
            <CardDescription>Test Queue Agent operations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="queue_action">Action</Label>
                <Select value={queueData.action} onValueChange={(value) => setQueueData(prev => ({ ...prev, action: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="get_queue_status">Get Queue Status</SelectItem>
                    <SelectItem value="call_next_patient">Call Next Patient</SelectItem>
                    <SelectItem value="add_to_queue">Add to Queue</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button 
                onClick={startQueueManagementWorkflow} 
                disabled={loading}
                className="w-full"
              >
                {loading ? 'Processing...' : 'Execute Queue Action'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Emergency Coordination */}
        <Card>
          <CardHeader>
            <CardTitle>Emergency Coordination</CardTitle>
            <CardDescription>Test Orchestrator Agent emergency response</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="emergency_patient_id">Patient ID</Label>
                <Input
                  id="emergency_patient_id"
                  value={emergencyData.patient_id}
                  onChange={(e) => setEmergencyData(prev => ({ ...prev, patient_id: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="emergency_type">Emergency Type</Label>
                <Select value={emergencyData.emergency_type} onValueChange={(value) => setEmergencyData(prev => ({ ...prev, emergency_type: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="cardiac">Cardiac</SelectItem>
                    <SelectItem value="respiratory">Respiratory</SelectItem>
                    <SelectItem value="trauma">Trauma</SelectItem>
                    <SelectItem value="neurological">Neurological</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="severity">Severity</Label>
                <Select value={emergencyData.severity} onValueChange={(value) => setEmergencyData(prev => ({ ...prev, severity: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button 
                onClick={startEmergencyCoordinationWorkflow} 
                disabled={loading}
                className="w-full bg-red-600 hover:bg-red-700"
              >
                {loading ? 'Processing...' : 'Trigger Emergency Response'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="border-t my-6"></div>

      {/* Communication Test */}
      <Card>
        <CardHeader>
          <CardTitle>Agent Communication Test</CardTitle>
          <CardDescription>Test basic agent-to-agent communication</CardDescription>
        </CardHeader>
        <CardContent>
          <Button 
            onClick={testAgentCommunication} 
            disabled={loading}
            className="w-full"
          >
            {loading ? 'Testing...' : 'Test Agent Communication'}
          </Button>
        </CardContent>
      </Card>

      {/* Activity Log */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Activity Log</CardTitle>
          <CardDescription>Real-time A2A protocol activity</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {logs.map((log, index) => (
              <div key={index} className="flex items-start gap-2 text-sm">
                <span className="text-gray-400 font-mono">{log.timestamp}</span>
                <span className={`font-medium ${getLogColor(log.level)}`}>
                  [{log.level.toUpperCase()}]
                </span>
                {log.agent && (
                  <Badge variant="outline" className="text-xs">
                    {log.agent}
                  </Badge>
                )}
                <span className="text-gray-700">{log.message}</span>
              </div>
            ))}
            {logs.length === 0 && (
              <p className="text-gray-500 text-center py-4">No activity yet. Start a workflow to see A2A protocol in action!</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Test Results */}
      {testResults.length > 0 && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Workflow Results</CardTitle>
            <CardDescription>Results from executed workflows</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {testResults.map((result, index) => (
                <div key={index} className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{result.message}</div>
                      <div className="text-sm text-gray-500">ID: {result.workflow_id}</div>
                    </div>
                    <Badge className={result.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {result.success ? 'SUCCESS' : 'FAILED'}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
