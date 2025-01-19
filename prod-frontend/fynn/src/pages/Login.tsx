import { useCallback, useState } from "react";
import { Button, IconButton, InputAdornment } from "@mui/material";
import Fynn100X100PxRectangle from "../components/Fynn100X100PxRectangle";
import FieldLabels from "../components/fieldLabels/FieldLabels";
import { useNavigate } from "react-router-dom";
import styles from "./Login.module.css";
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';

function Login(){
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);

  const onSignUpTextClick = useCallback(() => {
    navigate("/register1");
  }, [navigate]);

  const handleTogglePassword = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className={styles.login1}>
      <Fynn100X100PxRectangle
        fynn100X100PxRectangleWidth="100px"
        fynn100X100PxRectangleHeight="100px"
        fynn100X100PxRectanglePadding="0"
        fynn100X100PxRectangleMarginTop="40px"
        fynn100X100PxRectangleBackgroundImage="url('/fynn-100-x-100-px-rectangle-sticker-portrait-2@3x.png')"
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
          <h1 className={styles.fynnLogin}>Login</h1>
          <form className={styles.frameGroup}>
            <div className={styles.inputArea}>
              <FieldLabels 
                email="email" 
                placeholder="johndoe@gmail.com"
                fullWidth 
              />
              <FieldLabels
                email="password"
                placeholder="password"
                type={showPassword ? "text" : "password"}
                fullWidth
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={handleTogglePassword} edge="end">
                        {showPassword ? <VisibilityIcon /> : <VisibilityOffIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </div>
            <Button
              fullWidth
              variant="contained"
              sx={{
                background: "rgba(151, 229, 139, 0.77)",
                borderRadius: "20px",
                textTransform: "none",
                fontSize: "16px",
                padding: "8px 16px",
                "&:hover": { background: "rgba(151, 229, 139, 0.85)" },
              }}
            >
              Log in
            </Button>
            <div className={styles.divider}>
              <div className={styles.line} />
              <span>or</span>
              <div className={styles.line} />
            </div>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<img src="/googlelogo9808-1@2x.png" alt="" width="20" />}
              sx={{
                borderRadius: "20px",
                textTransform: "none",
                border: "1px solid #e0e0e0",
                color: "#000",
                "&:hover": { background: "#f5f5f5" },
              }}
            >
              Continue with Google
            </Button>
          </form>
          <div className={styles.signupLink}>
            <span>Don't have an account: </span>
            <span className={styles.signUp} onClick={onSignUpTextClick}>
              Sign Up
            </span>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Login;
