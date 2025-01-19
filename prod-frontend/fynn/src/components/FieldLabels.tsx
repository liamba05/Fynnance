import { FunctionComponent, useMemo, type CSSProperties } from "react";
import {
  TextField
} from "@mui/material";
import styles from "./FieldLabels.module.css";

export type FieldLabelsType = {
  className?: string;
  email?: string;
  placeholder?: string;
  value?: string;
  /** Style props */
  emailTextDecoration?: CSSProperties["textDecoration"];
  change?: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

const FieldLabels: FunctionComponent<FieldLabelsType> = ({
  className = "",
  email,
  emailTextDecoration,
  placeholder,
  change,
  value,
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
        value={value}
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
        onChange={change}
      />
    </div>
  );
};

export default FieldLabels;
