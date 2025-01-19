import { FunctionComponent } from "react";
import { Button } from "@mui/material";
import styles from "./QuestionRow.module.css";

export type QuestionRowType = {
  className?: string;
};

const QuestionRow: FunctionComponent<QuestionRowType> = ({
  className = "",
}) => {
  return (
    <div className={[styles.questionRow, className].join(" ")}>
      <Button
        className={styles.questionCardTemplate}
        disableElevation
        variant="contained"
        sx={{
          textTransform: "none",
          color: "#fff",
          fontSize: "20",
          background: "#9fdb95",
          border: "#79c46d solid 1px",
          borderRadius: "20px",
          "&:hover": { background: "#9fdb95" },
          width: 354,
          height: 114,
        }}
      >
        Question template?
      </Button>
      <Button
        className={styles.questionCardTemplate}
        disableElevation
        variant="contained"
        sx={{
          textTransform: "none",
          color: "#fff",
          fontSize: "20",
          background: "#9fdb95",
          border: "#79c46d solid 1px",
          borderRadius: "20px",
          "&:hover": { background: "#9fdb95" },
          width: 354,
          height: 114,
        }}
      >
        Question template?
      </Button>
    </div>
  );
};

export default QuestionRow;
