const form = document.getElementById("login-form");
const errorMessage = document.getElementById("login-error");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    errorMessage.textContent = "";

    const loginData = {
        email: document.getElementById("email").value.trim(),
        password: document.getElementById("password").value
    };

    try {
        const response = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(loginData)
        });

        if (response.status === 401) {
            errorMessage.textContent = "Incorrect email or password.";
            return;
        }

        if (!response.ok) {
            errorMessage.textContent = "Login failed. Please try again.";
            return;
        }

        const data = await response.json();

        sessionStorage.setItem("access_token", data.access_token);

        window.location.href = "/";

    } catch (error) {
        errorMessage.textContent = "Could not log in. Please try again.";
        console.error(error);
    }
});