import QuizSessionTTS from './quiz_session_tts.js';
import TextToSpeechEngine from "./text_to_speech_engine.js";

class QuizSession {
    constructor() {
        this.loggingEnabled = true; // Set this to false to disable logging
        this.retryButton = document.getElementById('retryButton');
        this.nextQuestionButton = document.getElementById('nextQuestionButton');
        this.resultText = document.getElementById('resultText');
        this.actionButtons = document.getElementById('actionButtons');
        this.recordButton = document.getElementById('recordButton');

        this.setupEventListeners();
        // Initialize TTS with error logging
        this.initializeTTS().catch(error => {
            console.error('Failed to initialize TTS:', error);
        });
    }

    log(message) {
        if (this.loggingEnabled) {
            console.log(message);
        }
    }

    setupEventListeners() {
        if (this.retryButton) {
            this.retryButton.addEventListener('click', () => this.resetQuestion());
        } else {
            console.error("Retry Button not found")
        }

        if (this.nextQuestionButton) {
            this.nextQuestionButton.addEventListener('click', () => this.loadNextQuestion());
        } else {
            console.error("Next Question Button not found")
        }
    }

    async initializeTTS() {
        try {
            // Initialize TTS for the question
            const quizSessionTTS = await QuizSessionTTS.init();
            if (quizSessionTTS && typeof quizSessionTTS.readQuestion === 'function') {
                // Attempt to read the question
                quizSessionTTS.readQuestion();
            } else {
                this.log('QuizSessionTTS initialized but readQuestion is not available');
            }
        } catch (error) {
            console.error('Failed to initialize QuizSessionTTS:', error);
        }
    }

    resetQuestion() {
        // Reset the UI for retrying the current question
        this.resultText.textContent = '';
        //this.actionButtons.style.display = 'none';
        //this.recordButton.disabled = false;
        this.hideActionButtons();
        // Stop any ongoing TTS
        this.log('Stopping speech');
        const textToSpeechInstance = TextToSpeechEngine.getInstance();
        textToSpeechInstance.stopSpeaking();
        //todo stop mp3 playback
    }

    showActionButtons() {
        if (this.actionButtons) {
            this.actionButtons.classList.remove('d-none');
        } else {
            console.error('Action buttons element not found');
        }
    }

    hideActionButtons() {
        if (this.actionButtons) {
            this.actionButtons.classList.add('d-none');
        } else {
            console.error('Action buttons element not found');
        }
    }

    loadNextQuestion() {
        // Redirect to the next question
        if (typeof nextQuestionUrl !== 'undefined') {
            window.location.href = nextQuestionUrl;
        } else {
            console.error('nextQuestionUrl is not defined');
        }
    }
}

// Initialize the QuizSession directly as the module will defer execution until the DOM is ready
// Create and export a singleton instance
const quizSessionInstance = new QuizSession();
export default quizSessionInstance;