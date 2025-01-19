import { FunctionComponent } from "react";
import { Button, Box } from "@mui/material";
import ConversationList from "./ConversationList";
import styles from "./ChatSection.module.css";

export type ChatSectionType = {
  className?: string;
};

const ChatSection: FunctionComponent<ChatSectionType> = ({
  className = "",
}) => {
  return (
    <div className={[styles.chatSection, className].join(" ")}>
      <Button
        className={styles.newChatButton}
        endIcon={<img width="32px" height="32px" src="/edit-3.svg" />}
        disableElevation
        variant="contained"
        sx={{
          textTransform: "none",
          color: "#000",
          background: "#9fdb95",
          borderRadius: "0px 0px 0px 0px",
          "&:hover": { background: "#9fdb95" },
          width: 274,
          height: 57,
        }}
      >
        New Chat
      </Button>
      <ConversationList />
    </div>
  );
};

export default ChatSection;
