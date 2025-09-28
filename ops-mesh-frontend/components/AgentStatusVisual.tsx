'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { api, fetchAPI } from '@/lib/api';

interface AgentStatus {
  agent_id: string;
  status: string;
  last_heartbeat: string;
  capabilities: string[];
  running: boolean;
}

interface AgentActivity {
  agent_id: string;
  activity: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error' | 'info';
}

export default function AgentStatusVisual() {
  const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>([]);
  const [agentActivities, setAgentActivities] = useState<AgentActivity[]>([]);
  const [loading, setLoading] = useState(false);

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

  const testAgentCommunication = async () => {
    setLoading(true);
    try {
      const data = await fetchAPI(api.agents.testCommunication, { method: 'GET' });
      
      // Add activity log
      const newActivity: AgentActivity = {
        agent_id: 'system',
        activity: 'Agent communication test completed',
        timestamp: new Date().toLocaleTimeString(),
        status: data.success ? 'success' : 'error'
      };
      
      setAgentActivities(prev => [newActivity, ...prev.slice(0, 9)]);
    } catch (error) {
      const newActivity: AgentActivity = {
        agent_id: 'system',
        activity: 'Agent communication test failed',
        timestamp: new Date().toLocaleTimeString(),
        status: 'error'
      };
      setAgentActivities(prev => [newActivity, ...prev.slice(0, 9)]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgentStatuses();
    
    // Refresh every 3 seconds
    const interval = setInterval(fetchAgentStatuses, 3000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string, running: boolean) => {
    if (!running) return 'bg-red-100 text-red-800 border-red-200';
    
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'inactive':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'starting':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getActivityColor = (status: AgentActivity['status']) => {
    switch (status) {
      case 'success':
        return 'text-green-600';
      case 'warning':
        return 'text-yellow-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-blue-600';
    }
  };

  const getAgentIcon = (agentId: string) => {
    switch (agentId) {
      case 'frontdesk_agent':
        return '🏥';
      case 'queue_agent':
        return '📋';
      case 'appointment_agent':
        return '📅';
      case 'notification_agent':
        return '🔔';
      case 'orchestrator_agent':
        return '🎯';
      default:
        return '🤖';
    }
  };

  const getAgentDescription = (agentId: string) => {
    switch (agentId) {
      case 'frontdesk_agent':
        return 'Handles patient registration and check-in';
      case 'queue_agent':
        return 'Manages patient queues and wait times';
      case 'appointment_agent':
        return 'Schedules and manages appointments';
      case 'notification_agent':
        return 'Sends alerts and notifications';
      case 'orchestrator_agent':
        return 'Coordinates complex workflows';
      default:
        return 'Specialized hospital agent';
    }
  };

  return (
    <div className="space-y-6">
      {/* Agent Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agentStatuses.map((agent) => (
          <Card key={agent.agent_id} className="relative">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{getAgentIcon(agent.agent_id)}</span>
                  <div>
                    <CardTitle className="text-lg">
                      {agent.agent_id.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </CardTitle>
                    <CardDescription className="text-xs">
                      {getAgentDescription(agent.agent_id)}
                    </CardDescription>
                  </div>
                </div>
                <Badge className={getStatusColor(agent.status, agent.running)}>
                  {agent.running ? 'ACTIVE' : 'INACTIVE'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-sm">
                  <span className="font-medium">Capabilities:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {agent.capabilities.slice(0, 3).map((capability, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {capability}
                      </Badge>
                    ))}
                    {agent.capabilities.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{agent.capabilities.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  Last heartbeat: {new Date(agent.last_heartbeat).toLocaleTimeString()}
                </div>
              </div>
            </CardContent>
            
            {/* Activity Indicator */}
            <div className="absolute top-2 right-2">
              <div className={`w-3 h-3 rounded-full ${
                agent.running ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`} />
            </div>
          </Card>
        ))}
      </div>

      {/* Agent Communication Test */}
      <Card>
        <CardHeader>
          <CardTitle>Agent Communication Test</CardTitle>
          <CardDescription>Test the A2A protocol communication between agents</CardDescription>
        </CardHeader>
        <CardContent>
          <Button 
            onClick={testAgentCommunication} 
            disabled={loading}
            className="w-full"
          >
            {loading ? 'Testing Communication...' : 'Test Agent Communication'}
          </Button>
        </CardContent>
      </Card>

      {/* Activity Log */}
      <Card>
        <CardHeader>
          <CardTitle>Agent Activity Log</CardTitle>
          <CardDescription>Real-time agent communication and activity</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {agentActivities.length > 0 ? (
              agentActivities.map((activity, index) => (
                <div key={index} className="flex items-start gap-2 text-sm p-2 border rounded">
                  <span className="text-gray-400 font-mono text-xs">{activity.timestamp}</span>
                  <span className={`font-medium ${getActivityColor(activity.status)}`}>
                    [{activity.status.toUpperCase()}]
                  </span>
                  <span className="text-gray-700">{activity.activity}</span>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-4">
                No activity yet. Test agent communication to see A2A protocol in action!
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
