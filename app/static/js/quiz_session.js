// quiz_session.js
document.addEventListener('DOMContentLoaded', function() {
    const retryButton = document.getElementById('retryButton');
    const nextQuestionButton = document.getElementById('nextQuestionButton');

    if (retryButton) {
        retryButton.addEventListener('click', resetQuestion);
    }

    if (nextQuestionButton) {
        nextQuestionButton.addEventListener('click', loadNextQuestion);
    }

    // Initialize TTS for the question
    if (typeof QuizSessionTTS !== 'undefined' && typeof QuizSessionTTS.init === 'function') {
        const quizSessionTTS = QuizSessionTTS.init();
        if (quizSessionTTS && typeof quizSessionTTS.readQuestion === 'function') {
            quizSessionTTS.readQuestion();
        }
    } else {
        console.error('QuizSessionTTS not available');
    }
});

function resetQuestion() {
    // Reset the UI for retrying the current question
    document.getElementById('resultText').textContent = '';
    document.getElementById('actionButtons').style.display = 'none';
    document.getElementById('recordButton').disabled = false;

    // Stop any ongoing TTS
    if (typeof TextToSpeech !== 'undefined' && typeof TextToSpeech.stopSpeaking === 'function') {
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