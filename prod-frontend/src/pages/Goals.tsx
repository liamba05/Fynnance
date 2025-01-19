import { FunctionComponent, useCallback } from "react";
import { Typography, Box, Button } from "@mui/material";
import Fynn100X100PxRectangle from "../components/Fynn100X100PxRectangle";
import { useNavigate } from "react-router-dom";
import styles from "./Goals.module.css";

export type GoalsType = {
  onClose?: () => void;
};

const Goals: FunctionComponent<GoalsType> = ({ onClose }) => {
  const navigate = useNavigate();

  const onSubmitButtonClick = useCallback(() => {
    navigate("/chatbot");
  }, [navigate]);

  const onBackFrameContainerClick = useCallback(() => {
    navigate("/financial-info");
  }, [navigate]);

  return (
    <div className={styles.goals1}>
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
      <div className={styles.registrationInputsWrapper}>
        <div className={styles.registrationInputs}>
          <div className={styles.inputPopUp}>
            <div className={styles.fynnLoginWrapper}>
              <h1 className={styles.fynnLogin}>Goals</h1>
            </div>
            <div className={styles.inputContainer}>
              <div className={styles.inputFields}>
                <div className={styles.goalField}>
                  <div className={styles.inputs}>
                    <div className={styles.goals}>
                      briefly summarize your goals
                    </div>
                  </div>
                </div>
                <textarea
                  className={styles.textBox}
                  placeholder="e.g) save for retirement"
                  rows={7}
                  cols={20}
                />
              </div>
              <div className={styles.submission}>
                <div className={styles.buttonContainer}>
                  <Button
                    className={styles.submitButton}
                    disableElevation
                    variant="contained"
                    sx={{
                      textTransform: "none",
                      color: "#000",
                      fontSize: "18",
                      background: "rgba(151, 229, 139, 0.77)",
                      borderRadius: "20px",
                      "&:hover": { background: "rgba(151, 229, 139, 0.77)" },
                      height: 27,
                    }}
                    onClick={onSubmitButtonClick}
                  >
                    Continue
                  </Button>
                  <div className={styles.navigation}>
                    <div className={styles.backFrameParent}>
                      <div
                        className={styles.backFrame}
                        onClick={onBackFrameContainerClick}
                      >
                        <div className={styles.backParent}>
                          <div className={styles.back}>
                            <p className={styles.back1}>back</p>
                          </div>
                          <img
                            className={styles.union1Icon}
                            loading="lazy"
                            alt=""
                            src="/union11.svg"
                          />
                        </div>
                      </div>
                      <div
                        className={styles.skipFrame}
                        onClick={onSubmitButtonClick}
                      >
                        <div className={styles.skipParent}>
                          <div className={styles.skip}>{`skip `}</div>
                          <img
                            className={styles.union1Icon1}
                            loading="lazy"
                            alt=""
                            src="/union1-1.svg"
                          />
                        </div>
                        <img
                          className={styles.union1Icon2}
                          loading="lazy"
                          alt=""
                          src="/union1-2.svg"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Goals;
