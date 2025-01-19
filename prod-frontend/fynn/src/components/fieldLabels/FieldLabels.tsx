import { FunctionComponent, useMemo, type CSSProperties } from "react";
import { TextField, TextFieldProps } from "@mui/material";
import styles from "./FieldLabels.module.css";

export type FieldLabelsType = {
  className?: string;
  email?: string;
  fname?: string;
  lname?: string;
  placeholder?: string;
  type?: string;
  fullWidth?: boolean;
  InputProps?: TextFieldProps['InputProps'];
  emailTextDecoration?: CSSProperties["textDecoration"];
  change?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  value?: string;
};

const FieldLabels: FunctionComponent<FieldLabelsType> = ({
  className = "",
  email,
  fname,
  lname,
  emailTextDecoration,
  placeholder,
  type,
  fullWidth,
  InputProps,
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
          {email || fname || lname}
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
          "& fieldset": { 
            borderColor: "#000",
            borderRadius: "10px",
          },
          "& .MuiInputBase-root": {
            height: "53px",
            backgroundColor: "#fff",
            borderRadius: "10px",
            fontSize: "20px",
            overflow: "hidden",
          },
          "& .MuiOutlinedInput-root": {
            borderRadius: "10px",
            "& fieldset": {
              borderRadius: "10px",
            },
          },
          "& .MuiInputBase-input": { 
            color: "#000",
          },
        }}
        onChange={change}
        value={value}
      />
    </div>
  );
};

export default FieldLabels;
