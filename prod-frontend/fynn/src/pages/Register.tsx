import { useCallback, useState } from "react";
import { Button } from "@mui/material";
import Fynn100X100PxRectangle from "../components/Fynn100X100PxRectangle";
import FieldLabels from "../components/fieldLabels/FieldLabels";
import { useNavigate } from "react-router-dom";
import styles from "./Register.module.css";
import fynnLogo from '../assets/fynn-100-x-100-px-rectangle-sticker-portrait-2@3x.png';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';


function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    birthday: ""
  });

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [field]: e.target.value });
  };

  const handleSubmit = () => {
    navigate("/financial-info");
    console.log(formData);
  };

  const onLoginClick = useCallback(() => {
    navigate("/login");
  }, [navigate]);

  const handleBack = () => {
    navigate(-1);
  };

  return (
    <div className={styles.register1}>
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
      <section className={styles.registerPopUpWrapper}>
        <div className={styles.registerPopUp}>
          <h1 className={styles.fynnRegister}>Register</h1>
          <form className={styles.frameGroup}>
            <div className={styles.inputArea}>
              <FieldLabels 
                email="first name" 
                placeholder="John"
                fullWidth
                value={formData.firstName}
                change={handleChange('firstName')}
              />
              <FieldLabels
                email="last name"
                placeholder="Doe"
                fullWidth
                value={formData.lastName}
                change={handleChange('lastName')}
              />
              <FieldLabels
                email="email"
                placeholder="johndoe@gmail.com"
                fullWidth
                value={formData.email}
                change={handleChange('email')}
              />
              <FieldLabels
                email="password"
                placeholder="password"
                type="password"
                fullWidth
                value={formData.password}
                change={handleChange('password')}
              />
              <FieldLabels
                email="birthday"
                type="date"
                fullWidth
                value={formData.birthday}
                change={handleChange('birthday')}
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
              onClick={handleSubmit}
            >
              Register
            </Button>
          </form>
          <div className={styles.loginLink}>
            <span>Already have an account? </span>
            <span className={styles.login} onClick={onLoginClick}>
              Login
            </span>
          </div>
          <div className={styles.backButton} onClick={handleBack}>
            <ArrowBackIcon sx={{ fontSize: 20, marginRight: '8px' }} />
            <span>Back</span>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Register;
