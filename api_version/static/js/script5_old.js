
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

// async function getDataFromBackend(userEmail) {
//     try {
//         console.log("Fetching data for email:", userEmail);
//         const response = await fetch('/generate/youtube', {
//             method: 'POST',
//             body: JSON.stringify({"user_email": userEmail}),
//             headers: { "Content-Type": "application/json" }
//         });

//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }

//         return await response.json();
//     } catch (error) {
//         console.error('Error in getDataFromBackend:', error);
//         return null;
//     }
// }
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
        console.log(platformName)
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

        let responseData;
        getDataFromBackend(userEmail, platform)
            .then(data => {
                console.log("Received data:", data);
                if (data) {
                    clearInterval(animationInterval);
                    setGaugeValue(gaugeElement, data.average_score);
                    localStorage.setItem(`${boxId}_data`, JSON.stringify(data));
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
    } catch (error) {
        console.error('Unexpected error in toggleUI:', error);
    }
}

//         // Fetch data from the backend
//         getDataFromBackend(userEmail)
//             .then(data => {
//                 console.log("Received data:", data);
//                 if (data) {
//                     clearInterval(animationInterval);
//                     setGaugeValue(gaugeElement, data.average_score);
//                     responseData = data; // Store the response data
//                     // Save the data in localStorage for report generation
//                     localStorage.setItem(`${boxId}_data`, JSON.stringify(data));
//                     return saveAsImage(boxId);
//                 }
//             })
//             .then(dataURL => {
//                 if (dataURL) {
//                     // Save the dataURL in localStorage for report generation
//                     localStorage.setItem(`${boxId}_image`, dataURL);
//                 }
//             })
//             .catch(error => {
//                 console.error('Error in toggleUI:', error);
//                 clearInterval(animationInterval);
//             });
//     } catch (error) {
//         console.error('Unexpected error in toggleUI:', error);
//     }
// }

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

        // Downloading PDF file
        // const blob = await response.blob();
        // const url = window.URL.createObjectURL(blob);
        // const a = document.createElement('a');
        // a.href = url;
        // a.download = `${platformName}_report.pdf`;
        // document.body.appendChild(a);
        // a.click();
        // document.body.removeChild(a);
        // window.URL.revokeObjectURL(url);

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



// -----------------------------------------------------------------------------------------------------------------------

// Add event listener to the complaint button
document.addEventListener('DOMContentLoaded', function() {
    const complaintButton = document.getElementById('complaint-button');
    if (complaintButton) {
        complaintButton.addEventListener('click', generateComplaintReport);
    }
    console.log("button clicked");
});

async function generateComplaintReport() {
    try {
        const platforms = [
            { boxId: 'box1', name: 'YouTube' },
            { boxId: 'box2', name: 'Instagram' },
            { boxId: 'box3', name: 'Facebook' },
            { boxId: 'box4', name: 'Twitter' }
        ];

        const allPlatformsData = {};

        platforms.forEach(platform => {
            const data = localStorage.getItem(`${platform.boxId}_data`);
            if (data) {
                allPlatformsData[platform.name.toLowerCase()] = JSON.parse(data);
            }
        });

        if (Object.keys(allPlatformsData).length === 0) {
            alert('No platform data found. Please analyze at least one platform first.');
            return;
        }

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
        // window.open(url, '_self');

        // Set the dynamically generated PDF URL in the iframe
        document.getElementById("pdfViewer").src = url;
        document.getElementById("pdfModal").style.display = "block";

        // Clean up object URL after opening
        setTimeout(() => window.URL.revokeObjectURL(url), 1000);

        // const url = URL.createObjectURL(blob);

        // // Get modal elements
        // const pdfViewer = document.getElementById("pdfViewer");
        // const pdfModal = document.getElementById("pdfModal");

        // if (!pdfViewer || !pdfModal) {
        //     console.error("PDF viewer or modal not found in DOM.");
        //     return;
        // }

        // // Set the PDF source in the iframe
        // pdfViewer.src = `${url}#toolbar=0&navpanes=0`;
        
        // // Show the modal
        // pdfModal.style.display = 'flex';

        // // Store the object URL in the modal for cleanup
        // pdfModal.dataset.url = url;
    

    } catch (error) {
        console.error('Error generating report:', error);
        alert('An error occurred while generating the complaint report.');
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

// PROPERLY WORKING
function sendMail() {
    const popup = window.open('/authenticate', 'authPopup', 'width=600,height=600'); // Open in a popup

    let timer = setInterval(() => {
        if (popup.closed) {
            clearInterval(timer);
            alert("✅ Authentication successful! Email sent.");
        }
    }, 1000);
}

// SAMPLE TESTING
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




// function sendMail() {
//     fetch('/authenticate')  // Call the Flask endpoint
//     .then(response => response.json())  // Convert response to JSON
//     .then(data => {
//         alert(data.message);  // Show the popup
//     })
//     .catch(error => {
//         alert("❌ Something went wrong!");  // Handle errors
//         console.error("Error:", error);
//     });
// }

// async function generateComplaintReport() {
//     try {
//         const platforms = [
//             { boxId: 'box1', name: 'YouTube' },
//             { boxId: 'box2', name: 'Instagram' },
//             { boxId: 'box3', name: 'Facebook' },
//             { boxId: 'box4', name: 'Twitter' }
//         ];

//         const allPlatformsData = {};

//         platforms.forEach(platform => {
//             const data = localStorage.getItem(`${platform.boxId}_data`);
//             console.log(data)
//             if (data) {
//                 allPlatformsData[platform.name.toLowerCase()] = JSON.parse(data);
//             }
//             console.log("allplatform data")
//             console.log(allPlatformsData)
//         });

//         if (Object.keys(allPlatformsData).length === 0) {
//             alert('No platform data found. Please analyze at least one platform first.');
//             return;
//         }

//         // Send collected data to Flask backend
//         const response = await fetch('/generate/complaint_report', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify(allPlatformsData)
//         });

    //     if (!response.ok) throw new Error('Failed to generate report');

    //     // Create a download link for the PDF
    //     const blob = await response.blob();
    //     const url = window.URL.createObjectURL(blob);
    //     const a = document.createElement('a');
    //     a.href = url;
    //     a.download = 'Cyberbullying_Complaint_Report.pdf';
    //     document.body.appendChild(a);
    //     a.click();
    //     window.URL.revokeObjectURL(url);
    // } catch (error) {
    //     console.error('Error:', error);
    //     alert('An error occurred while generating the report.');
    // }
//     if (!response.ok) {
//         throw new Error(`HTTP error! status: ${response.status}`);
//     }

//     // View PDF file
//     const blob = await response.blob();
//     const url = window.URL.createObjectURL(blob);
//     window.open(url, '_blank');
//     window.URL.revokeObjectURL(url);


//     } catch (error) {
//         console.error('Error generating report:', error);
//     }
//     console.log("backend passed");
// }


// Function to generate a comprehensive complaint report
// function generateComplaintReport() {
//     try {
//         // Platforms to check
//         const platforms = [
//             { boxId: 'box1', name: 'YouTube' },
//             { boxId: 'box2', name: 'Instagram' },
//             { boxId: 'box3', name: 'Facebook' },
//             { boxId: 'box4', name: 'Twitter' }
//         ];

//         // Collect data from all platforms
//         const allPlatformsData = [];
        
//         platforms.forEach(platform => {
//             const data = localStorage.getItem(`${platform.boxId}_data`);
//             if (data) {
//                 const parsedData = JSON.parse(data);
//                 allPlatformsData.push({
//                     platform: platform.name,
//                     data: parsedData
//                 });
//             }
//         });

//         // If no data found, show an alert
//         if (allPlatformsData.length === 0) {
//             alert('No platform data found. Please analyze at least one platform first.');
//             return;
//         }

//         // Create a new window to display the report
//         const reportWindow = window.open('', '_blank');
//         reportWindow.document.write(`
//             <!DOCTYPE html>
//             <html>
//             <head>
//                 <title>Comprehensive Complaint Report</title>
//                 <style>
//                     body { font-family: Arial, sans-serif; margin: 20px; }
//                     h1 { color: #333; }
//                     .platform { margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
//                     .platform-header { background-color: #f5f5f5; padding: 10px; margin-bottom: 15px; }
//                     .score { font-size: 18px; font-weight: bold; color: #d9534f; }
//                     .comment { margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-radius: 3px; }
//                     .comment-user { font-weight: bold; color: #31708f; }
//                     .print-button { margin: 20px 0; padding: 10px 20px; background-color: #5cb85c; color: white; 
//                                     border: none; border-radius: 4px; cursor: pointer; }
//                 </style>
//             </head>
//             <body>
//                 <h1>Comprehensive Complaint Report</h1>
//                 <button class="print-button" onclick="window.print()">Print Report</button>
//                 <p>Generated on: ${new Date().toLocaleString()}</p>
//                 <p>This report contains analysis from ${allPlatformsData.length} platform(s).</p>
//         `);

//         // Add data for each platform
//         allPlatformsData.forEach(platformData => {
//             const severity = getSeverityLevel(platformData.data.average_score);
            
//             reportWindow.document.write(`
//                 <div class="platform">
//                     <div class="platform-header">
//                         <h2>${platformData.platform}</h2>
//                         <p class="score">Toxicity Score: ${Math.round(platformData.data.average_score * 100)}% (${severity})</p>
//                         <p>Username: ${platformData.data.username || 'Not available'}</p>
//                     </div>
                    
//                     <h3>Flagged Comments (${platformData.data.filtered_comments.length}):</h3>
//             `);
            
//             // Add comments
//             if (platformData.data.filtered_comments.length > 0) {
//                 platformData.data.filtered_comments.forEach(comment => {
//                     reportWindow.document.write(`
//                         <div class="comment">
//                             <p class="comment-user">User: ${comment.user}</p>
//                             <p>Comment: ${comment.text}</p>
//                         </div>
//                     `);
//                 });
//             } else {
//                 reportWindow.document.write(`<p>No flagged comments found.</p>`);
//             }
            
//             reportWindow.document.write(`</div>`);
//         });

//         // Close the HTML
//         reportWindow.document.write(`
//                 <button class="print-button" onclick="window.print()">Print Report</button>
//             </body>
//             </html>
//         `);
        
//         reportWindow.document.close();
        
//     } catch (error) {
//         console.error('Error generating complaint report:', error);
//         alert('An error occurred while generating the complaint report. Please try again.');
//     }
// }

// // Helper function to determine severity level
// function getSeverityLevel(score) {
//     const percentage = Math.round(score * 100);
    
//     if (percentage <= 33) {
//         return "Low";
//     } else if (percentage <= 67) {
//         return "Medium";
//     } else {
//         return "High";
//     }
// }

// //-------------------------------------------------------------------------------------------------


