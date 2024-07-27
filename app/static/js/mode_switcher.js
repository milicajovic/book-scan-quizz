// mode_switcher.js

// Global variable to store the current mode
let currentMode = 'audio';

// Function to initialize the mode switcher
function initModeSwitcher() {
    const modeToggle = document.getElementById('mode-toggle');
    if (modeToggle) {
        modeToggle.addEventListener('change', toggleMode);
    }

    // Get the initial mode from local storage or default to 'audio'
    currentMode = localStorage.getItem('answerMode') || 'audio';
    updateUI(currentMode);
}

// Function to toggle between audio and text modes
function toggleMode() {
    currentMode = currentMode === 'audio' ? 'text' : 'audio';

    // Update local storage
    localStorage.setItem('answerMode', currentMode);

    // Update server preference
    updateServerPreference(currentMode);

    // Redirect to the same URL to reload with the new mode
    window.location.reload();
}
// Function to update UI elements based on the current mode
function updateUI(mode) {
    const audioElements = document.querySelectorAll('.audio-mode');
    const textElements = document.querySelectorAll('.text-mode');
    const modeToggle = document.getElementById('mode-toggle');

    if (mode === 'audio') {
        audioElements.forEach(el => el.style.display = 'block');
        textElements.forEach(el => el.style.display = 'none');
        if (modeToggle) modeToggle.checked = false;
    } else {
        audioElements.forEach(el => el.style.display = 'none');
        textElements.forEach(el => el.style.display = 'block');
        if (modeToggle) modeToggle.checked = true;
    }
}

// Function to send AJAX request to update mode preference on the server
function updateServerPreference(mode) {
    fetch('/quiz-session/update-mode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mode: mode }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Mode updated on server:', data);
    })
    .catch((error) => {
        console.error('Error updating mode on server:', error);
    });
}

// Initialize the mode switcher when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initModeSwitcher);

// Expose the toggleMode function globally so it can be called from HTML
window.toggleMode = toggleMode;