import { useEffect } from "react";
import {
  Routes,
  Route,
  useNavigationType,
  useLocation,
} from "react-router-dom";
import Register from "./pages/Register";
import Chatbot from "./pages/Chatbot";
import FinancialInfo from "./pages/FinancialInfo";
import Login from "./pages/Login";
import Goals from "./pages/Goals";
import GoalsTipsAccountSummary from "./pages/GoalsTipsAccountSummary";

function App() {
  // const action = useNavigationType();
  // const location = useLocation();
  // const pathname = location.pathname;

  // useEffect(() => {
  //   if (action !== "POP") {
  //     window.scrollTo(0, 0);
  //   }
  // }, [action, pathname]);

  // useEffect(() => {
  //   let title = "";
  //   let metaDescription = "";

  //   switch (pathname) {
  //     case "/":
  //       title = "";
  //       metaDescription = "";
  //       break;
  //     case "/chatbot":
  //       title = "";
  //       metaDescription = "";
  //       break;
  //     case "/financial-info":
  //       title = "";
  //       metaDescription = "";
  //       break;
  //     case "/login1":
  //       title = "";
  //       metaDescription = "";
  //       break;
  //     case "/goals1":
  //       title = "";
  //       metaDescription = "";
  //       break;
  //     case "/goalstips-account-summary":
  //       title = "";
  //       metaDescription = "";
  //       break;
  //   }

  //   if (title) {
  //     document.title = title;
  //   }

  //   if (metaDescription) {
  //     const metaDescriptionTag: HTMLMetaElement | null = document.querySelector(
  //       'head > meta[name="description"]'
  //     );
  //     if (metaDescriptionTag) {
  //       metaDescriptionTag.content = metaDescription;
  //     }
  //   }
  // }, [pathname]);

  return (
    <Routes>
      <Route path="/" element={<Login/>} />
      <Route path="/chatbot" element={<Chatbot />} />
      <Route path="/financial-info" element={<FinancialInfo />} />
      <Route path="/register" element={<Register />} />
      <Route path="/goals" element={<Goals />} />
      <Route
        path="/goalstips-account-summary"
        element={<GoalsTipsAccountSummary />}
      />
    </Routes>
  );
}
export default App;

{/* <Route path="/chatbot" element={<DefaultChatDesign />} />
<Route path="/login" element={<DefaultChatDesign />} />
<Route path="/signup" element={<DefaultChatDesign />} />
<Route path="/register" element={<DefaultChatDesign />} />
<Route path="/finances" element={<DefaultChatDesign />} />
<Route path="/goals" element={<DefaultChatDesign />} />
<Route path="/settings" element={<DefaultChatDesign />} />
<Route path="/profile" element={<DefaultChatDesign />} />
<Route path="/goal-sum" element={<DefaultChatDesign />} />
// this will be the landing page, temp is the chatbot
<Route path="/" element={<DefaultChatDesign />} /> */}

