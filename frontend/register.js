const form = document.getElementById("register-form");
const successMessage = document.getElementById("registration-success");
const errorMessage = document.getElementById("registration-error");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    successMessage.textContent = "";
    errorMessage.textContent = "";

    const customer = {
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        password: document.getElementById("password").value,
        delivery_address: document.getElementById("address").value.trim() || null
    };

    try {
        const response = await fetch("/customers", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(customer)
        });

        if (response.status === 409) {
            errorMessage.textContent = "Email already registered.";
            return;
        }

        if (response.status === 422) {
            errorMessage.textContent = "Please check your information and try again.";
            return;
        }

        if (!response.ok) {
            errorMessage.textContent = "Registration failed. Please try again.";
            return;
        }

        successMessage.textContent =
            "Account created successfully. You can sign in once login is available.";

        form.reset();

    } catch (error) {
        errorMessage.textContent =
            "Could not register. Please try again.";
        console.error(error);
    }
});