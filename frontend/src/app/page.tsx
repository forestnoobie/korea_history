"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function LandingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleStart() {
    setLoading(true);
    setError(null);
    try {
      const session = await api.startQuiz(5, "74");
      router.push(`/quiz/${session.session_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start quiz.");
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8 px-4">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900">
          한국사 능력검정시험
        </h1>
        <p className="mt-3 text-lg text-gray-500">
          Korean History Qualification Exam Practice Quiz
        </p>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm text-center max-w-sm w-full">
        <p className="mb-6 text-gray-600">
          5 random questions from exam <strong>#74</strong>. Answer all, then
          submit to see your score.
        </p>

        {error && (
          <p className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}

        <button
          onClick={handleStart}
          disabled={loading}
          className="w-full rounded-xl bg-blue-600 px-6 py-3 text-base font-semibold text-white shadow hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? "Loading…" : "Start Quiz"}
        </button>
      </div>
    </div>
  );
}
