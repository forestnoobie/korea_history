"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Image from "next/image";
import { api, imageUrl, type QuizState } from "@/lib/api";

const ANSWER_LABELS = ["①", "②", "③", "④", "⑤"];

export default function QuizPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const router = useRouter();

  const [session, setSession] = useState<QuizState | null>(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.getSession(sessionId).then(setSession).catch((e) => setError(e.message));
  }, [sessionId]);

  const question = session?.questions[currentIdx];
  const total = session?.total_questions ?? 0;
  const answerKey = question ? `${question.exam_id}_${question.question_no}` : "";
  const selectedAnswer = answerKey ? (session?.answers[answerKey] ?? null) : null;
  const isLast = currentIdx === total - 1;

  const handleAnswer = useCallback(
    async (choice: number) => {
      if (!question || !session || session.submitted) return;
      try {
        const updated = await api.submitAnswer(sessionId, {
          question_no: question.question_no,
          exam_id: question.exam_id,
          selected_answer: choice,
        });
        setSession(updated);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to record answer.");
      }
    },
    [question, session, sessionId]
  );

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await api.submitQuiz(sessionId);
      router.push(`/quiz/${sessionId}/result`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to submit quiz.");
      setSubmitting(false);
    }
  };

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  if (!session || !question) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-400">Loading…</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      {/* Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-sm text-gray-500 mb-1">
          <span>Question {currentIdx + 1} of {total}</span>
          <span>Exam #{session.exam_id}</span>
        </div>
        <div className="h-2 w-full rounded-full bg-gray-200">
          <div
            className="h-2 rounded-full bg-blue-500 transition-all"
            style={{ width: `${((currentIdx + 1) / total) * 100}%` }}
          />
        </div>
      </div>

      {/* Question image */}
      <div className="mb-6 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="relative w-full" style={{ maxHeight: "60vh", minHeight: 200 }}>
          <Image
            src={imageUrl(question.image_path)}
            alt={`Question ${question.question_no}`}
            width={800}
            height={600}
            className="w-full object-contain"
            style={{ maxHeight: "60vh" }}
            unoptimized={true}
          />
        </div>
      </div>

      {/* Answer buttons */}
      <div className="mb-8 grid grid-cols-5 gap-2">
        {ANSWER_LABELS.map((label, i) => {
          const val = i + 1;
          const isSelected = selectedAnswer === val;
          return (
            <button
              key={val}
              onClick={() => handleAnswer(val)}
              className={`rounded-xl border-2 py-3 text-lg font-semibold transition-colors
                ${isSelected
                  ? "border-blue-600 bg-blue-600 text-white shadow"
                  : "border-gray-200 bg-white text-gray-700 hover:border-blue-400 hover:bg-blue-50"
                }`}
            >
              {label}
            </button>
          );
        })}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentIdx((i) => Math.max(0, i - 1))}
          disabled={currentIdx === 0}
          className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-30"
        >
          Previous
        </button>

        {isLast ? (
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="rounded-xl bg-green-600 px-6 py-2 text-sm font-semibold text-white hover:bg-green-700 disabled:opacity-50"
          >
            {submitting ? "Submitting…" : "Submit Quiz"}
          </button>
        ) : (
          <button
            onClick={() => setCurrentIdx((i) => Math.min(total - 1, i + 1))}
            className="rounded-xl bg-blue-600 px-6 py-2 text-sm font-semibold text-white hover:bg-blue-700"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}
