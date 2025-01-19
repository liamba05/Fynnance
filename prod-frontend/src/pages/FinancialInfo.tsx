import { FunctionComponent, useCallback } from "react";
import {
  Typography,
  TextField,
  InputAdornment,
  Icon,
  IconButton,
  Box,
  Button,
} from "@mui/material";
import Fynn100X100PxRectangle from "../components/Fynn100X100PxRectangle";
import IncomeSelect from "../components/IncomeSelect";
import { useNavigate } from "react-router-dom";
import styles from "./FinancialInfo.module.css";

const FinancialInfo: FunctionComponent = () => {
  const navigate = useNavigate();

  const onBackFrameContainerClick = useCallback(() => {
    navigate("/register1");
  }, [navigate]);

  const onSkipFrameContainerClick = useCallback(() => {
    navigate("/goals1");
  }, [navigate]);

  return (
    <div className={styles.financialInfo}>
      <Fynn100X100PxRectangle showFynn />
      <section className={styles.financialInfoInner}>
        <div className={styles.registrationInputsParent}>
          <div className={styles.registrationInputs}>
            <h1 className={styles.fynnLogin}>Finances</h1>
            <div className={styles.frameParent}>
              <form className={styles.loginInputContainerParent}>
                <div className={styles.loginInputContainer}>
                  <IncomeSelect option="Default" visible={false} />
                  <div className={styles.loginInputContainerInner}>
                    <div className={styles.textBoxParent}>
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
                      <div className={styles.goals}>assets</div>
                    </div>
                  </div>
                  <div className={styles.frameGroup}>
                    <div className={styles.zipCodeWrapper}>
                      <div className={styles.zipCode}>zip code</div>
                    </div>
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
                      }}
                    />
                  </div>
                </div>
                <Button
                  className={styles.frameChild}
                  disableElevation
                  variant="text"
                  sx={{
                    textTransform: "none",
                    color: "#000",
                    fontSize: "18",
                    borderRadius: "0px 0px 0px 0px",
                    height: 27,
                  }}
                >
                  Continue
                </Button>
              </form>
              <div className={styles.navigationContainerWrapper}>
                <div className={styles.navigationContainer}>
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
                      src="/union11.svg"
                    />
                  </div>
                  <div
                    className={styles.backFrame}
                    onClick={onSkipFrameContainerClick}
                  >
                    <div className={styles.skipParent}>
                      <div className={styles.skip}>{`skip `}</div>
                      <img
                        className={styles.union1Icon1}
                        loading="lazy"
                        alt=""
                        src="/union1-1.svg"
                      />
                    </div>
                    <img
                      className={styles.union1Icon2}
                      loading="lazy"
                      alt=""
                      src="/union1-2.svg"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className={styles.disclaimerTheIncome}>
            Disclaimer: The income data you provide is used solely to
            personalize your responses. Your zip code is used to identify job
            opportunities and real estate options in your area. We prioritize
            the security and confidentiality of your data.
          </div>
        </div>
      </section>
    </div>
  );
};

export default FinancialInfo;
