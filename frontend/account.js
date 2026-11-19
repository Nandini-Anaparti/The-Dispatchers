const accountForm = document.getElementById("account-form");
const accountStatus = document.getElementById("account-status");
const accountError = document.getElementById("account-error");
const accountLogin = document.getElementById("account-login");
const profileName = document.getElementById("name");
const profileEmail = document.getElementById("email");
const savedAddress = document.getElementById("saved-address");
const addressAction = document.getElementById("address-action");
const addressFields = document.getElementById("address-fields");
const addressInputs = Array.from(addressFields.querySelectorAll("input"));
const saveButton = accountForm.querySelector('button[type="submit"]');
const deactivationSection = document.getElementById("deactivation-section");
const deactivateButton = document.getElementById("deactivate-account");

function showAddressFields() {
    const editing = addressAction.value === "update";
    addressFields.hidden = !editing;
    addressFields.disabled = !editing;
}

addressAction.addEventListener("change", showAddressFields);

async function requestProfile(method, changes, path = "/customers/me") {
    const token = sessionStorage.getItem("access_token");
    if (!token) {
        showSignInRequired();
        return null;
    }

    const headers = { Authorization: "Bearer " + token };
    if (changes) {
        headers["Content-Type"] = "application/json";
    }
    const response = await fetch(path, {
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
        deactivationSection.hidden = true;
        accountError.textContent = "This page is available to customer accounts.";
        return null;
    }
    if (!response.ok) {
        throw new Error("Profile request failed");
    }
    return response.status === 204 ? true : response.json();
}

function showSignInRequired() {
    accountForm.hidden = true;
    deactivationSection.hidden = true;
    accountError.textContent = "Sign in to access your profile.";
    accountLogin.hidden = false;
}

function displayProfile(profile) {
    profileName.value = profile.name;
    profileEmail.value = profile.email;
    savedAddress.value = profile.delivery_address ?? "No address saved";
    for (const input of addressInputs) {
        input.value = profile.delivery_address_details?.[input.id] ?? "";
    }
    addressAction.value = "keep";
    showAddressFields();
    accountForm.hidden = false;
    deactivationSection.hidden = false;
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

    const changes = { name };
    if (addressAction.value === "update") {
        const blank = addressInputs.find(input => !input.value.trim());
        if (blank) {
            accountError.textContent = "Enter all delivery address fields.";
            blank.focus();
            return;
        }
        changes.delivery_address = Object.fromEntries(
            addressInputs.map(input => [input.id, input.value.trim()])
        );
    } else if (addressAction.value === "clear") {
        changes.delivery_address = null;
    }

    saveButton.disabled = true;
    deactivateButton.disabled = true;
    profileName.readOnly = true;
    addressAction.disabled = true;
    addressFields.disabled = true;
    accountStatus.textContent = "Saving changes…";
    try {
        const profile = await requestProfile("PUT", changes);
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
        deactivateButton.disabled = false;
        profileName.readOnly = false;
        addressAction.disabled = false;
        showAddressFields();
    }
});

deactivateButton.addEventListener("click", async () => {
    if (!window.confirm("Deactivate your account and sign out?")) {
        return;
    }

    deactivateButton.disabled = true;
    saveButton.disabled = true;
    accountError.textContent = "";
    accountStatus.textContent = "Deactivating account…";
    try {
        if (await requestProfile("POST", undefined, "/customers/me/deactivate")) {
            sessionStorage.removeItem("access_token");
            accountForm.hidden = true;
            deactivationSection.hidden = true;
            accountStatus.textContent = "Your account has been deactivated.";
            await showNavbar();
        } else {
            accountStatus.textContent = "";
        }
    } catch {
        accountStatus.textContent = "";
        accountError.textContent = "Could not deactivate your account. Please try again.";
    } finally {
        deactivateButton.disabled = false;
        saveButton.disabled = false;
    }
});

loadProfile();
