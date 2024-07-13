document.addEventListener('DOMContentLoaded', function() {
    const retryButton = document.getElementById('retryButton');
    const nextQuestionButton = document.getElementById('nextQuestionButton');

    if (retryButton) {
        retryButton.addEventListener('click', resetQuestion);
    }

    if (nextQuestionButton) {
        nextQuestionButton.addEventListener('click', loadNextQuestion);
    }
});

function resetQuestion() {
    // Reset the UI for retrying the current question
    document.getElementById('resultText').textContent = '';
    document.getElementById('actionButtons').style.display = 'none';
    document.getElementById('recordButton').disabled = false;
}

function loadNextQuestion() {
    // Redirect to the next question
    window.location.href = nextQuestionUrl;
}