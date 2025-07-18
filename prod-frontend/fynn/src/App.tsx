import { Routes, Route, Navigate } from "react-router-dom";
import { useEffect, useState, createContext } from "react";
import Register from "./pages/Register";
import Chatbot from "./pages/Chatbot";
import FinancialInfo from "./pages/FinancialInfo";
import Login from "./pages/Login";
import Goals from "./pages/Goals";
import GoalsTipsAccountSummary from "./pages/GoalsTipsAccountSummary";
import { auth } from "./config";
import { onAuthStateChanged } from "firebase/auth";

interface ProfileData {
  first_name: string;
  last_name: string;
  email: string;
  date_of_birth: string | null;
  preferences: string;
}

export const UserContext = createContext<{
  profileData: ProfileData | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}>({
  profileData: null,
  isAuthenticated: false,
  isLoading: true
});

function App() {
  const [profileData, setProfileData] = useState<ProfileData | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication state
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        setIsAuthenticated(true);
        // Store a token for API calls
        user.getIdToken().then(token => {
          localStorage.setItem('authToken', token);
        });
        // Try to fetch profile data
        fetchProfileData();
      } else {
        setIsAuthenticated(false);
        localStorage.removeItem('authToken');
      }
      setIsLoading(false);
    });

    return () => unsubscribe();
  }, []);

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

      try {
        // Fetch all data in parallel
        const responses = await Promise.all(
          endpoints.map(endpoint =>
            fetch(`${backendApiPreface}/api/user/${endpoint}`, {
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
        // If backend is not available, use data from Firebase
        const user = auth.currentUser;
        if (user) {
          setProfileData({
            first_name: user.displayName?.split(' ')[0] || '',
            last_name: user.displayName?.split(' ')[1] || '',
            email: user.email || '',
            date_of_birth: null,
            preferences: ''
          });
        }
      }
    } catch (error) {
      console.error('Error fetching profile data:', error);
      return null;
    }
  };
  // Create a protected route component
  const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    if (isLoading) {
      // Render a loading indicator
      return <div className="loading">Loading...</div>;
    }

    if (!isAuthenticated) {
      // Redirect to login if not authenticated
      return <Navigate to="/login" />;
    }

    return (
      <UserContext.Provider value={{ profileData, isAuthenticated, isLoading }}>
        {children}
      </UserContext.Provider>
    );
  };

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* Protected routes */}
      <Route path="/chatbot" element={
        <ProtectedRoute>
          <Chatbot />
        </ProtectedRoute>
      } />
      <Route path="/financial-info" element={
        <ProtectedRoute>
          <FinancialInfo />
        </ProtectedRoute>
      } />
      <Route path="/goals" element={
        <ProtectedRoute>
          <Goals />
        </ProtectedRoute>
      } />
      <Route path="/goalstips-account-summary" element={
        <ProtectedRoute>
          <GoalsTipsAccountSummary />
        </ProtectedRoute>
      } />
      
      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}

// Backend API URL
export const backendApiPreface = "http://localhost:5002";

export default App;
