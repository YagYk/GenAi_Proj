document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const registerLink = document.getElementById('register-link');
    let isRegistering = false;

    registerLink.addEventListener('click', (e) => {
        e.preventDefault();
        isRegistering = !isRegistering;
        loginForm.querySelector('button').textContent = isRegistering ? 'Register' : 'Login';
        registerLink.textContent = isRegistering ? 'Back to Login' : 'Register';
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        const response = await fetch(isRegistering ? '/register' : '/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
        });

        const result = await response.json();

        if (result.success) {
            window.location.href = '/home';
        } else {
            alert(result.message || 'An error occurred');
        }
    });
});
