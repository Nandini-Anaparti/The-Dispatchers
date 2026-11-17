const form = document.getElementById("owner-register-form");
const successMessage = document.getElementById("owner-registration-success");
const errorMessage = document.getElementById("owner-registration-error");
const nextStep = document.getElementById("owner-next-step");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    successMessage.textContent = "";
    errorMessage.textContent = "";
    nextStep.hidden = true;

    const owner = {
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        password: document.getElementById("password").value
    };

    try {
        const response = await fetch("/restaurant-owners", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(owner)
        });

        if (response.status === 409) {
            errorMessage.textContent = "Email already registered.";
            return;
        }

        if (response.status === 422) {
            errorMessage.textContent =
                "Please check your information and try again.";
            return;
        }

        if (!response.ok) {
            errorMessage.textContent =
                "Registration failed. Please try again.";
            return;
        }

        successMessage.textContent =
            "Account created successfully!";

        nextStep.hidden = false;
        form.reset();

    } catch (error) {
        errorMessage.textContent =
            "Could not register. Please try again.";
        console.error(error);
    }
});