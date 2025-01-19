import { FunctionComponent } from "react";
import { Box } from "@mui/material";
import Fynn100X100PxRectangle from "./Fynn100X100PxRectangle";
import styles from "./FynnResponse.module.css";

export type FynnResponseType = {
  className?: string;
};

const FynnResponse: FunctionComponent<FynnResponseType> = ({
  className = "",
}) => {
  return (
    <div className={[styles.fynnResponse, className].join(" ")}>
      <Fynn100X100PxRectangle
        fynn100X100PxRectangleMarginTop="unset"
        fynn100X100PxRectangleBackgroundImage="url('/fynn-100-x-100-px-rectangle-sticker-portrait-1@3x.png')"
        fynn100X100PxRectangleHeight="84px"
        fynn100X100PxRectanglePadding="unset"
        fynn100X100PxRectangleWidth="59px"
        fynn100X100PxRectangleDisplay="unset"
        fynn100X100PxRectangleFlexDirection="unset"
        fynn100X100PxRectangleAlignItems="unset"
        fynn100X100PxRectangleJustifyContent="unset"
        showFynn={false}
        fynnTextDecoration="unset"
        fynnHeight="unset"
        fynnWidth="unset"
        fynnPosition="absolute"
        fynnMargin="unset"
        fynnBottom="unset"
        fynnLeft="35px"
        fynnFontWeight="unset"
        fynnTop="154px"
      />
      <div className={styles.fynnResponse1}>Fynn Response.</div>
    </div>
  );
};

export default FynnResponse;
