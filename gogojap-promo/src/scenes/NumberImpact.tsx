import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

const CounterNumber: React.FC<{
  target: number;
  suffix: string;
  prefix?: string;
  label: string;
  sublabel: string;
  delay: number;
}> = ({ target, suffix, prefix = "", label, sublabel, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjustedFrame = Math.max(0, frame - delay);
  const countProgress = interpolate(adjustedFrame, [0, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const eased = 1 - Math.pow(1 - countProgress, 3);
  const currentValue = Math.round(eased * target);

  const entryScale = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 50, stiffness: 150, mass: 1.2 },
  });

  const opacity = interpolate(adjustedFrame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const labelOpacity = interpolate(adjustedFrame, [30, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const barWidth = interpolate(adjustedFrame, [40, 70], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        textAlign: "center",
        opacity,
        transform: `scale(${entryScale})`,
        flex: 1,
      }}
    >
      <div
        style={{
          fontSize: 88,
          fontWeight: 200,
          color: "#1a1a1a",
          fontFamily: "'Noto Serif JP', Georgia, serif",
          lineHeight: 1,
        }}
      >
        {prefix}
        {currentValue.toLocaleString()}
        <span style={{ fontSize: 48, color: "#D4AF37", fontWeight: 300 }}>
          {suffix}
        </span>
      </div>

      <div
        style={{
          width: `${barWidth}%`,
          height: 2,
          background: "linear-gradient(90deg, transparent, #D4AF37, transparent)",
          margin: "16px auto",
        }}
      />

      <div style={{ opacity: labelOpacity }}>
        <div
          style={{
            fontSize: 26,
            fontWeight: 400,
            color: "#444",
            letterSpacing: "0.2em",
            fontFamily: "'Noto Sans JP', sans-serif",
          }}
        >
          {label}
        </div>
        <div
          style={{
            fontSize: 16,
            fontWeight: 300,
            color: "#999",
            marginTop: 8,
            letterSpacing: "0.15em",
            fontFamily: "'Noto Sans JP', sans-serif",
          }}
        >
          {sublabel}
        </div>
      </div>
    </div>
  );
};

export const NumberImpact: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pulseOpacity = interpolate(
    frame,
    [0, 45, 90, 135, 180],
    [0.02, 0.05, 0.02, 0.05, 0.02],
    { extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#FAFAF8",
        overflow: "hidden",
      }}
    >
      {/* Radial pulse */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(circle at 50% 50%, rgba(212,175,55,${pulseOpacity}) 0%, transparent 60%)`,
        }}
      />

      {/* Top decorative kanji */}
      <div
        style={{
          position: "absolute",
          top: 40,
          width: "100%",
          textAlign: "center",
          fontSize: 18,
          color: "#ccc",
          letterSpacing: "1.5em",
          fontFamily: "'Noto Serif JP', serif",
          opacity: interpolate(frame, [0, 30], [0, 0.5], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        信頼の実績
      </div>

      {/* Three stat columns */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 100,
          padding: "0 120px",
        }}
      >
        <CounterNumber
          target={500}
          suffix="+"
          label="餐廳信賴"
          sublabel="含五六星級酒店"
          delay={5}
        />
        <CounterNumber
          target={5000}
          suffix="+"
          label="產品選擇"
          sublabel="SKU 涵蓋全品類"
          delay={25}
        />
        <CounterNumber
          target={365}
          suffix="日"
          label="每日空運"
          sublabel="日本產地直送"
          delay={45}
        />
      </div>

      {/* Bottom dots */}
      <div
        style={{
          position: "absolute",
          bottom: 50,
          left: "50%",
          transform: "translateX(-50%)",
          display: "flex",
          gap: 30,
          alignItems: "center",
        }}
      >
        {[0, 1, 2, 3, 4].map((i) => {
          const dotScale = spring({
            frame: frame - 100 - i * 8,
            fps,
            config: { damping: 40, stiffness: 200 },
          });
          return (
            <div
              key={i}
              style={{
                width: i === 2 ? 10 : 5,
                height: i === 2 ? 10 : 5,
                borderRadius: "50%",
                backgroundColor: i === 2 ? "#D4AF37" : "#ddd",
                transform: `scale(${dotScale})`,
              }}
            />
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
