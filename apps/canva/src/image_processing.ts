export const MAX_INPUT_BYTES = 50 * 1024 * 1024;
export const MAX_OUTPUT_PIXELS = 25_000_000;

export type QuarterTurn = 0 | 90 | 180 | 270;
export type WarpPreset = "none" | "left" | "right" | "top" | "bottom";
type Point = { x: number; y: number };

export type ImageAdjustments = {
  brightness: number;
  contrast: number;
  saturation: number;
  sharpness: number;
  rotation: QuarterTurn;
  flipHorizontal: boolean;
  flipVertical: boolean;
  scale: 1 | 2;
  warp: WarpPreset;
};

export const DEFAULT_ADJUSTMENTS: ImageAdjustments = {
  brightness: 100,
  contrast: 100,
  saturation: 100,
  sharpness: 0,
  rotation: 0,
  flipHorizontal: false,
  flipVertical: false,
  scale: 1,
  warp: "none",
};

export const PRESETS = {
  neutral: DEFAULT_ADJUSTMENTS,
  product: {
    ...DEFAULT_ADJUSTMENTS,
    brightness: 106,
    contrast: 108,
    saturation: 112,
    sharpness: 24,
  },
  whiteBackground: {
    ...DEFAULT_ADJUSTMENTS,
    brightness: 110,
    contrast: 105,
    sharpness: 14,
  },
  vivid: {
    ...DEFAULT_ADJUSTMENTS,
    contrast: 112,
    saturation: 120,
    sharpness: 18,
  },
  produce: {
    ...DEFAULT_ADJUSTMENTS,
    brightness: 105,
    contrast: 108,
    saturation: 122,
    sharpness: 20,
  },
  meat: {
    ...DEFAULT_ADJUSTMENTS,
    brightness: 104,
    contrast: 112,
    saturation: 108,
    sharpness: 26,
  },
  cleaning: {
    ...DEFAULT_ADJUSTMENTS,
    brightness: 110,
    contrast: 110,
    saturation: 116,
    sharpness: 18,
  },
  frozen: {
    ...DEFAULT_ADJUSTMENTS,
    brightness: 108,
    contrast: 106,
    saturation: 108,
    sharpness: 16,
  },
} as const satisfies Record<string, ImageAdjustments>;

export type PresetName = keyof typeof PRESETS;

export function normalizeRotation(value: number): QuarterTurn {
  const normalized = ((value % 360) + 360) % 360;
  if (normalized === 0 || normalized === 90 || normalized === 180) {
    return normalized;
  }
  return 270;
}

export function getOutputSize(
  width: number,
  height: number,
  adjustments: ImageAdjustments,
): { width: number; height: number; pixels: number } {
  if (!Number.isSafeInteger(width) || !Number.isSafeInteger(height)) {
    throw new Error("INVALID_DIMENSIONS");
  }
  if (width <= 0 || height <= 0) {
    throw new Error("INVALID_DIMENSIONS");
  }

  const swapsAxes = adjustments.rotation === 90 || adjustments.rotation === 270;
  const outputWidth = (swapsAxes ? height : width) * adjustments.scale;
  const outputHeight = (swapsAxes ? width : height) * adjustments.scale;
  const pixels = outputWidth * outputHeight;

  if (!Number.isSafeInteger(pixels) || pixels > MAX_OUTPUT_PIXELS) {
    throw new Error("OUTPUT_TOO_LARGE");
  }

  return { width: outputWidth, height: outputHeight, pixels };
}

export function getPreviewStyle(adjustments: ImageAdjustments): {
  filter: string;
  transform: string;
} {
  return {
    filter: [
      `brightness(${adjustments.brightness}%)`,
      `contrast(${adjustments.contrast}%)`,
      `saturate(${adjustments.saturation}%)`,
    ].join(" "),
    transform: [
      `rotate(${adjustments.rotation}deg)`,
      `scaleX(${adjustments.flipHorizontal ? -1 : 1})`,
      `scaleY(${adjustments.flipVertical ? -1 : 1})`,
    ].join(" "),
  };
}

