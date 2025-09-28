'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Network, 
  Bot, 
  MessageSquare, 
  Activity, 
  Zap, 
  CheckCircle, 
  XCircle, 
  Clock,
  ArrowRight,
  ArrowLeft,
  Wifi,
  WifiOff,
  Cpu,
  Database,
  Users,
  Calendar,
  Play,
  RotateCcw
} from 'lucide-react';

interface AgentNode {
  id: string;
  name: string;
  type: 'frontdesk' | 'queue' | 'appointment' | 'notification' | 'orchestrator';
  status: 'active' | 'busy' | 'inactive';
  position: { x: number; y: number };
  capabilities: string[];
  currentTask?: string;
}

interface MessageFlow {
  id: string;
  from: string;
  to: string;
  message: string;
  timestamp: string;
  status: 'sending' | 'delivered' | 'processing' | 'completed' | 'error';
  type: 'request' | 'response' | 'notification';
}

export default function ADKAgentNetwork() {
  const [agents, setAgents] = useState<AgentNode[]>([
    {
      id: 'orchestrator',
      name: 'Orchestrator',
      type: 'orchestrator',
      status: 'active',
      position: { x: 400, y: 50 },
      capabilities: ['workflow_coordination', 'task_distribution', 'error_handling']
    },
    {
      id: 'frontdesk',
      name: 'Front Desk',
      type: 'frontdesk',
      status: 'active',
      position: { x: 100, y: 200 },
      capabilities: ['patient_registration', 'check_in', 'info_update']
    },
    {
      id: 'queue',
      name: 'Queue Manager',
      type: 'queue',
      status: 'active',
      position: { x: 300, y: 200 },
      capabilities: ['queue_management', 'wait_time_calculation', 'patient_calling']
    },
    {
      id: 'appointment',
      name: 'Appointment',
      type: 'appointment',
      status: 'active',
      position: { x: 500, y: 200 },
      capabilities: ['scheduling', 'rescheduling', 'cancellation']
    },
    {
      id: 'notification',
      name: 'Notification',
      type: 'notification',
      status: 'active',
      position: { x: 700, y: 200 },
      capabilities: ['sms', 'email', 'push_notifications']
    }
  ]);

  const [messageFlows, setMessageFlows] = useState<MessageFlow[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [networkStats, setNetworkStats] = useState({
    totalMessages: 0,
    activeConnections: 0,
    successRate: 99.8,
    averageLatency: 12
  });

  const getAgentIcon = (type: string) => {
    switch (type) {
      case 'orchestrator': return <Network className="h-6 w-6" />;
      case 'frontdesk': return <Users className="h-6 w-6" />;
      case 'queue': return <Clock className="h-6 w-6" />;
      case 'appointment': return <Calendar className="h-6 w-6" />;
      case 'notification': return <MessageSquare className="h-6 w-6" />;
      default: return <Bot className="h-6 w-6" />;
    }
  };

  const getAgentColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'busy': return 'bg-yellow-500';
      case 'inactive': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getMessageColor = (status: string) => {
    switch (status) {
      case 'sending': return 'text-blue-500';
      case 'delivered': return 'text-green-500';
      case 'processing': return 'text-yellow-500';
      case 'completed': return 'text-green-600';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const simulateWorkflow = async () => {
    setIsSimulating(true);
    
    const workflow = [
      {
        from: 'orchestrator',
        to: 'frontdesk',
        message: 'Register new patient: John Doe',
        type: 'request' as const
      },
      {
        from: 'frontdesk',
        to: 'orchestrator',
        message: 'Patient registered successfully (ID: 12345)',
        type: 'response' as const
      },
      {
        from: 'orchestrator',
        to: 'queue',
        message: 'Add patient 12345 to queue with priority: medium',
        type: 'request' as const
      },
      {
        from: 'queue',
        to: 'orchestrator',
        message: 'Patient added to queue, estimated wait: 15 minutes',
        type: 'response' as const
      },
      {
        from: 'orchestrator',
        to: 'appointment',
        message: 'Schedule follow-up appointment for patient 12345',
        type: 'request' as const
      },
      {
        from: 'appointment',
        to: 'orchestrator',
        message: 'Appointment scheduled for tomorrow 2:00 PM',
        type: 'response' as const
      },
      {
        from: 'orchestrator',
        to: 'notification',
        message: 'Send confirmation to patient 12345',
        type: 'request' as const
      },
      {
        from: 'notification',
        to: 'orchestrator',
        message: 'Confirmation sent via SMS and email',
        type: 'response' as const
      }
    ];

    for (let i = 0; i < workflow.length; i++) {
      const step = workflow[i];
      
      // Create message flow
      const messageFlow: MessageFlow = {
        id: `msg-${Date.now()}-${i}`,
        from: step.from,
        to: step.to,
        message: step.message,
        timestamp: new Date().toISOString(),
        status: 'sending',
        type: step.type
      };

      setMessageFlows(prev => [messageFlow, ...prev]);
      setNetworkStats(prev => ({ ...prev, totalMessages: prev.totalMessages + 1 }));

      // Update agent status to busy
      setAgents(prev => prev.map(agent => 
        agent.id === step.from || agent.id === step.to
          ? { ...agent, status: 'busy', currentTask: step.message }
          : agent
      ));

      // Simulate message delivery
      await new Promise(resolve => setTimeout(resolve, 800));
      setMessageFlows(prev => prev.map(msg => 
        msg.id === messageFlow.id 
          ? { ...msg, status: 'delivered' }
          : msg
      ));

      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 1200));
      setMessageFlows(prev => prev.map(msg => 
        msg.id === messageFlow.id 
          ? { ...msg, status: 'processing' }
          : msg
      ));

      // Simulate completion
      await new Promise(resolve => setTimeout(resolve, 1000));
      setMessageFlows(prev => prev.map(msg => 
        msg.id === messageFlow.id 
          ? { ...msg, status: 'completed' }
          : msg
      ));

      // Reset agent status
      setAgents(prev => prev.map(agent => 
        agent.id === step.from || agent.id === step.to
          ? { ...agent, status: 'active', currentTask: undefined }
          : agent
      ));
    }

    setIsSimulating(false);
  };

  const clearMessages = () => {
    setMessageFlows([]);
    setNetworkStats(prev => ({ ...prev, totalMessages: 0 }));
  };

  return (
    <div className="space-y-6">
      {/* Network Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <MessageSquare className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Total Messages</p>
                <p className="text-2xl font-bold">{networkStats.totalMessages}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Wifi className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Active Connections</p>
                <p className="text-2xl font-bold">{agents.filter(a => a.status === 'active').length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold">{networkStats.successRate}%</p>
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
                <p className="text-2xl font-bold">{networkStats.averageLatency}ms</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Network Visualization */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5" />
            A2A Agent Network Visualization
          </CardTitle>
          <CardDescription>
            Real-time visualization of agent-to-agent communication
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Control Panel */}
            <div className="flex gap-4">
              <Button 
                onClick={simulateWorkflow} 
                disabled={isSimulating}
                className="flex items-center gap-2"
              >
                {isSimulating ? (
                  <>
                    <Activity className="h-4 w-4 animate-pulse" />
                    Running Workflow...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    Simulate Patient Workflow
                  </>
                )}
              </Button>
              
              <Button 
                variant="outline" 
                onClick={clearMessages}
                disabled={isSimulating}
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Clear Messages
              </Button>
            </div>

            {/* Network Graph */}
            <div className="relative bg-gray-50 rounded-lg p-8 min-h-96">
              <svg width="100%" height="400" className="absolute inset-0">
                {/* Draw connections */}
                {messageFlows.slice(0, 10).map((flow, index) => {
                  const fromAgent = agents.find(a => a.id === flow.from);
                  const toAgent = agents.find(a => a.id === flow.to);
                  if (!fromAgent || !toAgent) return null;

                  return (
                    <g key={flow.id}>
                      <line
                        x1={fromAgent.position.x}
                        y1={fromAgent.position.y + 30}
                        x2={toAgent.position.x}
                        y2={toAgent.position.y + 30}
                        stroke={getMessageColor(flow.status)}
                        strokeWidth="2"
                        strokeDasharray={flow.status === 'sending' ? '5,5' : '0'}
                        className="animate-pulse"
                      />
                      <circle
                        cx={fromAgent.position.x + (toAgent.position.x - fromAgent.position.x) * 0.5}
                        cy={fromAgent.position.y + 30}
                        r="4"
                        fill={getMessageColor(flow.status)}
                        className="animate-ping"
                      />
                    </g>
                  );
                })}
              </svg>

              {/* Agent Nodes */}
              {agents.map((agent) => (
                <div
                  key={agent.id}
                  className="absolute transform -translate-x-1/2 -translate-y-1/2"
                  style={{ left: agent.position.x, top: agent.position.y }}
                >
                  <Card className={`w-48 border-2 ${getAgentColor(agent.status)} border-opacity-20`}>
                    <CardContent className="p-3">
                      <div className="flex items-center gap-2 mb-2">
                        {getAgentIcon(agent.type)}
                        <div className="flex-1">
                          <h3 className="font-semibold text-sm">{agent.name}</h3>
                          <Badge className={`text-xs ${getAgentColor(agent.status)} text-white`}>
                            {agent.status}
                          </Badge>
                        </div>
                      </div>
                      
                      {agent.currentTask && (
                        <div className="mt-2 p-2 bg-blue-50 rounded text-xs">
                          <p className="font-medium">Current Task:</p>
                          <p className="text-gray-600 truncate">{agent.currentTask}</p>
                        </div>
                      )}
                      
                      <div className="mt-2">
                        <p className="text-xs font-medium">Capabilities:</p>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {agent.capabilities.slice(0, 2).map((cap, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {cap}
                            </Badge>
                          ))}
                          {agent.capabilities.length > 2 && (
                            <Badge variant="outline" className="text-xs">
                              +{agent.capabilities.length - 2}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Message Flow Log */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Real-time Message Flow
          </CardTitle>
          <CardDescription>
            Live A2A protocol communication log
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {messageFlows.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No messages yet. Start a workflow to see A2A communication.</p>
            ) : (
              messageFlows.slice(0, 20).map((flow) => (
                <div key={flow.id} className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="flex-shrink-0">
                    {flow.status === 'sending' && <ArrowRight className="h-4 w-4 text-blue-500" />}
                    {flow.status === 'delivered' && <CheckCircle className="h-4 w-4 text-green-500" />}
                    {flow.status === 'processing' && <Activity className="h-4 w-4 text-yellow-500 animate-pulse" />}
                    {flow.status === 'completed' && <CheckCircle className="h-4 w-4 text-green-600" />}
                    {flow.status === 'error' && <XCircle className="h-4 w-4 text-red-500" />}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm">{flow.from}</span>
                      <ArrowRight className="h-3 w-3 text-gray-400" />
                      <span className="font-medium text-sm">{flow.to}</span>
                      <Badge className={`text-xs ${getMessageColor(flow.status)}`}>
                        {flow.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">{flow.message}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(flow.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
