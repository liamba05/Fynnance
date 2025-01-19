import { FunctionComponent } from "react";
import styles from "./IconSelection.module.css";

type IconSelectionProps = {
  option?: string;
  visible?: boolean;
};

const IconSelection: FunctionComponent<IconSelectionProps> = ({
  option = "Default",
  visible = true
}) => {
  return (
    <div className={styles.iconSelection} data-option={option}>
      {visible && <div className={styles.icon} />}
    </div>
  );
};

export default IconSelection; 