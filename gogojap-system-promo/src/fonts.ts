import { loadFont } from "@remotion/google-fonts/Inter";
import { loadFont as loadNoto } from "@remotion/google-fonts/NotoSansSC";

const { fontFamily: inter } = loadFont();
const { fontFamily: noto } = loadNoto();

export { inter, noto };
