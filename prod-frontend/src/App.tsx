import { useEffect } from "react";
import {
  Routes,
  Route,
  useNavigationType,
  useLocation,
} from "react-router-dom";
import GoalsTipsAccountSummary from "./pages/GoalsTipsAccountSummary";
import Register from "./pages/Register";
import Chatbot from "./pages/Chatbot";
import FinancialInfo from "./pages/FinancialInfo";
import Login from "./pages/Login";
import Goals from "./pages/Goals";

function App() {
  const action = useNavigationType();
  const location = useLocation();
  const pathname = location.pathname;

  useEffect(() => {
    if (action !== "POP") {
      window.scrollTo(0, 0);
    }
  }, [action, pathname]);

  useEffect(() => {
    let title = "";
    let metaDescription = "";

    switch (pathname) {
      case "/":
        title = "";
        metaDescription = "";
        break;
      case "/register1":
        title = "";
        metaDescription = "";
        break;
      case "/chatbot":
        title = "";
        metaDescription = "";
        break;
      case "/financial-info":
        title = "";
        metaDescription = "";
        break;
      case "/login1":
        title = "";
        metaDescription = "";
        break;
      case "/goals1":
        title = "";
        metaDescription = "";
        break;
    }

    if (title) {
      document.title = title;
    }

    if (metaDescription) {
      const metaDescriptionTag: HTMLMetaElement | null = document.querySelector(
        'head > meta[name="description"]'
      );
      if (metaDescriptionTag) {
        metaDescriptionTag.content = metaDescription;
      }
    }
  }, [pathname]);

  return (
    <Routes>
      <Route path="/" element={<GoalsTipsAccountSummary />} />
      <Route path="/register1" element={<Register />} />
      <Route path="/chatbot" element={<Chatbot />} />
      <Route path="/financial-info" element={<FinancialInfo />} />
      <Route path="/login1" element={<Login />} />
      <Route path="/goals1" element={<Goals />} />
    </Routes>
  );
}
export default App;