import { FunctionComponent } from "react";
import FynnResponse from "../fynnResponse/FynnResponse";
import styles from "./FynnResponseLayout.module.css";

export type FynnResponseLayoutType = {
  className?: string;
};

const FynnResponseLayout: FunctionComponent<FynnResponseLayoutType> = ({
  className = "",
}) => {
  return (
    <div className={[styles.fynnResponseLayout, className].join(" ")}>
      <FynnResponse />
    </div>
  );
};

export default FynnResponseLayout;
