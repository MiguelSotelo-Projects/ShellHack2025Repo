'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Bot, 
  MessageSquare, 
  Network, 
  Activity, 
  Zap, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Play,
  Pause,
  RotateCcw,
  Eye,
  Settings,
  Database,
  Wifi
} from 'lucide-react';

interface AgentCapability {
  name: string;
  description: string;
  parameters: string[];
  status: 'available' | 'busy' | 'offline';
}

interface AgentInfo {
  agent_id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'busy';
  capabilities: AgentCapability[];
  last_heartbeat: string;
  model: string;
  tools_count: number;
}

interface A2AMessage {
  id: string;
  from: string;
  to: string;
  message: string;
  timestamp: string;
  status: 'sent' | 'delivered' | 'processed' | 'error';
  response?: string;
}

interface WorkflowStep {
  id: string;
  name: string;
  agent: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration?: number;
  result?: Record<string, unknown>;
}

export default function ADKShowcasePage() {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [messages, setMessages] = useState<A2AMessage[]>([]);
  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([]);
  const [isWorkflowRunning, setIsWorkflowRunning] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  const [messageTo, setMessageTo] = useState('');
  const [discoveryStats, setDiscoveryStats] = useState({
    total_agents: 0,
    active_agents: 0,
    total_capabilities: 0,
    network_health: 'excellent'
  });

  useEffect(() => {
    // Mock agent data for demonstration
    const mockAgents: AgentInfo[] = [
      {
        agent_id: 'frontdesk_agent',
        name: 'Front Desk Agent',
        description: 'Handles patient registration and check-in processes',
        status: 'active',
        capabilities: [
          { name: 'register_patient', description: 'Register new patients', parameters: ['name', 'phone', 'email'], status: 'available' },
          { name: 'check_in_patient', description: 'Check in existing patients', parameters: ['patient_id'], status: 'available' },
          { name: 'update_patient_info', description: 'Update patient information', parameters: ['patient_id', 'updates'], status: 'available' }
        ],
        last_heartbeat: new Date().toISOString(),
        model: 'gemini-1.5-flash',
        tools_count: 3
      },
      {
        agent_id: 'queue_agent',
        name: 'Queue Management Agent',
        description: 'Manages patient queues and wait times',
        status: 'active',
        capabilities: [
          { name: 'add_to_queue', description: 'Add patient to queue', parameters: ['patient_id', 'priority'], status: 'available' },
          { name: 'get_queue_status', description: 'Get current queue status', parameters: [], status: 'available' },
          { name: 'call_next_patient', description: 'Call next patient from queue', parameters: [], status: 'available' }
        ],
        last_heartbeat: new Date().toISOString(),
        model: 'gemini-1.5-flash',
        tools_count: 3
      },
      {
        agent_id: 'appointment_agent',
        name: 'Appointment Agent',
        description: 'Manages appointment scheduling and coordination',
        status: 'active',
        capabilities: [
          { name: 'schedule_appointment', description: 'Schedule new appointment', parameters: ['patient_id', 'datetime', 'type'], status: 'available' },
          { name: 'reschedule_appointment', description: 'Reschedule existing appointment', parameters: ['appointment_id', 'new_datetime'], status: 'available' },
          { name: 'cancel_appointment', description: 'Cancel appointment', parameters: ['appointment_id'], status: 'available' }
        ],
        last_heartbeat: new Date().toISOString(),
        model: 'gemini-1.5-flash',
        tools_count: 3
      },
      {
        agent_id: 'notification_agent',
        name: 'Notification Agent',
        description: 'Handles notifications and alerts',
        status: 'active',
        capabilities: [
          { name: 'send_notification', description: 'Send notification to patient', parameters: ['patient_id', 'message', 'type'], status: 'available' },
          { name: 'send_reminder', description: 'Send appointment reminder', parameters: ['appointment_id'], status: 'available' },
          { name: 'broadcast_alert', description: 'Broadcast system alert', parameters: ['message', 'priority'], status: 'available' }
        ],
        last_heartbeat: new Date().toISOString(),
        model: 'gemini-1.5-flash',
        tools_count: 3
      },
      {
        agent_id: 'orchestrator_agent',
        name: 'Workflow Orchestrator',
        description: 'Coordinates complex workflows between agents',
        status: 'active',
        capabilities: [
          { name: 'orchestrate_workflow', description: 'Orchestrate multi-agent workflow', parameters: ['workflow_type', 'parameters'], status: 'available' },
          { name: 'monitor_workflow', description: 'Monitor workflow progress', parameters: ['workflow_id'], status: 'available' },
          { name: 'handle_workflow_error', description: 'Handle workflow errors', parameters: ['workflow_id', 'error'], status: 'available' }
        ],
        last_heartbeat: new Date().toISOString(),
        model: 'gemini-1.5-flash',
        tools_count: 3
      }
    ];

    setAgents(mockAgents);
    setDiscoveryStats({
      total_agents: mockAgents.length,
      active_agents: mockAgents.filter(a => a.status === 'active').length,
      total_capabilities: mockAgents.reduce((sum, agent) => sum + agent.capabilities.length, 0),
      network_health: 'excellent'
    });
  }, []);

  const sendMessage = async () => {
    if (!newMessage || !messageTo) return;

    const message: A2AMessage = {
      id: Date.now().toString(),
      from: 'user',
      to: messageTo,
      message: newMessage,
      timestamp: new Date().toISOString(),
      status: 'sent'
    };

    setMessages(prev => [message, ...prev]);
    setNewMessage('');

    // Simulate message processing
    setTimeout(() => {
      setMessages(prev => prev.map(m => 
        m.id === message.id 
          ? { ...m, status: 'delivered', response: `Agent ${messageTo} processed: "${newMessage}"` }
          : m
      ));
    }, 1000);
  };

  const runWorkflow = async () => {
    setIsWorkflowRunning(true);
    
    const workflow: WorkflowStep[] = [
      { id: '1', name: 'Register Patient', agent: 'frontdesk_agent', status: 'pending' },
      { id: '2', name: 'Add to Queue', agent: 'queue_agent', status: 'pending' },
      { id: '3', name: 'Schedule Follow-up', agent: 'appointment_agent', status: 'pending' },
      { id: '4', name: 'Send Confirmation', agent: 'notification_agent', status: 'pending' }
    ];

    setWorkflowSteps(workflow);

    // Simulate workflow execution
    for (let i = 0; i < workflow.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setWorkflowSteps(prev => prev.map((step, index) => {
        if (index === i) {
          return { ...step, status: 'running' };
        }
        return step;
      }));

      await new Promise(resolve => setTimeout(resolve, 1500));

      setWorkflowSteps(prev => prev.map((step, index) => {
        if (index === i) {
          return { 
            ...step, 
            status: 'completed', 
            duration: Math.random() * 2000 + 500,
            result: `Step ${i + 1} completed successfully`
          };
        }
        return step;
      }));
    }

    setIsWorkflowRunning(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'inactive': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'busy': return <Clock className="h-4 w-4 text-yellow-500" />;
      default: return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-red-100 text-red-800';
      case 'busy': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
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
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Bot className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-4xl font-bold">Google ADK/A2A Protocol Showcase</h1>
            <p className="text-gray-600 text-lg">
              Interactive demonstration of Agent-to-Agent communication and workflow orchestration
            </p>
          </div>
        </div>
        
        <Alert className="mb-6">
          <Zap className="h-4 w-4" />
          <AlertDescription>
            This showcase demonstrates the power of Google&apos;s ADK (Agent Development Kit) and A2A (Agent-to-Agent) protocol 
            in a real hospital operations management system. Watch as agents communicate, coordinate workflows, and manage 
            complex hospital processes autonomously.
          </AlertDescription>
        </Alert>
      </div>

      {/* Network Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Network className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Total Agents</p>
                <p className="text-2xl font-bold">{discoveryStats.total_agents}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Activity className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Active Agents</p>
                <p className="text-2xl font-bold">{discoveryStats.active_agents}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Settings className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">Capabilities</p>
                <p className="text-2xl font-bold">{discoveryStats.total_capabilities}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Wifi className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Network Health</p>
                <p className="text-lg font-bold text-green-600">Excellent</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="agents" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="agents">Agent Discovery</TabsTrigger>
          <TabsTrigger value="communication">A2A Communication</TabsTrigger>
          <TabsTrigger value="workflow">Workflow Orchestration</TabsTrigger>
          <TabsTrigger value="monitoring">Real-time Monitoring</TabsTrigger>
        </TabsList>

        {/* Agent Discovery Tab */}
        <TabsContent value="agents" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Agent Discovery & Capabilities
              </CardTitle>
              <CardDescription>
                Discover available agents and their capabilities in the A2A network
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {agents.map((agent) => (
                  <Card key={agent.agent_id} className="border-l-4 border-l-blue-500">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Bot className="h-6 w-6 text-blue-600" />
                          <div>
                            <CardTitle className="text-lg">{agent.name}</CardTitle>
                            <CardDescription>{agent.description}</CardDescription>
                          </div>
                        </div>
                        <Badge className={getStatusColor(agent.status)}>
                          {getStatusIcon(agent.status)}
                          <span className="ml-1">{agent.status.toUpperCase()}</span>
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                          <span>Model:</span>
                          <span className="font-medium">{agent.model}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Tools:</span>
                          <span className="font-medium">{agent.tools_count}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Last Heartbeat:</span>
                          <span className="font-medium">
                            {new Date(agent.last_heartbeat).toLocaleTimeString()}
                          </span>
                        </div>
                        
                        <div className="mt-4">
                          <h4 className="font-medium mb-2">Capabilities:</h4>
                          <div className="space-y-2">
                            {agent.capabilities.map((capability, index) => (
                              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                <div>
                                  <p className="font-medium text-sm">{capability.name}</p>
                                  <p className="text-xs text-gray-600">{capability.description}</p>
                                </div>
                                <Badge className={getCapabilityStatusColor(capability.status)}>
                                  {capability.status}
                                </Badge>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* A2A Communication Tab */}
        <TabsContent value="communication" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Send A2A Message
                </CardTitle>
                <CardDescription>
                  Send messages between agents using the A2A protocol
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="messageTo">To Agent:</Label>
                  <Select value={messageTo} onValueChange={setMessageTo}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select target agent" />
                    </SelectTrigger>
                    <SelectContent>
                      {agents.map((agent) => (
                        <SelectItem key={agent.agent_id} value={agent.agent_id}>
                          {agent.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="newMessage">Message:</Label>
                  <Textarea
                    id="newMessage"
                    placeholder="Enter your message..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                  />
                </div>
                
                <Button onClick={sendMessage} disabled={!newMessage || !messageTo} className="w-full">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Send A2A Message
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Message History
                </CardTitle>
                <CardDescription>
                  Real-time A2A communication log
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {messages.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No messages yet</p>
                  ) : (
                    messages.map((message) => (
                      <div key={message.id} className="border rounded-lg p-3">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{message.from}</span>
                            <span className="text-gray-400">→</span>
                            <span className="font-medium">{message.to}</span>
                          </div>
                          <Badge className={getStatusColor(message.status)}>
                            {message.status}
                          </Badge>
                        </div>
                        <p className="text-sm mb-2">{message.message}</p>
                        {message.response && (
                          <div className="bg-blue-50 p-2 rounded text-sm">
                            <strong>Response:</strong> {message.response}
                          </div>
                        )}
                        <p className="text-xs text-gray-500">
                          {new Date(message.timestamp).toLocaleString()}
                        </p>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Workflow Orchestration Tab */}
        <TabsContent value="workflow" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Network className="h-5 w-5" />
                Workflow Orchestration
              </CardTitle>
              <CardDescription>
                Demonstrate multi-agent workflow coordination
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex gap-4">
                  <Button 
                    onClick={runWorkflow} 
                    disabled={isWorkflowRunning}
                    className="flex items-center gap-2"
                  >
                    {isWorkflowRunning ? (
                      <>
                        <Pause className="h-4 w-4" />
                        Running...
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4" />
                        Run Patient Registration Workflow
                      </>
                    )}
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    onClick={() => setWorkflowSteps([])}
                    disabled={isWorkflowRunning}
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Reset
                  </Button>
                </div>

                {workflowSteps.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="font-semibold">Workflow Progress:</h3>
                    <div className="space-y-3">
                      {workflowSteps.map((step) => (
                        <div key={step.id} className="flex items-center gap-4 p-4 border rounded-lg">
                          <div className="flex-shrink-0">
                            {step.status === 'pending' && <Clock className="h-5 w-5 text-gray-400" />}
                            {step.status === 'running' && <Activity className="h-5 w-5 text-blue-500 animate-pulse" />}
                            {step.status === 'completed' && <CheckCircle className="h-5 w-5 text-green-500" />}
                            {step.status === 'failed' && <XCircle className="h-5 w-5 text-red-500" />}
                          </div>
                          
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <h4 className="font-medium">{step.name}</h4>
                              <Badge className={getStatusColor(step.status)}>
                                {step.status}
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-600">Agent: {step.agent}</p>
                            {step.duration && (
                              <p className="text-xs text-gray-500">
                                Duration: {step.duration.toFixed(0)}ms
                              </p>
                            )}
                            {step.result && (
                              <p className="text-xs text-green-600 mt-1">{step.result}</p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Real-time Monitoring Tab */}
        <TabsContent value="monitoring" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Agent Health Monitor
                </CardTitle>
                <CardDescription>
                  Real-time agent status and performance metrics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {agents.map((agent) => (
                    <div key={agent.agent_id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <Bot className="h-5 w-5 text-blue-600" />
                        <div>
                          <p className="font-medium">{agent.name}</p>
                          <p className="text-sm text-gray-600">{agent.model}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(agent.status)}>
                          {getStatusIcon(agent.status)}
                          <span className="ml-1">{agent.status}</span>
                        </Badge>
                        <div className="text-right">
                          <p className="text-sm font-medium">{agent.capabilities.length} tools</p>
                          <p className="text-xs text-gray-500">
                            {new Date(agent.last_heartbeat).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  System Metrics
                </CardTitle>
                <CardDescription>
                  A2A network performance and statistics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">Network Latency</span>
                    <span className="text-green-600 font-bold">12ms</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">Message Throughput</span>
                    <span className="text-blue-600 font-bold">1,247/min</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">Success Rate</span>
                    <span className="text-green-600 font-bold">99.8%</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">Active Workflows</span>
                    <span className="text-purple-600 font-bold">{isWorkflowRunning ? '1' : '0'}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
