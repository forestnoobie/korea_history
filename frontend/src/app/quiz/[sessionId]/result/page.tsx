"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, type QuizResult } from "@/lib/api";
import { T } from "@/lib/theme";

function Crest({ color, size = 24 }: { color: string; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10.5" stroke={color} strokeWidth="1" />
      <path d="M12 2.5v19" stroke={color} strokeWidth="1" />
      <path d="M3 12c2.5-2.5 6.5-2.5 9 0s6.5 2.5 9 0" stroke={color} strokeWidth="1" fill="none" />
    </svg>
  );
}

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

  const pct = Math.round((result.score / result.total) * 100);
  const passed = pct >= 60;

  return (
    <div style={{
      minHeight: "100vh",
      background: `radial-gradient(ellipse at top, ${T.surface} 0%, ${T.appBg} 70%)`,
      display: "flex", flexDirection: "column",
      alignItems: "center",
      fontFamily: T.serif,
    }}>
      <div style={{
        width: "100%", maxWidth: 480,
        display: "flex", flexDirection: "column",
        minHeight: "100vh",
      }}>
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
            }}>한국사 능력 검정</div>
            <div style={{
              fontFamily: T.mono, fontSize: 10, color: T.inkMuted,
              letterSpacing: 1, marginTop: 3,
            }}>시험 결과</div>
          </div>
        </div>

        {/* Content */}
        <div style={{ flex: 1, padding: "32px 18px 28px" }}>
          {/* Score */}
          <div style={{
            background: T.surface,
            border: `1px solid ${T.line}`,
            borderRadius: T.cardRadius,
            padding: "32px 24px",
            textAlign: "center",
            marginBottom: 24,
          }}>
            <div style={{
              fontFamily: T.mono, fontSize: 10, fontWeight: 600,
              letterSpacing: 2, textTransform: "uppercase",
              color: T.inkMuted, marginBottom: 16,
            }}>최종 점수</div>

            <div style={{
              fontFamily: T.serif, fontSize: 64, fontWeight: 900,
              color: passed ? T.correct : T.wrong,
              lineHeight: 1, letterSpacing: -2,
            }}>
              {result.score}<span style={{ fontSize: 32, opacity: 0.5 }}>/{result.total}</span>
            </div>

            <div style={{
              fontFamily: T.mono, fontSize: 20, fontWeight: 600,
              color: T.ink, marginTop: 12, letterSpacing: 1,
            }}>
              {pct}%
            </div>

            <div style={{
              fontFamily: T.sans, fontSize: 13, color: T.inkMuted,
              marginTop: 6,
            }}>
              {result.points_earned} / {result.total_points}점
            </div>

            {/* Result dots */}
            <div style={{
              display: "flex", justifyContent: "center", gap: 8, marginTop: 24,
            }}>
              {result.results.map((r) => (
                <div
                  key={`${r.exam_id}_${r.question_no}`}
                  title={`Q${r.question_no}: ${r.is_correct ? "정답" : "오답"}`}
                  style={{
                    width: 22, height: 22, borderRadius: 999,
                    background: r.is_correct ? T.correct : T.wrong,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontFamily: T.mono, fontSize: 10, fontWeight: 600, color: "#fff",
                  }}
                >
                  {r.question_no}
                </div>
              ))}
            </div>
          </div>

          {/* Verdict */}
          <div style={{
            background: T.paper,
            border: `1px solid ${T.line}`,
            borderLeft: `3px solid ${passed ? T.correct : T.wrong}`,
            borderRadius: T.radius,
            padding: "12px 14px",
            marginBottom: 32,
          }}>
            <div style={{
              fontFamily: T.sans, fontSize: 10, fontWeight: 700,
              letterSpacing: 1.5, color: passed ? T.correct : T.wrong,
              textTransform: "uppercase", marginBottom: 4,
            }}>
              {passed ? "합격 · PASS" : "불합격 · FAIL"}
            </div>
            <div style={{
              fontFamily: T.serif, fontSize: 13, lineHeight: 1.7, color: T.inkSoft,
            }}>
              {passed
                ? "축하합니다! 60% 이상 득점하여 합격 기준을 충족하였습니다."
                : "아쉽게도 60% 미만 득점입니다. 오답 문제를 복습해보세요."}
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <button
              onClick={() => router.push(`/quiz/${sessionId}/review`)}
              style={{
                all: "unset", cursor: "pointer",
                height: 44, borderRadius: T.radius,
                border: `1px solid ${T.line}`,
                background: T.surface, color: T.inkSoft,
                fontFamily: T.sans, fontWeight: 600, fontSize: 14,
                letterSpacing: 0.3,
                display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
                transition: "all .15s",
              }}
            >
              오답 복습하기
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M3 2l5 4-5 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
            <button
              onClick={() => router.push("/")}
              style={{
                all: "unset", cursor: "pointer",
                height: 44, borderRadius: T.radius,
                background: T.ink, color: T.appBg,
                fontFamily: T.sans, fontWeight: 600, fontSize: 14,
                letterSpacing: 0.3,
                display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
                transition: "all .15s",
              }}
            >
              새 시험 시작하기
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M3 2l5 4-5 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
