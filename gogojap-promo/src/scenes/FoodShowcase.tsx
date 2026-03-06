import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
} from "remotion";

// Wagyu marbling SVG
const WagyuMarble: React.FC<{ progress: number }> = ({ progress }) => (
  <svg width="280" height="200" viewBox="0 0 280 200">
    <rect width="280" height="200" rx="12" fill="#8B2252" opacity={0.9} />
    {/* Marbling lines */}
    {[0, 1, 2, 3, 4, 5, 6].map((i) => (
      <path
        key={i}
        d={`M${-20 + i * 45} ${10 + i * 8} Q${60 + i * 30} ${50 + Math.sin(i) * 30} ${140 + i * 20} ${30 + i * 12} Q${200 + i * 10} ${60 + Math.cos(i) * 20} ${300} ${40 + i * 15}`}
        stroke="rgba(255,255,255,0.6)"
        strokeWidth={2 + Math.sin(i * 1.5) * 1}
        fill="none"
        strokeDasharray="300"
        strokeDashoffset={300 * (1 - progress)}
        strokeLinecap="round"
      />
    ))}
    <text x="140" y="180" textAnchor="middle" fill="white" fontSize="16" fontFamily="'Noto Sans JP', sans-serif" fontWeight="300" letterSpacing="0.2em">
      宮崎 A5 和牛
    </text>
  </svg>
);

// Shrimp SVG
const ShrimpSVG: React.FC<{ progress: number }> = ({ progress }) => (
  <svg width="200" height="200" viewBox="0 0 200 200">
    <circle cx="100" cy="90" r="70" fill="#FFE4E1" opacity={0.3} />
    {/* Shrimp body */}
    <path
      d="M70 60 Q90 40 120 50 Q140 60 145 85 Q140 110 120 125 Q100 135 85 130 Q65 120 60 100 Q55 80 70 60Z"
      fill="#E8837C"
      opacity={progress}
    />
    {/* Tail segments */}
    <path d="M85 130 Q75 145 60 150 Q50 152 45 145" stroke="#D4726A" strokeWidth="3" fill="none" opacity={progress} />
    <path d="M85 130 Q80 148 70 158 Q62 162 55 155" stroke="#D4726A" strokeWidth="2.5" fill="none" opacity={progress} />
    {/* Antenna */}
    <path d="M90 55 Q70 30 50 20" stroke="#D4726A" strokeWidth="1.5" fill="none" opacity={progress} strokeLinecap="round" />
    <path d="M95 52 Q80 25 65 12" stroke="#D4726A" strokeWidth="1.5" fill="none" opacity={progress} strokeLinecap="round" />
    <text x="100" y="190" textAnchor="middle" fill="#666" fontSize="16" fontFamily="'Noto Sans JP', sans-serif" fontWeight="300" letterSpacing="0.2em">
      甜蝦・牡丹蝦
    </text>
  </svg>
);

// Crab SVG
const CrabSVG: React.FC<{ progress: number }> = ({ progress }) => (
  <svg width="220" height="200" viewBox="0 0 220 200">
    <circle cx="110" cy="90" r="65" fill="#FFF0E0" opacity={0.3} />
    {/* Body */}
    <ellipse cx="110" cy="90" rx="55" ry="40" fill="#C85A3E" opacity={progress} />
    {/* Shell pattern */}
    <ellipse cx="110" cy="85" rx="40" ry="28" fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" opacity={progress} />
    {/* Legs */}
    {[-1, 1].map((dir) =>
      [0, 1, 2].map((i) => (
        <path
          key={`${dir}-${i}`}
          d={`M${110 + dir * 45} ${80 + i * 15} Q${110 + dir * 75} ${70 + i * 20} ${110 + dir * 90} ${90 + i * 18}`}
          stroke="#A0442E"
          strokeWidth="3"
          fill="none"
          strokeLinecap="round"
          opacity={progress}
        />
      ))
    )}
    {/* Claws */}
    <path d="M55 75 Q30 55 25 45 Q22 38 30 35 Q38 38 40 48 Q42 55 55 65" fill="#C85A3E" opacity={progress} />
    <path d="M165 75 Q190 55 195 45 Q198 38 190 35 Q182 38 180 48 Q178 55 165 65" fill="#C85A3E" opacity={progress} />
    <text x="110" y="185" textAnchor="middle" fill="#666" fontSize="16" fontFamily="'Noto Sans JP', sans-serif" fontWeight="300" letterSpacing="0.2em">
      松葉蟹
    </text>
  </svg>
);

// Oyster SVG
const OysterSVG: React.FC<{ progress: number }> = ({ progress }) => (
  <svg width="200" height="200" viewBox="0 0 200 200">
    <circle cx="100" cy="90" r="60" fill="#F5F0E8" opacity={0.3} />
    {/* Shell */}
    <path
      d="M50 100 Q55 50 100 40 Q145 50 150 100 Q145 130 100 140 Q55 130 50 100Z"
      fill="#D4C5A9"
      opacity={progress}
    />
    {/* Shell ridges */}
    {[0, 1, 2, 3].map((i) => (
      <path
        key={i}
        d={`M${60 + i * 5} ${100 - i * 5} Q${100} ${55 - i * 3} ${140 - i * 5} ${100 - i * 5}`}
        stroke="rgba(255,255,255,0.4)"
        strokeWidth="1.5"
        fill="none"
        opacity={progress}
      />
    ))}
    {/* Pearl/meat */}
    <ellipse cx="100" cy="95" rx="30" ry="20" fill="#F0EBE0" opacity={progress * 0.8} />
    <text x="100" y="185" textAnchor="middle" fill="#666" fontSize="16" fontFamily="'Noto Sans JP', sans-serif" fontWeight="300" letterSpacing="0.2em">
      廣島蠔
    </text>
  </svg>
);

