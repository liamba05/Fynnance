import { FunctionComponent, useCallback } from "react";
import {
  TextField,
  Button
} from "@mui/material";
import TFrame from "../tFrame/TFrame";
import { useNavigate } from "react-router-dom";
import styles from "./InputPopUp.module.css";

export type InputPopUpType = {
  className?: string;
};

const InputPopUp: FunctionComponent<InputPopUpType> = ({ className = "" }) => {
  const navigate = useNavigate();

  const onSubmitButtonClick = useCallback(() => {
    navigate("/financial-info");
  }, [navigate]);

  const onBackFrameContainerClick = useCallback(() => {
    navigate("/login1");
  }, [navigate]);

  return (
    <div className={[styles.inputPopUp, className].join(" ")}>
      <div className={styles.loginContainerWrapper}>
        <div className={styles.loginContainer}>
          <h1 className={styles.fynnLogin}>Register</h1>
          <form className={styles.inputFrameParent}>
            <div className={styles.inputFrame}>
              <div className={styles.inputs}>
                <div className={styles.tFrame}>
                  <TextField
                    className={styles.textBox}
                    placeholder="John"
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
                      width: "390px",
                    }}
                  />
                  <div className={styles.firstName}>first name</div>
                </div>
                <TFrame lastName="last name" doe="Doe" />
                <div className={styles.tFrame}>
                  <TextField
                    className={styles.textBox1}
                    placeholder="03062"
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
                      width: "390px",
                    }}
                  />
                  <div className={styles.firstName}>email</div>
                </div>
                <TFrame
                  lastName="password"
                  lastNameDisplay="unset"
                  lastNameWidth="unset"
                  doe="password"
                />
                <TFrame
                  lastName="birthday"
                  lastNameDisplay="unset"
                  lastNameWidth="unset"
                  doe="1/1/1999"
                />
              </div>
            </div>
            <div className={styles.submission}>
              <Button
                className={styles.submitButton}
                disableElevation
                variant="contained"
                sx={{
                  textTransform: "none",
                  color: "#000",
                  fontSize: "18",
                  background: "rgba(151, 229, 139, 0.77)",
                  borderRadius: "20px",
                  "&:hover": { background: "rgba(151, 229, 139, 0.77)" },
                  height: 27,
                }}
                onClick={onSubmitButtonClick}
              >{`Continue

`}</Button>
              <div
                className={styles.backFrame}
                onClick={onBackFrameContainerClick}
              >
                <div className={styles.back}>
                  <p className={styles.back1}>back</p>
                </div>
                <img
                  className={styles.union1Icon}
                  loading="lazy"
                  alt=""
                  src="/union1.svg"
                />
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default InputPopUp;
