import { FunctionComponent } from "react";
import { Box } from "@mui/material";
import styles from "./ConversationTemplate.module.css";

export type ConversationTemplateType = {
  className?: string;
};

const ConversationTemplate: FunctionComponent<ConversationTemplateType> = ({
  className = "",
}) => {
  return (
    <div className={[styles.conversationTemplate, className].join(" ")}>
      <div className={styles.conversationTemplateChild} />
      <div className={styles.conversationTemplateItem} />
      <img
        className={styles.messageSquareIcon}
        loading="lazy"
        alt=""
        src="/message-square.svg"
      />
      <div className={styles.conversationTemplate1}>Conversation template</div>
    </div>
  );
};

export default ConversationTemplate;
