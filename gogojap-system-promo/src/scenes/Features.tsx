import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { C } from "../colors";
import { noto } from "../fonts";

const features = [
  { emoji: "📊", title: "競品監測", desc: "實時追蹤市場動態" },
  { emoji: "💰", title: "智能定價", desc: "AI 驅動價格策略" },
  { emoji: "✍️", title: "AI 文案", desc: "自動生成產品描述" },
  { emoji: "🔍", title: "SEO 優化", desc: "搜索排名提升" },
  { emoji: "⚡", title: "市場應對", desc: "快速響應競爭變化" },
  { emoji: "📈", title: "財務分析", desc: "全面利潤洞察" },
];

export const Features: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Highlight cycles through cards
  const highlightCycle = 60; // frames per card highlight
  const highlightIndex = Math.floor((frame - 60) / highlightCycle) % 6;

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg, justifyContent: "center", alignItems: "center" }}>
      <div style={{ fontFamily: noto, fontSize: 40, fontWeight: 700, color: C.text, marginBottom: 48 }}>
        {(() => {
          const titleOpacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
          return <span style={{ opacity: titleOpacity }}>核心功能</span>;
        })()}
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 340px)",
          gap: 28,
        }}
      >
        {features.map((f, i) => {
          const delay = 20 + i * 5;
          const s = spring({ frame: Math.max(0, frame - delay), fps, durationInFrames: 35 });
          const opacity = interpolate(s, [0, 1], [0, 1], { extrapolateRight: "clamp" });
          const translateY = interpolate(s, [0, 1], [30, 0], { extrapolateRight: "clamp" });

          const isHighlighted = frame > 60 && highlightIndex === i;
          const highlightScale = isHighlighted ? 1.03 : 1;
          const borderColor = isHighlighted ? C.primary : C.border;

          return (
            <div
              key={i}
              style={{
                opacity,
                transform: `translateY(${translateY}px) scale(${highlightScale})`,
                backgroundColor: C.bg,
                border: `2px solid ${borderColor}`,
                borderRadius: 12,
                padding: "32px 28px",
                boxShadow: C.cardShadow,
              }}
            >
              <div style={{ fontSize: 36, marginBottom: 16 }}>{f.emoji}</div>
              <div style={{ fontFamily: noto, fontSize: 20, fontWeight: 600, color: C.text, marginBottom: 8 }}>
                {f.title}
              </div>
              <div style={{ fontFamily: noto, fontSize: 15, color: C.textMuted, lineHeight: 1.5 }}>
                {f.desc}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
