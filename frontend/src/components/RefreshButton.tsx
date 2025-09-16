// components/RefreshButton.tsx
"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE ?? "").replace(/\/$/, "");

export default function RefreshButton({ runIngest = false }: { runIngest?: boolean }) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [busy, setBusy] = useState(false);

  async function handleClick() {
    if (runIngest && API_BASE) {
      try {
        setBusy(true);
        await fetch(`${API_BASE}/api/ingest-and-save?limit=10`, { method: "POST" });
      } catch (e) {
        console.error("ingest failed:", e);
      } finally {
        setBusy(false);
      }
    }
    startTransition(() => router.refresh());
  }

  const loading = pending || busy;

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleClick}
      disabled={loading}
      className="flex items-center gap-2"
    >
      <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
      Atualizar
    </Button>
  );
}
