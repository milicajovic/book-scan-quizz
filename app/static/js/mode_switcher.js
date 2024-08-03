// mode_switcher.js

class ModeSwitcher {
    constructor() {
        this.modeToggle = document.getElementById('mode-toggle');
        this.modeLabel = this.modeToggle.nextElementSibling;
        this.init();
    }

    init() {
        if (this.modeToggle) {
            this.modeToggle.addEventListener('change', this.toggleMode.bind(this));
        }
    }

    toggleMode() {
        const newMode = this.modeToggle.checked ? 'text' : 'audio';
        this.updateLabel(newMode);
        window.location.href = `${window.location.pathname}?set_mode=${newMode}`;
    }

    updateLabel(mode) {
        this.modeLabel.textContent = mode === 'text' ? 'Switch to Audio Mode' : 'Switch to Text Mode';
    }
}

export default new ModeSwitcher();