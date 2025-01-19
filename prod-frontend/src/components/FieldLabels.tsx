import { FunctionComponent, useMemo, type CSSProperties } from "react";
import {
  Box,
  TextField,
  InputAdornment,
  Icon,
  IconButton,
} from "@mui/material";
import styles from "./FieldLabels.module.css";

export type FieldLabelsType = {
  className?: string;
  email?: string;
  placeholder?: string;

  /** Style props */
  emailTextDecoration?: CSSProperties["textDecoration"];
};

const FieldLabels: FunctionComponent<FieldLabelsType> = ({
  className = "",
  email,
  emailTextDecoration,
  placeholder,
}) => {
  const emailStyle: CSSProperties = useMemo(() => {
    return {
      textDecoration: emailTextDecoration,
    };
  }, [emailTextDecoration]);

  return (
    <div className={[styles.fieldLabels, className].join(" ")}>
      <div className={styles.inputLabelPair}>
        <a className={styles.email} style={emailStyle}>
          {email}
        </a>
      </div>
      <TextField
        className={styles.textBox}
        placeholder={placeholder}
        variant="outlined"
        sx={{
          "& fieldset": { borderColor: "#000" },
          "& .MuiInputBase-root": {
            height: "53px",
            backgroundColor: "#fff",
            borderRadius: "10px",
            fontSize: "20px",
          },
          "& .MuiInputBase-input": { color: "#000" },
        }}
      />
    </div>
  );
};

export default FieldLabels;