export async function renderImageToPng(
  sourceUrl: string,
  adjustments: ImageAdjustments,
  overlayUrl: string | null = null,
): Promise<string> {
  const blob = await downloadImage(sourceUrl);
  const image = await decodeImage(blob);
  const output = getOutputSize(image.width, image.height, adjustments);
  let canvas = document.createElement("canvas");
  canvas.width = output.width;
  canvas.height = output.height;

  let context = canvas.getContext("2d", { willReadFrequently: true });
  if (!context) {
    throw new Error("CANVAS_UNAVAILABLE");
  }

  context.imageSmoothingEnabled = true;
  context.imageSmoothingQuality = "high";
  context.translate(output.width / 2, output.height / 2);
  context.rotate((adjustments.rotation * Math.PI) / 180);
  context.scale(
    adjustments.flipHorizontal ? -1 : 1,
    adjustments.flipVertical ? -1 : 1,
  );
  context.filter = [
    `brightness(${adjustments.brightness}%)`,
    `contrast(${adjustments.contrast}%)`,
    `saturate(${adjustments.saturation}%)`,
  ].join(" ");
  context.drawImage(
    image,
    (-image.width * adjustments.scale) / 2,
    (-image.height * adjustments.scale) / 2,
    image.width * adjustments.scale,
    image.height * adjustments.scale,
  );
  context.setTransform(1, 0, 0, 1, 0, 0);
  context.filter = "none";

  if (adjustments.warp !== "none") {
    canvas = warpWithMesh(canvas, adjustments.warp);
    context = canvas.getContext("2d", { willReadFrequently: true });
    if (!context) {
      throw new Error("CANVAS_UNAVAILABLE");
    }
  }

  if (overlayUrl) {
    const overlay = await decodeImage(await (await fetch(overlayUrl)).blob());
    context.drawImage(overlay, 0, 0, canvas.width, canvas.height);
  }

  if (adjustments.sharpness > 0) {
    applySharpen(context, output.width, output.height, adjustments.sharpness);
  }

  const png = await canvasToBlob(canvas);
  return blobToDataUrl(png);
}

export function getWarpCorners(
  width: number,
  height: number,
  preset: WarpPreset,
): [Point, Point, Point, Point] {
  const insetX = width * 0.12;
  const insetY = height * 0.12;
  switch (preset) {
    case "left":
      return [
        { x: insetX, y: insetY },
        { x: width, y: 0 },
        { x: width, y: height },
        { x: insetX, y: height - insetY },
      ];
    case "right":
      return [
        { x: 0, y: 0 },
        { x: width - insetX, y: insetY },
        { x: width - insetX, y: height - insetY },
        { x: 0, y: height },
      ];
    case "top":
      return [
        { x: insetX, y: insetY },
        { x: width - insetX, y: insetY },
        { x: width, y: height },
        { x: 0, y: height },
      ];
    case "bottom":
      return [
        { x: 0, y: 0 },
        { x: width, y: 0 },
        { x: width - insetX, y: height - insetY },
        { x: insetX, y: height - insetY },
      ];
    default:
      return [
        { x: 0, y: 0 },
        { x: width, y: 0 },
        { x: width, y: height },
        { x: 0, y: height },
      ];
  }
}

function warpWithMesh(
  source: HTMLCanvasElement,
  preset: WarpPreset,
): HTMLCanvasElement {
  const output = document.createElement("canvas");
  output.width = source.width;
  output.height = source.height;
  const context = output.getContext("2d");
  if (!context) throw new Error("CANVAS_UNAVAILABLE");
  const [topLeft, topRight, bottomRight, bottomLeft] = getWarpCorners(
    source.width,
    source.height,
    preset,
  );
  const columns = 12;
  const rows = 12;
  const destination = (u: number, v: number) => ({
    x:
      (1 - u) * (1 - v) * topLeft.x +
      u * (1 - v) * topRight.x +
      u * v * bottomRight.x +
      (1 - u) * v * bottomLeft.x,
    y:
      (1 - u) * (1 - v) * topLeft.y +
      u * (1 - v) * topRight.y +
      u * v * bottomRight.y +
      (1 - u) * v * bottomLeft.y,
  });
  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      const u0 = column / columns;
      const u1 = (column + 1) / columns;
      const v0 = row / rows;
      const v1 = (row + 1) / rows;
      const s00 = { x: u0 * source.width, y: v0 * source.height };
      const s10 = { x: u1 * source.width, y: v0 * source.height };
      const s11 = { x: u1 * source.width, y: v1 * source.height };
      const s01 = { x: u0 * source.width, y: v1 * source.height };
      const d00 = destination(u0, v0);
      const d10 = destination(u1, v0);
      const d11 = destination(u1, v1);
      const d01 = destination(u0, v1);
      drawTriangle(context, source, [s00, s10, s11], [d00, d10, d11]);
      drawTriangle(context, source, [s00, s11, s01], [d00, d11, d01]);
    }
  }
  return output;
}

