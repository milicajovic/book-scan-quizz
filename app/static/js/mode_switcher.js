// mode_switcher.js

class ModeSwitcher {
    constructor() {
        this.currentMode = localStorage.getItem('answerMode') || 'audio';
        this.modeToggle = document.getElementById('mode-toggle');
        this.audioElements = document.querySelectorAll('.audio-mode');
        this.textElements = document.querySelectorAll('.text-mode');

        this.init();
    }

    init() {
        if (this.modeToggle) {
            this.modeToggle.addEventListener('change', this.toggleMode.bind(this));
        }
        this.updateUI();
    }

    toggleMode() {
        this.currentMode = this.currentMode === 'audio' ? 'text' : 'audio';
        localStorage.setItem('answerMode', this.currentMode);
        this.updateServerPreference();
        window.location.reload();
    }

    updateUI() {
        const displayMode = this.currentMode === 'audio' ? 'block' : 'none';
        const hideMode = this.currentMode === 'audio' ? 'none' : 'block';

        this.audioElements.forEach(el => el.style.display = displayMode);
        this.textElements.forEach(el => el.style.display = hideMode);

        if (this.modeToggle) {
            this.modeToggle.checked = this.currentMode === 'text';
        }
    }

    updateServerPreference() {
        fetch('/quiz-session/update-mode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mode: this.currentMode }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Mode updated on server:', data);
        })
        .catch(error => {
            console.error('Error updating mode on server:', error);
        });
    }
}

export default new ModeSwitcher();
