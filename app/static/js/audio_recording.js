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

    if (!recordButton || !recordingFeedback || !recordingDuration || !resultText || !processingFeedback || !audioVisualization || !audioMeter) {
        console.error('One or more required elements are missing from the DOM');
        return;
    }

    recordButton.addEventListener('mousedown', startRecording);
    recordButton.addEventListener('mouseup', stopRecording);
    recordButton.addEventListener('mouseleave', stopRecording);

    function startRecording() {
        navigator.mediaDevices.getUserMedia({audio: true})
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
            sendAudioToServer(new Blob(audioChunks, {type: 'audio/wav'}));
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
        processingFeedback.style.display = 'none';
        disableButton();

        fetch(submitUrl, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            const reader = response.body.getReader();
            return new ReadableStream({
                start(controller) {
                    function push() {
                        reader.read().then(({ done, value }) => {
                            if (done) {
                                console.log('Stream complete');
                                TextToSpeech.handleStreamEnd(); // Call handleStreamEnd when the stream is complete
                                controller.close();
                                enableButton();
                                return;
                            }
                            const chunk = new TextDecoder().decode(value);
                            console.log('Received chunk:', chunk);
                            processChunk(chunk);
                            controller.enqueue(value);
                            push();
                        });
                    }
                    push();
                }
            });
        })
        .catch(handleError);
    }


    function processChunk(chunk) {
        appendToUI(chunk);
        if (localStorage.getItem('autoReadResults') === 'true') {
            TextToSpeech.speak(chunk);
        }
    }


    function appendToUI(text) {
        resultText.innerHTML += text;
    }

    function handleError(error) {
        console.error('Error:', error);
        processingFeedback.style.display = 'none';
        resultText.innerHTML += 'Error: ' + error.message;
        resultText.style.color = 'red';
        enableButton();
    }

    function disableButton() {
        if (recordButton) recordButton.disabled = true;
    }

    function enableButton() {
        if (recordButton) recordButton.disabled = false;
    }
}