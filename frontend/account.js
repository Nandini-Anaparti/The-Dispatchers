const accountForm = document.getElementById("account-form");
const accountStatus = document.getElementById("account-status");
const accountError = document.getElementById("account-error");
const accountLogin = document.getElementById("account-login");
const profileName = document.getElementById("name");
const profileEmail = document.getElementById("email");
const profileAddress = document.getElementById("address");
const saveButton = accountForm.querySelector('button[type="submit"]');

async function requestProfile(method, changes) {
    const token = sessionStorage.getItem("access_token");
    if (!token) {
        showSignInRequired();
        return null;
    }

    const headers = { Authorization: "Bearer " + token };
    if (changes) {
        headers["Content-Type"] = "application/json";
    }
    const response = await fetch("/customers/me", {
        method,
        headers,
        body: changes ? JSON.stringify(changes) : undefined
    });

    if (response.status === 401) {
        sessionStorage.removeItem("access_token");
        showSignInRequired();
        return null;
    }
    if (response.status === 403) {
        accountForm.hidden = true;
        accountError.textContent = "This page is available to customer accounts.";
        return null;
    }
    if (!response.ok) {
        throw new Error("Profile request failed");
    }
    return response.json();
}

function showSignInRequired() {
    accountForm.hidden = true;
    accountError.textContent = "Sign in to access your profile.";
    accountLogin.hidden = false;
}

function displayProfile(profile) {
    profileName.value = profile.name;
    profileEmail.value = profile.email;
    profileAddress.value = profile.delivery_address ?? "";
    accountForm.hidden = false;
}

async function loadProfile() {
    try {
        const profile = await requestProfile("GET");
        if (profile) {
            displayProfile(profile);
        }
    } catch {
        accountError.textContent = "Could not load your profile. Refresh to try again.";
    } finally {
        accountStatus.textContent = "";
    }
}

accountForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    accountStatus.textContent = "";
    accountError.textContent = "";

    const name = profileName.value.trim();
    if (!name) {
        accountError.textContent = "Enter your name.";
        profileName.focus();
        return;
    }

    saveButton.disabled = true;
    profileName.readOnly = true;
    profileAddress.readOnly = true;
    accountStatus.textContent = "Saving changes…";
    try {
        const profile = await requestProfile("PUT", {
            name,
            delivery_address: profileAddress.value.trim() || null
        });
        accountStatus.textContent = "";
        if (profile) {
            displayProfile(profile);
            accountStatus.textContent = "Profile saved.";
        }
    } catch {
        accountStatus.textContent = "";
        accountError.textContent = "Could not save your profile. Please try again.";
    } finally {
        saveButton.disabled = false;
        profileName.readOnly = false;
        profileAddress.readOnly = false;
    }
});

loadProfile();
