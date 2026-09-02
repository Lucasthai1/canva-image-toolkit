import { useSelection } from "@canva/app-hooks";
import {
  Button,
  Checkbox,
  FormField,
  Rows,
  Select,
  Slider,
  Text,
  Title,
} from "@canva/app-ui-kit";
import { getTemporaryUrl, upload } from "@canva/asset";
import { useEffect, useMemo, useRef, useState } from "react";
import { useIntl } from "react-intl";
import {
  DEFAULT_ADJUSTMENTS,
  PRESETS,
  type ImageAdjustments,
  type PresetName,
  type WarpPreset,
  getPreviewStyle,
  normalizeRotation,
  renderImageToPng,
} from "src/image_processing";
import { OverlayEditor, type OverlayEditorHandle } from "src/overlay_editor";
import * as styles from "styles/components.css";

type LoadState = "idle" | "loading" | "ready";

export const App = () => {
  const intl = useIntl();
  const selection = useSelection("image");
  const [adjustments, setAdjustments] = useState<ImageAdjustments>({
    ...DEFAULT_ADJUSTMENTS,
  });
  const [preset, setPreset] = useState<PresetName>("neutral");
  const [sourceUrl, setSourceUrl] = useState<string | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState(0);
  const overlayRef = useRef<OverlayEditorHandle | null>(null);

  useEffect(() => {
    let disposed = false;

    const loadSelection = async () => {
      setError(null);
      setMessage(null);

      if (selection.count !== 1) {
        setSourceUrl(null);
        setLoadState("idle");
        return;
      }

      setLoadState("loading");
      try {
        const draft = await selection.read();
        const image = draft.contents[0];
        if (!image || draft.contents.length !== 1) {
          throw new Error("SELECTION_CHANGED");
        }
        const result = await getTemporaryUrl({ type: "image", ref: image.ref });
        if (!disposed) {
          setSourceUrl(result.url);
          setLoadState("ready");
        }
      } catch (caught) {
        if (!disposed) {
          setSourceUrl(null);
          setLoadState("idle");
          setError(formatError(caught, intl));
        }
      }
    };

    void loadSelection();
    return () => {
      disposed = true;
    };
  }, [intl, refreshToken, selection]);

  useEffect(() => {
    overlayRef.current?.reset();
  }, [sourceUrl]);

  const previewStyle = useMemo(
    () => getPreviewStyle(adjustments),
    [adjustments],
  );

  const setNumericAdjustment = (
    key: "brightness" | "contrast" | "saturation" | "sharpness",
    value: number,
  ) => {
    setPreset("neutral");
    setAdjustments((current) => ({ ...current, [key]: value }));
  };

  const applyPreset = (name: PresetName) => {
    setPreset(name);
    setAdjustments({ ...PRESETS[name] });
    setMessage(null);
    setError(null);
  };

  const reset = () => {
    applyPreset("neutral");
    overlayRef.current?.reset();
  };

  const applyToSelection = async () => {
    if (selection.count !== 1 || busy) {
      return;
    }

    setBusy(true);
    setError(null);
    setMessage(
      intl.formatMessage({
        defaultMessage: "Processando a imagem no navegador…",
        description: "Status while the selected image is processed locally.",
      }),
    );

    try {
      const initialDraft = await selection.read();
      const selectedImage = initialDraft.contents[0];
      if (!selectedImage || initialDraft.contents.length !== 1) {
        throw new Error("SELECTION_CHANGED");
      }
      const originalRef = selectedImage.ref;
      const temporary = await getTemporaryUrl({
        type: "image",
        ref: originalRef,
      });
      const dataUrl = await renderImageToPng(
        temporary.url,
        adjustments,
        overlayRef.current?.exportPng() ?? null,
      );

      const currentDraft = await selection.read();
      const currentImage = currentDraft.contents[0];
      if (
        !currentImage ||
        currentDraft.contents.length !== 1 ||
        currentImage.ref !== originalRef
      ) {
        throw new Error("SELECTION_CHANGED");
      }

      setMessage(
        intl.formatMessage({
          defaultMessage: "Enviando o resultado ao Canva…",
          description: "Status while the processed image is uploaded to Canva.",
        }),
      );
      const asset = await upload({
        type: "image",
        mimeType: "image/png",
        url: dataUrl,
        thumbnailUrl: dataUrl,
        parentRef: originalRef,
        aiDisclosure: "none",
      });

      currentImage.ref = asset.ref;
      await currentDraft.save();
      setMessage(
        intl.formatMessage({
          defaultMessage: "Imagem atualizada com sucesso.",
          description: "Success message after replacing the selected image.",
        }),
      );
      setRefreshToken((value) => value + 1);
    } catch (caught) {
      setMessage(null);
      setError(formatError(caught, intl));
    } finally {
      setBusy(false);
    }
  };

  const hasOneImage = selection.count === 1;
  const canApply = hasOneImage && sourceUrl != null && loadState === "ready";

  return (
    <div className={styles.scrollContainer}>
      <Rows spacing="2u">
        <div className={styles.section}>
          <Title>
            {intl.formatMessage({
              defaultMessage: "Image Toolkit",
              description: "App title.",
            })}
          </Title>
          <Text>
            {intl.formatMessage({
              defaultMessage:
                "Selecione uma imagem do encarte, ajuste a prévia e aplique. Nenhum outro elemento do design será alterado.",
              description: "Short instructions shown at the top of the app.",
            })}
          </Text>
        </div>

        <div className={styles.previewFrame} aria-live="polite">
          {sourceUrl ? (
            <div
              className={styles.previewImage}
              role="img"
              aria-label={intl.formatMessage({
                defaultMessage: "Prévia da imagem selecionada",
                description: "Alternative text for the selected image preview.",
              })}
              style={{
                ...previewStyle,
                backgroundImage: `url(${JSON.stringify(sourceUrl)})`,
              }}
            />
          ) : (
            <div className={styles.emptyState}>
              <Text>{selectionHelp(selection.count, loadState, intl)}</Text>
            </div>
          )}
        </div>

        <FormField
          label={intl.formatMessage({
            defaultMessage: "Preset rápido",
            description: "Label for the quick image preset selector.",
          })}
          value={preset}
          control={(controlProps) => (
            <Select<PresetName>
              {...controlProps}
              disabled={busy}
              options={[
                {
                  value: "neutral",
                  label: intl.formatMessage({
                    defaultMessage: "Sem ajustes",
                    description: "Neutral image preset label.",
                  }),
                },
                {
                  value: "product",
                  label: intl.formatMessage({
                    defaultMessage: "Produto equilibrado",
                    description: "Balanced product photo preset label.",
                  }),
                },
                {
                  value: "whiteBackground",
                  label: intl.formatMessage({
                    defaultMessage: "Fundo claro",
                    description: "White background product photo preset label.",
                  }),
                },
                {
                  value: "vivid",
                  label: intl.formatMessage({
                    defaultMessage: "Cores vivas",
                    description: "Vivid image preset label.",
                  }),
                },
                {
                  value: "produce",
                  label: intl.formatMessage({
                    defaultMessage: "Hortifruti",
                    description: "Produce photo preset label.",
                  }),
                },
                {
                  value: "meat",
                  label: intl.formatMessage({
                    defaultMessage: "Carnes",
                    description: "Meat photo preset label.",
                  }),
                },
                {
                  value: "cleaning",
                  label: intl.formatMessage({
                    defaultMessage: "Limpeza",
                    description: "Cleaning product photo preset label.",
                  }),
                },
                {
                  value: "frozen",
                  label: intl.formatMessage({
                    defaultMessage: "Congelados",
                    description: "Frozen product photo preset label.",
                  }),
                },
              ]}
              onChange={applyPreset}
            />
          )}
        />

        <FormField
          label={intl.formatMessage({
            defaultMessage: "Perspectiva por malha",
            description: "Label for the local four-corner warp selector.",
          })}
          value={adjustments.warp}
          control={(controlProps) => (
            <Select<WarpPreset>
              {...controlProps}
              disabled={busy}
              options={[
                {
                  value: "none",
                  label: intl.formatMessage({
                    defaultMessage: "Sem perspectiva",
                    description: "No warp option.",
                  }),
                },
                {
                  value: "left",
                  label: intl.formatMessage({
                    defaultMessage: "Recuar lado esquerdo",
                    description: "Left perspective warp option.",
                  }),
                },
                {
                  value: "right",
                  label: intl.formatMessage({
                    defaultMessage: "Recuar lado direito",
                    description: "Right perspective warp option.",
                  }),
                },
                {
                  value: "top",
                  label: intl.formatMessage({
                    defaultMessage: "Recuar topo",
                    description: "Top perspective warp option.",
                  }),
                },
                {
                  value: "bottom",
                  label: intl.formatMessage({
                    defaultMessage: "Recuar base",
                    description: "Bottom perspective warp option.",
                  }),
                },
              ]}
              onChange={(warp) =>
                setAdjustments((current) => ({ ...current, warp }))
              }
            />
          )}
        />

        <RangeControl
          id="brightness"
          label={intl.formatMessage({
            defaultMessage: "Brilho",
            description: "Brightness image adjustment label.",
          })}
          min={60}
          max={140}
          value={adjustments.brightness}
          disabled={busy}
          onChange={(value) => setNumericAdjustment("brightness", value)}
        />
        <RangeControl
          id="contrast"
          label={intl.formatMessage({
            defaultMessage: "Contraste",
            description: "Contrast image adjustment label.",
          })}
          min={60}
          max={140}
          value={adjustments.contrast}
          disabled={busy}
          onChange={(value) => setNumericAdjustment("contrast", value)}
        />
        <RangeControl
          id="saturation"
          label={intl.formatMessage({
            defaultMessage: "Saturação",
            description: "Saturation image adjustment label.",
          })}
          min={0}
          max={180}
          value={adjustments.saturation}
          disabled={busy}
          onChange={(value) => setNumericAdjustment("saturation", value)}
        />
        <RangeControl
          id="sharpness"
          label={intl.formatMessage({
            defaultMessage: "Nitidez",
            description: "Sharpness image adjustment label.",
          })}
          min={0}
          max={60}
          value={adjustments.sharpness}
          disabled={busy}
          onChange={(value) => setNumericAdjustment("sharpness", value)}
        />

        <div className={styles.buttonGrid}>
          <Button
            variant="secondary"
            disabled={busy}
            onClick={() =>
              setAdjustments((current) => ({
                ...current,
                rotation: normalizeRotation(current.rotation - 90),
              }))
            }
          >
            {intl.formatMessage({
              defaultMessage: "Girar à esquerda",
              description: "Button to rotate the selected image left.",
            })}
          </Button>
          <Button
            variant="secondary"
            disabled={busy}
            onClick={() =>
              setAdjustments((current) => ({
                ...current,
                rotation: normalizeRotation(current.rotation + 90),
              }))
            }
          >
            {intl.formatMessage({
              defaultMessage: "Girar à direita",
              description: "Button to rotate the selected image right.",
            })}
          </Button>
          <Button
            variant="secondary"
            disabled={busy}
            onClick={() =>
              setAdjustments((current) => ({
                ...current,
                flipHorizontal: !current.flipHorizontal,
              }))
            }
          >
            {intl.formatMessage({
              defaultMessage: "Espelhar horizontal",
              description: "Button to flip the selected image horizontally.",
            })}
          </Button>
          <Button
            variant="secondary"
            disabled={busy}
            onClick={() =>
              setAdjustments((current) => ({
                ...current,
                flipVertical: !current.flipVertical,
              }))
            }
          >
            {intl.formatMessage({
              defaultMessage: "Espelhar vertical",
              description: "Button to flip the selected image vertically.",
            })}
          </Button>
        </div>

        <Checkbox
          label={intl.formatMessage({
            defaultMessage: "Ampliar a saída em 2x",
            description:
              "Checkbox label to upscale the output image two times.",
          })}
          checked={adjustments.scale === 2}
          disabled={busy}
          onChange={(_value, checked) =>
            setAdjustments((current) => ({
              ...current,
              scale: checked ? 2 : 1,
            }))
          }
        />

        <OverlayEditor
          ref={overlayRef}
          disabled={busy || !hasOneImage}
          backgroundUrl={sourceUrl}
        />

        {error ? (
          <div className={styles.error} role="alert">
            {error}
          </div>
        ) : null}
        {message ? (
          <div className={styles.status} role="status">
            {message}
          </div>
        ) : null}

        <Button
          variant="primary"
          stretch
          loading={busy}
          disabled={!canApply}
          onClick={applyToSelection}
        >
          {intl.formatMessage({
            defaultMessage: "Aplicar na imagem selecionada",
            description: "Primary button that applies edits to selected image.",
          })}
        </Button>
        <Button variant="secondary" stretch disabled={busy} onClick={reset}>
          {intl.formatMessage({
            defaultMessage: "Restaurar ajustes",
            description: "Button to reset all image adjustments.",
          })}
        </Button>

        <div className={styles.privacy}>
          {intl.formatMessage({
            defaultMessage:
              "Processamento local: a imagem só é enviada de volta ao Canva quando você aplica o resultado.",
            description: "Privacy note explaining local image processing.",
          })}
        </div>
      </Rows>
    </div>
  );
};

