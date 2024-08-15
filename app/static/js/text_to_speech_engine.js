// text_to_speech.js
import LanguageUtils from "./language_utils.js";
import LanguagePreferenceSender from "./language_preference_sender.js";

class TextToSpeechEngine {
    constructor() {
        //this.sessionId = sessionId;
        this.speechSynthesis = window.speechSynthesis;
        this.speechUtterance = new SpeechSynthesisUtterance();
        this.voices = [];
        this.currentVoice = null;
        this.isInitialized = false;
        this.isSpeaking = false;
        this.textBuffer = '';
        this.speechQueue = [];
        this.loggingEnabled = false;
    }

    static getInstance() {

        if (!TextToSpeechEngine.instance) {
            TextToSpeechEngine.instance = new TextToSpeechEngine();
            TextToSpeechEngine.instance.log("getInstance")
        } else {
            TextToSpeechEngine.instance.log("getInstance - cached")
        }
        return TextToSpeechEngine.instance;
    }

    log(message) {
        if (this.loggingEnabled) {
            console.log(message);
        }
    }

    init() {
        return new Promise((resolve, reject) => {
            if (this.isInitialized) {
                console.log("TextToSpeech already initialized.");
                resolve(true);
                return;
            }
            if ('speechSynthesis' in window) {
                this.speechSynthesis = window.speechSynthesis;
                this.speechUtterance = new SpeechSynthesisUtterance();

                this.loadVoices()
                    .then(() => {
                        this.setupSpeedSlider();
                        this.setupVoiceSelection();
                        this.isInitialized = true;
                        resolve(true);
                    })
                    .catch((error) => {
                        reject(error);
                    });
            } else {
                reject(new Error("Text-to-speech not supported"));
            }
        });
    }

    createFilterInput() {
        const voiceSelect = document.getElementById('voice-select');
        if (voiceSelect) {
            const filterInput = document.createElement('input');
            filterInput.type = 'text';
            filterInput.id = 'voice-filter';
            filterInput.className = 'form-control mb-2';
            filterInput.placeholder = 'Filter voices...';

            // Insert the filter input before the voice select dropdown
            voiceSelect.parentNode.insertBefore(filterInput, voiceSelect);

            // Set initial filter value based on user's language
            const userLanguage = navigator.language || navigator.userLanguage;
            let initialFilter = this.getVoiceFromStorage();
            if (!initialFilter) {
                initialFilter = userLanguage.split('-')[0]; // Get the language code (e.g., 'de' from 'de-DE')
                // Add 'google' for Chrome users
                if (navigator.userAgent.includes('Chrome')) {
                    initialFilter += ' google';
                }
            }
            filterInput.value = initialFilter;

            return filterInput;
        }
        return null;
    }

    getVoiceFromStorage() {
        return localStorage.getItem('selectedVoiceURI');
    }

    setupVoiceSelection() {
        const voiceSelect = document.getElementById('voice-select');
        if (voiceSelect) {
            const filterInput = this.createFilterInput();

            if (filterInput) {
                filterInput.addEventListener('input', () => {
                    this.populateVoiceList(filterInput.value);
                });
            }
            const savedVoiceURI = this.getVoiceFromStorage();
            if (savedVoiceURI) {
                voiceSelect.value = savedVoiceURI;
                this.setVoice(savedVoiceURI);
            }
            voiceSelect.addEventListener('change', (event) => {
                const selectedVoiceURI = event.target.value;
                this.setVoice(selectedVoiceURI);
                this.updateLanguage(selectedVoiceURI);
                this.triggerReadQuestion();
            });

            // Initial population of the voice list
            this.populateVoiceList(filterInput ? filterInput.value : '');
        }
    }

    getLanguageCodeFromVoice(voice) {
        return voice.lang.split('-')[0];
    }


    loadVoices() {
        return new Promise((resolve) => {
            this.voices = this.speechSynthesis.getVoices();
            if (this.voices.length > 0) {
                this.populateVoiceList();
                this.setDefaultVoice();
                resolve();
            } else {
                this.speechSynthesis.onvoiceschanged = () => {
                    this.voices = this.speechSynthesis.getVoices();
                    this.populateVoiceList();
                    this.setDefaultVoice();
                    resolve();
                };
            }
        });
    }

    populateVoiceList(filter = '') {
        const voiceSelect = document.getElementById('voice-select');
        if (voiceSelect) {
            voiceSelect.innerHTML = '';
            const filteredVoices = this.filterVoices(filter);
            this.addVoicesToSelect(voiceSelect, filteredVoices);
            this.selectAppropriateVoice(voiceSelect);
        }
    }

    filterVoices(filter) {
        const filterTerms = filter.toLowerCase().split(' ');
        return this.voices.filter(voice => {
            const voiceInfo = `${voice.name} (${voice.lang})`.toLowerCase();
            return filterTerms.every(term => voiceInfo.includes(term));
        });
    }

    addVoicesToSelect(voiceSelect, voices) {
        voices.forEach(voice => {
            const option = document.createElement('option');
            option.textContent = `${voice.name} (${voice.lang})`;
            option.value = voice.voiceURI;
            voiceSelect.appendChild(option);
        });
    }

