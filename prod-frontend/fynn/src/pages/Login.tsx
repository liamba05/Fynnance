import { useCallback, useState } from "react";
import { Button, IconButton, InputAdornment } from "@mui/material";
import Fynn100X100PxRectangle from "../components/Fynn100X100PxRectangle";
import FieldLabels from "../components/fieldLabels/FieldLabels";
import { useNavigate } from "react-router-dom";
import styles from "./Login.module.css";
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import googleLogo from '../assets/googlelogo9808-1@2x.png';
import fynnLogo from '../assets/fynn-100-x-100-px-rectangle-sticker-portrait-2@3x.png';
import { auth } from "../config";
import { signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from "firebase/auth";

function Login() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    setError("");
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    setError("");
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    
    try {
      await signInWithEmailAndPassword(auth, email, password);
      // Store a dummy token for now (in a real app, you'd get this from Firebase)
      localStorage.setItem('authToken', 'dummy-token-value');
      navigate("/chatbot");
    } catch (error: any) {
      console.error("Login error:", error);
      setError(error.message || "Failed to log in");
    } finally {
      setIsLoading(false);
    }
  }

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    setError("");
    
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
      // Store a dummy token for now
      localStorage.setItem('authToken', 'dummy-token-value');
      navigate("/chatbot");
    } catch (error: any) {
      console.error("Google login error:", error);
      setError(error.message || "Failed to log in with Google");
    } finally {
      setIsLoading(false);
    }
  }
 
  const onSignUpTextClick = useCallback(() => {
    navigate("/register");
  }, [navigate]);

  const handleTogglePassword = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className={styles.login1}>
      <Fynn100X100PxRectangle
        fynn100X100PxRectangleBackgroundImage={`url(${fynnLogo})`}
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
          <form className={styles.frameGroup} onSubmit={handleSubmit}>
            <div className={styles.inputArea}>
              <FieldLabels 
                email="email" 
                placeholder="johndoe@gmail.com"
                fullWidth 
                value={email}
                change={handleEmailChange}
              />
              <FieldLabels
                email="password"
                placeholder="password"
                type={showPassword ? "text" : "password"}
                fullWidth
                value={password}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={handleTogglePassword} edge="end">
                        {showPassword ? <VisibilityIcon /> : <VisibilityOffIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                change={handlePasswordChange}
              />
              {error && <div className={styles.errorMessage}>{error}</div>}
            </div>
            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={isLoading}
              sx={{
                background: "rgba(151, 229, 139, 0.77)",
                borderRadius: "20px",
                textTransform: "none",
                fontSize: "16px",
                padding: "8px 16px",
                "&:hover": { background: "rgba(151, 229, 139, 0.85)" },
              }}
            >
              {isLoading ? "Loading..." : "Log in"}
            </Button>
            <div className={styles.divider}>
              <div className={styles.line} />
              <span>or</span>
              <div className={styles.line} />
            </div>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<img src={googleLogo} width="20" alt="Google" />}
              sx={{
                borderRadius: "20px",
                textTransform: "none",
                border: "1px solid #e0e0e0",
                color: "#000",
                "&:hover": { background: "#f5f5f5" },
              }}
              onClick={handleGoogleSignIn}
              disabled={isLoading}
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
