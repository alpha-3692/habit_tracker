"use client";

import { BehaviorInsight } from "@/types";
import { Sparkles, CheckCircle2, AlertTriangle, Info } from "lucide-react";

interface BehavioralInsightsListProps {
  insights: BehaviorInsight[];
}

export function BehavioralInsightsList({
  insights,
}: BehavioralInsightsListProps) {
  if (!insights || insights.length === 0) {
    return null;
  }

  const getImpactStyles = (impact: "positive" | "neutral" | "warning") => {
    switch (impact) {
      case "positive":
        return {
          icon: <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />,
          border: "border-emerald-500/20 bg-emerald-950/10",
          badge: "bg-emerald-500/20 text-emerald-400",
        };
      case "warning":
        return {
          icon: <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0" />,
          border: "border-amber-500/20 bg-amber-950/10",
          badge: "bg-amber-500/20 text-amber-400",
        };
      default:
        return {
          icon: <Info className="w-5 h-5 text-indigo-400 flex-shrink-0" />,
          border: "border-indigo-500/20 bg-indigo-950/10",
          badge: "bg-indigo-500/20 text-indigo-400",
        };
    }
  };

  return (
    <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-6 shadow-xl space-y-6">
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h2 className="text-xl font-extrabold text-white tracking-tight">
            Behavioral Patterns & Insights
          </h2>
        </div>
        <p className="text-xs text-neutral-400">
          Automated pattern detection from your real execution logs.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {insights.map((insight, idx) => {
          const style = getImpactStyles(insight.impact);
          return (
            <div
              key={idx}
              className={`p-4 rounded-xl border flex items-start gap-3.5 transition shadow-md ${style.border}`}
            >
              {style.icon}
              <div className="space-y-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="text-xs font-bold text-white truncate">
                    {insight.title}
                  </h3>
                  <span className={`px-2 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wider ${style.badge}`}>
                    {insight.impact}
                  </span>
                </div>
                <p className="text-xs text-neutral-300 leading-relaxed">
                  {insight.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
