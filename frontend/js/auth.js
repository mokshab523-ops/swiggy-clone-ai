// Authentication Functions
function handleLogin(email, password) {
    return fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            setToken(data.token);
            setUser(data.user);
            return data;
        } else {
            throw new Error(data.error || 'Login failed');
        }
    });
}

function handleSignup(userData) {
    return fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            setToken(data.token);
            return data;
        } else {
            throw new Error(data.error || 'Signup failed');
        }
    });
}

function handleLogout() {
    clearToken();
    clearUser();
    // Clear cart and preferences
    localStorage.removeItem('cart');
    localStorage.removeItem('selectedRestaurant');
    window.location.href = 'index.html';
}

function verifyToken(token) {
    return fetch(`${API_BASE_URL}/auth/verify-token`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token })
    })
    .then(res => res.json());
}

function getProfile() {
    return fetch(`${API_BASE_URL}/auth/profile`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    })
    .then(res => res.json());
}

function updateProfile(profileData) {
    return fetch(`${API_BASE_URL}/auth/update-profile`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify(profileData)
    })
    .then(res => res.json());
}

function changePassword(oldPassword, newPassword) {
    return fetch(`${API_BASE_URL}/auth/change-password`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
            old_password: oldPassword,
            new_password: newPassword
        })
    })
    .then(res => res.json());
}

function addAddress(address) {
    return fetch(`${API_BASE_URL}/auth/add-address`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify(address)
    })
    .then(res => res.json());
}

// Event Listeners for Login/Logout
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm('Are you sure you want to logout?')) {
                handleLogout();
            }
        });
    }

    // Auto-login if token exists
    if (isAuthenticated()) {
        verifyToken(getToken()).then(data => {
            if (!data.valid) {
                clearToken();
                clearUser();
                window.location.href = 'login.html';
            } else {
                setUser(data.user);
                updateNavbar();
            }
        }).catch(err => {
            console.error('Token verification failed:', err);
            clearToken();
            clearUser();
        });
    }
});

function updateNavbar() {
    if (isAuthenticated()) {
        const user = getUser();
        const loginBtn = document.getElementById('login-btn');
        const userName = document.getElementById('user-name');
        const adminName = document.getElementById('admin-name');

        if (loginBtn) {
            loginBtn.textContent = 'Dashboard';
            loginBtn.onclick = () => window.location.href = 'dashboard.html';
        }

        if (userName) {
            userName.textContent = user.first_name + ' ' + user.last_name;
        }

        if (adminName) {
            adminName.textContent = user.first_name + ' ' + user.last_name;
        }
    }
}