// Force clear all persistent data
(function clearAllPersistentData() {
    // Clear localStorage for all platforms
    localStorage.removeItem('box1_data');
    localStorage.removeItem('box2_data');
    localStorage.removeItem('box3_data');
    localStorage.removeItem('box4_data');
    
    // Try to clear all platform-related indexed DB storage
    if (window.indexedDB) {
        try {
            indexedDB.deleteDatabase('bulwark-platform-data');
        } catch (e) {
            console.log('No indexedDB to clear');
        }
    }
    
    // Clear session storage too
    sessionStorage.clear();
    
    console.log('All persistent data cleared');
})();

// Track which platforms have been analyzed in this session ONLY
const analyzedPlatformsInCurrentSession = {
    'box1': false,  // YouTube
    'box2': false,  // Instagram
    'box3': false,  // Facebook
    'box4': false   // Twitter
};

// On page load, setup and clear any previous data
document.addEventListener('DOMContentLoaded', function() {
    console.log("SESSION-SPECIFIC PLATFORM TRACKING ENABLED");
    
    // Clear localStorage of ALL platform data
    localStorage.removeItem('box1_data');
    localStorage.removeItem('box2_data');
    localStorage.removeItem('box3_data');
    localStorage.removeItem('box4_data');
    
    console.log("All previous platform data cleared from localStorage");
    
    // Setup event listener for complaint button
    const complaintButton = document.getElementById('complaint-button');
    if (complaintButton) {
        complaintButton.addEventListener('click', generateComplaintReport);
    }
});

function setGaugeValue(gauge, value) {
    if (value < 0 || value > 1) {
        value = 0;
    }

    const gaugeFill = gauge.querySelector(".gauge_fill");
    gauge.querySelector(".gauge_fill").style.transform = `rotate(${value / 2}turn)`;

    if (value >= 0 && value <= 0.16) {
        gaugeFill.style.backgroundColor = "rgb(55, 137, 71)";
    } else if (value > 0.16 && value <= 0.33) {
        gaugeFill.style.backgroundColor = "rgb(63, 255, 101)";
    } else if (value > 0.33 && value <= 0.5) {
        gaugeFill.style.backgroundColor = "rgb(216, 255, 75)";
    } else if (value > 0.5 && value <= 0.66) {
        gaugeFill.style.backgroundColor = "rgb(255, 174, 60)";
    } else if (value > 0.66 && value <= 0.83) {
        gaugeFill.style.backgroundColor = "rgb(251, 115, 30)";
    } else if (value > 0.83 && value <= 1) {
        gaugeFill.style.backgroundColor = "rgb(255, 32, 32)";
    }

    gauge.querySelector(".gauge_cover").textContent = `${Math.round(value * 100)}%`;
}

