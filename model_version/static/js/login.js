// Form submission handler
document.getElementById("loginForm").addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent the default form submission behavior

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    // Check if email or password is blank
    if (!email || !password) {
        alert("Please enter both email and password.");
        return;
    }

    try {
        // Send email and password to the backend for authentication
        const response = await fetch('/login', {
            method: "POST",
            body: JSON.stringify({ email, password }),
            headers: { "Content-Type": "application/json" }
        });

        if (response.ok) {
            const result = await response.json();
            alert("Login successful!");
            localStorage.setItem("email", result.email); // Store email in local storage
            window.location.href = "/output"; // Redirect to result page
        } else {
            const errorMessage = await response.text();
            alert("Login failed: INVALID CREDENTIALS");
        }
    } catch (error) {
        alert("An error occurred during login. Please try again.");
        console.error("Error:", error);
    }
});
