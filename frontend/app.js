// DOM Elements
const loginSection = document.getElementById('loginSection');
const registerSection = document.getElementById('registerSection');
const dashboardSection = document.getElementById('dashboardSection');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const showRegisterLink = document.getElementById('showRegister');
const showLoginLink = document.getElementById('showLogin');
const userDisplay = document.getElementById('userDisplay');
const plaidButton = document.getElementById('plaidButton');
const logoutButton = document.getElementById('logoutButton');

// Navigation
showRegisterLink.addEventListener('click', (e) => {
    console.log('Show register clicked');
    e.preventDefault();
    loginSection.style.display = 'none';
    registerSection.style.display = 'block';
});

showLoginLink.addEventListener('click', (e) => {
    console.log('Show login clicked');
    e.preventDefault();
    registerSection.style.display = 'none';
    loginSection.style.display = 'block';
});

// Login
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    console.log('Login attempt');
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        await auth.signInWithEmailAndPassword(email, password);
        loginForm.reset();
    } catch (error) {
        console.error('Login error:', error);
        alert('Login error: ' + error.message);
    }
});

// Registration
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    console.log('Registration attempt');
    
    // Validate form data
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    if (password.length < 6) {
        alert('Password must be at least 6 characters long');
        return;
    }

    const userData = {
        firstName: document.getElementById('firstName').value,
        lastName: document.getElementById('lastName').value,
        email: email,
        dateOfBirth: document.getElementById('dateOfBirth').value,
        income: parseFloat(document.getElementById('income').value) || 0,
        assets: parseFloat(document.getElementById('assets').value) || 0,
        zipCode: document.getElementById('zipCode').value,
        createdAt: firebase.firestore.FieldValue.serverTimestamp(),
        updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
        // Add these fields to track Plaid connection status
        plaidConnected: false,
        plaidItemId: null
    };

    try {
        console.log('Creating user with email:', userData.email);
        // Create user in Firebase Auth
        const userCredential = await auth.createUserWithEmailAndPassword(email, password);
        const uid = userCredential.user.uid;
        
        console.log('User created, storing additional data');
        // Store additional user data in Firestore
        await db.collection('users').doc(uid).set(userData);
        
        console.log('User data stored successfully');
        registerForm.reset();
        
        // Switch to dashboard
        loginSection.style.display = 'none';
        registerSection.style.display = 'none';
        dashboardSection.style.display = 'block';
    } catch (error) {
        console.error('Registration error:', error);
        if (error.code === 'auth/email-already-in-use') {
            alert('This email is already registered. Please login instead.');
        } else if (error.code === 'auth/invalid-email') {
            alert('Please enter a valid email address.');
        } else if (error.code === 'auth/operation-not-allowed') {
            alert('Email/password accounts are not enabled. Please contact support.');
        } else if (error.code === 'auth/weak-password') {
            alert('Please choose a stronger password.');
        } else {
            alert('Registration error: ' + error.message);
        }
    }
});

// Logout
logoutButton.addEventListener('click', async () => {
    try {
        await auth.signOut();
        console.log('User signed out successfully');
    } catch (error) {
        console.error('Logout error:', error);
        alert('Logout error: ' + error.message);
    }
});

// Auth state observer
auth.onAuthStateChanged((user) => {
    console.log('Auth state changed:', user ? 'logged in' : 'logged out');
    if (user) {
        // User is signed in
        loginSection.style.display = 'none';
        registerSection.style.display = 'none';
        dashboardSection.style.display = 'block';
        userDisplay.textContent = user.email;
    } else {
        // User is signed out
        loginSection.style.display = 'block';
        registerSection.style.display = 'none';
        dashboardSection.style.display = 'none';
    }
});

// Plaid integration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second
const API_BASE_URL = 'http://localhost:5001';  // Flask server URL

