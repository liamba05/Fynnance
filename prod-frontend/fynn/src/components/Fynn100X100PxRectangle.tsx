import { FunctionComponent, useMemo, type CSSProperties } from "react";
import styles from "./Fynn100X100PxRectangle.module.css";

export type Fynn100X100PxRectangleType = {
  className?: string;
  showFynn?: boolean;

  /** Style props */
  fynn100X100PxRectangleMarginTop?: CSSProperties["marginTop"];
  fynn100X100PxRectangleBackgroundImage?: CSSProperties["backgroundImage"];
  fynn100X100PxRectangleHeight?: CSSProperties["height"];
  fynn100X100PxRectanglePadding?: CSSProperties["padding"];
  fynn100X100PxRectangleWidth?: CSSProperties["width"];
  fynn100X100PxRectangleDisplay?: CSSProperties["display"];
  fynn100X100PxRectangleFlexDirection?: CSSProperties["flexDirection"];
  fynn100X100PxRectangleAlignItems?: CSSProperties["alignItems"];
  fynn100X100PxRectangleJustifyContent?: CSSProperties["justifyContent"];
  fynnTextDecoration?: CSSProperties["textDecoration"];
  fynnHeight?: CSSProperties["height"];
  fynnWidth?: CSSProperties["width"];
  fynnPosition?: CSSProperties["position"];
  fynnMargin?: CSSProperties["margin"];
  fynnBottom?: CSSProperties["bottom"];
  fynnLeft?: CSSProperties["left"];
  fynnFontWeight?: CSSProperties["fontWeight"];
  fynnTop?: CSSProperties["top"];
};

const Fynn100X100PxRectangle: FunctionComponent<Fynn100X100PxRectangleType> = ({
  className = "",
  fynn100X100PxRectangleMarginTop,
  fynn100X100PxRectangleBackgroundImage,
  fynn100X100PxRectangleHeight,
  fynn100X100PxRectanglePadding,
  fynn100X100PxRectangleWidth,
  fynn100X100PxRectangleDisplay,
  fynn100X100PxRectangleFlexDirection,
  fynn100X100PxRectangleAlignItems,
  fynn100X100PxRectangleJustifyContent,
  showFynn,
  fynnTextDecoration,
  fynnHeight,
  fynnWidth,
  fynnPosition,
  fynnMargin,
  fynnBottom,
  fynnLeft,
  fynnFontWeight,
  fynnTop,
}) => {
  const fynn100X100PxRectangleStyle: CSSProperties = useMemo(() => {
    return {
      marginTop: fynn100X100PxRectangleMarginTop,
      backgroundImage: fynn100X100PxRectangleBackgroundImage,
      height: fynn100X100PxRectangleHeight,
      padding: fynn100X100PxRectanglePadding,
      width: fynn100X100PxRectangleWidth,
      display: fynn100X100PxRectangleDisplay,
      flexDirection: fynn100X100PxRectangleFlexDirection,
      alignItems: fynn100X100PxRectangleAlignItems,
      justifyContent: fynn100X100PxRectangleJustifyContent,
    };
  }, [
    fynn100X100PxRectangleMarginTop,
    fynn100X100PxRectangleBackgroundImage,
    fynn100X100PxRectangleHeight,
    fynn100X100PxRectanglePadding,
    fynn100X100PxRectangleWidth,
    fynn100X100PxRectangleDisplay,
    fynn100X100PxRectangleFlexDirection,
    fynn100X100PxRectangleAlignItems,
    fynn100X100PxRectangleJustifyContent,
  ]);

  const fynnStyle: CSSProperties = useMemo(() => {
    return {
      textDecoration: fynnTextDecoration,
      height: fynnHeight,
      width: fynnWidth,
      position: fynnPosition,
      margin: fynnMargin,
      bottom: fynnBottom,
      left: fynnLeft,
      fontWeight: fynnFontWeight,
      top: fynnTop,
    };
  }, [
    fynnTextDecoration,
    fynnHeight,
    fynnWidth,
    fynnPosition,
    fynnMargin,
    fynnBottom,
    fynnLeft,
    fynnFontWeight,
    fynnTop,
  ]);

  return (
    <div
      className={[styles.fynn100X100PxRectangle, className].join(" ")}
      style={fynn100X100PxRectangleStyle}
    >
      {showFynn && (
        <a className={styles.fynn} style={fynnStyle}>
          fynn
        </a>
      )}
    </div>
  );
};

export default Fynn100X100PxRectangle;
