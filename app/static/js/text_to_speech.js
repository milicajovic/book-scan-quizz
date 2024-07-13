// text_to_speech.js
const TextToSpeech = (function() {
    let speechSynthesis;
    let speechUtterance;
    let voices = [];
    let speechQueue = [];
    let isSpeaking = false;
    let textBuffer = '';

    function initTextToSpeech() {
        if ('speechSynthesis' in window) {
            speechSynthesis = window.speechSynthesis;
            speechUtterance = new SpeechSynthesisUtterance();

            // Load voices
            voices = speechSynthesis.getVoices();
            speechSynthesis.onvoiceschanged = () => {
                voices = speechSynthesis.getVoices();
                populateVoiceList();

                // Set the saved voice after populating the list
                const savedVoiceURI = localStorage.getItem('selectedVoiceURI');
                if (savedVoiceURI) {
                    document.getElementById('voice-select').value = savedVoiceURI;
                    setVoice(savedVoiceURI);
                }
            };

            // Set up speed slider
            const speedSlider = document.getElementById('tts-speed');
            const speedValue = document.getElementById('tts-speed-value');
            speedSlider.value = localStorage.getItem('ttsSpeed') || 1;
            speedValue.textContent = `${speedSlider.value}x`;

            speedSlider.addEventListener('input', function() {
                speedValue.textContent = `${this.value}x`;
                localStorage.setItem('ttsSpeed', this.value);
                speechUtterance.rate = parseFloat(this.value);
            });

            return true;
        } else {
            console.error("Text-to-speech not supported in this browser.");
            return false;
        }
    }

    function populateVoiceList() {
        const voiceSelect = document.getElementById('voice-select');
        voiceSelect.innerHTML = '';
        voices.forEach((voice) => {
            const option = document.createElement('option');
            option.textContent = `${voice.name} (${voice.lang})`;
            option.value = voice.voiceURI;
            voiceSelect.appendChild(option);
        });
    }

    function speak(text) {
        textBuffer += text;
        processSentenceBuffer();
    }

    function processSentenceBuffer() {
        const sentenceEndRegex = /[.!?]\s*/g;
        let match;
        let lastIndex = 0;

        while ((match = sentenceEndRegex.exec(textBuffer)) !== null) {
            const sentence = textBuffer.slice(lastIndex, match.index + match[0].length).trim();
            if (sentence) {
                enqueueSentence(sentence);
            }
            lastIndex = sentenceEndRegex.lastIndex;
        }

        // Remove processed text from the buffer
        textBuffer = textBuffer.slice(lastIndex);

        // If there's no ongoing speech, start speaking
        if (!isSpeaking) {
            speakNext();
        }
    }

    function enqueueSentence(sentence) {
        speechQueue.push(sentence);
    }

    function speakNext() {
        if (speechQueue.length === 0) {
            isSpeaking = false;
            return;
        }

        isSpeaking = true;
        const sentence = speechQueue.shift();
        speechUtterance.text = sentence;
        speechUtterance.rate = parseFloat(document.getElementById('tts-speed').value);
        speechSynthesis.speak(speechUtterance);

        // Display spoken text
        const textDisplay = document.getElementById('spoken-text-display');
        if (textDisplay) {
            textDisplay.textContent = sentence;
            textDisplay.style.display = 'block';
        }

        speechUtterance.onend = () => {
            speakNext();
        };
    }

    function stopSpeaking() {
        if (speechSynthesis) {
            speechSynthesis.cancel();
        }
        speechQueue = [];
        textBuffer = '';
        isSpeaking = false;
    }

    function setVoice(voiceURI) {
        const voice = voices.find(v => v.voiceURI === voiceURI);
        if (voice) {
            speechUtterance.voice = voice;
            localStorage.setItem('selectedVoiceURI', voiceURI);
        }
    }

    function speakWithoutBuffering(text) {
        if (!speechSynthesis) {
            console.error('Speech synthesis not initialized');
            return;
        }

        // Cancel any ongoing speech
        speechSynthesis.cancel();

        // Clear any existing queue and buffer
        speechQueue = [];
        textBuffer = '';
        isSpeaking = false;

        // Create a new utterance for the entire text
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = parseFloat(document.getElementById('tts-speed').value);

        // Use the selected voice
        const selectedVoiceURI = localStorage.getItem('selectedVoiceURI');
        if (selectedVoiceURI) {
            const voice = voices.find(v => v.voiceURI === selectedVoiceURI);
            if (voice) {
                utterance.voice = voice;
            }
        }

        // Speak the entire text
        speechSynthesis.speak(utterance);

        // Display spoken text
        const textDisplay = document.getElementById('spoken-text-display');
        if (textDisplay) {
            textDisplay.textContent = text;
            textDisplay.style.display = 'block';
        }
    }

    // Function to handle end of stream
    function handleStreamEnd() {
        if (textBuffer.trim()) {
            enqueueSentence(textBuffer.trim());
            textBuffer = '';
            if (!isSpeaking) {
                speakNext();
            }
        }
    }

    // Public API
    return {
        init: initTextToSpeech,
        speak: speak,
        stopSpeaking: stopSpeaking,
        setVoice: setVoice,
        speakWithoutBuffering: speakWithoutBuffering,
        handleStreamEnd: handleStreamEnd
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