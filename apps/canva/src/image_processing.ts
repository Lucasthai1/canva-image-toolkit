export const MAX_INPUT_BYTES = 50 * 1024 * 1024;
export const MAX_OUTPUT_PIXELS = 25_000_000;

export type QuarterTurn = 0 | 90 | 180 | 270;

export type ImageAdjustments = {
  brightness: number;
  contrast: number;
  saturation: number;
  sharpness: number;
  rotation: QuarterTurn;
  flipHorizontal: boolean;
  flipVertical: boolean;
  scale: 1 | 2;
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
): Promise<string> {
  const blob = await downloadImage(sourceUrl);
  const image = await decodeImage(blob);
  const output = getOutputSize(image.width, image.height, adjustments);
  const canvas = document.createElement("canvas");
  canvas.width = output.width;
  canvas.height = output.height;

  const context = canvas.getContext("2d", { willReadFrequently: true });
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

  if (adjustments.sharpness > 0) {
    applySharpen(context, output.width, output.height, adjustments.sharpness);
  }

  const png = await canvasToBlob(canvas);
  return blobToDataUrl(png);
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
