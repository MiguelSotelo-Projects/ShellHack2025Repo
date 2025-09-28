'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Bot, 
  Settings, 
  Play, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Code, 
  Database,
  Activity,
  Cpu
} from 'lucide-react';

interface AgentCapability {
  name: string;
  description: string;
  parameters: { name: string; type: string; required: boolean; description: string }[];
  examples: { input: Record<string, unknown>; output: Record<string, unknown> }[];
  status: 'available' | 'busy' | 'offline';
}

interface Agent {
  id: string;
  name: string;
  description: string;
  model: string;
  capabilities: AgentCapability[];
  status: 'active' | 'inactive' | 'busy';
  tools_count: number;
}

interface ExecutionResult {
  id: string;
  capability: string;
  agent: string;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
  status: 'success' | 'error';
  duration: number;
  timestamp: string;
}

export default function ADKCapabilityDemo() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [selectedCapability, setSelectedCapability] = useState<string>('');
  const [executionResults, setExecutionResults] = useState<ExecutionResult[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [parameterValues, setParameterValues] = useState<Record<string, unknown>>({});

  // Mock agent data with detailed capabilities
  const mockAgents: Agent[] = [
    {
      id: 'frontdesk_agent',
      name: 'Front Desk Agent',
      description: 'Handles patient registration and check-in processes using Google ADK',
      model: 'gemini-1.5-flash',
      status: 'active',
      tools_count: 3,
      capabilities: [
        {
          name: 'register_patient',
          description: 'Register a new patient in the system',
          parameters: [
            { name: 'first_name', type: 'string', required: true, description: 'Patient first name' },
            { name: 'last_name', type: 'string', required: true, description: 'Patient last name' },
            { name: 'phone', type: 'string', required: true, description: 'Patient phone number' },
            { name: 'email', type: 'string', required: false, description: 'Patient email address' },
            { name: 'date_of_birth', type: 'date', required: false, description: 'Patient date of birth' }
          ],
          examples: [
            {
              input: { first_name: 'John', last_name: 'Doe', phone: '555-0123', email: 'john@example.com' },
              output: { patient_id: 12345, status: 'registered', message: 'Patient registered successfully' }
            }
          ],
          status: 'available'
        },
        {
          name: 'check_in_patient',
          description: 'Check in an existing patient for their appointment',
          parameters: [
            { name: 'patient_id', type: 'integer', required: true, description: 'Patient ID to check in' },
            { name: 'appointment_id', type: 'integer', required: false, description: 'Specific appointment ID' }
          ],
          examples: [
            {
              input: { patient_id: 12345, appointment_id: 67890 },
              output: { status: 'checked_in', queue_position: 3, estimated_wait: 15 }
            }
          ],
          status: 'available'
        }
      ]
    },
    {
      id: 'queue_agent',
      name: 'Queue Management Agent',
      description: 'Manages patient queues and optimizes wait times using A2A protocol',
      model: 'gemini-1.5-flash',
      status: 'active',
      tools_count: 4,
      capabilities: [
        {
          name: 'add_to_queue',
          description: 'Add a patient to the appropriate queue',
          parameters: [
            { name: 'patient_id', type: 'integer', required: true, description: 'Patient ID' },
            { name: 'priority', type: 'string', required: true, description: 'Priority level (low, medium, high, urgent)' },
            { name: 'queue_type', type: 'string', required: true, description: 'Type of queue (walk_in, appointment, emergency)' }
          ],
          examples: [
            {
              input: { patient_id: 12345, priority: 'medium', queue_type: 'walk_in' },
              output: { queue_id: 789, position: 5, estimated_wait: 20, message: 'Added to queue successfully' }
            }
          ],
          status: 'available'
        },
        {
          name: 'optimize_queue',
          description: 'Optimize queue order based on priority and wait times',
          parameters: [
            { name: 'queue_type', type: 'string', required: true, description: 'Queue type to optimize' },
            { name: 'algorithm', type: 'string', required: false, description: 'Optimization algorithm (fifo, priority, smart)' }
          ],
          examples: [
            {
              input: { queue_type: 'walk_in', algorithm: 'smart' },
              output: { optimized: true, wait_time_reduction: 15, patients_reordered: 3 }
            }
          ],
          status: 'available'
        }
      ]
    },
    {
      id: 'appointment_agent',
      name: 'Appointment Agent',
      description: 'Manages appointment scheduling and coordination',
      model: 'gemini-1.5-flash',
      status: 'active',
      tools_count: 3,
      capabilities: [
        {
          name: 'schedule_appointment',
          description: 'Schedule a new appointment for a patient',
          parameters: [
            { name: 'patient_id', type: 'integer', required: true, description: 'Patient ID' },
            { name: 'datetime', type: 'datetime', required: true, description: 'Appointment date and time' },
            { name: 'appointment_type', type: 'string', required: true, description: 'Type of appointment' },
            { name: 'provider_id', type: 'integer', required: false, description: 'Specific provider ID' }
          ],
          examples: [
            {
              input: { patient_id: 12345, datetime: '2024-01-15T14:00:00Z', appointment_type: 'consultation' },
              output: { appointment_id: 67890, confirmation_code: 'ABC123', status: 'scheduled' }
            }
          ],
          status: 'available'
        }
      ]
    },
    {
      id: 'notification_agent',
      name: 'Notification Agent',
      description: 'Handles all patient notifications and alerts',
      model: 'gemini-1.5-flash',
      status: 'active',
      tools_count: 3,
      capabilities: [
        {
          name: 'send_notification',
          description: 'Send a notification to a patient',
          parameters: [
            { name: 'patient_id', type: 'integer', required: true, description: 'Patient ID' },
            { name: 'message', type: 'string', required: true, description: 'Notification message' },
            { name: 'notification_type', type: 'string', required: true, description: 'Type of notification (sms, email, push)' },
            { name: 'priority', type: 'string', required: false, description: 'Priority level (low, medium, high)' }
          ],
          examples: [
            {
              input: { patient_id: 12345, message: 'Your appointment is confirmed for tomorrow at 2 PM', notification_type: 'sms', priority: 'medium' },
              output: { notification_id: 456, status: 'sent', delivery_time: '2024-01-14T10:30:00Z' }
            }
          ],
          status: 'available'
        }
      ]
    }
  ];

  useEffect(() => {
    setAgents(mockAgents);
  }, [mockAgents]);

  const selectedAgentData = agents.find(a => a.id === selectedAgent);
  const selectedCapabilityData = selectedAgentData?.capabilities.find(c => c.name === selectedCapability);

  const executeCapability = async () => {
    if (!selectedCapabilityData || !selectedAgentData) return;

    setIsExecuting(true);
    const startTime = Date.now();

    // Simulate execution
    await new Promise(resolve => setTimeout(resolve, 2000));

    const result: ExecutionResult = {
      id: Date.now().toString(),
      capability: selectedCapability,
      agent: selectedAgent,
      input: parameterValues,
      output: selectedCapabilityData.examples[0]?.output || { status: 'success', message: 'Capability executed successfully' },
      status: 'success',
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString()
    };

    setExecutionResults(prev => [result, ...prev]);
    setIsExecuting(false);
    setParameterValues({});
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'inactive': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'busy': return <Clock className="h-4 w-4 text-yellow-500" />;
      default: return <XCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getCapabilityStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'bg-green-100 text-green-800';
      case 'busy': return 'bg-yellow-100 text-yellow-800';
      case 'offline': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              Select Agent
            </CardTitle>
            <CardDescription>
              Choose an agent to explore its capabilities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {agents.map((agent) => (
                <div
                  key={agent.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedAgent === agent.id ? 'border-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => {
                    setSelectedAgent(agent.id);
                    setSelectedCapability('');
                    setParameterValues({});
                  }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">{agent.name}</h3>
                    <Badge className={getCapabilityStatusColor(agent.status)}>
                      {getStatusIcon(agent.status)}
                      <span className="ml-1">{agent.status}</span>
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{agent.description}</p>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Model: {agent.model}</span>
                    <span>{agent.capabilities.length} capabilities</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Capability Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Capabilities
            </CardTitle>
            <CardDescription>
              Available capabilities for the selected agent
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedAgentData ? (
              <div className="space-y-3">
                {selectedAgentData.capabilities.map((capability) => (
                  <div
                    key={capability.name}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedCapability === capability.name ? 'border-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => {
                      setSelectedCapability(capability.name);
                      setParameterValues({});
                    }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{capability.name}</h3>
                      <Badge className={getCapabilityStatusColor(capability.status)}>
                        {capability.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">{capability.description}</p>
                    <div className="mt-2">
                      <p className="text-xs text-gray-500">
                        {capability.parameters.length} parameters
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">Select an agent to view capabilities</p>
            )}
          </CardContent>
        </Card>

        {/* Parameter Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code className="h-5 w-5" />
              Parameters
            </CardTitle>
            <CardDescription>
              Configure parameters for capability execution
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedCapabilityData ? (
              <div className="space-y-4">
                {selectedCapabilityData.parameters.map((param) => (
                  <div key={param.name}>
                    <Label htmlFor={param.name} className="flex items-center gap-2">
                      {param.name}
                      {param.required && <span className="text-red-500">*</span>}
                    </Label>
                    <Input
                      id={param.name}
                      type={param.type === 'integer' ? 'number' : param.type === 'datetime' ? 'datetime-local' : 'text'}
                      placeholder={param.description}
                      value={parameterValues[param.name] || ''}
                      onChange={(e) => setParameterValues(prev => ({
                        ...prev,
                        [param.name]: param.type === 'integer' ? parseInt(e.target.value) : e.target.value
                      }))}
                      className="mt-1"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Type: {param.type} {param.required ? '(required)' : '(optional)'}
                    </p>
                  </div>
                ))}
                
                <Button 
                  onClick={executeCapability} 
                  disabled={isExecuting || !selectedCapabilityData.parameters.every(p => !p.required || parameterValues[p.name])}
                  className="w-full"
                >
                  {isExecuting ? (
                    <>
                      <Activity className="h-4 w-4 mr-2 animate-pulse" />
                      Executing...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Execute Capability
                    </>
                  )}
                </Button>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">Select a capability to configure parameters</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Execution Results */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Execution Results
          </CardTitle>
          <CardDescription>
            Results from capability executions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {executionResults.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No executions yet. Execute a capability to see results.</p>
            ) : (
              executionResults.map((result) => (
                <div key={result.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Badge className={result.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                        {result.status === 'success' ? <CheckCircle className="h-3 w-3 mr-1" /> : <XCircle className="h-3 w-3 mr-1" />}
                        {result.status}
                      </Badge>
                      <span className="font-medium">{result.agent} - {result.capability}</span>
                    </div>
                    <div className="text-sm text-gray-500">
                      {result.duration}ms • {new Date(result.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  
                  <Tabs defaultValue="input" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="input">Input</TabsTrigger>
                      <TabsTrigger value="output">Output</TabsTrigger>
                    </TabsList>
                    <TabsContent value="input" className="mt-3">
                      <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
                        {JSON.stringify(result.input, null, 2)}
                      </pre>
                    </TabsContent>
                    <TabsContent value="output" className="mt-3">
                      <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
                        {JSON.stringify(result.output, null, 2)}
                      </pre>
                    </TabsContent>
                  </Tabs>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
