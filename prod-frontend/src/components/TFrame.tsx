import { FunctionComponent, useMemo, type CSSProperties } from "react";
import {
  TextField,
  InputAdornment,
  Icon,
  IconButton,
  Box,
} from "@mui/material";
import styles from "./TFrame.module.css";
export type TFrameType = {
  className?: string;
  lastName?: string;
  doe?: string;

  /** Style props */
  lastNameDisplay?: CSSProperties["display"];
  lastNameWidth?: CSSProperties["width"];
};

const TFrame: FunctionComponent<TFrameType> = ({
  className = "",
  lastName,
  lastNameDisplay,
  lastNameWidth,
  doe,
}) => {
  const lastNameStyle: CSSProperties = useMemo(() => {
    return {
      display: lastNameDisplay,
      width: lastNameWidth,
    };
  }, [lastNameDisplay, lastNameWidth]);

  return (
    <div className={[styles.tFrame, className].join(" ")}>
      <TextField
        className={styles.textBox}
        variant="outlined"
        sx={{
          "& fieldset": { borderColor: "#000" },
          "& .MuiInputBase-root": {
            height: "53px",
            backgroundColor: "#fff",
            borderRadius: "10px",
          },
          width: "390px",
        }}
      />
      <div className={styles.lastName} style={lastNameStyle}>
        {lastName}
      </div>
      <div className={styles.doe}>{doe}</div>
    </div>
  );
};

export default TFrame;
