import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import {
  CssBaseline,
  ThemeProvider,
  createTheme,
  StyledEngineProvider,
} from "@mui/material";

import App from "./App";
import "./index.css";

// Create a custom theme for the app
const muiTheme = createTheme({
  palette: {
    primary: {
      main: '#9fdb95',
    },
    secondary: {
      main: '#6ebb61',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    button: {
      textTransform: 'none',
    },
  },
  components: {
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          borderRadius: '20px',
        },
      },
    },
  },
});

const container = document.getElementById("root");
const root = createRoot(container!);

// Check if there's an authToken, if not and not on login/register page, redirect to login
const pathname = window.location.pathname;
if (!localStorage.getItem('authToken') && 
    !pathname.includes('/login') && 
    !pathname.includes('/register')) {
  window.location.href = '/login';
}

root.render(
  <BrowserRouter>
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={muiTheme}>
        <CssBaseline />
        <App/>
      </ThemeProvider>
    </StyledEngineProvider>
  </BrowserRouter>
);
