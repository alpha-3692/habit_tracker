"use client";

import { useEffect, useState } from "react";
import { Trophy, X } from "lucide-react";

interface AchievementUnlockedToastProps {
  achievementCode: string;
  onClose: () => void;
}

const ACHIEVEMENT_TITLES: Record<string, { title: string; description: string }> = {
  streak_7: { title: "7-Day Streak", description: "You've maintained a 7-day consistency streak!" },
  streak_14: { title: "14-Day Streak", description: "Two full weeks of relentless consistency!" },
  streak_30: { title: "30-Day Streak", description: "One month strong! A true milestone of discipline." },
  streak_60: { title: "60-Day Streak", description: "Two months of unstoppable momentum." },
  streak_100: { title: "Centurion Streak", description: "100 consecutive days of mastery!" },
  first_completion: { title: "First Step", description: "You completed your very first habit!" },
  completions_10: { title: "Double Digits", description: "10 habit completions logged." },
  completions_50: { title: "Half Century", description: "50 habit completions reached!" },
  completions_100: { title: "Century Club", description: "100 habit completions logged!" },
  completions_500: { title: "Master of Habit", description: "500 habit completions reached!" },
  completions_1000: { title: "Legendary Discipline", description: "1000 habit completions!" },
  first_habit: { title: "Habit Builder", description: "Created your first habit." },
  active_habits_3: { title: "Trio Focus", description: "3 active habits in your daily routine." },
  active_habits_5: { title: "Solid Foundation", description: "5 active habits in your daily routine." },
  active_habits_10: { title: "Power Routine", description: "10 active habits in your daily routine." },
  first_goal: { title: "Visionary", description: "Created your first goal." },
  first_goal_completed: { title: "Mission Accomplished", description: "Completed your first goal!" },
  goals_completed_3: { title: "Triple Victory", description: "3 goals successfully completed!" },
};

export function AchievementUnlockedToast({
  achievementCode,
  onClose,
}: AchievementUnlockedToastProps) {
  const [visible, setVisible] = useState(true);

  const info = ACHIEVEMENT_TITLES[achievementCode] || {
    title: "Achievement Unlocked!",
    description: "You've earned a new milestone badge.",
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      onClose();
    }, 6000);
    return () => clearTimeout(timer);
  }, [onClose]);

  if (!visible) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-slide-up max-w-sm w-full">
      <div className="bg-[#1f1a14] border-2 border-amber-500/50 rounded-2xl p-4 shadow-2xl shadow-amber-500/20 flex items-start gap-3.5 backdrop-blur-md">
        <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center flex-shrink-0 text-amber-400">
          <Trophy className="w-5 h-5 fill-amber-400" />
        </div>

        <div className="space-y-0.5 flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] font-extrabold text-amber-400 uppercase tracking-wider">
              🎉 Milestone Unlocked
            </span>
          </div>
          <h4 className="text-sm font-extrabold text-amber-100 truncate">
            {info.title}
          </h4>
          <p className="text-xs text-neutral-300 line-clamp-2">
            {info.description}
          </p>
        </div>

        <button
          onClick={() => {
            setVisible(false);
            onClose();
          }}
          className="text-neutral-400 hover:text-white p-1 rounded-lg hover:bg-[#2e2e2e] transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
