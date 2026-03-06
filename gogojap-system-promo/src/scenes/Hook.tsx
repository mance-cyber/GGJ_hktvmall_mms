import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { C } from "../colors";
import { inter, noto } from "../fonts";

const getTypedText = (frame: number, text: string, charFrames: number): string => {
  const chars = Math.min(text.length, Math.floor(frame / charFrames));
  return text.slice(0, chars);
};

const dotBg: React.CSSProperties = {
  backgroundImage: `radial-gradient(${C.bgMuted} 1px, transparent 1px)`,
  backgroundSize: "24px 24px",
};

export const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoScale = spring({ frame, fps, from: 0.8, to: 1, durationInFrames: 40 });
  const tagline = "智能驅動 · 數據決策";
  const typedTagline = getTypedText(Math.max(0, frame - 50), tagline, 5);

  const cursorOpacity = Math.floor(frame / 15) % 2 === 0 ? 1 : 0;

  return (
    <AbsoluteFill style={{ ...dotBg, backgroundColor: C.bg, justifyContent: "center", alignItems: "center" }}>
      {/* Logo */}
      <div
        style={{
          transform: `scale(${logoScale})`,
          background: C.gradientBlue,
          borderRadius: 16,
          padding: "24px 48px",
          boxShadow: C.cardShadow,
        }}
      >
        <div
          style={{
            fontFamily: inter,
            fontSize: 64,
            fontWeight: 800,
            color: "#FFFFFF",
            letterSpacing: -1,
          }}
        >
          GoGoJap
        </div>
      </div>

      {/* Tagline */}
      <div
        style={{
          marginTop: 32,
          fontFamily: noto,
          fontSize: 28,
          color: C.textMuted,
          letterSpacing: 4,
          height: 40,
        }}
      >
        {typedTagline}
        <span style={{ opacity: cursorOpacity, color: C.primary }}>|</span>
      </div>
    </AbsoluteFill>
  );
};
