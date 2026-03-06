import React, { useMemo } from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

export const BrandPosition: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const mainText = "酒店級日本食材";
  const subText = "下放到香港家庭";

  // Typewriter effect for main text
  const charsRevealed = interpolate(frame, [10, 80], [0, mainText.length], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const displayMain = mainText.slice(0, Math.floor(charsRevealed));

  // Cursor blink
  const cursorOpacity =
    Math.floor(charsRevealed) < mainText.length
      ? frame % 16 < 8
        ? 1
        : 0
      : interpolate(frame, [80, 90, 95], [1, 1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

  // Highlight bar behind text
  const highlightWidth = interpolate(frame, [85, 115], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Sub text
  const subOpacity = interpolate(frame, [95, 115], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const subY = interpolate(frame, [95, 115], [25, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Sub text typewriter
  const subCharsRevealed = interpolate(frame, [100, 140], [0, subText.length], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const displaySub = subText.slice(0, Math.floor(subCharsRevealed));

  // Decorative elements
  const decoOpacity = interpolate(frame, [60, 80], [0, 0.3], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Quote marks
  const quoteScale = spring({
    frame: frame - 5,
    fps,
    config: { damping: 60, stiffness: 100 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#FAFAF8",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
      }}
    >
      {/* Large decorative quote marks */}
      <div
        style={{
          position: "absolute",
          top: "22%",
          left: "15%",
          fontSize: 200,
          color: "rgba(212, 175, 55, 0.08)",
          fontFamily: "Georgia, serif",
          transform: `scale(${quoteScale})`,
          lineHeight: 1,
        }}
      >
        「
      </div>
      <div
        style={{
          position: "absolute",
          bottom: "22%",
          right: "15%",
          fontSize: 200,
          color: "rgba(212, 175, 55, 0.08)",
          fontFamily: "Georgia, serif",
          transform: `scale(${quoteScale})`,
          lineHeight: 1,
        }}
      >
        」
      </div>

      {/* Main text with typewriter */}
      <div style={{ textAlign: "center", position: "relative" }}>
        <div style={{ position: "relative", display: "inline-block" }}>
          {/* Highlight bar */}
          <div
            style={{
              position: "absolute",
              bottom: 5,
              left: 0,
              width: `${highlightWidth}%`,
              height: 16,
              background: "linear-gradient(90deg, rgba(212,175,55,0.15), rgba(200,16,46,0.1))",
              borderRadius: 4,
            }}
          />

          <span
            style={{
              fontSize: 72,
              fontWeight: 300,
              color: "#1a1a1a",
              fontFamily: "'Noto Serif JP', 'Yu Mincho', serif",
              letterSpacing: "0.12em",
              position: "relative",
            }}
          >
            {displayMain}
          </span>

          {/* Cursor */}
          <span
            style={{
              display: "inline-block",
              width: 3,
              height: 65,
              backgroundColor: "#D4AF37",
              marginLeft: 4,
              verticalAlign: "bottom",
              opacity: cursorOpacity,
            }}
          />
        </div>

        {/* Sub text */}
        <div
          style={{
            marginTop: 40,
            opacity: subOpacity,
            transform: `translateY(${subY}px)`,
          }}
        >
          <span
            style={{
              fontSize: 38,
              fontWeight: 300,
              color: "#666",
              fontFamily: "'Noto Sans JP', sans-serif",
              letterSpacing: "0.2em",
            }}
          >
            {displaySub}
          </span>
        </div>
      </div>

      {/* Side decorative lines */}
      {[-1, 1].map((dir) => {
        const lineHeight = interpolate(frame, [20, 60], [0, 200], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return (
          <div
            key={dir}
            style={{
              position: "absolute",
              [dir === -1 ? "left" : "right"]: 100,
              top: "50%",
              transform: "translateY(-50%)",
              width: 1,
              height: lineHeight,
              background: "linear-gradient(180deg, transparent, #D4AF37, transparent)",
              opacity: decoOpacity,
            }}
          />
        );
      })}

      {/* Small red seal/stamp */}
      <div
        style={{
          position: "absolute",
          bottom: 80,
          right: 120,
          opacity: interpolate(frame, [120, 140], [0, 0.6], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          transform: `rotate(-12deg) scale(${spring({
            frame: frame - 120,
            fps,
            config: { damping: 40, stiffness: 150 },
          })})`,
        }}
      >
        <svg width="70" height="70" viewBox="0 0 70 70">
          <rect x="5" y="5" width="60" height="60" rx="5" fill="none" stroke="#C8102E" strokeWidth="3" />
          <text x="35" y="42" textAnchor="middle" fill="#C8102E" fontSize="20" fontFamily="'Noto Serif JP', serif" fontWeight="700">
            極
          </text>
        </svg>
      </div>
    </AbsoluteFill>
  );
};
