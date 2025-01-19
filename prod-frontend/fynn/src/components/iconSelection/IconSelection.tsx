import { FunctionComponent } from "react";
import {
  Select,
  InputLabel,
  MenuItem,
  FormHelperText,
  FormControl
} from "@mui/material";
import styles from "./IconSelection.module.css";

export type IconSelectionType = {
  className?: string;

  /** Variant props */
  option?: string;
  visible?: boolean;
};

const IconSelection: FunctionComponent<IconSelectionType> = ({
  className = "",
  option = "Default",
  visible = false,
}) => {
  return (
    <div
      className={[styles.iconSelection, className].join(" ")}
      data-option={option}
      data-visible={visible}
    >
      <div className={styles.incomeWrapper}>
        <a className={styles.income}>income</a>
      </div>
      <FormControl
        className={styles.textBox}
        variant="standard"
        sx={{
          borderColor: "#000",
          borderStyle: "SOLID",
          borderTopWidth: "1px",
          borderRightWidth: "1px",
          borderBottomWidth: "1px",
          borderLeftWidth: "1px",
          backgroundColor: "#fff",
          borderRadius: "10px",
          width: "99.23664122137404%",
          height: "51px",
          m: 0,
          p: 0,
          "& .MuiInputBase-root": {
            m: 0,
            p: 0,
            minHeight: "51px",
            justifyContent: "center",
            display: "inline-flex",
          },
          "& .MuiInputLabel-root": {
            m: 0,
            p: 0,
            minHeight: "51px",
            display: "inline-flex",
          },
          "& .MuiMenuItem-root": {
            m: 0,
            p: 0,
            height: "51px",
            display: "inline-flex",
          },
          "& .MuiSelect-select": {
            m: 0,
            p: 0,
            height: "51px",
            alignItems: "center",
            display: "inline-flex",
          },
          "& .MuiInput-input": { m: 0, p: 0 },
          "& .MuiInputBase-input": {
            color: "#000",
            fontSize: 20,
            fontWeight: "Regular",
            fontFamily: "Heebo",
            textAlign: "left",
            p: "0 !important",
            marginLeft: "16px",
          },
        }}
      >
        <InputLabel color="secondary" />
        <Select
          color="secondary"
          disableUnderline
          displayEmpty
        >
          <MenuItem>{`select `}</MenuItem>
        </Select>
        <FormHelperText />
      </FormControl>
    </div>
  );
};

export default IconSelection;
