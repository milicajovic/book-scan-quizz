// text_to_speech.js
const TextToSpeech = (function() {
    let speechSynthesis;
    let speechUtterance;
    let voices = [];
    let currentVoice = null;

    function initTextToSpeech() {
        if ('speechSynthesis' in window) {
            speechSynthesis = window.speechSynthesis;
            speechUtterance = new SpeechSynthesisUtterance();

            // Load voices
            loadVoices();
            speechSynthesis.onvoiceschanged = loadVoices;

            // Set up speed slider
            setupSpeedSlider();

            return true;
        } else {
            console.error("Text-to-speech not supported in this browser.");
            return false;
        }
    }

    function loadVoices() {
        voices = speechSynthesis.getVoices();
        populateVoiceList();
        setDefaultVoice();
    }

    function populateVoiceList() {
        const voiceSelect = document.getElementById('voice-select');
        if (voiceSelect) {
            voiceSelect.innerHTML = '';
            voices.forEach((voice) => {
                const option = document.createElement('option');
                option.textContent = `${voice.name} (${voice.lang})`;
                option.value = voice.voiceURI;
                voiceSelect.appendChild(option);
            });
        }
    }

    function setDefaultVoice() {
        const savedVoiceURI = localStorage.getItem('selectedVoiceURI');
        if (savedVoiceURI) {
            setVoice(savedVoiceURI);
        } else {
            // Set a default voice (e.g., first available voice)
            setVoice(voices[0]?.voiceURI);
        }
    }

    function setupSpeedSlider() {
        const speedSlider = document.getElementById('tts-speed');
        const speedValue = document.getElementById('tts-speed-value');
        if (speedSlider && speedValue) {
            speedSlider.value = localStorage.getItem('ttsSpeed') || 1;
            speedValue.textContent = `${speedSlider.value}x`;

            speedSlider.addEventListener('input', function() {
                speedValue.textContent = `${this.value}x`;
                localStorage.setItem('ttsSpeed', this.value);
                speechUtterance.rate = parseFloat(this.value);
            });
        }
    }

    function speak(text) {
        if (!speechSynthesis || !currentVoice) {
            console.error('Speech synthesis not initialized or no voice selected');
            return;
        }

        speechSynthesis.cancel(); // Stop any ongoing speech
        speechUtterance.text = text;
        speechUtterance.voice = currentVoice;
        speechUtterance.rate = parseFloat(document.getElementById('tts-speed')?.value || 1);
        speechSynthesis.speak(speechUtterance);

        // Display spoken text
        updateSpokenTextDisplay(text);
    }

     // New method to speak without buffering
    function speakWithoutBuffering(text) {
        if (!speechSynthesis || !currentVoice) {
            console.error('Speech synthesis not initialized or no voice selected');
            return;
        }

        speechSynthesis.cancel(); // Stop any ongoing speech
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = currentVoice;
        utterance.rate = parseFloat(document.getElementById('tts-speed')?.value || 1);
        speechSynthesis.speak(utterance);

        // Display spoken text
        updateSpokenTextDisplay(text);
    }

    function stopSpeaking() {
        if (speechSynthesis) {
            speechSynthesis.cancel();
        }
    }

    function setVoice(voiceURI) {
        const voice = voices.find(v => v.voiceURI === voiceURI);
        if (voice) {
            currentVoice = voice;
            speechUtterance.voice = voice;
            localStorage.setItem('selectedVoiceURI', voiceURI);
        }
    }

    function updateSpokenTextDisplay(text) {
        const textDisplay = document.getElementById('spoken-text-display');
        if (textDisplay) {
            textDisplay.textContent = text;
            textDisplay.style.display = 'block';
        }
    }

    // Public API
    return {
        init: initTextToSpeech,
        speak: speak,
        speakWithoutBuffering: speakWithoutBuffering,
        stopSpeaking: stopSpeaking,
        setVoice: setVoice
    };
})();

// Initialize TTS when the page loads
document.addEventListener('DOMContentLoaded', () => {
    if (TextToSpeech.init()) {
        const voiceSelect = document.getElementById('voice-select');
        if (voiceSelect) {
            voiceSelect.addEventListener('change', (event) => {
                TextToSpeech.setVoice(event.target.value);
            });
        }

        // Set up auto-read checkbox
        const autoReadCheckbox = document.getElementById('autoReadResults');
        if (autoReadCheckbox) {
            autoReadCheckbox.checked = localStorage.getItem('autoReadResults') === 'true';
            autoReadCheckbox.addEventListener('change', (event) => {
                localStorage.setItem('autoReadResults', event.target.checked);
            });
        }
    } else {
        // Hide TTS controls if not supported
        const ttsControls = document.getElementById('tts-controls');
        if (ttsControls) {
            ttsControls.style.display = 'none';
        }
    }
});