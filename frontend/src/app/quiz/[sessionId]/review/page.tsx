"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Image from "next/image";
import { api, imageUrl, type QuizResult, type QuestionResult } from "@/lib/api";
import { T } from "@/lib/theme";

const CIRCLED = ["①", "②", "③", "④", "⑤"];

function Crest({ color, size = 24 }: { color: string; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10.5" stroke={color} strokeWidth="1" />
      <path d="M12 2.5v19" stroke={color} strokeWidth="1" />
      <path d="M3 12c2.5-2.5 6.5-2.5 9 0s6.5 2.5 9 0" stroke={color} strokeWidth="1" fill="none" />
    </svg>
  );
}

function AnswerRow({ item }: { item: QuestionResult }) {
  return (
    <div style={{ display: "flex", gap: 6 }}>
      {CIRCLED.map((label, i) => {
        const val = i + 1;
        const isCorrect = val === item.correct_answer;
        const isSelected = val === item.selected_answer;
        const border = isCorrect
          ? `1.5px solid ${T.correct}`
          : isSelected && !isCorrect
          ? `1.5px solid ${T.wrong}`
          : `1px solid ${T.line}`;
        const bg = isCorrect
          ? "rgba(63,107,58,0.08)"
          : isSelected && !isCorrect
          ? "rgba(160,43,31,0.08)"
          : T.surface;
        const color = isCorrect ? T.correct : isSelected && !isCorrect ? T.wrong : T.inkMuted;

        return (
          <div
            key={val}
            style={{
              flex: 1, height: 40, borderRadius: T.radius,
              border, background: bg,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontFamily: T.serif, fontSize: 16, color,
            }}
          >
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
      <div style={{
        minHeight: "100vh", background: T.appBg,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: T.serif, color: T.accent,
      }}>
        {error}
      </div>
    );
  }

  if (!result) {
    return (
      <div style={{
        minHeight: "100vh", background: T.appBg,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: T.mono, fontSize: 12, color: T.inkMuted, letterSpacing: 1,
      }}>
        불러오는 중…
      </div>
    );
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: `radial-gradient(ellipse at top, ${T.surface} 0%, ${T.appBg} 70%)`,
      display: "flex", flexDirection: "column",
      alignItems: "center",
      fontFamily: T.serif,
    }}>
      <div style={{ width: "100%", maxWidth: 480, display: "flex", flexDirection: "column", minHeight: "100vh" }}>
        {/* Header */}
        <div style={{
          padding: "14px 18px 10px",
          display: "flex", alignItems: "center", gap: 12,
          borderBottom: `1px solid ${T.lineSoft}`,
        }}>
          <Crest color={T.ink} size={22} />
          <div style={{ flex: 1 }}>
            <div style={{
              fontFamily: T.serif, fontSize: 15, fontWeight: 700,
              letterSpacing: 0.5, color: T.ink, lineHeight: 1,
            }}>오답 복습</div>
            <div style={{
              fontFamily: T.mono, fontSize: 10, color: T.inkMuted,
              letterSpacing: 1, marginTop: 3,
            }}>{result.score}/{result.total} 정답</div>
          </div>
          <button
            onClick={() => router.push(`/quiz/${sessionId}/result`)}
            style={{
              all: "unset", cursor: "pointer",
              fontFamily: T.mono, fontSize: 10, color: T.inkMuted,
              letterSpacing: 0.5, padding: "4px 8px",
              border: `1px solid ${T.line}`, borderRadius: T.radius,
            }}
          >
            결과로
          </button>
        </div>

        {/* Question cards */}
        <div style={{ flex: 1, padding: "20px 18px 28px", display: "flex", flexDirection: "column", gap: 24 }}>
          {result.results.map((item) => (
            <div
              key={`${item.exam_id}_${item.question_no}`}
              style={{
                background: T.surface,
                border: `1px solid ${T.line}`,
                borderLeft: `3px solid ${item.is_correct ? T.correct : T.wrong}`,
                borderRadius: T.cardRadius,
                overflow: "hidden",
              }}
            >
              {/* Card header */}
              <div style={{
                padding: "10px 14px",
                display: "flex", alignItems: "center", gap: 8,
                borderBottom: `1px solid ${T.lineSoft}`,
              }}>
                <span style={{
                  fontFamily: T.mono, fontSize: 11, color: T.inkMuted,
                }}>
                  문항 {String(item.question_no).padStart(2, "0")}
                </span>
                <span style={{ flex: 1 }} />
                <span style={{
                  fontFamily: T.sans, fontSize: 10, fontWeight: 700,
                  letterSpacing: 1, textTransform: "uppercase",
                  color: item.is_correct ? T.correct : T.wrong,
                  padding: "2px 8px",
                  border: `1px solid ${item.is_correct ? T.correct : T.wrong}`,
                  borderRadius: 2,
                }}>
                  {item.is_correct ? "정답" : "오답"}
                </span>
              </div>

              {/* Image */}
              <div style={{ background: T.paper, padding: 4 }}>
                <Image
                  src={imageUrl(item.image_path)}
                  alt={`Question ${item.question_no}`}
                  width={700}
                  height={500}
                  className="w-full object-contain"
                  style={{ display: "block", borderRadius: T.radius }}
                  unoptimized={true}
                />
              </div>

              {/* Answer row */}
              <div style={{ padding: "12px 14px 14px" }}>
                <AnswerRow item={item} />
                <div style={{
                  marginTop: 10, display: "flex", gap: 14,
                  fontFamily: T.mono, fontSize: 11, color: T.inkMuted,
                }}>
                  <span>
                    내 답:{" "}
                    <span style={{ color: item.is_correct ? T.correct : T.wrong, fontWeight: 600 }}>
                      {item.selected_answer ? CIRCLED[item.selected_answer - 1] : "미답변"}
                    </span>
                  </span>
                  <span>
                    정답:{" "}
                    <span style={{ color: T.correct, fontWeight: 600 }}>
                      {CIRCLED[item.correct_answer - 1]}
                    </span>
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div style={{
          padding: "12px 18px 28px",
          borderTop: `1px solid ${T.lineSoft}`,
          background: T.surface,
          display: "flex", gap: 10,
        }}>
          <button
            onClick={() => router.push(`/quiz/${sessionId}/result`)}
            style={{
              all: "unset", cursor: "pointer",
              flex: 1, height: 44, borderRadius: T.radius,
              border: `1px solid ${T.line}`,
              background: T.surface, color: T.inkSoft,
              fontFamily: T.sans, fontWeight: 600, fontSize: 14,
              display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
            }}
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M9 2L4 7l5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            결과로 돌아가기
          </button>
          <button
            onClick={() => router.push("/")}
            style={{
              all: "unset", cursor: "pointer",
              flex: 1, height: 44, borderRadius: T.radius,
              background: T.ink, color: T.appBg,
              fontFamily: T.sans, fontWeight: 600, fontSize: 14,
              display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
            }}
          >
            새 시험
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M3 2l5 4-5 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
