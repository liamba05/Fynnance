import { FunctionComponent } from "react";
import IconSelection from "./IconSelection";
import styles from "./CollapsableLeftSidebar.module.css";

type CollapsableLeftSidebarProps = {
  property1?: string;
  className?: string;
};

const CollapsableLeftSidebar: FunctionComponent<CollapsableLeftSidebarProps> = ({
  property1 = "Default",
  className = ""
}) => {
  return (
    <div className={[styles.collapsableLeftSidebar, className].join(" ")}>
      <div className={styles.collapsableLeftSidebarChild} />
      <IconSelection option={property1} visible={false} />
    </div>
  );
};

export default CollapsableLeftSidebar;