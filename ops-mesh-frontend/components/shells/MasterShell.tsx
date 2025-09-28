"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Activity, Hospital, MonitorSmartphone, Sparkles, ArrowRight } from "lucide-react";
import Link from "next/link";
import HoverCard from "@/components/ui-ext/HoverCard";

export default function MasterShell() {
  return (
    <div className="relative min-h-dvh w-full overflow-hidden bg-gradient-to-b from-white via-neutral-50 to-white">
      {/* soft background accents */}
      <div aria-hidden className="pointer-events-none absolute -top-24 -left-24 h-80 w-80 rounded-full bg-gradient-to-tr from-emerald-200/50 to-cyan-200/40 blur-3xl animate-pulse" />
      <div aria-hidden className="pointer-events-none absolute -bottom-24 -right-24 h-96 w-96 rounded-full bg-gradient-to-tr from-indigo-200/40 to-fuchsia-200/40 blur-3xl animate-[pulse_6s_ease-in-out_infinite]" />

      <div className="relative mx-auto max-w-6xl px-4 py-10">
        <header className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1.5">
            <div className="inline-flex items-center gap-2 rounded-full border bg-white/70 px-3 py-1 text-xs text-neutral-600 backdrop-blur">
              <Sparkles className="h-3.5 w-3.5" />
              Ops Mesh – Dual Dashboards
            </div>
            <h1 className="text-3xl md:text-4xl font-semibold tracking-tight">Choose your workspace</h1>
            <p className="text-sm text-neutral-500">
              Set up a <strong>Front Tablet</strong> for patients or open the <strong>Hospital Dashboard</strong> for staff.
            </p>
          </div>
          <Badge variant="outline" className="gap-1 bg-white/70 backdrop-blur">
            <Activity className="h-3.5 w-3.5" /> Live
          </Badge>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <HoverCard>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MonitorSmartphone className="h-5 w-5" /> Front Tablet (User/Kiosk)
              </CardTitle>
              <CardDescription>Appointment vs Walk-in, check-in tickets, friendly animations.</CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-neutral-600 space-y-2">
              <p>Mobile-first screens for reception tablets. Supports appointment code with retry → walk-in fallback.</p>
              <ul className="list-disc pl-5">
                <li>Appointment: code + last name → confirm</li>
                <li>Walk-in: reason/urgency → ETA</li>
                <li>Ticket + QR placeholder</li>
              </ul>
            </CardContent>
            <CardFooter className="justify-end">
              <Button asChild className="group">
                <Link href="/tablet">
                  Open Tablet Setup <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </Link>
              </Button>
            </CardFooter>
          </HoverCard>

          <HoverCard variant="outline">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Hospital className="h-5 w-5" /> Hospital Dashboard (Staff)
              </CardTitle>
              <CardDescription>Queues, swimlanes, KPIs, and failure toggles for demos.</CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-neutral-600 space-y-2">
              <p>Operational view for bed/transport/imaging. Real-time feed via WS; manual actions via API.</p>
              <ul className="list-disc pl-5">
                <li>Queues & triage list</li>
                <li>Swimlanes with live event chips</li>
                <li>KPIs (handoff latency, E2E time)</li>
              </ul>
            </CardContent>
            <CardFooter className="justify-end">
              <Button asChild variant="outline" className="group">
                <Link href="/hospital">
                  Open Hospital Dashboard <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </Link>
              </Button>
            </CardFooter>
          </HoverCard>

          <HoverCard variant="outline">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" /> Enhanced Dashboard
              </CardTitle>
              <CardDescription>Real-time patient management, queue monitoring, and agent status.</CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-neutral-600 space-y-2">
              <p>Advanced dashboard with visual agent monitoring, patient management, and queue operations.</p>
              <ul className="list-disc pl-5">
                <li>Visual agent status with activity indicators</li>
                <li>Patient management and status updates</li>
                <li>Queue management with dequeue operations</li>
                <li>Real-time statistics and monitoring</li>
              </ul>
            </CardContent>
            <CardFooter className="justify-end">
              <Button asChild variant="outline" className="group">
                <Link href="/enhanced-dashboard">
                  Open Enhanced Dashboard <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </Link>
              </Button>
            </CardFooter>
          </HoverCard>
        </div>

        <Separator className="my-8" />
        <p className="text-xs text-neutral-500">
          Tip: Keep this as the root route and maintain separate <code>/tablet</code> and <code>/hospital</code> apps.
        </p>
      </div>
    </div>
  );
}
