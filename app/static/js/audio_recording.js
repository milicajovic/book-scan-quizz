let mediaRecorder;
let audioChunks = [];
let recordingStartTime;
let recordingTimer;

function initAudioRecording(submitUrl) {
    const recordButton = document.getElementById('recordButton');
    const recordingStatus = document.getElementById('recordingStatus');
    const recordingTime = document.getElementById('recordingTime');
    const audioPlayback = document.getElementById('audioPlayback');
    const audioPlayer = document.getElementById('audioPlayer');
    const submitButton = document.getElementById('submitButton');
    const transcriptionDiv = document.getElementById('transcription');
    const transcriptionText = document.getElementById('transcriptionText');

    recordButton.addEventListener('click', toggleRecording);
    submitButton.addEventListener('click', () => submitAudio(submitUrl));

    function toggleRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            stopRecording();
        } else {
            startRecording();
        }
    }

    function startRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                audioChunks = [];

                mediaRecorder.addEventListener("dataavailable", event => {
                    audioChunks.push(event.data);
                });

                mediaRecorder.addEventListener("stop", () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    audioPlayer.src = audioUrl;
                    audioPlayback.style.display = 'block';
                });

                recordButton.textContent = 'Stop Recording';
                recordingStatus.style.display = 'block';
                recordingStartTime = Date.now();
                updateRecordingTime();
            });
    }

    function stopRecording() {
        mediaRecorder.stop();
        recordButton.textContent = 'Record Answer';
        recordingStatus.style.display = 'none';
        clearInterval(recordingTimer);
    }

    function updateRecordingTime() {
        recordingTimer = setInterval(() => {
            const elapsedTime = Math.floor((Date.now() - recordingStartTime) / 1000);
            recordingTime.textContent = elapsedTime;
        }, 1000);
    }

    function submitAudio(url) {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                transcriptionText.textContent = data.transcription;
                transcriptionDiv.style.display = 'block';
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while submitting the audio.');
        });
    }
}