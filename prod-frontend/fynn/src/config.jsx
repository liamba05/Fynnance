// Firebase configuration
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDfqtiZe5JTow-Zfa23QTaW5W_9eIuLzBg",
  authDomain: "fynnance-5031a.firebaseapp.com",
  projectId: "fynnance-5031a",
  storageBucket: "fynnance-5031a.firebasestorage.app",
  messagingSenderId: "258766016727",
  appId: "1:258766016727:web:3109e527f2249b661d6092",
  measurementId: "G-3FD2DRE0FS"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export { auth, db };