function drawTriangle(
  context: CanvasRenderingContext2D,
  source: CanvasImageSource,
  sourcePoints: [Point, Point, Point],
  destinationPoints: [Point, Point, Point],
): void {
  const [s0, s1, s2] = sourcePoints;
  const [d0, d1, d2] = destinationPoints;
  const determinant =
    s0.x * (s1.y - s2.y) + s1.x * (s2.y - s0.y) + s2.x * (s0.y - s1.y);
  if (Math.abs(determinant) < 1e-8) return;
  const coefficient = (v0: number, v1: number, v2: number) => ({
    a:
      (v0 * (s1.y - s2.y) + v1 * (s2.y - s0.y) + v2 * (s0.y - s1.y)) /
      determinant,
    c:
      (v0 * (s2.x - s1.x) + v1 * (s0.x - s2.x) + v2 * (s1.x - s0.x)) /
      determinant,
    e:
      (v0 * (s1.x * s2.y - s2.x * s1.y) +
        v1 * (s2.x * s0.y - s0.x * s2.y) +
        v2 * (s0.x * s1.y - s1.x * s0.y)) /
      determinant,
  });
  const x = coefficient(d0.x, d1.x, d2.x);
  const y = coefficient(d0.y, d1.y, d2.y);
  context.save();
  context.beginPath();
  context.moveTo(d0.x, d0.y);
  context.lineTo(d1.x, d1.y);
  context.lineTo(d2.x, d2.y);
  context.closePath();
  context.clip();
  context.setTransform(x.a, y.a, x.c, y.c, x.e, y.e);
  context.drawImage(source, 0, 0);
  context.restore();
}

async function downloadImage(url: string): Promise<Blob> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 30_000);

  try {
    const response = await fetch(url, {
      mode: "cors",
      signal: controller.signal,
    });
    if (!response.ok) {
      throw new Error("DOWNLOAD_FAILED");
    }

    const blob = await response.blob();
    if (blob.size === 0 || blob.size > MAX_INPUT_BYTES) {
      throw new Error("INPUT_TOO_LARGE");
    }
    if (blob.type && !blob.type.startsWith("image/")) {
      throw new Error("INVALID_IMAGE_TYPE");
    }
    return blob;
  } finally {
    window.clearTimeout(timeout);
  }
}

async function decodeImage(blob: Blob): Promise<HTMLImageElement> {
  const objectUrl = URL.createObjectURL(blob);
  const image = new Image();
  image.decoding = "async";

  try {
    await new Promise<void>((resolve, reject) => {
      image.onload = () => resolve();
      image.onerror = () => reject(new Error("DECODE_FAILED"));
      image.src = objectUrl;
    });
    if (image.width <= 0 || image.height <= 0) {
      throw new Error("INVALID_DIMENSIONS");
    }
    return image;
  } finally {
    URL.revokeObjectURL(objectUrl);
  }
}

function applySharpen(
  context: CanvasRenderingContext2D,
  width: number,
  height: number,
  sharpness: number,
): void {
  const source = context.getImageData(0, 0, width, height);
  const result = new ImageData(
    new Uint8ClampedArray(source.data),
    width,
    height,
  );
  const amount = Math.min(1, Math.max(0, sharpness / 100));

  for (let y = 1; y < height - 1; y += 1) {
    for (let x = 1; x < width - 1; x += 1) {
      const pixel = (y * width + x) * 4;
      const left = pixel - 4;
      const right = pixel + 4;
      const up = pixel - width * 4;
      const down = pixel + width * 4;

      for (let channel = 0; channel < 3; channel += 1) {
        const sharpened =
          (source.data[pixel + channel] ?? 0) * (1 + 4 * amount) -
          amount *
            ((source.data[left + channel] ?? 0) +
              (source.data[right + channel] ?? 0) +
              (source.data[up + channel] ?? 0) +
              (source.data[down + channel] ?? 0));
        result.data[pixel + channel] = Math.round(sharpened);
      }
    }
  }

  context.putImageData(result, 0, 0);
}

function canvasToBlob(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error("ENCODE_FAILED"));
        return;
      }
      resolve(blob);
    }, "image/png");
  });
}

function blobToDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result !== "string") {
        reject(new Error("ENCODE_FAILED"));
        return;
      }
      resolve(reader.result);
    };
    reader.onerror = () => reject(new Error("ENCODE_FAILED"));
    reader.readAsDataURL(blob);
  });
}
