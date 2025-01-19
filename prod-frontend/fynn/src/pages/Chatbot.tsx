import { useState, useRef, useEffect } from "react";
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
import { useChat } from 'ai/react';
// import { openai } from '@ai-sdk/openai';
// import { streamText } from 'ai';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

// export async function POST(req: Request) {
//   const { messages } = await req.json();

//   const result = streamText({
//     model: openai('gpt-4-turbo'),
//     system: 'You are a helpful assistant.',
//     messages,
//   });

//   return result.toDataStreamResponse();
// }

function Chatbot() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuText, setMenuText] = useState("Menu");
  const [showWelcome, setShowWelcome] = useState(true);
  const mockResponses = [
    "I understand what you're saying. Could you tell me more about that?",
    "That's interesting! Let me help you with that.",
    "I see. Here's what I think we could do...",
    "Thanks for sharing. Based on what you've told me, I would suggest...",
    "I'm analyzing your input. Here's my perspective on this matter..."
  ];

  const { messages, input, handleInputChange, setMessages } = useChat({
    initialMessages: [
      { id: '1', role: 'user', content: 'Hello!' },
      { id: '2', role: 'assistant', content: 'Hi there! How can I help you today?' }
    ],
    api: '/api/chat'
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleOptionClick = (text: string) => {
    setMenuText(text);
    setAnchorEl(null);
  };

  const handleNewChat = () => {
    setMessages([]);
    setShowWelcome(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const userMessage = { 
      id: Date.now().toString(), 
      role: 'user' as const, 
      content: input 
    };
    
    // Pick random mock response
    const mockResponse = {
      id: (Date.now() + 1).toString(),
      role: 'assistant' as const,
      content: mockResponses[Math.floor(Math.random() * mockResponses.length)]
    };

    setMessages([...messages, userMessage, mockResponse]);
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
              {messages.map(message => (
                <div 
                  key={message.id} 
                  className={styles.messageItem}
                  data-role={message.role}
                >
                  <span className={styles.messageRole}>
                    {message.role === 'user' ? 'You' : 'Fynn'}
                  </span>
                  <span>{message.content}</span>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Message Input */}
        <form 
          onClick={() => setShowWelcome(false)}
          onSubmit={handleSubmit} 
          className={styles.messageForm}
        >
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            placeholder="Type Message"
            className={styles.messageInput}
          />
          <IconButton type="submit" className={styles.sendButton}>
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
          onClick={handleNewChat}
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
        </div>
      </div>
    </div>
  );
}

export default Chatbot;
