// speech_to_text.js
import LanguageUtils from './language_utils.js';
import TextToSpeech from './text_to_speech.js';

function initSpeechRecognition(submitUrl, questionId, sessionId) {
    const resultElement = document.getElementById('resultText');
    const recordButton = document.getElementById('recordButton');
    const feedbackContainer = document.getElementById('feedbackContainer');
    const feedbackText = document.getElementById('feedbackText');
    const processingFeedback = document.getElementById('processingFeedback');
    const actionButtons = document.getElementById('actionButtons');

    let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

    // Use LanguageUtils to get the preferred language
    recognition.lang = LanguageUtils.getPreferredLanguage();
    recognition.interimResults = true;
    recognition.continuous = true;

    let finalTranscript = '';

    recognition.onresult = (event) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        resultElement.innerHTML = finalTranscript + '<i style="color: #999;">' + interimTranscript + '</i>';
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        stopRecording();
    };

    recognition.onend = () => {
        stopRecording();
    };

    function startRecording() {
        finalTranscript = '';
        // Update the language just before starting recognition
        recognition.lang = LanguageUtils.getPreferredLanguage();
        console.log('recognizing in '+ recognition.lang);
        recognition.start();
        recordButton.textContent = 'Release to Stop';
        resultElement.textContent = '';
        feedbackContainer.style.display = 'none';
    }

    function stopRecording() {
        recognition.stop();
        recordButton.textContent = 'Push to Answer';
        if (finalTranscript.trim()) {
            sendTranscriptToServer(finalTranscript.trim());
        }
    }

    function sendTranscriptToServer(transcript) {
        processingFeedback.style.display = 'block';
        recordButton.disabled = true;

        const formData = new FormData();
        formData.append('text', transcript);
        formData.append('question_id', questionId);
        formData.append('session_id', sessionId);

        fetch(submitUrl, {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(result => {
            processingFeedback.style.display = 'none';
            feedbackContainer.style.display = 'block';
            feedbackText.textContent = result;
            actionButtons.classList.remove('d-none');

            // If auto-read is enabled, read the feedback
            const autoReadCheckbox = document.getElementById('autoReadResults');
            if (autoReadCheckbox && autoReadCheckbox.checked) {
                TextToSpeech.speakWithoutBuffering(result);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            processingFeedback.style.display = 'none';
            feedbackContainer.style.display = 'block';
            feedbackText.textContent = 'Error: ' + error.message;
        })
        .finally(() => {
            recordButton.disabled = false;
        });
    }

    recordButton.addEventListener('mousedown', startRecording);
    recordButton.addEventListener('mouseup', stopRecording);
    recordButton.addEventListener('mouseleave', stopRecording);

    // Touch events for mobile devices
    recordButton.addEventListener('touchstart', (e) => {
        e.preventDefault(); // Prevent mousedown event on some browsers
        startRecording();
    });
    recordButton.addEventListener('touchend', stopRecording);
}

// Make sure the function is globally accessible
window.initSpeechRecognition = initSpeechRecognition;