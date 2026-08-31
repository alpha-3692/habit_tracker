"use client";

import { Reminder } from "@/types";
import { ReminderCard } from "./ReminderCard";
import { EmptyRemindersState } from "./EmptyRemindersState";

interface ReminderListProps {
  reminders: Reminder[];
  onToggleActive: (reminder: Reminder) => void;
  onEdit: (reminder: Reminder) => void;
  onDelete: (id: string) => void;
  onAddReminder: () => void;
  hasHabits: boolean;
}

export function ReminderList({
  reminders,
  onToggleActive,
  onEdit,
  onDelete,
  onAddReminder,
  hasHabits,
}: ReminderListProps) {
  if (reminders.length === 0) {
    return <EmptyRemindersState onAddReminder={onAddReminder} hasHabits={hasHabits} />;
  }

  return (
    <div className="space-y-3">
      {reminders.map((reminder) => (
        <ReminderCard
          key={reminder.id}
          reminder={reminder}
          onToggleActive={onToggleActive}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
