// quiz_session.js
document.addEventListener('DOMContentLoaded', async function() {
    const retryButton = document.getElementById('retryButton');
    const nextQuestionButton = document.getElementById('nextQuestionButton');

    if (retryButton) {
        retryButton.addEventListener('click', resetQuestion);
    }

    if (nextQuestionButton) {
        nextQuestionButton.addEventListener('click', loadNextQuestion);
    }

    try {
        // Initialize TTS for the question
        const quizSessionTTS = await QuizSessionTTS.init();
        if (quizSessionTTS && typeof quizSessionTTS.readQuestion === 'function') {
            // Attempt to read the question
            quizSessionTTS.readQuestion();
        } else {
            console.warn('QuizSessionTTS initialized but readQuestion is not available');
        }
    } catch (error) {
        console.error('Failed to initialize QuizSessionTTS:', error);
    }
});

function resetQuestion() {
    // Reset the UI for retrying the current question
    document.getElementById('resultText').textContent = '';
    document.getElementById('actionButtons').style.display = 'none';
    document.getElementById('recordButton').disabled = false;

    // Stop any ongoing TTS
    if (TextToSpeech.isInitialized()) {
        TextToSpeech.stopSpeaking();
    }
}

function loadNextQuestion() {
    // Redirect to the next question
    if (typeof nextQuestionUrl !== 'undefined') {
        window.location.href = nextQuestionUrl;
    } else {
        console.error('nextQuestionUrl is not defined');
    }
}