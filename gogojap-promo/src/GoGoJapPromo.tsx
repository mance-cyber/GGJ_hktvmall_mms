import { AbsoluteFill, Sequence } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { Opening } from "./scenes/Opening";
import { FoodShowcase } from "./scenes/FoodShowcase";
import { NumberImpact } from "./scenes/NumberImpact";
import { BrandPosition } from "./scenes/BrandPosition";
import { Closing } from "./scenes/Closing";

export const GoGoJapPromo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#FAFAF8" }}>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={180}>
          <Opening />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 20 })}
        />

        <TransitionSeries.Sequence durationInFrames={210}>
          <FoodShowcase />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={slide({ direction: "from-right" })}
          timing={linearTiming({ durationInFrames: 15 })}
        />

        <TransitionSeries.Sequence durationInFrames={180}>
          <NumberImpact />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 20 })}
        />

        <TransitionSeries.Sequence durationInFrames={150}>
          <BrandPosition />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 25 })}
        />

        <TransitionSeries.Sequence durationInFrames={210}>
          <Closing />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </AbsoluteFill>
  );
};
