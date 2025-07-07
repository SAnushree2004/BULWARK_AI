import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-app.js";
import {
    getFirestore,
    collection,
    query,
    where,
    getDocs,
} from "https://www.gstatic.com/firebasejs/10.11.0/firebase-firestore.js";

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyBfkOLMWNtiTll-7i4wBs6rK8Pg7z2JFjQ",
    authDomain: "bulwarkai-d5db8.firebaseapp.com",
    projectId: "bulwarkai-d5db8",
    storageBucket: "bulwarkai-d5db8.firebasestorage.app",
    messagingSenderId: "707359292845",
    appId: "1:707359292845:web:71db8696204aaa17d3b524",
    measurementId: "G-K2HJDGWGMK",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// Function to update social media links
const updateSocialLinks = async (userEmail) => {
    if (!userEmail) {
        console.error("No user email provided");
        return;
    }

    try {
        // Query the database for the user's social media data
        const q = query(collection(db, "users"), where("email", "==", userEmail));
        const querySnapshot = await getDocs(q);

        if (!querySnapshot.empty) {
            const userData = querySnapshot.docs[0].data();
            const socialMedia = userData.socialMedia || {};

            // Get the container for social media links
            const detailsContainer = document.querySelector(".details_cls");
            if (!detailsContainer) {
                console.error("Social media container not found");
                return;
            }

            // Define the social media platforms and their corresponding icons
            const platforms = [
                { key: "facebook", icon: "fb_icon.png", alt: "Facebook" },
                { key: "instagram", icon: "insta_icon.png", alt: "Instagram" },
                { key: "twitter", icon: "twitter_icon.png", alt: "Twitter" },
                { key: "youtube", icon: "YouTube_icon.png", alt: "YouTube" },
            ];

            // Update each social media link
            platforms.forEach((platform, index) => {
                const link = socialMedia[platform.key];
                const existingP = detailsContainer.children[index];

                if (existingP && link) {
                    existingP.innerHTML = `
                        <span>
                            <img src="static/images/${platform.icon}" alt="${platform.alt}">
                        </span>
                        <span class="social-link ${platform.key}-link">
                            <a href="${link}" target="_blank" rel="noopener noreferrer">${link}</a>
                        </span>
                    `;
                } else if (existingP) {
                    existingP.innerHTML = `
                        <span>
                            <img src="static/images/${platform.icon}" alt="${platform.alt}">
                        </span>
                        <span class="social-link ${platform.key}-link">Not Available</span>
                    `;
                }
            });
        } else {
            console.log("No user found with email:", userEmail);
        }
    } catch (error) {
        console.error("Error fetching social media links:", error);
    }
};

// Wait for DOM to be fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // Use the email passed from Flask
    if (typeof userEmail !== "undefined" && userEmail) {
        updateSocialLinks(userEmail);
    } else {
        console.error("User email not found");
    }
});



// import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-app.js";
// import { getFirestore, collection, query, where, getDocs } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-firestore.js";

// const firebaseConfig = {
//   apiKey: "AIzaSyBfkOLMWNtiTll-7i4wBs6rK8Pg7z2JFjQ",
//   authDomain: "bulwarkai-d5db8.firebaseapp.com",
//   projectId: "bulwarkai-d5db8",
//   storageBucket: "bulwarkai-d5db8.firebasestorage.app",
//   messagingSenderId: "707359292845",
//   appId: "1:707359292845:web:71db8696204aaa17d3b524",
//   measurementId: "G-K2HJDGWGMK"
// };

// // Initialize Firebase
// const app = initializeApp(firebaseConfig);
// const db = getFirestore(app);

// // Function to update social media links
// const updateSocialLinks = async (userEmail) => {
//   if (!userEmail) {
//     console.error("No user email provided");
//     return;
//   }

//   try {
//     const q = query(collection(db, "users"), where("email", "==", userEmail));
//     const querySnapshot = await getDocs(q);

//     if (!querySnapshot.empty) {
//       const userData = querySnapshot.docs[0].data();
//       const socialMedia = userData.socialMedia || {};

//       // Get the container for social media links
//       const detailsContainer = document.querySelector('.details_cls');
//       if (!detailsContainer) {
//         console.error("Social media container not found");
//         return;
//       }

//       // Define the social media platforms and their corresponding icons
//       const platforms = [
//         { key: 'facebook', icon: 'fb_icon.png', alt: 'Facebook' },
//         { key: 'instagram', icon: 'insta_icon.png', alt: 'Instagram' },
//         { key: 'twitter', icon: 'twitter_icon.png', alt: 'Twitter' },
//         { key: 'youtube', icon: 'YouTube_icon.png', alt: 'YouTube' }
//       ];

//       platforms.forEach((platform, index) => {
//     const link = socialMedia[platform.key];
//     const existingP = detailsContainer.children[index];

//     if (existingP && link) {
//         existingP.innerHTML = `
//             <span>
//                 <img src="static/images/${platform.icon}" alt="${platform.alt}">
//             </span>
//             <span class="social-link ${platform.key}-link">
//                 <a href="${link}" target="_blank" rel="noopener noreferrer">${link}</a>
//             </span>
//         `;
//     }
// });
//   } catch (error) {
//     console.error("Error fetching social media links:", error);
//   }
// };

// // Wait for DOM to be fully loaded
// document.addEventListener('DOMContentLoaded', () => {
//   // Use the email passed from Flask
//   if (typeof userEmail !== 'undefined' && userEmail) {
//     updateSocialLinks(userEmail);
//   } else {
//     console.error("User email not found");
//   }
// });