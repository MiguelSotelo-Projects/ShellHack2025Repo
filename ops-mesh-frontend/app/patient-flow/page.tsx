'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

interface PatientData {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  phone: string;
  email: string;
}

interface AppointmentData {
  patient_id: number;
  appointment_type: string;
  appointment_date: string;
  provider: string;
  notes: string;
}

interface WalkInData {
  patient: PatientData;
  reason: string;
  priority: string;
}

export default function PatientFlowPage() {
  const [activeTab, setActiveTab] = useState<'appointment' | 'walkin' | 'checkin'>('appointment');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Appointment form state
  const [appointmentForm, setAppointmentForm] = useState<AppointmentData>({
    patient_id: 1,
    appointment_type: 'consultation',
    appointment_date: '',
    provider: '',
    notes: ''
  });

  // Walk-in form state
  const [walkInForm, setWalkInForm] = useState<WalkInData>({
    patient: {
      first_name: '',
      last_name: '',
      date_of_birth: '',
      phone: '',
      email: ''
    },
    reason: '',
    priority: 'medium'
  });

  // Check-in form state
  const [checkInForm, setCheckInForm] = useState({
    confirmation_code: '',
    last_name: ''
  });

  const handleAppointmentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/appointments/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(appointmentForm)
      });

      const data = await response.json();
      if (response.ok) {
        setResult({ type: 'appointment', data });
      } else {
        setError(`Appointment creation failed: ${data.detail || response.statusText}`);
      }
    } catch (err) {
      setError(`Network error: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const handleWalkInSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/walkin/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(walkInForm)
      });

      const data = await response.json();
      if (response.ok) {
        setResult({ type: 'walkin', data });
      } else {
        setError(`Walk-in registration failed: ${data.detail || response.statusText}`);
      }
    } catch (err) {
      setError(`Network error: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckInSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/appointments/check-in', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(checkInForm)
      });

      const data = await response.json();
      if (response.ok) {
        setResult({ type: 'checkin', data });
      } else {
        setError(`Check-in failed: ${data.detail || response.statusText}`);
      }
    } catch (err) {
      setError(`Network error: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const getResultBadge = (type: string) => {
    switch (type) {
      case 'appointment': return <Badge className="bg-blue-100 text-blue-800">Appointment Created</Badge>;
      case 'walkin': return <Badge className="bg-green-100 text-green-800">Walk-in Registered</Badge>;
      case 'checkin': return <Badge className="bg-purple-100 text-purple-800">Checked In</Badge>;
      default: return <Badge>Success</Badge>;
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Patient Flow Management</h1>
        <p className="text-gray-600">
          Test the complete patient flow from appointment creation to check-in
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        <Button
          variant={activeTab === 'appointment' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('appointment')}
          className="flex-1"
        >
          📅 Create Appointment
        </Button>
        <Button
          variant={activeTab === 'walkin' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('walkin')}
          className="flex-1"
        >
          🚶 Walk-in Registration
        </Button>
        <Button
          variant={activeTab === 'checkin' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('checkin')}
          className="flex-1"
        >
          ✅ Check-in
        </Button>
      </div>

      {/* Appointment Creation Form */}
      {activeTab === 'appointment' && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Appointment</CardTitle>
            <CardDescription>
              Schedule a new appointment for a patient
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleAppointmentSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="patient_id">Patient ID</Label>
                  <Input
                    id="patient_id"
                    type="number"
                    value={appointmentForm.patient_id}
                    onChange={(e) => setAppointmentForm(prev => ({ ...prev, patient_id: parseInt(e.target.value) }))}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="appointment_type">Appointment Type</Label>
                  <Select
                    value={appointmentForm.appointment_type}
                    onValueChange={(value) => setAppointmentForm(prev => ({ ...prev, appointment_type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="consultation">Consultation</SelectItem>
                      <SelectItem value="routine">Routine</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                      <SelectItem value="follow_up">Follow-up</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="appointment_date">Appointment Date & Time</Label>
                  <Input
                    id="appointment_date"
                    type="datetime-local"
                    value={appointmentForm.appointment_date}
                    onChange={(e) => setAppointmentForm(prev => ({ ...prev, appointment_date: e.target.value }))}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="provider">Provider</Label>
                  <Input
                    id="provider"
                    value={appointmentForm.provider}
                    onChange={(e) => setAppointmentForm(prev => ({ ...prev, provider: e.target.value }))}
                    placeholder="Dr. Smith"
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={appointmentForm.notes}
                  onChange={(e) => setAppointmentForm(prev => ({ ...prev, notes: e.target.value }))}
                  placeholder="Additional notes for the appointment"
                />
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Creating Appointment...' : 'Create Appointment'}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Walk-in Registration Form */}
      {activeTab === 'walkin' && (
        <Card>
          <CardHeader>
            <CardTitle>Walk-in Patient Registration</CardTitle>
            <CardDescription>
              Register a walk-in patient and add them to the queue
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleWalkInSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="first_name">First Name</Label>
                  <Input
                    id="first_name"
                    value={walkInForm.patient.first_name}
                    onChange={(e) => setWalkInForm(prev => ({
                      ...prev,
                      patient: { ...prev.patient, first_name: e.target.value }
                    }))}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="last_name">Last Name</Label>
                  <Input
                    id="last_name"
                    value={walkInForm.patient.last_name}
                    onChange={(e) => setWalkInForm(prev => ({
                      ...prev,
                      patient: { ...prev.patient, last_name: e.target.value }
                    }))}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="date_of_birth">Date of Birth</Label>
                  <Input
                    id="date_of_birth"
                    type="date"
                    value={walkInForm.patient.date_of_birth}
                    onChange={(e) => setWalkInForm(prev => ({
                      ...prev,
                      patient: { ...prev.patient, date_of_birth: e.target.value + 'T00:00:00' }
                    }))}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    value={walkInForm.patient.phone}
                    onChange={(e) => setWalkInForm(prev => ({
                      ...prev,
                      patient: { ...prev.patient, phone: e.target.value }
                    }))}
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={walkInForm.patient.email}
                  onChange={(e) => setWalkInForm(prev => ({
                    ...prev,
                    patient: { ...prev.patient, email: e.target.value }
                  }))}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="reason">Reason for Visit</Label>
                  <Input
                    id="reason"
                    value={walkInForm.reason}
                    onChange={(e) => setWalkInForm(prev => ({ ...prev, reason: e.target.value }))}
                    placeholder="e.g., Chest pain, fever, etc."
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="priority">Priority</Label>
                  <Select
                    value={walkInForm.priority}
                    onValueChange={(value) => setWalkInForm(prev => ({ ...prev, priority: value }))}
                  >
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
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Registering Walk-in...' : 'Register Walk-in Patient'}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Check-in Form */}
      {activeTab === 'checkin' && (
        <Card>
          <CardHeader>
            <CardTitle>Patient Check-in</CardTitle>
            <CardDescription>
              Check in a patient using their confirmation code
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCheckInSubmit} className="space-y-4">
              <div>
                <Label htmlFor="confirmation_code">Confirmation Code</Label>
                <Input
                  id="confirmation_code"
                  value={checkInForm.confirmation_code}
                  onChange={(e) => setCheckInForm(prev => ({ ...prev, confirmation_code: e.target.value }))}
                  placeholder="e.g., ABCD-1234"
                  required
                />
              </div>

              <div>
                <Label htmlFor="last_name">Last Name</Label>
                <Input
                  id="last_name"
                  value={checkInForm.last_name}
                  onChange={(e) => setCheckInForm(prev => ({ ...prev, last_name: e.target.value }))}
                  placeholder="Patient's last name"
                  required
                />
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Checking In...' : 'Check In Patient'}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {(result || error) && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {result ? getResultBadge(result.type) : <Badge className="bg-red-100 text-red-800">Error</Badge>}
              {result ? 'Operation Successful' : 'Operation Failed'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
                <p className="text-red-800">{error}</p>
              </div>
            )}
            {result && (
              <div className="bg-green-50 border border-green-200 rounded-md p-4">
                <h4 className="font-medium text-green-800 mb-2">Response Data:</h4>
                <pre className="text-sm text-green-700 overflow-auto">
                  {JSON.stringify(result.data, null, 2)}
                </pre>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
