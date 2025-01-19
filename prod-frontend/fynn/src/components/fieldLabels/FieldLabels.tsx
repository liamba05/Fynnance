import { FunctionComponent, useMemo, type CSSProperties } from "react";
import { TextField, TextFieldProps } from "@mui/material";
import styles from "./FieldLabels.module.css";

export type FieldLabelsType = {
  className?: string;
  email?: string;
  placeholder?: string;
  type?: string;
  fullWidth?: boolean;
  InputProps?: TextFieldProps['InputProps'];
  emailTextDecoration?: CSSProperties["textDecoration"];
};

const FieldLabels: FunctionComponent<FieldLabelsType> = ({
  className = "",
  email,
  emailTextDecoration,
  placeholder,
  type,
  fullWidth,
  InputProps,
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
        type={type}
        fullWidth={fullWidth}
        InputProps={InputProps}
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
