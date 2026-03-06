import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { Hook } from "./scenes/Hook";
import { Dashboard } from "./scenes/Dashboard";
import { Features } from "./scenes/Features";
import { Closing } from "./scenes/Closing";

export const Main: React.FC = () => {
  const t = { timing: linearTiming({ durationInFrames: 20 }) };

  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={180}>
        <Hook />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} {...t} />
      <TransitionSeries.Sequence durationInFrames={300}>
        <Dashboard />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} {...t} />
      <TransitionSeries.Sequence durationInFrames={420}>
        <Features />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} {...t} />
      <TransitionSeries.Sequence durationInFrames={300}>
        <Closing />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
