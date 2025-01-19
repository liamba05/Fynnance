import { FunctionComponent } from "react";
import {
  Typography,
  Box,
  TextField,
  InputAdornment,
  Icon,
  IconButton,
} from "@mui/material";
import styles from "./GoalsTipsAccountSummary.module.css";

const GoalsTipsAccountSummary: FunctionComponent = () => {
  return (
    <div className={styles.goalstipsAccountSummary}>
      <section className={styles.goalsTips}>Goals + Tips</section>
      <h1 className={styles.accountSummary}>Account Summary</h1>
      <div className={styles.page}>
        <div className={styles.questions}>
          <div className={styles.trend}>
            <div className={styles.up}>
              <div className={styles.trending}>
                <img
                  className={styles.trendingUpIcon}
                  loading="lazy"
                  alt=""
                  src="/trending-up1.svg"
                />
              </div>
              <div className={styles.messageBar}>
                <TextField
                  className={styles.searchArea}
                  placeholder="Search"
                  variant="outlined"
                  InputProps={{
                    endAdornment: (
                      <img width="50px" height="45px" src="/empty.svg" />
                    ),
                  }}
                  sx={{
                    "& fieldset": { border: "none" },
                    "& .MuiInputBase-root": {
                      height: "48px",
                      backgroundColor: "rgba(255, 255, 255, 0.95)",
                      paddingRight: "26.5px",
                      borderRadius: "15px",
                      fontSize: "20px",
                    },
                    "& .MuiInputBase-input": {
                      color: "rgba(107, 107, 107, 0.5)",
                    },
                  }}
                />
              </div>
            </div>
          </div>
          <div className={styles.questionRow}>
            <div className={styles.questionCardTemplate}>
              <div className={styles.questionTemplate}>Question template?</div>
            </div>
            <div className={styles.questionCardTemplate1}>
              <div className={styles.questionTemplate1}>Question template?</div>
            </div>
          </div>
          <div className={styles.questionRow}>
            <div className={styles.questionCardTemplate}>
              <div className={styles.questionTemplate}>Question template?</div>
            </div>
            <div className={styles.questionCardTemplate1}>
              <div className={styles.questionTemplate1}>Question template?</div>
            </div>
          </div>
        </div>
      </div>
      <div className={styles.goalstipsAccountSummaryChild} />
    </div>
  );
};

export default GoalsTipsAccountSummary;
