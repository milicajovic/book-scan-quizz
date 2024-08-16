import TextToSpeechEngine from "./text_to_speech_engine.js";

class QuizSessionTTS {
    constructor() {
        this.loggingEnabled = false; // Set this to false to disable logging
    }

    log(message) {
        if (this.loggingEnabled) {
            console.log(message);
        }
    }

    async init() {
        this.log('Initializing QuizSessionTTS');
        try {
            const textToSpeechInstance = TextToSpeechEngine.getInstance();
            await textToSpeechInstance.init();

            const autoReadEnabled = this.checkAutoReadState();
            this.handleAutoReadCheckbox(autoReadEnabled);

            return {
                readQuestion: this.readQuestionText.bind(this)
            };
        } catch (error) {
            console.error('Failed to initialize QuizSessionTTS:', error);
            return {
                readQuestion: () => console.error('QuizSessionTTS not initialized properly')
            };
        }
    }

    readQuestionText() {
        const questionText = document.getElementById('question-text')?.textContent;
        this.log(`Question text: ${questionText}`);
        const textToSpeechInstance = TextToSpeechEngine.getInstance();
        if (questionText && textToSpeechInstance.isInitialized) {
            this.log('Reading question aloud');
            textToSpeechInstance.speakWithoutBuffering(questionText);
        } else {
            console.error('Unable to read question: TextToSpeech not initialized or question text not found');
        }
    }

    handleAutoReadCheckbox(autoReadEnabled) {
        const autoReadCheckbox = document.getElementById('autoReadResults');
        this.log(`Auto-read checkbox in QuizSessionTTS: ${autoReadCheckbox ? 'found' : 'not found'}`);
        if (autoReadCheckbox) {
            autoReadCheckbox.checked = autoReadEnabled;
            this.log(`Checkbox state set to: ${autoReadEnabled}`);

            if (autoReadEnabled) {
                this.readQuestionText();
            }

            autoReadCheckbox.addEventListener('change', () => {
                this.log(`Checkbox changed in QuizSessionTTS. New state: ${autoReadCheckbox.checked}`);
                localStorage.setItem('autoReadResults', autoReadCheckbox.checked);
                if (autoReadCheckbox.checked) {
                    this.readQuestionText();
                } else {
                    this.log('Stopping speech');
                    const textToSpeechInstance = TextToSpeechEngine.getInstance();
                    textToSpeechInstance.stopSpeaking();
                }
            });
        }
    }

    checkAutoReadState() {
        const autoReadEnabled = localStorage.getItem('autoReadResults') === 'true';
        this.log(`Auto-read enabled: ${autoReadEnabled}`);
        return autoReadEnabled;
    }
}

export default new QuizSessionTTS();
