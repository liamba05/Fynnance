import {
  Routes,
  Route
} from "react-router-dom";
import Register from "./pages/Register";
import Chatbot from "./pages/Chatbot";
import FinancialInfo from "./pages/FinancialInfo";
import Login from "./pages/Login";
import Goals from "./pages/Goals";
import GoalsTipsAccountSummary from "./pages/GoalsTipsAccountSummary";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login/>} />
      <Route path="/login" element={<Login/>} />
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
export const backendApiPreface = "http://localhost:8000";
export default App;
