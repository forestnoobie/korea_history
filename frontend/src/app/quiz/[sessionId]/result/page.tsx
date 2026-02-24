"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, type QuizResult } from "@/lib/api";

export default function ResultPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const router = useRouter();
  const [result, setResult] = useState<QuizResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getReview(sessionId).then(setResult).catch((e) => setError(e.message));
  }, [sessionId]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-400">Loading…</p>
      </div>
    );
  }

  const pct = Math.round((result.score / result.total) * 100);
  const passed = pct >= 60;

  return (
    <div className="mx-auto max-w-lg px-4 py-12 text-center">
      <h1 className="mb-2 text-2xl font-bold">Quiz Complete!</h1>

      {/* Score fraction */}
      <div
        className={`my-8 text-7xl font-extrabold tracking-tight ${
          passed ? "text-green-600" : "text-red-500"
        }`}
      >
        {result.score}/{result.total}
      </div>

      <p className="mb-1 text-xl text-gray-600">{pct}%</p>
      <p className="mb-8 text-gray-500">
        {result.points_earned} / {result.total_points} points
      </p>

      {/* Per-question dots */}
      <div className="mb-10 flex justify-center gap-3">
        {result.results.map((r) => (
          <div
            key={`${r.exam_id}_${r.question_no}`}
            title={`Q${r.question_no}: ${r.is_correct ? "Correct" : "Wrong"}`}
            className={`h-4 w-4 rounded-full ${
              r.is_correct ? "bg-green-500" : "bg-red-400"
            }`}
          />
        ))}
      </div>

      {/* Actions */}
      <div className="flex flex-col gap-3">
        <button
          onClick={() => router.push(`/quiz/${sessionId}/review`)}
          className="rounded-xl border-2 border-gray-300 bg-white px-6 py-3 font-semibold text-gray-700 hover:bg-gray-50"
        >
          Review Wrong Answers
        </button>
        <button
          onClick={() => router.push("/")}
          className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700"
        >
          New Quiz
        </button>
      </div>
    </div>
  );
}
