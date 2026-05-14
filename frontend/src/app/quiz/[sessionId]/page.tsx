"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Image from "next/image";
import { api, imageUrl, type QuizState } from "@/lib/api";
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

function ClockIcon({ color }: { color: string }) {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <circle cx="6" cy="6" r="5" stroke={color} strokeWidth="1" />
      <path d="M6 3v3l2 1.5" stroke={color} strokeWidth="1" strokeLinecap="round" />
    </svg>
  );
}

function ProgressTrail({
  total, current, answered,
}: { total: number; current: number; answered: Set<number> }) {
  return (
    <div style={{ display: "flex", gap: 6, alignItems: "center", flex: 1 }}>
      {Array.from({ length: total }).map((_, i) => {
        const isCurrent = i === current;
        const done = answered.has(i);
        const bg = isCurrent ? T.ink : done ? T.correct : T.lineSoft;
        const fg = isCurrent ? T.appBg : done ? "#fff" : T.inkMuted;
        return (
          <div key={i} style={{
            width: isCurrent ? 26 : 22, height: 22, borderRadius: 999,
            background: bg, color: fg,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: T.mono, fontSize: 11, fontWeight: 600,
            transition: "all .25s",
          }}>
            {i + 1}
          </div>
        );
      })}
    </div>
  );
}

