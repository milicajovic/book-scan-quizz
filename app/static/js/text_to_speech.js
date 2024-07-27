// text_to_speech.js
import LanguageUtils from "./language_utils.js";

const TextToSpeech = (function () {
    let speechSynthesis;
    let speechUtterance;
    let voices = [];
    let currentVoice = null;
    let isInitialized = false;
    let isSpeaking = false;
    let textBuffer = '';
    let speechQueue = [];

    function initTextToSpeech() {
        console.log('initTextToSpeech called');
        return new Promise((resolve, reject) => {
            if ('speechSynthesis' in window) {
                speechSynthesis = window.speechSynthesis;
                speechUtterance = new SpeechSynthesisUtterance();

                // Load voices
                loadVoices()
                    .then(() => {
                        // Set up speed slider
                        setupSpeedSlider();

                        // Set up voice selection
                        setupVoiceSelection();

                        isInitialized = true;
                        console.log("Text-to-speech initialized successfully");
                        resolve(true);
                    })
                    .catch((error) => {
                        console.error("Error initializing text-to-speech:", error);
                        reject(error);
                    });
            } else {
                console.error("Text-to-speech not supported in this browser.");
                reject(new Error("Text-to-speech not supported"));
            }
        });
    }

    function setupVoiceSelection() {
        const voiceSelect = document.getElementById('voice-select');
        if (voiceSelect) {
            const savedVoiceURI = localStorage.getItem('selectedVoiceURI');
            console.log('Saved voice URI:', savedVoiceURI);
            if (savedVoiceURI) {
                voiceSelect.value = savedVoiceURI;
                setVoice(savedVoiceURI);
            }
            voiceSelect.addEventListener('change', (event) => {
                const selectedVoiceURI = event.target.value;
                setVoice(selectedVoiceURI);
                saveSelectedVoice(selectedVoiceURI);
                console.log('Voice changed to:', selectedVoiceURI);

                // Store the language code of the selected voice
                const selectedVoice = voices.find(v => v.voiceURI === selectedVoiceURI);
                if (selectedVoice) {
                    const languageCode = selectedVoice.lang.split('-')[0]; // Get the primary language code
                    LanguageUtils.setSelectedLanguage(languageCode);
                    console.log('Language code stored:', languageCode);
                }

                // Trigger re-reading of the question
                if (typeof QuizSessionTTS !== 'undefined' && typeof QuizSessionTTS.readCurrentQuestion === 'function') {
                    QuizSessionTTS.readCurrentQuestion();
                }
            });
        } else {
            console.error('Voice select element not found');
        }
    }

    function saveSelectedVoice(voiceURI) {
        localStorage.setItem('selectedVoiceURI', voiceURI);
    }

    function loadVoices() {
        return new Promise((resolve) => {
            voices = speechSynthesis.getVoices();
            if (voices.length > 0) {
                populateVoiceList();
                setDefaultVoice();
                resolve();
            } else {
                speechSynthesis.onvoiceschanged = () => {
                    voices = speechSynthesis.getVoices();
                    populateVoiceList();
                    setDefaultVoice();
                    resolve();
                };
            }
        });
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

            // Set the selected voice from localStorage
            const savedVoiceURI = localStorage.getItem('selectedVoiceURI');
            if (savedVoiceURI) {
                voiceSelect.value = savedVoiceURI;
            }
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

            speedSlider.addEventListener('input', function () {
                speedValue.textContent = `${this.value}x`;
                localStorage.setItem('ttsSpeed', this.value);
                speechUtterance.rate = parseFloat(this.value);
            });
        }
    }


    function addToSpeechQueue(text) {
        textBuffer += text;
        processSentences();
    }

    function processSentences() {
        let sentenceEnd = textBuffer.search(/[.!?]\s/);
        while (sentenceEnd !== -1) {
            const sentence = textBuffer.slice(0, sentenceEnd + 1);
            speechQueue.push(sentence.trim());
            textBuffer = textBuffer.slice(sentenceEnd + 1);
            sentenceEnd = textBuffer.search(/[.!?]\s/);
        }
        if (!isSpeaking) {
            speakNext();
        }
    }

    function speakNext() {
        if (speechQueue.length === 0) {
            isSpeaking = false;
            return;
        }

        isSpeaking = true;
        const textToSpeak = speechQueue.shift();
        console.log('Speaking:', textToSpeak);

        speechUtterance = new SpeechSynthesisUtterance(textToSpeak);
        speechUtterance.voice = currentVoice;
        speechUtterance.rate = parseFloat(document.getElementById('tts-speed')?.value || 1);

        speechUtterance.onend = () => {
            console.log('Finished speaking:', textToSpeak);
            speakNext();
        };

        speechUtterance.onerror = (event) => {
            console.error('Speech synthesis error:', event.error);
            speakNext();
        };

        speechSynthesis.speak(speechUtterance);
    }

    function finishSpeaking() {
        if (textBuffer.trim().length > 0) {
            speechQueue.push(textBuffer.trim());
            textBuffer = '';
        }
        if (!isSpeaking) {
            speakNext();
        }
    }


    function speakWithoutBuffering(text) {
        if (!isInitialized || !currentVoice) {
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
        addToSpeechQueue: addToSpeechQueue,
        finishSpeaking: finishSpeaking,
        speakWithoutBuffering: speakWithoutBuffering,
        stopSpeaking: stopSpeaking,
        setVoice: setVoice,
        isInitialized: () => isInitialized,
    };
})();

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event fired in text_to_speech.js');
    TextToSpeech.init()
        .then(() => {
            console.log('TextToSpeech initialized successfully');
        })
        .catch((error) => {
            console.error("Failed to initialize Text-to-Speech:", error);
            // Hide TTS controls if not supported or initialization failed
            const ttsControls = document.getElementById('tts-controls');
            if (ttsControls) {
                ttsControls.style.display = 'none';
            }
        });
});

export default TextToSpeech;