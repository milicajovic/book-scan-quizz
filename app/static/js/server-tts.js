export class ServerTTS {
    constructor() {
        this.elements = {
            form: document.getElementById('ttsForm'),
            spinner: document.getElementById('spinner'),
            audioPlayer: document.getElementById('audioPlayer'),
            errorMessage: document.getElementById('errorMessage')
        };

        this.checkElements();
        this.initEventListeners();
    }

    checkElements() {
        for (const [key, element] of Object.entries(this.elements)) {
            if (!element) {
                console.error(`ServerTTS: Element '${key}' not found in the DOM`);
            }
        }
    }

    initEventListeners() {
        if (this.elements.form) {
            this.elements.form.addEventListener('submit', this.handleSubmit.bind(this));
        } else {
            console.error("ServerTTS: Cannot add event listener to form because it's not found");
        }
    }

    handleSubmit(e) {
        e.preventDefault();

        this.elements.spinner.classList.remove('d-none');
        this.elements.audioPlayer.classList.add('d-none');
        this.elements.errorMessage.classList.add('d-none');

        fetch('/tts-demo', {
            method: 'POST',
            body: new FormData(this.elements.form)
        })
        .then(response => response.json())
        .then(data => this.handleResponse(data))
        .catch(error => this.handleError(error));
    }

    handleResponse(data) {
        this.elements.spinner.classList.add('d-none');
        if (data.error) {
            this.showError(data.error);
        } else {
            this.playAudio(data.audio_file);
        }
    }

    handleError(error) {
        this.elements.spinner.classList.add('d-none');
        this.showError('Network error: ' + error.message);
    }

    showError(message) {
        if (this.elements.errorMessage) {
            this.elements.errorMessage.textContent = message;
            this.elements.errorMessage.classList.remove('d-none');
        } else {
            console.error('ServerTTS: Cannot show error because errorMessage element is not found');
        }
    }

    playAudio(audioFile) {
        if (this.elements.audioPlayer) {
            this.elements.audioPlayer.src = '/play-audio?file=' + encodeURIComponent(audioFile);
            this.elements.audioPlayer.classList.remove('d-none');
            this.elements.audioPlayer.play();
        } else {
            console.error('ServerTTS: Cannot play audio because audioPlayer element is not found');
        }
    }
}