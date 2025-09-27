// components/ui-ext/HoverCard.tsx
"use client";

import React from "react";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";

export default function HoverCard({
  children,
  onClick,
  variant,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "default" | "outline";
}) {
  return (
    <motion.div
      whileHover={{ y: -2, rotate: -0.15 }}
      transition={{ type: "spring", stiffness: 280, damping: 22 }}
      onClick={onClick}
      className="cursor-pointer"
    >
      <Card className={`${variant === "outline" ? "border-dashed" : ""} shadow-sm border-neutral-200 hover:shadow-lg transition-all`}>
        {children}
      </Card>
    </motion.div>
  );
}