async function getDataFromBackend(userEmail, platform) {
    try {
        console.log(`Fetching data for ${platform} with email:`, userEmail);
        const response = await fetch(`/generate/${platform}`, {
            method: 'POST',
            body: JSON.stringify({"user_email": userEmail}),
            headers: { "Content-Type": "application/json" }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error in getDataFromBackend:', error);
        return null;
    }
}

// function toggleUI(boxId) {
//     try {
//         // Properly declare userEmail
//         let userEmail = localStorage.getItem("email");
//         if (!userEmail) {
//             console.error("No email found in localStorage");
//             alert("Please log in to access this feature.");
//             return;
//         }

//         const boxElement = document.getElementById(boxId);
//         if (!boxElement) {
//             console.error("Box element not found:", boxId);
//             return;
//         }

//         const currentImage = boxElement.querySelector(".status_upr img")?.src;
//         const platformName = boxElement.querySelector(".status_upr img")?.alt;
//         console.log(platformName);
        
//         if (!currentImage) {
//             console.error("Current image not found");
//             return;
//         }

//         // Convert boxId to platform name for API calls
//         const platformMap = {
//             'box1': 'youtube',
//             'box2': 'instagram',
//             'box3': 'facebook',
//             'box4': 'twitter'
//         };
        
//         const platform = platformMap[boxId];
//         if (!platform) {
//             console.error("Invalid box ID:", boxId);
//             return;
//         }

//         // First check if the user has registered this platform in Firebase
//         // We'll make an API call to verify this before proceeding
//         checkPlatformAccount(userEmail, platform)
//             .then(accountExists => {
//                 if (!accountExists) {
//                     // Account doesn't exist for this platform
//                     alert(`No account details found for ${platformName}. Please add your ${platformName} details in your profile.`);
//                     return;
//                 }
                
//                 // Continue with the rest of the function if account exists
//                 proceedWithDataFetch(boxId, platform, platformName, currentImage, userEmail);
//             })
//             .catch(error => {
//                 console.error(`Error checking ${platform} account:`, error);
//                 alert(`Error checking your ${platformName} account details. Please try again later.`);
//             });
//     } catch (error) {
//         console.error('Unexpected error in toggleUI:', error);
//     }
// }

// Function to check if user has registered the platform in Firebase

// Function to check if a token is expired for a specific platform
async function checkTokenExpiry(userEmail, platform) {
    // Only Instagram and Facebook require access tokens
    if (platform !== 'instagram' && platform !== 'facebook') {
        return { expired: false, requiresToken: false };
    }
    
    try {
        const response = await fetch('/check_token_expiry', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_email: userEmail,
                platform: platform
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return {
            expired: data.expired,
            requiresToken: true
        };
    } catch (error) {
        console.error("Error checking token expiry:", error);
        // Default to not expired in case of errors
        return { expired: false, requiresToken: true };
    }
}

// Function to check if user has registered the platform in Firebase
async function checkPlatformAccount(userEmail, platform) {
    try {
        const response = await fetch('/check_platform_account', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_email: userEmail,
                platform: platform
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.exists;
    } catch (error) {
        console.error("Error checking platform account:", error);
        throw error;
    }
}

// The main toggleUI function that performs the checks
function toggleUI(boxId) {
    try {
        // Properly declare userEmail
        let userEmail = localStorage.getItem("email");
        if (!userEmail) {
            console.error("No email found in localStorage");
            return;
        }

        const boxElement = document.getElementById(boxId);
        if (!boxElement) {
            console.error("Box element not found:", boxId);
            return;
        }

        const currentImage = boxElement.querySelector(".status_upr img")?.src;
        const platformName = boxElement.querySelector(".status_upr img")?.alt;
        console.log(platformName);
        
        if (!currentImage) {
            console.error("Current image not found");
            return;
        }

        // Convert boxId to platform name for API calls
        const platformMap = {
            'box1': 'youtube',
            'box2': 'instagram',
            'box3': 'facebook',
            'box4': 'twitter'
        };
        
        const platform = platformMap[boxId];
        if (!platform) {
            console.error("Invalid box ID:", boxId);
            return;
        }

        // First check if the user has registered this platform in Firebase
        checkPlatformAccount(userEmail, platform)
            .then(accountExists => {
                if (!accountExists) {
                    // Account doesn't exist for this platform
                    alert(`No account details found for ${platformName}. Please add your ${platformName} details in your profile.`);
                    return;
                }
                
                // Then check if the token for this platform is expired
                checkTokenExpiry(userEmail, platform)
                    .then(expiryResult => {
                        // If token is expired for a platform that requires tokens, show alert and return
                        if (expiryResult.expired && expiryResult.requiresToken) {
                            const platformDisplay = platform.charAt(0).toUpperCase() + platform.slice(1);
                            alert(`Your ${platformDisplay} access token has expired. Please update it in your profile settings.`);
                            return;
                        }
                        
                        // Continue with normal processing if account exists and token is valid or not required
                        continueWithToggleUI(boxId, platform, platformName, currentImage, userEmail);
                    })
                    .catch(error => {
                        console.error("Error checking token expiry:", error);
                        // Continue with regular processing on error
                        continueWithToggleUI(boxId, platform, platformName, currentImage, userEmail);
                    });
            })
            .catch(error => {
                console.error(`Error checking ${platform} account:`, error);
                alert(`Error checking your ${platformName} account details. Please try again later.`);
            });
    } catch (error) {
        console.error('Unexpected error in toggleUI:', error);
    }
}

// The original toggleUI functionality, extracted into a separate function
function continueWithToggleUI(boxId, platform, platformName, currentImage, userEmail) {
    const boxElement = document.getElementById(boxId);
    
    boxElement.innerHTML = `
        <div class="box_in">
            <img src="${currentImage}" alt="Top-left image" class="top-left-image">
            <div class="status_upr">
                <div class="gauge">
                    <div class="gauge_body">
                        <div class="gauge_fill"></div>
                        <div class="gauge_cover"></div>
                    </div>
                </div>
            </div>
            <div class="status_lwr">
                <button type="button" class="generate-report-btn">
                    <span><img src="static/images/star_icon.png" alt=""></span> &nbsp; Generate Report
                </button>
            </div>
        </div>
    `;

    // Add click event listener to the generate report button
    const generateButton = boxElement.querySelector('.generate-report-btn');
    generateButton.addEventListener('click', () => {
        console.log(boxId, platformName)
        generateReport(boxId, platformName);
    });

    const gaugeElement = boxElement.querySelector(".gauge");
    let currentValue = 0;
    const animationInterval = setInterval(() => {
        currentValue += 0.01;
        if (currentValue > 1) currentValue = 0;
        setGaugeValue(gaugeElement, currentValue);
    }, 50);

    getDataFromBackend(userEmail, platform)
        .then(data => {
            console.log("Received data:", data);
            if (data) {
                clearInterval(animationInterval);
                setGaugeValue(gaugeElement, data.average_score);
                
                // Save data to localStorage
                localStorage.setItem(`${boxId}_data`, JSON.stringify(data));
                
                // Mark this platform as analyzed in THIS session only
                analyzedPlatformsInCurrentSession[boxId] = true;
                console.log(`Marked ${platform} as analyzed in current session`);
                console.log("Current session analyzed platforms:", analyzedPlatformsInCurrentSession);
                
                return saveAsImage(boxId);
            }
        })
        .then(dataURL => {
            if (dataURL) {
                localStorage.setItem(`${boxId}_image`, dataURL);
            }
        })
        .catch(error => {
            console.error('Error in toggleUI:', error);
            clearInterval(animationInterval);
        });
}

async function checkPlatformAccount(userEmail, platform) {
    try {
        // Make an API call to verify if the user has this platform registered
        const response = await fetch('/check_platform_account', {
            method: 'POST',
            body: JSON.stringify({
                "user_email": userEmail,
                "platform": platform
            }),
            headers: { "Content-Type": "application/json" }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return result.exists;
    } catch (error) {
        console.error('Error checking platform account:', error);
        throw error;
    }
}

// Continue with data fetching if account exists
function proceedWithDataFetch(boxId, platform, platformName, currentImage, userEmail) {
    const boxElement = document.getElementById(boxId);
    
    boxElement.innerHTML = `
        <div class="box_in">
            <img src="${currentImage}" alt="Top-left image" class="top-left-image">
            <div class="status_upr">
                <div class="gauge">
                    <div class="gauge_body">
                        <div class="gauge_fill"></div>
                        <div class="gauge_cover"></div>
                    </div>
                </div>
            </div>
            <div class="status_lwr">
                <button type="button" class="generate-report-btn">
                    <span><img src="static/images/star_icon.png" alt=""></span> &nbsp; Generate Report
                </button>
            </div>
        </div>
    `;

    

    // Add click event listener to the generate report button
    const generateButton = boxElement.querySelector('.generate-report-btn');
    generateButton.addEventListener('click', () => {
        console.log(boxId, platformName);
        generateReport(boxId, platformName);
    });

    const gaugeElement = boxElement.querySelector(".gauge");
    let currentValue = 0;
    const animationInterval = setInterval(() => {
        currentValue += 0.01;
        if (currentValue > 1) currentValue = 0;
        setGaugeValue(gaugeElement, currentValue);
    }, 50);

    getDataFromBackend(userEmail, platform)
        .then(data => {
            console.log("Received data:", data);
            if (data) {
                clearInterval(animationInterval);
                setGaugeValue(gaugeElement, data.average_score);
                
                // Clear any previous data for this platform
                localStorage.removeItem(`${boxId}_data`);
                
                // Save data to localStorage
                localStorage.setItem(`${boxId}_data`, JSON.stringify(data));
                
                // Mark this platform as analyzed in THIS session only
                analyzedPlatformsInCurrentSession[boxId] = true;
                console.log(`Marked ${platform} as analyzed in current session`);
                console.log("Current session analyzed platforms:", analyzedPlatformsInCurrentSession);
                
                
                
                return saveAsImage(boxId);
            }
        })
        .then(dataURL => {
            if (dataURL) {
                localStorage.setItem(`${boxId}_image`, dataURL);
            }
        })
        .catch(error => {
            console.error('Error in toggleUI:', error);
            clearInterval(animationInterval);
 
        });
}

async function generateReport(boxId, platformName) {
    try {
        // Retrieve stored data
        const commentsData = JSON.parse(localStorage.getItem(`${boxId}_data`));
        const dataURL = localStorage.getItem(`${boxId}_image`);
        
        if (!commentsData || !dataURL) {
            console.error("Required data not found");
            return;
        }

        // Send to backend
        const response = await fetch('/generate/report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                platform_name: platformName,
                comments_data: commentsData,
                dataurl: dataURL
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // View PDF file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error generating report:', error);
    }
}

function saveAsImage(boxId) {
    return new Promise((resolve, reject) => {
        const boxElement = document.getElementById(boxId);
        const boxInElement = boxElement.querySelector(".box_in");
        const statusLwrElement = boxInElement.querySelector(".status_lwr");

        if (statusLwrElement) {
            statusLwrElement.style.display = "none";
        }

        html2canvas(boxInElement)
            .then(canvas => {
                const dataURL = canvas.toDataURL('image/png');
                console.log("Generated dataURL:", dataURL.substring(0, 100) + "...");
                resolve(dataURL);
            })
            .catch(error => {
                console.error('Failed to save image:', error);
                reject(error);
            })
            .finally(() => {
                if (statusLwrElement) {
                    statusLwrElement.style.display = "";
                }
            });
    });
}

async function generateComplaintReport() {
    try {
        console.log("Generating complaint report...");
        console.log("Current session analyzed platforms:", analyzedPlatformsInCurrentSession);
        
        const platforms = [
            { boxId: 'box1', name: 'YouTube' },
            { boxId: 'box2', name: 'Instagram' },
            { boxId: 'box3', name: 'Facebook' },
            { boxId: 'box4', name: 'Twitter' }
        ];

        // Create a new object to hold ONLY the platforms analyzed in this session
        const allPlatformsData = {};
        let analyzedCount = 0;

        // Loop through platforms and only include those analyzed in this session
        for (const platform of platforms) {
            if (analyzedPlatformsInCurrentSession[platform.boxId]) {
                const data = localStorage.getItem(`${platform.boxId}_data`);
                if (data) {
                    console.log(`Including ${platform.name} in complaint report`);
                    allPlatformsData[platform.name.toLowerCase()] = JSON.parse(data);
                    analyzedCount++;
                } else {
                    console.log(`${platform.name} was analyzed but no data found`);
                }
            } else {
                console.log(`Skipping ${platform.name} - not analyzed in this session`);
                
                // Explicitly ensure this platform data doesn't exist in localStorage
                localStorage.removeItem(`${platform.boxId}_data`);
            }
        }

        if (analyzedCount === 0) {
            alert('No platforms have been analyzed in this session. Please click "Generate" on at least one platform first.');
            return;
        }

        console.log("Platforms included in complaint report:", Object.keys(allPlatformsData));
        
        // Show what will be included in the report
        const platformsToInclude = Object.keys(allPlatformsData).join(', ');
        alert(`Generating report with data from: ${platformsToInclude}`);

        // Send ONLY the platforms we've analyzed in this session
        const response = await fetch('/generate/complaint_report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(allPlatformsData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        // Set the dynamically generated PDF URL in the iframe
        document.getElementById("pdfViewer").src = url;
        document.getElementById("pdfModal").style.display = "block";

        // Clean up object URL after opening
        setTimeout(() => window.URL.revokeObjectURL(url), 1000);
    } catch (error) {
        console.error('Error generating report:', error);
        alert(`Error generating complaint report: ${error.message}`);
    }
}

function closePDF() {
    document.getElementById("pdfModal").style.display = "none";

    // Revoke the object URL to free up memory
    const pdfViewer = document.getElementById("pdfViewer");
    window.URL.revokeObjectURL(pdfViewer.src);
    pdfViewer.src = ""; // Reset iframe src
}

// Attach close event listener (only once, outside the function)
document.getElementById("closeModalBtn")?.addEventListener("click", function () {
    const pdfModal = document.getElementById("pdfModal");
    const pdfViewer = document.getElementById("pdfViewer");

    if (pdfModal) {
        // Cleanup the object URL to free memory
        if (pdfModal.dataset.url) {
            URL.revokeObjectURL(pdfModal.dataset.url);
            pdfModal.dataset.url = "";
        }

        // Hide modal
        pdfModal.style.display = 'none';

        // Clear the iframe src (optional for security)
        if (pdfViewer) {
            pdfViewer.src = "";
        }
    }
});

function sendMail() {
    fetch('/authenticate')
        .then(response => response.json())  // Get the authentication URL
        .then(data => {
            const popup = window.open(data.auth_url, 'authPopup', 'width=600,height=600');

            let timer = setInterval(() => {
                if (popup && popup.closed) {
                    clearInterval(timer);
                    alert("✅ Authentication successful! Email sent.");
                }
            }, 1000);
        })
        .catch(error => console.error("Error fetching auth URL:", error));
}