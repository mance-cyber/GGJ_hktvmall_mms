import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { inter, noto } from "../fonts";
import { C } from "../colors";

export const Opening: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Logo icon scale
  const logoScale = spring({
    frame,
    fps,
    config: { damping: 200 },
    durationInFrames: 40,
  });

  // Title fade in after logo
  const titleOpacity = interpolate(frame, [25, 55], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const titleY = interpolate(frame, [25, 55], [20, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Subtitle
  const subOpacity = interpolate(frame, [60, 90], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const subY = interpolate(frame, [60, 90], [12, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Tagline
  const tagOpacity = interpolate(frame, [100, 130], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Subtle gradient movement
  const g1x = interpolate(frame, [0, 180], [35, 42], { extrapolateRight: "clamp" });
  const g2x = interpolate(frame, [0, 180], [65, 58], { extrapolateRight: "clamp" });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: C.bgDark2,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Ambient glow */}
      <div
        style={{
          position: "absolute",
          left: `${g1x}%`,
          top: "40%",
          width: 500,
          height: 500,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${C.primary}30 0%, transparent 70%)`,
          transform: "translate(-50%, -50%)",
          filter: "blur(80px)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: `${g2x}%`,
          top: "55%",
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${C.purple}20 0%, transparent 70%)`,
          transform: "translate(-50%, -50%)",
          filter: "blur(80px)",
        }}
      />

      {/* Logo square */}
      <div
        style={{
          width: 72,
          height: 72,
          borderRadius: 18,
          background: `linear-gradient(135deg, ${C.primary}, ${C.purple})`,
          transform: `scale(${logoScale})`,
          boxShadow: `0 8px 40px ${C.glowBlue}`,
          marginBottom: 28,
          position: "relative",
          zIndex: 2,
        }}
      />

      {/* Title */}
      <div
        style={{
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
          fontSize: 72,
          fontWeight: 800,
          fontFamily: inter,
          color: "#FFFFFF",
          letterSpacing: -1,
          position: "relative",
          zIndex: 2,
        }}
      >
        GoGoJap AI
      </div>

      {/* Subtitle */}
      <div
        style={{
          opacity: subOpacity,
          transform: `translateY(${subY}px)`,
          fontSize: 26,
          fontWeight: 400,
          fontFamily: noto,
          color: "rgba(255,255,255,0.5)",
          marginTop: 12,
          letterSpacing: 6,
          position: "relative",
          zIndex: 2,
        }}
      >
        HKTVmall 智能運營系統
      </div>

      {/* Value proposition */}
      <div
        style={{
          opacity: tagOpacity,
          fontSize: 18,
          fontFamily: noto,
          color: "rgba(255,255,255,0.35)",
          marginTop: 24,
          letterSpacing: 2,
          position: "relative",
          zIndex: 2,
        }}
      >
        自動化運營 · 智能定價 · 數據驅動增長
      </div>
    </div>
  );
};