    selectAppropriateVoice(voiceSelect) {
        const savedVoiceURI = localStorage.getItem('selectedVoiceURI');
        if (savedVoiceURI) {
            const savedOption = voiceSelect.querySelector(`option[value="${savedVoiceURI}"]`);
            if (savedOption) {
                savedOption.selected = true;
            } else {
                this.selectFirstAvailableVoice(voiceSelect);
            }
        } else {
            this.selectFirstAvailableVoice(voiceSelect);
        }
    }

    selectFirstAvailableVoice(voiceSelect) {
        if (voiceSelect.options.length > 0) {
            voiceSelect.options[0].selected = true;
            this.setVoice(voiceSelect.options[0].value);
        }
    }

    setDefaultVoice() {
        const savedVoiceURI = localStorage.getItem('selectedVoiceURI');
        this.log("setDefaultVoice:" + savedVoiceURI)
        if (savedVoiceURI) {
            this.setVoice(savedVoiceURI);
        } else {
            this.setVoice(this.voices[0]?.voiceURI);
        }
    }

    setupSpeedSlider() {
        const speedSlider = document.getElementById('tts-speed');
        const speedValue = document.getElementById('tts-speed-value');
        if (speedSlider && speedValue) {
            speedSlider.value = localStorage.getItem('ttsSpeed') || 1;
            speedValue.textContent = `${speedSlider.value}x`;

            speedSlider.addEventListener('input', () => {
                speedValue.textContent = `${speedSlider.value}x`;
                localStorage.setItem('ttsSpeed', speedSlider.value);
                this.speechUtterance.rate = parseFloat(speedSlider.value);
            });
        }
    }

    addToSpeechQueue(text) {
        this.textBuffer += text;
        this.processSentences();
    }

    processSentences() {
        let sentenceEnd = this.textBuffer.search(/[.!?]\s/);
        while (sentenceEnd !== -1) {
            const sentence = this.textBuffer.slice(0, sentenceEnd + 1);
            this.speechQueue.push(sentence.trim());
            this.textBuffer = this.textBuffer.slice(sentenceEnd + 1);
            sentenceEnd = this.textBuffer.search(/[.!?]\s/);
        }
        if (!this.isSpeaking) {
            this.speakNext();
        }
    }

    speakNext() {
        if (this.speechQueue.length === 0) {
            this.isSpeaking = false;
            return;
        }

        this.isSpeaking = true;
        const textToSpeak = this.speechQueue.shift();

        this.speechUtterance = new SpeechSynthesisUtterance(textToSpeak);
        this.speechUtterance.voice = this.currentVoice;
        this.speechUtterance.rate = parseFloat(document.getElementById('tts-speed')?.value || 1);

        this.speechUtterance.onend = () => {
            this.speakNext();
        };

        this.speechUtterance.onerror = (event) => {
            console.error('Speech synthesis error:', event.error);
            this.speakNext();
        };

        this.speechSynthesis.speak(this.speechUtterance);
    }

    finishSpeaking() {
        if (this.textBuffer.trim().length > 0) {
            this.speechQueue.push(this.textBuffer.trim());
            this.textBuffer = '';
        }
        if (!this.isSpeaking) {
            this.speakNext();
        }
    }

    speakWithoutBuffering(text) {
        if (!this.isInitialized || !this.currentVoice) {
            console.error('Speech synthesis not initialized or no voice selected');
            return;
        }

        this.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = this.currentVoice;
        utterance.rate = parseFloat(document.getElementById('tts-speed')?.value || 1);
        this.speechSynthesis.speak(utterance);

        this.updateSpokenTextDisplay(text);
    }

    stopSpeaking() {
        if (this.speechSynthesis) {
            this.speechSynthesis.cancel();
        }
    }

    setVoice(voiceURI) {
        this.log("setVoice:" + voiceURI)

        const voice = this.voices.find(v => v.voiceURI === voiceURI);
        if (voice) {
            this.currentVoice = voice;
            this.speechUtterance.voice = voice;
            localStorage.setItem('selectedVoiceURI', voiceURI);
            const languageCode = this.getLanguageCodeFromVoice(voice);
            LanguagePreferenceSender.sendLanguagePreference(languageCode);
        }

    }


    updateSpokenTextDisplay(text) {
        const textDisplay = document.getElementById('spoken-text-display');
        if (textDisplay) {
            textDisplay.textContent = text;
            textDisplay.style.display = 'block';
        }
    }

    updateLanguage(voiceURI) {
        const selectedVoice = this.voices.find(v => v.voiceURI === voiceURI);
        if (selectedVoice) {
            const languageCode = selectedVoice.lang.split('-')[0];
            LanguageUtils.setSelectedLanguage(languageCode);
        }
    }

    triggerReadQuestion() {
        console.log('triggerReadQuestion called'); // Added logging
        const questionText = document.getElementById('question-text')?.textContent;
        this.speakWithoutBuffering(questionText);
    }
}

export default TextToSpeechEngine;
