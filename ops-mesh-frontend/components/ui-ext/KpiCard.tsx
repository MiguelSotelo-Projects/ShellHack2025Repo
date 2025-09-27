// components/ui-ext/KpiCard.tsx
"use client";

import React from "react";

export default function KpiCard({ label, value, trend }: { label: string; value: string; trend: "good" | "warn" | "bad" }) {
  const hue =
    trend === "good" ? "from-emerald-400 to-cyan-400" : trend === "warn" ? "from-amber-400 to-orange-400" : "from-rose-400 to-red-400";
  return (
    <div className="rounded-lg border p-4 shadow-sm">
      <p className="text-xs text-neutral-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
      <div className={`mt-2 h-1.5 w-full rounded-full bg-neutral-200 overflow-hidden`}>
        <div className={`h-full w-2/3 bg-gradient-to-r ${hue}`} />
      </div>
    </div>
  );
}
