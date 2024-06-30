let mediaRecorder;
let audioChunks = [];
let startTime;
let durationInterval;
let audioContext;
let analyser;
let dataArray;
let animationId;

function initAudioRecording(submitUrl) {
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

    function disableButton() {
        recordButton.disabled = true;
        recordButton.classList.remove('btn-success', 'btn-danger');
        recordButton.classList.add('btn-secondary');
        recordButton.style.cursor = 'not-allowed';
    }

    function enableButton() {
        recordButton.disabled = false;
        recordButton.classList.remove('btn-secondary');
        recordButton.classList.add('btn-success');
        recordButton.style.cursor = 'pointer';
    }

    function startRecording() {
        if (recordButton.disabled) return;

        audioChunks = [];
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                startTime = Date.now();

                mediaRecorder.addEventListener("dataavailable", event => {
                    audioChunks.push(event.data);
                });

                recordButton.classList.remove('btn-success');
                recordButton.classList.add('btn-danger');
                recordingFeedback.style.display = 'block';
                audioVisualization.style.display = 'block';
                startDurationCounter();
                startAudioVisualization(stream);
            })
            .catch(error => {
                console.error('Error accessing microphone:', error);
                alert('Unable to access the microphone. Please ensure it is connected and you have granted permission to use it.');
            });
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            recordButton.classList.remove('btn-danger');
            recordButton.classList.add('btn-success');
            recordingFeedback.style.display = 'none';
            audioVisualization.style.display = 'none';
            stopDurationCounter();
            stopAudioVisualization();

            mediaRecorder.addEventListener("stop", () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendAudioToServer(audioBlob);
            });
        }
    }

    function startDurationCounter() {
        recordingDuration.textContent = '0';
        durationInterval = setInterval(() => {
            const duration = Math.floor((Date.now() - startTime) / 1000);
            recordingDuration.textContent = duration;
        }, 1000);
    }

    function stopDurationCounter() {
        clearInterval(durationInterval);
    }

    function startAudioVisualization(stream) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        function updateAudioMeter() {
            analyser.getByteFrequencyData(dataArray);
            const average = dataArray.reduce((acc, val) => acc + val, 0) / dataArray.length;
            const volume = Math.min(100, Math.max(0, average * 2));
            audioMeter.style.width = `${volume}%`;
            animationId = requestAnimationFrame(updateAudioMeter);
        }

        updateAudioMeter();
    }

    function stopAudioVisualization() {
        if (audioContext) {
            audioContext.close();
        }
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
    }

    function sendAudioToServer(audioBlob) {
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.wav");

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
            return response.json();
        })
        .then(data => {
            processingFeedback.style.display = 'none';
            if (data.error) {
                resultText.textContent = data.error;
                resultText.style.color = 'red';
            } else {
                resultText.textContent = data.transcription || data.result;
                resultText.style.color = 'initial';
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
}