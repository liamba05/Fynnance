import { FunctionComponent, useCallback } from "react";
import {
  TextField,
  Button
} from "@mui/material";
import TFrame from "../tFrame/TFrame";
import { useNavigate } from "react-router-dom";
import styles from "./InputPopUp.module.css";
import FieldLabels from "../FieldLabels";

export type InputPopUpType = {
  className?: string;
};

const InputPopUp: FunctionComponent<InputPopUpType> = ({ className = "" }) => {
  const navigate = useNavigate();

  const onSubmitButtonClick = useCallback(() => {
    navigate("/financial-info");
  }, [navigate]);

  const onBackFrameContainerClick = useCallback(() => {
    navigate("/login");
  }, [navigate]);

  return (
    <div className={[styles.inputPopUp, className].join(" ")}>
      <div className={styles.loginContainerWrapper}>
        <div className={styles.loginContainer}>
          <h1 className={styles.fynnLogin}>Register</h1>
          <form className={styles.frameGroup}>
            <div className={styles.inputArea}>
              <FieldLabels 
                email="first name" 
                placeholder="John"
               
              />
              <FieldLabels
                email="last name "
                placeholder="Doe"
              />
              <FieldLabels
                email="last name "
                placeholder="Doe"
              />
              <FieldLabels
                email="email "
                placeholder="johndoe@gmail.com"
              />
              <FieldLabels
                email="password"
                placeholder="password"
              />
              <FieldLabels
                email="birthday"
                placeholder="1/1/1999"
              />
            </div>
            
          </form>
         
      
        </div>
      </div>
    </div>
  );
};

export default InputPopUp;
