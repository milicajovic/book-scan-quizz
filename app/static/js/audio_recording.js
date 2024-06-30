let mediaRecorder;
let audioChunks = [];
let startTime;
let durationInterval;
let audioContext;
let analyser;
let dataArray;
let animationId;

function initAudioRecording(submitUrl, questionId, sessionId) {
    const recordButton = document.getElementById('recordButton');
    const recordingFeedback = document.getElementById('recordingFeedback');
    const recordingDuration = document.getElementById('recordingDuration');
    const resultText = document.getElementById('resultText');
    const processingFeedback = document.getElementById('processingFeedback');
    const audioVisualization = document.getElementById('audioVisualization');
    const audioMeter = document.getElementById('audioMeter');

    recordButton.addEventListener('mousedown', startRecording);
    recordButton.addEventListener('mouseup', stopRecording);
    recordButton.addEventListener('mouseleave', stopRecording);

    function startRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                startTime = Date.now();

                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.start();
                updateUI(true);
                startVisualization(stream);
            })
            .catch(error => {
                console.error('Error accessing microphone:', error);
                alert('Error accessing microphone. Please ensure you have given permission to use the microphone.');
            });
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            updateUI(false);
            stopVisualization();
            sendAudioToServer(new Blob(audioChunks, { type: 'audio/wav' }));
        }
    }

    function updateUI(isRecording) {
        recordButton.classList.toggle('btn-danger', isRecording);
        recordButton.classList.toggle('btn-success', !isRecording);
        recordButton.textContent = isRecording ? 'Recording...' : 'Record';
        recordingFeedback.style.display = isRecording ? 'block' : 'none';

        if (isRecording) {
            durationInterval = setInterval(updateDuration, 1000);
        } else {
            clearInterval(durationInterval);
            recordingDuration.textContent = '0';
        }
    }

    function updateDuration() {
        const duration = Math.floor((Date.now() - startTime) / 1000);
        recordingDuration.textContent = duration;
    }

    function startVisualization(stream) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        function updateVisualization() {
            animationId = requestAnimationFrame(updateVisualization);
            analyser.getByteFrequencyData(dataArray);
            const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
            const volume = Math.min(100, Math.max(0, average * 100 / 256));
            audioMeter.style.width = `${volume}%`;
        }

        audioVisualization.style.display = 'block';
        updateVisualization();
    }

    function stopVisualization() {
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        if (audioContext) {
            audioContext.close();
        }
        audioVisualization.style.display = 'none';
    }

    function sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");
    formData.append("question_id", questionId);
    formData.append("session_id", sessionId);

    resultText.textContent = '';
    processingFeedback.style.display = 'block';
    disableButton();

    fetch(submitUrl, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(data => {
        processingFeedback.style.display = 'none';

        // Split the response into evaluation and JSON parts
        const [evaluationText, jsonDataString] = data.split('####');

        // Display evaluation text
        resultText.innerHTML = evaluationText.trim().replace(/\n/g, '<br>');
        resultText.style.color = 'initial';

        // Parse and handle JSON data
        const jsonLines = jsonDataString.trim().split('\n');
        const correctnessLine = jsonLines.find(line => line.startsWith('Correctness:'));
        const completenessLine = jsonLines.find(line => line.startsWith('Completeness:'));
        const jsonData = jsonLines[jsonLines.length - 1];

        if (correctnessLine && completenessLine) {
            const correctness = correctnessLine.split(':')[1].trim();
            const completeness = completenessLine.split(':')[1].trim();
            resultText.innerHTML += `<br><br>Correctness: ${correctness}/10<br>Completeness: ${completeness}/10`;
        }

        try {
            const responseData = JSON.parse(jsonData);

            if (responseData.session_completed) {
                // Redirect to session completion page
                window.location.href = '/quiz-session/complete/' + sessionId;
            } else if (responseData.next_question) {
                // Prepare for next question
                setTimeout(() => {
                    window.location.href = '/quiz-session/answer/' + sessionId;
                }, 5000);  // Wait 5 seconds before loading next question
            }
        } catch (error) {
            console.error('Error parsing JSON:', error);
        }

        enableButton();
    })
    .catch(error => {
        console.error('Error:', error);
        processingFeedback.style.display = 'none';
        resultText.textContent = 'An error occurred while processing the audio. Please try again.';
        resultText.style.color = 'red';
        enableButton();
    });
}
    function disableButton() {
        recordButton.disabled = true;
    }

    function enableButton() {
        recordButton.disabled = false;
    }
}