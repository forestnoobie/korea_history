"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
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
    <div style={{
      minHeight: "100vh",
      background: `radial-gradient(ellipse at top, ${T.surface} 0%, ${T.appBg} 70%)`,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "40px 20px",
      fontFamily: T.serif,
    }}>
      <div style={{ maxWidth: 400, width: "100%", textAlign: "center" }}>
        {/* Crest + title */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16, marginBottom: 48 }}>
          <Crest color={T.ink} size={48} />
          <div>
            <div style={{
              fontFamily: T.serif, fontSize: 22, fontWeight: 700,
              letterSpacing: 1, color: T.ink, lineHeight: 1.2,
            }}>
              한국사 능력 검정
            </div>
            <div style={{
              fontFamily: T.mono, fontSize: 11, color: T.inkMuted,
              letterSpacing: 2, marginTop: 6, textTransform: "uppercase",
            }}>
              Korean History Exam
            </div>
          </div>
        </div>

        {/* Card */}
        <div style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: T.cardRadius,
          padding: "32px 28px",
        }}>
          <div style={{
            display: "inline-block",
            fontFamily: T.sans, fontSize: 10, fontWeight: 600,
            letterSpacing: 1.2, textTransform: "uppercase",
            color: T.accent,
            border: `1px solid ${T.accent}`,
            padding: "3px 8px", borderRadius: 2,
            marginBottom: 20,
          }}>
            제74회 · 심화
          </div>

          <p style={{
            fontFamily: T.serif, fontSize: 15, lineHeight: 1.7,
            color: T.inkSoft, marginBottom: 28,
          }}>
            제74회 한국사능력검정시험에서 무작위로 5문항을 출제합니다. 모든 문항에 답한 뒤 제출하세요.
          </p>

          {error && (
            <div style={{
              background: "rgba(160,43,31,0.08)",
              border: `1px solid ${T.accent}`,
              borderRadius: T.radius,
              padding: "10px 14px",
              marginBottom: 20,
              fontFamily: T.sans, fontSize: 13, color: T.accent,
            }}>
              {error}
            </div>
          )}

          <button
            onClick={handleStart}
            disabled={loading}
            style={{
              width: "100%", height: 48,
              background: loading ? T.surfaceAlt : T.ink,
              color: loading ? T.inkMuted : T.appBg,
              border: "none", borderRadius: T.radius,
              fontFamily: T.sans, fontSize: 15, fontWeight: 600,
              letterSpacing: 0.3, cursor: loading ? "default" : "pointer",
              transition: "all .15s",
              display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
            }}
          >
            {loading ? "불러오는 중…" : "시험 시작하기"}
            {!loading && (
              <svg width="13" height="13" viewBox="0 0 12 12" fill="none">
                <path d="M3 2l5 4-5 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            )}
          </button>
        </div>

        {/* Footer note */}
        <p style={{
          marginTop: 24, fontFamily: T.mono, fontSize: 10,
          color: T.inkMuted, letterSpacing: 1,
        }}>
          출처 · 국사편찬위원회
        </p>
      </div>
    </div>
  );
}
