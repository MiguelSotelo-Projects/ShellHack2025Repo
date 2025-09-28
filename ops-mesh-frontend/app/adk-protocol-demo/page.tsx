'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Bot, 
  Network, 
  Zap, 
  Database,
  MessageSquare,
  Activity,
  CheckCircle,
  XCircle,
  Play,
  RotateCcw,
  Eye,
  Cpu,
  Wifi,
  ArrowRight,
  ArrowLeft,
  Target,
  Shield,
  Lock
} from 'lucide-react';

interface ProtocolMessage {
  id: string;
  type: 'discovery' | 'task_request' | 'task_response' | 'heartbeat' | 'error';
  from: string;
  to: string;
  payload: Record<string, unknown>;
  timestamp: string;
  status: 'sent' | 'delivered' | 'processed' | 'error';
}

interface AgentProtocol {
  agent_id: string;
  name: string;
  capabilities: string[];
  status: 'active' | 'inactive' | 'busy';
  last_heartbeat: string;
  protocol_version: string;
  security_level: 'high' | 'medium' | 'low';
}

export default function ADKProtocolDemoPage() {
  const [agents, setAgents] = useState<AgentProtocol[]>([]);
  const [protocolMessages, setProtocolMessages] = useState<ProtocolMessage[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [protocolStats, setProtocolStats] = useState({
    total_messages: 0,
    successful_handshakes: 0,
    active_connections: 0,
    protocol_errors: 0,
    average_latency: 12,
    security_violations: 0
  });

  useEffect(() => {
    // Mock agent data with protocol information
    const mockAgents: AgentProtocol[] = [
      {
        agent_id: 'orchestrator_agent',
        name: 'Workflow Orchestrator',
        capabilities: ['workflow_coordination', 'task_distribution', 'error_handling', 'security_monitoring'],
        status: 'active',
        last_heartbeat: new Date().toISOString(),
        protocol_version: 'A2A-v1.2',
        security_level: 'high'
      },
      {
        agent_id: 'frontdesk_agent',
        name: 'Front Desk Agent',
        capabilities: ['patient_registration', 'check_in', 'info_update', 'data_validation'],
        status: 'active',
        last_heartbeat: new Date().toISOString(),
        protocol_version: 'A2A-v1.2',
        security_level: 'high'
      },
      {
        agent_id: 'queue_agent',
        name: 'Queue Management Agent',
        capabilities: ['queue_management', 'wait_time_calculation', 'patient_calling', 'optimization'],
        status: 'active',
        last_heartbeat: new Date().toISOString(),
        protocol_version: 'A2A-v1.2',
        security_level: 'medium'
      },
      {
        agent_id: 'appointment_agent',
        name: 'Appointment Agent',
        capabilities: ['scheduling', 'rescheduling', 'cancellation', 'conflict_resolution'],
        status: 'active',
        last_heartbeat: new Date().toISOString(),
        protocol_version: 'A2A-v1.2',
        security_level: 'high'
      },
      {
        agent_id: 'notification_agent',
        name: 'Notification Agent',
        capabilities: ['sms', 'email', 'push_notifications', 'delivery_tracking'],
        status: 'active',
        last_heartbeat: new Date().toISOString(),
        protocol_version: 'A2A-v1.2',
        security_level: 'medium'
      }
    ];
    
    setAgents(mockAgents);
  }, []);

  const simulateProtocolFlow = async () => {
    setIsSimulating(true);
    
    const protocolFlows = [
      // Discovery Phase
      {
        type: 'discovery' as const,
        from: 'orchestrator_agent',
        to: 'broadcast',
        payload: { action: 'discover_agents', capabilities: ['workflow_coordination'] }
      },
      {
        type: 'discovery' as const,
        from: 'frontdesk_agent',
        to: 'orchestrator_agent',
        payload: { response: 'agent_discovered', capabilities: ['patient_registration', 'check_in'] }
      },
      {
        type: 'discovery' as const,
        from: 'queue_agent',
        to: 'orchestrator_agent',
        payload: { response: 'agent_discovered', capabilities: ['queue_management', 'optimization'] }
      },
      
      // Task Request Phase
      {
        type: 'task_request' as const,
        from: 'orchestrator_agent',
        to: 'frontdesk_agent',
        payload: { task: 'register_patient', parameters: { name: 'John Doe', phone: '555-0123' } }
      },
      {
        type: 'task_response' as const,
        from: 'frontdesk_agent',
        to: 'orchestrator_agent',
        payload: { task_id: 'task_001', status: 'completed', result: { patient_id: 12345 } }
      },
      
      // Workflow Coordination
      {
        type: 'task_request' as const,
        from: 'orchestrator_agent',
        to: 'queue_agent',
        payload: { task: 'add_to_queue', parameters: { patient_id: 12345, priority: 'medium' } }
      },
      {
        type: 'task_response' as const,
        from: 'queue_agent',
        to: 'orchestrator_agent',
        payload: { task_id: 'task_002', status: 'completed', result: { queue_position: 3, wait_time: 15 } }
      },
      
      // Heartbeat Monitoring
      {
        type: 'heartbeat' as const,
        from: 'frontdesk_agent',
        to: 'orchestrator_agent',
        payload: { status: 'healthy', load: 0.3, capabilities: ['patient_registration', 'check_in'] }
      },
      {
        type: 'heartbeat' as const,
        from: 'queue_agent',
        to: 'orchestrator_agent',
        payload: { status: 'healthy', load: 0.7, capabilities: ['queue_management', 'optimization'] }
      }
    ];

    for (let i = 0; i < protocolFlows.length; i++) {
      const flow = protocolFlows[i];
      
      const message: ProtocolMessage = {
        id: `protocol-${Date.now()}-${i}`,
        type: flow.type,
        from: flow.from,
        to: flow.to,
        payload: flow.payload,
        timestamp: new Date().toISOString(),
        status: 'sent'
      };

      setProtocolMessages(prev => [message, ...prev]);
      setProtocolStats(prev => ({ ...prev, total_messages: prev.total_messages + 1 }));

      // Simulate message delivery
      await new Promise(resolve => setTimeout(resolve, 500));
      setProtocolMessages(prev => prev.map(msg => 
        msg.id === message.id ? { ...msg, status: 'delivered' } : msg
      ));

      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 800));
      setProtocolMessages(prev => prev.map(msg => 
        msg.id === message.id ? { ...msg, status: 'processed' } : msg
      ));

      // Update stats based on message type
      if (flow.type === 'discovery') {
        setProtocolStats(prev => ({ ...prev, successful_handshakes: prev.successful_handshakes + 1 }));
      }
    }

    setIsSimulating(false);
  };

  const clearProtocolLog = () => {
    setProtocolMessages([]);
    setProtocolStats(prev => ({ ...prev, total_messages: 0 }));
  };

  const getProtocolIcon = (type: string) => {
    switch (type) {
      case 'discovery': return <Eye className="h-4 w-4" />;
      case 'task_request': return <ArrowRight className="h-4 w-4" />;
      case 'task_response': return <ArrowLeft className="h-4 w-4" />;
      case 'heartbeat': return <Activity className="h-4 w-4" />;
      case 'error': return <XCircle className="h-4 w-4" />;
      default: return <MessageSquare className="h-4 w-4" />;
    }
  };

  const getProtocolColor = (type: string) => {
    switch (type) {
      case 'discovery': return 'text-blue-600';
      case 'task_request': return 'text-green-600';
      case 'task_response': return 'text-green-700';
      case 'heartbeat': return 'text-purple-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'sent': return 'bg-blue-100 text-blue-800';
      case 'delivered': return 'bg-yellow-100 text-yellow-800';
      case 'processed': return 'bg-green-100 text-green-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSecurityIcon = (level: string) => {
    switch (level) {
      case 'high': return <Shield className="h-4 w-4 text-green-600" />;
      case 'medium': return <Lock className="h-4 w-4 text-yellow-600" />;
      case 'low': return <Target className="h-4 w-4 text-red-600" />;
      default: return <Target className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Network className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-4xl font-bold">A2A Protocol Deep Dive</h1>
            <p className="text-gray-600 text-lg">
              Advanced demonstration of Google ADK&apos;s Agent-to-Agent protocol implementation
            </p>
          </div>
        </div>
        
        <Alert className="mb-6">
          <Zap className="h-4 w-4" />
          <AlertDescription>
            This page demonstrates the core A2A protocol features including agent discovery, 
            secure communication, task distribution, and real-time monitoring. Watch as agents 
            establish connections, exchange capabilities, and coordinate complex workflows.
          </AlertDescription>
        </Alert>
      </div>

      {/* Protocol Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-8">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <MessageSquare className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Total Messages</p>
                <p className="text-2xl font-bold">{protocolStats.total_messages}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Handshakes</p>
                <p className="text-2xl font-bold">{protocolStats.successful_handshakes}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Wifi className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Connections</p>
                <p className="text-2xl font-bold">{protocolStats.active_connections}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <XCircle className="h-8 w-8 text-red-600" />
              <div>
                <p className="text-sm text-gray-600">Protocol Errors</p>
                <p className="text-2xl font-bold">{protocolStats.protocol_errors}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Zap className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">Avg Latency</p>
                <p className="text-2xl font-bold">{protocolStats.average_latency}ms</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Shield className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Security Violations</p>
                <p className="text-2xl font-bold">{protocolStats.security_violations}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="agents" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="agents">Agent Registry</TabsTrigger>
          <TabsTrigger value="protocol">Protocol Flow</TabsTrigger>
          <TabsTrigger value="security">Security & Auth</TabsTrigger>
          <TabsTrigger value="monitoring">Real-time Monitoring</TabsTrigger>
        </TabsList>

        {/* Agent Registry Tab */}
        <TabsContent value="agents" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                A2A Agent Registry
              </CardTitle>
              <CardDescription>
                Registered agents with their protocol capabilities and security levels
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
                            <CardDescription>ID: {agent.agent_id}</CardDescription>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className={agent.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                            {agent.status === 'active' ? <CheckCircle className="h-3 w-3 mr-1" /> : <XCircle className="h-3 w-3 mr-1" />}
                            {agent.status}
                          </Badge>
                          <div className="flex items-center gap-1">
                            {getSecurityIcon(agent.security_level)}
                            <span className="text-xs text-gray-600">{agent.security_level}</span>
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                          <span>Protocol Version:</span>
                          <span className="font-medium">{agent.protocol_version}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Last Heartbeat:</span>
                          <span className="font-medium">
                            {new Date(agent.last_heartbeat).toLocaleTimeString()}
                          </span>
                        </div>
                        
                        <div className="mt-4">
                          <h4 className="font-medium mb-2">Capabilities:</h4>
                          <div className="flex flex-wrap gap-1">
                            {agent.capabilities.map((capability, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {capability}
                              </Badge>
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

        {/* Protocol Flow Tab */}
        <TabsContent value="protocol" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Network className="h-5 w-5" />
                A2A Protocol Flow Simulation
              </CardTitle>
              <CardDescription>
                Simulate the complete A2A protocol flow including discovery, handshakes, and task coordination
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex gap-4">
                  <Button 
                    onClick={simulateProtocolFlow} 
                    disabled={isSimulating}
                    className="flex items-center gap-2"
                  >
                    {isSimulating ? (
                      <>
                        <Activity className="h-4 w-4 animate-pulse" />
                        Simulating Protocol...
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4" />
                        Simulate A2A Protocol Flow
                      </>
                    )}
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    onClick={clearProtocolLog}
                    disabled={isSimulating}
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Clear Log
                  </Button>
                </div>

                {protocolMessages.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="font-semibold">Protocol Message Log:</h3>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {protocolMessages.slice(0, 20).map((message) => (
                        <div key={message.id} className="flex items-center gap-3 p-3 border rounded-lg">
                          <div className="flex-shrink-0">
                            <div className={`p-2 rounded-full ${getProtocolColor(message.type)} bg-opacity-10`}>
                              {getProtocolIcon(message.type)}
                            </div>
                          </div>
                          
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-medium text-sm">{message.from}</span>
                              <ArrowRight className="h-3 w-3 text-gray-400" />
                              <span className="font-medium text-sm">{message.to}</span>
                              <Badge className={`text-xs ${getStatusColor(message.status)}`}>
                                {message.status}
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-600 mb-1">
                              <strong>{message.type.toUpperCase()}:</strong> {JSON.stringify(message.payload).substring(0, 100)}...
                            </p>
                            <p className="text-xs text-gray-500">
                              {new Date(message.timestamp).toLocaleTimeString()}
                            </p>
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

        {/* Security & Auth Tab */}
        <TabsContent value="security" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Security Overview
                </CardTitle>
                <CardDescription>
                  A2A protocol security features and authentication
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                    <span className="font-medium">End-to-End Encryption</span>
                    <Badge className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                    <span className="font-medium">Certificate Validation</span>
                    <Badge className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                    <span className="font-medium">Message Authentication</span>
                    <Badge className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                    <span className="font-medium">Rate Limiting</span>
                    <Badge className="bg-yellow-100 text-yellow-800">Active</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lock className="h-5 w-5" />
                  Authentication Status
                </CardTitle>
                <CardDescription>
                  Current authentication status for all agents
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {agents.map((agent) => (
                    <div key={agent.agent_id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <Bot className="h-5 w-5 text-blue-600" />
                        <div>
                          <p className="font-medium text-sm">{agent.name}</p>
                          <p className="text-xs text-gray-600">{agent.agent_id}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {getSecurityIcon(agent.security_level)}
                        <Badge className={agent.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                          {agent.status === 'active' ? 'Authenticated' : 'Offline'}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Real-time Monitoring Tab */}
        <TabsContent value="monitoring" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Protocol Performance
                </CardTitle>
                <CardDescription>
                  Real-time A2A protocol performance metrics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">Message Throughput</span>
                    <span className="text-blue-600 font-bold">1,247/min</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">Average Response Time</span>
                    <span className="text-green-600 font-bold">12ms</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">Success Rate</span>
                    <span className="text-green-600 font-bold">99.8%</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">Active Connections</span>
                    <span className="text-purple-600 font-bold">{agents.filter(a => a.status === 'active').length}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cpu className="h-5 w-5" />
                  System Health
                </CardTitle>
                <CardDescription>
                  Overall system health and resource utilization
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">CPU Usage</span>
                    <span className="text-green-600 font-bold">23%</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">Memory Usage</span>
                    <span className="text-yellow-600 font-bold">67%</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">Network Latency</span>
                    <span className="text-green-600 font-bold">8ms</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">Error Rate</span>
                    <span className="text-green-600 font-bold">0.2%</span>
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
