const QuizSessionTTS = (function () {
    async function initQuizSessionTTS() {
        console.log('Initializing QuizSessionTTS');
        try {
            // Wait for TextToSpeech to initialize
            await TextToSpeech.init();
            console.log('TextToSpeech initialized in QuizSessionTTS');

            // Function to read the question aloud
            function readQuestion() {
                const questionText = document.getElementById('question-text')?.textContent;
                console.log('Question text:', questionText);
                if (questionText && TextToSpeech.isInitialized()) {
                    console.log('Reading question aloud');
                    TextToSpeech.speakWithoutBuffering(questionText);
                } else {
                    console.error('Unable to read question: TextToSpeech not initialized or question text not found');
                }
            }

            // Check if auto-read is enabled and set checkbox state
            const autoReadEnabled = localStorage.getItem('autoReadResults') === 'true';
            console.log('Auto-read enabled:', autoReadEnabled);

            const autoReadCheckbox = document.getElementById('autoReadResults');
            console.log('Auto-read checkbox in QuizSessionTTS:', autoReadCheckbox ? 'found' : 'not found');
            if (autoReadCheckbox) {
                autoReadCheckbox.checked = autoReadEnabled;
                console.log('Checkbox state set to:', autoReadEnabled);

                if (autoReadEnabled) {
                    readQuestion();
                }

                autoReadCheckbox.addEventListener('change', function () {
                    console.log('Checkbox changed in QuizSessionTTS. New state:', this.checked);
                    localStorage.setItem('autoReadResults', this.checked);
                    if (this.checked) {
                        readQuestion();
                    } else {
                        console.log('Stopping speech');
                        TextToSpeech.stopSpeaking();
                    }
                });
            }

            // Expose readQuestion function to be callable from outside
            return {
                readQuestion: readQuestion
            };
        } catch (error) {
            console.error('Failed to initialize QuizSessionTTS:', error);
            return {
                readQuestion: () => console.error('QuizSessionTTS not initialized properly')
            };
        }
    }

    function readCurrentQuestion() {
        const questionText = document.getElementById('question-text')?.textContent;
        console.log('Reading current question:', questionText);
        if (questionText && TextToSpeech.isInitialized()) {
            TextToSpeech.speakWithoutBuffering(questionText);
        } else {
            console.error('Unable to read question: TextToSpeech not initialized or question text not found');
        }
    }

    return {
        init: initQuizSessionTTS,
        readCurrentQuestion: readCurrentQuestion
    };
})();