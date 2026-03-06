import React, { useMemo } from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
} from "remotion";

// Gold particle system
const Particle: React.FC<{
  x: number;
  y: number;
  delay: number;
  size: number;
  speed: number;
}> = ({ x, y, delay, size, speed }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjustedFrame = Math.max(0, frame - delay);
  const opacity = interpolate(adjustedFrame, [0, 20, 60, 90], [0, 0.8, 0.6, 0], {
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(adjustedFrame, [0, 90], [0, -speed * 3], {
    extrapolateRight: "clamp",
  });
  const translateX = interpolate(
    adjustedFrame,
    [0, 30, 60, 90],
    [0, Math.sin(x) * 20, Math.sin(x) * -15, Math.sin(x) * 25],
    { extrapolateRight: "clamp" }
  );
  const scale = interpolate(adjustedFrame, [0, 15, 70, 90], [0, 1.2, 1, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        left: `${x}%`,
        top: `${y}%`,
        width: size,
        height: size,
        borderRadius: "50%",
        background: `radial-gradient(circle, #D4AF37 0%, #F5E6A3 50%, transparent 70%)`,
        opacity,
        transform: `translate(${translateX}px, ${translateY}px) scale(${scale})`,
        boxShadow: `0 0 ${size * 2}px rgba(212, 175, 55, 0.4)`,
      }}
    />
  );
};

// Text scramble effect
const ScrambleText: React.FC<{
  text: string;
  startFrame: number;
  fontSize: number;
  color?: string;
  fontWeight?: number;
}> = ({ text, startFrame, fontSize, color = "#1a1a1a", fontWeight = 300 }) => {
  const frame = useCurrentFrame();
  const chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン";

  const displayText = useMemo(() => {
    const elapsed = Math.max(0, frame - startFrame);
    const progress = Math.min(1, elapsed / 40);

    return text
      .split("")
      .map((char, i) => {
        if (char === " ") return " ";
        const charProgress = interpolate(
          progress,
          [i / text.length, Math.min(1, (i + 3) / text.length)],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );
        if (charProgress >= 1) return char;
        if (charProgress <= 0) return "";
        const randomIndex = Math.floor(
          ((elapsed * 7 + i * 13) % chars.length)
        );
        return chars[randomIndex];
      })
      .join("");
  }, [frame, startFrame, text, chars]);

  const opacity = interpolate(frame - startFrame, [0, 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        fontSize,
        fontWeight,
        color,
        letterSpacing: "0.15em",
        fontFamily: "'Noto Serif JP', 'Yu Mincho', serif",
        opacity,
      }}
    >
      {displayText}
    </div>
  );
};

// Ink brush stroke SVG
const InkStroke: React.FC<{ frame: number; delay: number }> = ({
  frame,
  delay,
}) => {
  const progress = interpolate(frame - delay, [0, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <svg
      width="600"
      height="20"
      viewBox="0 0 600 20"
      style={{ position: "absolute", bottom: -30, left: "50%", transform: "translateX(-50%)" }}
    >
      <path
        d="M10 10 Q150 2 300 10 Q450 18 590 10"
        stroke="#C8102E"
        strokeWidth="3"
        fill="none"
        strokeDasharray="600"
        strokeDashoffset={600 * (1 - progress)}
        strokeLinecap="round"
        opacity={0.7}
      />
    </svg>
  );
};

export const Opening: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Zen circle animation
  const circleProgress = interpolate(frame, [10, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const circleOpacity = interpolate(frame, [10, 20, 140, 170], [0, 0.15, 0.15, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Main title spring
  const titleSpring = spring({
    frame: frame - 30,
    fps,
    config: { damping: 80, stiffness: 100, mass: 1.5 },
  });

  // Subtitle
  const subtitleOpacity = interpolate(frame, [70, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const subtitleY = interpolate(frame, [70, 90], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Generate particles
  const particles = useMemo(() => {
    const p = [];
    for (let i = 0; i < 40; i++) {
      p.push({
        x: ((i * 37 + 11) % 100),
        y: 30 + ((i * 53 + 7) % 60),
        delay: 20 + (i * 3),
        size: 3 + ((i * 11) % 8),
        speed: 20 + ((i * 17) % 40),
      });
    }
    return p;
  }, []);

  // Vertical Japanese text decoration
  const verticalOpacity = interpolate(frame, [50, 70], [0, 0.3], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
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
      {/* Subtle grid pattern */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `
            linear-gradient(rgba(212,175,55,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(212,175,55,0.03) 1px, transparent 1px)
          `,
          backgroundSize: "60px 60px",
        }}
      />

      {/* Zen circle (Ensō) */}
      <svg
        width="500"
        height="500"
        viewBox="0 0 500 500"
        style={{
          position: "absolute",
          opacity: circleOpacity,
        }}
      >
        <circle
          cx="250"
          cy="250"
          r="200"
          fill="none"
          stroke="#1a1a1a"
          strokeWidth="8"
          strokeDasharray={`${2 * Math.PI * 200}`}
          strokeDashoffset={2 * Math.PI * 200 * (1 - circleProgress)}
          strokeLinecap="round"
          transform="rotate(-90 250 250)"
        />
      </svg>

      {/* Gold particles */}
      {particles.map((p, i) => (
        <Particle key={i} {...p} />
      ))}

      {/* Main title */}
      <div
        style={{
          position: "relative",
          textAlign: "center",
          transform: `scale(${titleSpring})`,
        }}
      >
        <Sequence from={20} premountFor={20}>
          <ScrambleText
            text="GoGoJap"
            startFrame={0}
            fontSize={120}
            fontWeight={200}
          />
        </Sequence>

        {/* Ink brush underline */}
        <InkStroke frame={frame} delay={60} />
      </div>

      {/* Subtitle */}
      <div
        style={{
          position: "absolute",
          top: "62%",
          textAlign: "center",
          opacity: subtitleOpacity,
          transform: `translateY(${subtitleY}px)`,
        }}
      >
        <div
          style={{
            fontSize: 28,
            fontWeight: 300,
            color: "#666",
            letterSpacing: "0.3em",
            fontFamily: "'Noto Sans JP', sans-serif",
          }}
        >
          by GoGoFoods
        </div>
        <div
          style={{
            fontSize: 20,
            color: "#999",
            marginTop: 12,
            letterSpacing: "0.5em",
            fontFamily: "'Noto Sans JP', sans-serif",
          }}
        >
          HKTVmall
        </div>
      </div>

      {/* Vertical Japanese decoration - left */}
      <div
        style={{
          position: "absolute",
          left: 60,
          top: "20%",
          writingMode: "vertical-rl",
          fontSize: 18,
          color: "#bbb",
          letterSpacing: "0.5em",
          opacity: verticalOpacity,
          fontFamily: "'Noto Serif JP', serif",
        }}
      >
        酒店級日本食材
      </div>

      {/* Vertical decoration - right */}
      <div
        style={{
          position: "absolute",
          right: 60,
          top: "25%",
          writingMode: "vertical-rl",
          fontSize: 18,
          color: "#bbb",
          letterSpacing: "0.5em",
          opacity: verticalOpacity,
          fontFamily: "'Noto Serif JP', serif",
        }}
      >
        毎日空輸直送
      </div>
    </AbsoluteFill>
  );
};