export default function QuizPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const router = useRouter();

  const [session, setSession] = useState<QuizState | null>(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    api.getSession(sessionId).then(setSession).catch((e) => setError(e.message));
  }, [sessionId]);

  useEffect(() => {
    const id = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, []);

  const question = session?.questions[currentIdx];
  const total = session?.total_questions ?? 0;
  const answerKey = question ? `${question.exam_id}_${question.question_no}` : "";
  const selectedAnswer = answerKey ? (session?.answers[answerKey] ?? null) : null;
  const isLast = currentIdx === total - 1;
  const mm = String(Math.floor(seconds / 60)).padStart(2, "0");
  const ss = String(seconds % 60).padStart(2, "0");

  const answered = new Set(
    session?.questions.map((q, i) => {
      const k = `${q.exam_id}_${q.question_no}`;
      return session?.answers[k] != null ? i : -1;
    }).filter((i) => i >= 0) ?? []
  );

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
      <div style={{
        minHeight: "100vh", background: T.appBg,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: T.serif, color: T.accent,
      }}>
        {error}
      </div>
    );
  }

  if (!session || !question) {
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
    }}>
      <div style={{
        width: "100%", maxWidth: 480,
        display: "flex", flexDirection: "column",
        minHeight: "100vh",
        fontFamily: T.sans, color: T.ink,
      }}>
        {/* HEADER */}
        <div style={{
          padding: "14px 18px 10px",
          display: "flex", alignItems: "center", gap: 12,
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
            }}>제{session.exam_id}회 · 심화</div>
          </div>
          <div style={{
            width: 32, height: 32, borderRadius: 999,
            border: `1px solid ${T.line}`, background: T.surface,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <ClockIcon color={T.inkMuted} />
          </div>
        </div>

        {/* STATUS ROW */}
        <div style={{
          padding: "4px 18px 10px",
          display: "flex", alignItems: "center", gap: 14,
          borderBottom: `1px solid ${T.lineSoft}`,
        }}>
          <ProgressTrail total={total} current={currentIdx} answered={answered} />
          <div style={{
            display: "flex", alignItems: "center", gap: 5,
            fontFamily: T.mono, fontSize: 12, color: T.inkMuted,
          }}>
            <ClockIcon color={T.inkMuted} />
            <span style={{ fontWeight: 600, color: T.ink }}>{mm}:{ss}</span>
          </div>
        </div>

        {/* SCROLL AREA */}
        <div style={{ flex: 1, overflow: "auto", padding: "16px 18px 24px" }}>
          {/* Meta row */}
          <div style={{
            display: "flex", alignItems: "center", gap: 8, marginBottom: 12,
          }}>
            <span style={{ flex: 1 }} />
            <span style={{
              fontFamily: T.mono, fontSize: 11, color: T.inkMuted,
            }}>
              문항 {String(question.question_no).padStart(2, "0")}
            </span>
            <span style={{
              fontFamily: T.sans, fontWeight: 700, fontSize: 11,
              color: T.ink, background: T.surfaceAlt,
              padding: "3px 7px", borderRadius: 2,
            }}>
              {question.points}점
            </span>
          </div>

          {/* Question paper card: image + bottom selection strip */}
          <div style={{
            background: T.paper,
            border: `1px solid ${T.line}`,
            borderRadius: T.cardRadius,
            marginBottom: 18,
            position: "relative",
            overflow: "hidden",
          }}>
            {/* torn-edge top decoration */}
            <div style={{
              position: "absolute", top: 0, left: 14, right: 14, height: 6,
              backgroundImage: `repeating-linear-gradient(135deg, ${T.paper} 0 4px, transparent 4px 8px)`,
              zIndex: 1, pointerEvents: "none",
            }} />

            <Image
              src={imageUrl(question.image_path)}
              alt={`Question ${question.question_no}`}
              width={800}
              height={600}
              className="w-full object-contain"
              style={{ display: "block", padding: 4 }}
              unoptimized={true}
            />

            {/* Ornament divider */}
            <div style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "0 14px",
            }}>
              <div style={{ flex: 1, height: 1, background: T.line }} />
              <span style={{
                fontFamily: T.mono, fontSize: 9, letterSpacing: 2,
                color: T.inkMuted, textTransform: "uppercase",
              }}>선택지</span>
              <div style={{ flex: 1, height: 1, background: T.line }} />
            </div>

            {/* Selection strip — 5 circles in one row */}
            <div style={{
              display: "flex", gap: 8,
              padding: "12px 14px 14px",
            }}>
              {CIRCLED.map((label, i) => {
                const val = i + 1;
                const isSelected = selectedAnswer === val;
                return (
                  <button
                    key={val}
                    onClick={() => handleAnswer(val)}
                    aria-label={`선택지 ${val}`}
                    style={{
                      all: "unset",
                      cursor: session.submitted ? "default" : "pointer",
                      flex: 1, height: 48,
                      display: "flex", alignItems: "center", justifyContent: "center",
                      background: isSelected ? T.ink : T.surface,
                      color: isSelected ? T.appBg : T.inkSoft,
                      border: `1.5px solid ${isSelected ? T.ink : T.line}`,
                      borderRadius: T.radius,
                      fontFamily: T.serif, fontSize: 22, lineHeight: 1,
                      transition: "background .15s, color .15s, border-color .15s",
                    }}
                  >
                    {label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* BOTTOM ACTION BAR */}
        <div style={{
          padding: "12px 18px 28px",
          borderTop: `1px solid ${T.lineSoft}`,
          background: T.surface,
          display: "flex", gap: 10, alignItems: "center",
        }}>
          <button
            onClick={() => setCurrentIdx((i) => Math.max(0, i - 1))}
            disabled={currentIdx === 0}
            style={{
              all: "unset",
              cursor: currentIdx === 0 ? "default" : "pointer",
              width: 44, height: 44, borderRadius: T.radius,
              border: `1px solid ${T.line}`, color: T.inkSoft,
              display: "flex", alignItems: "center", justifyContent: "center",
              opacity: currentIdx === 0 ? 0.3 : 1,
            }}
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M9 2L4 7l5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>

          {isLast ? (
            <button
              onClick={handleSubmit}
              disabled={submitting || answered.size < total}
              style={{
                all: "unset",
                cursor: (submitting || answered.size < total) ? "default" : "pointer",
                flex: 1, height: 44, borderRadius: T.radius,
                background: (submitting || answered.size < total) ? T.surfaceAlt : T.ink,
                color: (submitting || answered.size < total) ? T.inkMuted : T.appBg,
                textAlign: "center", fontFamily: T.sans,
                fontWeight: 600, fontSize: 14, letterSpacing: 0.3,
                display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
                transition: "all .15s",
              }}
            >
              {submitting ? "제출 중…" : answered.size < total ? `${answered.size}/${total} 답변됨` : "결과 보기"}
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M3 2l5 4-5 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          ) : (
            <button
              onClick={() => setCurrentIdx((i) => Math.min(total - 1, i + 1))}
              style={{
                all: "unset", cursor: "pointer",
                flex: 1, height: 44, borderRadius: T.radius,
                background: T.ink, color: T.appBg,
                textAlign: "center", fontFamily: T.sans,
                fontWeight: 600, fontSize: 14, letterSpacing: 0.3,
                display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
                transition: "all .15s",
              }}
            >
              다음 문항
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M3 2l5 4-5 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
