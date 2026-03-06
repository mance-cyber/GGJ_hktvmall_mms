import React, { useMemo } from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
} from "remotion";

// Sakura petal
const SakuraPetal: React.FC<{
  x: number;
  delay: number;
  size: number;
  rotation: number;
  speed: number;
}> = ({ x, delay, size, rotation, speed }) => {
  const frame = useCurrentFrame();
  const adj = Math.max(0, frame - delay);

  const y = interpolate(adj, [0, 150], [-50, 1200], { extrapolateRight: "clamp" });
  const rot = interpolate(adj, [0, 150], [rotation, rotation + 360 * (speed > 0.5 ? 1 : -1)], {
    extrapolateRight: "clamp",
  });
  const sway = Math.sin(adj * 0.08 + x) * 30;
  const opacity = interpolate(adj, [0, 10, 120, 150], [0, 0.5, 0.4, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 30 30"
      style={{
        position: "absolute",
        left: `${x}%`,
        top: y,
        transform: `rotate(${rot}deg) translateX(${sway}px)`,
        opacity,
      }}
    >
      <path
        d="M15 2 Q20 8 22 15 Q20 22 15 28 Q10 22 8 15 Q10 8 15 2Z"
        fill="#FFD4DC"
        opacity={0.7}
      />
    </svg>
  );
};

export const Closing: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Logo entrance
  const logoScale = spring({
    frame: frame - 10,
    fps,
    config: { damping: 50, stiffness: 80, mass: 1.5 },
  });

  const logoOpacity = interpolate(frame, [10, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Tagline
  const taglineOpacity = interpolate(frame, [50, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const taglineY = interpolate(frame, [50, 70], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // CTA button
  const ctaScale = spring({
    frame: frame - 90,
    fps,
    config: { damping: 40, stiffness: 120 },
  });
  const ctaOpacity = interpolate(frame, [90, 110], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // HKTVmall badge
  const badgeOpacity = interpolate(frame, [70, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Final fade out (last 30 frames)
  const fadeOut = interpolate(frame, [170, 200], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Gold ring animation
  const ringProgress = interpolate(frame, [5, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Sakura petals
  const petals = useMemo(() => {
    const p = [];
    for (let i = 0; i < 20; i++) {
      p.push({
        x: ((i * 47 + 13) % 100),
        delay: 30 + ((i * 7) % 60),
        size: 15 + ((i * 11) % 15),
        rotation: (i * 73) % 360,
        speed: (i % 3) * 0.3 + 0.2,
      });
    }
    return p;
  }, []);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#FAFAF8",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
        opacity: fadeOut,
      }}
    >
      {/* Sakura petals */}
      {petals.map((p, i) => (
        <SakuraPetal key={i} {...p} />
      ))}

      {/* Gold ring behind logo */}
      <svg
        width="300"
        height="300"
        viewBox="0 0 300 300"
        style={{
          position: "absolute",
          opacity: 0.15,
        }}
      >
        <circle
          cx="150"
          cy="150"
          r="130"
          fill="none"
          stroke="#D4AF37"
          strokeWidth="1.5"
          strokeDasharray={`${2 * Math.PI * 130}`}
          strokeDashoffset={2 * Math.PI * 130 * (1 - ringProgress)}
        />
        <circle
          cx="150"
          cy="150"
          r="120"
          fill="none"
          stroke="#D4AF37"
          strokeWidth="0.5"
          strokeDasharray={`${2 * Math.PI * 120}`}
          strokeDashoffset={2 * Math.PI * 120 * (1 - ringProgress * 0.9)}
        />
      </svg>

      {/* Logo area */}
      <div
        style={{
          textAlign: "center",
          transform: `scale(${logoScale})`,
          opacity: logoOpacity,
        }}
      >
        {/* GoGoJap Logo text */}
        <div
          style={{
            fontSize: 80,
            fontWeight: 200,
            color: "#1a1a1a",
            letterSpacing: "0.1em",
            fontFamily: "'Noto Serif JP', 'Yu Mincho', serif",
          }}
        >
          GoGoJap
        </div>

        {/* Small red circle mark */}
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            marginTop: 8,
          }}
        >
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: "#C8102E",
            }}
          />
          <span
            style={{
              fontSize: 16,
              color: "#999",
              letterSpacing: "0.4em",
              fontFamily: "'Noto Sans JP', sans-serif",
              fontWeight: 300,
            }}
          >
            by GoGoFoods
          </span>
        </div>
      </div>

      {/* Tagline */}
      <div
        style={{
          position: "absolute",
          top: "62%",
          textAlign: "center",
          opacity: taglineOpacity,
          transform: `translateY(${taglineY}px)`,
        }}
      >
        <div
          style={{
            fontSize: 28,
            fontWeight: 300,
            color: "#555",
            letterSpacing: "0.25em",
            fontFamily: "'Noto Sans JP', sans-serif",
          }}
        >
          酒店級日本食材 · 送到你家
        </div>
      </div>

      {/* HKTVmall badge */}
      <div
        style={{
          position: "absolute",
          top: "72%",
          opacity: badgeOpacity,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            padding: "10px 30px",
            border: "1px solid #e0e0e0",
            borderRadius: 30,
            backgroundColor: "rgba(255,255,255,0.8)",
          }}
        >
          <div
            style={{
              fontSize: 14,
              color: "#999",
              letterSpacing: "0.2em",
              fontFamily: "'Noto Sans JP', sans-serif",
            }}
          >
            立即選購
          </div>
          <div
            style={{
              fontSize: 18,
              fontWeight: 600,
              color: "#E31937",
              fontFamily: "Arial, sans-serif",
            }}
          >
            HKTVmall
          </div>
        </div>
      </div>

      {/* CTA */}
      <div
        style={{
          position: "absolute",
          top: "82%",
          opacity: ctaOpacity,
          transform: `scale(${ctaScale})`,
        }}
      >
        <div
          style={{
            padding: "16px 60px",
            background: "linear-gradient(135deg, #D4AF37, #C5972C)",
            borderRadius: 40,
            fontSize: 20,
            fontWeight: 400,
            color: "white",
            letterSpacing: "0.3em",
            fontFamily: "'Noto Sans JP', sans-serif",
            boxShadow: "0 4px 20px rgba(212, 175, 55, 0.3)",
          }}
        >
          搜尋 GoGoJap
        </div>
      </div>

      {/* Corner decorations */}
      {[
        { top: 30, left: 30 },
        { top: 30, right: 30 },
        { bottom: 30, left: 30 },
        { bottom: 30, right: 30 },
      ].map((pos, i) => {
        const cornerOpacity = interpolate(frame - 20 - i * 10, [0, 20], [0, 0.15], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              ...pos,
              width: 40,
              height: 40,
              borderTop: i < 2 ? "1px solid #D4AF37" : "none",
              borderBottom: i >= 2 ? "1px solid #D4AF37" : "none",
              borderLeft: i % 2 === 0 ? "1px solid #D4AF37" : "none",
              borderRight: i % 2 === 1 ? "1px solid #D4AF37" : "none",
              opacity: cornerOpacity,
            } as any}
          />
        );
      })}
    </AbsoluteFill>
  );
};
