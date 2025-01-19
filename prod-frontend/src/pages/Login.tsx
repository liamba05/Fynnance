import { FunctionComponent, useCallback } from "react";
import { Typography, Box, Button } from "@mui/material";
import Fynn100X100PxRectangle from "../components/Fynn100X100PxRectangle";
import FieldLabels from "../components/FieldLabels";
import { useNavigate } from "react-router-dom";
import styles from "./Login.module.css";

const Login: FunctionComponent = () => {
  const navigate = useNavigate();

  const onSignUpTextClick = useCallback(() => {
    navigate("/register1");
  }, [navigate]);

  return (
    <div className={styles.login1}>
      <Fynn100X100PxRectangle
        fynn100X100PxRectangleMarginTop="-254px"
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
      <section className={styles.loginPopUpWrapper}>
        <div className={styles.loginPopUp}>
          <div className={styles.frameParent}>
            <div className={styles.fynnLoginWrapper}>
              <h1 className={styles.fynnLogin}>{`Login `}</h1>
            </div>
            <form className={styles.frameGroup}>
              <div className={styles.inputAreaWrapper}>
                <div className={styles.inputArea}>
                  <FieldLabels email="email" placeholder="johndoe@gmail.com" />
                  <FieldLabels
                    email="password"
                    emailTextDecoration="unset"
                    placeholder="password"
                  />
                </div>
              </div>
              <div className={styles.loginOptionsParent}>
                <div className={styles.loginOptions}>
                  <Button
                    className={styles.loginButton}
                    disableElevation
                    variant="contained"
                    sx={{
                      textTransform: "none",
                      color: "#000",
                      fontSize: "18",
                      background: "rgba(151, 229, 139, 0.77)",
                      borderRadius: "20px",
                      "&:hover": { background: "rgba(151, 229, 139, 0.77)" },
                      width: 295,
                      height: 33,
                    }}
                  >
                    Log in
                  </Button>
                </div>
                <div className={styles.lineParent}>
                  <div className={styles.frameChild} />
                  <div className={styles.frameChild} />
                  <div className={styles.or}>{`or `}</div>
                </div>
                <div className={styles.loginOptions1}>
                  <div className={styles.frame}>
                    <img
                      className={styles.googleLogo98081Icon}
                      loading="lazy"
                      alt=""
                      src="/googlelogo9808-1@2x.png"
                    />
                    <div className={styles.googleLogin}>
                      <div className={styles.continueWithGoogle}>
                        Continue with Google
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div className={styles.signupLinkWrapper}>
            <div className={styles.signupLink}>
              <div
                className={styles.dontHaveAn}
              >{`Don’t have an account: `}</div>
              <div className={styles.signUp} onClick={onSignUpTextClick}>
                Sign Up
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Login;
