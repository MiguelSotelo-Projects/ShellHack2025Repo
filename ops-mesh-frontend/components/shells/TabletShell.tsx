// components/shells/TabletShell.tsx
"use client";

import React, { useMemo, useState } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Loader2, Settings, TriangleAlert, CheckCircle2, Clock, QrCode } from "lucide-react";
import Link from "next/link";
import { decideNextAfterInvalid, validateAppointmentInput } from "@/utils/validation";
import { AppointmentService, AppointmentCheckIn } from "@/lib/services/appointmentService";
import { QueueService, WalkInRequest } from "@/lib/services/queueService";
import { useApi, useApiMutation } from "@/lib/hooks/useApi";

export default function TabletShell() {
  const [tab, setTab] = useState("appointment");
  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Front Tablet</h2>
          <p className="text-neutral-500 text-sm">Patient-facing, large touch targets, minimal steps.</p>
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
          <TabsTrigger value="appointment">Appointment</TabsTrigger>
          <TabsTrigger value="walkin">Walk-in</TabsTrigger>
          <TabsTrigger value="status">Status</TabsTrigger>
        </TabsList>

        <TabsContent value="appointment" className="p-4">
          <AppointmentMini onRouteWalkIn={() => setTab("walkin")} />
        </TabsContent>
        <TabsContent value="walkin" className="p-4">
          <WalkInMini />
        </TabsContent>
        <TabsContent value="status" className="p-4">
          <StatusMini />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function AppointmentMini({ onRouteWalkIn }: { onRouteWalkIn: () => void }) {
  const [code, setCode] = useState("");
  const [last, setLast] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [attempts, setAttempts] = useState(0);
  const [confirmed, setConfirmed] = useState<any | null>(null);

  const checkInMutation = useApiMutation(AppointmentService.checkInAppointment);

  async function submit() {
    const validation = validateAppointmentInput(code, last);
    if (validation) {
      const next = decideNextAfterInvalid(attempts + 1);
      setAttempts((a) => a + 1);
      if (next === "retry") {
        setError("We couldn't verify that. Please try again — double-check your code and last name.");
        return;
      }
      // walk-in path
      setError(null);
      onRouteWalkIn();
      return;
    }

    try {
      setError(null);
      const appointment = await checkInMutation.mutate({
        confirmation_code: code,
        last_name: last,
      });
      
      setConfirmed({
        apptId: appointment.confirmation_code,
        time: new Date(appointment.scheduled_time).toLocaleTimeString(),
        provider: appointment.provider_name,
      });
    } catch (err) {
      const next = decideNextAfterInvalid(attempts + 1);
      setAttempts((a) => a + 1);
      if (next === "retry") {
        setError("We couldn't verify that. Please try again — double-check your code and last name.");
      } else {
        setError(null);
        onRouteWalkIn();
      }
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Appointment check-in</CardTitle>
        <CardDescription>Enter your confirmation code & last name.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {error && (
          <div className="flex items-center gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            <TriangleAlert className="h-4 w-4" /> {error}
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <Label htmlFor="code">Confirmation code</Label>
            <Input id="code" placeholder="ABCD-1234" value={code} onChange={(e) => setCode(e.target.value)} />
          </div>
          <div>
            <Label htmlFor="last">Last name</Label>
            <Input id="last" placeholder="Sotelo" value={last} onChange={(e) => setLast(e.target.value)} />
          </div>
          <div className="flex items-end">
            <Button className="w-full" onClick={submit} disabled={checkInMutation.loading}>
              {checkInMutation.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Confirm"}
            </Button>
          </div>
        </div>

        {confirmed && (
          <div className="mt-4 rounded-lg border p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-500">Appointment</span>
              <Badge variant="secondary">{confirmed.time}</Badge>
            </div>
            <p className="font-medium">with {confirmed.provider}</p>
            <div className="mt-3 flex justify-end">
              <Button className="gap-2">
                <CheckCircle2 className="h-4 w-4" /> Check-in now
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function WalkInMini() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [reason, setReason] = useState("");
  const [urgency, setUrgency] = useState<"low" | "medium" | "high" | "urgent">("medium");
  const [phone, setPhone] = useState("");
  const [eta, setEta] = useState<number | null>(null);
  const [ticketNumber, setTicketNumber] = useState<string | null>(null);

  const walkInMutation = useApiMutation(QueueService.createWalkIn);

  async function submitWalkIn() {
    if (!firstName.trim() || !lastName.trim() || !reason.trim()) {
      return;
    }

    try {
      const queueEntry = await walkInMutation.mutate({
        first_name: firstName,
        last_name: lastName,
        reason: reason,
        priority: urgency,
        phone: phone || undefined,
      });
      
      setTicketNumber(queueEntry.ticket_number);
      setEta(queueEntry.estimated_wait_time || 30);
    } catch (err) {
      console.error("Failed to create walk-in:", err);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Walk-in intake</CardTitle>
        <CardDescription>Tell us why you’re here and how urgent it feels.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <Label htmlFor="firstName">First Name</Label>
            <Input id="firstName" placeholder="John" value={firstName} onChange={(e) => setFirstName(e.target.value)} />
          </div>
          <div>
            <Label htmlFor="lastName">Last Name</Label>
            <Input id="lastName" placeholder="Doe" value={lastName} onChange={(e) => setLastName(e.target.value)} />
          </div>
        </div>
        <div>
          <Label htmlFor="phone">Phone (Optional)</Label>
          <Input id="phone" placeholder="(555) 123-4567" value={phone} onChange={(e) => setPhone(e.target.value)} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <Label htmlFor="reason">Reason</Label>
            <Input id="reason" placeholder="Headache, abdominal pain, check-up..." value={reason} onChange={(e) => setReason(e.target.value)} />
          </div>
          <div>
            <Label>Urgency</Label>
            <Select value={urgency} onValueChange={setUrgency}>
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
        <div className="flex items-center gap-3">
          <Button onClick={submitWalkIn} disabled={walkInMutation.loading} className="gap-2">
            {walkInMutation.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Submit Walk-in"}
          </Button>
          {eta !== null && ticketNumber && (
            <span className="inline-flex items-center gap-2 rounded-md border bg-neutral-50 px-3 py-2 text-sm">
              <Clock className="h-4 w-4" /> Ticket {ticketNumber} - ~{eta} min
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function StatusMini() {
  const eta = useMemo(() => Math.floor(Math.random() * 9) + 8, []);
  return (
    <Card>
      <CardHeader>
        <CardTitle>Check-in ticket</CardTitle>
        <CardDescription>Show this to a greeter if asked.</CardDescription>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
        <div className="md:col-span-2">
          <div className="rounded-lg border p-4 shadow-sm">
            <p className="text-sm text-neutral-500">Ticket</p>
            <p className="text-2xl font-semibold tracking-widest">C-1027</p>
            <div className="mt-2 flex items-center gap-2 text-sm text-neutral-600">
              <Clock className="h-4 w-4" /> Estimated escort in ~{eta} min
            </div>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center gap-2">
          <QrCode className="h-28 w-28 text-neutral-400" />
          <p className="text-xs text-neutral-500">(QR placeholder)</p>
        </div>
      </CardContent>
    </Card>
  );
}