async function retryWithDelay(fn, retries = MAX_RETRIES, delay = RETRY_DELAY) {
    try {
        return await fn();
    } catch (error) {
        console.error('Request failed:', error);
        if (retries > 0) {
            console.log(`Retrying... ${retries} attempts remaining`);
            await new Promise(resolve => setTimeout(resolve, delay));
            return retryWithDelay(fn, retries - 1, delay);
        }
        throw error;
    }
}

plaidButton.addEventListener('click', async () => {
    try {
        console.log('Initializing Plaid connection...');

        // Get the current user's ID token
        const currentUser = auth.currentUser;
        if (!currentUser) {
            throw new Error('User must be logged in to connect bank account');
        }

        console.log('Getting ID token...');
        const idToken = await currentUser.getIdToken();

        // Request link token from your backend with retry logic
        console.log('Requesting link token...');
        const response = await retryWithDelay(async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/create_link_token`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${idToken}`,
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    mode: 'cors'
                });

                console.log('Response status:', res.status);
                console.log('Response headers:', Object.fromEntries(res.headers.entries()));

                if (!res.ok) {
                    const errorText = await res.text();
                    console.error('Error response:', errorText);
                    try {
                        const errorData = JSON.parse(errorText);
                        throw new Error(errorData.error || errorData.details || `HTTP error! status: ${res.status}`);
                    } catch (e) {
                        throw new Error(`HTTP error! status: ${res.status}, body: ${errorText}`);
                    }
                }

                const data = await res.json();
                console.log('Response data:', data);
                return data;
            } catch (error) {
                console.error('Fetch error:', error);
                throw error;
            }
        });

        if (!response.link_token) {
            throw new Error('No link token received from server');
        }

        console.log('Received link token, initializing Plaid...');

        // Initialize Plaid Link
        const config = {
            token: response.link_token,
            onSuccess: async (public_token, metadata) => {
                console.log('Plaid Link success, exchanging public token...');
                try {
                    const currentUser = auth.currentUser;
                    const idToken = await currentUser.getIdToken();

                    // Exchange public token for access token
                    const exchangeResponse = await retryWithDelay(async () => {
                        const res = await fetch(`${API_BASE_URL}/api/exchange_public_token`, {
                            method: 'POST',
                            headers: {
                                'Authorization': `Bearer ${idToken}`,
                                'Content-Type': 'application/json'
                            },
                            credentials: 'include',
                            mode: 'cors',
                            body: JSON.stringify({ public_token })
                        });

                        if (!res.ok) {
                            const errorText = await res.text();
                            console.error('Error response:', errorText);
                            throw new Error(errorText);
                        }

                        return res.json();
                    });

                    // Update Firestore with Plaid connection status
                    await db.collection('users').doc(currentUser.uid).update({
                        plaidConnected: true,
                        plaidItemId: exchangeResponse.item_id,
                        updatedAt: firebase.firestore.FieldValue.serverTimestamp()
                    });

                    console.log('Bank account connected successfully!');
                    alert('Bank account connected successfully!');

                } catch (error) {
                    console.error('Error exchanging public token:', error);
                    alert('Error connecting bank account: ' + error.message);
                }
            },
            onExit: (err, metadata) => {
                if (err != null) {
                    console.error('Plaid Link error:', err);
                    if (err.error_code === 'INVALID_LINK_TOKEN') {
                        alert('Session expired. Please try again.');
                    } else {
                        alert('Error: ' + (err.display_message || err.error_message));
                    }
                }
                console.log('Plaid Link exit:', metadata);
            },
            onEvent: (eventName, metadata) => {
                console.log('Plaid Link event:', eventName, metadata);
                // Handle specific events if needed
                switch(eventName) {
                    case 'ERROR':
                        console.error('Plaid Link error event:', metadata);
                        break;
                    case 'EXIT':
                        if (metadata.status === 'requires_credentials') {
                            console.log('User needs to re-enter credentials');
                        }
                        break;
                }
            }
        };

        const handler = Plaid.create(config);
        handler.open();
    } catch (error) {
        console.error('Error initializing Plaid:', error);
        alert('Error initializing Plaid: ' + error.message + '\n' + error.stack);
    }
}); 