import TextToSpeech from "./text_to_speech.js";

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

function initAudioRecording(submitUrl, questionId, sessionId) {
    const recordButton = document.getElementById('recordButton');
    const recordingFeedback = document.getElementById('recordingFeedback');
    const recordingDuration = document.getElementById('recordingDuration');
    const resultText = document.getElementById('resultText');
    const processingFeedback = document.getElementById('processingFeedback');
    const audioVisualization = document.getElementById('audioVisualization');
    const audioMeter = document.getElementById('audioMeter');

    let startTime;
    let durationInterval;
    let visualizationInterval;

    recordButton.addEventListener('mousedown', () => handleRecording('start'));
    recordButton.addEventListener('mouseup', () => handleRecording('stop'));
    recordButton.addEventListener('mouseleave', () => handleRecording('stop'));

    function handleRecording(action) {
        if (action === 'start') {
            if (isRecording) return;
            isRecording = true;
            audioChunks = [];
            startRecordingStream();
        } else if (action === 'stop') {
            if (!isRecording) return;
            isRecording = false;
            stopMediaRecorder();
            updateUI(false);
        }
    }

    function startRecordingStream() {
        navigator.mediaDevices.getUserMedia({audio: true})
            .then(stream => setupMediaRecorder(stream))
            .catch(error => handleStreamError(error));
    }

    function setupMediaRecorder(stream) {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        startTime = Date.now();
        updateUI(true);
        startVisualization(stream);
        
        mediaRecorder.addEventListener("dataavailable", event => {
            audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener("stop", () => {
            const audioBlob = new Blob(audioChunks, {type: 'audio/wav'});
            sendAudioToServer(audioBlob);
            stopVisualization();
        });
    }

    function handleStreamError(error) {
        console.error("Error accessing microphone:", error);
        isRecording = false;
        alert('Error accessing microphone. Please ensure you have given permission to use the microphone.');
    }

    function stopMediaRecorder() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    }

    function updateUI(isRecording) {
        recordButton.classList.toggle('btn-danger', isRecording);
        recordButton.classList.toggle('btn-success', !isRecording);
        recordButton.textContent = isRecording ? 'Recording...' : 'Record';
        recordingFeedback.style.display = isRecording ? 'block' : 'none';
        audioVisualization.style.display = isRecording ? 'block' : 'none';

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
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const analyser = audioContext.createAnalyser();
        const microphone = audioContext.createMediaStreamSource(stream);
        microphone.connect(analyser);
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        visualizationInterval = setInterval(() => {
            analyser.getByteFrequencyData(dataArray);
            const average = dataArray.reduce((a, b) => a + b) / bufferLength;
            const volume = Math.min(100, Math.max(0, average));
            audioMeter.style.width = volume + '%';
        }, 100);
    }

    function stopVisualization() {
        clearInterval(visualizationInterval);
        audioMeter.style.width = '0%';
    }

    function sendAudioToServer(audioBlob) {
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.wav");
        formData.append("question_id", questionId);
        formData.append("session_id", sessionId);

        resultText.textContent = '';
        processingFeedback.style.display = 'block';
        recordButton.disabled = true;

        fetch(submitUrl, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.body.getReader();
        })
        .then(reader => processStreamResponse(reader))
        .catch(error => {
            console.error('Error:', error);
            processingFeedback.style.display = 'none';
            resultText.textContent = 'Error: ' + error.message;
            resultText.style.color = 'red';
            recordButton.disabled = false;
        });
    }

    function processStreamResponse(reader) {
        let accumulatedText = '';
        const decoder = new TextDecoder();

        function readChunk() {
            reader.read().then(({done, value}) => {
                if (done) {
                    processingFeedback.style.display = 'none';
                    recordButton.disabled = false;
                    showNextQuestionButton();
                    TextToSpeech.finishSpeaking();
                    return;
                }

                const chunk = decoder.decode(value, {stream: true});
                resultText.textContent += chunk;
                TextToSpeech.addToSpeechQueue(chunk);

                readChunk();
            }).catch(error => {
                console.error('Error reading stream:', error);
                processingFeedback.style.display = 'none';
                resultText.textContent += '\nError reading stream: ' + error.message;
                recordButton.disabled = false;
            });
        }

        readChunk();
    }

    function showNextQuestionButton() {
        const actionButtons = document.getElementById('actionButtons');
        if (actionButtons) {
            actionButtons.classList.remove('d-none');
        } else {
            console.error('Action buttons container not found');
        }
    }
}

// Make sure the function is globally accessible
window.initAudioRecording = initAudioRecording;
