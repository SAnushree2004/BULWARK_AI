// Firebase configuration and initialization
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-app.js";
import { getFirestore, collection, addDoc, query, where, getDocs  } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-firestore.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword} from "https://www.gstatic.com/firebasejs/10.11.0/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyBfkOLMWNtiTll-7i4wBs6rK8Pg7z2JFjQ",
    authDomain: "bulwarkai-d5db8.firebaseapp.com",
    projectId: "bulwarkai-d5db8",
    storageBucket: "bulwarkai-d5db8.firebasestorage.app",
    messagingSenderId: "707359292845",
    appId: "1:707359292845:web:71db8696204aaa17d3b524",
    measurementId: "G-K2HJDGWGMK"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signupForm');
    
    const validateField = (field, message) => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            field.nextElementSibling.textContent = message;
            return false;
        }
        field.classList.remove('is-invalid');
        return true;
    };

    const validateEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const validatePassword = (password, confirmPassword) => {
        if (password.length < 6) {
            return "Password must be at least 6 characters long";
        }
        if (password !== confirmPassword) {
            return "Passwords do not match";
        }
        return null;
    };

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        let isValid = true;
        const errorMessages = [];

        // Get form fields
        const firstname = document.getElementById('firstname');
        const lastname = document.getElementById('lastname');
        const email = document.getElementById('mailid');
        const phone = document.getElementById('phno');
        const password = document.getElementById('crpwd');
        const confirmPassword = document.getElementById('cnpwd');
        const facebookUrl = document.getElementById('facebookurl');
        const instagramUrl = document.getElementById('instagramurl');
        const twitterUrl = document.getElementById('twitterurl');
        const youtubeUrl = document.getElementById('yturl');
        const fbAccessToken = document.getElementById('fbaccesstoken');
        const instaAccessToken = document.getElementById('instaaccesstoken');

        // Validate required fields
        if (!validateField(firstname, 'First name is required')) {
            isValid = false;
            errorMessages.push("First name is required");
        }
        if (!validateField(lastname, 'Last name is required')) {
            isValid = false;
            errorMessages.push("Last name is required");
        }
        if (!validateField(email, 'Email is required')) {
            isValid = false;
            errorMessages.push("Email is required");
        } else if (!validateEmail(email.value)) {
            isValid = false;
            email.classList.add('is-invalid');
            errorMessages.push("Please enter a valid email address");
        }
        if (!validateField(phone, 'Phone number is required')) {
            isValid = false;
            errorMessages.push("Phone number is required");
        } else if (phone.value.length !== 10) {
            isValid = false;
            phone.classList.add('is-invalid');
            errorMessages.push("Phone number must be 10 digits");
        }

        // Validate password
        const passwordError = validatePassword(password.value, confirmPassword.value);
        if (passwordError) {
            isValid = false;
            password.classList.add('is-invalid');
            confirmPassword.classList.add('is-invalid');
            errorMessages.push(passwordError);
        }

        if (!isValid) {
            alert(errorMessages.join('\n'));
            return;
        }

        try {

             // First, check if the email already exists in Firebase Auth
            try {
                // Try to sign in with the email to see if it exists
                await signInWithEmailAndPassword(auth, email.value.trim(), "dummyPassword");
                // If we reach here without an error, it means the email exists
                // (This won't happen as the password is dummy, but we're checking for exceptions)
                alert("Mail id already registered");
                return;

            } catch (signInError) {
                // Check if the error is because the user doesn't exist or because of wrong password
                if (signInError.code === 'auth/user-not-found') {
                    // Email is not registered, continue with registration
                    console.log("Email not found, proceeding with registration");
                } else if (signInError.code === 'auth/wrong-password' || signInError.code === 'auth/invalid-credential') {
                    // Email exists but password is wrong (expected with dummy password)
                    alert("Mail id already registered");
                    return;

                } else {
                    // Some other error occurred
                    throw signInError;
                }
            }

            // Alternatively, check Firestore for the email
            const usersCollection = collection(db, "users");
            const q = query(usersCollection, where("email", "==", email.value.trim()));
            const querySnapshot = await getDocs(q);
            if (!querySnapshot.empty) {
                alert("Mail id already registered");
                return;
            }
            // If we reach here, the email is not registered, proceed with registration

            // Create user with Firebase Authentication
            const userCredential = await createUserWithEmailAndPassword(
                auth,
                email.value.trim(),
                password.value
            );

            // Get current timestamp

            const currentTimestamp = new Date().toISOString();

            // Create token timestamps if tokens are provided

            const fbTokenTimestamp = fbAccessToken.value.trim() ? currentTimestamp : null;

            const instaTokenTimestamp = instaAccessToken.value.trim() ? currentTimestamp : null;

            // Store additional user data in Firestore
            const userData = {
                firstName: firstname.value.trim(),
                lastName: lastname.value.trim(),
                email: email.value.trim(),
                phone: parseInt(phone.value), // Convert to number as per your schema
                socialMedia: {
                    facebook: facebookUrl.value.trim() || null,
                    facebook_access: fbAccessToken.value.trim() || null,
                    facebook_token_timestamp: fbTokenTimestamp,
                    instagram: instagramUrl.value.trim() || null,
                    instagram_access: instaAccessToken.value.trim() || null,
                    instagram_token_timestamp: instaTokenTimestamp,
                    twitter: twitterUrl.value.trim() || null,
                    youtube: youtubeUrl.value.trim() || null
                },
                createdAt: new Date().toISOString(),
                userId: userCredential.user.uid
            };

            // Set the database location
            // const usersCollection = collection(db, "users");
            await addDoc(usersCollection, userData);
            
            alert("Account created successfully!");
            window.location.href = "/login";

        } catch (error) {
            console.error("Signup error:", error);
            alert(error.message || "An error occurred during signup");
        }
    });
});