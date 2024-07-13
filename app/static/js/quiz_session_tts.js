// quiz_session_tts.js
const QuizSessionTTS = (function() {
    function initQuizSessionTTS() {
        // Function to read the question aloud
        function readQuestion() {
            const questionText = document.getElementById('question-text').textContent;
            if (typeof TextToSpeech !== 'undefined' && typeof TextToSpeech.speakWithoutBuffering === 'function') {
                TextToSpeech.speakWithoutBuffering(questionText);
            } else {
                console.error('TextToSpeech.speakWithoutBuffering function is not available');
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
    }

    return {
        init: initQuizSessionTTS
    };
})();