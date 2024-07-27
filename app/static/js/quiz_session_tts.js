import TextToSpeech from './text_to_speech.js';

// Common function to read question text aloud
function readQuestionText() {
    const questionText = document.getElementById('question-text')?.textContent;
    console.log('Question text:', questionText);
    if (questionText && TextToSpeech.isInitialized()) {
        console.log('Reading question aloud');
        TextToSpeech.speakWithoutBuffering(questionText);
    } else {
        console.error('Unable to read question: TextToSpeech not initialized or question text not found');
    }
}

// Function to initialize TextToSpeech
async function initializeTextToSpeech() {
    await TextToSpeech.init();
    console.log('TextToSpeech initialized in QuizSessionTTS');
}

// Function to handle the auto-read checkbox state and events
function handleAutoReadCheckbox(autoReadEnabled) {
    const autoReadCheckbox = document.getElementById('autoReadResults');
    console.log('Auto-read checkbox in QuizSessionTTS:', autoReadCheckbox ? 'found' : 'not found');
    if (autoReadCheckbox) {
        autoReadCheckbox.checked = autoReadEnabled;
        console.log('Checkbox state set to:', autoReadEnabled);

        if (autoReadEnabled) {
            readQuestionText();
        }

        autoReadCheckbox.addEventListener('change', function () {
            console.log('Checkbox changed in QuizSessionTTS. New state:', this.checked);
            localStorage.setItem('autoReadResults', this.checked);
            if (this.checked) {
                readQuestionText();
            } else {
                console.log('Stopping speech');
                TextToSpeech.stopSpeaking();
            }
        });
    }
}

// Function to check the auto-read state from localStorage
function checkAutoReadState() {
    const autoReadEnabled = localStorage.getItem('autoReadResults') === 'true';
    console.log('Auto-read enabled:', autoReadEnabled);
    return autoReadEnabled;
}

// IIFE to create the QuizSessionTTS module
const QuizSessionTTS = (function () {
    // Main function to initialize the QuizSessionTTS
    async function initQuizSessionTTS() {
        console.log('Initializing QuizSessionTTS');
        try {
            // Initialize TextToSpeech
            await initializeTextToSpeech();

            // Check the auto-read state
            const autoReadEnabled = checkAutoReadState();

            // Handle the auto-read checkbox
            handleAutoReadCheckbox(autoReadEnabled);

            // Expose the readQuestion function for external use
            return {
                readQuestion: readQuestionText
            };
        } catch (error) {
            console.error('Failed to initialize QuizSessionTTS:', error);
            return {
                readQuestion: () => console.error('QuizSessionTTS not initialized properly')
            };
        }
    }

    // Return the public API of the module
    return {
        init: initQuizSessionTTS,
        readCurrentQuestion: readQuestionText
    };
})();

export default QuizSessionTTS;
