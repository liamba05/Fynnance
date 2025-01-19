import { FunctionComponent } from "react";
import { Box } from "@mui/material";
import Fynn100X100PxRectangle from "../components/Fynn100X100PxRectangle";
import InputPopUp from "../components/InputPopUp";
import styles from "./Register.module.css";

const Register: FunctionComponent = () => {
  return (
    <div className={styles.register1}>
      <Fynn100X100PxRectangle
        fynn100X100PxRectangleMarginTop="-234px"
        fynn100X100PxRectangleBackgroundImage="url('/fynn-100-x-100-px-rectangle-sticker-portrait-2@3x.png')"
        fynn100X100PxRectangleHeight="215px"
        fynn100X100PxRectanglePadding="154px 26px 21px 35px"
        fynn100X100PxRectangleWidth="193px"
        fynn100X100PxRectangleDisplay="flex"
        fynn100X100PxRectangleFlexDirection="row"
        fynn100X100PxRectangleAlignItems="flex-start"
        fynn100X100PxRectangleJustifyContent="flex-start"
        showFynn
        fynnTextDecoration="none"
        fynnHeight="40px"
        fynnWidth="133px"
        fynnPosition="relative"
        fynnMargin="unset"
        fynnBottom="unset"
        fynnLeft="unset"
        fynnFontWeight="unset"
        fynnTop="unset"
      />
      <section className={styles.inputPopUpWrapper}>
        <InputPopUp />
      </section>
    </div>
  );
};

export default Register;
