import {
  Routes,
  Route
} from "react-router-dom";
import { useEffect, useState } from "react";
import Register from "./pages/Register";
import Chatbot from "./pages/Chatbot";
import FinancialInfo from "./pages/FinancialInfo";
import Login from "./pages/Login";
import Goals from "./pages/Goals";
import GoalsTipsAccountSummary from "./pages/GoalsTipsAccountSummary";

interface ProfileData {
  first_name: string;
  last_name: string;
  email: string;
  date_of_birth: string | null;
  preferences: string;
}

function App() {
  const [profileData, setProfileData] = useState<ProfileData | null>(null);

  const fetchProfileData = async () => {
    try {
      // Get the auth token from wherever you store it (localStorage, context, etc.)
      const authToken = localStorage.getItem('authToken');
      if (!authToken) {
        console.error('No auth token found');
        return;
      }

      const headers = {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      };

      // Define the endpoints to fetch
      const endpoints = [
        'first_name',
        'last_name',
        'email',
        'date_of_birth',
        'preferences'
      ];

      // Fetch all data in parallel
      const responses = await Promise.all(
        endpoints.map(endpoint =>
          fetch(`http://localhost:5002/api/user/${endpoint}`, {
            method: 'GET',
            headers,
            credentials: 'include'
          })
        )
      );

      // Process all responses
      const results = await Promise.all(
        responses.map(async (response, index) => {
          if (!response.ok) {
            throw new Error(`Failed to fetch ${endpoints[index]}`);
          }
          const data = await response.json();
          return [endpoints[index], data[endpoints[index]]];
        })
      );

      // Combine all results into a single object
      const profileData = Object.fromEntries(results) as ProfileData;
      setProfileData(profileData);
      
      return profileData;

    } catch (error) {
      console.error('Error fetching profile data:', error);
      return null;
    }
  };

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
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
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
export const backendApiPreface = "http://localhost:5002";
export default App;
