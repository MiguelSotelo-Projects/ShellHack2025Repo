// components/shells/HospitalShell.tsx
"use client";

import React, { useState } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ClipboardList, LineChart, Settings, UsersRound, Loader2 } from "lucide-react";
import Link from "next/link";
import KpiCard from "@/components/ui-ext/KpiCard";
import { DashboardService, DashboardStats, QueueSummary, KPIs } from "@/lib/services/dashboardService";
import { useApi } from "@/lib/hooks/useApi";

export default function HospitalShell() {
  const [tab, setTab] = useState("overview");
  
  const { data: dashboardStats, loading: statsLoading, error: statsError } = useApi(DashboardService.getDashboardStats);
  const { data: queueSummary, loading: queueLoading, error: queueError } = useApi(DashboardService.getQueueSummary);
  const { data: kpis, loading: kpisLoading, error: kpisError } = useApi(DashboardService.getKPIs);

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Hospital Dashboard</h2>
          <p className="text-neutral-500 text-sm">Staff-facing, real-time visibility, manual actions.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button asChild variant="ghost">
            <Link href="/">Back</Link>
          </Button>
          <Button variant="secondary" className="gap-2">
            <Settings className="h-4 w-4" /> Settings
          </Button>
        </div>
      </div>

      <Tabs value={tab} onValueChange={setTab} className="bg-white/70 backdrop-blur rounded-xl border p-2">
        <TabsList className="grid grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="queue">Queue</TabsTrigger>
          <TabsTrigger value="kpis">KPIs</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="p-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UsersRound className="h-5 w-5" /> Overview
              </CardTitle>
              <CardDescription>At-a-glance status of current operations.</CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-neutral-600 space-y-2">
              {statsLoading ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Loading dashboard data...
                </div>
              ) : statsError ? (
                <p className="text-red-600">Error loading dashboard: {statsError}</p>
              ) : dashboardStats ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="rounded-lg border p-3">
                    <p className="font-medium">Queue Status</p>
                    <p>Waiting: {dashboardStats.queue_stats.total_waiting}</p>
                    <p>In Progress: {dashboardStats.queue_stats.total_in_progress}</p>
                    <p>Called: {dashboardStats.queue_stats.total_called}</p>
                  </div>
                  <div className="rounded-lg border p-3">
                    <p className="font-medium">Appointments Today</p>
                    <p>Total: {dashboardStats.appointment_stats.total_today}</p>
                    <p>Checked In: {dashboardStats.appointment_stats.checked_in_today}</p>
                    <p>Rate: {dashboardStats.appointment_stats.check_in_rate}%</p>
                  </div>
                  <div className="rounded-lg border p-3">
                    <p className="font-medium">Performance</p>
                    <p>Avg Wait: {dashboardStats.performance_metrics.average_wait_time_minutes}min</p>
                    <p>Recent Check-ins: {dashboardStats.performance_metrics.recent_check_ins}</p>
                    <p>Recent Completions: {dashboardStats.performance_metrics.recent_completions}</p>
                  </div>
                </div>
              ) : null}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="queue" className="p-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ClipboardList className="h-5 w-5" /> Queue
              </CardTitle>
              <CardDescription>Current queue status and patient list.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {queueLoading ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Loading queue data...
                </div>
              ) : queueError ? (
                <p className="text-red-600">Error loading queue: {queueError}</p>
              ) : queueSummary ? (
                <div className="space-y-4">
                  {queueSummary.waiting.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Waiting ({queueSummary.waiting.length})</h4>
                      {queueSummary.waiting.map((patient) => (
                        <div key={patient.id} className="rounded-md border p-3 flex items-center justify-between mb-2">
                          <div>
                            <span className="font-medium">{patient.ticket_number}</span>
                            <span className="text-neutral-500"> • {patient.patient_name}</span>
                            <span className="text-neutral-500"> • {patient.reason}</span>
                            <Badge variant="outline" className="ml-2">{patient.priority}</Badge>
                          </div>
                          <Badge variant="secondary">
                            {patient.estimated_wait_time ? `${patient.estimated_wait_time}m` : 'Pending'}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {queueSummary.called.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Called ({queueSummary.called.length})</h4>
                      {queueSummary.called.map((patient) => (
                        <div key={patient.id} className="rounded-md border p-3 flex items-center justify-between mb-2 bg-yellow-50">
                          <div>
                            <span className="font-medium">{patient.ticket_number}</span>
                            <span className="text-neutral-500"> • {patient.patient_name}</span>
                            <span className="text-neutral-500"> • {patient.reason}</span>
                          </div>
                          <Badge variant="default">Called</Badge>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {queueSummary.in_progress.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">In Progress ({queueSummary.in_progress.length})</h4>
                      {queueSummary.in_progress.map((patient) => (
                        <div key={patient.id} className="rounded-md border p-3 flex items-center justify-between mb-2 bg-green-50">
                          <div>
                            <span className="font-medium">{patient.ticket_number}</span>
                            <span className="text-neutral-500"> • {patient.patient_name}</span>
                            <span className="text-neutral-500"> • {patient.reason}</span>
                          </div>
                          <Badge variant="default" className="bg-green-600">In Progress</Badge>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {queueSummary.waiting.length === 0 && queueSummary.called.length === 0 && queueSummary.in_progress.length === 0 && (
                    <p className="text-neutral-500 text-center py-4">No patients in queue</p>
                  )}
                </div>
              ) : null}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="kpis" className="p-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LineChart className="h-5 w-5" /> KPIs
              </CardTitle>
              <CardDescription>Performance metrics and key indicators.</CardDescription>
            </CardHeader>
            <CardContent>
              {kpisLoading ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Loading KPI data...
                </div>
              ) : kpisError ? (
                <p className="text-red-600">Error loading KPIs: {kpisError}</p>
              ) : kpis ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <KpiCard 
                    label="Handoff latency" 
                    value={`${kpis.handoff_latency_seconds}s`} 
                    trend={kpis.handoff_latency_seconds < 2 ? "good" : kpis.handoff_latency_seconds < 5 ? "warn" : "bad"} 
                  />
                  <KpiCard 
                    label="End-to-end time" 
                    value={`${kpis.end_to_end_time_minutes}m`} 
                    trend={kpis.end_to_end_time_minutes < 30 ? "good" : kpis.end_to_end_time_minutes < 60 ? "warn" : "bad"} 
                  />
                  <KpiCard 
                    label="Auto-resolved" 
                    value={`${kpis.auto_resolved_percentage}%`} 
                    trend={kpis.auto_resolved_percentage > 90 ? "good" : kpis.auto_resolved_percentage > 75 ? "warn" : "bad"} 
                  />
                </div>
              ) : null}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
