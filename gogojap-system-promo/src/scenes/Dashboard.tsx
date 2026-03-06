import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { C } from "../colors";
import { inter, noto } from "../fonts";

const navItems = ["概覽", "產品管理", "競品分析", "定價策略", "報表"];
const stats = [
  { label: "GMV", value: 2300000, prefix: "$", suffix: "", format: (v: number) => `$${(v / 1000000).toFixed(1)}M` },
  { label: "產品", value: 5000, prefix: "", suffix: "+", format: (v: number) => `${v.toLocaleString()}+` },
  { label: "AI 建議", value: 1247, prefix: "", suffix: "", format: (v: number) => v.toLocaleString() },
];

const chartPoints = [40, 55, 45, 65, 50, 75, 60, 80, 70, 90, 85, 95];

export const Dashboard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: C.bgMuted, justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          width: 1600,
          height: 900,
          display: "flex",
          borderRadius: 16,
          overflow: "hidden",
          boxShadow: "0 8px 48px rgba(0,0,0,0.08)",
          backgroundColor: C.bg,
        }}
      >
        {/* Sidebar */}
        <div style={{ width: 200, backgroundColor: C.bgSoft, borderRight: `1px solid ${C.border}`, padding: "32px 0" }}>
          <div style={{ padding: "0 24px 32px", fontFamily: inter, fontSize: 20, fontWeight: 700, color: C.primary }}>
            GoGoJap
          </div>
          {navItems.map((item, i) => {
            const slideX = interpolate(
              spring({ frame: Math.max(0, frame - i * 8), fps, durationInFrames: 30 }),
              [0, 1],
              [-200, 0],
              { extrapolateRight: "clamp" }
            );
            return (
              <div
                key={i}
                style={{
                  transform: `translateX(${slideX}px)`,
                  padding: "12px 24px",
                  fontFamily: noto,
                  fontSize: 14,
                  color: i === 0 ? C.primary : C.textMuted,
                  backgroundColor: i === 0 ? C.bgMuted : "transparent",
                  fontWeight: i === 0 ? 600 : 400,
                }}
              >
                {item}
              </div>
            );
          })}
        </div>

        {/* Content */}
        <div style={{ flex: 1, padding: 40 }}>
          {/* Stat Cards */}
          <div style={{ display: "flex", gap: 24, marginBottom: 32 }}>
            {stats.map((stat, i) => {
              const s = spring({ frame: Math.max(0, frame - 20 - i * 10), fps, durationInFrames: 40 });
              const translateY = interpolate(s, [0, 1], [-40, 0], { extrapolateRight: "clamp" });
              const opacity = interpolate(s, [0, 1], [0, 1], { extrapolateRight: "clamp" });

              const countProgress = interpolate(frame, [30 + i * 10, 120 + i * 10], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
              const currentValue = Math.floor(stat.value * countProgress);
              const displayValue = stat.format(currentValue);

              return (
                <div
                  key={i}
                  style={{
                    flex: 1,
                    transform: `translateY(${translateY}px)`,
                    opacity,
                    backgroundColor: C.bg,
                    border: `1px solid ${C.border}`,
                    borderRadius: 12,
                    padding: "24px 28px",
                    boxShadow: C.cardShadow,
                  }}
                >
                  <div style={{ fontFamily: noto, fontSize: 13, color: C.textLight, marginBottom: 8 }}>{stat.label}</div>
                  <div style={{ fontFamily: inter, fontSize: 36, fontWeight: 700, color: C.text }}>{displayValue}</div>
                </div>
              );
            })}
          </div>

          {/* Area Chart */}
          <div
            style={{
              backgroundColor: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 12,
              padding: 28,
              boxShadow: C.cardShadow,
              height: 400,
              position: "relative",
              overflow: "hidden",
            }}
          >
            <div style={{ fontFamily: noto, fontSize: 14, color: C.textMuted, marginBottom: 16 }}>月度營收趨勢</div>
            <div style={{ position: "relative", height: 320, display: "flex", alignItems: "flex-end", gap: 0 }}>
              {/* Chart using clip-path reveal */}
              <svg viewBox="0 0 1200 300" style={{ width: "100%", height: 300 }}>
                <defs>
                  <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={C.primary} stopOpacity="0.15" />
                    <stop offset="100%" stopColor={C.primary} stopOpacity="0.02" />
                  </linearGradient>
                </defs>
                {(() => {
                  const clipProgress = interpolate(frame, [60, 200], [0, 100], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
                  const w = 1200 / (chartPoints.length - 1);
                  const pts = chartPoints.map((p, i) => `${i * w},${300 - p * 3}`).join(" ");
                  const areaPts = `0,300 ${pts} ${(chartPoints.length - 1) * w},300`;
                  return (
                    <g style={{ clipPath: `inset(0 ${100 - clipProgress}% 0 0)` }}>
                      <polygon points={areaPts} fill="url(#chartFill)" />
                      <polyline points={pts} fill="none" stroke={C.primary} strokeWidth="3" />
                      {chartPoints.map((p, i) => (
                        <circle key={i} cx={i * w} cy={300 - p * 3} r="4" fill={C.primary} />
                      ))}
                    </g>
                  );
                })()}
              </svg>
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
