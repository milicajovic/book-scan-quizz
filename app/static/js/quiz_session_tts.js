// quiz_session_tts.js
const QuizSessionTTS = (function() {
    async function initQuizSessionTTS() {
        try {
            // Wait for TextToSpeech to initialize
            await TextToSpeech.init();

            // Function to read the question aloud
            function readQuestion() {
                const questionText = document.getElementById('question-text')?.textContent;
                if (questionText && TextToSpeech.isInitialized()) {
                    TextToSpeech.speakWithoutBuffering(questionText);
                } else {
                    console.error('Unable to read question: TextToSpeech not initialized or question text not found');
                }
            }

            // Check if auto-read is enabled and read the question if it is
            if (localStorage.getItem('autoReadResults') === 'true') {
                readQuestion();
            }

            // Add event listener to the auto-read checkbox
            const autoReadCheckbox = document.getElementById('autoReadResults');
            if (autoReadCheckbox) {
                autoReadCheckbox.addEventListener('change', function() {
                    if (this.checked) {
                        readQuestion();
                    } else {
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

    return {
        init: initQuizSessionTTS
    };
})();