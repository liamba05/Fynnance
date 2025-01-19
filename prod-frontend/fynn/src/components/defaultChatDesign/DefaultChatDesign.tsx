import { FunctionComponent } from "react";
import Fynn100X100PxRectangle from "../Fynn100X100PxRectangle";
import QuestionRow from "../questionRow/QuestionRow";
import styles from "./DefaultChatDesign.module.css";

export type DefaultChatDesignType = {
  className?: string;
};

const DefaultChatDesign: FunctionComponent<DefaultChatDesignType> = ({
  className = "",
}) => {
  return (
    <div className={[styles.defaultChatDesign, className].join(" ")}>
      <div className={styles.fynn100X100PxRectangleWrapper}>
        <Fynn100X100PxRectangle
          fynn100X100PxRectangleMarginTop="unset"
          fynn100X100PxRectangleBackgroundImage="url('/fynn-100-x-100-px-rectangle-sticker-portrait-21@3x.png')"
          fynn100X100PxRectangleHeight="123px"
          fynn100X100PxRectanglePadding="0px 27px"
          fynn100X100PxRectangleWidth="193px"
          fynn100X100PxRectangleDisplay="flex"
          fynn100X100PxRectangleFlexDirection="row"
          fynn100X100PxRectangleAlignItems="flex-start"
          fynn100X100PxRectangleJustifyContent="flex-start"
          showFynn
          fynnTextDecoration="unset"
          fynnHeight="19px"
          fynnWidth="123px"
          fynnPosition="absolute"
          fynnMargin="0 !important"
          fynnBottom="-50px"
          fynnLeft="calc(50% - 61.5px)"
          fynnFontWeight="400"
          fynnTop="unset"
        />
      </div>
      <QuestionRow />
    </div>
  );
};

export default DefaultChatDesign;
