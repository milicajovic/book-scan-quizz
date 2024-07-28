import QuizSessionTTS from './quiz_session_tts.js';
import TextToSpeech from './text_to_speech.js';

class QuizSession {
    constructor() {
        this.loggingEnabled = false; // Set this to false to disable logging
        this.retryButton = document.getElementById('retryButton');
        this.nextQuestionButton = document.getElementById('nextQuestionButton');
        this.resultText = document.getElementById('resultText');
        this.actionButtons = document.getElementById('actionButtons');
        this.recordButton = document.getElementById('recordButton');

        this.setupEventListeners();
        this.initializeTTS();
    }

    log(message) {
        if (this.loggingEnabled) {
            console.log(message);
        }
    }

    setupEventListeners() {
        if (this.retryButton) {
            this.retryButton.addEventListener('click', () => this.resetQuestion());
        }

        if (this.nextQuestionButton) {
            this.nextQuestionButton.addEventListener('click', () => this.loadNextQuestion());
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
        this.actionButtons.style.display = 'none';
        this.recordButton.disabled = false;

        // Stop any ongoing TTS
        if (TextToSpeech.isInitialized()) {
            TextToSpeech.stopSpeaking();
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
new QuizSession();
