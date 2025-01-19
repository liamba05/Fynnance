import { useState } from "react";
import { Button, IconButton, Menu, MenuItem } from "@mui/material";
import styles from "./Chatbot.module.css";
import EditIcon from '@mui/icons-material/Edit';
import SendIcon from '@mui/icons-material/Send';
import MenuIcon from '@mui/icons-material/Menu';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TvIcon from '@mui/icons-material/Tv';
import PersonIcon from '@mui/icons-material/Person';
import SettingsIcon from '@mui/icons-material/Settings';
import Fynn100X100PxRectangle from "../components/Fynn100X100PxRectangle";
import fynnLogo from '../assets/fynn-100-x-100-px-rectangle-sticker-portrait-2@3x.png';
// import '@chatscope/chat-ui-kit-react-styles/dist/default/styles.min.css';
// import { MainContainer, ChatContainer, MessageList, Message } from '@chatscope/chat-ui-kit-react';

interface ChatMessage {
  sender: string;
  message: string;
  direction: string;
}

function Chatbot() {
  const [message, setMessage] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuText, setMenuText] = useState("Menu");
  const [showWelcome, setShowWelcome] = useState(true);

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);

  const handleSubmit = async (message: string) => {
    setShowWelcome(false);
    const newMessage: ChatMessage = {
      sender: "user",
      message: message,
      direction: "outgoing",
    };
    setChatMessages([...chatMessages, newMessage]);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleOptionClick = (text: string) => {
    setMenuText(text);
    setAnchorEl(null);
  };



  return (
    <div className={styles.chatbot}>
      {/* Right Sidebar (now on left) */}
      <div className={styles.rightSidebar}>
        <div className={styles.rightSidebarContent}>
          <Button
            endIcon={<KeyboardArrowDownIcon />}
            onClick={handleMenuClick}
            className={styles.menuButton}
          >
            {menuText}
          </Button>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
            className={styles.dropdownMenu}
          >
            <MenuItem onClick={() => handleOptionClick("Goals + Tips")}>
              <TrendingUpIcon sx={{ marginRight: '8px' }} />
              Goals + Tips
            </MenuItem>
            <MenuItem onClick={() => handleOptionClick("Live News")}>
              <TvIcon sx={{ marginRight: '8px' }} />
              Live News
            </MenuItem>
            <MenuItem onClick={() => handleOptionClick("Profile")}>
              <PersonIcon sx={{ marginRight: '8px' }} />
              Profile
            </MenuItem>
            <MenuItem onClick={() => handleOptionClick("Settings")}>
              <SettingsIcon sx={{ marginRight: '8px' }} />
              Settings
            </MenuItem>
          </Menu>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className={styles.mainContent}>
        {/* Toggle Sidebar Button */}
        <IconButton 
          className={styles.toggleButton}
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        >
          <MenuIcon />
        </IconButton>

        {/* Chat Messages Area */}
        <div className={styles.messagesArea}>
          <div className={styles.welcomeMessage} style={{ display: showWelcome ? 'flex' : 'none' }}>
            <div className={styles.logoContainer}>
              <div className={styles.fynnLogoWrapper}>
                <Fynn100X100PxRectangle
                  fynn100X100PxRectangleBackgroundImage={`url(${fynnLogo})`}
                  showFynn
                  fynnTextDecoration="none"
                  fynnHeight="120px"
                  fynnWidth="399px"
                  fynnPosition="relative"
                  fynnFontWeight="unset"
                  fynnTop="unset"
                />
              </div>
            </div>
            <div className={styles.questionTemplates}>
              <Button variant="contained" className={styles.templateButton}>
                Question template?
              </Button>
              <Button variant="contained" className={styles.templateButton}>
                Question template?
              </Button>
            </div>
          </div>
          {!showWelcome && (
            <div className={styles.chatMessages}>
              <MainContainer>
                <ChatContainer>
                  <MessageList>
                    {chatMessages.map((message, index) => (
                      <Message key={index} model={{
                        message: message.message,
                        sender: message.sender,
                        direction: message.direction
                      }} />
                    ))}
                  </MessageList>
                </ChatContainer>
              </MainContainer>
            </div>
          )}
        </div>

        {/* Message Input */}
        <form onSubmit={() => handleSubmit(message)} className={styles.messageForm}>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type Message"
            className={styles.messageInput}
          />
          <IconButton type="submit" className={styles.sendButton} 
          onSubmit={() => handleSubmit(message)}>
            <SendIcon />
          </IconButton>
        </form>
      </div>

      {/* Left Sidebar (now on right) */}
      <div className={`${styles.sidebar} ${isSidebarOpen ? styles.open : styles.closed}`}>
        <Button
          className={styles.newChatButton}
          startIcon={<EditIcon />}
          fullWidth
          variant="contained"
          sx={{
            background: "#9fdb95",
            color: "#000",
            textTransform: "none",
            fontSize: "16px",
            padding: "12px",
            "&:hover": { background: "#8bc681" },
          }}
        >
          New Chat
        </Button>
        <div className={styles.sidebarContent}>
          {/* Previous chats would go here */}
        </div>
      </div>
    </div>
  );
}

export default Chatbot;
