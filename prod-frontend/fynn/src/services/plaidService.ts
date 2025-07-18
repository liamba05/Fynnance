import { auth, db } from "../config";

declare global {
  interface Window {
    Plaid: {
      create: (config: any) => { open: () => void };
    };
  }
}

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5001";
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

async function retryWithDelay(
  fn: () => Promise<any>,
  retries = MAX_RETRIES,
  delay = RETRY_DELAY
) {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0) {
      await new Promise((resolve) => setTimeout(resolve, delay));
      return retryWithDelay(fn, retries - 1, delay);
    }
    throw error;
  }
}

export const initializePlaid = async () => {
  try {
    const currentUser = auth.currentUser;
    if (!currentUser) {
      throw new Error("User must be logged in to connect bank account");
    }

    try {
      const healthCheck = await fetch(`${API_BASE_URL}/health`);
      if (!healthCheck.ok) {
        throw new Error("Backend server is not responding");
      }
    } catch (error) {
      throw new Error("Cannot connect to backend server. Please ensure the server is running.");
    }

    const idToken = await currentUser.getIdToken();
    const response = await retryWithDelay(async () => {
      const res = await fetch(`${API_BASE_URL}/api/create_link_token`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${idToken}`,
          "Content-Type": "application/json",
        },
        credentials: "include",
        mode: "cors",
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.json();
    });

    if (!response.link_token) {
      throw new Error("No link token received from server");
    }

    const config = {
      token: response.link_token,
      onSuccess: async (public_token: string) => {
        try {
          const idToken = await currentUser.getIdToken();
          const exchangeResponse = await retryWithDelay(async () => {
            const res = await fetch(
              `${API_BASE_URL}/api/exchange_public_token`,
              {
                method: "POST",
                headers: {
                  Authorization: `Bearer ${idToken}`,
                  "Content-Type": "application/json",
                },
                credentials: "include",
                mode: "cors",
                body: JSON.stringify({ public_token }),
              }
            );

            if (!res.ok) {
              throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
          });

          await db.collection("users").doc(currentUser.uid).update({
            plaidConnected: true,
            plaidItemId: exchangeResponse.item_id,
            updatedAt: new Date(),
          });

          alert("Bank account connected successfully!");
        } catch (error) {
          console.error("Error exchanging public token:", error);
          alert("Error connecting bank account: " + error.message);
        }
      },
      onExit: (err: any) => {
        if (err != null) {
          if (err.error_code === "INVALID_LINK_TOKEN") {
            alert("Session expired. Please try again.");
          } else {
            alert("Error: " + (err.display_message || err.error_message));
          }
        }
      },
    };

    // @ts-ignore
    const handler = window.Plaid.create(config);
    handler.open();
  } catch (error) {
    console.error("Error initializing Plaid:", error);
    alert("Error initializing Plaid: " + error.message);
  }
};
