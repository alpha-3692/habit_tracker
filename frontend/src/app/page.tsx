import Link from "next/link";
import { Sparkles, ArrowRight, ShieldCheck, Zap, Activity } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0f0f0f] text-white flex flex-col items-center justify-center px-4 py-16">
      <div className="max-w-3xl text-center space-y-8">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          <span>HabitForge — AI-Powered Consistency Coach</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight text-white">
          Turn goals into sustainable <span className="text-indigo-500">daily habits.</span>
        </h1>

        <p className="text-lg text-neutral-400 max-w-xl mx-auto">
          Understand your behavior, maintain backend-verified streaks, and build long-term consistency with intelligent coaching.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            href="/signup"
            className="w-full sm:w-auto px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl transition flex items-center justify-center gap-2 shadow-xl shadow-indigo-600/25"
          >
            <span>Get Started Free</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/login"
            className="w-full sm:w-auto px-8 py-4 bg-[#242424] hover:bg-[#2e2e2e] text-neutral-300 font-semibold text-sm rounded-xl border border-[#333] transition"
          >
            Sign In
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-12 text-left">
          <div className="p-5 rounded-2xl bg-[#1a1a1a] border border-[#2e2e2e] space-y-2">
            <Zap className="w-5 h-5 text-indigo-400" />
            <h3 className="font-semibold text-white text-sm">Goal-Linked Habits</h3>
            <p className="text-xs text-neutral-400">
              Associate daily habits directly with long-term target outcomes.
            </p>
          </div>
          <div className="p-5 rounded-2xl bg-[#1a1a1a] border border-[#2e2e2e] space-y-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="font-semibold text-white text-sm">Authoritative Streaks</h3>
            <p className="text-xs text-neutral-400">
              Backend-calculated streaks derived from historical log entries.
            </p>
          </div>
          <div className="p-5 rounded-2xl bg-[#1a1a1a] border border-[#2e2e2e] space-y-2">
            <Activity className="w-5 h-5 text-violet-400" />
            <h3 className="font-semibold text-white text-sm">Behavioral Insights</h3>
            <p className="text-xs text-neutral-400">
              AI analysis to help recover momentum after missed days.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
