import { FunctionComponent } from "react";
import { Box } from "@mui/material";
import ConversationTemplate from "./ConversationTemplate";
import styles from "./ConversationList.module.css";

export type ConversationListType = {
  className?: string;
};

const ConversationList: FunctionComponent<ConversationListType> = ({
  className = "",
}) => {
  return (
    <div className={[styles.conversationList, className].join(" ")}>
      <ConversationTemplate />
    </div>
  );
};

export default ConversationList;
