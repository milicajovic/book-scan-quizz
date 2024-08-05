import TextToSpeech from "./text_to_speech.js";

class AudioRecorder {
    constructor(submitUrl, questionId, sessionId) {
        this.submitUrl = submitUrl;
        this.questionId = questionId;
        this.sessionId = sessionId;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.textToSpeechInstance = TextToSpeech.getInstance(); // Ensure we use an instance

        this.loggingEnabled = true; // Set this to false to disable logging
        this.isResetting = false;
        this.initElements();
        this.addEventListeners();
    }

    log(message) {
        if (this.loggingEnabled) {
            console.log(message);
        }
    }

    reset() {
        if (this.isResetting) return;
        this.isResetting = true;

        // Stop any ongoing recording
        this.stopRecording();

        // Reset state variables
        this.audioChunks = [];
        this.isRecording = false;

        // Reset UI elements
        this.updateUI(false);
        //this.resultText.textContent = '';
        this.processingFeedback.style.display = 'none';
        this.recordButton.disabled = false;

        // Clear visualizations
        this.stopVisualization();

        // Reset the audio context if it exists
        if (this.audioContext) {
            this.audioContext.close().then(() => {
                this.audioContext = null;
            });
        }

        this.isResetting = false;
    }

    initElements() {
        this.recordButton = document.getElementById('recordButton');
        this.recordingFeedback = document.getElementById('recordingFeedback');
        this.recordingDuration = document.getElementById('recordingDuration');
        this.resultText = document.getElementById('resultText');
        this.processingFeedback = document.getElementById('processingFeedback');
        this.audioVisualization = document.getElementById('audioVisualization');
        this.audioMeter = document.getElementById('audioMeter');
    }

    addEventListeners() {
        this.recordButton.addEventListener('mousedown', () => this.handleRecording('start'));
        this.recordButton.addEventListener('mouseup', () => this.handleRecording('stop'));
        //this.recordButton.addEventListener('mouseleave', () => this.handleRecording('stop'));

        // this.recordButton.addEventListener('touchstart', (e) => {
        //     e.preventDefault();
        //     this.startRecording();
        // });
        // this.recordButton.addEventListener('touchend', this.stopRecording.bind(this));
    }

    handleRecording(action) {
        if (action === 'start' && !this.isRecording) {
            this.startRecordingStream();
        } else if (action === 'stop' && this.isRecording) {
            this.stopMediaRecorder();
            this.updateUI(false);
        }
    }

    stopRecording() {
        this.handleRecording('stop');
    }

    startRecordingStream() {
        navigator.mediaDevices.getUserMedia({audio: true})
            .then(stream => this.setupMediaRecorder(stream))
            .catch(error => this.handleStreamError(error));
    }

    setupMediaRecorder(stream) {
        this.mediaRecorder = new MediaRecorder(stream);
        this.mediaRecorder.start();
        this.isRecording = true;
        this.audioChunks = [];
        this.startTime = Date.now();
        this.updateUI(true);
        this.startVisualization(stream);

        this.mediaRecorder.addEventListener("dataavailable", event => {
            this.audioChunks.push(event.data);
        });

        this.mediaRecorder.addEventListener("stop", () => {
            const audioBlob = new Blob(this.audioChunks, {type: 'audio/wav'});
            this.sendAudioToServer(audioBlob);
            this.stopVisualization();
        });
    }

    handleStreamError(error) {
        console.error("Error accessing microphone:", error);
        this.isRecording = false;
        alert('Error accessing microphone. Please ensure you have given permission to use the microphone.');
    }

    stopMediaRecorder() {
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    }

    updateUI(isRecording) {
        this.recordButton.classList.toggle('btn-danger', isRecording);
        this.recordButton.classList.toggle('btn-success', !isRecording);
        this.recordButton.textContent = isRecording ? 'Recording...' : 'Record';
        this.recordingFeedback.style.display = isRecording ? 'block' : 'none';
        this.audioVisualization.style.display = isRecording ? 'block' : 'none';
        if (isRecording) {
            this.durationInterval = setInterval(() => this.updateDuration(), 1000);
        } else {
            clearInterval(this.durationInterval);
            this.recordingDuration.textContent = '0';
        }
    }

    updateDuration() {
        const duration = Math.floor((Date.now() - this.startTime) / 1000);
        this.recordingDuration.textContent = duration;
    }

    startVisualization(stream) {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const analyser = audioContext.createAnalyser();
        const microphone = audioContext.createMediaStreamSource(stream);
        microphone.connect(analyser);
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        this.visualizationInterval = setInterval(() => {
            analyser.getByteFrequencyData(dataArray);
            const average = dataArray.reduce((a, b) => a + b) / bufferLength;
            const volume = Math.min(100, Math.max(0, average));
            this.audioMeter.style.width = `${volume}%`;
        }, 100);
    }

    stopVisualization() {
        clearInterval(this.visualizationInterval);
        this.audioMeter.style.width = '0%';
    }

    sendAudioToServer(audioBlob) {
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.wav");
        formData.append("question_id", this.questionId);
        formData.append("session_id", this.sessionId);

        this.resultText.textContent = '';
        this.processingFeedback.style.display = 'block';
        this.recordButton.disabled = true;

        fetch(this.submitUrl, {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.body.getReader();
            })
            .then(reader => this.processStreamResponse(reader))
            .catch(error => {
                console.error('Error:', error);
                this.processingFeedback.style.display = 'none';
                this.resultText.textContent = 'Error: ' + error.message;
                this.resultText.style.color = 'red';
                this.recordButton.disabled = false;
            })
            .finally(() => {
                // Call reset method after processing is complete
                setTimeout(() => this.reset(), 1000); // 5-second delay before resetting
            });
        ;
    }

    processStreamResponse(reader) {
        const decoder = new TextDecoder();

        const readChunk = () => {
            reader.read().then(({done, value}) => {
                if (done) {
                    this.processingFeedback.style.display = 'none';
                    this.recordButton.disabled = false;
                    this.showNextQuestionButton();
                    this.textToSpeechInstance.finishSpeaking();
                    return;
                }

                this.handleStreamChunk(decoder.decode(value, {stream: true}));

                readChunk();
            }).catch(error => {
                console.error('Error reading stream:', error);
                this.processingFeedback.style.display = 'none';
                this.resultText.textContent += `\nError reading stream: ${error.message}`;
                this.recordButton.disabled = false;
            });
        };

        readChunk();
    }

    handleStreamChunk(chunk) {
        this.resultText.textContent += chunk;
        this.textToSpeechInstance.addToSpeechQueue(chunk); // Call on the instance
    }

    showNextQuestionButton() {
        const actionButtons = document.getElementById('actionButtons');
        if (actionButtons) {
            actionButtons.classList.remove('d-none');
        } else {
            console.error('Action buttons container not found');
        }
    }
}

export default (submitUrl, questionId, sessionId) => new AudioRecorder(submitUrl, questionId, sessionId);