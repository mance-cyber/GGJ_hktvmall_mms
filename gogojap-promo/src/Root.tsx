import { Composition } from "remotion";
import { GoGoJapPromo } from "./GoGoJapPromo";

export const Root: React.FC = () => {
  return (
    <Composition
      id="GoGoJapPromo"
      component={GoGoJapPromo}
      durationInFrames={900}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
