"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Image from "next/image";
import { api, imageUrl, type QuizResult, type QuestionResult } from "@/lib/api";

const ANSWER_LABELS = ["①", "②", "③", "④", "⑤"];

function AnswerGrid({ item }: { item: QuestionResult }) {
  return (
    <div className="grid grid-cols-5 gap-2">
      {ANSWER_LABELS.map((label, i) => {
        const val = i + 1;
        const isCorrect = val === item.correct_answer;
        const isSelected = val === item.selected_answer;

        let cls = "rounded-xl border-2 py-2 text-lg font-semibold ";
        if (isCorrect) {
          cls += "border-green-500 bg-green-100 text-green-700";
        } else if (isSelected && !isCorrect) {
          cls += "border-red-400 bg-red-100 text-red-600";
        } else {
          cls += "border-gray-200 bg-white text-gray-400";
        }

        return (
          <div key={val} className={cls + " text-center"}>
            {label}
          </div>
        );
      })}
    </div>
  );
}

export default function ReviewPage() {
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

  const wrong = result.results.filter((r) => !r.is_correct);

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="mb-2 text-2xl font-bold">Wrong Answers Review</h1>
      <p className="mb-8 text-gray-500">
        {wrong.length === 0
          ? "Perfect score — no wrong answers!"
          : `${wrong.length} question${wrong.length > 1 ? "s" : ""} to review`}
      </p>

      {wrong.length === 0 ? (
        <p className="text-center text-green-600 text-xl font-semibold py-12">
          All correct!
        </p>
      ) : (
        <div className="flex flex-col gap-10">
          {wrong.map((item) => (
            <div
              key={`${item.exam_id}_${item.question_no}`}
              className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"
            >
              <p className="mb-3 text-sm font-medium text-gray-500">
                Question {item.question_no}
              </p>

              <div className="mb-4 overflow-hidden rounded-lg border border-gray-100">
                <Image
                  src={imageUrl(item.image_path)}
                  alt={`Question ${item.question_no}`}
                  width={700}
                  height={500}
                  className="w-full object-contain"
                  unoptimized={true}
                />
              </div>

              <AnswerGrid item={item} />

              <p className="mt-3 text-xs text-gray-400">
                Your answer:{" "}
                <span className="font-medium text-red-500">
                  {item.selected_answer
                    ? ANSWER_LABELS[item.selected_answer - 1]
                    : "Not answered"}
                </span>{" "}
                &nbsp;·&nbsp; Correct:{" "}
                <span className="font-medium text-green-600">
                  {ANSWER_LABELS[item.correct_answer - 1]}
                </span>
              </p>
            </div>
          ))}
        </div>
      )}

      <div className="mt-10 flex gap-3">
        <button
          onClick={() => router.push(`/quiz/${sessionId}/result`)}
          className="rounded-xl border-2 border-gray-300 bg-white px-5 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
        >
          Back to Results
        </button>
        <button
          onClick={() => router.push("/")}
          className="rounded-xl bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-700"
        >
          New Quiz
        </button>
      </div>
    </div>
  );
}
