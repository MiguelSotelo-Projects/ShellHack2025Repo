'use client';

import { useState, useEffect } from 'react';
import { DashboardService } from '@/lib/services/dashboardService';
import { QueueService } from '@/lib/services/queueService';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

interface DashboardStats {
  queue_stats: {
    total_waiting: number;
    total_in_progress: number;
    total_called: number;
    walk_ins_waiting: number;
    appointments_waiting: number;
    urgent_waiting: number;
    high_waiting: number;
  };
  appointment_stats: {
    total_today: number;
    checked_in_today: number;
    completed_today: number;
    check_in_rate: number;
  };
  performance_metrics: {
    average_wait_time_minutes: number;
    recent_check_ins: number;
    recent_completions: number;
  };
}

interface QueueEntry {
  id: number;
  ticket_number: string;
  status: string;
  queue_type: string;
  priority: string;
  reason?: string;
  estimated_wait_time?: number;
  patient_name?: string;
  appointment_code?: string;
  created_at: string;
}

export default function LiveDashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [queueEntries, setQueueEntries] = useState<QueueEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchData = async () => {
    try {
      setError(null);
      const [statsData, queueData] = await Promise.all([
        DashboardService.getDashboardStats(),
        QueueService.getQueueEntries()
      ]);
      
      setStats(statsData);
      setQueueEntries(queueData);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'urgent': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'waiting': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'called': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'in_progress': return 'bg-green-100 text-green-800 border-green-200';
      case 'completed': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading dashboard data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="text-red-600">Connection Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={fetchData}>Retry Connection</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Live Hospital Dashboard</h1>
            <p className="text-gray-600">
              Real-time hospital operations monitoring
              {lastUpdated && (
                <span className="ml-2 text-sm">
                  • Last updated: {lastUpdated.toLocaleTimeString()}
                </span>
              )}
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant={autoRefresh ? "default" : "outline"}
              onClick={() => setAutoRefresh(!autoRefresh)}
            >
              {autoRefresh ? 'Auto Refresh ON' : 'Auto Refresh OFF'}
            </Button>
            <Button variant="outline" onClick={fetchData}>
              Refresh Now
            </Button>
          </div>
        </div>
      </div>

      {stats && (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Total Waiting</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">{stats.queue_stats.total_waiting}</div>
                <p className="text-xs text-gray-500">
                  {stats.queue_stats.walk_ins_waiting} walk-ins, {stats.queue_stats.appointments_waiting} appointments
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">In Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{stats.queue_stats.total_in_progress}</div>
                <p className="text-xs text-gray-500">Currently being served</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Check-in Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-600">{stats.appointment_stats.check_in_rate}%</div>
                <p className="text-xs text-gray-500">
                  {stats.appointment_stats.checked_in_today} of {stats.appointment_stats.total_today} today
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Avg Wait Time</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">{stats.performance_metrics.average_wait_time_minutes}m</div>
                <p className="text-xs text-gray-500">Average wait time</p>
              </CardContent>
            </Card>
          </div>

          {/* Priority Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Urgent Priority</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{stats.queue_stats.urgent_waiting}</div>
                <p className="text-xs text-gray-500">Requires immediate attention</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">High Priority</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">{stats.queue_stats.high_waiting}</div>
                <p className="text-xs text-gray-500">High priority cases</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Called</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-600">{stats.queue_stats.total_called}</div>
                <p className="text-xs text-gray-500">Ready for service</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-indigo-600">{stats.performance_metrics.recent_check_ins}</div>
                <p className="text-xs text-gray-500">Check-ins in last hour</p>
              </CardContent>
            </Card>
          </div>
        </>
      )}

      {/* Queue Entries */}
      <Card>
        <CardHeader>
          <CardTitle>Current Queue</CardTitle>
          <CardDescription>
            Real-time queue status with {queueEntries.length} entries
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {queueEntries.slice(0, 10).map((entry) => (
              <div key={entry.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="text-lg font-mono font-bold">{entry.ticket_number}</div>
                  <div>
                    <div className="font-medium">{entry.patient_name || 'Unknown Patient'}</div>
                    <div className="text-sm text-gray-500">{entry.reason}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={getPriorityColor(entry.priority)}>
                    {entry.priority.toUpperCase()}
                  </Badge>
                  <Badge className={getStatusColor(entry.status)}>
                    {entry.status.replace('_', ' ').toUpperCase()}
                  </Badge>
                  {entry.estimated_wait_time && (
                    <div className="text-sm text-gray-500">
                      ~{entry.estimated_wait_time}m wait
                    </div>
                  )}
                </div>
              </div>
            ))}
            {queueEntries.length > 10 && (
              <div className="text-center text-gray-500 py-2">
                ... and {queueEntries.length - 10} more entries
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
