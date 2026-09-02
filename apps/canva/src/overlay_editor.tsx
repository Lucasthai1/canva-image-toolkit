import { Button, Checkbox, Rows, Text } from "@canva/app-ui-kit";
import { Canvas, Circle, IText, PencilBrush, Rect } from "fabric";
import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react";
import { useIntl } from "react-intl";
import * as styles from "styles/components.css";

export type OverlayEditorHandle = {
  exportPng: () => string | null;
  reset: () => void;
};

type Props = {
  disabled: boolean;
  backgroundUrl: string | null;
};

export const OverlayEditor = forwardRef<OverlayEditorHandle, Props>(
  ({ disabled, backgroundUrl }, forwardedRef) => {
    const elementRef = useRef<HTMLCanvasElement | null>(null);
    const editorRef = useRef<Canvas | null>(null);
    const historyRef = useRef<string[]>([]);
    const historyIndexRef = useRef(-1);
    const restoringRef = useRef(false);
    const [drawing, setDrawing] = useState(false);
    const [historyIndex, setHistoryIndex] = useState(-1);
    const [historyLength, setHistoryLength] = useState(0);
    const intl = useIntl();

    const record = () => {
      const editor = editorRef.current;
      if (!editor || restoringRef.current) return;
      const snapshot = JSON.stringify(editor.toJSON());
      const next = historyRef.current.slice(0, historyIndexRef.current + 1);
      if (next.at(-1) !== snapshot) next.push(snapshot);
      historyRef.current = next.slice(-30);
      historyIndexRef.current = historyRef.current.length - 1;
      setHistoryIndex(historyIndexRef.current);
      setHistoryLength(historyRef.current.length);
    };

    useEffect(() => {
      if (!elementRef.current) return;
      const editor = new Canvas(elementRef.current, {
        width: 280,
        height: 220,
        backgroundColor: "transparent",
        preserveObjectStacking: true,
        selection: true,
      });
      const brush = new PencilBrush(editor);
      brush.color = "#e11919";
      brush.width = 4;
      editor.freeDrawingBrush = brush;
      editor.on("path:created", record);
      editor.on("object:modified", record);
      editorRef.current = editor;
      record();
      return () => {
        editor.dispose();
        editorRef.current = null;
      };
    }, []);

    useEffect(() => {
      const editor = editorRef.current;
      if (!editor) return;
      editor.isDrawingMode = drawing && !disabled;
      editor.selection = !drawing && !disabled;
      editor.getObjects().forEach((object) => {
        object.selectable = !drawing && !disabled;
        object.evented = !disabled;
      });
      editor.requestRenderAll();
    }, [disabled, drawing]);

    const reset = () => {
      const editor = editorRef.current;
      if (!editor) return;
      editor.clear();
      editor.backgroundColor = "transparent";
      editor.requestRenderAll();
      record();
    };

    useImperativeHandle(forwardedRef, () => ({
      exportPng: () => {
        const editor = editorRef.current;
        if (!editor || editor.getObjects().length === 0) return null;
        editor.discardActiveObject();
        editor.requestRenderAll();
        return editor.toDataURL({ format: "png", multiplier: 1 });
      },
      reset,
    }));

    const addRectangle = () => {
      editorRef.current?.add(
        new Rect({
          left: 70,
          top: 55,
          width: 140,
          height: 90,
          fill: "transparent",
          stroke: "#e11919",
          strokeWidth: 4,
        }),
      );
      record();
    };

    const addCircle = () => {
      editorRef.current?.add(
        new Circle({
          left: 90,
          top: 40,
          radius: 55,
          fill: "transparent",
          stroke: "#1565c0",
          strokeWidth: 4,
        }),
      );
      record();
    };

    const addText = () => {
      editorRef.current?.add(
        new IText("Oferta", {
          left: 85,
          top: 85,
          fill: "#111111",
          fontFamily: "Arial",
          fontSize: 32,
          fontWeight: "700",
        }),
      );
      record();
    };

    const removeSelected = () => {
      const editor = editorRef.current;
      if (!editor) return;
      const selected = editor.getActiveObjects();
      selected.forEach((object) => editor.remove(object));
      editor.discardActiveObject();
      editor.requestRenderAll();
      record();
    };

    const restore = async (nextIndex: number) => {
      const editor = editorRef.current;
      const snapshot = historyRef.current[nextIndex];
      if (!editor || !snapshot) return;
      restoringRef.current = true;
      try {
        await editor.loadFromJSON(snapshot);
        editor.requestRenderAll();
        historyIndexRef.current = nextIndex;
        setHistoryIndex(nextIndex);
      } finally {
        restoringRef.current = false;
      }
    };

    return (
      <Rows spacing="1u">
        <Text>
          {intl.formatMessage({
            defaultMessage: "Desenho e objetos",
            description: "Overlay editor section title.",
          })}
        </Text>
        <div
          className={styles.overlayCanvas}
          style={{
            backgroundImage: backgroundUrl
              ? `url(${JSON.stringify(backgroundUrl)})`
              : undefined,
          }}
        >
          <canvas
            ref={elementRef}
            aria-label={intl.formatMessage({
              defaultMessage: "Editor de desenho sobre a imagem",
              description: "Accessible label for the overlay drawing canvas.",
            })}
          />
        </div>
        <Checkbox
          label={intl.formatMessage({
            defaultMessage: "Caneta vermelha",
            description: "Toggle for free drawing mode.",
          })}
          checked={drawing}
          disabled={disabled}
          onChange={(_value, checked) => setDrawing(checked)}
        />
        <div className={styles.buttonGrid}>
          <Button
            variant="secondary"
            disabled={disabled}
            onClick={addRectangle}
          >
            {intl.formatMessage({
              defaultMessage: "Retângulo",
              description: "Add rectangle button.",
            })}
          </Button>
          <Button variant="secondary" disabled={disabled} onClick={addCircle}>
            {intl.formatMessage({
              defaultMessage: "Círculo",
              description: "Add circle button.",
            })}
          </Button>
          <Button variant="secondary" disabled={disabled} onClick={addText}>
            {intl.formatMessage({
              defaultMessage: "Texto",
              description: "Add text button.",
            })}
          </Button>
          <Button
            variant="secondary"
            disabled={disabled}
            onClick={removeSelected}
          >
            {intl.formatMessage({
              defaultMessage: "Borracha",
              description: "Remove selected overlay object button.",
            })}
          </Button>
          <Button
            variant="secondary"
            disabled={disabled || historyIndex <= 0}
            onClick={() => void restore(historyIndex - 1)}
          >
            {intl.formatMessage({
              defaultMessage: "Desfazer",
              description: "Undo overlay edit button.",
            })}
          </Button>
          <Button
            variant="secondary"
            disabled={disabled || historyIndex >= historyLength - 1}
            onClick={() => void restore(historyIndex + 1)}
          >
            {intl.formatMessage({
              defaultMessage: "Refazer",
              description: "Redo overlay edit button.",
            })}
          </Button>
        </div>
        <Button variant="secondary" stretch disabled={disabled} onClick={reset}>
          {intl.formatMessage({
            defaultMessage: "Limpar desenho",
            description: "Clear all overlay objects button.",
          })}
        </Button>
      </Rows>
    );
  },
);

OverlayEditor.displayName = "OverlayEditor";
