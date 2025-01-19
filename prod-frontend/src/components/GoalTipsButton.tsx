import { FunctionComponent } from "react";
import { Box } from "@mui/material";
import styles from "./GoalTipsButton.module.css";

export type GoalTipsButtonType = {
  className?: string;
};

const GoalTipsButton: FunctionComponent<GoalTipsButtonType> = ({
  className = "",
}) => {
  return (
    <div className={[styles.goaltipsButton, className].join(" ")}>
      <img
        className={styles.trendingUpIcon}
        loading="lazy"
        alt=""
        src="/trending-up.svg"
      />
      <div className={styles.goalsTips}>Goals + Tips</div>
    </div>
  );
};

export default GoalTipsButton;
