import {
  DEFAULT_ADJUSTMENTS,
  MAX_OUTPUT_PIXELS,
  getOutputSize,
  getPreviewStyle,
  getWarpCorners,
  normalizeRotation,
} from "./image_processing";

describe("image processing safeguards", () => {
  it("normalizes quarter turns in both directions", () => {
    expect(normalizeRotation(450)).toBe(90);
    expect(normalizeRotation(-90)).toBe(270);
  });

  it("swaps dimensions after a quarter turn and applies scale", () => {
    expect(
      getOutputSize(1200, 800, {
        ...DEFAULT_ADJUSTMENTS,
        rotation: 90,
        scale: 2,
      }),
    ).toEqual({ width: 1600, height: 2400, pixels: 3_840_000 });
  });

  it("refuses invalid and excessive output dimensions", () => {
    expect(() => getOutputSize(0, 100, DEFAULT_ADJUSTMENTS)).toThrow(
      "INVALID_DIMENSIONS",
    );
    expect(() =>
      getOutputSize(MAX_OUTPUT_PIXELS, 2, DEFAULT_ADJUSTMENTS),
    ).toThrow("OUTPUT_TOO_LARGE");
  });

  it("creates a deterministic preview style", () => {
    expect(
      getPreviewStyle({
        ...DEFAULT_ADJUSTMENTS,
        brightness: 110,
        rotation: 270,
        flipHorizontal: true,
      }),
    ).toEqual({
      filter: "brightness(110%) contrast(100%) saturate(100%)",
      transform: "rotate(270deg) scaleX(-1) scaleY(1)",
    });
  });

  it("builds bounded four-corner mesh presets", () => {
    expect(getWarpCorners(100, 50, "top")).toEqual([
      { x: 12, y: 6 },
      { x: 88, y: 6 },
      { x: 100, y: 50 },
      { x: 0, y: 50 },
    ]);
  });
});
