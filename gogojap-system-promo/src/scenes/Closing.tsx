import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { C } from "../colors";
import { inter, noto } from "../fonts";

const badges = ["Python", "Next.js", "Claude AI", "PostgreSQL"];

const dotBg: React.CSSProperties = {
  backgroundImage: `radial-gradient(${C.bgMuted} 1px, transparent 1px)`,
  backgroundSize: "24px 24px",
};

export const Closing: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleScale = spring({ frame, fps, from: 0.8, to: 1, durationInFrames: 45 });
  const titleOpacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  const badgesOpacity = interpolate(frame, [50, 80], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const badgesY = interpolate(frame, [50, 80], [20, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  const poweredOpacity = interpolate(frame, [100, 130], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  return (
    <AbsoluteFill style={{ ...dotBg, backgroundColor: C.bg, justifyContent: "center", alignItems: "center" }}>
      {/* Main Title */}
      <div
        style={{
          transform: `scale(${titleScale})`,
          opacity: titleOpacity,
          fontFamily: noto,
          fontSize: 64,
          fontWeight: 800,
          background: C.gradientBlue,
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          letterSpacing: 2,
        }}
      >
        AI 賦能電商未來
      </div>

      {/* Tech Badges */}
      <div
        style={{
          display: "flex",
          gap: 16,
          marginTop: 48,
          opacity: badgesOpacity,
          transform: `translateY(${badgesY}px)`,
        }}
      >
        {badges.map((b, i) => (
          <div
            key={i}
            style={{
              fontFamily: inter,
              fontSize: 14,
              fontWeight: 500,
              color: C.textMuted,
              backgroundColor: C.bgSoft,
              border: `1px solid ${C.border}`,
              borderRadius: 20,
              padding: "8px 20px",
            }}
          >
            {b}
          </div>
        ))}
      </div>

      {/* Powered by */}
      <div
        style={{
          marginTop: 48,
          opacity: poweredOpacity,
          fontFamily: inter,
          fontSize: 15,
          color: C.textLight,
          letterSpacing: 1,
        }}
      >
        Powered by Mercury Production
      </div>
    </AbsoluteFill>
  );
};
