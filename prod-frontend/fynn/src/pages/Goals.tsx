import { useState } from "react";
import { Button } from "@mui/material";
import Fynn100X100PxRectangle from "../components/Fynn100X100PxRectangle";
import { useNavigate } from "react-router-dom";
import styles from "./Goals.module.css";
import fynnLogo from '../assets/fynn-100-x-100-px-rectangle-sticker-portrait-2@3x.png';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

function Goals() {
  const navigate = useNavigate();
  const [goals, setGoals] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();  // Prevent default form submission
    navigate("/chatbot");
    console.log(goals);
  };

  const handleSkip = () => {
    navigate("/chatbot");
  };

  return (
    <div className={styles.goals1}>
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
      <section className={styles.goalsWrapper}>
        <div className={styles.goalsPopUp}>
          <h1 className={styles.fynnGoals}>Goals</h1>
          <form className={styles.frameGroup} onSubmit={handleSubmit}>
            <div className={styles.inputArea}>
              <div className={styles.label}>briefly summarize your goals</div>
              <textarea
                className={styles.textArea}
                placeholder="e.g) save for retirement"
                value={goals}
                onChange={(e) => setGoals(e.target.value)}
                rows={7}
                required
              />
            </div>
            <Button
              type="submit"
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
              Submit
            </Button>
          </form>
          <div className={styles.navigationButtons}>
            <div className={styles.skipButton} onClick={handleSkip}>
              <span>Skip</span>
              <ArrowBackIcon sx={{ fontSize: 20, marginLeft: '8px', transform: 'rotate(180deg)' }} />
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Goals;
