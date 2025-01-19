import { FunctionComponent } from "react";
import {
  Box,
  Select,
  InputLabel,
  MenuItem,
  FormHelperText,
  FormControl,
  InputAdornment,
} from "@mui/material";
import CollapsableLeftSidebar from "../components/CollapsableLeftSidebar";
import FynnResponseLayout from "../components/FynnResponseLayout";
import DefaultChatDesign from "../components/DefaultChatDesign";
import UserQuestionLayout from "../components/UserQuestionLayout";
import ChatSection from "../components/ChatSection";
import GoalTipsButton from "../components/GoalTipsButton";
import styles from "./Chatbot.module.css";

export type ChatbotType = {
  onClose?: () => void;
};

const Chatbot: FunctionComponent<ChatbotType> = ({ onClose }) => {
  return (
    <div className={styles.chatbot}>
      <div className={styles.collapsableLeftSidebarWrapper}>
        <CollapsableLeftSidebar property1="Default" />
      </div>
      <div className={styles.messageBarLayout}>
        <div className={styles.messageBarLayoutInner}>
          <div className={styles.frameParent}>
            <div className={styles.fynnResponseLayoutParent}>
              <FynnResponseLayout />
              <DefaultChatDesign />
            </div>
            <FormControl
              className={styles.parent}
              variant="standard"
              sx={{
                borderTopWidth: "0px",
                borderRightWidth: "0px",
                borderBottomWidth: "0px",
                borderLeftWidth: "0px",
                borderRadius: "0px 0px 0px 0px",
                width: "95.09132420091323%",
                height: "76px",
                m: 0,
                p: 0,
                "& .MuiInputBase-root": {
                  m: 0,
                  p: 0,
                  minHeight: "76px",
                  justifyContent: "center",
                  display: "inline-flex",
                },
                "& .MuiInputLabel-root": {
                  m: 0,
                  p: 0,
                  minHeight: "76px",
                  display: "inline-flex",
                },
                "& .MuiMenuItem-root": {
                  m: 0,
                  p: 0,
                  height: "76px",
                  display: "inline-flex",
                },
                "& .MuiSelect-select": {
                  m: 0,
                  p: 0,
                  height: "76px",
                  alignItems: "center",
                  display: "inline-flex",
                },
                "& .MuiInput-input": { m: 0, p: 0 },
                "& .MuiInputBase-input": {
                  color: "rgba(107, 107, 107, 0.5)",
                  fontSize: 20,
                  fontWeight: "SemiBold",
                  fontFamily: "IBM Plex Mono",
                  textAlign: "left",
                  p: "0 !important",
                  marginLeft: "62px",
                },
              }}
            >
              <InputLabel color="primary" />
              <Select
                color="primary"
                disableUnderline
                displayEmpty
                IconComponent={() => (
                  <img
                    width="56.6px"
                    height="56.6px"
                    src="/send.png"
                    style={{ marginRight: "81.4px" }}
                  />
                )}
              >
                <MenuItem>Type Message</MenuItem>
              </Select>
              <FormHelperText />
            </FormControl>
          </div>
        </div>
        <div className={styles.messageBarLayoutChild} />
      </div>
      <header className={styles.frameGroup}>
        <div className={styles.frameWrapper}>
          <div className={styles.frameContainer}>
            <div className={styles.leftCollapsableButtonWrapper}>
              <img
                className={styles.leftCollapsableButton}
                loading="lazy"
                alt=""
                src="/left-collapsable-button.svg"
              />
            </div>
            <img
              className={styles.chevronBottomNormalIcon}
              loading="lazy"
              alt=""
              src="/chevronbottomnormal.svg"
            />
          </div>
        </div>
        <UserQuestionLayout />
      </header>
      <div className={styles.frameDiv}>
        <div className={styles.chatSectionWrapper}>
          <ChatSection />
        </div>
        <div className={styles.vectorParent}>
          <img
            className={styles.frameChild}
            loading="lazy"
            alt=""
            src="/line-1.svg"
          />
          <div className={styles.frameWrapper1}>
            <div className={styles.goaltipsButtonParent}>
              <GoalTipsButton />
              <div className={styles.frameParent1}>
                <div className={styles.goaltipsButtonParent}>
                  <img
                    className={styles.tvIcon}
                    loading="lazy"
                    alt=""
                    src="/tv.svg"
                  />
                  <img
                    className={styles.tvIcon}
                    loading="lazy"
                    alt=""
                    src="/user.svg"
                  />
                  <img
                    className={styles.tvIcon}
                    loading="lazy"
                    alt=""
                    src="/settings.svg"
                  />
                </div>
                <div className={styles.frameWrapper2}>
                  <div className={styles.liveNewsParent}>
                    <div className={styles.liveNews}>Live News</div>
                    <div className={styles.profile}>Profile</div>
                    <div className={styles.settings}>Settings</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
