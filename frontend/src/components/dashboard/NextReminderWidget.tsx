"use client";

import { useEffect, useState } from "react";
import { NextReminder } from "@/types";
import { remindersApi } from "@/lib/api/reminders";
import { Bell, Clock, ArrowRight } from "lucide-react";
import Link from "next/link";

interface NextReminderWidgetProps {
  accessToken: string;
}

export function NextReminderWidget({ accessToken }: NextReminderWidgetProps) {
  const [nextReminder, setNextReminder] = useState<NextReminder | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    let mounted = true;
    const fetchNext = async () => {
      try {
        const res = await remindersApi.getNextReminder(accessToken);
        if (mounted) setNextReminder(res);
      } catch (err) {
        // Silently ignore if fails or empty
      } finally {
        if (mounted) setIsLoading(false);
      }
    };
    fetchNext();
    return () => {
      mounted = false;
    };
  }, [accessToken]);

  if (isLoading || !nextReminder) return null;

  return (
    <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-4 flex items-center justify-between gap-4 shadow-md hover:border-[#3e3e3e] transition">
      <div className="flex items-center gap-3.5">
        <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 flex-shrink-0">
          <Bell className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
              Next Reminder
            </span>
            <span className="text-xs text-amber-400 font-bold">
              • {nextReminder.next_occurrence}
            </span>
          </div>
          <p className="text-sm font-bold text-white tracking-tight">
            {nextReminder.habit_title}
          </p>
        </div>
      </div>

      <Link
        href="/reminders"
        className="flex items-center gap-1 text-xs font-semibold text-neutral-400 hover:text-amber-400 transition"
      >
        <span>Manage</span>
        <ArrowRight className="w-3.5 h-3.5" />
      </Link>
    </div>
  );
}