// Skewer SVG
const SkewerSVG: React.FC<{ progress: number }> = ({ progress }) => (
  <svg width="180" height="220" viewBox="0 0 180 220">
    {/* Stick */}
    <line x1="90" y1="20" x2="90" y2="180" stroke="#C8A96E" strokeWidth="4" strokeLinecap="round" opacity={progress} />
    {/* Meat pieces */}
    {[0, 1, 2, 3].map((i) => (
      <React.Fragment key={i}>
        <rect
          x="68"
          y={35 + i * 38}
          width="44"
          height="30"
          rx="8"
          fill={i % 2 === 0 ? "#8B4513" : "#A0522D"}
          opacity={progress}
        />
        {/* Grill marks */}
        <line
          x1="72"
          y1={42 + i * 38}
          x2="108"
          y2={42 + i * 38}
          stroke="rgba(0,0,0,0.15)"
          strokeWidth="2"
          opacity={progress}
        />
        <line
          x1="72"
          y1={52 + i * 38}
          x2="108"
          y2={52 + i * 38}
          stroke="rgba(0,0,0,0.15)"
          strokeWidth="2"
          opacity={progress}
        />
      </React.Fragment>
    ))}
    <text x="90" y="210" textAnchor="middle" fill="#666" fontSize="15" fontFamily="'Noto Sans JP', sans-serif" fontWeight="300" letterSpacing="0.15em">
      長洲町串燒
    </text>
  </svg>
);

// Food card wrapper with animation
const FoodCard: React.FC<{
  children: React.ReactNode;
  index: number;
  x: number;
  y: number;
}> = ({ children, index, x, y }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entryDelay = index * 25;
  const slideX = interpolate(frame - entryDelay, [0, 30], [120, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const slideOpacity = interpolate(frame - entryDelay, [0, 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const hoverY = interpolate(
    frame,
    [0, 60, 120, 180],
    [0, -6, 0, 6],
    { extrapolateRight: "clamp" }
  );

  const scaleSpring = spring({
    frame: frame - entryDelay,
    fps,
    config: { damping: 60, stiffness: 120 },
  });

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        opacity: slideOpacity,
        transform: `translateX(${slideX}px) translateY(${hoverY}px) scale(${scaleSpring})`,
      }}
    >
      {children}
    </div>
  );
};

export const FoodShowcase: React.FC = () => {
  const frame = useCurrentFrame();

  // Section title
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [0, 20], [-20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Decorative line width
  const lineWidth = interpolate(frame, [10, 50], [0, 300], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Progress for SVG animations
  const svgProgress = (delay: number) =>
    interpolate(frame - delay, [0, 30], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#FAFAF8",
        overflow: "hidden",
      }}
    >
      {/* Subtle radial gradient */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse at center, rgba(212,175,55,0.04) 0%, transparent 70%)",
        }}
      />

      {/* Section title */}
      <div
        style={{
          position: "absolute",
          top: 50,
          width: "100%",
          textAlign: "center",
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
        }}
      >
        <div
          style={{
            fontSize: 22,
            fontWeight: 300,
            color: "#999",
            letterSpacing: "0.8em",
            fontFamily: "'Noto Sans JP', sans-serif",
          }}
        >
          嚴選食材
        </div>
        {/* Gold decorative line */}
        <div
          style={{
            width: lineWidth,
            height: 1,
            background: "linear-gradient(90deg, transparent, #D4AF37, transparent)",
            margin: "15px auto",
          }}
        />
      </div>

      {/* Food items arranged in elegant layout */}
      <FoodCard index={0} x={120} y={160}>
        <WagyuMarble progress={svgProgress(0)} />
      </FoodCard>

      <FoodCard index={1} x={500} y={180}>
        <ShrimpSVG progress={svgProgress(25)} />
      </FoodCard>

      <FoodCard index={2} x={800} y={150}>
        <CrabSVG progress={svgProgress(50)} />
      </FoodCard>

      <FoodCard index={3} x={1150} y={170}>
        <OysterSVG progress={svgProgress(75)} />
      </FoodCard>

      <FoodCard index={4} x={1500} y={130}>
        <SkewerSVG progress={svgProgress(100)} />
      </FoodCard>

      {/* Bottom tagline */}
      <div
        style={{
          position: "absolute",
          bottom: 60,
          width: "100%",
          textAlign: "center",
          opacity: interpolate(frame, [120, 150], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        <div
          style={{
            fontSize: 20,
            fontWeight: 300,
            color: "#aaa",
            letterSpacing: "0.5em",
            fontFamily: "'Noto Sans JP', sans-serif",
          }}
        >
          毎日空運 · 新鮮直送
        </div>
      </div>

      {/* Decorative dots */}
      {[0, 1, 2].map((i) => {
        const dotOpacity = interpolate(frame - 30 - i * 20, [0, 15], [0, 0.2], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              bottom: 110,
              left: `${46 + i * 4}%`,
              width: 6,
              height: 6,
              borderRadius: "50%",
              backgroundColor: "#D4AF37",
              opacity: dotOpacity,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
