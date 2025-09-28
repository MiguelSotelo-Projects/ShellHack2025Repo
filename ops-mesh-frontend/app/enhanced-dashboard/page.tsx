'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { api, fetchAPI } from '@/lib/api';

interface Patient {
  id: number;
  first_name: string;
  last_name: string;
  phone: string;
  email: string;
  medical_record_number: string;
  created_at: string;
  status?: string;
}

interface QueueEntry {
  id: number;
  ticket_number: string;
  patient_id: number;
  queue_type: string;
  status: string;
  priority: string;
  estimated_wait_time: number;
  created_at: string;
  patient?: Patient;
}

interface AgentStatus {
  agent_id: string;
  status: string;
  last_heartbeat: string;
  capabilities: string[];
  running: boolean;
}

interface DashboardStats {
  total_patients: number;
  patients_served: number;
  queue_waiting: number;
  queue_in_progress: number;
  average_wait_time: number;
}

export default function EnhancedDashboardPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [queueEntries, setQueueEntries] = useState<QueueEntry[]>([]);
  const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  // Form states
  const [newPatient, setNewPatient] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    email: '',
    priority: 'medium'
  });

  const [patientStatusUpdate, setPatientStatusUpdate] = useState({
    patient_id: '',
    status: 'waiting'
  });

  const fetchPatients = async () => {
    try {
      const data = await fetchAPI(api.patients.list);
      setPatients(data.patients || []);
    } catch (error) {
      console.error('Failed to fetch patients:', error);
    }
  };

  const fetchQueueEntries = async () => {
    try {
      const data = await fetchAPI(api.queue.entries);
      setQueueEntries(data.queue_entries || []);
    } catch (error) {
      console.error('Failed to fetch queue entries:', error);
    }
  };

  const fetchAgentStatuses = async () => {
    try {
      const data = await fetchAPI(api.agents.status);
      // Transform the agents object into an array
      const agentsArray = data.agents ? Object.values(data.agents).map((agent: any) => ({
        agent_id: agent.agent_id,
        status: agent.running ? 'active' : 'inactive',
        last_heartbeat: new Date().toISOString(),
        capabilities: [], // We don't have capabilities in the current API
        running: agent.running
      })) : [];
      setAgentStatuses(agentsArray);
    } catch (error) {
      console.error('Failed to fetch agent statuses:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await fetchAPI(api.dashboard.stats);
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const createPatient = async () => {
    if (!newPatient.first_name || !newPatient.last_name) {
      alert('Please fill in required fields');
      return;
    }

    setLoading(true);
    try {
      await fetchAPI(api.patients.create, {
        method: 'POST',
        body: JSON.stringify(newPatient)
      });
      
      setNewPatient({ first_name: '', last_name: '', phone: '', email: '', priority: 'medium' });
      await fetchPatients();
      await fetchQueueEntries();
      await fetchStats();
    } catch (error) {
      console.error('Failed to create patient:', error);
    } finally {
      setLoading(false);
    }
  };

  const callNextPatient = async () => {
    setLoading(true);
    try {
      await fetchAPI(api.queue.callNext, { method: 'POST' });
      await fetchQueueEntries();
      await fetchStats();
    } catch (error) {
      console.error('Failed to call next patient:', error);
    } finally {
      setLoading(false);
    }
  };

  const updatePatientStatus = async (patientId: string, status: string) => {
    setLoading(true);
    try {
      await fetchAPI(api.patients.update(patientId), {
        method: 'PUT',
        body: JSON.stringify({ status })
      });
      await fetchPatients();
      await fetchQueueEntries();
      await fetchStats();
    } catch (error) {
      console.error('Failed to update patient status:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateQueueEntryStatus = async (entryId: number, status: string) => {
    setLoading(true);
    try {
      await fetchAPI(api.queue.updateStatus(entryId.toString()), {
        method: 'PUT',
        body: JSON.stringify({ status })
      });
      await fetchQueueEntries();
      await fetchStats();
    } catch (error) {
      console.error('Failed to update queue entry status:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
    fetchQueueEntries();
    fetchAgentStatuses();
    fetchStats();
    
    // Refresh data every 5 seconds
    const interval = setInterval(() => {
      fetchPatients();
      fetchQueueEntries();
      fetchAgentStatuses();
      fetchStats();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'served':
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'waiting':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'urgent':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Enhanced Hospital Dashboard</h1>
        <p className="text-gray-600">
          Real-time patient management, queue monitoring, and agent status
        </p>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Patients</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_patients}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Patients Served</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.patients_served}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Queue Waiting</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{stats.queue_waiting}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Avg Wait Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.average_wait_time} min</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Agent Status */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Agent Status</CardTitle>
          <CardDescription>Real-time status of all A2A agents</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {agentStatuses.map((agent) => (
              <div key={agent.agent_id} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <div className="font-medium">{agent.agent_id.replace('_', ' ')}</div>
                  <div className="text-sm text-gray-500">
                    {agent.capabilities.length} capabilities
                  </div>
                </div>
                <Badge className={getStatusColor(agent.status)}>
                  {agent.running ? 'ACTIVE' : 'INACTIVE'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="patients" className="space-y-4">
        <TabsList>
          <TabsTrigger value="patients">Patient Management</TabsTrigger>
          <TabsTrigger value="queue">Queue Management</TabsTrigger>
          <TabsTrigger value="add-patient">Add Patient</TabsTrigger>
        </TabsList>

        <TabsContent value="patients" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Patient List</CardTitle>
              <CardDescription>Manage patient status and information</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {patients.map((patient) => (
                  <div key={patient.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium">
                        {patient.first_name} {patient.last_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        MRN: {patient.medical_record_number} | Phone: {patient.phone}
                      </div>
                      <div className="text-xs text-gray-400">
                        Registered: {new Date(patient.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Select
                        value={patient.status || 'waiting'}
                        onValueChange={(value) => updatePatientStatus(patient.id.toString(), value)}
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="waiting">Waiting</SelectItem>
                          <SelectItem value="in_progress">In Progress</SelectItem>
                          <SelectItem value="served">Served</SelectItem>
                          <SelectItem value="cancelled">Cancelled</SelectItem>
                        </SelectContent>
                      </Select>
                      <Badge className={getStatusColor(patient.status || 'waiting')}>
                        {patient.status || 'waiting'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="queue" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Queue Management</CardTitle>
              <CardDescription>Monitor and manage patient queue</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <Button 
                  onClick={callNextPatient} 
                  disabled={loading}
                  className="w-full"
                >
                  {loading ? 'Processing...' : 'Call Next Patient'}
                </Button>
              </div>
              
              <div className="space-y-4">
                {queueEntries.map((entry) => (
                  <div key={entry.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium">
                        Ticket: {entry.ticket_number}
                      </div>
                      <div className="text-sm text-gray-500">
                        Patient: {entry.patient?.first_name} {entry.patient?.last_name}
                      </div>
                      <div className="text-xs text-gray-400">
                        Type: {entry.queue_type} | Wait: {entry.estimated_wait_time} min
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getPriorityColor(entry.priority)}>
                        {entry.priority}
                      </Badge>
                      <Select
                        value={entry.status}
                        onValueChange={(value) => updateQueueEntryStatus(entry.id, value)}
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="waiting">Waiting</SelectItem>
                          <SelectItem value="called">Called</SelectItem>
                          <SelectItem value="in_progress">In Progress</SelectItem>
                          <SelectItem value="completed">Completed</SelectItem>
                          <SelectItem value="cancelled">Cancelled</SelectItem>
                        </SelectContent>
                      </Select>
                      <Badge className={getStatusColor(entry.status)}>
                        {entry.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="add-patient" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Add New Patient</CardTitle>
              <CardDescription>Register a new patient and add to queue</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="first_name">First Name *</Label>
                    <Input
                      id="first_name"
                      value={newPatient.first_name}
                      onChange={(e) => setNewPatient(prev => ({ ...prev, first_name: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="last_name">Last Name *</Label>
                    <Input
                      id="last_name"
                      value={newPatient.last_name}
                      onChange={(e) => setNewPatient(prev => ({ ...prev, last_name: e.target.value }))}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    value={newPatient.phone}
                    onChange={(e) => setNewPatient(prev => ({ ...prev, phone: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={newPatient.email}
                    onChange={(e) => setNewPatient(prev => ({ ...prev, email: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="priority">Priority</Label>
                  <Select value={newPatient.priority} onValueChange={(value) => setNewPatient(prev => ({ ...prev, priority: value }))}>
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
                  onClick={createPatient} 
                  disabled={loading}
                  className="w-full"
                >
                  {loading ? 'Creating...' : 'Create Patient & Add to Queue'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
