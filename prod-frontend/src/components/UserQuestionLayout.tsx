import { FunctionComponent } from "react";
import { Button, Box } from "@mui/material";
import styles from "./UserQuestionLayout.module.css";

export type UserQuestionLayoutType = {
  className?: string;
};

const UserQuestionLayout: FunctionComponent<UserQuestionLayoutType> = ({
  className = "",
}) => {
  return (
    <div className={[styles.userQuestionLayout, className].join(" ")}>
      <Button
        className={styles.userQuestionBubble}
        disableElevation
        variant="contained"
        sx={{
          textTransform: "none",
          color: "#000",
          fontSize: "20",
          background: "#fff",
          border: "#9fdb95 solid 3px",
          borderRadius: "50px",
          "&:hover": { background: "#fff" },
          width: 233,
          height: 58,
        }}
      >
        User Question?
      </Button>
    </div>
  );
};

export default UserQuestionLayout;
