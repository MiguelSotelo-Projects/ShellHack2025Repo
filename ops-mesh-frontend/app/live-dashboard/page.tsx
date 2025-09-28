'use client';

import { useState, useEffect } from 'react';
import { DashboardService } from '@/lib/services/dashboardService';
import { QueueService } from '@/lib/services/queueService';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { 
  User, 
  Clock, 
  Phone, 
  Trash2, 
  CheckCircle, 
  AlertCircle,
  Users,
  Activity,
  TrendingUp,
  BarChart3,
  PieChart as PieChartIcon,
  RefreshCw
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';

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
  const [dequeuing, setDequeuing] = useState<number | null>(null);

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

  const handleDequeue = async (queueId: number, ticketNumber: string) => {
    if (!confirm(`Are you sure you want to remove ${ticketNumber} from the queue?`)) {
      return;
    }

    setDequeuing(queueId);
    try {
      await QueueService.dequeuePatient(queueId);
      // Refresh data after successful dequeue
      await fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to dequeue patient');
    } finally {
      setDequeuing(null);
    }
  };

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
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${autoRefresh ? 'animate-spin' : ''}`} />
              {autoRefresh ? 'Auto Refresh ON' : 'Auto Refresh OFF'}
            </Button>
            <Button variant="outline" onClick={fetchData} className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4" />
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

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Queue Status Pie Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChartIcon className="h-5 w-5" />
                  Queue Status Distribution
                </CardTitle>
                <CardDescription>
                  Current distribution of patients by status
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Tooltip />
                    <Pie
                      data={[
                        { name: 'Waiting', value: stats.queue_stats.total_waiting, color: '#3B82F6' },
                        { name: 'In Progress', value: stats.queue_stats.total_in_progress, color: '#10B981' },
                        { name: 'Called', value: stats.queue_stats.total_called, color: '#F59E0B' }
                      ]}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {[
                        { name: 'Waiting', value: stats.queue_stats.total_waiting, color: '#3B82F6' },
                        { name: 'In Progress', value: stats.queue_stats.total_in_progress, color: '#10B981' },
                        { name: 'Called', value: stats.queue_stats.total_called, color: '#F59E0B' }
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Priority Distribution Bar Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Priority Distribution
                </CardTitle>
                <CardDescription>
                  Patients by priority level
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={[
                    { name: 'Urgent', value: stats.queue_stats.urgent_waiting, color: '#EF4444' },
                    { name: 'High', value: stats.queue_stats.high_waiting, color: '#F59E0B' },
                    { name: 'Medium', value: Math.max(0, stats.queue_stats.total_waiting - stats.queue_stats.urgent_waiting - stats.queue_stats.high_waiting), color: '#3B82F6' },
                    { name: 'Low', value: 0, color: '#10B981' }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Performance Metrics Chart */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Performance Trends
              </CardTitle>
              <CardDescription>
                Key performance indicators over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={[
                  { time: '9:00', waitTime: 25, patients: 8, efficiency: 85 },
                  { time: '10:00', waitTime: 30, patients: 12, efficiency: 78 },
                  { time: '11:00', waitTime: 28, patients: 15, efficiency: 82 },
                  { time: '12:00', waitTime: 35, patients: 18, efficiency: 75 },
                  { time: '13:00', waitTime: 30, patients: 16, efficiency: 80 },
                  { time: '14:00', waitTime: 32, patients: 14, efficiency: 77 },
                  { time: '15:00', waitTime: 28, patients: 11, efficiency: 83 }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="waitTime" stackId="1" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.6} />
                  <Area type="monotone" dataKey="efficiency" stackId="2" stroke="#10B981" fill="#10B981" fillOpacity={0.6} />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Currently Serving Patient */}
          {queueEntries.filter(entry => entry.status === 'in_progress').length > 0 && (
            <Card className="mb-6 border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-800">
                  <User className="h-5 w-5" />
                  Currently Serving
                </CardTitle>
                <CardDescription className="text-green-700">
                  Patients currently being served by staff
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {queueEntries
                    .filter(entry => entry.status === 'in_progress')
                    .map((entry) => (
                      <div key={entry.id} className="flex items-center justify-between p-4 bg-white rounded-lg border border-green-200">
                        <div className="flex items-center gap-4">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                            <div className="text-lg font-mono font-bold text-green-800">{entry.ticket_number}</div>
                          </div>
                          <div>
                            <div className="font-semibold text-green-800">{entry.patient_name || 'Unknown Patient'}</div>
                            <div className="text-sm text-green-600">{entry.reason}</div>
                            <div className="text-xs text-green-500">
                              Started: {new Date(entry.created_at).toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className="bg-green-100 text-green-800 border-green-300">
                            <Activity className="h-3 w-3 mr-1" />
                            IN PROGRESS
                          </Badge>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDequeue(entry.id, entry.ticket_number)}
                            disabled={dequeuing === entry.id}
                            className="text-red-600 border-red-200 hover:bg-red-50"
                          >
                            {dequeuing === entry.id ? (
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                            ) : (
                              <>
                                <Trash2 className="h-4 w-4 mr-1" />
                                Remove
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          )}

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
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Current Queue
          </CardTitle>
          <CardDescription>
            Real-time queue status with {queueEntries.length} entries
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {queueEntries.slice(0, 10).map((entry) => (
              <div key={entry.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="text-lg font-mono font-bold">{entry.ticket_number}</div>
                  <div>
                    <div className="font-medium">{entry.patient_name || 'Unknown Patient'}</div>
                    <div className="text-sm text-gray-500">{entry.reason}</div>
                    <div className="text-xs text-gray-400">
                      {new Date(entry.created_at).toLocaleTimeString()}
                    </div>
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
                    <div className="text-sm text-gray-500 flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      ~{entry.estimated_wait_time}m wait
                    </div>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDequeue(entry.id, entry.ticket_number)}
                    disabled={dequeuing === entry.id}
                    className="text-red-600 border-red-200 hover:bg-red-50"
                  >
                    {dequeuing === entry.id ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                    ) : (
                      <>
                        <Trash2 className="h-4 w-4 mr-1" />
                        Remove
                      </>
                    )}
                  </Button>
                </div>
              </div>
            ))}
            {queueEntries.length > 10 && (
              <div className="text-center text-gray-500 py-2">
                ... and {queueEntries.length - 10} more entries
              </div>
            )}
            {queueEntries.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium">No patients in queue</p>
                <p className="text-sm">All patients have been served</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
