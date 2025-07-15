function getCSRFToken() {
    const cookieString = document.cookie;
    const cookies = cookieString.split(';');
    for (const cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {  // Flask-WTF default CSRF cookie name
            return value;
        }
    }
    return null;
}