type RangeControlProps = {
  id: string;
  label: string;
  min: number;
  max: number;
  value: number;
  disabled: boolean;
  onChange: (value: number) => void;
};

const RangeControl = ({
  id,
  label,
  min,
  max,
  value,
  disabled,
  onChange,
}: RangeControlProps) => (
  <FormField
    label={label}
    value={value}
    control={(controlProps) => (
      <Slider
        {...controlProps}
        min={min}
        max={max}
        origin={min <= 100 && max >= 100 ? 100 : min}
        step={1}
        disabled={disabled}
        onChange={onChange}
      />
    )}
  />
);

function selectionHelp(
  count: number,
  loadState: LoadState,
  intl: ReturnType<typeof useIntl>,
): string {
  if (loadState === "loading") {
    return intl.formatMessage({
      defaultMessage: "Carregando a imagem selecionada…",
      description: "Status while the selected image preview loads.",
    });
  }
  if (count > 1) {
    return intl.formatMessage({
      defaultMessage: "Selecione somente uma imagem por vez.",
      description: "Instruction shown when multiple images are selected.",
    });
  }
  return intl.formatMessage({
    defaultMessage: "Selecione uma imagem raster no design para começar.",
    description: "Instruction shown when no image is selected.",
  });
}

function formatError(
  caught: unknown,
  intl: ReturnType<typeof useIntl>,
): string {
  const code = caught instanceof Error ? caught.message : "UNKNOWN";
  switch (code) {
    case "OUTPUT_TOO_LARGE":
      return intl.formatMessage({
        defaultMessage:
          "A saída ultrapassaria 25 megapixels. Desative o upscale em 2x.",
        description: "Error shown when the processed output is too large.",
      });
    case "INPUT_TOO_LARGE":
      return intl.formatMessage({
        defaultMessage: "A imagem de origem é grande demais para edição local.",
        description: "Error shown when the source file is too large.",
      });
    case "SELECTION_CHANGED":
      return intl.formatMessage({
        defaultMessage:
          "A seleção mudou durante o processamento. Selecione a imagem e tente novamente.",
        description: "Error shown when selection changes during processing.",
      });
    default:
      return intl.formatMessage({
        defaultMessage:
          "Não foi possível processar a imagem. Tente novamente ou escolha outra imagem.",
        description: "Generic recoverable image processing error.",
      });
  }
}
