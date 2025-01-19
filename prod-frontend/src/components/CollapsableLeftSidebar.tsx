import { FunctionComponent } from "react";
import { Box } from "@mui/material";
import IconSelection from "./IconSelection";
import styles from "./CollapsableLeftSidebar.module.css";

export type CollapsableLeftSidebarType = {
  className?: string;

  /** Variant props */
  property1?: string;
};

const CollapsableLeftSidebar: FunctionComponent<CollapsableLeftSidebarType> = ({
  className = "",
  property1 = "Default",
}) => {
  return (
    <div
      className={[styles.collapsableLeftSidebar, className].join(" ")}
      data-property1={property1}
    >
      <div className={styles.collapsableLeftSidebarChild} />
      <IconSelection option="Default" visible={false} />
    </div>
  );
};

export default CollapsableLeftSidebar;
